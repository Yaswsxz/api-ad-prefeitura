from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from importlib.metadata import version as pkg_version, PackageNotFoundError
import sys

from app.routers import users, audit, estrutura, identidade
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
app.include_router(estrutura.router)
app.include_router(identidade.router)
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


def _versao_pacote(nome: str) -> str:
    """Busca a versão instalada de uma biblioteca, sem quebrar se não achar."""
    try:
        return pkg_version(nome)
    except PackageNotFoundError:
        return "desconhecida"


@app.get("/versao", tags=["Status"])
def versao():
    """
    Mostra a versão da API e das principais bibliotecas usadas em tempo
    de execução. Não exige autenticação. Útil para confirmar rapidamente
    se uma atualização/deploy foi aplicada de fato.
    """
    return {
        "versao_api": app.version,
        "python": sys.version.split()[0],
        "dependencias": {
            "fastapi": _versao_pacote("fastapi"),
            "ldap3": _versao_pacote("ldap3"),
            "sqlalchemy": _versao_pacote("sqlalchemy"),
            "pydantic": _versao_pacote("pydantic"),
        },
    }
