from ldap3 import Server, Connection, NTLM

server = Server("cegonha.londrina.pr.gov.br")
user = "pmldomain\\grds1.estag"
password = "SENHA_REMOVIDA"

conn = Connection(server, user=user, password=password, authentication=NTLM)
conn.bind()
print("Conectado!")

dn = "CN=TesteDireto,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
attrs = {
    "objectClass": ["top", "person", "organizationalPerson", "user"],
    "cn": "TesteDireto",
    "sAMAccountName": "teste.direto",
    "userPrincipalName": "teste.direto@cegonha.londrina.pr.gov.br",
    "givenName": "Teste",
    "sn": "Direto"
}

result = conn.add(dn, attributes=attrs)
print(f"Resultado: {conn.result}")

if conn.result['result'] == 0:
    print("USUARIO CRIADO COM SUCESSO!")
else:
    print(f"FALHA: {conn.result}")
