import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from .estrutura import RamoOU


class TipoPessoa(str, Enum):
    """
    Os 4 subcontainers que existem dentro de cada unidade da Direta.
    (Indireta/Terceirizadas/Prepostos não têm essa subdivisão.)
    """
    ESTAGIO = "Estagio"
    CARREIRA = "Carreira"
    COMISSIONADO = "Comissionados"
    NAO_HUMANO = "NaoHumanos"


# Regras de validação copiadas literalmente do documento da API:
#   samAccountName humano = mínimo 5, (a-zA-Z){2,10}.(a-zA-Z){2,10}
#   name humano           = mínimo 5, "Primeiro Ultimo" (cada parte capitalizada)
#   samAccountName não-humano = mínimo 5, nhu.(a-zA-Z){2,10}.(a-zA-Z){2,10}
#   name não-humano           = mínimo 5, só minúsculas
REGEX_LOGIN_HUMANO = re.compile(r"^[a-zA-Z]{2,10}\.[a-zA-Z]{2,10}$")
REGEX_NOME_HUMANO = re.compile(r"^[A-Z][a-z]+\s[A-Z][a-z]+$")
REGEX_LOGIN_NAO_HUMANO = re.compile(r"^nhu\.[a-zA-Z]{2,10}\.[a-zA-Z]{2,10}$")
REGEX_NOME_NAO_HUMANO = re.compile(r"^[a-z]{5,}$")


class PessoaCreate(BaseModel):
    """
    Payload para criar uma identidade (humana ou não) dentro de uma unidade
    da Direta. A pessoa é criada já em Inoperantes (bloqueada) — a ativação
    em Operativos acontece depois (fora do escopo desta função).
    """
    tipo: TipoPessoa
    unidade: str = Field(
        ...,
        example="FAZENDA",
        description="Nome (CN) da unidade da Direta onde a pessoa será alocada. Deve já existir.",
    )

    # --- campos para humanos (Estagio / Carreira / Comissionados) ---
    primeiro_nome: Optional[str] = Field(None, example="Joao")
    ultimo_nome: Optional[str] = Field(None, example="Silva")
    cpf: Optional[str] = None
    cargo: Optional[str] = None
    email: Optional[str] = None

    # --- campos exclusivos para NaoHumanos ---
    nao_humano_categoria: Optional[str] = Field(
        None,
        example="sistema",
        description="Primeiro segmento do login não-humano (ex.: 'sistema' em nhu.sistema.contas).",
    )
    nao_humano_identificador: Optional[str] = Field(
        None,
        example="contas",
        description="Segundo segmento do login não-humano (ex.: 'contas' em nhu.sistema.contas).",
    )
    nao_humano_tipo: Optional[str] = Field(
        None,
        example="impressora",
        description="Valor livre gravado em pmlNaoHumanoTipo (ex.: impressora, servico, software).",
    )

    @field_validator("primeiro_nome", "ultimo_nome")
    @classmethod
    def nome_capitalizado(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().capitalize()
        return v

    def validar_por_tipo(self) -> None:
        """
        Validação cruzada entre campos, chamada no service (Pydantic sozinho
        não valida bem campos condicionais entre si sem model_validator).
        """
        if self.tipo == TipoPessoa.NAO_HUMANO:
            if not self.nao_humano_categoria or not self.nao_humano_identificador:
                raise ValueError(
                    "Para tipo NaoHumanos é obrigatório informar "
                    "nao_humano_categoria e nao_humano_identificador"
                )
            nome_gerado = f"{self.nao_humano_categoria}{self.nao_humano_identificador}".lower()
            if not REGEX_NOME_NAO_HUMANO.match(nome_gerado) or len(nome_gerado) < 5:
                raise ValueError(
                    "Nome resultante do não-humano deve ter no mínimo 5 caracteres "
                    "e conter apenas letras minúsculas"
                )
        else:
            if not self.primeiro_nome or not self.ultimo_nome:
                raise ValueError(
                    "Para pessoas humanas é obrigatório informar primeiro_nome e ultimo_nome"
                )
            nome_completo = f"{self.primeiro_nome} {self.ultimo_nome}"
            if not REGEX_NOME_HUMANO.match(nome_completo) or len(nome_completo) < 5:
                raise ValueError(
                    "primeiro_nome/ultimo_nome devem começar com maiúscula, "
                    "resto minúsculo (ex.: 'Joao Silva')"
                )


class PessoaUpdate(BaseModel):
    """
    Payload para alterar os atributos mutáveis de uma identidade já existente.
    Só é permitido alterar dentro da árvore Operativos.
    """
    cargo: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    nao_humano_tipo: Optional[str] = None


class PessoaOut(BaseModel):
    login: str
    nome: str
    tipo: TipoPessoa
    unidade: str
    ramo: RamoOU = RamoOU.DIRETA
    ativo: bool
    distinguished_name: str
    cargo: Optional[str] = None
    email: Optional[str] = None


class PessoaCriadaOut(PessoaOut):
    senha_gerada: Optional[str] = None  # None para NaoHumanos
