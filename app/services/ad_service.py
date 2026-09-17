from ldap3 import MODIFY_REPLACE, SUBTREE
from ldap3.core.exceptions import LDAPException
from fastapi import HTTPException

from app.core.config import settings
from app.core.ldap_connection import get_connection
from app.core.generators import gerar_login, gerar_senha
from app.core.logging_config import logger
from app.schemas.user import UsuarioOut

# Flags do atributo userAccountControl no Active Directory
# 512 = conta habilitada | 514 = conta desabilitada (bit 2 = 2)
UAC_NORMAL_ATIVO = 512
UAC_NORMAL_DESABILITADA = 514


# ---------------------------------------------------------------------------
# Padrão único de tratamento de erro usado em toda função que fala com o AD:
#
#   except HTTPException:
#       raise  # erros intencionais (404, 409, 422...) passam direto
#   except LDAPException as e:
#       logger.error(...)
#       raise HTTPException(status_code=503, detail="Erro de comunicação com o AD") from e
#   except Exception as e:
#       logger.error(...)
#       raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
#
# 503 = falha de comunicação com o AD (rede, servidor fora do ar, timeout).
# 500 = bug inesperado de verdade, não relacionado à disponibilidade do AD.
# ---------------------------------------------------------------------------


RAMAIS = {
    "OPERATIVOS": "OPERATIVOS",
    "INOPERANTES": "INOPERANTES",
    "DESINCORPORADOS": "DESINCORPORADOS",
}


RAMAIS_ESPELHADOS = ("OPERATIVOS", "INOPERANTES")


def _ramo_do_dn(dn: str) -> str | None:
    """
    Retorna 'OPERATIVOS', 'INOPERANTES' ou None se o DN não estiver em nenhum.
    Comparação exata (case-insensitive) para não confundir com nomes parecidos.
    """
    for parte in dn.split(","):
        p = parte.strip().upper()
        if p == "OU=OPERATIVOS":
            return "OPERATIVOS"
        if p == "OU=INOPERANTES":
            return "INOPERANTES"
    return None


def _dn_espelhado(dn: str, novo_ramo: str) -> str:
    """
    Troca o ramo do DN (OPERATIVOS ↔ INOPERANTES), preservando o resto do caminho.
    
    Ex:
        CN=arthur.thomas,CN=Carreira,OU=FAZENDA,OU=DIRETA,OU=OPERATIVOS,OU=PML,DC=...
        → (novo_ramo='INOPERANTES')
        CN=arthur.thomas,CN=Carreira,OU=FAZENDA,OU=DIRETA,OU=INOPERANTES,OU=PML,DC=...
    """
    partes = [p.strip() for p in dn.split(",")]
    for i, p in enumerate(partes):
        if p.upper() in ("OU=OPERATIVOS", "OU=INOPERANTES"):
            partes[i] = f"OU={novo_ramo.upper()}"
            return ",".join(partes)
    raise HTTPException(
        status_code=409,
        detail=f"Pessoa não está sob OPERATIVOS nem INOPERANTES. DN: {dn}",
    )


def _registrar_atividade(operator: str, action: str, target_user: str, details: dict,
                          ip_address: str = None, user_agent: str = None, status: str = "SUCCESS") -> None:
    """
    Registra uma ação no banco de auditoria. Centraliza o padrão repetido em
    quase toda função de escrita do serviço (abrir sessão, registrar, fechar,
    nunca deixar uma falha de auditoria quebrar a operação principal).
    """
    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_activity(
            username=operator,
            action=action,
            target_user=target_user,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )
        db.close()
    except Exception as e:
        logger.error(f"Erro ao registrar auditoria (action={action}, target_user={target_user}): {e}")


def _registrar_login(username: str, ip_address: str = None, user_agent: str = None,
                      success: bool = True, error_message: str = None) -> None:
    """
    Registra uma tentativa de login (sucesso ou falha) no banco de auditoria.
    """
    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_login(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )
        db.close()
    except Exception as e:
        logger.error(f"Erro ao registrar login (username={username}): {e}")


def _entry_to_usuario_out(entry) -> UsuarioOut:
    """
    Converte um registro do LDAP para o schema de saída da API.
    """
    uac = int(entry.userAccountControl.value) if entry.userAccountControl.value else UAC_NORMAL_ATIVO
    ativo = not (uac & 2)
    return UsuarioOut(
        login=str(entry.sAMAccountName.value),
        nome_completo=str(entry.cn.value),
        email=str(entry.mail.value) if entry.mail.value else None,
        cargo=str(entry.title.value) if entry.title.value else None,
        tipo=str(entry.description.value) if entry.description.value else None,
        ativo=ativo,
        distinguished_name=str(entry.entry_dn),
    )


def _resolver_dn(login: str) -> str:
    """
    Busca o Distinguished Name completo a partir do login (sAMAccountName).
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=f"(sAMAccountName={login})",
            search_scope=SUBTREE,
        )
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Usuário não encontrado no AD")
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


def listar_cargos() -> list[str]:
    """
    Lista os cargos (atributo 'title') distintos já cadastrados entre os
    usuários do AD, sem duplicatas e em ordem alfabética. Útil para
    popular um dropdown no frontend, evitando variações de digitação
    para o mesmo cargo.
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter="(&(objectClass=user)(objectCategory=person)(title=*))",
            search_scope=SUBTREE,
            attributes=["title"],
        )
        cargos = {str(entry.title.value) for entry in conn.entries if entry.title.value}
        return sorted(cargos)
    except LDAPException as e:
        logger.error(f"Erro LDAP em listar_cargos: {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em listar_cargos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def listar_usuarios(
    filtro_nome: str | None = None,
    filtro_cargo: str | None = None,
    filtro_email: str | None = None,
    filtro_ativo: bool | None = None,
    ordenar_por: str = "nome",
    ordem: str = "asc",
):
    """
    Retorna lista de usuários do Active Directory, com filtros opcionais
    e ordenação.

    filtro_nome, filtro_cargo e filtro_email são aplicados direto no
    filtro LDAP (mais eficiente, filtra no servidor). filtro_ativo é
    aplicado depois, em Python, porque já vem calculado a partir de
    userAccountControl.
    """
    conn = get_connection()
    try:
        ldap_filter = "(&(objectClass=user)(objectCategory=person)"
        if filtro_nome:
            ldap_filter += f"(cn=*{filtro_nome}*)"
        if filtro_cargo:
            ldap_filter += f"(title=*{filtro_cargo}*)"
        if filtro_email:
            ldap_filter += f"(mail=*{filtro_email}*)"
        ldap_filter += ")"

        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=ldap_filter,
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "title", "description", "userAccountControl"],
        )
        usuarios = [_entry_to_usuario_out(e) for e in conn.entries]

        if filtro_ativo is not None:
            usuarios = [u for u in usuarios if u.ativo == filtro_ativo]

        campo_map = {
            "nome": "nome_completo",
            "login": "login",
            "cargo": "cargo",
            "email": "email",
        }
        campo = campo_map.get(ordenar_por, "nome_completo")
        usuarios.sort(key=lambda u: (getattr(u, campo, None) or "").lower(), reverse=(ordem == "desc"))

        return usuarios
    except LDAPException as e:
        logger.error(f"Erro LDAP em listar_usuarios (filtro_nome={filtro_nome}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em listar_usuarios (filtro_nome={filtro_nome}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def buscar_usuario(login: str) -> UsuarioOut:
    """
    Busca um usuário específico no AD pelo login.
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=f"(&(objectClass=user)(sAMAccountName={login}))",
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "title", "description", "userAccountControl"],
        )
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Usuário não encontrado no AD")
        return _entry_to_usuario_out(conn.entries[0])
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em buscar_usuario (login={login}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em buscar_usuario (login={login}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def trocar_senha(login: str, nova_senha: str | None, ip_address: str = None, user_agent: str = None, operator: str = "system") -> str:
    """
    Troca a senha de um usuário no AD. Se não for fornecida, gera uma automática.
    """
    dn_usuario = _resolver_dn(login)
    senha = nova_senha or gerar_senha(8)

    conn = get_connection()
    try:
        ok = conn.extend.microsoft.modify_password(dn_usuario, senha)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao trocar senha: {conn.result}")

        _registrar_atividade(
            operator=operator,
            action="CHANGE_PASSWORD",
            target_user=login,
            details={"senha_gerada": senha if nova_senha is None else "Senha fornecida pelo usuário"},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return senha
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em trocar_senha (login={login}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em trocar_senha (login={login}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def mover_usuario(login: str, nova_ou: str) -> bool:
    """
    Move um usuário para uma nova OU/container (Organizational Unit ou container).

    Args:
        login (str): Login do usuário.
        nova_ou (str): Caminho completo do NOVO PAI (destino) do usuário.
                       Ex: "CN=Inativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
                       ou "CN=Saude,CN=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"

    Returns:
        bool: True se movido com sucesso, False caso contrário.
    """
    dn_atual = _resolver_dn(login)
    usuario = buscar_usuario(login)
    nome_completo = usuario.nome_completo
    novo_rdn = f"CN={nome_completo}"  # modify_dn espera só o NOVO NOME aqui, não o caminho inteiro

    conn = get_connection()
    try:
        # new_superior é o parâmetro correto para mudar de "pasta" (pai) no AD.
        # Passar o caminho completo como segundo argumento (sem new_superior)
        # causa erro de namingViolation, pois o AD tenta interpretar tudo como um nome só.
        conn.modify_dn(dn_atual, novo_rdn, new_superior=nova_ou)
        if conn.result['result'] == 0:
            return True
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao mover usuário: {conn.result}"
            )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em mover_usuario (login={login}, nova_ou={nova_ou}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em mover_usuario (login={login}, nova_ou={nova_ou}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def identificar_candidatos_teste() -> list[dict]:
    """
    Varre usuários do AD e sinaliza contas que aparentam ser de teste,
    com base em padrões comuns (email placeholder 'string', nome/login
    contendo 'teste'/'test'). NÃO deleta nada — apenas lista candidatos
    para revisão manual antes de qualquer remoção.
    """
    conn = get_connection()
    try:
        base = settings.AD_SEARCH_BASE  # cobre toda a OU=DESENVOL, nao so PML
        conn.search(
            search_base=base,
            search_filter="(&(objectClass=user)(objectCategory=person))",
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "userAccountControl"],
        )

        candidatos = []
        for entry in conn.entries:
            cn = str(entry.cn.value) if entry.cn.value else ""
            login = str(entry.sAMAccountName.value) if entry.sAMAccountName.value else ""
            mail = str(entry.mail.value) if entry.mail.value else ""

            motivos = []
            if mail.strip().lower() == "string":
                motivos.append("email é o placeholder padrão 'string' do Swagger")
            if "teste" in cn.lower() or "teste" in login.lower():
                motivos.append("nome/login contém 'teste'")
            if "test" in cn.lower() or "test" in login.lower():
                motivos.append("nome/login contém 'test'")

            if motivos:
                candidatos.append({
                    "login": login,
                    "nome": cn,
                    "email": mail,
                    "motivos": motivos,
                })

        return candidatos
    except LDAPException as e:
        logger.error(f"Erro LDAP em identificar_candidatos_teste: {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em identificar_candidatos_teste: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


def autenticar_usuario(login: str, senha: str, ip_address: str = None, user_agent: str = None) -> bool:
    """
    Autentica um usuário no Active Directory, tentando abrir uma conexão
    NTLM usando o login e a senha informados, e registra a tentativa
    (sucesso ou falha) no banco de auditoria.

    Monta o usuário no formato DOMINIO\\login, que é o exigido pela
    autenticação NTLM (o DN completo do usuário não funciona aqui).
    O domínio é extraído de AD_BIND_USER, que já vem nesse formato.

    Retorna False tanto para credenciais inválidas quanto para falha de
    comunicação com o AD — quem chama essa função (a rota de login) decide
    o status HTTP certo a partir do resultado e do contexto.
    """
    dominio_netbios = settings.AD_BIND_USER.split("\\")[0] if "\\" in settings.AD_BIND_USER else None
    user_ntlm = f"{dominio_netbios}\\{login}" if dominio_netbios else login

    try:
        test_conn = get_connection(user=user_ntlm, password=senha)
        test_conn.unbind()

        _registrar_login(username=login, ip_address=ip_address, user_agent=user_agent, success=True)

        return True

    except LDAPException as e:
        logger.warning(f"Falha de autenticação (credenciais ou AD indisponível) para {login}: {e}")
        _registrar_login(username=login, ip_address=ip_address, user_agent=user_agent, success=False, error_message=str(e))
        return False
    except Exception as e:
        logger.error(f"Erro inesperado em autenticar_usuario (login={login}): {e}")
        _registrar_login(username=login, ip_address=ip_address, user_agent=user_agent, success=False, error_message=str(e))
        return False


def registrar_logout(login: str, ip_address: str = None, user_agent: str = None) -> None:
    """
    Registra o logout de um usuário no banco de auditoria.
    """
    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_logout(
            username=login,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.close()
    except Exception as e:
        logger.error(f"Erro ao registrar logout (login={login}): {e}")
