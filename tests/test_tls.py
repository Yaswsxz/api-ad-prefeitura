"""TLS com o AD: certificado fixado, modo legado e ordem das verificações. Sem rede."""
import ssl
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.core import ldap_connection, tls
from app.core.config import Settings, settings
from app.core.erros_ad import Codigo, ErroConfiguracao, ErroDominio
from app.core.raiz import validar_configuracao

CERT = "config/tls/cegonha.pem"
# SHA-256 do certificado do DC de desenvolvimento, conferido e confirmado em 2026-10-20
IMPRESSAO_DO_DC = "1c1d920b8bdb18cfdfa9a08da55bdc50adb7f40e3ce7f1e88935b2600b23f4db"


def config(**campos) -> Settings:
    return Settings(_env_file=None, **campos)


def definir(monkeypatch, *, fixado="", ca="", inseguro=False, legado=False):
    monkeypatch.setattr(settings, "AD_TLS_CERT_FIXADO", fixado)
    monkeypatch.setattr(settings, "AD_TLS_CA_FILE", ca)
    monkeypatch.setattr(settings, "AD_ALLOW_INSECURE", inseguro)
    monkeypatch.setattr(settings, "AD_TLS_LEGADO", legado)


def der_do_certificado() -> bytes:
    return ssl.PEM_cert_to_DER_cert(Path(CERT).read_text(encoding="ascii"))


def conexao_que_apresenta(der: bytes):
    return SimpleNamespace(socket=SimpleNamespace(getpeercert=lambda binary_form=False: der))


# --- o certificado fixado ----------------------------------------------------------------

def test_impressao_do_certificado_do_dc(monkeypatch):
    definir(monkeypatch)
    assert tls.impressao_fixada() is None
    definir(monkeypatch, fixado=CERT)
    assert tls.impressao_fixada() == IMPRESSAO_DO_DC


def test_certificado_que_confere_passa(monkeypatch):
    definir(monkeypatch, fixado=CERT)
    tls.conferir_certificado(conexao_que_apresenta(der_do_certificado()))


def test_sem_certificado_fixado_nao_confere_nada(monkeypatch):
    definir(monkeypatch)
    tls.conferir_certificado(SimpleNamespace(socket=object()))


@pytest.mark.parametrize("conexao", [
    conexao_que_apresenta(b"outro certificado qualquer"),
    conexao_que_apresenta(b""),
    SimpleNamespace(socket=object()),                      # conexão sem TLS
])
def test_certificado_diferente_ou_sem_tls_e_recusado(monkeypatch, caplog, conexao):
    definir(monkeypatch, fixado=CERT)
    with pytest.raises(ErroDominio) as e:
        tls.conferir_certificado(conexao)
    assert (e.value.status_code, e.value.codigo) == (503, Codigo.AD_CERTIFICADO_NAO_CONFERE)
    assert f"esperado_sha256={IMPRESSAO_DO_DC}" in caplog.text


def test_a_credencial_so_vai_depois_de_conferir_o_certificado(monkeypatch):
    definir(monkeypatch, fixado=CERT)
    encerrada = []

    def bind_proibido():
        raise AssertionError("não pode autenticar antes de conferir o certificado")

    falsa = SimpleNamespace(socket=object(), bind=bind_proibido, unbind=lambda: encerrada.append(True))
    monkeypatch.setattr(ldap_connection, "_abrir", lambda: falsa)
    with pytest.raises(ErroDominio, check=lambda e: e.codigo == Codigo.AD_CERTIFICADO_NAO_CONFERE):
        ldap_connection.get_connection()
    assert encerrada == [True]


# --- como o TLS é configurado -------------------------------------------------------------------

@pytest.mark.parametrize("situacao,validacao", [
    (dict(fixado=CERT), ssl.CERT_NONE),                    # a confiança vem do certificado fixado
    (dict(ca=CERT), ssl.CERT_REQUIRED),
    (dict(inseguro=True), ssl.CERT_NONE),                  # só desenvolvimento
    (dict(), ssl.CERT_REQUIRED),
    (dict(fixado=CERT, inseguro=True), ssl.CERT_NONE),
    (dict(ca=CERT, inseguro=True), ssl.CERT_REQUIRED),     # com CA, a validação não se desliga
])
def test_modo_de_validacao(monkeypatch, situacao, validacao):
    definir(monkeypatch, **situacao)
    assert tls.config_tls().validate == validacao


def test_modo_legado_liga_tls_1_0_e_cifras_de_nivel_0(monkeypatch):
    definir(monkeypatch, fixado=CERT, legado=True)
    legado = tls.config_tls()
    assert legado.version == ssl.PROTOCOL_TLSv1 and "SECLEVEL=0" in legado.ciphers
    definir(monkeypatch, fixado=CERT)
    moderno = tls.config_tls()
    assert moderno.version is None and moderno.ciphers is None


def test_ca_configurada_e_usada(monkeypatch):
    definir(monkeypatch, ca=CERT)
    assert tls.config_tls().ca_certs_file == CERT


# --- configuração ---------------------------------------------------------------------------------------

def test_legado_exige_certificado_fixado_ou_ca():
    with pytest.raises(ValidationError):
        config(AD_TLS_LEGADO=True)
    assert config(AD_TLS_LEGADO=True, AD_TLS_CERT_FIXADO=CERT).AD_TLS_LEGADO
    assert config(AD_TLS_LEGADO=True, AD_TLS_CA_FILE=CERT).AD_TLS_LEGADO


def test_legado_e_aceito_em_producao_com_certificado_fixado():     # limitação aceita
    assert config(AMBIENTE="prod", AD_TLS_LEGADO=True, AD_TLS_CERT_FIXADO=CERT).AMBIENTE == "prod"


@pytest.mark.parametrize("arquivo", ["config/nao_existe.pem", "config/regras.toml"])
def test_certificado_fixado_ausente_ou_invalido_impede_de_subir(monkeypatch, arquivo):
    definir(monkeypatch, fixado=arquivo)
    with pytest.raises(ErroConfiguracao):
        validar_configuracao()


def test_certificado_fixado_valido_nao_impede_de_subir(monkeypatch):
    definir(monkeypatch, fixado=CERT)
    validar_configuracao()
