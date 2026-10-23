"""
Unidades (OUs) da estrutura: criar, alterar, consultar, desincorporar e
reincorporar, nos 4 ramos. A forma da árvore está em app/core/arvore.py.

Uma unidade tem DOIS lados em cada árvore, o de Humanos e o de NaoHumanos; toda
operação de unidade age nos dois. O lado Humanos é o que as listagens e os DNs principais mostram.
"""
from functools import partial
from typing import NamedTuple, Optional

from fastapi import HTTPException
from ldap3 import BASE, LEVEL, SUBTREE
from ldap3.utils.conv import escape_filter_chars

from app.audit_service import Acao, executar_auditado, marcar_inconsistente
from app.core.arvore import (
    ARVORES_ESPELHADAS, HUMANO, NAO_HUMANO, OUS_INTERNAS_DIRETA, Arvore, Ramo, TipoIdentidade,
    dn_arvore, dn_ramo, dn_tipo, dn_unidade, dns_da_unidade, local_da_unidade, rdn_ou,
)
from app.core.atributos import (
    DESINCORPORADO, PML_NOME_ORGAO, REINCORPORADO, bloqueada, bloquear, desbloquear, texto,
)
from app.core.config import settings
from app.core.contexto import Contexto
from app.core.erros_ad import tratar_erros
from app.core.ldap_connection import buscar, conexao
from app.core.logging_config import logger
from app.core.raiz import mascarar_dn
from app.schemas.estrutura import (
    AtoUnidade, OUCreate, OUOut, OUUpdate, UnidadeItem, UnidadeListOut, UnidadeMovidaOut, UnidadeOut,
)
from app.services.base_ad import (
    alterar_uac, contas_da_unidade, data_do_ato, gravar_pml, reverter, unidade_existe,
)


class UnidadeAchada(NamedTuple):
    dn: str
    arvore: Arvore
    ramo: Ramo
    tipo: TipoIdentidade
    pml_nome_orgao: Optional[str]


# =============================================================================
# Leitura
# =============================================================================

def _achar_unidades(conn, nome: str) -> list[UnidadeAchada]:
    """Todas as ocorrências de uma unidade, em qualquer ramo, árvore e lado, sob AD_PML_BASE."""
    achadas = buscar(
        conn, settings.AD_PML_BASE,
        f"(&(objectClass=organizationalUnit)(ou={escape_filter_chars(nome)}))",
        SUBTREE, ["ou", PML_NOME_ORGAO],
    )
    unidades = []
    for entrada in achadas:
        local = local_da_unidade(entrada["dn"])
        if local:  # ignora OUs que não estão no formato <unidade>/<ramo>/<tipo>/<árvore>
            unidades.append(UnidadeAchada(
                dn=entrada["dn"], arvore=local[0], ramo=local[1], tipo=local[2],
                pml_nome_orgao=texto(entrada.get("attributes", {}), PML_NOME_ORGAO),
            ))
    return unidades


def _ler_pml_nome(conn, dn: str) -> Optional[str]:
    achadas = buscar(conn, dn, "(objectClass=*)", BASE, [PML_NOME_ORGAO])
    return texto(achadas[0].get("attributes", {}), PML_NOME_ORGAO) if achadas else None


def _existe_filho(conn, parent_dn: str, nome: str) -> bool:
    """Existe um filho direto com cn=<nome> ou ou=<nome> sob parent_dn?"""
    valor = escape_filter_chars(nome)
    return len(buscar(conn, parent_dn, f"(|(cn={valor})(ou={valor}))", LEVEL, ["distinguishedName"])) > 0


@tratar_erros
def listar_unidades(ramo: Ramo, arvore: Arvore, limite: int, deslocamento: int) -> UnidadeListOut:
    """Lista paginada das unidades de um ramo, numa árvore (lado Humanos)."""
    with conexao() as conn:
        entradas = buscar(conn, dn_ramo(arvore, ramo), "(objectClass=organizationalUnit)",
                          LEVEL, ["ou", PML_NOME_ORGAO])
    itens = sorted(
        (
            UnidadeItem(
                nome=texto(e.get("attributes", {}), "ou") or e["dn"].split(",", 1)[0][3:],
                ramo=ramo,
                arvore=arvore,
                pml_nome_orgao=texto(e.get("attributes", {}), PML_NOME_ORGAO),
                distinguished_name=e["dn"],
            )
            for e in entradas
        ),
        key=lambda i: i.nome,
    )
    return UnidadeListOut(
        total=len(itens), limite=limite, deslocamento=deslocamento,
        items=itens[deslocamento:deslocamento + limite],
    )


@tratar_erros
def consultar_unidade(ramo: Ramo, nome: str) -> UnidadeOut:
    """Uma unidade pelo nome, com as árvores em que existe e os DNs dos dois lados."""
    nome = nome.strip().upper()
    with conexao() as conn:
        achadas = [u for u in _achar_unidades(conn, nome) if u.ramo == ramo]
    if not achadas:
        raise HTTPException(status_code=404, detail=f"Unidade '{nome}' não encontrada no ramo {ramo.ou}")
    # Prefere o valor de Operativos; senão, o primeiro encontrado.
    achadas.sort(key=lambda u: (u.arvore is not Arvore.OPERATIVOS, u.tipo is not HUMANO))
    return UnidadeOut(
        nome=nome,
        ramo=ramo,
        arvores=sorted({u.arvore for u in achadas}, key=lambda a: a.value),
        pml_nome_orgao=next((u.pml_nome_orgao for u in achadas if u.pml_nome_orgao), None),
        distinguished_names={u.arvore: u.dn for u in achadas if u.tipo is HUMANO},
        distinguished_names_nao_humanos={u.arvore: u.dn for u in achadas if u.tipo is NAO_HUMANO},
    )


# =============================================================================
# Estrutura fixa e criação de OUs
# =============================================================================

def _criar_ou(conn, parent_dn: str, nome: str) -> str:
    """Cria uma OU sob parent_dn e devolve o DN criado."""
    dn = f"{rdn_ou(nome)},{parent_dn}"
    conn.add(dn, attributes={"objectClass": ["top", "organizationalUnit"], "ou": nome})
    return dn


def _garantir_ou(conn, parent_dn: str, nome: str) -> str:
    """Cria a OU se não existir; devolve o DN dela em qualquer caso."""
    if _existe_filho(conn, parent_dn, nome):
        return f"{rdn_ou(nome)},{parent_dn}"
    return _criar_ou(conn, parent_dn, nome)


def _garantir_ramo(conn, arvore: Arvore, tipo: TipoIdentidade, ramo: Ramo) -> str:
    """
    Garante os nós fixos <ramo>/<tipo>/<árvore> (criados se faltarem, como o ramo de
    Desincorporados sempre foi) e devolve o DN do ramo. A OU da árvore tem de existir.
    """
    _garantir_ou(conn, dn_arvore(arvore), tipo.ou)
    return _garantir_ou(conn, dn_tipo(arvore, tipo), ramo.ou)


def _desfazer_criacao(conn, criados: list[str]) -> None:
    """Remove, dos mais novos para os mais antigos, o que a operação já criou."""
    for dn in reversed(criados):
        reverter(partial(conn.delete, dn),
                 f"não foi possível desfazer a criação de {mascarar_dn(dn)}; remover manualmente")


def _exigir_arvore(conn, arvore: Arvore) -> None:
    if not unidade_existe(conn, dn_arvore(arvore)):
        raise HTTPException(status_code=409, detail=f"Estrutura base ausente no AD: OU={arvore.ou}")


def _exigir_lados(conn, nome: str, ramo: Ramo, arvore: Arvore, *, ausente: str) -> tuple[str, str]:
    """
    DNs (Humanos, NaoHumanos) da unidade na árvore. Sem o lado Humanos, 404 com `ausente`;
    com Humanos e sem NaoHumanos, 409: a estrutura está incompleta (não se adivinha o que fazer).
    """
    dn_h, dn_nh = dns_da_unidade(arvore, ramo, nome)
    if not unidade_existe(conn, dn_h):
        raise HTTPException(status_code=404, detail=ausente)
    if not unidade_existe(conn, dn_nh):
        raise HTTPException(
            status_code=409,
            detail=f"A unidade '{nome}' está incompleta em {arvore.ou}/{ramo.ou}: falta o lado NaoHumanos",
        )
    return dn_h, dn_nh


# =============================================================================
# Criar
# =============================================================================

@tratar_erros
def criar_ou(ramo: Ramo, dados: OUCreate, ctx: Contexto) -> OUOut:
    """
    Cria a unidade em Operativos E em Inoperantes, em cada uma nos lados Humanos e NaoHumanos
    (4 OUs). Na Direta, o lado Humanos nasce com as OUs de categoria. Depois grava
    pmlNomeOrgao nas 4. Se qualquer passo falhar, o que a operação criou é desfeito (os nós
    fixos garantidos permanecem).

    O nome é único em toda a árvore: existir em qualquer ramo, árvore ou lado,
    inclusive Desincorporados, resulta em 409.
    """
    return executar_auditado(
        ctx, Acao.CRIAR_UNIDADE, dados.nome,
        {"ramo": ramo.ou, "pml_nome_orgao": dados.pml_nome_orgao or dados.nome},
        lambda: _executar_criar(ramo, dados),
    )


def _executar_criar(ramo: Ramo, dados: OUCreate) -> tuple[OUOut, dict]:
    pml_nome_orgao = dados.pml_nome_orgao or dados.nome
    criados: list[str] = []
    avisos: list[str] = []
    with conexao() as conn:
        existentes = _achar_unidades(conn, dados.nome)
        if existentes:
            locais = sorted({f"{u.arvore.ou}/{u.tipo.ou}/{u.ramo.ou}" for u in existentes})
            raise HTTPException(
                status_code=409, detail=f"Já existe uma unidade '{dados.nome}' em {', '.join(locais)}",
            )
        for arvore in ARVORES_ESPELHADAS:
            _exigir_arvore(conn, arvore)

        try:
            for arvore in ARVORES_ESPELHADAS:
                for tipo in (HUMANO, NAO_HUMANO):
                    pai = _garantir_ramo(conn, arvore, tipo, ramo)
                    dn = _criar_ou(conn, pai, dados.nome)
                    criados.append(dn)
                    if tipo is HUMANO and ramo is Ramo.DIRETA:
                        for interna in OUS_INTERNAS_DIRETA:
                            criados.append(_criar_ou(conn, dn, interna))

            # Se pmlNomeOrgao ainda não existir no schema, falha aqui com
            # AD_SCHEMA_INCOMPLETO e a criação acima é desfeita.
            for arvore in ARVORES_ESPELHADAS:
                for dn in dns_da_unidade(arvore, ramo, dados.nome):
                    gravar_pml(conn, dn, {PML_NOME_ORGAO: pml_nome_orgao}, avisos)
        except Exception:
            _desfazer_criacao(conn, criados)
            raise

    saida = OUOut(
        nome=dados.nome,
        ramo=ramo,
        pml_nome_orgao=pml_nome_orgao,
        distinguished_name_operativos=dn_unidade(Arvore.OPERATIVOS, ramo, dados.nome, HUMANO),
        distinguished_name_inoperantes=dn_unidade(Arvore.INOPERANTES, ramo, dados.nome, HUMANO),
        distinguished_name_operativos_nao_humanos=dn_unidade(Arvore.OPERATIVOS, ramo, dados.nome, NAO_HUMANO),
        distinguished_name_inoperantes_nao_humanos=dn_unidade(Arvore.INOPERANTES, ramo, dados.nome, NAO_HUMANO),
        avisos=avisos,
    )
    return saida, {"pml_gravado": not avisos,
                   "ous_internas": list(OUS_INTERNAS_DIRETA) if ramo is Ramo.DIRETA else []}


# =============================================================================
# Alterar
# =============================================================================

@tratar_erros
def alterar_ou(ramo: Ramo, nome: str, dados: OUUpdate, ctx: Contexto) -> OUOut:
    """
    Altera pmlNomeOrgao nas 4 OUs da unidade (dois lados em Operativos e em Inoperantes). Só vale
    para unidade que está em Operativos (desincorporadas não são alteráveis). Se uma gravação
    falhar, as anteriores voltam ao valor anterior.
    """
    return executar_auditado(
        ctx, Acao.ALTERAR_UNIDADE, nome, {"ramo": ramo.ou, "pml_nome_orgao": dados.pml_nome_orgao},
        lambda: _executar_alterar(ramo, nome, dados),
    )


def _executar_alterar(ramo: Ramo, nome: str, dados: OUUpdate) -> tuple[OUOut, dict]:
    avisos: list[str] = []

    with conexao() as conn:
        dn_oh, dn_onh = _exigir_lados(
            conn, nome, ramo, Arvore.OPERATIVOS,
            ausente=f"Unidade '{nome}' não encontrada em Operativos/{ramo.ou} "
                    f"(não é possível alterar unidades desincorporadas)",
        )
        dn_ih, dn_inh = dns_da_unidade(Arvore.INOPERANTES, ramo, nome)
        for dn in (dn_ih, dn_inh):
            if not unidade_existe(conn, dn):
                raise HTTPException(
                    status_code=409,
                    detail=f"O espelho da unidade '{nome}' em Inoperantes/{ramo.ou} está incompleto no AD",
                )
        lados = (dn_oh, dn_onh, dn_ih, dn_inh)

        # Com PML_GRAVAR=false nada é gravado (só avisa) e não há o que restaurar.
        anteriores = {dn: _ler_pml_nome(conn, dn) for dn in lados} if settings.PML_GRAVAR else {}
        alterados: list[str] = []
        try:
            for dn in lados:
                # Se pmlNomeOrgao não existir no schema: AD_SCHEMA_INCOMPLETO.
                gravar_pml(conn, dn, {PML_NOME_ORGAO: dados.pml_nome_orgao}, avisos)
                alterados.append(dn)
        except Exception:
            for dn in reversed(alterados):
                reverter(partial(gravar_pml, conn, dn, {PML_NOME_ORGAO: anteriores[dn]}, []),
                         f"não foi possível restaurar {PML_NOME_ORGAO} em {mascarar_dn(dn)}")
            raise

    saida = OUOut(
        nome=nome,
        ramo=ramo,
        pml_nome_orgao=dados.pml_nome_orgao,
        distinguished_name_operativos=dn_oh,
        distinguished_name_inoperantes=dn_ih,
        distinguished_name_operativos_nao_humanos=dn_onh,
        distinguished_name_inoperantes_nao_humanos=dn_inh,
        avisos=avisos,
    )
    return saida, {"pml_gravado": not avisos}


# =============================================================================
# Desincorporar e reincorporar
# =============================================================================

def _mover_lados(conn, nome: str, origem: tuple[str, str], destino_pai: tuple[str, str],
                 destino_final: tuple[str, str], pai_origem: tuple[str, str]) -> None:
    """
    Move os dois lados da unidade (primeiro NaoHumanos, depois Humanos). Se o segundo move falhar,
    o primeiro volta; se o retorno também falhar, fica INCONSISTENTE (a causa original sobe).
    """
    conn.modify_dn(origem[1], rdn_ou(nome), new_superior=destino_pai[1])
    try:
        conn.modify_dn(origem[0], rdn_ou(nome), new_superior=destino_pai[0])
    except Exception:
        reverter(partial(conn.modify_dn, destino_final[1], rdn_ou(nome), new_superior=pai_origem[1]),
                 f"o lado NaoHumanos da unidade '{nome}' foi movido e o lado Humanos não; "
                 f"o retorno falhou ({mascarar_dn(destino_final[1])})")
        raise


@tratar_erros
def desincorporar_unidade(ramo: Ramo, nome: str, ato: AtoUnidade, ctx: Contexto) -> UnidadeMovidaOut:
    """
    Tira a unidade de Operativos e a leva para Desincorporados, com todo o conteúdo, nos dois
    lados (Humanos e NaoHumanos). Ordem: (1) grava pmlDesincorporado*, (2) bloqueia as contas
    habilitadas dos dois lados, (3) move os lados. A OU espelho em Inoperantes não é tocada. Se o
    passo 1 falhar (ex.: schema), nada foi alterado. Se o passo 2 ou 3 falhar, as contas já
    bloqueadas CONTINUAM bloqueadas (falha segura): registra INCONSISTENTE; repetir a operação é
    seguro, pois contas já bloqueadas são puladas.
    """
    nome = nome.strip().upper()
    data = data_do_ato(ato)
    return executar_auditado(
        ctx, Acao.DESINCORPORAR_UNIDADE, nome,
        {"ramo": ramo.ou, "instrumento": ato.instrumento, "data": data},
        lambda: _executar_desincorporar(ramo, nome, ato, data),
    )


def _executar_desincorporar(ramo: Ramo, nome: str, ato: AtoUnidade, data: str) -> tuple[UnidadeMovidaOut, dict]:
    final = dns_da_unidade(Arvore.DESINCORPORADOS, ramo, nome)
    avisos: list[str] = []
    bloqueadas: list[str] = []

    with conexao() as conn:
        atual = _exigir_lados(conn, nome, ramo, Arvore.OPERATIVOS,
                              ausente=f"Unidade '{nome}' não encontrada em Operativos/{ramo.ou}")
        if any(unidade_existe(conn, dn) for dn in final):
            raise HTTPException(status_code=409, detail=f"A unidade '{nome}' já existe em Desincorporados/{ramo.ou}")
        # Os nós fixos de Desincorporados são criados se faltarem.
        pais = (_garantir_ramo(conn, Arvore.DESINCORPORADOS, HUMANO, ramo),
                _garantir_ramo(conn, Arvore.DESINCORPORADOS, NAO_HUMANO, ramo))
        pais_origem = (dn_ramo(Arvore.OPERATIVOS, ramo, HUMANO), dn_ramo(Arvore.OPERATIVOS, ramo, NAO_HUMANO))

        for dn in atual:
            gravar_pml(conn, dn, DESINCORPORADO.valores(ato.instrumento, data), avisos)
        try:
            for conta in contas_da_unidade(conn, *atual):
                if bloqueada(conta.uac):
                    continue  # já bloqueada: preserva o estado
                alterar_uac(conn, conta.dn, bloquear(conta.uac))
                bloqueadas.append(conta.login)
            _mover_lados(conn, nome, atual, pais, final, pais_origem)
        except Exception:
            if bloqueadas:
                logger.error(
                    f"INCONSISTENTE: desincorporar '{nome}' falhou depois de bloquear {len(bloqueadas)} "
                    "conta(s); elas permanecem bloqueadas na unidade em Operativos. Repetir é seguro."
                )
                marcar_inconsistente()
            raise

    saida = UnidadeMovidaOut(nome=nome, ramo=ramo, distinguished_name=final[0],
                             distinguished_name_nao_humanos=final[1],
                             instrumento=ato.instrumento, data=data, contas=bloqueadas, avisos=avisos)
    return saida, {"contas_bloqueadas": bloqueadas, "pml_gravado": not avisos}


@tratar_erros
def reincorporar_unidade(ramo: Ramo, nome: str, ato: AtoUnidade, ctx: Contexto) -> UnidadeMovidaOut:
    """
    Traz de volta a unidade de Desincorporados para Operativos (os dois lados) e desbloqueia
    TODAS as contas dela, inclusive as que já estavam bloqueadas antes.
    Ordem: (1) grava pmlReincorporado*, (2) move, (3) desbloqueia as contas.
    Se o passo 3 falhar no meio, a unidade já está em Operativos e parte das contas segue
    bloqueada: registra INCONSISTENTE e informa quantas faltam.
    """
    nome = nome.strip().upper()
    data = data_do_ato(ato)
    return executar_auditado(
        ctx, Acao.REINCORPORAR_UNIDADE, nome,
        {"ramo": ramo.ou, "instrumento": ato.instrumento, "data": data},
        lambda: _executar_reincorporar(ramo, nome, ato, data),
    )


def _executar_reincorporar(ramo: Ramo, nome: str, ato: AtoUnidade, data: str) -> tuple[UnidadeMovidaOut, dict]:
    final = dns_da_unidade(Arvore.OPERATIVOS, ramo, nome)
    avisos: list[str] = []
    desbloqueadas: list[str] = []

    with conexao() as conn:
        atual = _exigir_lados(conn, nome, ramo, Arvore.DESINCORPORADOS,
                              ausente=f"Unidade '{nome}' não encontrada em Desincorporados/{ramo.ou}")
        if any(unidade_existe(conn, dn) for dn in final):
            raise HTTPException(status_code=409, detail=f"A unidade '{nome}' já existe em Operativos/{ramo.ou}")
        pais = (_garantir_ramo(conn, Arvore.OPERATIVOS, HUMANO, ramo),
                _garantir_ramo(conn, Arvore.OPERATIVOS, NAO_HUMANO, ramo))
        pais_origem = (dn_ramo(Arvore.DESINCORPORADOS, ramo, HUMANO), dn_ramo(Arvore.DESINCORPORADOS, ramo, NAO_HUMANO))

        for dn in atual:
            gravar_pml(conn, dn, REINCORPORADO.valores(ato.instrumento, data), avisos)
        _mover_lados(conn, nome, atual, pais, final, pais_origem)

        try:
            for conta in contas_da_unidade(conn, *final):
                if not bloqueada(conta.uac):
                    continue  # já habilitada
                alterar_uac(conn, conta.dn, desbloquear(conta.uac))
                desbloqueadas.append(conta.login)
        except Exception:
            logger.error(
                f"INCONSISTENTE: reincorporar '{nome}' moveu a unidade, mas desbloqueou só "
                f"{len(desbloqueadas)} conta(s); as demais seguem bloqueadas em Operativos."
            )
            marcar_inconsistente()
            raise

    saida = UnidadeMovidaOut(nome=nome, ramo=ramo, distinguished_name=final[0],
                             distinguished_name_nao_humanos=final[1],
                             instrumento=ato.instrumento, data=data, contas=desbloqueadas, avisos=avisos)
    return saida, {"contas_desbloqueadas": desbloqueadas, "pml_gravado": not avisos}
