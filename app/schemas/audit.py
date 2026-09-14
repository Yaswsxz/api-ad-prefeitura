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
