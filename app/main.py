from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from importlib.metadata import version as pkg_version, PackageNotFoundError
from ldap3 import BASE
from sqlalchemy import text
import sys

from app.routers import auth, audit, estrutura, identidade
from app.database import SessionLocal, iniciar_banco
from app.core.auth import get_current_user
from app.core.config import settings
from app.core.erros_ad import registrar_handlers
from app.core.ldap_connection import conexao
from app.core.logging_config import logger
from app.core.raiz import validar_configuracao
from app.core.regras import carregar as carregar_regras
from app.core.requisicao import instalar_request_id

# Falha rápido: AD_PML_BASE fora de OU=DESENVOL, ou CA de TLS inexistente,
# impedem a API de subir. Não contata o AD.
validar_configuracao()
carregar_regras()  # arquivo de regras ausente ou inválido também impede de subir
iniciar_banco()

app = FastAPI(
    title="API de Gerenciamento de Usuários - Prefeitura de Londrina",
    description="API responsável por gerenciar usuários no Active Directory, com registro completo de auditoria",
    version="2.0.0",
)

# Erros de domínio com corpo {codigo, mensagem, detalhes}
registrar_handlers(app)
instalar_request_id(app)

# CORS: só as origens listadas em CORS_ALLOW_ORIGINS (vazio = nenhuma).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origens,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Administrador", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

app.include_router(auth.router)
app.include_router(estrutura.router)
app.include_router(identidade.router)
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
def health_check():
    """
    Saúde mínima, pública, que NÃO toca o Active Directory nem o banco
    (para não servir de amplificador de conexões). Os detalhes ficam em
    /health/detalhes, autenticado.
    """
    return {"status": "ok"}


@app.get("/health/detalhes", tags=["Status"], dependencies=[Depends(get_current_user)])
def health_detalhes(response: Response):
    """
    Verifica as dependências reais. O AD é testado com uma consulta de
    escopo BASE dentro de AD_PML_BASE (nunca rootDSE). 200 se tudo estiver
    OK, 503 se alguma dependência falhar.
    """
    checks = {"active_directory": "ok", "banco_auditoria": "ok"}
    saudavel = True

    try:
        with conexao() as conn:
            conn.search(settings.AD_PML_BASE, "(objectClass=*)", search_scope=BASE,
                        attributes=["distinguishedName"])
            if not conn.entries:
                raise RuntimeError("AD_PML_BASE não encontrada")
    except Exception as e:
        logger.error(f"Health check: falha no Active Directory: {getattr(e, 'codigo', type(e).__name__)}")
        checks["active_directory"] = f"falha ({getattr(e, 'codigo', 'erro')})"
        saudavel = False

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check: falha no banco de auditoria: {e}")
        checks["banco_auditoria"] = "falha"
        saudavel = False

    response.status_code = 200 if saudavel else 503
    return {"status": "ok" if saudavel else "degraded", "checks": checks}


def _versao_pacote(nome: str) -> str:
    """Busca a versão instalada de uma biblioteca, sem quebrar se não achar."""
    try:
        return pkg_version(nome)
    except PackageNotFoundError:
        return "desconhecida"


@app.get("/versao", tags=["Status"], dependencies=[Depends(get_current_user)])
def versao():
    """
    Mostra a versão da API e das principais bibliotecas usadas em tempo
    de execução. Exige autenticação. Útil para confirmar se uma
    atualização/deploy foi aplicada de fato.
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
