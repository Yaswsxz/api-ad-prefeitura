"""
Service responsável pelas outras 2 operações que ficaram sob minha
responsabilidade: Criar Pessoa e Alterar Pessoa, para os 4 subtipos que
existem dentro de cada unidade da Direta (Estagio, Carreira, Comissionados,
NaoHumanos).

Conforme o documento da API:
  - Criar sempre cria a pessoa dentro da árvore Inoperantes (bloqueada).
    (A ativação / passagem para Operativos não está descrita no documento
    e não faz parte destas 2 funções — assumi que é feita por outro fluxo.
    Vale confirmar isso com o time.)
  - Alterar só é permitido em pessoas que já estão na árvore Operativos.

Sem endpoint de DELETE físico: quando alguém deixa de ser operante, o
esperado é mover para o mesmo caminho dentro de Inoperantes (espelho),
não apagar do AD.
"""

from ldap3 import MODIFY_REPLACE, SUBTREE
from ldap3.core.exceptions import LDAPException
from fastapi import HTTPException

from app.core.config import settings
from app.core.ldap_connection import get_connection
from app.core.logging_config import logger
from app.core.generators import gerar_login, gerar_senha
from app.schemas.estrutura import RamoOU
from app.schemas.identidade import TipoPessoa, PessoaCreate, PessoaUpdate, PessoaOut, PessoaCriadaOut
from app.services.ad_service import _registrar_atividade
from app.services.estrutura_service import _dn_unidade, _unidade_existe

UAC_NORMAL_ATIVO = 512
UAC_NORMAL_DESABILITADA = 514


def _dn_subcontainer(arvore: str, unidade: str, tipo: TipoPessoa) -> str:
    """DN do subcontainer de tipo dentro de uma unidade da Direta."""
    dn_unidade = _dn_unidade(arvore, RamoOU.DIRETA, unidade)
    return f"CN={tipo.value},{dn_unidade}"


def _gerar_login_e_nome(dados: PessoaCreate) -> tuple[str, str]:
    if dados.tipo == TipoPessoa.NAO_HUMANO:
        login = f"nhu.{dados.nao_humano_categoria.lower()}.{dados.nao_humano_identificador.lower()}"
        nome = f"{dados.nao_humano_categoria}{dados.nao_humano_identificador}".lower()
    else:
        login = gerar_login(dados.primeiro_nome, dados.ultimo_nome)
        nome = f"{dados.primeiro_nome} {dados.ultimo_nome}"
    return login, nome


def criar_pessoa(dados: PessoaCreate, ip_address: str = None, user_agent: str = None,
                  operator: str = "system") -> PessoaCriadaOut:
    """
    Cria uma identidade (humana ou não) dentro do subcontainer de tipo,
    na unidade indicada. É criada já em Inoperantes, bloqueada.
    """
    dados.validar_por_tipo()

    conn = get_connection()
    try:
        dn_unidade_op = _dn_unidade("Operativos", RamoOU.DIRETA, dados.unidade)
        if not _unidade_existe(conn, dn_unidade_op):
            raise HTTPException(
                status_code=422,
                detail=f"Unidade '{dados.unidade}' não existe em Operativos/Direta. Crie a OU primeiro.",
            )

        login, nome = _gerar_login_e_nome(dados)

        # Login precisa ser único no domínio inteiro, não só na unidade
        conn.search(search_base=settings.AD_PML_BASE, search_filter=f"(sAMAccountName={login})",
                    search_scope=SUBTREE)
        if conn.entries:
            raise HTTPException(status_code=409, detail=f"Login '{login}' já existe no AD")

        dn_pai = _dn_subcontainer("Inoperantes", dados.unidade, dados.tipo)
        dn_pessoa = f"CN={nome},{dn_pai}"

        senha_gerada = None
        if dados.tipo == TipoPessoa.NAO_HUMANO:
            atributos = {
                "objectClass": ["top", "person", "organizationalPerson", "user"],
                "cn": nome,
                "sAMAccountName": login,
                "userPrincipalName": f"{login}@{settings.AD_DOMAIN}",
                "userAccountControl": UAC_NORMAL_DESABILITADA,
                "pmlNaoHumanoTipo": dados.nao_humano_tipo or "",
            }
        else:
            atributos = {
                "objectClass": ["top", "person", "organizationalPerson", "user"],
                "cn": nome,
                "sAMAccountName": login,
                "userPrincipalName": f"{login}@{settings.AD_DOMAIN}",
                "givenName": dados.primeiro_nome,
                "sn": dados.ultimo_nome,
                "displayName": nome,
                "userAccountControl": UAC_NORMAL_DESABILITADA,
            }
            if dados.cargo:
                atributos["title"] = dados.cargo
            if dados.email:
                atributos["mail"] = dados.email

        ok = conn.add(dn_pessoa, attributes=atributos)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao criar identidade: {conn.result}")

        if dados.tipo != TipoPessoa.NAO_HUMANO:
            senha_gerada = gerar_senha(8)
            conn.extend.microsoft.modify_password(dn_pessoa, senha_gerada)
        # Fica bloqueada (UAC_NORMAL_DESABILITADA) mesmo após criação, conforme documento.

        _registrar_atividade(
            operator=operator,
            action="CREATE_PESSOA",
            target_user=login,
            details={
                "tipo": dados.tipo.value,
                "unidade": dados.unidade,
                "cpf": dados.cpf,
                "cargo": dados.cargo,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return PessoaCriadaOut(
            login=login,
            nome=nome,
            tipo=dados.tipo,
            unidade=dados.unidade,
            ativo=False,
            distinguished_name=dn_pessoa,
            cargo=dados.cargo,
            email=dados.email,
            senha_gerada=senha_gerada,
        )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em criar_pessoa (unidade={dados.unidade}, tipo={dados.tipo}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em criar_pessoa (unidade={dados.unidade}, tipo={dados.tipo}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def alterar_pessoa(login: str, dados: PessoaUpdate, ip_address: str = None, user_agent: str = None,
                    operator: str = "system") -> PessoaOut:
    """
    Altera os atributos mutáveis de uma identidade. Só é permitido se a
    pessoa estiver atualmente dentro da árvore Operativos.
    """
    conn = get_connection()
    try:
        conn.search(search_base=settings.AD_PML_BASE, search_filter=f"(sAMAccountName={login})",
                    search_scope=SUBTREE,
                    attributes=["cn", "sAMAccountName", "mail", "title", "userAccountControl", "distinguishedName"])
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Identidade não encontrada no AD")

        entry = conn.entries[0]
        dn = str(entry.entry_dn)

        if "CN=Operativos" not in dn:
            raise HTTPException(
                status_code=409,
                detail="Não é possível alterar identidades fora da árvore Operativos",
            )

        mudancas = {}
        if dados.cargo is not None:
            mudancas["title"] = [(MODIFY_REPLACE, [dados.cargo])]
        if dados.email is not None:
            mudancas["mail"] = [(MODIFY_REPLACE, [dados.email])]
        if dados.telefone is not None:
            mudancas["telephoneNumber"] = [(MODIFY_REPLACE, [dados.telefone])]
        if dados.nao_humano_tipo is not None:
            mudancas["pmlNaoHumanoTipo"] = [(MODIFY_REPLACE, [dados.nao_humano_tipo])]

        if mudancas:
            ok = conn.modify(dn, mudancas)
            if not ok:
                raise HTTPException(status_code=500, detail=f"Falha ao alterar identidade: {conn.result}")

        uac = int(entry.userAccountControl.value) if entry.userAccountControl.value else UAC_NORMAL_ATIVO
        ativo = not (uac & 2)

        # Deduz tipo e unidade a partir do próprio DN (CN=<tipo>,CN=<unidade>,CN=Direta,...)
        partes = dn.split(",")
        tipo_str = partes[1].replace("CN=", "") if len(partes) > 1 else None
        unidade_str = partes[2].replace("CN=", "") if len(partes) > 2 else None

        _registrar_atividade(
            operator=operator,
            action="UPDATE_PESSOA",
            target_user=login,
            details={"campos_alterados": dados.model_dump(exclude_unset=True)},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return PessoaOut(
            login=login,
            nome=str(entry.cn.value),
            tipo=TipoPessoa(tipo_str) if tipo_str in TipoPessoa._value2member_map_ else TipoPessoa.CARREIRA,
            unidade=unidade_str or "",
            ativo=ativo,
            distinguished_name=dn,
            cargo=str(entry.title.value) if entry.title.value else None,
            email=str(entry.mail.value) if entry.mail.value else None,
        )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em alterar_pessoa (login={login}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em alterar_pessoa (login={login}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def remover_pessoa(login: str, ip_address: str = None, user_agent: str = None, operator: str = "system") -> None:
    """
    Remove fisicamente uma identidade do AD. Aceita remoção de qualquer
    ramo (Operativos, Inoperantes, Desincorporados) — a decisão de permitir
    isso foi tomada de forma consciente, sabendo que é uma operação
    destrutiva e auditada.
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_PML_BASE,
            search_filter=f"(sAMAccountName={login})",
            search_scope=SUBTREE,
            attributes=["distinguishedName"],
        )
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Identidade não encontrada no AD")

        dn = str(conn.entries[0].entry_dn)

        ok = conn.delete(dn)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao remover identidade: {conn.result}")

        _registrar_atividade(
            operator=operator,
            action="DELETE_PESSOA",
            target_user=login,
            details={"dn": dn},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em remover_pessoa (login={login}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em remover_pessoa (login={login}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


from app.services.ad_service import mover_usuario, buscar_usuario, UAC_NORMAL_ATIVO, UAC_NORMAL_DESABILITADA


# =============================================================================
# Helpers de ramo (Operativos / Inoperantes / Desincorporados)
# =============================================================================
# Aceitamos tanto OU= quanto CN= no DN, porque a árvore do AD tem os dois
# casos (o script criar_estrutura_ad.py cria como CN=, mas o modelo final
# pode migrar para OU=). A busca é case-insensitive no nome do ramo.

RAMAIS_ESPELHAVEIS = ("OPERATIVOS", "INOPERANTES")
RAMAIS_CONHECIDOS = ("OPERATIVOS", "INOPERANTES", "DESINCORPORADOS")


def _ramo_do_dn(dn: str) -> tuple[str | None, int | None]:
    """
    Dado um DN, retorna (nome_do_ramo, índice_no_DN).
    Ex: 'CN=arthur.thomas,CN=Carreira,CN=FAZENDA,CN=DIRETA,CN=OPERATIVOS,OU=PML,...'
        → ('OPERATIVOS', 4)
    Retorna (None, None) se não encontrar nenhum ramo conhecido.
    """
    partes = [p.strip() for p in dn.split(",")]
    for i, parte in enumerate(partes):
        upper = parte.upper()
        if upper.startswith("OU=") or upper.startswith("CN="):
            nome = upper.split("=", 1)[1]
            if nome in RAMAIS_CONHECIDOS:
                return nome, i
    return None, None


def _calcular_dn_espelhado(dn_atual: str, novo_ramo: str) -> str:
    """
    Devolve o DN espelhado em outro ramo, preservando o caminho interno
    (CN=Carreira, CN=FAZENDA, CN=DIRETA, etc.) e o prefixo (OU= ou CN=).

    Ex:
      dn_atual = 'CN=arthur.thomas,CN=Carreira,CN=FAZENDA,CN=DIRETA,CN=OPERATIVOS,OU=PML,...'
      novo_ramo = 'INOPERANTES'
      → 'CN=arthur.thomas,CN=Carreira,CN=FAZENDA,CN=DIRETA,CN=INOPERANTES,OU=PML,...'
    """
    ramo_atual, idx = _ramo_do_dn(dn_atual)
    if ramo_atual is None:
        raise HTTPException(
            status_code=409,
            detail=f"Não foi possível identificar o ramo da pessoa no DN: {dn_atual}",
        )

    novo_ramo = novo_ramo.upper()
    if novo_ramo not in RAMAIS_ESPELHAVEIS:
        raise HTTPException(
            status_code=422,
            detail=f"Ramo '{novo_ramo}' não é espelhável. Use OPERATIVOS ou INOPERANTES.",
        )

    if ramo_atual == novo_ramo:
        return dn_atual

    partes = [p.strip() for p in dn_atual.split(",")]
    prefixo = partes[idx].split("=", 1)[0]  # preserva "CN" ou "OU"
    partes[idx] = f"{prefixo}={novo_ramo}"
    return ",".join(partes)


def _usuario_out_to_pessoa_out(u) -> PessoaOut:
    """
    Converte o UsuarioOut que o ad_service devolve em PessoaOut, deduzindo
    tipo e unidade a partir do DN.
    """
    dn = u.distinguished_name
    partes = dn.split(",")
    tipo_str = partes[1].replace("CN=", "").replace("OU=", "") if len(partes) > 1 else None
    unidade_str = partes[2].replace("CN=", "").replace("OU=", "") if len(partes) > 2 else None
    return PessoaOut(
        login=u.login,
        nome=u.nome_completo,
        tipo=TipoPessoa(tipo_str) if tipo_str in TipoPessoa._value2member_map_ else TipoPessoa.CARREIRA,
        unidade=unidade_str or "",
        ativo=u.ativo,
        distinguished_name=dn,
        cargo=u.cargo,
        email=u.email,
    )


# =============================================================================
# Mover Pessoa (genérico)
# =============================================================================

def mover_pessoa(
    login: str,
    destino: str,
    ip_address: str = None,
    user_agent: str = None,
    operator: str = "system",
) -> PessoaOut:
    """
    Move uma pessoa para outro local no AD.

    'destino' aceita 2 formas:
      - Ramo espelhável: 'OPERATIVOS' | 'INOPERANTES'
        → troca só o ramo, preservando o caminho interno (CN=Carreira, CN=FAZENDA, ...)
      - DN completo do novo pai
        → move diretamente (ex: trocar FAZENDA por EDUCACAO dentro de Direta)
    """
    dn_atual = _resolver_dn(login)
    usuario = buscar_usuario(login)
    rdn = f"CN={usuario.nome_completo}"

    destino_limpo = destino.strip()
    destino_upper = destino_limpo.upper()

    if destino_upper in RAMAIS_ESPELHAVEIS:
        novo_dn_completo = _calcular_dn_espelhado(dn_atual, destino_upper)
        novo_parent_dn = novo_dn_completo[len(rdn) + 1:]
    elif destino_upper == "DESINCORPORADOS":
        raise HTTPException(
            status_code=422,
            detail=(
                "DESINCORPORADOS não aceita movimento espelhado de pessoa. "
                "Para mover alguém para dentro de Desincorporados, informe o DN "
                "completo do novo pai (ex: 'CN=FAZENDA,CN=DESINCORPORADOS,OU=PML,...')."
            ),
        )
    else:
        novo_parent_dn = destino_limpo

    mover_usuario(login, novo_parent_dn)

    _registrar_atividade(
        operator=operator,
        action="MOVE_PESSOA",
        target_user=login,
        details={
            "dn_anterior": dn_atual,
            "novo_parent": novo_parent_dn,
            "destino_informado": destino,
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return _usuario_out_to_pessoa_out(buscar_usuario(login))


# =============================================================================
# Bloquear / Desbloquear Pessoa
# =============================================================================

def bloquear_pessoa(
    login: str,
    ip_address: str = None,
    user_agent: str = None,
    operator: str = "system",
) -> PessoaOut:
    """
    Bloqueia/inativa uma pessoa:
      1. Move para o ramo INOPERANTES (espelhado, preserva o caminho interno)
      2. Define userAccountControl = 514 (conta desabilitada)
    Idempotente: se já estiver em INOPERANTES, só reaplica o UAC.
    """
    dn_atual = _resolver_dn(login)
    ramo_atual, _ = _ramo_do_dn(dn_atual)

    if ramo_atual == "DESINCORPORADOS":
        raise HTTPException(
            status_code=409,
            detail="Pessoa em Desincorporados não pode ser bloqueada por este fluxo.",
        )

    if ramo_atual != "INOPERANTES":
        usuario = buscar_usuario(login)
        rdn = f"CN={usuario.nome_completo}"
        novo_dn = _calcular_dn_espelhado(dn_atual, "INOPERANTES")
        novo_parent = novo_dn[len(rdn) + 1:]
        mover_usuario(login, novo_parent)

    dn_atualizado = _resolver_dn(login)
    conn = get_connection()
    try:
        conn.modify(dn_atualizado, {"userAccountControl": [(MODIFY_REPLACE, [UAC_NORMAL_DESABILITADA])]})
        if conn.result["result"] != 0:
            raise HTTPException(status_code=500, detail=f"Falha ao desabilitar conta: {conn.result}")
    finally:
        conn.unbind()

    _registrar_atividade(
        operator=operator,
        action="BLOCK_PESSOA",
        target_user=login,
        details={"dn_anterior": dn_atual, "dn_atual": dn_atualizado},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return _usuario_out_to_pessoa_out(buscar_usuario(login))


def desbloquear_pessoa(
    login: str,
    ip_address: str = None,
    user_agent: str = None,
    operator: str = "system",
) -> PessoaOut:
    """
    Desbloqueia/reativa uma pessoa:
      1. Move para o ramo OPERATIVOS (espelhado)
      2. Define userAccountControl = 512 (conta habilitada)
    Idempotente: se já estiver em OPERATIVOS, só reaplica o UAC.
    """
    dn_atual = _resolver_dn(login)
    ramo_atual, _ = _ramo_do_dn(dn_atual)

    if ramo_atual == "DESINCORPORADOS":
        raise HTTPException(
            status_code=409,
            detail="Pessoa em Desincorporados não pode ser desbloqueada por este fluxo.",
        )

    if ramo_atual != "OPERATIVOS":
        usuario = buscar_usuario(login)
        rdn = f"CN={usuario.nome_completo}"
        novo_dn = _calcular_dn_espelhado(dn_atual, "OPERATIVOS")
        novo_parent = novo_dn[len(rdn) + 1:]
        mover_usuario(login, novo_parent)

    dn_atualizado = _resolver_dn(login)
    conn = get_connection()
    try:
        conn.modify(dn_atualizado, {"userAccountControl": [(MODIFY_REPLACE, [UAC_NORMAL_ATIVO])]})
        if conn.result["result"] != 0:
            raise HTTPException(status_code=500, detail=f"Falha ao habilitar conta: {conn.result}")
    finally:
        conn.unbind()

    _registrar_atividade(
        operator=operator,
        action="UNBLOCK_PESSOA",
        target_user=login,
        details={"dn_anterior": dn_atual, "dn_atual": dn_atualizado},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return _usuario_out_to_pessoa_out(buscar_usuario(login))



def _resolver_dn(login: str) -> str:
    """
    Resolve o DN de uma pessoa a partir do sAMAccountName.
    (Cópia local — evita depender de função privada do ad_service.)
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_PML_BASE,
            search_filter=f"(sAMAccountName={login})",
            search_scope=SUBTREE,
        )
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada no AD")
        return conn.entries[0].entry_dn
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em _resolver_dn (login={login}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em _resolver_dn (login={login}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()