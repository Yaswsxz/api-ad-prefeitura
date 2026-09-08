from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configurações do sistema carregadas a partir do arquivo .env.
    Usa Pydantic para validação automática e caching com lru_cache.
    """
    # --- Active Directory ---
    AD_SERVER: str = "ldap://cegonha.londrina.pr.gov.br"
    AD_DOMAIN: str = "cegonha.londrina.pr.gov.br"
    AD_BASE_DN: str = "OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
    AD_USER_OU: str = "OU=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
    AD_BIND_USER: str = "pmldomain\grids1.estag"
    AD_BIND_PASSWORD: str = ""

    # --- Banco de Dados ---
    DATABASE_URL: str = "sqlite:///./ad_audit.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Permite variáveis extras no .env sem causar erro

@lru_cache()
def get_settings():
    """Retorna instância única de configuração (singleton) usando cache."""
    return Settings()

settings = get_settings()