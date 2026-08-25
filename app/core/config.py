from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Configurações do Active Directory
    AD_SERVER: str = "ldap://192.168.0.1"
    AD_DOMAIN: str = "prefeitura.local"
    AD_BASE_DN: str = "DC=prefeitura,DC=local"
    AD_USER_OU: str = "OU=Funcionarios,DC=prefeitura,DC=local"
    
    # Credenciais da conta de serviço
    AD_BIND_USER: str = "svc_api@prefeitura.local"
    AD_BIND_PASSWORD: str = ""
    
    # Banco de Dados
    DATABASE_URL: str = "sqlite:///./ad_audit.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # <--- ADICIONA ESTA LINHA AQUI

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()