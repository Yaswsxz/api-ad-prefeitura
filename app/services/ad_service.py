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
    """
    uac = int(entry.userAccountControl.value) if entry.userAccountControl.value else UAC_NORMAL_ATIVO
    ativo = not (uac & 2)
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
    O usuário é criado na OU de ATIVOS (padrão).
    """
    login = gerar_login(dados.primeiro_nome, dados.ultimo_nome)
    senha = gerar_senha(8)
    nome_completo = f"{dados.primeiro_nome} {dados.ultimo_nome}"
    email = dados.email or f"{login}@{settings.AD_DOMAIN}"
    base_path = f"CN={dados.subcontainer},{settings.AD_ATIVOS_BASE}"
    dn = f"CN={nome_completo},{base_path}"

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
            "userAccountControl": UAC_NORMAL_DESABILITADA,
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
            print(f"Erro ao registrar auditoria: {e}")

        return UsuarioCriadoOut(**usuario.model_dump(), senha_gerada=senha)

    except LDAPException as e:
        raise HTTPException(status_code=500, detail=f"Erro LDAP ao criar usuário: {e}")
    finally:
        conn.unbind()


def atualizar_usuario(login: str, dados: UsuarioUpdate, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioOut:
    """
    Atualiza dados de um usuário existente no AD (cargo, email, telefone).
    """
    dn_usuario = _resolver_dn(login)
    mudancas = {}

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
    """
    dn_usuario = _resolver_dn(login)
    conn = get_connection()
    try:
        ok = conn.delete(dn_usuario)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao remover usuário: {conn.result}")

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
    """
    dn_usuario = _resolver_dn(login)
    senha = nova_senha or gerar_senha(8)

    conn = get_connection()
    try:
        ok = conn.extend.microsoft.modify_password(dn_usuario, senha)
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao trocar senha: {conn.result}")

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


def mover_usuario(login: str, nova_ou: str) -> bool:
    """
    Move um usuário para uma nova OU (Organizational Unit).

    Args:
        login (str): Login do usuário.
        nova_ou (str): Caminho completo da OU de destino.
                       Ex: "OU=Inativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"

    Returns:
        bool: True se movido com sucesso, False caso contrário.
    """
    try:
        dn_atual = _resolver_dn(login)
        usuario = buscar_usuario(login)
        nome_completo = usuario.nome_completo
        novo_dn = f"CN={nome_completo},{nova_ou}"

        conn = get_connection()
        try:
            conn.modify_dn(dn_atual, novo_dn)
            if conn.result['result'] == 0:
                return True
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao mover usuário: {conn.result}"
                )
        finally:
            conn.unbind()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao mover usuário: {e}")


def desabilitar_usuario(login: str, desabilitar: bool = True, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioOut:
    """
    Habilita ou desabilita a conta de um usuário no AD.
    Ao desabilitar, move o usuário para OU=Inativos.
    Ao habilitar, move o usuário para OU=Ativos.
    """
    dn_usuario = _resolver_dn(login)
    novo_uac = UAC_NORMAL_DESABILITADA if desabilitar else UAC_NORMAL_ATIVO
    acao = "DISABLE_USER" if desabilitar else "ENABLE_USER"

    # Define a OU de destino
    if desabilitar:
        ou_destino = "OU=Inativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
    else:
        ou_destino = "OU=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"

    conn = get_connection()
    try:
        # 1. Altera o status da conta
        ok = conn.modify(dn_usuario, {"userAccountControl": [(MODIFY_REPLACE, [novo_uac])]})
        if not ok:
            raise HTTPException(status_code=500, detail=f"Falha ao alterar status da conta: {conn.result}")

        # 2. Move o usuário para a OU correta
        mover_usuario(login, ou_destino)

        # 3. Busca os dados atualizados
        usuario = buscar_usuario(login)

        # 4. Registra a ação no banco de auditoria
        try:
            from app.audit_service import AuditService
            from app.database import SessionLocal
            db = SessionLocal()
            audit = AuditService(db)
            audit.log_activity(
                username=operator,
                action=acao,
                target_user=login,
                details={
                    "status": "desabilitado" if desabilitar else "habilitado",
                    "ou_destino": ou_destino
                },
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
    """
    try:
        dn_usuario = _resolver_dn(login)
        conn = get_connection()
        try:
            test_conn = get_connection(user=dn_usuario, password=senha)
            test_conn.unbind()

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