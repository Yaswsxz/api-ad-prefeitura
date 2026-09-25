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

from ldap3 import MODIFY_REPLACE
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
    """DN da OU do ramo (ex: OU=Direta,OU=Operativos,<PML_BASE>)."""
    return f"OU={ramo.value},OU={arvore},{settings.AD_PML_BASE}"


def _dn_unidade(arvore: str, ramo: RamoOU, nome: str) -> str:
    """DN de uma unidade específica dentro de um ramo (ex: OU=FAZENDA,...)."""
    return f"OU={nome},{_dn_ramo(arvore, ramo)}"


def _criar_container(conn, dn: str, nome_ou: str) -> None:
    """
    Cria uma Organizational Unit no AD. Idempotente: tenta criar direto
    e, se o AD responder que já existe, trata como sucesso (em vez de
    checar antes com um search — que pode ficar inconsistente com o
    estado real por atraso de replicação ou resquício de tentativa
    anterior, causando falso negativo e erro na hora de criar).
    """
    ok = conn.add(dn, attributes={"objectClass": ["top", "organizationalUnit"], "ou": nome_ou})
    if ok:
        return
    if conn.result.get("description") == "entryAlreadyExists":
        return
    raise HTTPException(status_code=500, detail=f"Falha ao criar OU '{nome_ou}': {conn.result}")


def _unidade_existe(conn, dn: str) -> bool:
    conn.search(search_base=settings.AD_PML_BASE, search_filter=f"(distinguishedName={dn})", search_scope="SUBTREE")
    return len(conn.entries) > 0


def _schema_tem_atributo(conn, nome_atributo: str) -> bool:
    """Verifica se um atributo (customizado ou não) existe de verdade no schema do AD."""
    try:
        schema = conn.server.schema
        if schema and schema.attribute_types:
            for attr_type in schema.attribute_types.values():
                nomes = attr_type.name if isinstance(attr_type.name, list) else [attr_type.name]
                if nomes and nome_atributo in nomes:
                    return True
    except Exception as e:
        logger.warning(f"Não foi possível checar o schema do AD para '{nome_atributo}': {e}")
    return False


def _atributo_nome_orgao(conn) -> str:
    """
    O documento da API sugere gravar o nome descritivo do órgão no
    atributo customizado 'pmlNomeOrgao' — mas esse atributo só existe
    de verdade se alguém já estendeu o schema do AD pra criá-lo (isso
    exige permissão de Schema Admin, não é algo que a API resolve
    sozinha). Enquanto isso não acontece, usamos 'description' (atributo
    padrão que todo objeto do AD já tem) como alternativa temporária —
    e volta a usar 'pmlNomeOrgao' automaticamente assim que o schema for
    estendido, sem precisar mexer em código de novo.
    """
    return "pmlNomeOrgao" if _schema_tem_atributo(conn, "pmlNomeOrgao") else "description"


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
        unidade_ja_existe = _unidade_existe(conn, dn_operativos)

        if not unidade_ja_existe:
            atributo_nome_orgao = _atributo_nome_orgao(conn)
            if atributo_nome_orgao == "description":
                logger.warning(
                    "Atributo 'pmlNomeOrgao' não existe no schema do AD — gravando o nome "
                    "descritivo em 'description' até o schema ser estendido."
                )

            atributos = {
                "objectClass": ["top", "organizationalUnit"],
                "ou": dados.nome,
                atributo_nome_orgao: pml_nome_orgao,
            }

            for dn in (dn_operativos, dn_inoperantes):
                ok = conn.add(dn, attributes=atributos)
                if not ok:
                    raise HTTPException(status_code=500, detail=f"Falha ao criar unidade em '{dn}': {conn.result}")

        # Garante os 4 subcontainers da Direta mesmo quando a unidade já
        # existia (conserta o caso de uma tentativa anterior ter criado a
        # unidade sem eles, por exemplo por causa de um erro no meio do
        # caminho) — _criar_container já é idempotente, não recria à toa.
        if ramo == RamoOU.DIRETA:
            for dn in (dn_operativos, dn_inoperantes):
                for sub in SUBCONTAINERS_DIRETA:
                    _criar_container(conn, f"OU={sub},{dn}", sub)

        if unidade_ja_existe:
            raise HTTPException(status_code=409, detail=f"Já existe uma unidade '{dados.nome}' em Operativos/{ramo.value}")

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

        ok = conn.modify(dn_operativos, {_atributo_nome_orgao(conn): [(MODIFY_REPLACE, [dados.pml_nome_orgao])]})
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

        # Idem ao pmlNomeOrgao: esses 2 atributos customizados podem não
        # existir ainda no schema do AD. Se não existirem, acrescenta a
        # informação ao 'description' (mesmo atributo padrão já usado
        # como alternativa pro pmlNomeOrgao), sem apagar o que já tinha.
        if _schema_tem_atributo(conn, "pmlDesincorporadoInstrumento") and _schema_tem_atributo(conn, "pmlDesincorporadoData"):
            mudancas = {
                "pmlDesincorporadoInstrumento": [(MODIFY_REPLACE, [dados.instrumento])],
                "pmlDesincorporadoData": [(MODIFY_REPLACE, [data_hoje])],
            }
        else:
            logger.warning(
                "Atributos 'pmlDesincorporadoInstrumento'/'pmlDesincorporadoData' não existem no "
                "schema do AD — acrescentando ao 'description' até o schema ser estendido."
            )
            conn.search(search_base=settings.AD_PML_BASE, search_filter=f"(distinguishedName={dn_atual})",
                        search_scope="SUBTREE", attributes=["description"])
            descricao_atual = ""
            if conn.entries and conn.entries[0].description.value:
                descricao_atual = str(conn.entries[0].description.value)
            novo_valor = f"{descricao_atual} | Desincorporado em {data_hoje}: {dados.instrumento}".strip(" |")
            mudancas = {"description": [(MODIFY_REPLACE, [novo_valor])]}

        ok = conn.modify(dn_atual, mudancas)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao gravar dados de desincorporação: {conn.result}")

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
