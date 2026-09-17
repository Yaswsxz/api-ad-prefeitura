from datetime import timedelta
from fastapi import APIRouter, Query, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.user import UsuarioUpdate, UsuarioOut, TrocaSenha, CampoOrdenacao, Ordem
from app.services import ad_service
from app.database import get_db
from app.core.auth import criar_token_acesso, get_current_user
from app.core.config import settings

# Rotas públicas: não exigem token, pois são o próprio ponto de entrada
# para se autenticar e obter um.
public_router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# Rotas protegidas: qualquer chamada exige um token JWT válido no header
# Authorization: Bearer <token>. Sem token válido, a API responde 401
# antes mesmo de a função da rota ser executada.
router = APIRouter(prefix="/usuarios", tags=["Usuários"], dependencies=[Depends(get_current_user)])


@public_router.post("/login", summary="Login e geração de token JWT")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica um usuário no Active Directory usando login e senha,
    e retorna um token JWT para uso nos demais endpoints (protegidos).
    Envie o token no header: Authorization: Bearer <access_token>
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    success = ad_service.autenticar_usuario(
        form_data.username,
        form_data.password,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    if not success:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token_acesso(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@public_router.post("/auth", summary="Autenticar usuário no AD (sem gerar token)")
def autenticar_usuario(
    request: Request,
    login: str,
    senha: str,
    db: Session = Depends(get_db)
):
    """
    Verifica se um login/senha são válidos no AD, sem gerar token.
    Para obter um token de acesso, use POST /usuarios/login.
    """
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
        raise HTTPException(status_code=401, detail="Credenciais inválidas")


@router.get("/cargos", summary="Listar cargos já cadastrados no AD")
def get_cargos():
    """
    Retorna a lista de cargos distintos já usados por usuários existentes
    no AD, sem duplicatas. Útil para popular um dropdown ao criar ou
    atualizar um usuário, evitando variações de digitação.
    """
    return {"cargos": ad_service.listar_cargos()}


@router.get("/candidatos-teste", summary="Identificar possíveis contas de teste no AD")
def get_candidatos_teste():
    """
    Sinaliza contas que aparentam ser de teste (email placeholder 'string',
    nome/login contendo 'teste'/'test'). NÃO remove nada — apenas lista
    candidatos para você revisar antes de decidir o que apagar.
    """
    return {"candidatos": ad_service.identificar_candidatos_teste()}


@router.get("", response_model=List[UsuarioOut], summary="Listar/buscar usuários com filtros")
def listar_usuarios(
    request: Request,
    nome: Optional[str] = Query(None, description="Filtra por parte do nome"),
    cargo: Optional[str] = Query(None, description="Filtra por parte do cargo (ex: Analista)"),
    email: Optional[str] = Query(None, description="Filtra por parte do email"),
    ativo: Optional[bool] = Query(None, description="Filtra por status: true=ativos, false=inativos"),
    ordenar_por: CampoOrdenacao = Query(CampoOrdenacao.NOME, description="Campo para ordenação"),
    ordem: Ordem = Query(Ordem.ASC, description="Direção da ordenação")
):
    return ad_service.listar_usuarios(
        filtro_nome=nome,
        filtro_cargo=cargo,
        filtro_email=email,
        filtro_ativo=ativo,
        ordenar_por=ordenar_por.value,
        ordem=ordem.value
    )


@router.get("/{login}", response_model=UsuarioOut, summary="Consultar um usuário pelo login")
def buscar_usuario(
    request: Request,
    login: str,
):
    """
    Retorna os dados de um único usuário do AD a partir do login (sAMAccountName).
    """
    return ad_service.buscar_usuario(login)


@router.put("/{login}", response_model=UsuarioOut, summary="Atualizar dados de um usuário")
def atualizar_usuario(
    request: Request,
    login: str,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.atualizar_usuario(
        login,
        dados,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


@router.post("/{login}/trocar-senha", summary="Trocar a senha de um usuário")
def trocar_senha(
    request: Request,
    login: str,
    dados: TrocaSenha,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    senha = ad_service.trocar_senha(
        login,
        dados.nova_senha,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )
    return {"login": login, "nova_senha": senha}


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
