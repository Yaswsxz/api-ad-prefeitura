from fastapi import APIRouter, Request, Depends

from app.schemas.identidade import PessoaCreate, PessoaUpdate, PessoaOut, PessoaCriadaOut
from app.services import identidade_service
from app.core.auth import get_current_user  # ajuste o import conforme o nome real da sua dependência de auth

router = APIRouter(prefix="/identidade", tags=["Identidade (Pessoa)"])


@router.post("/humanos", response_model=PessoaCriadaOut, status_code=201)
def criar_pessoa(dados: PessoaCreate, request: Request, current_user: str = Depends(get_current_user)):
    """
    Cria uma identidade (Estagio, Carreira, Comissionados ou NaoHumanos)
    dentro da unidade indicada. É criada em Inoperantes, bloqueada.
    """
    return identidade_service.criar_pessoa(
        dados,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


@router.patch("/humanos/{login}", response_model=PessoaOut)
def alterar_pessoa(login: str, dados: PessoaUpdate, request: Request,
                    current_user: str = Depends(get_current_user)):
    """Altera os atributos mutáveis de uma identidade (só se estiver em Operativos)."""
    return identidade_service.alterar_pessoa(
        login, dados,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


from app.schemas.identidade import PessoaMover


@router.post("/humanos/{login}/mover", response_model=PessoaOut)
def mover_pessoa(
    login: str,
    dados: PessoaMover,
    request: Request,
    current_user: str = Depends(get_current_user),
):
    """
    Move a pessoa para outro ramo (OPERATIVOS / INOPERANTES) ou para um
    DN específico (ex: trocar FAZENDA → EDUCACAO dentro de Direta).
    """
    return identidade_service.mover_pessoa(
        login,
        dados.destino,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


@router.post("/humanos/{login}/bloquear", response_model=PessoaOut)
def bloquear_pessoa(
    login: str,
    request: Request,
    current_user: str = Depends(get_current_user),
):
    """Move a pessoa para INOPERANTES e marca a conta como desabilitada (UAC 514)."""
    return identidade_service.bloquear_pessoa(
        login,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


@router.post("/humanos/{login}/desbloquear", response_model=PessoaOut)
def desbloquear_pessoa(
    login: str,
    request: Request,
    current_user: str = Depends(get_current_user),
):
    """Move a pessoa de volta para OPERATIVOS e habilita a conta (UAC 512)."""
    return identidade_service.desbloquear_pessoa(
        login,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )

@router.delete("/humanos/{login}", status_code=204)
def remover_pessoa(login: str, request: Request, current_user: str = Depends(get_current_user)):
    """Remove fisicamente uma identidade do AD. Só funciona se ela já estiver em Inoperantes."""
    identidade_service.remover_pessoa(
        login,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )
