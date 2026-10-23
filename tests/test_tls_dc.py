"""
Handshake TLS REAL com o controlador de domínio (marcado `integration`: desligado por padrão).

Só abre o canal e confere o certificado fixado; NÃO faz bind nem nenhuma operação LDAP, então
não envia credencial nem lê dados do AD. Rodar só com autorização:

    .venv/bin/python -m pytest -m integration tests/test_tls_dc.py
"""
from urllib.parse import urlparse

import pytest

from app.core import ldap_connection, tls
from app.core.config import settings

pytestmark = pytest.mark.integration


def test_dc_apresenta_o_certificado_fixado_em_tls_1_0(monkeypatch):
    host = urlparse(settings.AD_SERVER).hostname
    monkeypatch.setattr(settings, "AD_SERVER", f"ldaps://{host}")
    monkeypatch.setattr(settings, "AD_ALLOW_INSECURE", False)
    monkeypatch.setattr(settings, "AD_TLS_CA_FILE", "")
    monkeypatch.setattr(settings, "AD_TLS_LEGADO", True)
    monkeypatch.setattr(settings, "AD_TLS_CERT_FIXADO", "config/tls/cegonha.pem")

    conn = ldap_connection._abrir()
    try:
        assert conn.socket.version() == "TLSv1"
        tls.conferir_certificado(conn)          # levanta ErroDominio se o certificado não confere
    finally:
        ldap_connection._encerrar(conn)
