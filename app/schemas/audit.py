from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.user import LoginHistoryOut


class LoginHistoryListOut(BaseModel):
    """Envelope padrão para listas de auditoria: total de registros + os itens em si."""
    total: int
    items: List[LoginHistoryOut]


class ActivityHistoryItemOut(BaseModel):
    id: int
    username: str
    action: str
    target_user: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    status: str


class ActivityHistoryListOut(BaseModel):
    total: int
    period_days: int
    items: List[ActivityHistoryItemOut]


class UserHistoryEventOut(BaseModel):
    """
    Um evento na linha do tempo de um usuário — pode ter vindo de um
    login/logout ou de uma atividade (criação, edição, remoção etc.).
    O formato é o mesmo nos dois casos, para simplificar o consumo.
    """
    tipo: str
    timestamp: datetime
    sucesso: bool
    ip_address: Optional[str] = None
    detalhes: Optional[str] = None


class UserHistoryListOut(BaseModel):
    total: int
    login: str
    items: List[UserHistoryEventOut]