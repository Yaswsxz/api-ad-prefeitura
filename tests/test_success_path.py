import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


# --- Teste de caminho de sucesso (login válido + ação concluída) ---
#
# Usa um usuário de teste dedicado no AD (settings.TEST_AD_USER /
# TEST_AD_PASSWORD, vindos do .env — nunca hardcoded aqui). Se essas
# variáveis não estiverem configuradas no ambiente (ex: em outra
# máquina ou no CI), o teste é pulado em vez de falhar, já que ele
# depende de acesso real ao AD de teste.

AD_TESTE_DISPONIVEL = bool(settings.TEST_AD_USER and settings.TEST_AD_PASSWORD)

pytestmark_skip_sem_ad = pytest.mark.skipif(
    not AD_TESTE_DISPONIVEL,
    reason="TEST_AD_USER/TEST_AD_PASSWORD não configurados no .env — pulando teste que depende do AD real",
)


@pytestmark_skip_sem_ad
def test_login_valido_gera_token():
    """
    Login com o usuário de teste dedicado deve funcionar e devolver
    um token JWT utilizável (não vazio, tipo 'bearer').
    """
    response = client.post(
        "/usuarios/login",
        data={"username": settings.TEST_AD_USER, "password": settings.TEST_AD_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytestmark_skip_sem_ad
def test_caminho_sucesso_login_e_acao_concluida():
    """
    Caminho de sucesso completo: login válido -> token -> chamada a um
    endpoint protegido (listar setores) usando esse token -> confirma
    que a ação foi concluída com dados reais vindos do AD.
    """
    # 1. Login com o usuário de teste dedicado
    login_response = client.post(
        "/usuarios/login",
        data={"username": settings.TEST_AD_USER, "password": settings.TEST_AD_PASSWORD},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 2. Usa o token para chamar um endpoint protegido
    headers = {"Authorization": f"Bearer {token}"}
    setores_response = client.get("/usuarios/setores", headers=headers)

    # 3. Confirma que a ação foi concluída de verdade (200, não 401/403)
    assert setores_response.status_code == 200
    assert "setores" in setores_response.json()
    assert isinstance(setores_response.json()["setores"], list)


@pytestmark_skip_sem_ad
def test_caminho_sucesso_buscar_usuario_de_teste():
    """
    Confirma que, com um token válido, dá para buscar o próprio usuário
    de teste no AD e receber os dados esperados de volta.
    """
    login_response = client.post(
        "/usuarios/login",
        data={"username": settings.TEST_AD_USER, "password": settings.TEST_AD_PASSWORD},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/usuarios", params={"nome": "teste"}, headers=headers)
    assert response.status_code == 200
    usuarios = response.json()
    assert isinstance(usuarios, list)
    assert any(u["login"] == settings.TEST_AD_USER for u in usuarios)
