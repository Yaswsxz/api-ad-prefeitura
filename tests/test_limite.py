"""Limite de tentativas falhas em POST /auth/token (R3). Sem AD."""
import pytest
from fastapi.testclient import TestClient

import app.main as principal
from app.core import limite
from app.core.config import settings
from app.core.erros_ad import Codigo
from app.core.limite import LimiteDeFalhas
from tests.conftest import SEGREDO_DE_TESTE

client = TestClient(principal.app)
CERTO = {"client_id": "cliente-de-teste", "client_secret": SEGREDO_DE_TESTE}


class Relogio:
    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


# --- o limitador ------------------------------------------------------------------------------------

def test_bloqueia_ao_atingir_o_maximo_e_libera_quando_a_janela_passa():
    relogio = Relogio()
    lim = LimiteDeFalhas(maximo=3, janela=100, relogio=relogio)
    for _ in range(2):
        lim.registrar_falha("a")
    assert lim.segundos_restantes("a") == 0
    lim.registrar_falha("a")
    assert lim.segundos_restantes("a") == 100
    relogio.agora += 60
    assert lim.segundos_restantes("a") == 40
    relogio.agora += 40
    assert lim.segundos_restantes("a") == 0


def test_chaves_sao_independentes_e_zerar_libera():
    lim = LimiteDeFalhas(maximo=1, janela=100, relogio=Relogio())
    lim.registrar_falha("a")
    assert lim.segundos_restantes("a") > 0 and lim.segundos_restantes("b") == 0
    lim.zerar("a")
    assert lim.segundos_restantes("a") == 0


def test_a_espera_conta_so_a_falha_que_precisa_sair_da_janela():
    relogio = Relogio()
    lim = LimiteDeFalhas(maximo=2, janela=100, relogio=relogio)
    lim.registrar_falha("a")
    relogio.agora += 30
    lim.registrar_falha("a")
    relogio.agora += 30
    lim.registrar_falha("a")                 # 3 falhas (em 0, 30 e 60 s), limite 2: precisam sair a 1ª e a 2ª
    assert lim.segundos_restantes("a") == 70    # a 2ª (30 s) sai aos 130 s; já se passaram 60


def test_a_memoria_e_limitada():
    lim = LimiteDeFalhas(maximo=1, janela=100, relogio=Relogio(), capacidade=3)
    for chave in "abcd":
        lim.registrar_falha(chave)
    assert lim.segundos_restantes("a") == 0 and lim.segundos_restantes("d") > 0     # a mais antiga saiu


# --- na rota ------------------------------------------------------------------------------------------------------

def errado(cliente="cliente-de-teste"):
    return client.post("/auth/token", json={"client_id": cliente, "client_secret": "errado"})


def test_depois_de_muitas_falhas_responde_429_ate_com_o_segredo_certo():
    for _ in range(settings.AUTH_MAX_FALHAS):
        assert errado().status_code == 401
    r = client.post("/auth/token", json=CERTO)
    corpo = r.json()
    assert (r.status_code, corpo["codigo"]) == (429, Codigo.MUITAS_TENTATIVAS)
    assert int(r.headers["retry-after"]) == corpo["detalhes"]["aguarde_segundos"] > 0


def test_um_sucesso_zera_as_falhas_do_cliente():
    for _ in range(settings.AUTH_MAX_FALHAS - 1):
        errado()
    assert client.post("/auth/token", json=CERTO).status_code == 200
    for _ in range(settings.AUTH_MAX_FALHAS - 1):
        assert errado().status_code == 401


def test_o_mesmo_ip_tentando_muitos_clientes_tambem_e_barrado():
    for i in range(settings.AUTH_MAX_FALHAS * 4):
        assert errado(f"cliente-{i}").status_code == 401
    assert errado("cliente-novo").status_code == 429


def test_o_limite_nao_atinge_quem_nao_falhou():
    assert limite.por_ip.segundos_restantes("ip:testclient") == 0
    assert client.post("/auth/token", json=CERTO).status_code == 200
