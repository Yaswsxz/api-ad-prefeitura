"""
Service responsável pelas 4 operações de OU que ficaram sob minha
responsabilidade: Criar OU e Alterar/Mover OU, para os 4 ramos
(Direta, Indireta, Terceirizadas, Prepostos).

Estrutura do AD assumida (ver app/core/config.py -> settings.AD_PML_BASE):

    OU=PML
     +-- OU=Operativos
     |    +-- OU=Direta        (cada unidade aqui tem 4 subcontainers CN=)
     |    |     +-- OU=<UNIDADE>
     |    |          +-- CN=Estagio         (container)
     |    |          +-- CN=Carreira        (container)
     |    |          +-- CN=Comissionados   (container)
     |    |          +-- CN=NaoHumanos      (container)
     |    +-- OU=Indireta
     |    +-- OU=Terceirizadas
     |    +-- OU=Prepostos
     +-- OU=Inoperantes        (espelho 1:1 de Operativos)
     +-- OU=Desincorporados    (sem ramos fixos; nascem sob demanda)

Regra de tipos:
  - Árvores, ramos e unidades  →  OU  (organizationalUnit)
  - Subcontainers da Direta    →  CN  (container)
"""

from ldap3 import MODIFY_REPLACE, LEVEL
from ldap3.core.exceptions import LDAPException
from fastapi import HTTPException
from datetime import datetime, timezone

from app.core.config import settings
from app.core.ldap_connection import get_connection
from app.core.logging_config import logger
from app.schemas.estrutura import RamoOU, OUCreate, OUUpdate, OUMover, OUOut
from app.services.ad_service import _registrar_atividade

# Subcontainers fixos que só existem dentro de unidades do ramo Direta.
# Estes continuam sendo containers (objectClass=container), não OUs.
SUBCONTAINERS_DIRETA = ["Estagio", "Carreira", "Comissionados", "NaoHumanos"]


# =============================================================================
# DN helpers
# =============================================================================

def _dn_ramo(arvore: str, ramo: RamoOU) -> str:
    """DN do ramo dentro de uma árvore: OU=<ramo>,OU=<arvore>,<PML_BASE>."""
    return f"OU={ramo.value},OU={arvore},{settings.AD_PML_BASE}"


def _dn_unidade(arvore: str, ramo: RamoOU, nome: str) -> str:
    """DN de uma unidade: OU=<nome>,OU=<ramo>,OU=<arvore>,<PML_BASE>."""
    return f"OU={nome},{_dn_ramo(arvore, ramo)}"


# =============================================================================
# Existência
# =============================================================================

def _existe_filho(conn, parent_dn: str, nome: str) -> bool:
    """
    Verifica se existe um filho direto com cn=<nome> OU ou=<nome> sob parent_dn.
    Aceita os dois porque containers usam cn= e OUs usam ou=.
    """
    conn.search(
        search_base=parent_dn,
        search_filter=f"(|(cn={nome})(ou={nome}))",
        search_scope=LEVEL,
    )
    return len(conn.entries) > 0


def _unidade_existe(conn, dn: str) -> bool:
    """Verifica se um DN específico existe em qualquer ponto do PML."""
    conn.search(
        search_base=settings.AD_PML_BASE,
        search_filter=f"(distinguishedName={dn})",
        search_scope="SUBTREE",
    )
    return len(conn.entries) > 0


# =============================================================================
# Criação — OU e container separados
# =============================================================================

def _criar_ou(conn, parent_dn: str, nome: str, extras: dict = None) -> str:
    """
    Cria uma Organizational Unit (OU) sob parent_dn.
    Retorna o DN criado. Lança HTTPException se falhar.
    """
    dn = f"OU={nome},{parent_dn}"
    attrs = {
        "objectClass": ["top", "organizationalUnit"],
        "ou": nome,
    }
    if extras:
        attrs.update(extras)

    ok = conn.add(dn, attributes=attrs)
    if not ok:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao criar OU '{dn}': {conn.result}",
        )
    return dn


def _criar_container(conn, parent_dn: str, nome: str) -> str:
    """
    Cria um container (objectClass=container) sob parent_dn.
    Usado APENAS para os 4 subcontainers fixos da Direta
    (Estagio, Carreira, Comissionados, NaoHumanos).
    Retorna o DN criado.
    """
    dn = f"CN={nome},{parent_dn}"
    ok = conn.add(dn, attributes={
        "objectClass": ["top", "container"],
        "cn": nome,
    })
    if not ok:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao criar container '{dn}': {conn.result}",
        )
    return dn


def _garantir_ou(conn, parent_dn: str, nome: str, extras: dict = None) -> str:
    """Cria a OU se não existir; devolve o DN dela em qualquer caso."""
    if _existe_filho(conn, parent_dn, nome):
        return f"OU={nome},{parent_dn}"
    return _criar_ou(conn, parent_dn, nome, extras)


def _garantir_container(conn, parent_dn: str, nome: str) -> str:
    """Cria o container se não existir; devolve o DN dele em qualquer caso."""
    if _existe_filho(conn, parent_dn, nome):
        return f"CN={nome},{parent_dn}"
    return _criar_container(conn, parent_dn, nome)


# =============================================================================
# Operação: Criar OU
# =============================================================================

def criar_ou(ramo: RamoOU, dados: OUCreate, ip_address: str = None, user_agent: str = None,
             operator: str = "system") -> OUOut:
    """
    Cria uma nova unidade dentro do ramo indicado, em Operativos E em
    Inoperantes (espelhado). Se o ramo for Direta, também cria os 4
    subcontainers fixos (Estagio, Carreira, Comissionados, NaoHumanos)
    nas duas cópias.
    """
    dn_operativos = _dn_unidade("Operativos", ramo, dados.nome)
    dn_inoperantes = _dn_unidade("Inoperantes", ramo, dados.nome)
    pml_nome_orgao = dados.pml_nome_orgao or dados.nome
    conn = get_connection()
    try:
        if _unidade_existe(conn, dn_operativos):
            raise HTTPException(
                status_code=409,
                detail=f"Já existe uma unidade '{dados.nome}' em Operativos/{ramo.value}",
            )

        # 1. Cria a unidade em Operativos (com pmlNomeOrgao)
                # 1. Cria a unidade em Operativos
        # ⚠️ pmlNomeOrgao ainda não existe no schema do AD.
        # Quando for criado pelo admin do domínio, descomente a linha abaixo
        # e remova o `extras=None`.
        extras = None
        # extras = {"pmlNomeOrgao": pml_nome_orgao}
        _criar_ou(conn, _dn_ramo("Operativos", ramo), dados.nome, extras=extras)

        # 2. Cria a unidade espelhada em Inoperantes (sem pmlNomeOrgao)
        _criar_ou(conn, _dn_ramo("Inoperantes", ramo), dados.nome)

        # 3. Se for Direta, cria os 4 subcontainers (CN=) em ambas as cópias
        if ramo == RamoOU.DIRETA:
            for dn_unidade in (dn_operativos, dn_inoperantes):
                for sub in SUBCONTAINERS_DIRETA:
                    _garantir_container(conn, dn_unidade, sub)

        _registrar_atividade(
            operator=operator,
            action="CREATE_OU",
            target_user=dados.nome,
            details={
                "ramo": ramo.value,
                "pml_nome_orgao": pml_nome_orgao,
                "subcontainers_criados": SUBCONTAINERS_DIRETA if ramo == RamoOU.DIRETA else [],
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return OUOut(
            nome=dados.nome,
            ramo=ramo,
            pml_nome_orgao=pml_nome_orgao,
            distinguished_name_operativos=dn_operativos,
            distinguished_name_inoperantes=dn_inoperantes,
        )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em criar_ou (ramo={ramo}, nome={dados.nome}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em criar_ou (ramo={ramo}, nome={dados.nome}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


# =============================================================================
# Operação: Alterar OU
# =============================================================================

def alterar_ou(ramo: RamoOU, nome: str, dados: OUUpdate, ip_address: str = None,
                user_agent: str = None, operator: str = "system") -> OUOut:
    """
    Altera pmlNomeOrgao de uma unidade. Só é permitido em unidades que
    estão em Operativos (regra: não é possível alterar desincorporadas).
    """
    dn_operativos = _dn_unidade("Operativos", ramo, nome)

    conn = get_connection()
    try:
        if not _unidade_existe(conn, dn_operativos):
            raise HTTPException(
                status_code=404,
                detail=f"Unidade '{nome}' não encontrada em Operativos/{ramo.value} "
                       f"(não é possível alterar unidades desincorporadas)",
            )

        ok = conn.modify(dn_operativos, {
            "pmlNomeOrgao": [(MODIFY_REPLACE, [dados.pml_nome_orgao])],
        })
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao alterar unidade: {conn.result}")

        _registrar_atividade(
            operator=operator,
            action="UPDATE_OU",
            target_user=nome,
            details={"ramo": ramo.value, "pml_nome_orgao": dados.pml_nome_orgao},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return OUOut(
            nome=nome,
            ramo=ramo,
            pml_nome_orgao=dados.pml_nome_orgao,
            distinguished_name_operativos=dn_operativos,
        )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em alterar_ou (ramo={ramo}, nome={nome}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em alterar_ou (ramo={ramo}, nome={nome}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


# =============================================================================
# Operação: Desincorporar OU
# =============================================================================

def mover_ou_desincorporar(ramo: RamoOU, nome: str, dados: OUMover, ip_address: str = None,
                            user_agent: str = None, operator: str = "system") -> OUOut:
    """
    Desincorpora uma unidade: move de Operativos/<ramo> para
    Desincorporados/<ramo>, registrando instrumento e data.
    Não mexe em Inoperantes.
    """
    dn_atual = _dn_unidade("Operativos", ramo, nome)
    dn_destino_pai = _dn_ramo("Desincorporados", ramo)
    data_hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        if not _unidade_existe(conn, dn_atual):
            raise HTTPException(status_code=404, detail=f"Unidade '{nome}' não encontrada em Operativos/{ramo.value}")

        # Garante que o ramo destino existe em Desincorporados (cria como OU)
        _garantir_ou(conn, f"OU=Desincorporados,{settings.AD_PML_BASE}", ramo.value)

        ok = conn.modify(dn_atual, {
            "pmlDesincorporadoInstrumento": [(MODIFY_REPLACE, [dados.instrumento])],
            "pmlDesincorporadoData": [(MODIFY_REPLACE, [data_hoje])],
        })
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao gravar dados de desincorporação: {conn.result}")

        # RDN é OU=<nome> (mudou de CN= para OU=)
        conn.modify_dn(dn_atual, f"OU={nome}", new_superior=dn_destino_pai)
        if conn.result["result"] != 0:
            raise HTTPException(status_code=500, detail=f"Falha ao mover unidade: {conn.result}")

        dn_final = f"OU={nome},{dn_destino_pai}"

        _registrar_atividade(
            operator=operator,
            action="DESINCORPORAR_OU",
            target_user=nome,
            details={"ramo": ramo.value, "instrumento": dados.instrumento, "data": data_hoje},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return OUOut(nome=nome, ramo=ramo, distinguished_name_operativos=dn_final)
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em mover_ou_desincorporar (ramo={ramo}, nome={nome}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em mover_ou_desincorporar (ramo={ramo}, nome={nome}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:
        conn.unbind()


# =============================================================================
# Operação: Remover OU fisicamente
# =============================================================================

def remover_ou_fisicamente(ramo: RamoOU, nome: str, ip_address: str = None,
                            user_agent: str = None, operator: str = "system") -> None:
    """
    Remove fisicamente uma unidade do AD. Só é permitido para unidades que
    já estão em Desincorporados (primeiro desincorpora, depois remove).
    """
    dn = _dn_unidade("Desincorporados", ramo, nome)

    conn = get_connection()
    try:
        if not _unidade_existe(conn, dn):
            raise HTTPException(
                status_code=404,
                detail=f"Unidade '{nome}' não encontrada em Desincorporados/{ramo.value} "
                       f"(só é possível remover fisicamente unidades já desincorporadas)",
            )

        ok = conn.delete(dn)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao remover unidade: {conn.result}")

        _registrar_atividade(
            operator=operator,
            action="DELETE_OU",
            target_user=nome,
            details={"ramo": ramo.value, "dn": dn},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except HTTPException:
        raise
    except LDAPException as e:
        logger.error(f"Erro LDAP em remover_ou_fisicamente (ramo={ramo}, nome={nome}): {e}")
        raise HTTPException(status_code=503, detail="Erro de comunicação com o Active Directory") from e
    except Exception as e:
        logger.error(f"Erro inesperado em remover_ou_fisicamente (ramo={ramo}, nome={nome}): {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação") from e
    finally:

        conn.unbind()