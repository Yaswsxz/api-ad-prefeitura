"""
Ciclo de vida das identidades: destituir, ativar, transferir e
redefinir senha, para humanos e não humanos. Em todas, a ordem das operações é fixa e a falha deixa a conta
bloqueada ou de volta ao lugar de origem.
"""
from dataclasses import replace
from functools import partial
from typing import Optional

from fastapi import HTTPException
from ldap3 import MODIFY_REPLACE

from app.audit_service import Acao, executar_auditado, marcar_inconsistente
from app.core import atributos as at
from app.core.arvore import Arvore, Categoria, Ramo, TipoIdentidade, dn_container, dn_unidade, ou_interna, rdn_cn
from app.core.contexto import Contexto
from app.core.erros_ad import tratar_erros
from app.core.generators import gerar_senha
from app.core.ldap_connection import conexao
from app.core.logging_config import logger
from app.core.raiz import componentes_dn, mascarar_dn
from app.schemas.estrutura import AtoUnidade
from app.schemas.identidade import AtivacaoOut, AtivarHumano, AtivarNaoHumano, IdentidadeOut
from app.schemas.identidade import RedefinirSenha, SenhaRedefinidaOut, TransferirHumano, TransferirNaoHumano
from app.services.base_ad import alterar_uac, data_do_ato, gravar_pml, reverter, unidade_existe
from app.services.identidade_service import exigir, exigir_operativos


def _destino_em_operativos(conn, tipo: TipoIdentidade, ramo: Ramo, unidade: str, categoria: Optional[Categoria],
                           unidade_ausente: Optional[HTTPException] = None) -> str:
    """
    DN onde a conta ficará em Operativos, no lado do seu tipo (Humanos ou NaoHumanos). 404 se a
    unidade não existe lá (ou o erro dado em `unidade_ausente`); 409 se falta a OU de categoria
    de um humano da Direta.
    """
    if not unidade_existe(conn, dn_unidade(Arvore.OPERATIVOS, ramo, unidade, tipo)):
        raise unidade_ausente or HTTPException(
            status_code=404, detail=f"Unidade '{unidade}' não existe em Operativos/{tipo.ou}/{ramo.ou}",
        )
    destino = dn_container(Arvore.OPERATIVOS, ramo, unidade, categoria, tipo)
    interna = ou_interna(ramo, tipo, categoria)
    if interna and not unidade_existe(conn, destino):
        raise HTTPException(status_code=409, detail=f"OU interna ausente no destino: {interna}")
    return destino


# =============================================================================
# Destituir
# =============================================================================

@tratar_erros
def destituir(login: str, tipo: TipoIdentidade, ato: AtoUnidade, ctx: Contexto) -> IdentidadeOut:
    """
    Tira a conta do quadro ativo: grava pmlDestituido*, bloqueia e move para a MESMA OU em
    Inoperantes. Vale a partir de Operativos ou de uma unidade desincorporada.
    Se o bloqueio já foi feito e o move falhar, a conta permanece bloqueada onde estava (falha
    segura): registra INCONSISTENTE; repetir é seguro.
    """
    data = data_do_ato(ato)
    return executar_auditado(
        ctx, Acao.DESTITUIR_IDENTIDADE, login, {"instrumento": ato.instrumento, "data": data},
        lambda: _executar_destituir(login, tipo, ato, data),
    )


def _executar_destituir(login: str, tipo: TipoIdentidade, ato: AtoUnidade, data: str) -> tuple[IdentidadeOut, dict]:
    avisos: list[str] = []
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        if c.arvore is Arvore.INOPERANTES:
            raise HTTPException(status_code=409, detail="A identidade já está em Inoperantes")
        destino = c.container_em(Arvore.INOPERANTES)
        if not unidade_existe(conn, destino):
            raise HTTPException(
                status_code=409,
                detail=f"A OU de destino em Inoperantes não existe no AD ({destino.split(',', 1)[0]})",
            )

        gravado = gravar_pml(conn, c.dn, at.DESTITUIDO.valores(ato.instrumento, data), avisos)
        bloqueou = not c.bloqueada
        if bloqueou:
            alterar_uac(conn, c.dn, at.bloquear(c.uac))
        try:
            conn.modify_dn(c.dn, rdn_cn(c.nome), new_superior=destino)
        except Exception:
            if bloqueou:
                logger.error(
                    f"INCONSISTENTE: destituir falhou ao mover depois de bloquear a conta em "
                    f"{mascarar_dn(c.dn)}; ela permanece bloqueada. Repetir é seguro.")
                marcar_inconsistente()
            raise

    destituida = replace(c, dn=f"{rdn_cn(c.nome)},{destino}", arvore=Arvore.INOPERANTES, uac=at.bloquear(c.uac))
    if gravado:
        destituida = replace(destituida, pml={**c.pml, **at.DESTITUIDO.valores(ato.instrumento, data)})
    return destituida.para_out(avisos), {
        "dn_anterior": c.dn, "arvore_anterior": c.arvore.ou, "pml_gravado": gravado,
    }


# =============================================================================
# Ativar
# =============================================================================

def _troca_obrigatoria(tipo: TipoIdentidade, uac: int) -> bool:
    """
    Humano troca a senha no próximo logon. Não humano não troca; e uma conta
    com "senha não expira" definida fora da API também não (o AD recusa as duas coisas juntas).
    """
    return tipo is TipoIdentidade.HUMANO and not at.sem_expiracao(uac)


def _senha_em_unicode_pwd(senha: str, troca_obrigatoria: bool) -> dict:
    """
    Modificação de `unicodePwd` (exige TLS): a senha entre aspas, em UTF-16LE. Com troca
    obrigatória, `pwdLastSet=0` vai na mesma operação, que o AD aplica em bloco.
    """
    mudancas = {"unicodePwd": [(MODIFY_REPLACE, [f'"{senha}"'.encode("utf-16-le")])]}
    if troca_obrigatoria:
        mudancas["pwdLastSet"] = [(MODIFY_REPLACE, [0])]
    return mudancas


def _ativar(login: str, tipo: TipoIdentidade, dados, categoria_destino: Optional[Categoria],
            ctx: Contexto) -> AtivacaoOut:
    """
    Ordem: (1) senha inicial, ainda em Inoperantes e com a conta bloqueada; (2) pmlAtivado*;
    (3) move para Operativos; (4) habilita. Sem TLS, falha em (1) e nada foi alterado; se (4)
    falhar, a conta volta, bloqueada, a Inoperantes. A senha nunca é registrada.
    """
    data = data_do_ato(dados)
    return executar_auditado(
        ctx, Acao.ATIVAR_IDENTIDADE, login,
        {"instrumento": dados.instrumento, "data": data, "tamanho_senha": dados.tamanho_senha},
        lambda: _executar_ativar(login, tipo, dados, categoria_destino, data),
    )


def _executar_ativar(login: str, tipo: TipoIdentidade, dados, categoria_destino: Optional[Categoria],
                     data: str) -> tuple[AtivacaoOut, dict]:
    avisos: list[str] = []
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        if c.arvore is not Arvore.INOPERANTES:
            raise HTTPException(
                status_code=409,
                detail=f"Só é possível ativar a partir de Inoperantes (a identidade está em {c.arvore.ou})",
            )
        origem = c.container_em(Arvore.INOPERANTES)

        if dados.ramo_destino is None:  # volta ao mesmo lugar, em Operativos
            ramo_d, unidade_d, categoria_d = c.ramo, c.unidade, c.categoria
            destino = _destino_em_operativos(conn, tipo, ramo_d, unidade_d, categoria_d, HTTPException(
                status_code=422,
                detail=f"A unidade '{unidade_d}' não existe em Operativos (está desincorporada?). "
                       "Informe ramo_destino e unidade_destino.",
            ))
        else:
            ramo_d, unidade_d, categoria_d = dados.ramo_destino, dados.unidade_destino, categoria_destino
            destino = _destino_em_operativos(conn, tipo, ramo_d, unidade_d, categoria_d)

        troca = _troca_obrigatoria(tipo, c.uac)
        senha = gerar_senha(dados.tamanho_senha)
        conn.modify(c.dn, _senha_em_unicode_pwd(senha, troca))
        gravado = gravar_pml(conn, c.dn, at.ATIVADO.valores(dados.instrumento, data), avisos)
        rdn = rdn_cn(c.nome)
        conn.modify_dn(c.dn, rdn, new_superior=destino)
        novo_dn = f"{rdn},{destino}"
        novo_uac = at.habilitar_ao_ativar(c.uac, nao_humano=tipo is TipoIdentidade.NAO_HUMANO)
        try:
            alterar_uac(conn, novo_dn, novo_uac)
        except Exception:
            reverter(partial(conn.modify_dn, novo_dn, rdn, new_superior=origem),
                     f"a conta foi movida para Operativos e não pôde ser habilitada nem voltar "
                     f"({mascarar_dn(novo_dn)}); segue bloqueada")
            raise

    ativada = replace(c, dn=novo_dn, arvore=Arvore.OPERATIVOS, ramo=ramo_d, unidade=unidade_d,
                      categoria=categoria_d, uac=novo_uac)
    if gravado:
        ativada = replace(ativada, pml={**c.pml, **at.ATIVADO.valores(dados.instrumento, data)})
    saida = AtivacaoOut(**ativada.para_out(avisos).model_dump(), senha_inicial=senha)
    return saida, {"dn_anterior": c.dn, "dn_novo": novo_dn, "pml_gravado": gravado,
                   "troca_obrigatoria": troca}   # a senha NUNCA entra aqui


@tratar_erros
def ativar_humano(login: str, dados: AtivarHumano, ctx: Contexto) -> AtivacaoOut:
    return _ativar(login, TipoIdentidade.HUMANO, dados, dados.categoria_destino, ctx)


@tratar_erros
def ativar_nao_humano(login: str, dados: AtivarNaoHumano, ctx: Contexto) -> AtivacaoOut:
    return _ativar(login, TipoIdentidade.NAO_HUMANO, dados, None, ctx)


# =============================================================================
# Redefinir senha
# =============================================================================

def _redefinir_senha(login: str, tipo: TipoIdentidade, dados: RedefinirSenha, ctx: Contexto) -> SenhaRedefinidaOut:
    """
    Gera nova senha para uma conta em Operativos, sem mexer no bloqueio. Num não humano, garante
    antes a flag "senha não expira" (se a senha falhar, a flag sobra, inofensiva; o contrário
    perderia a senha). A senha nunca é registrada.
    """
    return executar_auditado(
        ctx, Acao.REDEFINIR_SENHA, login, {"motivo": dados.motivo, "tamanho_senha": dados.tamanho_senha},
        lambda: _executar_redefinir_senha(login, tipo, dados),
    )


def _executar_redefinir_senha(login: str, tipo: TipoIdentidade, dados: RedefinirSenha) -> tuple[SenhaRedefinidaOut, dict]:
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        exigir_operativos(c)
        uac = c.uac
        if tipo is TipoIdentidade.NAO_HUMANO and not at.sem_expiracao(uac):
            uac |= at.UAC_SENHA_NAO_EXPIRA
            alterar_uac(conn, c.dn, uac)
        troca = _troca_obrigatoria(tipo, uac)
        senha = gerar_senha(dados.tamanho_senha)
        conn.modify(c.dn, _senha_em_unicode_pwd(senha, troca))

    saida = SenhaRedefinidaOut(**replace(c, uac=uac).para_out().model_dump(), senha_nova=senha)
    return saida, {"troca_obrigatoria": troca}     # a senha NUNCA entra aqui


@tratar_erros
def redefinir_senha_humano(login: str, dados: RedefinirSenha, ctx: Contexto) -> SenhaRedefinidaOut:
    return _redefinir_senha(login, TipoIdentidade.HUMANO, dados, ctx)


@tratar_erros
def redefinir_senha_nao_humano(login: str, dados: RedefinirSenha, ctx: Contexto) -> SenhaRedefinidaOut:
    return _redefinir_senha(login, TipoIdentidade.NAO_HUMANO, dados, ctx)


# =============================================================================
# Transferir
# =============================================================================

def _transferir(login: str, tipo: TipoIdentidade, dados, categoria_destino: Optional[Categoria],
                ctx: Contexto) -> IdentidadeOut:
    """Move dentro de Operativos e depois grava pmlTransferido*; se gravar falhar, a conta volta."""
    data = data_do_ato(dados)
    return executar_auditado(
        ctx, Acao.TRANSFERIR_IDENTIDADE, login, {"instrumento": dados.instrumento, "data": data},
        lambda: _executar_transferir(login, tipo, dados, categoria_destino, data),
    )


def _executar_transferir(login: str, tipo: TipoIdentidade, dados, categoria_destino: Optional[Categoria],
                         data: str) -> tuple[IdentidadeOut, dict]:
    ramo_d = dados.ramo_destino
    avisos: list[str] = []
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        exigir_operativos(c)
        destino = _destino_em_operativos(conn, tipo, ramo_d, dados.unidade_destino, categoria_destino)
        origem = c.container_em(Arvore.OPERATIVOS)
        if componentes_dn(origem) == componentes_dn(destino):
            raise HTTPException(status_code=409, detail="A identidade já está nesse destino")

        rdn = rdn_cn(c.nome)
        conn.modify_dn(c.dn, rdn, new_superior=destino)
        novo_dn = f"{rdn},{destino}"
        try:
            gravado = gravar_pml(conn, novo_dn, at.TRANSFERIDO.valores(dados.instrumento, data), avisos)
        except Exception:
            reverter(partial(conn.modify_dn, novo_dn, rdn, new_superior=origem),
                     f"a conta foi transferida e não pôde voltar após falha ao gravar pml* "
                     f"({mascarar_dn(novo_dn)})")
            raise

    transferida = replace(c, dn=novo_dn, ramo=ramo_d, unidade=dados.unidade_destino, categoria=categoria_destino)
    if gravado:
        transferida = replace(transferida, pml={**c.pml, **at.TRANSFERIDO.valores(dados.instrumento, data)})
    return transferida.para_out(avisos), {"dn_anterior": c.dn, "dn_novo": novo_dn, "pml_gravado": gravado}


@tratar_erros
def transferir_humano(login: str, dados: TransferirHumano, ctx: Contexto) -> IdentidadeOut:
    return _transferir(login, TipoIdentidade.HUMANO, dados, dados.categoria_destino, ctx)


@tratar_erros
def transferir_nao_humano(login: str, dados: TransferirNaoHumano, ctx: Contexto) -> IdentidadeOut:
    return _transferir(login, TipoIdentidade.NAO_HUMANO, dados, None, ctx)
