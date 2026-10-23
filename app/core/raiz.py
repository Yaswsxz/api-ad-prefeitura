"""
Contenção na raiz do LDAP.

Nada se lê nem se escreve fora de OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br.
A raiz é uma constante: não é configurável. A comparação é por componentes
de DN (RDN), nunca por substring. Em caso de dúvida (DN inválido ou vazio),
a operação é recusada.
"""
import os
from typing import Optional

from ldap3.utils.dn import parse_dn

from app.core.config import settings
from app.core.erros_ad import ErroConfiguracao, ErroForaDaRaiz
from app.core.logging_config import logger
from app.core.tls import impressao_fixada

RAIZ_LDAP = "OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"


def componentes_dn(dn: str) -> tuple[tuple[str, str], ...]:
    """
    Componentes RDN do DN, do mais específico para a raiz, normalizados
    (tipo em maiúsculas, valor em minúsculas). Levanta ValueError se o DN
    for vazio ou inválido.
    """
    if not dn or not dn.strip():
        raise ValueError("DN vazio")
    try:
        partes = parse_dn(dn.strip(), escape=False)
    except Exception as e:  # qualquer falha do parser: falha fechada (DN recusado)
        raise ValueError(f"DN inválido: {e}") from e
    return tuple((t.upper(), v.strip().lower()) for t, v, _ in partes)


def dn_dentro(dn: str, base: str = RAIZ_LDAP) -> bool:
    """True se `dn` é a própria `base` ou descende dela, comparando RDN a RDN."""
    try:
        alvo = componentes_dn(dn)
        raiz = componentes_dn(base)
    except ValueError:
        return False
    return len(alvo) >= len(raiz) and alvo[len(alvo) - len(raiz):] == raiz


def garantir_dentro(dn: Optional[str], operacao: str) -> None:
    """Levanta ErroForaDaRaiz (403) se `dn` não estiver dentro de OU=DESENVOL."""
    if not dn or not dn_dentro(dn):
        logger.warning(f"Contenção da raiz: operação '{operacao}' recusada (DN fora de OU=DESENVOL ou vazio)")
        raise ErroForaDaRaiz(
            "A operação alcançaria um objeto fora da raiz permitida (OU=DESENVOL).",
            detalhes={"operacao": operacao},
        )


def mascarar_dn(dn: Optional[str]) -> str:
    """DN para log: mantém as OUs e troca o valor de CN= (nome de pessoa) por <nome>."""
    if not dn:
        return ""
    try:
        partes = parse_dn(dn.strip(), escape=False)
    except Exception:
        return "<dn-invalido>"
    return ",".join(f"{t}=<nome>" if t.upper() == "CN" else f"{t}={v}" for t, v, _ in partes)


def validar_configuracao() -> None:
    """Validações da subida que não precisam do AD: a API não sobe se falharem."""
    if not dn_dentro(settings.AD_PML_BASE):
        raise ErroConfiguracao(
            f"AD_PML_BASE ({settings.AD_PML_BASE}) está fora de {RAIZ_LDAP}: a API não sobe."
        )
    if settings.AD_TLS_CA_FILE and not os.path.isfile(settings.AD_TLS_CA_FILE):
        # O ldap3 ignora em silêncio um arquivo de CA inexistente.
        raise ErroConfiguracao(f"AD_TLS_CA_FILE não encontrado: {settings.AD_TLS_CA_FILE}")
    impressao_fixada()  # AD_TLS_CERT_FIXADO ausente ou que não seja um certificado PEM também impede de subir
