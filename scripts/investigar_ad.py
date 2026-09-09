from ldap3 import Server, Connection, SUBTREE

server = Server("cegonha.londrina.pr.gov.br")
conn = Connection(server, user="pmldomain\\grds1.estag", password="SENHA_REMOVIDA", auto_bind=True)

conn.search(
    search_base="OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
    search_filter="(objectClass=*)",
    search_scope=SUBTREE,
    attributes=["objectClass", "name"],
)

print("Quantidade de entradas encontradas:", len(conn.entries))
for entry in conn.entries:
    print("-", entry.entry_dn, "| classes:", list(entry.objectClass))

conn.unbind()