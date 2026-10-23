"""
Atributos do AD usados pela API: nomes `pml*`, bits do userAccountControl e leitura de
valores devolvidos pela busca.
"""
from dataclasses import dataclass
from typing import Optional

# =============================================================================
# Atributos pml* (a extensão do schema do AD é pedida à Infraestrutura)
# =============================================================================

PML_NOME_ORGAO = "pmlNomeOrgao"
PML_CPF = "pmlCpf"
PML_NAO_HUMANO_TIPO = "pmlNaoHumanoTipo"


@dataclass(frozen=True)
class AtoPml:
    """Par de atributos que documenta um ato: o instrumento legal e a data."""
    instrumento: str
    data: str

    @property
    def nomes(self) -> tuple[str, str]:
        return (self.instrumento, self.data)

    def valores(self, instrumento: str, data: str) -> dict[str, str]:
        return {self.instrumento: instrumento, self.data: data}


DESINCORPORADO = AtoPml("pmlDesincorporadoInstrumento", "pmlDesincorporadoData")
REINCORPORADO = AtoPml("pmlReincorporadoInstrumento", "pmlReincorporadoData")
DESTITUIDO = AtoPml("pmlDestituidoInstrumento", "pmlDestituidoData")
ATIVADO = AtoPml("pmlAtivadoInstrumento", "pmlAtivadoData")
TRANSFERIDO = AtoPml("pmlTransferidoInstrumento", "pmlTransferidoData")

# Atributos pml* lidos de uma identidade
PML_IDENTIDADE = (
    PML_CPF, PML_NAO_HUMANO_TIPO, *DESTITUIDO.nomes, *ATIVADO.nomes, *TRANSFERIDO.nomes,
)


# =============================================================================
# userAccountControl
# =============================================================================

UAC_DESABILITADA = 2          # ACCOUNTDISABLE
UAC_SENHA_NAO_EXIGIDA = 32    # PASSWD_NOTREQD: a API nunca a liga e a limpa ao ativar
UAC_SENHA_NAO_EXPIRA = 65536  # DONT_EXPIRE_PASSWD: contas não humanas
UAC_NOVA_CONTA = 514          # normal + desabilitada; SEM PASSWD_NOTREQD
UAC_PADRAO = 512              # conta normal habilitada, se o AD não devolver o valor


def bloqueada(uac: int) -> bool:
    return bool(uac & UAC_DESABILITADA)


def bloquear(uac: int) -> int:
    return uac | UAC_DESABILITADA


def desbloquear(uac: int) -> int:
    return uac & ~UAC_DESABILITADA


def sem_expiracao(uac: int) -> bool:
    return bool(uac & UAC_SENHA_NAO_EXPIRA)


def habilitar_ao_ativar(uac: int, nao_humano: bool = False) -> int:
    """
    Habilita e limpa o PASSWD_NOTREQD; preserva as demais flags. Conta não humana também fica
    com a senha sem expiração (não troca senha).
    """
    novo = uac & ~UAC_DESABILITADA & ~UAC_SENHA_NAO_EXIGIDA
    return novo | UAC_SENHA_NAO_EXPIRA if nao_humano else novo


# =============================================================================
# Valores devolvidos pelas buscas
# =============================================================================

def texto(attrs: dict, nome: str) -> Optional[str]:
    """Primeiro valor de um atributo, como texto (aceita escalar, lista ou bytes)."""
    valor = attrs.get(nome)
    if isinstance(valor, (list, tuple)):
        valor = valor[0] if valor else None
    if isinstance(valor, bytes):
        valor = valor.decode("utf-8", errors="replace")
    return str(valor) if valor not in (None, "") else None


def uac_de(attrs: dict) -> int:
    valor = texto(attrs, "userAccountControl")
    return int(valor) if valor and valor.isdigit() else UAC_PADRAO
