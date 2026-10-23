from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.segredo import gerar_hash_segredo, verificar_segredo  # noqa: F401 (reexportados)

_bearer = HTTPBearer(auto_error=False)


def criar_token_acesso(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Token JWT assinado com o identificador do cliente em `sub`."""
    agora = datetime.now(timezone.utc)
    expira = agora + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode(
        {"sub": subject, "iat": agora, "exp": expira},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


async def get_current_user(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    """
    Dependência que protege as rotas: exige `Authorization: Bearer <token>`
    emitido por POST /auth/token e devolve o `sub` (identificador do cliente).
    """
    nao_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciais is None:
        raise nao_autorizado
    try:
        payload = jwt.decode(
            credenciais.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise nao_autorizado
    sub = payload.get("sub")
    if not sub:
        raise nao_autorizado
    return str(sub)
