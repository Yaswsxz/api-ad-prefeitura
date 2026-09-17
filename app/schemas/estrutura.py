from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RamoOU(str, Enum):
    """Os 4 ramos que existem dentro de Operativos/Inoperantes/Desincorporados."""
    DIRETA = "Direta"
    INDIRETA = "Indireta"
    TERCEIRIZADAS = "Terceirizadas"
    PREPOSTOS = "Prepostos"


class OUCreate(BaseModel):
    """
    Payload para criar um órgão/unidade dentro de um dos 4 ramos.
    O nome vira o CN técnico do nó (ex: "FAZENDA") e também é usado
    como valor inicial de pmlNomeOrgao.
    """
    nome: str = Field(
        ...,
        min_length=2,
        example="FAZENDA",
        description="Nome do órgão. Será normalizado para uppercase (mínimo 2 caracteres).",
    )
    pml_nome_orgao: Optional[str] = Field(
        None,
        example="Secretaria Municipal da Fazenda",
        description="Nome descritivo/oficial do órgão. Se não informado, usa o mesmo valor de 'nome'.",
    )

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) < 2:
            raise ValueError("Nome da OU deve ter no mínimo 2 caracteres")
        return v


class OUUpdate(BaseModel):
    """
    Payload para alterar um órgão já existente.
    Só é permitido alterar o atributo pmlNomeOrgao (nome descritivo) —
    o CN técnico (nome usado no DN) não é alterado por aqui.
    """
    pml_nome_orgao: str = Field(
        ...,
        min_length=2,
        example="Secretaria Municipal da Fazenda",
    )


class OUOut(BaseModel):
    nome: str
    ramo: RamoOU
    pml_nome_orgao: Optional[str] = None
    distinguished_name_operativos: str
    distinguished_name_inoperantes: Optional[str] = None


class OUMover(BaseModel):
    """Payload para desincorporar uma OU (Operativos -> Desincorporados)."""
    instrumento: str = Field(
        ...,
        example="Decreto nº 1234/2026",
        description="Instrumento legal que justifica a desincorporação (vira pmlDesincorporadoInstrumento).",
    )
