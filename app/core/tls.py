"""
Transporte TLS com o AD: como o certificado do servidor é validado,
o modo legado (TLS 1.0) e o certificado fixado.

Três formas de confiar no servidor, da mais específica para a mais geral:
  1. AD_TLS_CERT_FIXADO: o servidor tem de apresentar exatamente aquele certificado;
  2. AD_TLS_CA_FILE: o certificado tem de ser emitido por aquela CA (e o nome tem de conferir);
  3. nenhuma: repositório de CAs do sistema. Só em desenvolvimento, com AD_ALLOW_INSECURE=true
     e sem as duas acima, a validação é desligada.
"""
import hashlib
import ssl
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ldap3 import Tls

from app.core.config import settings
from app.core.erros_ad import Codigo, ErroConfiguracao, ErroDominio
from app.core.logging_config import logger

_RAIZ_PROJETO = Path(__file__).resolve().parents[2]

# DC legado: TLS 1.0 e cifras de nível de segurança 0 (o OpenSSL 3 recusa o handshake
# MD5+SHA-1 do TLS 1.0 em níveis mais altos). Risco aceito.
_OPCOES_LEGADO = {"version": ssl.PROTOCOL_TLSv1, "ciphers": "ALL:@SECLEVEL=0"}


def config_tls() -> Tls:
    legado = _OPCOES_LEGADO if settings.AD_TLS_LEGADO else {}
    if settings.AD_TLS_CERT_FIXADO:
        # A cadeia não é validada: a confiança vem de conferir o certificado fixado
        # (conferir_certificado), que roda antes de qualquer credencial ser enviada.
        return Tls(validate=ssl.CERT_NONE, **legado)
    if settings.AD_TLS_CA_FILE:
        return Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=settings.AD_TLS_CA_FILE, **legado)
    if settings.AD_ALLOW_INSECURE:
        return Tls(validate=ssl.CERT_NONE, **legado)
    return Tls(validate=ssl.CERT_REQUIRED, **legado)


@lru_cache()
def _impressao_do_arquivo(arquivo: str) -> str:
    caminho = Path(arquivo)
    if not caminho.is_absolute():
        caminho = _RAIZ_PROJETO / caminho
    try:
        der = ssl.PEM_cert_to_DER_cert(caminho.read_text(encoding="ascii"))
    except (OSError, ValueError) as e:
        raise ErroConfiguracao(f"AD_TLS_CERT_FIXADO inválido ({arquivo}): {e}") from e
    return hashlib.sha256(der).hexdigest()


def impressao_fixada() -> Optional[str]:
    """SHA-256 (hexadecimal) do certificado em AD_TLS_CERT_FIXADO; None se não há certificado fixado."""
    if not settings.AD_TLS_CERT_FIXADO:
        return None
    return _impressao_do_arquivo(settings.AD_TLS_CERT_FIXADO)


def conferir_certificado(conn) -> None:
    """
    Com AD_TLS_CERT_FIXADO, exige que o certificado apresentado pelo servidor seja exatamente o
    fixado. Deve rodar antes do bind, para a credencial nunca ir a um servidor não confirmado.
    Uma conexão sem TLS também não confere.
    """
    esperado = impressao_fixada()
    if esperado is None:
        return
    obter = getattr(conn.socket, "getpeercert", None)    # só soquetes TLS têm
    der = obter(binary_form=True) if obter else None
    obtido = hashlib.sha256(der).hexdigest() if der else None
    if obtido == esperado:
        return
    logger.error(
        f"AD_ERRO operacao=certificado obtido_sha256={obtido or '-'} esperado_sha256={esperado}"
    )
    raise ErroDominio(
        "O certificado apresentado pelo Active Directory não é o fixado em AD_TLS_CERT_FIXADO.",
        codigo=Codigo.AD_CERTIFICADO_NAO_CONFERE,
        status_code=503,
        detalhes={"providencia": "Se o certificado do controlador foi renovado, confirme com a "
                                 "Infraestrutura e atualize o arquivo fixado."},
    )
