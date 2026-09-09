#!/usr/bin/env python
"""
Script para testar a conexão com o Active Directory
Usando as variáveis do seu .env
"""

import os
from dotenv import load_dotenv
from ldap3 import Server, Connection, ALL, NTLM
import ssl

# Carrega as variáveis do .env
load_dotenv()

def testar_conexao_ad():
    """Testa a conexão com o AD e lista as OUs encontradas"""
    
    # 🔥 Usando as variáveis do seu .env
    server_url = os.getenv('AD_SERVER', 'ldap://cegonha.londrina.pr.gov.br')
    user = os.getenv('AD_BIND_USER', 'pmldomain\grds1.estag')
    password = os.getenv('AD_BIND_PASSWORD', 'pmldesenvol')
    base_dn = os.getenv('AD_BASE_DN', 'OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br')
    search_base = os.getenv('AD_SEARCH_BASE', 'OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br')
    domain = os.getenv('AD_DOMAIN', 'cegonha.londrina.pr.gov.br')
    user_ou = os.getenv('AD_USER_OU', 'OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br')
    
    print("=" * 70)
    print("🧪 TESTE DE CONEXÃO COM O ACTIVE DIRECTORY")
    print("=" * 70)
    print(f"📡 Servidor: {server_url}")
    print(f"👤 Usuário: {user}")
    print(f"🔑 Senha: {'*' * len(password) if password else 'NÃO DEFINIDA'}")
    print(f"📁 Base DN: {base_dn}")
    print(f"🔍 Search Base: {search_base}")
    print(f"🏢 Domínio: {domain}")
    print(f"📂 OU de Usuários: {user_ou}")
    print("=" * 70)
    
    # Verifica se as credenciais foram preenchidas
    if not server_url:
        print("❌ ERRO: AD_SERVER não configurado no .env!")
        return False
    
    if not user or not password:
        print("❌ ERRO: Usuário ou senha não configurados no .env!")
        print("   Verifique AD_BIND_USER e AD_BIND_PASSWORD")
        return False
    
    if not base_dn:
        print("❌ ERRO: AD_BASE_DN não configurado no .env!")
        return False
    
    try:
        # Conecta ao servidor
        print("🔄 Tentando conectar ao AD...")
        
        # Detecta se é SSL
        use_ssl = server_url.startswith('ldaps://')
        
        if use_ssl:
            print("🔒 Usando LDAPS (SSL)")
            # Configuração para ignorar certificado (apenas teste)
            tls_config = ssl.create_default_context()
            tls_config.check_hostname = False
            tls_config.verify_mode = ssl.CERT_NONE
            
            server = Server(server_url, get_info=ALL, use_ssl=True)
            conn = Connection(
                server,
                user=user,
                password=password,
                authentication=NTLM,
                auto_bind=True
            )
        else:
            print("🔓 Usando LDAP (sem SSL)")
            server = Server(server_url, get_info=ALL)
            conn = Connection(server, user=user, password=password, authentication=NTLM)
            conn.open()
            conn.bind()
        
        print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        print("=" * 70)
        
        # BUSCA 1: Organizational Units
        print("\n🔍 Buscando Organizational Units...")
        conn.search(
            search_base=base_dn,
            search_filter='(objectClass=organizationalUnit)',
            search_scope='SUBTREE',
            attributes=['ou', 'name', 'distinguishedName']
        )
        
        print(f"📌 Total de OUs encontradas: {len(conn.entries)}")
        print("-" * 70)
        
        if conn.entries:
            for entry in conn.entries:
                nome = entry.ou.value if hasattr(entry, 'ou') and entry.ou else entry.name.value if hasattr(entry, 'name') else 'N/A'
                print(f"   📁 {nome} - {entry.entry_dn}")
        else:
            print("   ⚠️ Nenhuma OU encontrada!")
        
        # BUSCA 2: Containers
        print("\n🔍 Buscando Containers...")
        conn.search(
            search_base=base_dn,
            search_filter='(objectClass=container)',
            search_scope='SUBTREE',
            attributes=['name', 'distinguishedName']
        )
        
        print(f"📌 Total de Containers encontrados: {len(conn.entries)}")
        print("-" * 70)
        
        if conn.entries:
            for entry in conn.entries:
                nome = entry.name.value if hasattr(entry, 'name') else 'N/A'
                print(f"   📦 {nome} - {entry.entry_dn}")
        else:
            print("   ⚠️ Nenhum Container encontrado!")
        
        # BUSCA 3: Usuários (se AD_USER_OU estiver definido)
        if user_ou:
            print(f"\n🔍 Buscando Usuários em: {user_ou}...")
            conn.search(
                search_base=user_ou,
                search_filter='(objectClass=user)',
                search_scope='SUBTREE',
                attributes=['sAMAccountName', 'cn', 'displayName']
            )
            
            print(f"📌 Total de Usuários encontrados: {len(conn.entries)}")
            print("-" * 70)
            
            if conn.entries:
                for entry in conn.entries[:10]:  # Mostra apenas os 10 primeiros
                    nome = entry.sAMAccountName.value if hasattr(entry, 'sAMAccountName') else 'N/A'
                    print(f"   👤 {nome} - {entry.entry_dn}")
                if len(conn.entries) > 10:
                    print(f"   ... e mais {len(conn.entries) - 10} usuários")
            else:
                print("   ⚠️ Nenhum usuário encontrado!")
        
        # Desconecta
        conn.unbind()
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA CONEXÃO: {e}")
        print("\n💡 DICAS DE SOLUÇÃO:")
        print("   1. Verifique se o servidor está acessível (ping)")
        print("   2. Confirme a porta correta (389 para LDAP, 636 para LDAPS)")
        print("   3. Verifique se o AD_SERVER está com 'ldap://' ou 'ldaps://'")
        print("   4. Confirme as credenciais (AD_BIND_USER e AD_BIND_PASSWORD)")
        print("   5. Verifique se o AD_BASE_DN está correto")
        return False

if __name__ == "__main__":
    testar_conexao_ad()