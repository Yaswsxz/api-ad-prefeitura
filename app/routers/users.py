from datetime import timedelta
from fastapi import APIRouter, Query, Request, Depends, Body, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.user import UsuarioCreate, UsuarioUpdate, UsuarioOut, UsuarioCriadoOut, TrocaSenha
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


@router.get("/setores", summary="Listar setores válidos (subcontainers) dentro de Ativos")
def get_setores():
    """
    Retorna a lista de setores reais existentes no AD (ex: CODEL, CMTU, Planejamento...).
    Use este endpoint para saber quais valores são aceitos no campo 'subcontainer'
    ao criar ou transferir um usuário.
    """
    return {"setores": ad_service.listar_setores()}


@router.get("/inconsistencias", summary="Detectar usuários com status divergente da pasta onde estão")
def get_inconsistencias():
    """
    Lista usuários onde o status real da conta (habilitada/desabilitada)
    não bate com a pasta (Ativos/Inativos) onde estão guardados no AD.
    """
    return {"inconsistencias": ad_service.detectar_inconsistencias()}


@router.post("/inconsistencias/corrigir", summary="Corrigir automaticamente usuários com status divergente")
def corrigir_inconsistencias_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    """
    Move automaticamente cada usuário inconsistente para a pasta certa
    (Ativos ou Inativos), de acordo com o status real da conta.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.corrigir_inconsistencias(
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


@router.get("/candidatos-teste", summary="Identificar possíveis contas de teste no AD")
def get_candidatos_teste():
    """
    Sinaliza contas que aparentam ser de teste (email placeholder 'string',
    nome/login contendo 'teste'/'test'). NÃO remove nada — apenas lista
    candidatos para você revisar antes de decidir o que apagar.
    """
    return {"candidatos": ad_service.identificar_candidatos_teste()}


@router.post("/deletar-lote", summary="Remover uma lista específica de usuários")
def deletar_lote(
    request: Request,
    logins: List[str] = Body(..., embed=True, description="Lista de logins a remover, revisada manualmente"),
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    """
    Remove os usuários cujos logins forem informados explicitamente.
    Use GET /usuarios/candidatos-teste para identificar candidatos,
    revise a lista, e só então chame este endpoint com os logins escolhidos.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.deletar_usuarios_em_lote(
        logins,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


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
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.criar_usuario(
        dados,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


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


@router.delete("/{login}", status_code=204, summary="Remover usuário do AD")
def remover_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    ad_service.remover_usuario(
        login,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )
    return None


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


@router.post("/{login}/desabilitar", response_model=UsuarioOut, summary="Desabilitar conta de usuário")
def desabilitar_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.desabilitar_usuario(
        login,
        desabilitar=True,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


@router.post("/{login}/habilitar", response_model=UsuarioOut, summary="Reabilitar conta de usuário")
def habilitar_usuario(
    request: Request,
    login: str,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.desabilitar_usuario(
        login,
        desabilitar=False,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


@router.post("/{login}/transferir-setor", response_model=UsuarioOut, summary="Transferir usuário para outro setor")
def transferir_setor(
    request: Request,
    login: str,
    novo_subcontainer: str,
    db: Session = Depends(get_db),
    usuario_atual: str = Depends(get_current_user),
):
    """
    Move o usuário para outro subcontainer (setor), mantendo o mesmo status
    (Ativos permanece Ativos, Inativos permanece Inativos).
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return ad_service.transferir_usuario_setor(
        login,
        novo_subcontainer,
        ip_address=client_ip,
        user_agent=user_agent,
        operator=usuario_atual
    )


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