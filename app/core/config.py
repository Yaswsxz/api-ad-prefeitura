from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # --- Active Directory ---
    AD_SERVER: str = "ldap://cegonha.londrina.pr.gov.br"
    AD_DOMAIN: str = "cegonha.londrina.pr.gov.br"
    AD_BASE_DN: str = "OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
    AD_USER_OU: str = "OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
    AD_BIND_USER: str = "pmldomain\grds1.estag"
    AD_BIND_PASSWORD: str = "SENHA_REMOVIDA"

    # --- Banco de Dados ---
    DATABASE_URL: str = "sqlite:///./ad_audit.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()