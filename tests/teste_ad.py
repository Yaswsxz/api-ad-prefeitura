from app.core.ldap_connection import get_connection
from app.core.config import settings

def testar_conexao():
    print("Testando conexao com o Active Directory...")
    print(f"Servidor: {settings.AD_SERVER}")
    print(f"Usuario: {settings.AD_BIND_USER}")

    try:
        conn = get_connection()
        print("Conectado ao AD com sucesso!\n")

        # MUDE A LINHA ABAIXO PARA TESTAR OUTRAS OUs
        conn.search(
            search_base="CN=Users,DC=londrina,DC=pr,DC=gov,DC=br",
            search_filter="(objectClass=user)",
            search_scope=2,
            attributes=["cn", "sAMAccountName", "mail", "title"],
            size_limit=10
        )

        print(f"Encontrados {len(conn.entries)} usuarios:")
        for entry in conn.entries:
            nome = entry.cn.value if entry.cn else "N/A"
            login = entry.sAMAccountName.value if entry.sAMAccountName else "N/A"
            print(f"   - {nome} ({login})")

        print("\nTeste de conexao finalizado com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao conectar ou buscar usuarios: {e}")
        return False

if __name__ == "__main__":
    testar_conexao()
