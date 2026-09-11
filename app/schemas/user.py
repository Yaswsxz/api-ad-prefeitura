from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UsuarioCreate(BaseModel):
    primeiro_nome: str = Field(..., example="Joao")
    ultimo_nome: str = Field(..., example="Silva")
    cpf: Optional[str] = Field(None, example="12345678900")
    cargo: Optional[str] = Field(None, example="Analista Administrativo")
    tipo: Optional[str] = Field("efetivo", example="efetivo ou estagiario")
    email: Optional[str] = None  # se não informado, é gerado automaticamente
    subcontainer: str = Field(
        ...,
        example="CODEL",
        description="Subpasta dentro de Ativos/Inativos (setores válidos: CODEL, CMTU, Planejamento, Ouvidoria, Saude, Sercontel)"
    )


class UsuarioUpdate(BaseModel):
    cargo: Optional[str] = None
    tipo: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None


class TrocaSenha(BaseModel):
    nova_senha: Optional[str] = Field(
        None, description="Se não informada, uma senha aleatória é gerada"
    )
    forcar_troca_no_proximo_login: bool = True


class UsuarioOut(BaseModel):
    login: str
    nome_completo: str
    email: Optional[str] = None
    cargo: Optional[str] = None
    tipo: Optional[str] = None
    ativo: bool
    distinguished_name: str
    setor: Optional[str] = None   # ← NOVO CAMPO


class UsuarioCriadoOut(UsuarioOut):
    senha_gerada: str

class CampoOrdenacao(str, Enum):
    """Campos disponíveis para ordenação."""
    NOME = "nome"
    LOGIN = "login"
    EMAIL = "email"
    CARGO = "cargo"
    STATUS = "status"
    SETOR = "setor"   # ← NOVO


class Ordem(str, Enum):
    """Direção da ordenação."""
    ASC = "crescente"
    DESC = "decrescente"

class Setor(str, Enum):
    """Setores disponíveis (subcontainers dentro de Ativos/Inativos)."""
    CMTU = "CMTU"
    CODEL = "CODEL"
    OUVIDORIA = "Ouvidoria"
    PLANEJAMENTO = "Planejamento"
    SAUDE = "Saude"
    SERRCONTEL = "Sercontel"


class EventoLogin(str, Enum):
    """Tipos de evento de login/logout."""
    LOGIN = "login"
    LOGOUT = "logout"


class CampoOrdenacaoAuditoria(str, Enum):
    """Campos disponíveis para ordenação na auditoria."""
    TIMESTAMP = "timestamp"
    USERNAME = "username"
    EVENT_TYPE = "event_type"


class OrdemAuditoria(str, Enum):
    """Direção da ordenação para auditoria."""
    ASC = "crescente"
    DESC = "decrescente"


class LoginHistoryOut(BaseModel):
    """Schema de saída para registros de login/logout."""
    id: int
    username: str
    event_type: str
    timestamp: datetime
    ip_address: Optional[str] = None
    success: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
