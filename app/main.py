from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, audit
from app.database import engine, Base

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

# Registra os endpoints (roteadores) da aplicação
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