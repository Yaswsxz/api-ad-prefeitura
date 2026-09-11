import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # --- Active Directory ---
    AD_SERVER: str = "ldap://192.168.0.1"
    AD_DOMAIN: str = "prefeitura.local"
    AD_BASE_DN: str = "DC=prefeitura,DC=local"
    AD_ATIVOS_BASE: str = os.getenv("AD_ATIVOS_BASE", "")
    AD_INATIVOS_BASE: str = os.getenv("AD_INATIVOS_BASE", "")
    AD_SEARCH_BASE: str = os.getenv("AD_SEARCH_BASE", "")
    AD_USER_OU: str = "OU=Funcionarios,DC=prefeitura,DC=local"
    AD_BIND_USER: str = "svc_api@prefeitura.local"
    AD_BIND_PASSWORD: str = ""

    # --- Banco de Dados ---
    DATABASE_URL: str = "sqlite:///./ad_audit.db"

    # --- Autenticação JWT ---
    # IMPORTANTE: defina JWT_SECRET_KEY no seu .env com um valor único e secreto.
    # O valor abaixo é só um placeholder para não quebrar em ambiente sem configuração —
    # nunca deve ser usado como está fora do seu ambiente de desenvolvimento local.
    JWT_SECRET_KEY: str = "TROQUE_ESTA_CHAVE_NO_SEU_ENV_ANTES_DE_USAR"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()