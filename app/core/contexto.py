import re
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, Request

from app.core.auth import get_current_user

LIMITE_ADMINISTRADOR = 100
_CARACTERES_DE_CONTROLE = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class Contexto:
    """Quem pede a operação e de onde: o que a auditoria registra junto com a ação."""
    operador: str                          # o cliente autenticado (token)
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    administrador: Optional[str] = None    # informado pelo cliente em X-Administrador; NÃO verificado


def limpar_administrador(valor: Optional[str]) -> Optional[str]:
    """Sem caracteres de controle, com espaços aparados e no máximo 100 caracteres; vazio vira None."""
    if not valor:
        return None
    limpo = _CARACTERES_DE_CONTROLE.sub(" ", valor).strip()[:LIMITE_ADMINISTRADOR].strip()
    return limpo or None


def contexto(request: Request, operador: str = Depends(get_current_user),
             x_administrador: Optional[str] = Header(None)) -> Contexto:
    """Dependência das rotas: exige token e reúne operador, IP, user-agent e administrador da requisição."""
    return Contexto(
        operador=operador,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        administrador=limpar_administrador(x_administrador),
    )
