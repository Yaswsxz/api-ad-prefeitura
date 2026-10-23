from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.arvore import Arvore, Ramo
from app.core.auth import get_current_user
from app.core.contexto import Contexto, contexto
from app.schemas.estrutura import AtoUnidade, OUCreate, OUOut, OUUpdate, UnidadeListOut, UnidadeMovidaOut, UnidadeOut
from app.services import estrutura_service as svc

router = APIRouter(
    prefix="/estrutura/unidades", tags=["Estrutura (OU)"], dependencies=[Depends(get_current_user)],
)


def ramo_da_rota(ramo_path: str) -> Ramo:
    """Ramo da URL (direta, indireta, terceirizada, preposto); desconhecido é 404."""
    try:
        return Ramo(ramo_path)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Ramo '{ramo_path}' inexistente")


RamoDaRota = Annotated[Ramo, Depends(ramo_da_rota)]
Ctx = Annotated[Contexto, Depends(contexto)]


@router.get("/{ramo_path}", response_model=UnidadeListOut, summary="Listar unidades de um ramo")
def listar_unidades(
    ramo: RamoDaRota,
    arvore: Arvore = Query(Arvore.OPERATIVOS, description="Árvore a consultar"),
    limite: int = Query(100, ge=1, le=1000),
    deslocamento: int = Query(0, ge=0),
):
    """Lista paginada das unidades do ramo na árvore escolhida (padrão: operativos)."""
    return svc.listar_unidades(ramo, arvore, limite, deslocamento)


@router.get("/{ramo_path}/{nome}", response_model=UnidadeOut, summary="Consultar uma unidade pelo nome")
def consultar_unidade(ramo: RamoDaRota, nome: str):
    """Dados da unidade e as árvores (operativos, inoperantes, desincorporados) em que ela existe."""
    return svc.consultar_unidade(ramo, nome)


@router.post("/{ramo_path}", response_model=OUOut, status_code=201)
def criar_ou(ramo: RamoDaRota, dados: OUCreate, ctx: Ctx):
    """Cria um órgão/unidade dentro do ramo indicado (direta, indireta, terceirizada, preposto)."""
    return svc.criar_ou(ramo, dados, ctx)


@router.patch("/{ramo_path}/{nome}", response_model=OUOut)
def alterar_ou(ramo: RamoDaRota, nome: str, dados: OUUpdate, ctx: Ctx):
    """Altera o pmlNomeOrgao de uma unidade existente (só se estiver em Operativos)."""
    return svc.alterar_ou(ramo, nome, dados, ctx)


@router.post("/{ramo_path}/{nome}/desincorporar", response_model=UnidadeMovidaOut,
             summary="Desincorporar uma unidade")
def desincorporar(ramo: RamoDaRota, nome: str, dados: AtoUnidade, ctx: Ctx):
    """
    Move a unidade de Operativos para Desincorporados, com todo o conteúdo, e bloqueia as
    contas habilitadas dentro dela. A OU espelho em Inoperantes permanece. Devolve as contas
    que esta operação bloqueou.
    """
    return svc.desincorporar_unidade(ramo, nome, dados, ctx)


@router.post("/{ramo_path}/{nome}/reincorporar", response_model=UnidadeMovidaOut,
             summary="Reincorporar uma unidade desincorporada")
def reincorporar(ramo: RamoDaRota, nome: str, dados: AtoUnidade, ctx: Ctx):
    """
    Traz a unidade de Desincorporados de volta para Operativos e desbloqueia TODAS as contas
    dela, inclusive as que já estavam bloqueadas antes da desincorporação.
    Devolve as contas desbloqueadas.
    """
    return svc.reincorporar_unidade(ramo, nome, dados, ctx)
