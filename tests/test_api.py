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


def test_criar_usuario_sem_dados():
    """Sem token, mesmo um corpo vazio/inválido deve barrar por autenticação."""
    response = client.post("/usuarios", json={})
    assert response.status_code in [401, 422]


def test_auditoria():
    """
    Testa se a auditoria esta funcionando.
    /auditoria/login-history usa response_model=List[LoginHistoryOut],
    então devolve a lista de registros diretamente (não embrulhada em
    um campo "history" como acontece em /auditoria/activity-history).
    """
    response = client.get("/auditoria/login-history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


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


# --- Testes novos: endpoints adicionados na sessão de hoje ---
# Cada um confirma que a proteção por token está realmente aplicada.
# Não testam o "caminho de sucesso" (login válido + ação concluída) porque
# isso exigiria credenciais reais de AD dentro do código de teste — o mesmo
# tipo de risco que já causamos e corrigimos hoje (senha exposta em script).

def test_setores_sem_token():
    """Listar setores exige autenticação."""
    response = client.get("/usuarios/setores")
    assert response.status_code == 401


def test_inconsistencias_sem_token():
    """Detectar inconsistências exige autenticação."""
    response = client.get("/usuarios/inconsistencias")
    assert response.status_code == 401


def test_corrigir_inconsistencias_sem_token():
    """Corrigir inconsistências em lote exige autenticação."""
    response = client.post("/usuarios/inconsistencias/corrigir")
    assert response.status_code == 401


def test_candidatos_teste_sem_token():
    """Listar candidatos a conta de teste exige autenticação."""
    response = client.get("/usuarios/candidatos-teste")
    assert response.status_code == 401


def test_deletar_lote_sem_token():
    """Deletar em lote exige autenticação, mesmo com um corpo válido."""
    response = client.post("/usuarios/deletar-lote", json={"logins": ["qualquer.login"]})
    assert response.status_code == 401


def test_transferir_setor_sem_token():
    """Transferir usuário de setor exige autenticação."""
    response = client.post(
        "/usuarios/algum.login/transferir-setor",
        params={"novo_subcontainer": "CODEL"},
    )
    assert response.status_code == 401


def test_habilitar_desabilitar_sem_token():
    """Habilitar e desabilitar usuário exigem autenticação."""
    resp_desabilitar = client.post("/usuarios/algum.login/desabilitar")
    resp_habilitar = client.post("/usuarios/algum.login/habilitar")
    assert resp_desabilitar.status_code == 401
    assert resp_habilitar.status_code == 401


def test_atualizar_remover_usuario_sem_token():
    """Atualizar e remover usuário exigem autenticação."""
    resp_put = client.put("/usuarios/algum.login", json={"cargo": "Teste"})
    resp_delete = client.delete("/usuarios/algum.login")
    assert resp_put.status_code == 401
    assert resp_delete.status_code == 401


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