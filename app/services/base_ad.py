"""
Operações sobre o AD comuns aos serviços de unidades e de identidades.

Toda falha do AD (permissão, schema, duplicidade) é levantada, já interpretada, pela conexão
(ErroAD); estas funções não inspecionam `conn.result`.
"""
from datetime import datetime, timezone
from typing import Callable, NamedTuple, Optional

from ldap3 import MODIFY_REPLACE, SUBTREE
from ldap3.utils.conv import escape_filter_chars

from app.audit_service import marcar_inconsistente
from app.core.atributos import texto, uac_de
from app.core.config import settings
from app.core.ldap_connection import buscar
from app.core.logging_config import logger
from app.core.raiz import mascarar_dn
from app.schemas.estrutura import AtoUnidade


class ContaUnidade(NamedTuple):
    dn: str
    login: str
    uac: int


def data_do_ato(ato: AtoUnidade) -> str:
    """Data do ato em ISO-8601; hoje, se não informada."""
    return (ato.data or datetime.now(timezone.utc).date()).strftime("%Y-%m-%d")


def unidade_existe(conn, dn: str) -> bool:
    """O DN existe em algum ponto de AD_PML_BASE? (serve para unidades e OUs internas)"""
    achadas = buscar(
        conn, settings.AD_PML_BASE,
        f"(distinguishedName={escape_filter_chars(dn)})", SUBTREE, ["distinguishedName"],
    )
    return len(achadas) > 0


def gravar_pml(conn, dn: str, valores: dict[str, Optional[str]], avisos: list[str]) -> bool:
    """
    Grava atributos pml* num objeto (valor None limpa o atributo). Com PML_GRAVAR=false
    (temporário, só em desenvolvimento) NÃO grava: avisa no log e na resposta.
    Com a chave ligada e o atributo ausente do schema, a conexão levanta AD_SCHEMA_INCOMPLETO.
    Devolve se gravou.
    """
    if not settings.PML_GRAVAR:
        nomes = ", ".join(valores)
        logger.warning(f"PML_GRAVAR=false: atributos NÃO gravados em {mascarar_dn(dn)}: {nomes}")
        aviso = f"Atributos não gravados no AD (PML_GRAVAR=false): {nomes}"
        if aviso not in avisos:
            avisos.append(aviso)
        return False
    conn.modify(dn, {k: [(MODIFY_REPLACE, [v] if v is not None else [])] for k, v in valores.items()})
    return True


def alterar_uac(conn, dn: str, uac: int) -> None:
    conn.modify(dn, {"userAccountControl": [(MODIFY_REPLACE, [uac])]})


def contas_da_unidade(conn, *dns_unidade: str) -> list[ContaUnidade]:
    """
    Contas em qualquer nível das OUs da unidade informadas (os lados Humanos e NaoHumanos),
    com o userAccountControl atual.
    """
    contas = []
    for dn_unidade in dns_unidade:
        for e in buscar(conn, dn_unidade, "(&(objectCategory=person)(objectClass=user))",
                        SUBTREE, ["sAMAccountName", "userAccountControl"]):
            attrs = e.get("attributes", {})
            contas.append(ContaUnidade(
                dn=e["dn"],
                login=texto(attrs, "sAMAccountName") or e["dn"].split(",", 1)[0][3:],
                uac=uac_de(attrs),
            ))
    return contas


def reverter(desfazer: Callable[[], None], mensagem: str) -> None:
    """
    Executa o desfazer de uma operação composta. Se ele também falhar, registra INCONSISTENTE
    (a causa original continua sendo a que o chamador levanta).
    """
    try:
        desfazer()
    except Exception as e:
        logger.error(f"INCONSISTENTE: {mensagem} [{getattr(e, 'codigo', type(e).__name__)}]")
        marcar_inconsistente()
