"""
Service responsável pelas 4 operações de OU que ficaram sob minha
responsabilidade: Criar OU e Alterar/Mover OU, para os 4 ramos
(Direta, Indireta, Terceirizadas, Prepostos).

Estrutura do AD assumida (ver app/core/config.py -> settings.AD_PML_BASE):

    PML
     +-- Operativos
     |    +-- Direta        (cada unidade aqui tem os 4 subcontainers)
     |    |     +-- <UNIDADE>
     |    |          +-- Estagio
     |    |          +-- Carreira
     |    |          +-- Comissionados
     |    |          +-- NaoHumanos
     |    +-- Indireta
     |    +-- Terceirizadas
     |    +-- Prepostos
     +-- Inoperantes        (espelho 1:1 de Operativos, mesma estrutura acima)
     +-- Desincorporados
          +-- Direta / Indireta / Terceirizadas / Prepostos

Criar uma OU cria o nó em Operativos E em Inoperantes ao mesmo tempo
(a cópia em Inoperantes fica vazia, pronta para receber pessoas movidas
no futuro). Alterar só mexe no atributo pmlNomeOrgao. Mover/Desincorporar
só tira o nó de Operativos e leva para Desincorporados (Inoperantes não
é tocado).
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

# Subcontainers fixos que só existem dentro de unidades do ramo Direta
SUBCONTAINERS_DIRETA = ["Estagio", "Carreira", "Comissionados", "NaoHumanos"]


def _dn_ramo(arvore: str, ramo: RamoOU) -> str:
    """DN do container do ramo (ex: CN=Direta,CN=Operativos,<PML_BASE>)."""
    return f"CN={ramo.value},CN={arvore},{settings.AD_PML_BASE}"


def _dn_unidade(arvore: str, ramo: RamoOU, nome: str) -> str:
    """DN de uma unidade específica dentro de um ramo (ex: CN=FAZENDA,...)."""
    return f"CN={nome},{_dn_ramo(arvore, ramo)}"


def _criar_container(conn, dn: str, nome_cn: str) -> None:
    """Cria um container genérico (objectClass=container) no AD, se não existir."""
    conn.search(search_base=dn.split(",", 1)[1], search_filter=f"(&(objectClass=container)(cn={nome_cn}))",
                search_scope=LEVEL)
    if conn.entries:
        return  # já existe, não recria
    ok = conn.add(dn, attributes={"objectClass": ["top", "container"], "cn": nome_cn})
    if not ok:
        raise HTTPException(status_code=500, detail=f"Falha ao criar container '{nome_cn}': {conn.result}")


def _unidade_existe(conn, dn: str) -> bool:
    conn.search(search_base=settings.AD_PML_BASE, search_filter=f"(distinguishedName={dn})", search_scope="SUBTREE")
    return len(conn.entries) > 0


def criar_ou(ramo: RamoOU, dados: OUCreate, ip_address: str = None, user_agent: str = None,
             operator: str = "system") -> OUOut:
    """
    Cria uma nova unidade dentro do ramo indicado, em Operativos e em
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
            raise HTTPException(status_code=409, detail=f"Já existe uma unidade '{dados.nome}' em Operativos/{ramo.value}")

        atributos = {
            "objectClass": ["top", "container"],
            "cn": dados.nome,
            "pmlNomeOrgao": pml_nome_orgao,
        }

        for dn in (dn_operativos, dn_inoperantes):
            ok = conn.add(dn, attributes=atributos)
            if not ok:
                raise HTTPException(status_code=500, detail=f"Falha ao criar unidade em '{dn}': {conn.result}")

            if ramo == RamoOU.DIRETA:
                for sub in SUBCONTAINERS_DIRETA:
                    _criar_container(conn, f"CN={sub},{dn}", sub)

        _registrar_atividade(
            operator=operator,
            action="CREATE_OU",
            target_user=dados.nome,
            details={"ramo": ramo.value, "pml_nome_orgao": pml_nome_orgao,
                     "subcontainers_criados": SUBCONTAINERS_DIRETA if ramo == RamoOU.DIRETA else []},
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


def alterar_ou(ramo: RamoOU, nome: str, dados: OUUpdate, ip_address: str = None, user_agent: str = None,
                operator: str = "system") -> OUOut:
    """
    Altera pmlNomeOrgao de uma unidade. Só é permitido em unidades que
    estão em Operativos (regra do documento: não é possível alterar
    desincorporadas).
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

        ok = conn.modify(dn_operativos, {"pmlNomeOrgao": [(MODIFY_REPLACE, [dados.pml_nome_orgao])]})
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


def mover_ou_desincorporar(ramo: RamoOU, nome: str, dados: OUMover, ip_address: str = None,
                            user_agent: str = None, operator: str = "system") -> OUOut:
    """
    Desincorpora uma unidade: move de Operativos/<ramo> para
    Desincorporados/<ramo>, registrando instrumento e data. Caso raro —
    só para órgão que deixou de existir de fato. Não mexe em Inoperantes.
    """
    dn_atual = _dn_unidade("Operativos", ramo, nome)
    dn_destino_pai = _dn_ramo("Desincorporados", ramo)
    data_hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    conn = get_connection()
    try:
        if not _unidade_existe(conn, dn_atual):
            raise HTTPException(status_code=404, detail=f"Unidade '{nome}' não encontrada em Operativos/{ramo.value}")

        # Garante que o container do ramo já existe em Desincorporados
        _criar_container(conn, dn_destino_pai, ramo.value)

        ok = conn.modify(dn_atual, {
            "pmlDesincorporadoInstrumento": [(MODIFY_REPLACE, [dados.instrumento])],
            "pmlDesincorporadoData": [(MODIFY_REPLACE, [data_hoje])],
        })
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao gravar dados de desincorporação: {conn.result}")

        conn.modify_dn(dn_atual, f"CN={nome}", new_superior=dn_destino_pai)
        if conn.result["result"] != 0:
            raise HTTPException(status_code=500, detail=f"Falha ao mover unidade: {conn.result}")

        dn_final = f"CN={nome},{dn_destino_pai}"

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


def remover_ou_fisicamente(ramo: RamoOU, nome: str, ip_address: str = None, user_agent: str = None,
                            operator: str = "system") -> None:
    """
    Remove fisicamente uma unidade do AD. Só é permitido para unidades que
    já estão em Desincorporados (ou seja: primeiro desincorpora, depois,
    se realmente quiser apagar de vez, remove). Nunca apaga direto de
    Operativos/Inoperantes.
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
