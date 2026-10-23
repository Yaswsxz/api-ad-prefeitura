"""Auditoria em duas fases e bloqueante, sobre um banco SQLite em memória."""
import json
from contextlib import contextmanager
from dataclasses import replace
from datetime import date
from io import StringIO

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import audit_service
from app.audit_service import Acao, executar_auditado, marcar_inconsistente
from app.core.erros_ad import Codigo, ErroAD, ErroDominio
from app.database import ActivityHistory, Base
from app.services.base_ad import reverter
from tests.ad_falso import CTX


@pytest.fixture
def banco(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)
    monkeypatch.setattr(audit_service, "SessionLocal", sessao)
    return sessao


def linhas(sessao) -> list[tuple]:
    with sessao() as db:
        return [(l.action, l.status, l.username, l.target_user, l.ip_address, json.loads(l.details or "{}"))
                for l in db.query(ActivityHistory).order_by(ActivityHistory.id)]


def auditado(operacao, ctx=CTX, inicial=None, acao=Acao.CRIAR_UNIDADE, alvo="FAZENDA"):
    return executar_auditado(ctx, acao, alvo, inicial or {"entrada": 1}, operacao)


# --- sucesso e falha são registrados -------------------------------------------------------------

def test_sucesso_grava_intencao_e_resultado_na_mesma_linha(banco):
    assert auditado(lambda: ("pronto", {"saida": 2})) == "pronto"
    assert linhas(banco) == [
        ("CREATE_OU", "SUCCESS", "operador-teste", "FAZENDA", "127.0.0.1", {"entrada": 1, "saida": 2}),
    ]


def test_a_intencao_ja_esta_gravada_antes_da_operacao_rodar(banco):
    vista = []

    def operacao():
        vista.extend(linhas(banco))           # a "escrita no AD" ainda não terminou
        return None, {}

    auditado(operacao)
    assert [(l[1], l[5]) for l in vista] == [("INICIADA", {"entrada": 1})]


@pytest.mark.parametrize("erro,esperado", [
    (HTTPException(status_code=409, detail="x"), {"erro": "HTTP_409", "status_http": 409}),
    (ErroAD("negado", codigo=Codigo.AD_PERMISSAO_NEGADA, status_code=502),
     {"erro": Codigo.AD_PERMISSAO_NEGADA, "status_http": 502}),
    (ValueError("bug"), {"erro": "ValueError"}),
])
def test_falha_e_registrada_e_o_erro_original_continua(banco, erro, esperado):
    def operacao():
        raise erro

    with pytest.raises(type(erro)) as e:
        auditado(operacao)
    assert e.value is erro
    (acao, status, _, _, _, detalhes), = linhas(banco)
    assert (acao, status) == ("CREATE_OU", "FAILED")
    assert detalhes == {"entrada": 1, **esperado}


# --- a auditoria bloqueia ----------------------------------------------------------------

def test_sem_registrar_a_intencao_a_operacao_nao_acontece(monkeypatch, caplog):
    def sem_banco():
        raise RuntimeError("banco fora do ar")

    monkeypatch.setattr(audit_service, "SessionLocal", sem_banco)
    executada = []
    with pytest.raises(ErroDominio) as e:
        auditado(lambda: (executada.append(True), {}))
    assert (e.value.status_code, e.value.codigo) == (503, Codigo.AUDITORIA_INDISPONIVEL)
    assert executada == [] and "AUDITORIA_INDISPONIVEL" in caplog.text


@pytest.fixture
def banco_que_falha_ao_fechar(monkeypatch, banco):
    """A 1ª sessão (intenção) funciona; a 2ª (resultado) falha, como um banco que cai no meio."""
    chamadas = []

    def sessao():
        chamadas.append(1)
        if len(chamadas) > 1:
            raise RuntimeError("banco caiu")
        return banco()

    monkeypatch.setattr(audit_service, "SessionLocal", sessao)
    return banco


def arquivo_falso(monkeypatch, falha=False):
    escrito = StringIO()

    @contextmanager
    def abrir(*args, **kwargs):
        if falha:
            raise OSError("disco cheio")
        yield escrito

    monkeypatch.setattr(audit_service, "open", abrir, raising=False)
    return escrito


def test_resultado_nao_gravado_vai_para_a_contingencia_sem_derrubar_a_operacao(
        monkeypatch, banco_que_falha_ao_fechar, caplog):
    escrito = arquivo_falso(monkeypatch)
    assert auditado(lambda: ("feito no AD", {"saida": 2})) == "feito no AD"      # a operação não é desfeita
    fato = json.loads(escrito.getvalue())
    assert (fato["acao"], fato["alvo"], fato["status"], fato["operador"]) == ("CREATE_OU", "FAZENDA", "SUCCESS", "operador-teste")
    assert fato["detalhes"] == {"entrada": 1, "saida": 2}
    assert "INCONSISTENTE" in caplog.text


def test_se_nem_a_contingencia_grava_o_fato_vai_para_o_log(monkeypatch, banco_que_falha_ao_fechar, caplog):
    arquivo_falso(monkeypatch, falha=True)
    assert auditado(lambda: ("ok", {})) == "ok"
    assert "AUDITORIA_PERDIDA" in caplog.text and "CREATE_OU" in caplog.text


# --- inconsistência --------------------------------------------------------------------------------------------

def test_compensacao_que_falha_marca_a_acao_como_inconsistente(banco):
    def falha():
        raise ErroAD("negado", codigo=Codigo.AD_PERMISSAO_NEGADA, status_code=502)

    def operacao():
        reverter(falha, "não foi possível desfazer")
        raise ErroAD("causa original", codigo=Codigo.AD_SCHEMA_INCOMPLETO, status_code=502)

    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        auditado(operacao)
    assert linhas(banco)[0][1] == "INCONSISTENTE"


def test_a_marca_de_inconsistencia_nao_vaza_para_a_acao_seguinte(banco):
    def operacao_que_marca():
        marcar_inconsistente()
        return None, {}

    auditado(operacao_que_marca)
    auditado(lambda: (None, {}))
    assert [l[1] for l in linhas(banco)] == ["INCONSISTENTE", "SUCCESS"]
    marcar_inconsistente()                 # fora de uma ação auditada não faz nada


# --- o que vai nos detalhes ---------------------------------------------------------------------------------------

def test_administrador_informado_entra_nos_detalhes(banco):
    auditado(lambda: (None, {}), ctx=replace(CTX, administrador="Maria Souza"))
    auditado(lambda: (None, {}))
    assert linhas(banco)[0][5]["administrador"] == "Maria Souza"
    assert "administrador" not in linhas(banco)[1][5]


def test_detalhes_nao_serializaveis_nao_quebram_a_auditoria(banco):
    auditado(lambda: (None, {"quando": date(2026, 10, 20)}))
    assert linhas(banco)[0][5]["quando"] == "2026-10-20"
