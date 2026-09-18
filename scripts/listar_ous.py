import sys
sys.path.insert(0, ".")  # garante que "app" seja importável rodando da raiz do projeto

from app.core.config import settings
from app.core.ldap_connection import get_connection

conn = get_connection()

conn.search(
    search_base=settings.AD_PML_BASE,
    search_filter="(objectClass=organizationalUnit)",
    search_scope=2,  # SUBTREE
    attributes=["ou", "distinguishedName"]
)

print(f"OUs encontradas dentro de {settings.AD_PML_BASE}:")
for entry in conn.entries:
    print(f"   - {entry.ou} ({entry.distinguishedName})")

conn.unbind()
