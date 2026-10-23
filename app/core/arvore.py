"""
Vocabulário da árvore do AD: árvores, tipos, ramos, categorias e como montar
e ler DNs. É o ÚNICO lugar onde aparecem os nomes das OUs fixas.

    <AD_PML_BASE>
      OU=<Arvore>                 Operativos | Inoperantes | Desincorporados
        OU=<Tipo>                 Humanos | NaoHumanos
          OU=<Ramo>               Direta | Indireta | Terceirizadas | Prepostos
            OU=<UNIDADE>
              OU=<categoria>      só em Humanos/Direta: Estagio | Carreira | Comissionados

Humanos e não humanos ficam em ramos separados desde o topo: uma base LDAP só de
humanos (`OU=Humanos,OU=Operativos,...`). A unidade existe nos dois tipos.

Na API, árvores, tipos e ramos são os valores minúsculos dos enums (`direta`, `terceirizada`...);
no AD, o nome da OU é a propriedade `.ou`.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ldap3.utils.dn import escape_rdn

from app.core.config import settings
from app.core.raiz import componentes_dn


class Arvore(str, Enum):
    OPERATIVOS = "operativos"
    INOPERANTES = "inoperantes"
    DESINCORPORADOS = "desincorporados"

    @property
    def ou(self) -> str:
        return self.value.capitalize()

    @classmethod
    def da_ou(cls, nome: str) -> Optional["Arvore"]:
        """A árvore cuja OU tem este nome (sem diferenciar maiúsculas)."""
        return _ARVORE_POR_OU.get(nome.lower())


class Ramo(str, Enum):
    DIRETA = "direta"
    INDIRETA = "indireta"
    TERCEIRIZADA = "terceirizada"
    PREPOSTO = "preposto"

    @property
    def ou(self) -> str:
        return _OU_DO_RAMO[self]

    @classmethod
    def da_ou(cls, nome: str) -> Optional["Ramo"]:
        return _RAMO_POR_OU.get(nome.lower())


class Categoria(str, Enum):
    """Categorias de humanos; existem só em unidades da Direta."""
    ESTAGIO = "estagio"
    CARREIRA = "carreira"
    COMISSIONADO = "comissionado"

    @property
    def ou(self) -> str:
        return _OU_DA_CATEGORIA[self]

    @classmethod
    def da_ou(cls, nome: str) -> Optional["Categoria"]:
        """None para qualquer OU desconhecida."""
        return _CATEGORIA_POR_OU.get(nome.lower())


class TipoIdentidade(str, Enum):
    HUMANO = "humano"
    NAO_HUMANO = "nao_humano"

    @property
    def ou(self) -> str:
        return "Humanos" if self is TipoIdentidade.HUMANO else "NaoHumanos"

    @classmethod
    def da_ou(cls, nome: str) -> Optional["TipoIdentidade"]:
        return _TIPO_POR_OU.get(nome.lower())


_OU_DO_RAMO = {
    Ramo.DIRETA: "Direta", Ramo.INDIRETA: "Indireta",
    Ramo.TERCEIRIZADA: "Terceirizadas", Ramo.PREPOSTO: "Prepostos",
}
_OU_DA_CATEGORIA = {
    Categoria.ESTAGIO: "Estagio", Categoria.CARREIRA: "Carreira", Categoria.COMISSIONADO: "Comissionados",
}
_ARVORE_POR_OU = {a.ou.lower(): a for a in Arvore}
_RAMO_POR_OU = {r.ou.lower(): r for r in Ramo}
_CATEGORIA_POR_OU = {c.ou.lower(): c for c in Categoria}
_TIPO_POR_OU = {t.ou.lower(): t for t in TipoIdentidade}

HUMANO, NAO_HUMANO = TipoIdentidade.HUMANO, TipoIdentidade.NAO_HUMANO
OUS_INTERNAS_DIRETA = tuple(c.ou for c in Categoria)     # só em Humanos/Direta
ARVORES_ESPELHADAS = (Arvore.OPERATIVOS, Arvore.INOPERANTES)

# Nomes fixos da estrutura: uma unidade não pode ter um deles (colidiria com a árvore).
NOMES_RESERVADOS = frozenset(
    nome.upper() for nome in (
        *(a.ou for a in Arvore), *(t.ou for t in TipoIdentidade), *(r.ou for r in Ramo), *OUS_INTERNAS_DIRETA,
    )
)


# =============================================================================
# Montar DNs
# =============================================================================

def rdn_ou(nome: str) -> str:
    """RDN de uma OU; o nome é escapado."""
    return f"OU={escape_rdn(nome)}"


def rdn_cn(nome: str) -> str:
    """RDN de uma conta; o nome é escapado."""
    return f"CN={escape_rdn(nome)}"


def dn_arvore(arvore: Arvore) -> str:
    return f"OU={arvore.ou},{settings.AD_PML_BASE}"


def dn_tipo(arvore: Arvore, tipo: TipoIdentidade) -> str:
    """A base de todas as identidades de um tipo numa árvore (ex.: a base do realm de humanos)."""
    return f"OU={tipo.ou},{dn_arvore(arvore)}"


def dn_ramo(arvore: Arvore, ramo: Ramo, tipo: TipoIdentidade = HUMANO) -> str:
    return f"OU={ramo.ou},{dn_tipo(arvore, tipo)}"


def dn_unidade(arvore: Arvore, ramo: Ramo, nome: str, tipo: TipoIdentidade = HUMANO) -> str:
    return f"{rdn_ou(nome)},{dn_ramo(arvore, ramo, tipo)}"


def dns_da_unidade(arvore: Arvore, ramo: Ramo, nome: str) -> tuple[str, str]:
    """Os dois lados de uma unidade numa árvore: (Humanos, NaoHumanos)."""
    return dn_unidade(arvore, ramo, nome, HUMANO), dn_unidade(arvore, ramo, nome, NAO_HUMANO)


def ou_interna(ramo: Ramo, tipo: TipoIdentidade, categoria: Optional[Categoria]) -> Optional[str]:
    """OU interna em que uma identidade fica: só a de categoria de um humano da Direta."""
    if tipo is NAO_HUMANO or ramo is not Ramo.DIRETA:
        return None
    return categoria.ou if categoria else None


def dn_container(arvore: Arvore, ramo: Ramo, unidade: str, categoria: Optional[Categoria] = None,
                 tipo: TipoIdentidade = HUMANO) -> str:
    """
    DN onde as identidades de uma unidade ficam: a própria OU da unidade (do lado do tipo) ou,
    para humanos da Direta, a OU interna da categoria.
    """
    base = dn_unidade(arvore, ramo, unidade, tipo)
    interna = ou_interna(ramo, tipo, categoria)
    return f"OU={interna},{base}" if interna else base


# =============================================================================
# Ler DNs
# =============================================================================

def local_da_unidade(dn: str) -> Optional[tuple[Arvore, Ramo, TipoIdentidade]]:
    """
    (árvore, ramo, tipo) de uma UNIDADE, isto é, de um DN com exatamente quatro níveis abaixo de
    AD_PML_BASE (<unidade>/<ramo>/<tipo>/<árvore>); senão None.
    """
    alvo = componentes_dn(dn)
    abaixo = len(alvo) - len(componentes_dn(settings.AD_PML_BASE))
    if abaixo != 4:
        return None
    # alvo vem do mais específico para a raiz: [unidade, ramo, tipo, arvore, <PML_BASE>...]
    arvore, tipo, ramo = Arvore.da_ou(alvo[3][1]), TipoIdentidade.da_ou(alvo[2][1]), Ramo.da_ou(alvo[1][1])
    return (arvore, ramo, tipo) if arvore and ramo and tipo else None


@dataclass(frozen=True)
class LocalIdentidade:
    arvore: Arvore
    tipo: TipoIdentidade
    ramo: Ramo
    unidade: str
    categoria: Optional[Categoria]   # só humanos da Direta


def local_da_identidade(dn: str) -> Optional[LocalIdentidade]:
    """Onde uma identidade está, pelo DN; None se o DN não segue a estrutura esperada."""
    alvo = componentes_dn(dn)
    abaixo = len(alvo) - len(componentes_dn(settings.AD_PML_BASE))
    if abaixo < 5:
        return None
    # da raiz para a folha: árvore, tipo, ramo, unidade, [categoria], CN
    rel = list(reversed(alvo[:abaixo]))
    arvore, tipo, ramo = Arvore.da_ou(rel[0][1]), TipoIdentidade.da_ou(rel[1][1]), Ramo.da_ou(rel[2][1])
    if not arvore or not tipo or not ramo:
        return None
    if tipo is HUMANO and ramo is Ramo.DIRETA:
        categoria = Categoria.da_ou(rel[4][1]) if abaixo == 6 else None
        if abaixo != 6 or categoria is None:
            return None
    else:
        if abaixo != 5:
            return None
        categoria = None
    return LocalIdentidade(arvore, tipo, ramo, rel[3][1].upper(), categoria)
