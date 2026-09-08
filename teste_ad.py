from app.core.ldap_connection import get_connection
from app.core.config import settings

def testar_busca(search_base):
    print(f"\n--- Buscando em: {search_base} ---")
    try:
        conn = get_connection()
        conn.search(
           search_base="OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
            search_filter="(objectClass=user)",
            search_scope=2,
            attributes=["cn", "sAMAccountName", "mail", "title"],
            size_limit=10
        )
        print(f"Encontrados {len(conn.entries)} usuarios")
        for entry in conn.entries:
            nome = entry.cn.value if entry.cn else "N/A"
            login = entry.sAMAccountName.value if entry.sAMAccountName else "N/A"
            print(f"   - {nome} ({login})")
        return len(conn.entries)
    except Exception as e:
        print(f"Erro: {e}")
        return 0

if __name__ == "__main__":
    print("=== TESTANDO VÁRIAS OUs ===")
    
    # Lista de OUs para testar
    ous = [
        "OU=Users,DC=londrina,DC=pr,DC=gov,DC=br",
        "OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
        "OU=PMLROOT,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
        "OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br",
        "OU=VMware Conv SA,DC=londrina,DC=pr,DC=gov,DC=br",
        "DC=londrina,DC=pr,DC=gov,DC=br",  # Raiz
    ]
    
    for ou in ous:
        testar_busca(ou)