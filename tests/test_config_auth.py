"""
Configuração, arquivo de regras, segredo/senha e a API protegida por token.
Nenhuma rota usada aqui chega ao AD.
"""
import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from jose import jwt
from pydantic import ValidationError

import app.main as principal
from app.core import ldap_connection, regras as regras_mod, segredo as segredo_mod
from app.core.auth import verificar_segredo
from app.core.config import PLACEHOLDER_JWT, Settings, settings
from app.core.erros_ad import ErroConfiguracao
from app.core.generators import gerar_senha
from app.core.raiz import validar_configuracao
from app.core.segredo import gerar_hash_segredo
from tests.conftest import SEGREDO_DE_TESTE

CLIENTE = "cliente-de-teste"
client = TestClient(principal.app)


def config(**campos) -> Settings:
    return Settings(_env_file=None, **campos)


# --- configuração -------------------------------------------------------------------------

@pytest.mark.parametrize("campos", [
    {"JWT_SECRET_KEY": "curta"},
    {"JWT_SECRET_KEY": PLACEHOLDER_JWT},
    {"API_CLIENT_SECRET_HASH": "sem-formato"},
    {"API_CLIENT_SECRET_HASH": "bcrypt$1$aa$bb"},
    {"AMBIENTE": "homologacao"},
    {"AMBIENTE": "prod", "AD_ALLOW_INSECURE": True},
    {"AMBIENTE": "prod", "PML_GRAVAR": False},
])
def test_configuracao_invalida_impede_de_subir(campos):
    with pytest.raises(ValidationError):
        config(**campos)


def test_configuracao_valida_e_origens_de_cors():
    assert config(AMBIENTE="PROD", AD_ALLOW_INSECURE=False).AMBIENTE == "prod"
    assert config(CORS_ALLOW_ORIGINS=" http://a , http://b ,").cors_origens == ["http://a", "http://b"]
    assert config(CORS_ALLOW_ORIGINS="").cors_origens == []


def test_validar_configuracao_recusa_base_fora_da_raiz_e_ca_inexistente(monkeypatch):
    validar_configuracao()
    monkeypatch.setattr(settings, "AD_PML_BASE", "OU=PML,DC=londrina,DC=pr,DC=gov,DC=br")
    with pytest.raises(ErroConfiguracao):
        validar_configuracao()
    monkeypatch.undo()
    monkeypatch.setattr(settings, "AD_TLS_CA_FILE", "config/nao_existe.pem")
    with pytest.raises(ErroConfiguracao):
        validar_configuracao()


# --- arquivo de regras ---------------------------------------------------

def test_arquivo_de_regras_do_projeto():
    r = regras_mod.carregar()
    assert r.mutaveis(nao_humano=False) == ("pmlCpf",)
    assert r.mutaveis(nao_humano=True) == ("pmlNaoHumanoTipo",)
    assert r.tipos_nao_humano == ("bot", "impressora", "servico", "outro")


@pytest.mark.parametrize("texto", [
    "isto não é toml =",
    "[nao_humano]\n",                                              # sem tipos
    "[nao_humano]\ntipos = []",                                    # tipos vazios
    '[nao_humano]\ntipos = [1]',                                   # não são textos
    '[nao_humano]\ntipos = ["bot"]\n[atributos_mutaveis]\nhumano = "pmlCpf"',   # não é lista
])
def test_arquivo_de_regras_invalido(texto):
    with pytest.raises(ErroConfiguracao):
        regras_mod.interpretar(texto)


def test_arquivo_de_regras_ausente():
    with pytest.raises(ErroConfiguracao):
        regras_mod.carregar("config/nao_existe.toml")


# --- segredo do cliente e senha inicial ------------------------------------------------------------

def test_hash_do_segredo_ida_e_volta():
    h = gerar_hash_segredo("outro-segredo", iteracoes=1000)
    assert h.startswith("pbkdf2_sha256$1000$")
    assert verificar_segredo("outro-segredo", h)
    assert not verificar_segredo("errado", h)
    assert not verificar_segredo("x", "formato-invalido")


def _credenciais_impressas(capsys) -> tuple[str, str, str]:
    """Roda segredo.main() e devolve (segredo, linha do hash, linha da chave JWT) como impressas."""
    segredo_mod.main()
    linhas = capsys.readouterr().out.splitlines()
    segredo = linhas[linhas.index("SEGREDO DO CLIENTE (entregue ao cliente; não é mostrado de novo):") + 1].strip()
    return (
        segredo,
        next(l.strip() for l in linhas if l.strip().startswith("API_CLIENT_SECRET_HASH=")),
        next(l.strip() for l in linhas if l.strip().startswith("JWT_SECRET_KEY=")),
    )


def test_comando_de_gerar_segredos_imprime_credenciais_validas(capsys, tmp_path):
    segredo, linha_hash, linha_jwt = _credenciais_impressas(capsys)

    # as duas linhas são coladas no .env: lidas como o pydantic-settings as lê, voltam exatas e passam nos validadores
    env = tmp_path / ".env"
    env.write_text(f"{linha_hash}\n{linha_jwt}\n", encoding="utf-8")
    lidos = dotenv_values(env)
    assert lidos["API_CLIENT_SECRET_HASH"].startswith("pbkdf2_sha256$")
    assert verificar_segredo(segredo, lidos["API_CLIENT_SECRET_HASH"])
    assert len(lidos["JWT_SECRET_KEY"]) >= 32
    config(JWT_SECRET_KEY=lidos["JWT_SECRET_KEY"], API_CLIENT_SECRET_HASH=lidos["API_CLIENT_SECRET_HASH"])


def test_comando_de_gerar_segredos_gera_valores_novos_a_cada_vez(capsys):
    assert _credenciais_impressas(capsys) != _credenciais_impressas(capsys)


def test_senha_gerada_atende_a_complexidade_do_ad():
    for _ in range(50):
        senha = gerar_senha()
        assert len(senha) == 12
        assert any(c.isupper() for c in senha) and any(c.islower() for c in senha)
        assert any(c.isdigit() for c in senha) and any(c in "!@#$%&*" for c in senha)


# --- POST /auth/token ----------------------------------------------------------------

def token() -> dict:
    r = client.post("/auth/token", json={"client_id": CLIENTE, "client_secret": SEGREDO_DE_TESTE})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_token_com_chave_correta():
    r = client.post("/auth/token", json={"client_id": CLIENTE, "client_secret": SEGREDO_DE_TESTE})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer" and r.json()["expires_in"] > 0


@pytest.mark.parametrize("corpo", [
    {"client_id": CLIENTE, "client_secret": "errado"},
    {"client_id": "outro", "client_secret": SEGREDO_DE_TESTE},
    {"client_id": CLIENTE, "client_secret": ""},
])
def test_token_recusa_credenciais_invalidas(corpo):
    assert client.post("/auth/token", json=corpo).status_code == 401


def test_token_so_aceita_corpo_json():
    assert client.post("/auth/token").status_code == 422
    r = client.post("/auth/token", params={"client_id": CLIENTE, "client_secret": SEGREDO_DE_TESTE})
    assert r.status_code == 422


# --- tudo protegido por token ---------------------------------------------------------------------------

ATO = {"instrumento": "Portaria 1"}
ROTAS_PROTEGIDAS = [
    ("get", "/versao", None),
    ("get", "/health/detalhes", None),
    ("get", "/auditoria/login-history", None),
    ("get", "/auditoria/activity-history", None),
    ("get", "/auditoria/security-report", None),
    ("get", "/estrutura/unidades/direta", None),
    ("get", "/estrutura/unidades/direta/TESTE", None),
    ("post", "/estrutura/unidades/direta", {"nome": "TESTE"}),
    ("patch", "/estrutura/unidades/direta/TESTE", {"pml_nome_orgao": "Teste"}),
    ("post", "/estrutura/unidades/direta/TESTE/desincorporar", ATO),
    ("post", "/estrutura/unidades/direta/TESTE/reincorporar", ATO),
    ("get", "/identidade/humanos", None),
    ("post", "/identidade/humanos", {"ramo": "direta", "unidade": "TESTE"}),
    ("get", "/identidade/humanos/ana.lima", None),
    ("patch", "/identidade/humanos/ana.lima", {"pmlCpf": "1"}),
    ("delete", "/identidade/humanos/ana.lima", None),
    *[("post", f"/identidade/humanos/ana.lima/{acao}", corpo) for acao, corpo in
      (("bloquear", None), ("desbloquear", None), ("destituir", ATO), ("ativar", ATO), ("transferir", ATO))],
    ("get", "/identidade/naohumanos", None),
    ("post", "/identidade/naohumanos", {"ramo": "direta", "unidade": "TESTE"}),
    ("patch", "/identidade/naohumanos/nhu.a.b", {"pmlNaoHumanoTipo": "bot"}),
    *[("post", f"/identidade/naohumanos/nhu.a.b/{acao}", corpo) for acao, corpo in
      (("bloquear", None), ("desbloquear", None), ("destituir", ATO), ("ativar", ATO), ("transferir", ATO))],
]


@pytest.mark.parametrize("metodo,rota,corpo", ROTAS_PROTEGIDAS)
def test_rotas_exigem_token(metodo, rota, corpo):
    r = getattr(client, metodo)(rota, **({"json": corpo} if corpo is not None else {}))
    assert r.status_code == 401


def test_token_invalido_ou_de_outra_chave_e_recusado():
    assert client.get("/versao", headers={"Authorization": "Bearer lixo"}).status_code == 401
    falso = jwt.encode({"sub": CLIENTE}, "outra-chave-completamente-diferente-123456", algorithm="HS256")
    assert client.get("/versao", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_valido_acessa_rotas_que_nao_tocam_o_ad():
    assert client.get("/versao", headers=token()).status_code == 200
    r = client.get("/auditoria/login-history", headers=token())
    assert r.status_code == 200 and set(r.json()) >= {"total", "items"}


def test_health_publico_nao_toca_no_ad(monkeypatch):
    def proibido():
        raise AssertionError("/health não pode abrir conexão com o AD")
    monkeypatch.setattr(ldap_connection, "get_connection", proibido)
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_legado_de_escopo_de_dominio_nao_existe_mais():
    for metodo, rota in [("post", "/usuarios/login"), ("post", "/usuarios/auth"), ("get", "/usuarios"),
                         ("post", "/usuarios/x/trocar-senha"), ("post", "/identidade/humanos/x/mover")]:
        assert getattr(client, metodo)(rota).status_code in (404, 405)


# --- validação de entrada, antes de qualquer AD -----------------------------------------------------------

def test_ramo_desconhecido_e_404_e_nao_422():
    r = client.post("/estrutura/unidades/inexistente", json={"nome": "TESTE"}, headers=token())
    assert r.status_code == 404


@pytest.mark.parametrize("nome", ["A,OU=B", "A=B", "FAZ*ENDA", "A\\B", "DIRETA", "x"])
def test_nome_de_unidade_invalido_e_422(nome):
    r = client.post("/estrutura/unidades/direta", json={"nome": nome}, headers=token())
    assert r.status_code == 422
