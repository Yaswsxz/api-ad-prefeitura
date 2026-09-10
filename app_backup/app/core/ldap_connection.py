from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE, SUBTREE
from ldap3.core.exceptions import LDAPException
from fastapi import HTTPException
from app.core.config import settings


def get_connection() -> Connection:
    """
    Abre uma conexão autenticada com o Active Directory usando NTLM.
    """
    try:
        use_ssl = settings.AD_SERVER.lower().startswith("ldaps")
        server = Server(settings.AD_SERVER, use_ssl=use_ssl, get_info=ALL)

        conn = Connection(
            server,
            user=settings.AD_BIND_USER,
            password=settings.AD_BIND_PASSWORD,
            authentication=NTLM,      
            auto_bind=True,
        )
        return conn
    except LDAPException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Não foi possível conectar ao Active Directory: {e}",
        )