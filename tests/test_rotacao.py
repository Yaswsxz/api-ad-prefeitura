"""Logs e auditoria em logs/: quebra de arquivos sem apagar, caminhos e contingência mensal."""
import json
import logging
import os
from datetime import date, datetime, timedelta

import pytest

from app import audit_service
from app.audit_service import Acao, Registro
from app.core import rotacao
from app.core.caminhos import RAIZ_PROJETO, com_sufixo_do_mes, resolver
from app.core.config import Settings, settings
from app.core.rotacao import RotacaoSemApagamento
from app.database import url_do_banco
from tests.ad_falso import CTX


class Relogio:
    def __init__(self, dia: date = date(2026, 10, 22)):
        self.agora = datetime(dia.year, dia.month, dia.day, 10, 0, 0)

    def __call__(self) -> datetime:
        return self.agora

    def avancar(self, dias: int = 1) -> None:
        self.agora += timedelta(days=dias)


def escrever(handler, mensagem: str) -> None:
    handler.handle(logging.LogRecord("t", logging.INFO, __file__, 1, mensagem, None, None))


@pytest.fixture
def log(tmp_path):
    relogio = Relogio()
    handler = RotacaoSemApagamento(str(tmp_path / "api_ad.log"), max_bytes=10_000, agora=relogio)
    handler.setFormatter(logging.Formatter("%(message)s"))
    yield handler, relogio, tmp_path
    handler.close()


def arquivos(pasta) -> list[str]:
    return sorted(p.name for p in pasta.iterdir())


def conteudo_cronologico(pasta) -> str:
    """Os arquivos virados (ordem alfabética) e depois o corrente, como uma sequência só."""
    virados = sorted(p for p in pasta.glob("api_ad-*.log"))
    return "".join(p.read_text(encoding="utf-8") for p in [*virados, pasta / "api_ad.log"] if p.exists())


# --- quebra de arquivos ----------------------------------------------------------------------------

def test_no_mesmo_dia_e_abaixo_do_teto_nao_vira(log):
    handler, _, pasta = log
    for i in range(20):
        escrever(handler, f"linha {i}")
    assert arquivos(pasta) == ["api_ad.log"]


def test_vira_ao_mudar_o_dia_e_o_nome_leva_a_data_do_conteudo(log):
    handler, relogio, pasta = log
    escrever(handler, "ontem")
    relogio.avancar()
    escrever(handler, "hoje")
    assert arquivos(pasta) == ["api_ad-2026-10-22.001.log", "api_ad.log"]
    assert (pasta / "api_ad-2026-10-22.001.log").read_text(encoding="utf-8") == "ontem\n"
    assert (pasta / "api_ad.log").read_text(encoding="utf-8") == "hoje\n"


def test_vira_ao_passar_do_teto_no_mesmo_dia(log):
    handler, _, pasta = log
    handler._max_bytes = 100
    for i in range(30):
        escrever(handler, f"linha numero {i:02d}")
    nomes = arquivos(pasta)
    assert "api_ad.log" in nomes and "api_ad-2026-10-22.001.log" in nomes and len(nomes) >= 3
    assert all(n.startswith("api_ad-2026-10-22.") for n in nomes if n != "api_ad.log")


def test_nunca_sobrescreve_nem_remove_arquivo_existente(log):
    handler, relogio, pasta = log
    antigo = pasta / "api_ad-2026-10-22.001.log"
    antigo.write_text("historico que nao pode sumir\n", encoding="utf-8")
    escrever(handler, "a")
    relogio.avancar()
    escrever(handler, "b")
    assert antigo.read_text(encoding="utf-8") == "historico que nao pode sumir\n"
    assert (pasta / "api_ad-2026-10-22.002.log").read_text(encoding="utf-8") == "a\n"


def test_o_conteudo_total_e_preservado_apos_muitas_viradas(log):
    handler, relogio, pasta = log
    handler._max_bytes = 200
    esperado = []
    for dia in range(3):
        for i in range(40):
            mensagem = f"dia {dia} linha {i:03d}"
            esperado.append(mensagem)
            escrever(handler, mensagem)
        relogio.avancar()
    handler.close()
    assert conteudo_cronologico(pasta) == "".join(m + "\n" for m in esperado)
    assert len(arquivos(pasta)) > 6                      # virou várias vezes e nada sumiu


def test_arquivo_de_dia_anterior_existente_vira_no_primeiro_registro(tmp_path):
    corrente = tmp_path / "api_ad.log"
    corrente.write_text("de ontem\n", encoding="utf-8")
    ontem = datetime(2026, 10, 21, 18, 0).timestamp()
    os.utime(corrente, (ontem, ontem))
    handler = RotacaoSemApagamento(str(corrente), max_bytes=10_000, agora=Relogio(date(2026, 10, 22)))
    handler.setFormatter(logging.Formatter("%(message)s"))
    escrever(handler, "de hoje")
    handler.close()
    assert (tmp_path / "api_ad-2026-10-21.001.log").read_text(encoding="utf-8") == "de ontem\n"
    assert corrente.read_text(encoding="utf-8") == "de hoje\n"


def test_arquivo_vazio_nao_gera_arquivo_virado(tmp_path):
    (tmp_path / "api_ad.log").write_text("", encoding="utf-8")
    handler = RotacaoSemApagamento(str(tmp_path / "api_ad.log"), max_bytes=10, agora=Relogio())
    handler.setFormatter(logging.Formatter("%(message)s"))
    escrever(handler, "x")
    handler.close()
    assert arquivos(tmp_path) == ["api_ad.log"]


def test_falha_ao_virar_nao_derruba_e_segue_no_mesmo_arquivo(log, monkeypatch, capsys):
    handler, relogio, pasta = log
    escrever(handler, "ontem")
    relogio.avancar()

    def falha(*_a, **_k):
        raise PermissionError("arquivo em uso")

    monkeypatch.setattr(rotacao.os, "rename", falha)
    escrever(handler, "hoje")                            # não levanta
    escrever(handler, "hoje de novo")                    # não tenta de novo na espera
    assert arquivos(pasta) == ["api_ad.log"]
    assert (pasta / "api_ad.log").read_text(encoding="utf-8") == "ontem\nhoje\nhoje de novo\n"
    erro = capsys.readouterr().err
    assert erro.count("LOG_ROTACAO_FALHOU") == 1 and "PermissionError" in erro


# --- caminhos ------------------------------------------------------------------------------------------

def test_caminhos_relativos_valem_a_partir_da_raiz_do_projeto(tmp_path):
    assert resolver("logs/x.log") == RAIZ_PROJETO / "logs" / "x.log"
    assert resolver(str(tmp_path / "y.log")) == tmp_path / "y.log"


def test_contingencia_ganha_o_mes_no_nome():
    assert com_sufixo_do_mes(resolver("logs/auditoria_contingencia.jsonl"), datetime(2026, 10, 22)) == \
        RAIZ_PROJETO / "logs" / "auditoria_contingencia-2026-10.jsonl"
    assert str(com_sufixo_do_mes(resolver(os.devnull), datetime(2026, 10, 22))) == os.devnull


def test_padroes_apontam_para_logs():
    padrao = Settings(_env_file=None, API_LOG_FILE="", AUDITORIA_CONTINGENCIA_FILE="", DATABASE_URL="")
    assert padrao.arquivo_log == RAIZ_PROJETO / "logs" / "api_ad.log"
    assert padrao.arquivo_contingencia == RAIZ_PROJETO / "logs" / "auditoria_contingencia.jsonl"
    assert padrao.database_url == f"sqlite:///{RAIZ_PROJETO / 'logs' / 'ad_audit.db'}"
    outro = Settings(_env_file=None, LOG_DIR="outros", API_LOG_FILE="", AUDITORIA_CONTINGENCIA_FILE="", DATABASE_URL="")
    assert outro.arquivo_log == RAIZ_PROJETO / "outros" / "api_ad.log"
    assert outro.database_url == f"sqlite:///{RAIZ_PROJETO / 'outros' / 'ad_audit.db'}"


def test_url_do_banco_resolve_sqlite_pela_raiz_e_preserva_o_resto():
    u = url_do_banco("sqlite:///logs/teste/outro.db")
    assert u.database == str(RAIZ_PROJETO / "logs" / "teste" / "outro.db") and (RAIZ_PROJETO / "logs" / "teste").is_dir()
    assert url_do_banco("sqlite:///:memory:").database == ":memory:"
    assert url_do_banco("sqlite:////tmp/absoluto.db").database == "/tmp/absoluto.db"
    assert url_do_banco("postgresql://u:p@host/banco").get_backend_name() == "postgresql"


# --- contingência mensal ---------------------------------------------------------------------------------

def test_contingencia_grava_um_arquivo_por_mes_so_acrescentando(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "AUDITORIA_CONTINGENCIA_FILE", str(tmp_path / "sub" / "contingencia.jsonl"))
    registro = Registro(CTX, Acao.CRIAR_UNIDADE, "FAZENDA", {"ramo": "Direta"})
    registro._contingencia("SUCCESS")
    registro._contingencia("FAILED")
    arquivo = next((tmp_path / "sub").glob("contingencia-*.jsonl"))
    assert arquivo.name == f"contingencia-{audit_service.agora():%Y-%m}.jsonl"
    linhas = [json.loads(l) for l in arquivo.read_text(encoding="utf-8").splitlines()]
    assert [l["status"] for l in linhas] == ["SUCCESS", "FAILED"] and linhas[0]["alvo"] == "FAZENDA"
