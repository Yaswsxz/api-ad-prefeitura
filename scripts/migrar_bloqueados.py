"""
Script para migrar usuarios da OU Bloqueados para OU Inativos.
"""
from app.core.ldap_connection import get_connection
from app.core.config import settings

OU_BLOQUEADOS = "OU=Bloqueados,DC=londrina,DC=pr,DC=gov,DC=br"
OU_INATIVOS = "OU=Inativos,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"


def listar_usuarios_da_ou(ou: str):
    conn = get_connection()
    try:
        conn.search(
            search_base=ou,
            search_filter="(objectClass=user)",
            search_scope=2,
            attributes=["cn", "sAMAccountName"]
        )
        return conn.entries
    finally:
        conn.unbind()


def mover_usuario_por_dn(dn: str, nova_ou: str):
    """Move um usuário para uma nova OU usando o DN diretamente."""
    conn = get_connection()
    try:
        # Extrai o CN do DN
        cn = dn.split(',')[0]
        novo_dn = f"{cn},{nova_ou}"
        conn.modify_dn(dn, novo_dn)
        if conn.result['result'] == 0:
            return True
        else:
            raise Exception(f"Erro ao mover: {conn.result}")
    finally:
        conn.unbind()


def migrar_bloqueados_para_inativos():
    print("=" * 60)
    print("SCRIPT DE MIGRACAO: Bloqueados -> Inativos")
    print("=" * 60)

    print(f"\nBuscando usuarios em: {OU_BLOQUEADOS}")
    usuarios = listar_usuarios_da_ou(OU_BLOQUEADOS)

    if not usuarios:
        print("Nenhum usuario encontrado em Bloqueados.")
        return

    print(f"Encontrados {len(usuarios)} usuarios em Bloqueados.\n")

    print("Usuarios a serem migrados:")
    for entry in usuarios:
        nome = entry.cn.value if entry.cn else "N/A"
        login = entry.sAMAccountName.value if entry.sAMAccountName else "N/A"
        print(f"   - {nome} ({login})")

    confirmacao = input("\nDeseja continuar? (s/N): ")
    if confirmacao.lower() != 's':
        print("Operacao cancelada.")
        return

    print("\nMigrando...")
    sucessos = 0
    erros = 0

    for entry in usuarios:
        dn = entry.entry_dn
        nome = entry.cn.value if entry.cn else "N/A"
        try:
            mover_usuario_por_dn(dn, OU_INATIVOS)
            print(f"   OK {nome} movido para Inativos")
            sucessos += 1
        except Exception as e:
            print(f"   ERRO ao mover {nome}: {e}")
            erros += 1

    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"   Sucessos: {sucessos}")
    print(f"   Erros: {erros}")
    print(f"   Total: {len(usuarios)}")
    print("=" * 60)


if __name__ == "__main__":
    migrar_bloqueados_para_inativos()