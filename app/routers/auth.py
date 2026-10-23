import hmac

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.audit_service import AuditService
from app.core.auth import criar_token_acesso, verificar_segredo
from app.core.config import settings
from app.core.erros_ad import Codigo, ErroDominio
from app.core.limite import por_cliente, por_ip
from app.core.logging_config import logger
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


@router.post("/token", summary="Emitir token de acesso para o cliente da API")
def emitir_token(dados: TokenRequest, request: Request, db: Session = Depends(get_db)):
    """
    Autentica o cliente da API por chave própria (client_id e segredo no
    corpo) e emite um JWT de curta duração. Não usa contas do
    Active Directory. Após muitas falhas do mesmo cliente ou IP, responde 429
    (`Retry-After`) até a janela liberar.
    """
    ip = request.client.host if request.client else None
    agente = request.headers.get("user-agent")
    auditoria = AuditService(db)
    cliente = dados.client_id[:100]
    chaves = ((por_ip, f"ip:{ip}"), (por_cliente, f"cliente:{cliente}"))

    espera = max(limite.segundos_restantes(chave) for limite, chave in chaves)
    if espera:
        logger.warning(f"AUTH_BLOQUEADO cliente={cliente} ip={ip} espera={espera}s")
        auditoria.registrar_login(username=cliente, ip_address=ip, user_agent=agente, sucesso=False,
                                  mensagem_erro="bloqueado: muitas tentativas")
        raise ErroDominio(
            "Muitas tentativas de autenticação; aguarde antes de tentar de novo.",
            codigo=Codigo.MUITAS_TENTATIVAS, status_code=429,
            headers={"Retry-After": str(espera)}, detalhes={"aguarde_segundos": espera},
        )

    # Os dois testes sempre executam, para não revelar qual deles falhou.
    id_ok = hmac.compare_digest(
        dados.client_id.encode("utf-8"), settings.API_CLIENT_ID.encode("utf-8")
    )
    segredo_ok = verificar_segredo(dados.client_secret, settings.API_CLIENT_SECRET_HASH)
    autenticado = id_ok and segredo_ok

    auditoria.registrar_login(
        username=cliente, ip_address=ip, user_agent=agente, sucesso=autenticado,
        mensagem_erro=None if autenticado else "credenciais inválidas",
    )
    if not autenticado:
        for limite, chave in chaves:
            limite.registrar_falha(chave)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    for limite, chave in chaves:
        limite.zerar(chave)
    return {
        "access_token": criar_token_acesso(dados.client_id),
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
