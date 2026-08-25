from ldap3 import MODIFY_REPLACE, SUBTREE
from ldap3.core.exceptions import LDAPException
from fastapi import HTTPException
from typing import Optional

from app.core.config import settings
from app.core.ldap_connection import get_connection
from app.core.generators import gerar_login, gerar_senha
from app.schemas.user import UsuarioCreate, UsuarioUpdate, UsuarioOut, UsuarioCriadoOut

# Flags do atributo userAccountControl no Active Directory
# 512 = conta habilitada | 514 = conta desabilitada (bit 2 = 2)
UAC_NORMAL_ATIVO = 512
UAC_NORMAL_DESABILITADA = 514


def _entry_to_usuario_out(entry) -> UsuarioOut:
    """
    Converte um registro do LDAP para o schema de saída da API.

    Args:
        entry: Entrada retornada pela consulta LDAP.

    Returns:
        UsuarioOut: Dados formatados no padrão da API.
    """
    uac = int(entry.userAccountControl.value) if entry.userAccountControl.value else UAC_NORMAL_ATIVO
    ativo = not (uac & 2)  # Bit 2 = conta desabilitada
    return UsuarioOut(
        login=str(entry.sAMAccountName.value),
        nome_completo=str(entry.cn.value),
        email=str(entry.mail.value) if entry.mail.value else None,
        cargo=str(entry.title.value) if entry.title.value else None,
        ativo=ativo,
        distinguished_name=str(entry.entry_dn),
    )


def _resolver_dn(login: str) -> str:
    """
    Busca o Distinguished Name completo a partir do login (sAMAccountName).

    Args:
        login (str): Nome de usuário no AD.

    Returns:
        str: DN completo do usuário.

    Raises:
        HTTPException: Se o usuário não for encontrado (404).
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=f"(sAMAccountName={login})",
            search_scope=SUBTREE,
        )
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Usuário não encontrado no AD")
        return conn.entries[0].entry_dn
    finally:
        conn.unbind()


def listar_usuarios(filtro_nome: str | None = None):
    """
    Retorna lista de todos os usuários do Active Directory.

    Args:
        filtro_nome (str | None): Filtro opcional por parte do nome (CN).

    Returns:
        list[UsuarioOut]: Lista de usuários formatados.
    """
    conn = get_connection()
    try:
        ldap_filter = "(&(objectClass=user)(objectCategory=person)"
        if filtro_nome:
            ldap_filter += f"(cn=*{filtro_nome}*)"
        ldap_filter += ")"

        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=ldap_filter,
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "title", "userAccountControl"],
        )
        return [_entry_to_usuario_out(e) for e in conn.entries]
    finally:
        conn.unbind()


def buscar_usuario(login: str) -> UsuarioOut:
    """
    Busca um usuário específico no AD pelo login.

    Args:
        login (str): Nome de usuário.

    Returns:
        UsuarioOut: Dados do usuário.

    Raises:
        HTTPException: Se o usuário não for encontrado (404).
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=f"(&(objectClass=user)(sAMAccountName={login}))",
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "title", "userAccountControl"],
        )
        if not conn.entries:
            raise HTTPException(status_code=404, detail="Usuário não encontrado no AD")
        return _entry_to_usuario_out(conn.entries[0])
    finally:
        conn.unbind()


def criar_usuario(dados: UsuarioCreate, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioCriadoOut:
    """
    Cria um novo usuário no Active Directory com login e senha gerados automaticamente.

    O fluxo é:
        1. Gera login no formato 'primeiro.ultimo'
        2. Gera senha aleatória de 8 caracteres
        3. Verifica se o login já existe no AD
        4. Cria o usuário com atributos básicos
        5. Define a senha e ativa a conta
        6. Registra a ação no banco de auditoria

    Args:
        dados (UsuarioCreate): Dados do usuário (nome, cargo, etc.)
        ip_address (str, optional): IP da origem da requisição.
        user_agent (str, optional): User-Agent do navegador.
        operator (str): Identificação de quem executou a ação.

    Returns:
        UsuarioCriadoOut: Dados do usuário criado + senha gerada.

    Raises:
        HTTPException: Se login já existir (409) ou erro no AD (500).
    """
    login = gerar_login(dados.primeiro_nome, dados.ultimo_nome)
    senha = gerar_senha(8)
    nome_completo = f"{dados.primeiro_nome} {dados.ultimo_nome}"
    email = dados.email or f"{login}@{settings.AD_DOMAIN}"
    dn = f"CN={nome_completo},{settings.AD_USER_OU}"

    conn = get_connection()
    try:
        # 1. Verifica se o login já existe no AD
        conn.search(
            search_base=settings.AD_BASE_DN,
            search_filter=f"(sAMAccountName={login})",
            search_scope=SUBTREE,
        )
        if conn.entries:
            raise HTTPException(status_code=409, detail=f"Login '{login}' já existe no AD")

        # 2. Prepara os atributos do novo usuário
        attrs = {
            "objectClass": ["top", "person", "organizationalPerson", "user"],
            "cn": nome_completo,
            "sAMAccountName": login,
            "userPrincipalName": f"{login}@{settings.AD_DOMAIN}",
            "givenName": dados.primeiro_nome,
            "sn": dados.ultimo_nome,
            "mail": email,
            "displayName": nome_completo,
            "userAccountControl": UAC_NORMAL_DESABILITADA,  # Começa desabilitado
        }
        if dados.cargo:
            attrs["title"] = dados.cargo

        ok = conn.add(dn, attributes=attrs)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao criar usuário: {conn.result}")

        # 3. Define a senha
        conn.extend.microsoft.modify_password(dn, senha)

        # 4. Ativa a conta
        conn.modify(dn, {"userAccountControl": [(MODIFY_REPLACE, [UAC_NORMAL_ATIVO])]})

        usuario = buscar_usuario(login)

        # 5. Registra a ação no banco de auditoria
        try:
            from app.audit_service import AuditService
            from app.database import SessionLocal
            db = SessionLocal()
            audit = AuditService(db)
            audit.log_activity(
                username=operator,
                action="CREATE_USER",
                target_user=login,
                details={
                    "nome_completo": nome_completo,
                    "email": email,
                    "cargo": dados.cargo
                },
                ip_address=ip_address,
                user_agent=user_agent,
                status="SUCCESS"
            )
            db.close()
        except Exception as e:
            # Não interrompe o fluxo se falhar o registro do log
            print(f"Erro ao registrar auditoria: {e}")

        return UsuarioCriadoOut(**usuario.model_dump(), senha_gerada=senha)

    except LDAPException as e:
        raise HTTPException(status_code=500, detail=f"Erro LDAP ao criar usuário: {e}")
    finally:
        conn.unbind()


def atualizar_usuario(login: str, dados: UsuarioUpdate, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioOut:
    """
    Atualiza dados de um usuário existente no AD (cargo, email, telefone).

    Args:
        login (str): Login do usuário a ser atualizado.
        dados (UsuarioUpdate): Campos a serem alterados.
        ip_address (str, optional): IP da origem.
        user_agent (str, optional): User-Agent.
        operator (str): Quem executou a ação.

    Returns:
        UsuarioOut: Dados atualizados do usuário.

    Raises:
        HTTPException: Se o usuário não for encontrado ou erro no AD.
    """
    dn_usuario = _resolver_dn(login)
    mudancas = {}

    # Monta apenas os campos que foram enviados
    if dados.cargo is not None:
        mudancas["title"] = [(MODIFY_REPLACE, [dados.cargo])]
    if dados.email is not None:
        mudancas["mail"] = [(MODIFY_REPLACE, [dados.email])]
    if dados.telefone is not None:
        mudancas["telephoneNumber"] = [(MODIFY_REPLACE, [dados.telefone])]

    if not mudancas:
        return buscar_usuario(login)

    conn = get_connection()
    try:
        ok = conn.modify(dn_usuario, mudancas)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao atualizar usuário: {conn.result}")

        usuario = buscar_usuario(login)

        # Registra a ação
        try:
            from app.audit_service import AuditService
            from app.database import SessionLocal
            db = SessionLocal()
            audit = AuditService(db)
            audit.log_activity(
                username=operator,
                action="UPDATE_USER",
                target_user=login,
                details={"campos_alterados": dados.model_dump(exclude_unset=True)},
                ip_address=ip_address,
                user_agent=user_agent,
                status="SUCCESS"
            )
            db.close()
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")

        return usuario
    finally:
        conn.unbind()


def remover_usuario(login: str, ip_address: str = None, user_agent: str = None, operator: str = "system") -> None:
    """
    Remove um usuário do Active Directory.

    Args:
        login (str): Login do usuário a ser removido.
        ip_address (str, optional): IP da origem.
        user_agent (str, optional): User-Agent.
        operator (str): Quem executou a ação.

    Raises:
        HTTPException: Se o usuário não for encontrado ou erro no AD.
    """
    dn_usuario = _resolver_dn(login)
    conn = get_connection()
    try:
        ok = conn.delete(dn_usuario)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao remover usuário: {conn.result}")

        # Registra a ação
        try:
            from app.audit_service import AuditService
            from app.database import SessionLocal
            db = SessionLocal()
            audit = AuditService(db)
            audit.log_activity(
                username=operator,
                action="DELETE_USER",
                target_user=login,
                details={"usuario_removido": login},
                ip_address=ip_address,
                user_agent=user_agent,
                status="SUCCESS"
            )
            db.close()
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")

    finally:
        conn.unbind()


def trocar_senha(login: str, nova_senha: str | None, ip_address: str = None, user_agent: str = None, operator: str = "system") -> str:
    """
    Troca a senha de um usuário no AD. Se não for fornecida, gera uma automática.

    Args:
        login (str): Login do usuário.
        nova_senha (str | None): Nova senha (opcional).
        ip_address (str, optional): IP da origem.
        user_agent (str, optional): User-Agent.
        operator (str): Quem executou a ação.

    Returns:
        str: A nova senha (gerada ou fornecida).

    Raises:
        HTTPException: Se o usuário não for encontrado ou erro no AD.
    """
    dn_usuario = _resolver_dn(login)
    senha = nova_senha or gerar_senha(8)

    conn = get_connection()
    try:
        ok = conn.extend.microsoft.modify_password(dn_usuario, senha)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao trocar senha: {conn.result}")

        # Registra a ação
        try:
            from app.audit_service import AuditService
            from app.database import SessionLocal
            db = SessionLocal()
            audit = AuditService(db)
            audit.log_activity(
                username=operator,
                action="CHANGE_PASSWORD",
                target_user=login,
                details={"senha_gerada": senha if nova_senha is None else "Senha fornecida pelo usuário"},
                ip_address=ip_address,
                user_agent=user_agent,
                status="SUCCESS"
            )
            db.close()
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")

        return senha
    finally:
        conn.unbind()


def desabilitar_usuario(login: str, desabilitar: bool = True, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioOut:
    """
    Habilita ou desabilita a conta de um usuário no AD.

    Args:
        login (str): Login do usuário.
        desabilitar (bool): True = desabilitar, False = habilitar.
        ip_address (str, optional): IP da origem.
        user_agent (str, optional): User-Agent.
        operator (str): Quem executou a ação.

    Returns:
        UsuarioOut: Dados atualizados do usuário.

    Raises:
        HTTPException: Se o usuário não for encontrado ou erro no AD.
    """
    dn_usuario = _resolver_dn(login)
    novo_uac = UAC_NORMAL_DESABILITADA if desabilitar else UAC_NORMAL_ATIVO
    acao = "DISABLE_USER" if desabilitar else "ENABLE_USER"

    conn = get_connection()
    try:
        ok = conn.modify(dn_usuario, {"userAccountControl": [(MODIFY_REPLACE, [novo_uac])]})
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao alterar status da conta: {conn.result}")

        usuario = buscar_usuario(login)

        # Registra a ação
        try:
            from app.audit_service import AuditService
            from app.database import SessionLocal
            db = SessionLocal()
            audit = AuditService(db)
            audit.log_activity(
                username=operator,
                action=acao,
                target_user=login,
                details={"status": "desabilitado" if desabilitar else "habilitado"},
                ip_address=ip_address,
                user_agent=user_agent,
                status="SUCCESS"
            )
            db.close()
        except Exception as e:
            print(f"Erro ao registrar auditoria: {e}")

        return usuario
    finally:
        conn.unbind()


def autenticar_usuario(login: str, senha: str, ip_address: str = None, user_agent: str = None) -> bool:
    """
    Autentica um usuário no Active Directory e registra a tentativa de login.

    Args:
        login (str): Nome de usuário.
        senha (str): Senha do usuário.
        ip_address (str, optional): IP da origem.
        user_agent (str, optional): User-Agent.

    Returns:
        bool: True se autenticado com sucesso, False caso contrário.
    """
    try:
        dn_usuario = _resolver_dn(login)
        conn = get_connection()
        try:
            # Tenta bind com as credenciais do usuário
            test_conn = get_connection(user=dn_usuario, password=senha)
            test_conn.unbind()

            # Registra login bem-sucedido
            try:
                from app.audit_service import AuditService
                from app.database import SessionLocal
                db = SessionLocal()
                audit = AuditService(db)
                audit.log_login(
                    username=login,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                db.close()
            except Exception as e:
                print(f"Erro ao registrar login: {e}")

            return True

        except Exception as e:
            # Registra falha de login
            try:
                from app.audit_service import AuditService
                from app.database import SessionLocal
                db = SessionLocal()
                audit = AuditService(db)
                audit.log_login(
                    username=login,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    error_message=str(e)
                )
                db.close()
            except Exception as e2:
                print(f"Erro ao registrar falha de login: {e2}")
            return False
        finally:
            conn.unbind()
    except HTTPException:
        return False


def registrar_logout(login: str, ip_address: str = None, user_agent: str = None) -> None:
    """
    Registra o logout de um usuário no banco de auditoria.

    Args:
        login (str): Nome de usuário.
        ip_address (str, optional): IP da origem.
        user_agent (str, optional): User-Agent.
    """
    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_logout(
            username=login,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.close()
    except Exception as e:
        print(f"Erro ao registrar logout: {e}")