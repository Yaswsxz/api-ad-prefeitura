"""Corpo de erro único, request_id e X-Administrador. Sem AD."""
import logging
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.main as principal
from app.core.contexto import LIMITE_ADMINISTRADOR, Contexto, contexto, limpar_administrador
from app.core.erros_ad import Codigo, registrar_handlers
from app.core.logging_config import _FiltroRequestId, request_id_var
from app.core.requisicao import CABECALHO, instalar_request_id
from tests.conftest import SEGREDO_DE_TESTE

client = TestClient(principal.app, raise_server_exceptions=False)


def token() -> dict:
    r = client.post("/auth/token", json={"client_id": "cliente-de-teste", "client_secret": SEGREDO_DE_TESTE})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def corpo_ok(r) -> dict:
    corpo = r.json()
    assert set(corpo) == {"codigo", "mensagem", "detalhes"}
    return corpo


# --- um só formato de erro ----------------------------------------------------------------------

def test_401_tem_o_corpo_unico_e_mantem_o_cabecalho_www_authenticate():
    r = client.get("/versao")
    corpo = corpo_ok(r)
    assert (r.status_code, corpo["codigo"]) == (401, Codigo.NAO_AUTENTICADO)
    assert r.headers["www-authenticate"] == "Bearer"
    assert corpo["detalhes"]["request_id"] == r.headers[CABECALHO]


@pytest.mark.parametrize("metodo,rota,status,codigo", [
    ("get", "/rota/que/nao/existe", 404, Codigo.NAO_ENCONTRADO),
    ("delete", "/health", 405, Codigo.METODO_NAO_PERMITIDO),
])
def test_erros_http_comuns(metodo, rota, status, codigo):
    r = getattr(client, metodo)(rota)
    assert (r.status_code, corpo_ok(r)["codigo"]) == (status, codigo)


def test_ramo_desconhecido_segue_o_mesmo_formato():
    r = client.post("/estrutura/unidades/inexistente", json={"nome": "TESTE"}, headers=token())
    assert (r.status_code, corpo_ok(r)["codigo"]) == (404, Codigo.NAO_ENCONTRADO)


def test_validacao_lista_campo_e_mensagem_sem_devolver_o_valor_enviado():
    r = client.post("/estrutura/unidades/direta", json={"nome": "A,OU=B"}, headers=token())
    corpo = corpo_ok(r)
    assert (r.status_code, corpo["codigo"]) == (422, Codigo.VALIDACAO)
    assert corpo["detalhes"]["erros"][0]["campo"] == "body.nome"
    assert "A,OU=B" not in r.text and "input" not in r.text


def test_excecao_inesperada_vira_500_sem_vazar_a_causa():
    app = FastAPI()
    registrar_handlers(app)
    instalar_request_id(app)

    @app.get("/boom")
    def boom():
        raise RuntimeError("segredo-interno")

    r = TestClient(app, raise_server_exceptions=False).get("/boom")
    corpo = corpo_ok(r)
    assert (r.status_code, corpo["codigo"]) == (500, Codigo.ERRO_INTERNO)
    assert "segredo-interno" not in r.text
    assert corpo["detalhes"]["request_id"] == r.headers[CABECALHO]


# --- request_id ---------------------------------------------------------------------------------------

def test_todo_resposta_traz_o_request_id():
    a, b = client.get("/health"), client.get("/health")
    assert len(a.headers[CABECALHO]) == 32 and a.headers[CABECALHO] != b.headers[CABECALHO]


def test_request_id_valido_do_cliente_e_aceito_e_o_invalido_e_trocado():
    assert client.get("/health", headers={CABECALHO: "abc-123_XYZ.01"}).headers[CABECALHO] == "abc-123_XYZ.01"
    for ruim in ("curto", "com espaco no meio", "x" * 65, "invalido!@#$%^"):
        assert client.get("/health", headers={CABECALHO: ruim}).headers[CABECALHO] != ruim


def test_o_filtro_de_log_poe_o_request_id_no_registro():
    registro = logging.LogRecord("api_ad", logging.INFO, __file__, 1, "msg", None, None)
    marca = request_id_var.set("req-de-teste")
    try:
        assert _FiltroRequestId().filter(registro) and registro.request_id == "req-de-teste"
    finally:
        request_id_var.reset(marca)


# --- X-Administrador -----------------------------------------------------------------------------------

@pytest.mark.parametrize("entrada,esperado", [
    (None, None), ("", None), ("   ", None), ("\x00\x01", None),
    ("Maria Silva", "Maria Silva"),
    ("  Maria\x00Silva\n", "Maria Silva"),
    ("x" * 150, "x" * LIMITE_ADMINISTRADOR),
])
def test_administrador_e_sanitizado(entrada, esperado):
    assert limpar_administrador(entrada) == esperado


def test_contexto_reune_operador_ip_user_agent_e_administrador():
    requisicao = SimpleNamespace(client=SimpleNamespace(host="10.0.0.5"), headers={"user-agent": "pytest"})
    assert contexto(requisicao, "cliente", " Ana Souza ") == Contexto("cliente", "10.0.0.5", "pytest", "Ana Souza")
    assert contexto(SimpleNamespace(client=None, headers={}), "cliente", None) == Contexto("cliente")
