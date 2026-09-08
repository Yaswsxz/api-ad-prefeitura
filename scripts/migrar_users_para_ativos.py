"""
Script para migrar usuarios da pasta CN=Users para OU=Ativos.
"""

from app.core.ldap_connection import get_connection
from app.core.config import settings

# CAMINHOS (já existentes)
OU_ATIVOS = "OU=Ativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
OU_USERS = "CN=Users,DC=londrina,DC=pr,DC=gov,DC=br"


def listar_usuarios_da_pasta_users():
    """Lista todos os usuários da pasta CN=Users."""
    conn = get_connection()
    try:
        conn.search(
            search_base=OU_USERS,
            search_filter="(&(objectClass=user)(objectCategory=person))",
            search_scope=2,
            attributes=["cn", "sAMAccountName"]
        )
        return conn.entries
    finally:
        conn.unbind()


def mover_usuario(dn: str, nova_ou: str):
    """Move um usuário para uma nova OU."""
    conn = get_connection()
    try:
        cn = dn.split(',')[0]
        novo_dn = f"{cn},{nova_ou}"
        conn.modify_dn(dn, novo_dn)
        if conn.result['result'] == 0:
            return True
        else:
            raise Exception(f"Erro ao mover: {conn.result}")
    finally:
        conn.unbind()


def migrar_usuarios():
    print("=" * 60)
    print("MIGRANDO USUARIOS: CN=Users -> OU=Ativos")
    print("=" * 60)

    print(f"\n🔍 Buscando usuarios em: {OU_USERS}")
    usuarios = listar_usuarios_da_pasta_users()

    if not usuarios:
        print("Nenhum usuario encontrado.")
        return

    print(f"\n✅ Encontrados {len(usuarios)} usuarios.\n")

    # Mostra alguns usuarios
    print("Primeiros 5 usuarios:")
    for entry in usuarios[:5]:
        nome = entry.cn.value if entry.cn else "N/A"
        login = entry.sAMAccountName.value if entry.sAMAccountName else "N/A"
        print(f"   - {login} ({nome})")

    confirmacao = input(f"\n⚠️ Deseja mover {len(usuarios)} usuarios para {OU_ATIVOS}? (s/N): ")
    if confirmacao.lower() != 's':
        print("Operacao cancelada.")
        return

    print("\n🔄 Migrando...")
    sucessos = 0
    erros = 0

    for entry in usuarios:
        dn = entry.entry_dn
        nome = entry.cn.value if entry.cn else "N/A"
        try:
            mover_usuario(dn, OU_ATIVOS)
            print(f"   ✅ {nome} movido para Ativos")
            sucessos += 1
        except Exception as e:
            print(f"   ❌ {nome}: {e}")
            erros += 1

    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📦 Total: {len(usuarios)}")
    print("=" * 60)


if __name__ == "__main__":
    migrar_usuarios()