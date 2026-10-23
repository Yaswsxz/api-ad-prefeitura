import re
from datetime import date, datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.arvore import NOMES_RESERVADOS, Arvore, Ramo


def normalizar_nome_unidade(v: str) -> str:
    """Nome de unidade: trim, maiúsculas, 2 a 64 caracteres, sem caracteres de DN, não reservado."""
    v = v.strip().upper()
    if len(v) < 2:
        raise ValueError("Nome da OU deve ter no mínimo 2 caracteres")
    if len(v) > 64:
        raise ValueError("Nome da OU deve ter no máximo 64 caracteres")
    if re.search(r'[,=+<>#;\\"*()/]', v):
        raise ValueError('Nome da OU não pode conter os caracteres , = + < > # ; \\ " * ( ) /')
    if v in NOMES_RESERVADOS:
        raise ValueError(f"'{v}' é um nome reservado da estrutura e não pode ser usado em uma unidade")
    return v


class OUCreate(BaseModel):
    """
    Cria uma unidade num dos 4 ramos. O nome vira o RDN técnico da OU (ex.: "FAZENDA") e
    também o valor inicial de pmlNomeOrgao.
    """
    nome: str = Field(
        ..., min_length=2, json_schema_extra={"example": "FAZENDA"},
        description="Nome do órgão. Será normalizado para uppercase (mínimo 2 caracteres).",
    )
    pml_nome_orgao: Optional[str] = Field(
        None, json_schema_extra={"example": "Secretaria Municipal da Fazenda"},
        description="Nome descritivo/oficial do órgão. Se não informado, usa o mesmo valor de 'nome'.",
    )

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, v: str) -> str:
        return normalizar_nome_unidade(v)


class OUUpdate(BaseModel):
    """Só pmlNomeOrgao é alterável; o nome técnico (RDN) não muda por aqui."""
    pml_nome_orgao: str = Field(
        ..., min_length=2, json_schema_extra={"example": "Secretaria Municipal da Fazenda"},
    )


class OUOut(BaseModel):
    nome: str
    ramo: Ramo
    pml_nome_orgao: Optional[str] = None
    # DNs do lado Humanos; os do lado NaoHumanos vêm nos campos irmãos
    distinguished_name_operativos: str
    distinguished_name_inoperantes: Optional[str] = None
    distinguished_name_operativos_nao_humanos: Optional[str] = None
    distinguished_name_inoperantes_nao_humanos: Optional[str] = None
    avisos: list[str] = []   # ex.: atributos pml* não gravados (PML_GRAVAR=false)


class UnidadeItem(BaseModel):
    """Uma unidade numa listagem de uma árvore."""
    nome: str
    ramo: Ramo
    arvore: Arvore
    pml_nome_orgao: Optional[str] = None
    distinguished_name: str


class UnidadeListOut(BaseModel):
    total: int
    limite: int
    deslocamento: int
    items: list[UnidadeItem]


class UnidadeOut(BaseModel):
    """Uma unidade consultada pelo nome, com as árvores em que existe."""
    nome: str
    ramo: Ramo
    arvores: list[Arvore]
    pml_nome_orgao: Optional[str] = None
    distinguished_names: dict[Arvore, str]                       # lado Humanos
    distinguished_names_nao_humanos: dict[Arvore, str] = {}      # lado NaoHumanos


class AtoUnidade(BaseModel):
    """Corpo de um ato com instrumento legal e data (desincorporar, reincorporar e as ordens de identidade)."""
    instrumento: str = Field(
        ..., min_length=3, max_length=200,
        json_schema_extra={"example": "Decreto nº 1234/2026"},
        description="Ato legal que justifica a operação.",
    )
    data: Optional[date] = Field(
        None, description="Data do ato (AAAA-MM-DD). Padrão: hoje. Não pode ser futura."
    )

    @field_validator("instrumento")
    @classmethod
    def _instrumento(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Instrumento deve ter no mínimo 3 caracteres")
        return v

    @field_validator("data")
    @classmethod
    def _data_nao_futura(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > datetime.now(timezone.utc).date():
            raise ValueError("A data do ato não pode ser futura")
        return v


class UnidadeMovidaOut(BaseModel):
    """Resultado de desincorporar ou reincorporar uma unidade."""
    nome: str
    ramo: Ramo
    distinguished_name: str                                  # lado Humanos
    distinguished_name_nao_humanos: Optional[str] = None     # lado NaoHumanos
    instrumento: str
    data: str
    # Desincorporar: contas que esta operação bloqueou. Reincorporar: contas desbloqueadas.
    contas: list[str]
    avisos: list[str] = []
