from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.routers import users, audit
from app.database import engine, Base, SessionLocal
from app.core.ldap_connection import get_connection
from app.core.logging_config import logger

# Cria as tabelas no banco SQLite automaticamente ao iniciar a API
# Isso garante que a estrutura de auditoria exista antes de qualquer requisição
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gerenciamento de Usuários - Prefeitura de Londrina",
    description="API responsável por gerenciar usuários no Active Directory, com registro completo de auditoria",
    version="2.0.0",
)

# Libera acesso para front-ends (CORS) - necessário para integração com React/Vue futuramente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os endpoints (roteadores) da aplicação.
# users.public_router: endpoints de login/autenticação, sem exigir token prévio.
# users.router: todos os demais endpoints de usuários, protegidos por JWT.
app.include_router(users.public_router)
app.include_router(users.router)
app.include_router(audit.router)

@app.get("/", tags=["Status"])
def status():
    """Endpoint de verificação de saúde da API."""
    return {
        "status": "online",
        "servico": "API Gerenciador de Usuários AD",
        "versao": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Status"])
def health_check(response: Response):
    """
    Verifica se a API consegue se comunicar com suas dependências reais:
    o Active Directory e o banco de auditoria. Não exige autenticação —
    pensado para ferramentas de monitoramento checarem rapidamente se
    algo caiu, sem precisar de um token válido.

    Retorna 200 se tudo estiver OK, 503 se alguma dependência falhar.
    """
    checks = {"active_directory": "ok", "banco_auditoria": "ok"}
    saudavel = True

    try:
        conn = get_connection()
        conn.unbind()
    except Exception as e:
        logger.error(f"Health check: falha ao conectar no Active Directory: {e}")
        checks["active_directory"] = "falha"
        saudavel = False

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        logger.error(f"Health check: falha ao conectar no banco de auditoria: {e}")
        checks["banco_auditoria"] = "falha"
        saudavel = False

    response.status_code = 200 if saudavel else 503
    return {
        "status": "ok" if saudavel else "degraded",
        "checks": checks,
    }