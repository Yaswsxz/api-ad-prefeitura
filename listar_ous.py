from app.core.ldap_connection import get_connection

conn = get_connection()

conn.search(
    search_base="DC=londrina,DC=pr,DC=gov,DC=br",
    search_filter="(objectClass=organizationalUnit)",
    search_scope=2,
    attributes=["ou", "distinguishedName"]
)

print("OUs encontradas:")
for entry in conn.entries:
    print(f"   - {entry.ou} ({entry.distinguishedName})")
