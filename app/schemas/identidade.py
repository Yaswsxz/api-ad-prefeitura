"""
Identidades: humanos e não humanos, nos quatro ramos.
O `login` (sAMAccountName) é enviado pelo front-end; a API só valida padrão e
unicidade.
"""
import re
import unicodedata
from typing import ClassVar, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.arvore import Arvore, Categoria, Ramo, TipoIdentidade
from app.core.generators import TAMANHO_SENHA_MAX, TAMANHO_SENHA_MIN, TAMANHO_SENHA_PADRAO
from .estrutura import AtoUnidade, normalizar_nome_unidade

# Letras com acento (Latin-1) para aceitar José, João, André, Conceição etc.
_MAIUSC = "A-ZÀ-ÖØ-Þ"
_MINUSC = "a-zß-öø-ÿ"
REGEX_NOME_HUMANO = re.compile(
    rf"^[{_MAIUSC}][{_MINUSC}]+(\s(?:[{_MAIUSC}][{_MINUSC}]+|de|da|do|das|dos|e))*\s[{_MAIUSC}][{_MINUSC}]+$"
)
REGEX_LOGIN_HUMANO = re.compile(r"^[a-z]{2,}\.[a-z]{2,}$")
REGEX_LOGIN_NAO_HUMANO = re.compile(r"^nhu\.[a-z]{2,10}\.[a-z0-9]{2,10}$")
REGEX_NOME_NAO_HUMANO = re.compile(r"^[a-z0-9]{5,}$")
LIMITE_SAMACCOUNTNAME = 20  # limite do AD


# =============================================================================
# Criar
# =============================================================================

class _NovaIdentidade(BaseModel):
    ramo: Ramo
    unidade: str = Field(..., json_schema_extra={"example": "FAZENDA"},
                         description="Nome da unidade, que já deve existir.")

    @field_validator("unidade")
    @classmethod
    def _unidade(cls, v: str) -> str:
        return normalizar_nome_unidade(v)


class HumanoCreate(_NovaIdentidade):
    """Cria um humano em Inoperantes, bloqueado e sem senha."""
    categoria: Optional[Categoria] = Field(
        None, description="Obrigatória e aceita somente quando ramo = direta.")
    login: str = Field(..., json_schema_extra={"example": "joao.silva"})
    nome_completo: str = Field(..., json_schema_extra={"example": "Joao Silva"})
    cpf: Optional[str] = Field(None, description="Campo comum; a validação é do front-end.")

    @field_validator("login")
    @classmethod
    def _login(cls, v: str) -> str:
        v = v.strip()
        if not REGEX_LOGIN_HUMANO.match(v) or len(v) > LIMITE_SAMACCOUNTNAME:
            raise ValueError(
                "login deve ser nome.sobrenome em minúsculas, sem acento, com no máximo 20 caracteres")
        return v

    @field_validator("nome_completo")
    @classmethod
    def _nome(cls, v: str) -> str:
        v = unicodedata.normalize("NFC", v.strip())
        if len(v) < 5 or not REGEX_NOME_HUMANO.match(v):
            raise ValueError("nome_completo deve ter ao menos dois nomes, cada um iniciado por maiúscula")
        return v

    @model_validator(mode="after")
    def _categoria(self):
        if self.ramo is Ramo.DIRETA and self.categoria is None:
            raise ValueError("categoria é obrigatória quando ramo = direta")
        if self.ramo is not Ramo.DIRETA and self.categoria is not None:
            raise ValueError("categoria só existe em unidades da Direta")
        return self


class NaoHumanoCreate(_NovaIdentidade):
    """Cria uma conta não humana em Inoperantes, bloqueada e sem senha."""
    login: str = Field(..., json_schema_extra={"example": "nhu.sistema.contas"})
    nome: str = Field(..., json_schema_extra={"example": "sistemacontas"})
    pml_nao_humano_tipo: str = Field(..., description="Um dos tipos do arquivo de regras.")

    @field_validator("login")
    @classmethod
    def _login(cls, v: str) -> str:
        v = v.strip()
        if not REGEX_LOGIN_NAO_HUMANO.match(v) or len(v) > LIMITE_SAMACCOUNTNAME:
            raise ValueError("login deve seguir nhu.<categoria>.<nome>, minúsculo, com no máximo 20 caracteres")
        return v

    @field_validator("nome")
    @classmethod
    def _nome(cls, v: str) -> str:
        v = v.strip()
        if not REGEX_NOME_NAO_HUMANO.match(v):
            raise ValueError("nome deve ter ao menos 5 caracteres, só minúsculas e números")
        return v


# =============================================================================
# Transferir e ativar: ato com instrumento e destino
# =============================================================================

class _Destino(AtoUnidade):
    """
    Destino (ramo e unidade) de um ato sobre uma identidade. Em transferir é obrigatório;
    em ativar é opcional (sem destino, a conta volta ao mesmo lugar em Operativos).
    """
    DESTINO_OBRIGATORIO: ClassVar[bool] = False

    ramo_destino: Optional[Ramo] = None
    unidade_destino: Optional[str] = Field(None, json_schema_extra={"example": "EDUCACAO"})

    @field_validator("unidade_destino")
    @classmethod
    def _unidade_destino(cls, v: Optional[str]) -> Optional[str]:
        return normalizar_nome_unidade(v) if v is not None else None

    @model_validator(mode="after")
    def _destino_completo(self):
        if (self.ramo_destino is None) != (self.unidade_destino is None):
            raise ValueError("ramo_destino e unidade_destino devem ser informados juntos")
        if self.DESTINO_OBRIGATORIO and self.ramo_destino is None:
            raise ValueError("ramo_destino e unidade_destino são obrigatórios")
        return self


class _DestinoHumano(_Destino):
    """Ao entrar na Direta, `categoria_destino` é obrigatória; fora dela, é recusada."""
    categoria_destino: Optional[Categoria] = None

    @model_validator(mode="after")
    def _categoria(self):
        if self.ramo_destino is None:
            if self.categoria_destino is not None:
                raise ValueError("categoria_destino só pode ser informada junto com o destino")
        elif self.ramo_destino is Ramo.DIRETA and self.categoria_destino is None:
            raise ValueError("categoria_destino é obrigatória quando ramo_destino = direta")
        elif self.ramo_destino is not Ramo.DIRETA and self.categoria_destino is not None:
            raise ValueError("categoria_destino só existe em unidades da Direta")
        return self


class TransferirHumano(_DestinoHumano):
    DESTINO_OBRIGATORIO: ClassVar[bool] = True


class TransferirNaoHumano(_Destino):
    """A conta não humana vai sempre para a unidade de destino no lado NaoHumanos."""
    DESTINO_OBRIGATORIO: ClassVar[bool] = True


class _GeraSenha(BaseModel):
    """Operações que geram senha: o tamanho é escolha da chamada."""
    tamanho_senha: int = Field(
        TAMANHO_SENHA_PADRAO, ge=TAMANHO_SENHA_MIN, le=TAMANHO_SENHA_MAX,
        description="Tamanho da senha gerada pela API. A política de comprimento do domínio pode exigir mais.")


class AtivarHumano(_DestinoHumano, _GeraSenha):
    pass


class AtivarNaoHumano(_Destino, _GeraSenha):
    """A conta não humana vai sempre para a unidade de destino no lado NaoHumanos."""


class RedefinirSenha(_GeraSenha):
    """Nova senha gerada para uma conta em Operativos."""
    motivo: str = Field(..., min_length=3, max_length=200)


# =============================================================================
# Respostas
# =============================================================================

class IdentidadeOut(BaseModel):
    login: str
    nome: str
    tipo: TipoIdentidade
    ramo: Ramo
    unidade: str
    categoria: Optional[Categoria] = None  # só na Direta, para humanos
    arvore: Arvore
    bloqueada: bool
    distinguished_name: str
    atributos_pml: dict[str, str] = {}
    avisos: list[str] = []         # ex.: pml* não gravados (PML_GRAVAR=false)


class AtivacaoOut(IdentidadeOut):
    """Resultado da ativação. A senha inicial é devolvida UMA ÚNICA VEZ (nunca é registrada)."""
    senha_inicial: str


class SenhaRedefinidaOut(IdentidadeOut):
    """Resultado da redefinição. A nova senha é devolvida UMA ÚNICA VEZ (nunca é registrada)."""
    senha_nova: str


class IdentidadeListOut(BaseModel):
    total: int
    limite: int
    deslocamento: int
    items: list[IdentidadeOut]
