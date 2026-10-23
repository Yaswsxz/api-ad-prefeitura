"""
Identidades: consultar, listar, criar, alterar, bloquear/desbloquear e
remover, para humanos e não humanos nos quatro ramos. O ciclo de vida (destituir, ativar,
transferir) está em identidade_ciclo.py.

Onde a identidade fica:
  humano da Direta:  OU=<Categoria>,OU=<UNIDADE>,OU=Direta,OU=Humanos,OU=<árvore>,<PML>
  demais humanos:    OU=<UNIDADE>,OU=<ramo>,OU=Humanos,OU=<árvore>,<PML>
  não humano:        OU=<UNIDADE>,OU=<ramo>,OU=NaoHumanos,OU=<árvore>,<PML>

Humano x não humano: o lado da árvore (Humanos/NaoHumanos) em que o DN está.
"""
from dataclasses import dataclass, replace
from functools import partial
from typing import Optional

from fastapi import HTTPException
from ldap3 import MODIFY_REPLACE, SUBTREE
from ldap3.utils.conv import escape_filter_chars

from app.audit_service import Acao, executar_auditado
from app.core import atributos as at
from app.core.arvore import (
    Arvore, Categoria, Ramo, TipoIdentidade,
    dn_container, dn_ramo, dn_tipo, dn_unidade, local_da_identidade, ou_interna, rdn_cn,
)
from app.core.config import settings
from app.core.contexto import Contexto
from app.core.erros_ad import tratar_erros
from app.core.ldap_connection import buscar, conexao
from app.core.raiz import mascarar_dn
from app.core.regras import regras
from app.schemas.identidade import HumanoCreate, IdentidadeListOut, IdentidadeOut, NaoHumanoCreate
from app.services.base_ad import alterar_uac, gravar_pml, reverter, unidade_existe

FILTRO_PESSOA = "(&(objectCategory=person)(objectClass=user))"
ATRIBUTOS = ["sAMAccountName", "cn", "userAccountControl", *at.PML_IDENTIDADE]


# =============================================================================
# A conta lida do AD
# =============================================================================

@dataclass(frozen=True)
class Conta:
    dn: str
    login: str
    nome: str
    tipo: TipoIdentidade
    arvore: Arvore
    ramo: Ramo
    unidade: str
    categoria: Optional[Categoria]
    uac: int
    pml: dict[str, str]

    @property
    def bloqueada(self) -> bool:
        return at.bloqueada(self.uac)

    def container_em(self, arvore: Arvore) -> str:
        """DN da OU onde esta conta ficaria na árvore indicada (mesma unidade e categoria)."""
        return dn_container(arvore, self.ramo, self.unidade, self.categoria, self.tipo)

    def para_out(self, avisos: Optional[list[str]] = None) -> IdentidadeOut:
        return IdentidadeOut(
            login=self.login, nome=self.nome, tipo=self.tipo, ramo=self.ramo, unidade=self.unidade,
            categoria=self.categoria, arvore=self.arvore, bloqueada=self.bloqueada,
            distinguished_name=self.dn, atributos_pml=self.pml, avisos=avisos or [],
        )


def _montar(entrada: dict) -> Optional[Conta]:
    attrs = entrada.get("attributes", {})
    login = at.texto(attrs, "sAMAccountName")
    local = local_da_identidade(entrada["dn"])
    if not login or not local:
        return None
    return Conta(
        dn=entrada["dn"],
        login=login,
        nome=at.texto(attrs, "cn") or entrada["dn"].split(",", 1)[0][3:],
        tipo=local.tipo,
        arvore=local.arvore, ramo=local.ramo, unidade=local.unidade, categoria=local.categoria,
        uac=at.uac_de(attrs),
        pml={k: v for k in at.PML_IDENTIDADE if (v := at.texto(attrs, k))},
    )


def buscar_conta(conn, login: str) -> Optional[Conta]:
    achadas = buscar(
        conn, settings.AD_PML_BASE,
        f"(&(objectCategory=person)(objectClass=user)(sAMAccountName={escape_filter_chars(login)}))",
        SUBTREE, ATRIBUTOS,
    )
    return next((c for c in map(_montar, achadas) if c), None)


def exigir(conn, login: str, tipo: TipoIdentidade) -> Conta:
    c = buscar_conta(conn, login)
    if not c or c.tipo != tipo:
        raise HTTPException(status_code=404, detail="Identidade não encontrada no AD")
    return c


def exigir_operativos(c: Conta) -> None:
    if c.arvore is not Arvore.OPERATIVOS:
        raise HTTPException(
            status_code=409,
            detail=f"A identidade está em {c.arvore.ou}; esta operação só vale em Operativos",
        )


# =============================================================================
# Consultar e listar
# =============================================================================

@tratar_erros
def consultar(login: str, tipo: TipoIdentidade) -> IdentidadeOut:
    with conexao() as conn:
        return exigir(conn, login, tipo).para_out()


@tratar_erros
def listar(tipo: TipoIdentidade, arvore: Arvore, ramo: Optional[Ramo], unidade: Optional[str],
           categoria: Optional[Categoria], bloqueada: Optional[bool],
           limite: int, deslocamento: int) -> IdentidadeListOut:
    if unidade and not ramo:
        raise HTTPException(status_code=422, detail="O filtro 'unidade' exige 'ramo'")
    if categoria and ramo not in (None, Ramo.DIRETA):
        raise HTTPException(status_code=422, detail="categoria só existe em unidades da Direta")
    base = dn_tipo(arvore, tipo)
    if ramo:
        base = dn_ramo(arvore, ramo, tipo)
    if unidade:
        base = dn_unidade(arvore, ramo, unidade.strip().upper(), tipo)

    with conexao() as conn:
        encontradas = [_montar(e) for e in buscar(conn, base, FILTRO_PESSOA, SUBTREE, ATRIBUTOS)]
    itens = sorted(
        (c for c in encontradas
         if c and c.tipo == tipo
         and (categoria is None or c.categoria == categoria)
         and (bloqueada is None or c.bloqueada == bloqueada)),
        key=lambda c: c.login,
    )
    return IdentidadeListOut(
        total=len(itens), limite=limite, deslocamento=deslocamento,
        items=[c.para_out() for c in itens[deslocamento:deslocamento + limite]],
    )


# =============================================================================
# Criar: nasce em Inoperantes, bloqueada e sem senha utilizável
# =============================================================================

def _criar(dados, tipo: TipoIdentidade, ctx: Contexto) -> IdentidadeOut:
    nao_humano = tipo is TipoIdentidade.NAO_HUMANO
    return executar_auditado(
        ctx, Acao.CRIAR_NAO_HUMANO if nao_humano else Acao.CRIAR_HUMANO, dados.login,
        {"ramo": dados.ramo.ou, "unidade": dados.unidade,
         "categoria": ou_interna(dados.ramo, tipo, None if nao_humano else dados.categoria),
         "cpf": None if nao_humano else dados.cpf,
         "tipo": dados.pml_nao_humano_tipo if nao_humano else None},
        lambda: _executar_criar(dados, tipo),
    )


def _executar_criar(dados, tipo: TipoIdentidade) -> tuple[IdentidadeOut, dict]:
    ramo = dados.ramo
    nao_humano = tipo is TipoIdentidade.NAO_HUMANO
    if nao_humano and dados.pml_nao_humano_tipo not in regras().tipos_nao_humano:
        raise HTTPException(
            status_code=422,
            detail=f"pml_nao_humano_tipo inválido; valores aceitos: {', '.join(regras().tipos_nao_humano)}",
        )

    nome = dados.nome if nao_humano else dados.nome_completo
    categoria = None if nao_humano else dados.categoria
    interna = ou_interna(ramo, tipo, categoria)
    avisos: list[str] = []
    with conexao() as conn:
        if not unidade_existe(conn, dn_unidade(Arvore.INOPERANTES, ramo, dados.unidade, tipo)):
            raise HTTPException(
                status_code=404,
                detail=f"Unidade '{dados.unidade}' não existe em Inoperantes/{tipo.ou}/{ramo.ou}. Crie a unidade primeiro.",
            )
        container = dn_container(Arvore.INOPERANTES, ramo, dados.unidade, categoria, tipo)
        if interna and not unidade_existe(conn, container):
            raise HTTPException(status_code=409, detail=f"OU interna ausente no AD: {interna}")
        if buscar_conta(conn, dados.login):
            raise HTTPException(status_code=409, detail=f"Login '{dados.login}' já existe na estrutura")

        dn = f"{rdn_cn(nome)},{container}"
        conn.add(dn, attributes={
            "objectClass": ["top", "person", "organizationalPerson", "user"],
            "cn": nome,
            "sAMAccountName": dados.login,
            "userPrincipalName": f"{dados.login}@{settings.AD_UPN_SUFIXO}",
            "displayName": nome,
            "userAccountControl": at.UAC_NOVA_CONTA,
        })

        pml = ({at.PML_NAO_HUMANO_TIPO: dados.pml_nao_humano_tipo} if nao_humano
               else ({at.PML_CPF: dados.cpf} if dados.cpf else {}))
        gravado = False
        if pml:
            try:
                gravado = gravar_pml(conn, dn, pml, avisos)
            except Exception:
                # a conta não pode ficar sem os atributos exigidos
                reverter(partial(conn.delete, dn),
                         f"conta criada e não removida após falha ao gravar pml* ({mascarar_dn(dn)}); "
                         "remover manualmente")
                raise

    saida = Conta(
        dn=dn, login=dados.login, nome=nome, tipo=tipo, arvore=Arvore.INOPERANTES, ramo=ramo,
        unidade=dados.unidade, categoria=categoria, uac=at.UAC_NOVA_CONTA,
        pml=pml if gravado else {},
    ).para_out(avisos)
    return saida, {"pml_gravado": gravado or not pml}


@tratar_erros
def criar_humano(dados: HumanoCreate, ctx: Contexto) -> IdentidadeOut:
    return _criar(dados, TipoIdentidade.HUMANO, ctx)


@tratar_erros
def criar_nao_humano(dados: NaoHumanoCreate, ctx: Contexto) -> IdentidadeOut:
    return _criar(dados, TipoIdentidade.NAO_HUMANO, ctx)


# =============================================================================
# Alterar: só atributos do arquivo de regras, só em Operativos
# =============================================================================

@tratar_erros
def alterar(login: str, tipo: TipoIdentidade, campos: dict[str, Optional[str]], ctx: Contexto) -> IdentidadeOut:
    return executar_auditado(
        ctx, Acao.ALTERAR_IDENTIDADE, login, {"campos": sorted(campos)},
        lambda: _executar_alterar(login, tipo, campos),
    )


def _executar_alterar(login: str, tipo: TipoIdentidade, campos: dict[str, Optional[str]]) -> tuple[IdentidadeOut, dict]:
    nao_humano = tipo is TipoIdentidade.NAO_HUMANO
    permitidos = {a.lower(): a for a in regras().mutaveis(nao_humano)}
    invalidos = sorted(k for k in campos if k.lower() not in permitidos)
    if not campos or invalidos:
        raise HTTPException(
            status_code=422,
            detail=(f"Atributos não alteráveis: {', '.join(invalidos)}. " if invalidos else "Nenhum atributo informado. ")
                   + f"Alteráveis: {', '.join(permitidos.values()) or 'nenhum'}",
        )
    mudancas = {permitidos[k.lower()]: v for k, v in campos.items()}
    for k, v in mudancas.items():
        if v is not None and len(v) > 255:
            raise HTTPException(status_code=422, detail=f"{k} excede 255 caracteres")
    if nao_humano and at.PML_NAO_HUMANO_TIPO in mudancas:
        if mudancas[at.PML_NAO_HUMANO_TIPO] not in regras().tipos_nao_humano:
            raise HTTPException(
                status_code=422,
                detail=f"{at.PML_NAO_HUMANO_TIPO} inválido; valores aceitos: {', '.join(regras().tipos_nao_humano)}",
            )

    avisos: list[str] = []
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        exigir_operativos(c)
        pml = {k: v for k, v in mudancas.items() if k.lower().startswith("pml")}
        comuns = {k: v for k, v in mudancas.items() if k not in pml}
        if comuns:
            conn.modify(c.dn, {k: [(MODIFY_REPLACE, [v] if v is not None else [])] for k, v in comuns.items()})
        gravado = gravar_pml(conn, c.dn, pml, avisos) if pml else False

    if gravado:
        c = replace(c, pml={k: v for k, v in {**c.pml, **pml}.items() if v is not None})
    return c.para_out(avisos), {"pml_gravado": gravado or not pml}


# =============================================================================
# Bloquear / desbloquear no lugar: não move a conta
# =============================================================================

def _alternar_bloqueio(login: str, tipo: TipoIdentidade, bloquear: bool, ctx: Contexto) -> IdentidadeOut:
    return executar_auditado(
        ctx, Acao.BLOQUEAR_IDENTIDADE if bloquear else Acao.DESBLOQUEAR_IDENTIDADE, login, {},
        lambda: _executar_bloqueio(login, tipo, bloquear),
    )


def _executar_bloqueio(login: str, tipo: TipoIdentidade, bloquear: bool) -> tuple[IdentidadeOut, dict]:
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        exigir_operativos(c)
        if bloquear == c.bloqueada:
            raise HTTPException(
                status_code=409,
                detail=f"A identidade já está {'bloqueada' if bloquear else 'desbloqueada'}",
            )
        novo = at.bloquear(c.uac) if bloquear else at.desbloquear(c.uac)
        alterar_uac(conn, c.dn, novo)
    return replace(c, uac=novo).para_out(), {"uac_anterior": c.uac, "uac_novo": novo}


@tratar_erros
def bloquear(login: str, tipo: TipoIdentidade, ctx: Contexto) -> IdentidadeOut:
    return _alternar_bloqueio(login, tipo, True, ctx)


@tratar_erros
def desbloquear(login: str, tipo: TipoIdentidade, ctx: Contexto) -> IdentidadeOut:
    return _alternar_bloqueio(login, tipo, False, ctx)


# =============================================================================
# Remover fisicamente: só inclusão indevida ou duplicada, só em Inoperantes
# =============================================================================

@tratar_erros
def remover(login: str, tipo: TipoIdentidade, motivo: str, ctx: Contexto) -> None:
    executar_auditado(ctx, Acao.REMOVER_IDENTIDADE, login, {"motivo": motivo},
                      lambda: _executar_remover(login, tipo))


def _executar_remover(login: str, tipo: TipoIdentidade) -> tuple[None, dict]:
    with conexao() as conn:
        c = exigir(conn, login, tipo)
        if c.arvore is not Arvore.INOPERANTES:
            raise HTTPException(
                status_code=409,
                detail=f"Só é possível remover fisicamente identidades em Inoperantes (está em {c.arvore.ou})",
            )
        conn.delete(c.dn)
    return None, {"dn": c.dn}
