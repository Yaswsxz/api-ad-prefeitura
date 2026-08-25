from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users
from app.routers import audit
from app.database import engine, Base

# Cria as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gerenciamento de Usuarios - Prefeitura",
    description="API para cadastro, consulta, atualizacao, remocao, troca de senha e desabilitacao de usuarios no Active Directory.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(audit.router)

@app.get("/", tags=["Status"])
def status():
    return {
        "status": "online",
        "servico": "API Gerenciador de Usuarios AD",
        "versao": "2.0.0",
        "docs": "/docs"
    }