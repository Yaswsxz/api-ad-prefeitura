from ldap3 import Server, Connection, NTLM

server = Server("cegonha.londrina.pr.gov.br")
user = "pmldomain\\grds1.estag"
password = "REMOVIDO"

conn = Connection(
    server,
    user=user,
    password=password,
    authentication=NTLM
)

conn.bind()
print(conn.result)
