from fastapi import APIRouter, Request, Depends

from app.schemas.estrutura import RamoOU, OUCreate, OUUpdate, OUMover, OUOut
from app.services import estrutura_service
from app.core.auth import get_current_user  # ajuste o import conforme o nome real da sua dependência de auth

router = APIRouter(prefix="/estrutura/unidades", tags=["Estrutura (OU)"])


def _ramo_para_path(ramo_path: str) -> RamoOU:
    mapa = {
        "direta": RamoOU.DIRETA,
        "indireta": RamoOU.INDIRETA,
        "terceirizada": RamoOU.TERCEIRIZADAS,
        "preposto": RamoOU.PREPOSTOS,
    }
    return mapa[ramo_path]


@router.post("/{ramo_path}", response_model=OUOut, status_code=201)
def criar_ou(ramo_path: str, dados: OUCreate, request: Request, current_user: str = Depends(get_current_user)):
    """Cria um órgão/unidade dentro do ramo indicado (direta, indireta, terceirizada, preposto)."""
    ramo = _ramo_para_path(ramo_path)
    return estrutura_service.criar_ou(
        ramo, dados,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


@router.patch("/{ramo_path}/{nome}", response_model=OUOut)
def alterar_ou(ramo_path: str, nome: str, dados: OUUpdate, request: Request,
                current_user: str = Depends(get_current_user)):
    """Altera o pmlNomeOrgao de uma unidade existente (só se estiver em Operativos)."""
    ramo = _ramo_para_path(ramo_path)
    return estrutura_service.alterar_ou(
        ramo, nome, dados,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


@router.patch("/{ramo_path}/{nome}/desincorporar", response_model=OUOut)
def desincorporar_ou(ramo_path: str, nome: str, dados: OUMover, request: Request,
                      current_user: str = Depends(get_current_user)):
    """
    Move a unidade de Operativos para Desincorporados. Caso raro — usar só
    quando o órgão realmente deixou de existir (não é o mesmo que 'saiu
    da prefeitura', que usa o espelho em Inoperantes).
    """
    ramo = _ramo_para_path(ramo_path)
    return estrutura_service.mover_ou_desincorporar(
        ramo, nome, dados,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )


@router.delete("/{ramo_path}/{nome}", status_code=204)
def remover_ou(ramo_path: str, nome: str, request: Request, current_user: str = Depends(get_current_user)):
    """
    Remove fisicamente uma unidade do AD. Só funciona se ela já estiver
    em Desincorporados (desincorpora primeiro, depois remove se quiser
    apagar de vez). A unidade precisa estar vazia (sem nada dentro).
    """
    ramo = _ramo_para_path(ramo_path)
    estrutura_service.remover_ou_fisicamente(
        ramo, nome,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        operator=current_user,
    )
