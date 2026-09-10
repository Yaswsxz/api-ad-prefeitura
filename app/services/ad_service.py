from ldap3 import MODIFY_REPLACE, SUBTREE, LEVEL
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
        tipo=str(entry.description.value) if entry.description.value else None,
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


def _subcontainer_existe(subcontainer: str, base: str) -> bool:
    """
    Verifica se um subcontainer (ex: CODEL, CMTU) existe de verdade
    como filho direto de 'base' (Ativos ou Inativos) no AD.
    Consulta o AD em tempo real, sem depender de lista fixa no código —
    então funciona mesmo com setores novos criados depois.
    """
    conn = get_connection()
    try:
        conn.search(
            search_base=base,
            search_filter=f"(&(objectClass=container)(cn={subcontainer}))",
            search_scope=LEVEL,  # só filhos diretos, não desce a árvore inteira
        )
        return len(conn.entries) > 0
    finally:
        conn.unbind()


def listar_setores(base: Optional[str] = None) -> list[str]:
    """
    Lista todos os subcontainers (setores) existentes dentro de Ativos no AD.
    Útil para popular um dropdown no frontend ou validar valores antes de enviar.
    """
    base = base or settings.AD_ATIVOS_BASE
    conn = get_connection()
    try:
        conn.search(
            search_base=base,
            search_filter="(objectClass=container)",
            search_scope=LEVEL,
            attributes=["cn"],
        )
        return sorted(str(entry.cn.value) for entry in conn.entries)
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
            attributes=["cn", "sAMAccountName", "mail", "title", "description", "userAccountControl"],
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
            attributes=["cn", "sAMAccountName", "mail", "title", "description", "userAccountControl"],
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
    # Valida se o subcontainer informado existe de verdade no AD antes de tentar criar
    if not _subcontainer_existe(dados.subcontainer, settings.AD_ATIVOS_BASE):
        raise HTTPException(
            status_code=422,
            detail=f"Subcontainer '{dados.subcontainer}' não existe em Ativos no AD. "
                   f"Consulte GET /usuarios/setores para ver os valores válidos."
        )

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
        if dados.tipo:
            attrs["description"] = dados.tipo

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
                    "cargo": dados.cargo,
                    "cpf": dados.cpf,
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
    if dados.tipo is not None:
        mudancas["description"] = [(MODIFY_REPLACE, [dados.tipo])]
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
    Move um usuário para uma nova OU/container (Organizational Unit ou container).

    Args:
        login (str): Login do usuário.
        nova_ou (str): Caminho completo do NOVO PAI (destino) do usuário.
                       Ex: "CN=Inativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
                       ou "CN=Saude,CN=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"

    Returns:
        bool: True se movido com sucesso, False caso contrário.
    """
    try:
        dn_atual = _resolver_dn(login)
        usuario = buscar_usuario(login)
        nome_completo = usuario.nome_completo
        novo_rdn = f"CN={nome_completo}"  # modify_dn espera só o NOVO NOME aqui, não o caminho inteiro

        conn = get_connection()
        try:
            # new_superior é o parâmetro correto para mudar de "pasta" (pai) no AD.
            # Passar o caminho completo como segundo argumento (sem new_superior)
            # causa erro de namingViolation, pois o AD tenta interpretar tudo como um nome só.
            conn.modify_dn(dn_atual, novo_rdn, new_superior=nova_ou)
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


def transferir_usuario_setor(login: str, novo_subcontainer: str, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioOut:
    """
    Transfere um usuário para outro subcontainer (setor), mantendo o mesmo
    status (quem está em Ativos permanece em Ativos, quem está em Inativos
    permanece em Inativos). Usado quando um usuário muda de setor/departamento
    sem mudar seu status de ativo/inativo.
    """
    dn_atual = _resolver_dn(login)

    # Descobre se o usuário está em Ativos ou Inativos hoje, pelo DN atual
    if settings.AD_ATIVOS_BASE in dn_atual:
        base_destino = settings.AD_ATIVOS_BASE
    elif settings.AD_INATIVOS_BASE in dn_atual:
        base_destino = settings.AD_INATIVOS_BASE
    else:
        raise HTTPException(
            status_code=409,
            detail="Não foi possível identificar se o usuário está em Ativos ou Inativos."
        )

    # Valida se o setor de destino existe de verdade no AD
    if not _subcontainer_existe(novo_subcontainer, base_destino):
        raise HTTPException(
            status_code=422,
            detail=f"Subcontainer '{novo_subcontainer}' não existe. "
                   f"Consulte GET /usuarios/setores para ver os valores válidos."
        )

    novo_dn_base = f"CN={novo_subcontainer},{base_destino}"
    mover_usuario(login, novo_dn_base)

    usuario = buscar_usuario(login)

    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_activity(
            username=operator,
            action="TRANSFER_SETOR",
            target_user=login,
            details={"novo_setor": novo_subcontainer, "dn_anterior": dn_atual},
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS"
        )
        db.close()
    except Exception as e:
        print(f"Erro ao registrar auditoria: {e}")

    return usuario


def detectar_inconsistencias() -> list[dict]:
    """
    Varre todos os usuários dentro de Ativos e Inativos e detecta
    casos onde o status real da conta (userAccountControl) não bate
    com a "pasta" onde o usuário está fisicamente guardado no AD.
    """
    conn = get_connection()
    try:
        base = "OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
        conn.search(
            search_base=base,
            search_filter="(&(objectClass=user)(objectCategory=person))",
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "userAccountControl"],
        )

        inconsistencias = []
        for entry in conn.entries:
            dn = entry.entry_dn
            uac = int(entry.userAccountControl.value) if entry.userAccountControl.value else UAC_NORMAL_ATIVO
            conta_ativa = not (uac & 2)  # True = habilitada, False = desabilitada

            esta_em_ativos = "CN=Ativos" in dn
            esta_em_inativos = "CN=Inativos" in dn

            problema = None
            if conta_ativa and esta_em_inativos:
                problema = "Conta HABILITADA mas está na pasta Inativos"
            elif not conta_ativa and esta_em_ativos:
                problema = "Conta DESABILITADA mas está na pasta Ativos"

            if problema:
                inconsistencias.append({
                    "login": str(entry.sAMAccountName.value),
                    "nome": str(entry.cn.value),
                    "dn": dn,
                    "conta_ativa": conta_ativa,
                    "problema": problema,
                })

        return inconsistencias
    finally:
        conn.unbind()


def corrigir_inconsistencias(ip_address: str = None, user_agent: str = None, operator: str = "system") -> dict:
    """
    Detecta usuários com status divergente da pasta onde estão (Ativos/Inativos)
    e corrige automaticamente, movendo cada um para a pasta correta,
    de acordo com o status real da conta (userAccountControl).
    """
    problemas = detectar_inconsistencias()

    if not problemas:
        return {"corrigidos": 0, "erros": 0, "detalhes": []}

    detalhes = []
    corrigidos = 0
    erros = 0

    for item in problemas:
        login = item["login"]
        conta_ativa = item["conta_ativa"]

        # Extrai o subcontainer atual (o que vem logo antes de CN=Ativos/CN=Inativos)
        dn = item["dn"]
        partes = dn.split(",")
        subcontainer_atual = partes[1].replace("CN=", "")  # ex: "CODEL"

        # Decide a pasta correta com base no status real da conta
        base_correta = settings.AD_ATIVOS_BASE if conta_ativa else settings.AD_INATIVOS_BASE
        destino = f"CN={subcontainer_atual},{base_correta}"

        try:
            mover_usuario(login, destino)
            corrigidos += 1
            detalhes.append({
                "login": login,
                "acao": f"Movido para {'Ativos' if conta_ativa else 'Inativos'}/{subcontainer_atual}",
                "status": "SUCESSO"
            })
        except Exception as e:
            erros += 1
            detalhes.append({
                "login": login,
                "acao": "Falha ao mover",
                "status": f"ERRO: {e}"
            })

    # Registra a correção em lote na auditoria
    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_activity(
            username=operator,
            action="FIX_INCONSISTENCIAS",
            target_user="multiplos",
            details={"corrigidos": corrigidos, "erros": erros, "detalhes": detalhes},
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS" if erros == 0 else "PARTIAL"
        )
        db.close()
    except Exception as e:
        print(f"Erro ao registrar auditoria: {e}")

    return {"corrigidos": corrigidos, "erros": erros, "detalhes": detalhes}


def identificar_candidatos_teste() -> list[dict]:
    """
    Varre usuários do AD e sinaliza contas que aparentam ser de teste,
    com base em padrões comuns (email placeholder 'string', nome/login
    contendo 'teste'/'test'). NÃO deleta nada — apenas lista candidatos
    para revisão manual antes de qualquer remoção.
    """
    conn = get_connection()
    try:
        base = "OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
        conn.search(
            search_base=base,
            search_filter="(&(objectClass=user)(objectCategory=person))",
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "mail", "userAccountControl"],
        )

        candidatos = []
        for entry in conn.entries:
            cn = str(entry.cn.value) if entry.cn.value else ""
            login = str(entry.sAMAccountName.value) if entry.sAMAccountName.value else ""
            mail = str(entry.mail.value) if entry.mail.value else ""

            motivos = []
            if mail.strip().lower() == "string":
                motivos.append("email é o placeholder padrão 'string' do Swagger")
            if "teste" in cn.lower() or "teste" in login.lower():
                motivos.append("nome/login contém 'teste'")
            if "test" in cn.lower() or "test" in login.lower():
                motivos.append("nome/login contém 'test'")

            if motivos:
                candidatos.append({
                    "login": login,
                    "nome": cn,
                    "email": mail,
                    "motivos": motivos,
                })

        return candidatos
    finally:
        conn.unbind()


def deletar_usuarios_em_lote(logins: list[str], ip_address: str = None, user_agent: str = None, operator: str = "system") -> dict:
    """
    Remove uma lista específica de usuários do AD. Requer que os logins
    sejam informados explicitamente pelo chamador — nunca deleta com base
    em heurística automática. Garante que uma pessoa revisou e confirmou
    a lista antes de qualquer remoção acontecer de fato.
    """
    resultados = []
    sucesso = 0
    erros = 0

    for login in logins:
        try:
            remover_usuario(login, ip_address=ip_address, user_agent=user_agent, operator=operator)
            resultados.append({"login": login, "status": "REMOVIDO"})
            sucesso += 1
        except HTTPException as e:
            resultados.append({"login": login, "status": f"ERRO: {e.detail}"})
            erros += 1
        except Exception as e:
            resultados.append({"login": login, "status": f"ERRO: {e}"})
            erros += 1

    try:
        from app.audit_service import AuditService
        from app.database import SessionLocal
        db = SessionLocal()
        audit = AuditService(db)
        audit.log_activity(
            username=operator,
            action="DELETE_BATCH",
            target_user="multiplos",
            details={"logins": logins, "removidos": sucesso, "erros": erros, "detalhes": resultados},
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS" if erros == 0 else "PARTIAL"
        )
        db.close()
    except Exception as e:
        print(f"Erro ao registrar auditoria: {e}")

    return {"removidos": sucesso, "erros": erros, "detalhes": resultados}


def desabilitar_usuario(login: str, desabilitar: bool = True, ip_address: str = None, user_agent: str = None, operator: str = "system") -> UsuarioOut:
    """
    Habilita ou desabilita a conta de um usuário no AD.
    Ao desabilitar, move o usuário para dentro de Inativos, preservando
    o mesmo subcontainer (setor) em que ele já estava.
    Ao habilitar, faz o mesmo movimento de volta para Ativos.
    """
    dn_usuario = _resolver_dn(login)
    novo_uac = UAC_NORMAL_DESABILITADA if desabilitar else UAC_NORMAL_ATIVO
    acao = "DISABLE_USER" if desabilitar else "ENABLE_USER"

    # Descobre o subcontainer atual (ex: CODEL) a partir do DN do usuário,
    # para preservar o setor dele ao mover entre Ativos/Inativos.
    partes = dn_usuario.split(",")
    subcontainer_atual = partes[1].replace("CN=", "") if len(partes) > 1 else None

    base_destino = settings.AD_INATIVOS_BASE if desabilitar else settings.AD_ATIVOS_BASE
    if subcontainer_atual:
        ou_destino = f"CN={subcontainer_atual},{base_destino}"
    else:
        ou_destino = base_destino

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