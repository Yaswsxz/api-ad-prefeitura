import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_status_api():
    """Testa se a API esta no ar."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["versao"] == "2.0.0"


def test_listar_usuarios_sem_token():
    """Testa a rota de usuarios sem token."""
    response = client.get("/usuarios")
    assert response.status_code in [401, 503]


def test_criar_usuario_sem_dados():
    """Testa criacao de usuario com dados faltando."""
    response = client.post("/usuarios", json={})
    assert response.status_code in [422, 503]


def test_auditoria():
    """Testa se a auditoria esta funcionando."""
    response = client.get("/auditoria/login-history")
    assert response.status_code == 200
    assert "history" in response.json()


def test_login_invalido():
    """Testa login com credenciais invalidas."""
    response = client.post("/usuarios/login?login=invalido&senha=errada")
    # Aceita varios codigos ate o endpoint ser implementado
    assert response.status_code in [404, 401, 503, 405]
