from pydantic import BaseModel, Field
from typing import Optional


class UsuarioCreate(BaseModel):
    primeiro_nome: str = Field(..., example="Joao")
    ultimo_nome: str = Field(..., example="Silva")
    cpf: Optional[str] = Field(None, example="12345678900")
    cargo: Optional[str] = Field(None, example="Analista Administrativo")
    tipo: Optional[str] = Field("efetivo", example="efetivo ou estagiario")
    email: Optional[str] = None  # se não informado, é gerado automaticamente


class UsuarioUpdate(BaseModel):
    cargo: Optional[str] = None
    tipo: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None


class TrocaSenha(BaseModel):
    nova_senha: Optional[str] = Field(
        None, description="Se não informada, uma senha aleatória é gerada"
    )
    forcar_troca_no_proximo_login: bool = True


class UsuarioOut(BaseModel):
    login: str
    nome_completo: str
    email: Optional[str] = None
    cargo: Optional[str] = None
    ativo: bool
    distinguished_name: str


class UsuarioCriadoOut(UsuarioOut):
    senha_gerada: str
