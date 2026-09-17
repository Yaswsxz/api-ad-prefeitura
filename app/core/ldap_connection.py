from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE, SUBTREE
from ldap3.core.exceptions import LDAPException
from fastapi import HTTPException
from app.core.logging_config import logger
from app.core.config import settings


def get_connection(user: str = None, password: str = None) -> Connection:
    """
    Abre uma conexão autenticada com o Active Directory usando NTLM.

    Se o servidor não estiver configurado como LDAPS (ldaps://), a conexão
    tenta um upgrade para TLS via StartTLS logo após abrir, antes do bind.
    Isso é necessário porque o AD recusa silenciosamente operações
    sensíveis — como a troca de senha (extend.microsoft.modify_password)
    — em conexões sem criptografia.

    IMPORTANTE: no ambiente de AD de testes atual (Windows Server 2003
    sem certificado configurado), o StartTLS é recusado pelo próprio
    servidor. Nesse caso, a conexão é reaberta sem criptografia (mesmo
    comportamento de antes), mas a troca de senha continuará falhando
    de forma silenciosa até que um administrador de domínio configure
    um certificado TLS no controlador de domínio.

    Por padrão, usa a conta de serviço (AD_BIND_USER/AD_BIND_PASSWORD do .env).
    Passando 'user' e 'password', é possível testar as credenciais de
    qualquer usuário.
    """
    use_ssl = settings.AD_SERVER.lower().startswith("ldaps")

    def _nova_conexao() -> Connection:
        server = Server(settings.AD_SERVER, use_ssl=use_ssl, get_info=ALL)
        return Connection(
            server,
            user=user or settings.AD_BIND_USER,
            password=password or settings.AD_BIND_PASSWORD,
            authentication=NTLM,
            auto_bind=False,
        )

    try:
        conn = _nova_conexao()
        conn.open()

        if not use_ssl:
            try:
                conn.start_tls()
            except LDAPException as e:
                # O servidor recusou o StartTLS (comum em AD antigo sem
                # certificado configurado). A tentativa deixa o socket
                # inutilizável, então descartamos essa conexão e abrimos
                # uma nova, sem TLS, em vez de seguir com um socket quebrado.
                logger.warning(
                    f"StartTLS recusado pelo servidor AD — reconectando sem "
                    f"criptografia (operações como troca de senha vão falhar "
                    f"até haver certificado TLS configurado no domínio): {e}"
                )
                try:
                    conn.unbind()
                except LDAPException:
                    pass
                conn = _nova_conexao()
                conn.open()

        if not conn.bind():
            raise HTTPException(
                status_code=401,
                detail="Credenciais inválidas para o Active Directory",
            )

        return conn

    except LDAPException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Não foi possível conectar ao Active Directory: {e}",
        )