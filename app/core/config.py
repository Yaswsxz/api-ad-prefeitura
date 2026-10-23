from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.caminhos import resolver

AMBIENTES = ("dev", "prod")
PLACEHOLDER_JWT = "TROQUE_ESTA_CHAVE_NO_SEU_ENV_ANTES_DE_USAR"


class Settings(BaseSettings):
    # --- Ambiente ---
    # 'prod' proíbe AD_ALLOW_INSECURE (TLS é obrigatório em produção).
    AMBIENTE: str = "dev"

    # --- Active Directory ---
    AD_SERVER: str = "ldap://192.168.0.1"
    # Sufixo do userPrincipalName das contas criadas (login@sufixo).
    AD_UPN_SUFIXO: str = "londrina.pr.gov.br"
    AD_BIND_USER: str = "svc_api@prefeitura.local"
    AD_BIND_PASSWORD: str = ""
    # Raiz da sub-árvore gerenciada pela API. Precisa estar dentro de
    # OU=DESENVOL (constante em app/core/raiz.py); senão a API não sobe.
    AD_PML_BASE: str = "OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"

    # --- Transporte (TLS) ---
    # TLS é obrigatório. Enquanto o DC de desenvolvimento recusar StartTLS,
    # AD_ALLOW_INSECURE=true permite seguir sem criptografia (proibido em prod).
    AD_ALLOW_INSECURE: bool = False
    # CA que valida o certificado do DC (vazio = repositório de CAs do sistema).
    AD_TLS_CA_FILE: str = ""
    # Certificado do DC FIXADO (PEM público; relativo à raiz do projeto). Quando informado,
    # a confiança vem dele: antes de qualquer credencial, a API confere que o servidor
    # apresenta exatamente este certificado.
    AD_TLS_CERT_FIXADO: str = ""
    # DC que só fala TLS 1.0 (RSA 1024 / SHA-1): habilita TLS 1.0 e cifras de nível 0.
    # Risco aceito; exige AD_TLS_CERT_FIXADO ou AD_TLS_CA_FILE.
    AD_TLS_LEGADO: bool = False

    # --- Atributos pml* (chave TEMPORÁRIA) ---
    # false = não grava nenhum pml* (o schema ainda não existe) e avisa na resposta.
    # Só em desenvolvimento: AMBIENTE=prod recusa subir com false.
    PML_GRAVAR: bool = True

    # --- Arquivo de regras ---
    # Atributos mutáveis por PATCH e tipos de conta não humana. Caminho relativo
    # à raiz do projeto, ou absoluto.
    API_REGRAS_FILE: str = "config/regras.toml"

    # --- Logs e auditoria: tudo em LOG_DIR, nada é apagado ---
    # Relativo à raiz do projeto (ou absoluto). O diretório é criado na subida e fica fora do Git.
    LOG_DIR: str = "logs"
    # O log da aplicação vira (sem apagar nada) ao mudar o dia ou ao passar deste tamanho.
    LOG_MAX_BYTES: int = 50 * 1024 * 1024
    # Vazio = <LOG_DIR>/api_ad.log. Os testes apontam para os.devnull.
    API_LOG_FILE: str = ""

    # --- Banco de Dados (auditoria) ---
    # Vazio = SQLite em <LOG_DIR>/ad_audit.db. SQLite relativo vale a partir da raiz do projeto.
    DATABASE_URL: str = ""
    # Arquivo onde vai o fato quando o resultado de uma ação não pôde ser auditado depois de o AD
    # já ter mudado. Uma linha JSON por fato, um arquivo por mês
    # (`auditoria_contingencia-AAAA-MM.jsonl`). Vazio = <LOG_DIR>/auditoria_contingencia.jsonl.
    AUDITORIA_CONTINGENCIA_FILE: str = ""

    # --- Autenticação do cliente da API ---
    # Obrigatórios, sem valor padrão: a API não sobe sem eles.
    JWT_SECRET_KEY: str
    API_CLIENT_ID: str
    # Formato: pbkdf2_sha256$<iteracoes>$<salt_hex>$<hash_hex> (ver app/core/auth.py)
    API_CLIENT_SECRET_HASH: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Limite de falhas em POST /auth/token: após AUTH_MAX_FALHAS erros do mesmo cliente (ou 4x isso do
    # mesmo IP) dentro de AUTH_JANELA_SEGUNDOS, responde 429 até a janela liberar.
    AUTH_MAX_FALHAS: int = 5
    AUTH_JANELA_SEGUNDOS: int = 900

    # --- CORS ---
    # Origens permitidas, separadas por vírgula. Vazio = nenhuma origem de navegador.
    CORS_ALLOW_ORIGINS: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("AMBIENTE")
    @classmethod
    def _validar_ambiente(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in AMBIENTES:
            raise ValueError(f"AMBIENTE deve ser um de {AMBIENTES}")
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def _validar_jwt(cls, v: str) -> str:
        if v == PLACEHOLDER_JWT or len(v) < 32:
            raise ValueError("JWT_SECRET_KEY deve ser único e secreto, com ao menos 32 caracteres")
        return v

    @field_validator("API_CLIENT_SECRET_HASH")
    @classmethod
    def _validar_hash(cls, v: str) -> str:
        partes = v.split("$")
        if len(partes) != 4 or partes[0] != "pbkdf2_sha256" or not partes[1].isdigit():
            raise ValueError("API_CLIENT_SECRET_HASH deve ter o formato pbkdf2_sha256$iter$salt$hash")
        return v

    @model_validator(mode="after")
    def _validar_producao(self):
        if self.AMBIENTE == "prod" and self.AD_ALLOW_INSECURE:
            raise ValueError("AMBIENTE=prod não permite AD_ALLOW_INSECURE=true")
        if self.AMBIENTE == "prod" and not self.PML_GRAVAR:
            raise ValueError("AMBIENTE=prod não permite PML_GRAVAR=false")
        if self.AD_TLS_LEGADO and not (self.AD_TLS_CERT_FIXADO or self.AD_TLS_CA_FILE):
            raise ValueError("AD_TLS_LEGADO exige AD_TLS_CERT_FIXADO ou AD_TLS_CA_FILE")
        return self

    @property
    def diretorio_logs(self) -> Path:
        return resolver(self.LOG_DIR)

    @property
    def arquivo_log(self) -> Path:
        return resolver(self.API_LOG_FILE) if self.API_LOG_FILE else self.diretorio_logs / "api_ad.log"

    @property
    def arquivo_contingencia(self) -> Path:
        """Base do arquivo de contingência; o mês entra no nome na hora de gravar."""
        if self.AUDITORIA_CONTINGENCIA_FILE:
            return resolver(self.AUDITORIA_CONTINGENCIA_FILE)
        return self.diretorio_logs / "auditoria_contingencia.jsonl"

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL or f"sqlite:///{self.diretorio_logs / 'ad_audit.db'}"

    @property
    def cors_origens(self) -> list[str]:
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
