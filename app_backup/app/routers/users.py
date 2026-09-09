from fastapi import APIRouter, Query, Request, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.user import UsuarioCreate, UsuarioUpdate, UsuarioOut, UsuarioCriadoOut, TrocaSenha
from app.services import ad_service
from app.database import get_db

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("", response_model=List[UsuarioOut], summary="Listar/buscar usuários")
def listar_usuarios(
    request: Request,
    nome: Optional[str] = Query(None, description="Filtra por parte do nome")
):
    return ad_service.listar_usuarios(filtro_nome=nome)


@router.get("/{login}", response_model=UsuarioOut, summary="Consultar um usuário pelo login")
def buscar_usuario(request: Request, login: str):
    return ad_service.buscar_usuario(login)


@router.post("", response_model=UsuarioCriadoOut, status_code=201, summary="Criar novo usuário")
def criar_usuario(
    request: Request,
    dados: UsuarioCreate,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    operator = dados.primeiro_nome  # ou use um usuário autenticado via JWT
    
    return ad_service.criar_usuario(
        dados,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=operator
    )


@router.put("/{login}", response_model=UsuarioOut, summary="Atualizar dados de um usuário")
def atualizar_usuario(
    request: Request,
    login: str,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    operator = "system"  # Substituir por usuário autenticado via JWT
    
    return ad_service.atualizar_usuario(
        login,
        dados,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=operator
    )


@router.delete("/{login}", status_code=204, summary="Remover usuário do AD")
def remover_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    operator = "system"  # Substituir por usuário autenticado via JWT
    
    ad_service.remover_usuario(
        login,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=operator
    )
    return None


@router.post("/{login}/trocar-senha", summary="Trocar a senha de um usuário")
def trocar_senha(
    request: Request,
    login: str,
    dados: TrocaSenha,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    operator = login  # O próprio usuário está trocando a senha
    
    senha = ad_service.trocar_senha(
        login,
        dados.nova_senha,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=operator
    )
    return {"login": login, "nova_senha": senha}


@router.post("/{login}/desabilitar", response_model=UsuarioOut, summary="Desabilitar conta de usuário")
def desabilitar_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    operator = "system"  # Substituir por usuário autenticado via JWT
    
    return ad_service.desabilitar_usuario(
        login,
        desabilitar=True,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=operator
    )


@router.post("/{login}/habilitar", response_model=UsuarioOut, summary="Reabilitar conta de usuário")
def habilitar_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    operator = "system"  # Substituir por usuário autenticado via JWT
    
    return ad_service.desabilitar_usuario(
        login,
        desabilitar=False,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=operator
    )


# 🔐 NOVO: Endpoint de autenticação
@router.post("/auth", summary="Autenticar usuário no AD")
def autenticar_usuario(
    request: Request,
    login: str,
    senha: str,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    success = ad_service.autenticar_usuario(
        login,
        senha,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if success:
        return {"message": "Autenticado com sucesso", "success": True}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Credenciais inválidas")


# 🔐 NOVO: Endpoint de logout
@router.post("/{login}/logout", summary="Registrar logout do usuário")
def logout_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    ad_service.registrar_logout(
        login,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return {"message": f"Logout registrado para {login}"}

from pydantic import BaseModel, Field
from typing import Optional


class UsuarioCreate(BaseModel):
    primeiro_nome: str = Field(..., example="Joao")
    ultimo_nome: str = Field(..., example="Silva")
    cpf: Optional[str] = Field(None, example="12345678900")
    cargo: Optional[str] = Field(None, example="Analista Administrativo")
    tipo: Optional[str] = Field("efetivo", example="efetivo ou estagiario")
    email: Optional[str] = None


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


# 🔐 NOVOS SCHEMAS PARA AUDITORIA
class LoginHistoryResponse(BaseModel):
    id: int
    username: str
    event_type: str  # 'login' ou 'logout'
    timestamp: str
    ip_address: Optional[str]
    success: bool
    error_message: Optional[str]


class ActivityHistoryResponse(BaseModel):
    id: int
    username: str
    action: str
    target_user: Optional[str]
    details: Optional[str]
    timestamp: str
    ip_address: Optional[str]
    status: str