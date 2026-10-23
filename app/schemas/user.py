from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


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

    model_config = ConfigDict(from_attributes=True)
