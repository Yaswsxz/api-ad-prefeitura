from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


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


class CampoOrdenacao(str, Enum):
    """Campos disponíveis para ordenação."""
    NOME = "nome"
    LOGIN = "login"
    EMAIL = "email"
    CARGO = "cargo"
    STATUS = "status"


class Ordem(str, Enum):
    """Direção da ordenação."""
    ASC = "asc"
    DESC = "desc"


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
    ASC = "asc"
    DESC = "desc"


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
