from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, Query, Response

from app.core.arvore import Arvore, Categoria, Ramo, TipoIdentidade
from app.core.auth import get_current_user
from app.core.contexto import Contexto, contexto
from app.schemas.estrutura import AtoUnidade
from app.schemas.identidade import (
    AtivacaoOut, AtivarHumano, AtivarNaoHumano, HumanoCreate, IdentidadeListOut, IdentidadeOut,
    NaoHumanoCreate, RedefinirSenha, SenhaRedefinidaOut, TransferirHumano, TransferirNaoHumano,
)
from app.services import identidade_ciclo as ciclo
from app.services import identidade_service as svc

router = APIRouter(prefix="/identidade", tags=["Identidade"], dependencies=[Depends(get_current_user)])

Ctx = Annotated[Contexto, Depends(contexto)]
HUMANO, NAO_HUMANO = TipoIdentidade.HUMANO, TipoIdentidade.NAO_HUMANO


# =============================================================================
# Humanos
# =============================================================================

@router.get("/humanos", response_model=IdentidadeListOut, summary="Listar humanos")
def listar_humanos(
    arvore: Arvore = Query(Arvore.OPERATIVOS),
    ramo: Optional[Ramo] = Query(None),
    unidade: Optional[str] = Query(None, description="Exige 'ramo'"),
    categoria: Optional[Categoria] = Query(None, description="Só na Direta"),
    bloqueada: Optional[bool] = Query(None),
    limite: int = Query(100, ge=1, le=1000),
    deslocamento: int = Query(0, ge=0),
):
    return svc.listar(HUMANO, arvore, ramo, unidade, categoria, bloqueada, limite, deslocamento)


@router.post("/humanos", response_model=IdentidadeOut, status_code=201, summary="Criar humano")
def criar_humano(dados: HumanoCreate, ctx: Ctx):
    """Cria o humano em Inoperantes, bloqueado e sem senha. A ativação é uma operação à parte."""
    return svc.criar_humano(dados, ctx)


@router.get("/humanos/{login}", response_model=IdentidadeOut, summary="Consultar humano")
def consultar_humano(login: str):
    return svc.consultar(login, HUMANO)


@router.patch("/humanos/{login}", response_model=IdentidadeOut, summary="Alterar atributos de um humano")
def alterar_humano(
    login: str, ctx: Ctx,
    campos: dict[str, Optional[str]] = Body(..., examples=[{"pmlCpf": "00000000000"}]),
):
    """Corpo: atributos do AD e valores. Só os atributos do arquivo de regras; só em Operativos."""
    return svc.alterar(login, HUMANO, campos, ctx)


@router.post("/humanos/{login}/bloquear", response_model=IdentidadeOut, summary="Bloquear (suspender) humano")
def bloquear_humano(login: str, ctx: Ctx):
    """Bloqueia a autenticação SEM mover a conta. Só em Operativos."""
    return svc.bloquear(login, HUMANO, ctx)


@router.post("/humanos/{login}/desbloquear", response_model=IdentidadeOut, summary="Desbloquear humano")
def desbloquear_humano(login: str, ctx: Ctx):
    """Habilita a autenticação SEM mover a conta. Só em Operativos."""
    return svc.desbloquear(login, HUMANO, ctx)


@router.post("/humanos/{login}/destituir", response_model=IdentidadeOut, summary="Destituir humano")
def destituir_humano(login: str, dados: AtoUnidade, ctx: Ctx):
    """
    Grava o instrumento e a data, bloqueia a conta e a move para a mesma OU em Inoperantes.
    Vale a partir de Operativos ou de uma unidade desincorporada.
    """
    return ciclo.destituir(login, HUMANO, dados, ctx)


@router.post("/humanos/{login}/ativar", response_model=AtivacaoOut, summary="Ativar (admitir) humano")
def ativar_humano(login: str, dados: AtivarHumano, ctx: Ctx, response: Response):
    """
    Move de Inoperantes para Operativos (mesma unidade, ou o destino informado; obrigatório se a
    unidade de origem estiver desincorporada), define a senha inicial e habilita a conta.
    A senha é devolvida UMA ÚNICA VEZ. Exige TLS no controlador de domínio.
    """
    response.headers["Cache-Control"] = "no-store"
    return ciclo.ativar_humano(login, dados, ctx)


@router.post("/humanos/{login}/redefinir-senha", response_model=SenhaRedefinidaOut,
             summary="Redefinir a senha de humano")
def redefinir_senha_humano(login: str, dados: RedefinirSenha, ctx: Ctx, response: Response):
    """
    Gera nova senha para a conta em Operativos, sem mexer no bloqueio, e exige a troca no próximo
    logon. A senha é devolvida UMA ÚNICA VEZ; se a resposta se perder, redefina de novo.
    """
    response.headers["Cache-Control"] = "no-store"
    return ciclo.redefinir_senha_humano(login, dados, ctx)


@router.post("/humanos/{login}/transferir", response_model=IdentidadeOut, summary="Transferir humano")
def transferir_humano(login: str, dados: TransferirHumano, ctx: Ctx):
    """
    Muda o humano de unidade, de categoria e/ou de ramo, dentro de Operativos, mantendo o
    login. Ao entrar na Direta, `categoria_destino` é obrigatória.
    """
    return ciclo.transferir_humano(login, dados, ctx)


@router.delete("/humanos/{login}", status_code=204, summary="Remover fisicamente (inclusão indevida ou duplicada)")
def remover_humano(login: str, ctx: Ctx, motivo: str = Query(..., min_length=3, max_length=200)):
    """Só para inclusão indevida ou duplicada, e só em Inoperantes."""
    svc.remover(login, HUMANO, motivo, ctx)


# =============================================================================
# Não humanos
# =============================================================================

@router.get("/naohumanos", response_model=IdentidadeListOut, summary="Listar não humanos")
def listar_nao_humanos(
    arvore: Arvore = Query(Arvore.OPERATIVOS),
    ramo: Optional[Ramo] = Query(None),
    unidade: Optional[str] = Query(None, description="Exige 'ramo'"),
    bloqueada: Optional[bool] = Query(None),
    limite: int = Query(100, ge=1, le=1000),
    deslocamento: int = Query(0, ge=0),
):
    return svc.listar(NAO_HUMANO, arvore, ramo, unidade, None, bloqueada, limite, deslocamento)


@router.post("/naohumanos", response_model=IdentidadeOut, status_code=201, summary="Criar não humano")
def criar_nao_humano(dados: NaoHumanoCreate, ctx: Ctx):
    """Cria a conta técnica em Inoperantes, bloqueada e sem senha."""
    return svc.criar_nao_humano(dados, ctx)


@router.get("/naohumanos/{login}", response_model=IdentidadeOut, summary="Consultar não humano")
def consultar_nao_humano(login: str):
    return svc.consultar(login, NAO_HUMANO)


@router.patch("/naohumanos/{login}", response_model=IdentidadeOut, summary="Alterar atributos de um não humano")
def alterar_nao_humano(
    login: str, ctx: Ctx,
    campos: dict[str, Optional[str]] = Body(..., examples=[{"pmlNaoHumanoTipo": "bot"}]),
):
    """Corpo: atributos do AD e valores. Só os atributos do arquivo de regras; só em Operativos."""
    return svc.alterar(login, NAO_HUMANO, campos, ctx)


@router.post("/naohumanos/{login}/bloquear", response_model=IdentidadeOut, summary="Bloquear não humano")
def bloquear_nao_humano(login: str, ctx: Ctx):
    return svc.bloquear(login, NAO_HUMANO, ctx)


@router.post("/naohumanos/{login}/desbloquear", response_model=IdentidadeOut, summary="Desbloquear não humano")
def desbloquear_nao_humano(login: str, ctx: Ctx):
    return svc.desbloquear(login, NAO_HUMANO, ctx)


@router.post("/naohumanos/{login}/destituir", response_model=IdentidadeOut, summary="Destituir não humano")
def destituir_nao_humano(login: str, dados: AtoUnidade, ctx: Ctx):
    return ciclo.destituir(login, NAO_HUMANO, dados, ctx)


@router.post("/naohumanos/{login}/ativar", response_model=AtivacaoOut, summary="Ativar não humano")
def ativar_nao_humano(login: str, dados: AtivarNaoHumano, ctx: Ctx, response: Response):
    """Como a ativação de humano; a conta vai para a unidade do lado NaoHumanos. A senha sai uma única vez."""
    response.headers["Cache-Control"] = "no-store"
    return ciclo.ativar_nao_humano(login, dados, ctx)


@router.post("/naohumanos/{login}/redefinir-senha", response_model=SenhaRedefinidaOut,
             summary="Redefinir a senha de não humano")
def redefinir_senha_nao_humano(login: str, dados: RedefinirSenha, ctx: Ctx, response: Response):
    """Como a de humano, mas sem troca no logon: a senha da conta não humana não expira."""
    response.headers["Cache-Control"] = "no-store"
    return ciclo.redefinir_senha_nao_humano(login, dados, ctx)


@router.post("/naohumanos/{login}/transferir", response_model=IdentidadeOut, summary="Transferir não humano")
def transferir_nao_humano(login: str, dados: TransferirNaoHumano, ctx: Ctx):
    """A conta vai para a unidade de destino no lado NaoHumanos (sem categoria)."""
    return ciclo.transferir_nao_humano(login, dados, ctx)


@router.delete("/naohumanos/{login}", status_code=204, summary="Remover fisicamente (inclusão indevida ou duplicada)")
def remover_nao_humano(login: str, ctx: Ctx, motivo: str = Query(..., min_length=3, max_length=200)):
    svc.remover(login, NAO_HUMANO, motivo, ctx)
