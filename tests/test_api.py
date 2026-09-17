import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# --- Testes já existentes ---

def test_status_api():
    """Testa se a API esta no ar."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["versao"] == "2.0.0"


def test_listar_usuarios_sem_token():
    """
    Sem token, a rota de usuarios deve ser recusada com 401.
    Esse teste pegou, originalmente, uma falha real: os endpoints não
    exigiam autenticação nenhuma. Agora que a proteção JWT está aplicada
    de verdade (via dependencies=[Depends(get_current_user)] no router),
    o resultado é sempre 401 — não depende de o AD estar acessível ou não,
    porque a checagem de token acontece antes de qualquer chamada ao AD.
    """
    response = client.get("/usuarios")
    assert response.status_code == 401


def test_auditoria():
    """
    Testa se a auditoria esta funcionando.
    /auditoria/login-history agora usa o mesmo envelope padrão dos
    demais endpoints de listagem: {"total": N, "items": [...]}.
    """
    response = client.get("/auditoria/login-history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_login_invalido():
    """
    Login com credenciais erradas deve ser recusado.
    Usa 'data=' (form-urlencoded) com os campos 'username'/'password',
    que é o formato exigido pelo OAuth2PasswordRequestForm em /usuarios/login
    — usar JSON ou nomes de campo diferentes (como 'login'/'senha') resulta
    em erro de validação (422), não em credenciais recusadas (401).
    """
    response = client.post(
        "/usuarios/login",
        data={"username": "usuario.invalido.teste", "password": "senha-errada-123"},
    )
    # 401: credenciais recusadas pelo AD | 503: AD inacessível neste ambiente de teste
    assert response.status_code in [401, 503]


def test_login_sem_dados():
    """Login sem enviar usuário/senha deve falhar na validação do formulário (422)."""
    response = client.post("/usuarios/login", data={})
    assert response.status_code == 422


# --- Testes dos endpoints que sobreviveram à limpeza ---
# Cada um confirma que a proteção por token está realmente aplicada.
# Não testam o "caminho de sucesso" (login válido + ação concluída) porque
# isso exigiria credenciais reais de AD dentro do código de teste — o mesmo
# tipo de risco que já causamos e corrigimos hoje (senha exposta em script).

def test_candidatos_teste_sem_token():
    """Listar candidatos a conta de teste exige autenticação."""
    response = client.get("/usuarios/candidatos-teste")
    assert response.status_code == 401


def test_atualizar_usuario_sem_token():
    """Atualizar usuário exige autenticação."""
    response = client.put("/usuarios/algum.login", json={"cargo": "Teste"})
    assert response.status_code == 401


def test_trocar_senha_sem_token():
    """Trocar senha exige autenticação."""
    response = client.post("/usuarios/algum.login/trocar-senha", json={})
    assert response.status_code == 401


def test_auth_publico_nao_exige_token():
    """
    /usuarios/auth e /usuarios/login são as únicas rotas públicas —
    devem responder normalmente (não bloqueadas por falta de token)
    mesmo que as credenciais enviadas sejam inválidas.
    """
    response = client.post("/usuarios/auth", params={"login": "teste", "senha": "teste"})
    # 401: credenciais recusadas pelo AD | 503: AD inacessível neste ambiente de teste
    assert response.status_code in [401, 503]
    if response.status_code == 401:
        # Confirma que foi bloqueado por credencial errada, não por falta de token
        # (a mensagem do bloqueio por token é sempre "Not authenticated")
        assert response.json().get("detail") != "Not authenticated"


# --- Testes dos novos endpoints de OU/Pessoa (Direta/Indireta/Terceirizadas/Prepostos) ---

def test_criar_ou_sem_token():
    """Criar OU exige autenticação."""
    response = client.post("/estrutura/unidades/direta", json={"nome": "TESTE"})
    assert response.status_code == 401


def test_criar_pessoa_sem_token():
    """Criar pessoa exige autenticação."""
    response = client.post("/identidade/humanos", json={"tipo": "Estagio", "unidade": "TESTE"})
    assert response.status_code == 401
