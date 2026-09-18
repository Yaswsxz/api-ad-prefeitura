"""
Corrige os 4 subcontainers fixos da Direta: agora devem ser OUs
(organizationalUnit), não containers.

Alvo:
    OU=Direta (em Operativos e Inoperantes)
      └── OU=<UNIDADE>
            ├── OU=Estagio         (organizationalUnit)
            ├── OU=Carreira        (organizationalUnit)
            ├── OU=Comissionados   (organizationalUnit)
            └── OU=NaoHumanos      (organizationalUnit)

Idempotente — cobre 3 cenários por subcontainer:
  1. Existe como CN (container)   → deleta e recria como OU
  2. Existe como OU (correto)     → pula
  3. Não existe                   → cria como OU

Uso:
    py -3.11 scripts/corrigir_subcontainers_como_ou.py --dry-run
    py -3.11 scripts/corrigir_subcontainers_como_ou.py --confirmar
"""

import sys
sys.path.insert(0, ".")

import argparse
from app.core.config import settings
from app.core.ldap_connection import get_connection


SUBCONTAINERS = ["Estagio", "Carreira", "Comissionados", "NaoHumanos"]
ARVORES = ["Operativos", "Inoperantes"]


# =============================================================================
# Helpers
# =============================================================================

def _listar_unidades_direta(conn, arvore: str):
    """Lista DNs das unidades (filhas diretas de OU=Direta)."""
    base = f"OU=Direta,OU={arvore},{settings.AD_PML_BASE}"
    conn.search(
        search_base=base,
        search_filter="(objectClass=organizationalUnit)",
        search_scope="LEVEL",
        attributes=["distinguishedName"],
    )
    return [str(e.entry_dn) for e in conn.entries]


def _buscar_subcontainer(conn, unidade_dn: str, nome: str):
    """
    Procura um filho direto com cn=<nome> OU ou=<nome>.
    Devolve (dn, tipo, objectClass_list) onde tipo é 'OU', 'container',
    'outro' ou None se não achar.
    """
    conn.search(
        search_base=unidade_dn,
        search_filter=f"(|(cn={nome})(ou={nome}))",
        search_scope="LEVEL",
        attributes=["distinguishedName", "objectClass"],
    )
    if not conn.entries:
        return None, None, []

    e = conn.entries[0]
    classes = [str(c).lower() for c in e.objectClass]
    dn = str(e.entry_dn)

    if "organizationalunit" in classes:
        return dn, "OU", classes
    if "container" in classes:
        return dn, "container", classes
    return dn, "outro", classes


def _tem_filhos(conn, dn: str) -> bool:
    conn.search(search_base=dn, search_filter="(objectClass=*)", search_scope="LEVEL")
    return len(conn.entries) > 0


def _criar_ou(conn, parent_dn: str, nome: str) -> None:
    dn = f"OU={nome},{parent_dn}"
    ok = conn.add(dn, attributes={
        "objectClass": ["top", "organizationalUnit"],
        "ou": nome,
    })
    if not ok:
        raise RuntimeError(f"Falha ao criar OU '{dn}': {conn.result}")


# =============================================================================
# Planejamento
# =============================================================================

def planejar(conn):
    """
    Percorre todas as unidades da Direta (Operativos e Inoperantes) e
    planeja o que fazer para cada um dos 4 subcontainers.
    """
    plano = []

    for arvore in ARVORES:
        for unidade_dn in _listar_unidades_direta(conn, arvore):
            for nome in SUBCONTAINERS:
                dn_atual, tipo, _ = _buscar_subcontainer(conn, unidade_dn, nome)
                dn_final = f"OU={nome},{unidade_dn}"

                if dn_atual is None:
                    acao = "criar_ou"
                    dn_antigo = None
                elif tipo == "container":
                    acao = "deletar_container_criar_ou"
                    dn_antigo = dn_atual
                elif tipo == "OU":
                    acao = "ok"
                    dn_antigo = None
                else:
                    acao = "inconsistente"
                    dn_antigo = dn_atual

                plano.append({
                    "arvore": arvore,
                    "unidade": unidade_dn,
                    "nome": nome,
                    "acao": acao,
                    "dn_antigo": dn_antigo,
                    "dn_final": dn_final,
                })

    return plano


# =============================================================================
# Execução
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Corrige subcontainers da Direta para OU")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirmar", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.confirmar:
        print("⚠️  Use --dry-run para listar OU --confirmar para aplicar.")
        return

    print(f"\nAD_PML_BASE = {settings.AD_PML_BASE}\n")

    conn = get_connection()
    try:
        plano = planejar(conn)

        total_del = sum(1 for i in plano if i["acao"] == "deletar_container_criar_ou")
        total_new = sum(1 for i in plano if i["acao"] == "criar_ou")
        total_ok  = sum(1 for i in plano if i["acao"] == "ok")
        total_err = sum(1 for i in plano if i["acao"] == "inconsistente")

        print(f"Plano: {total_del} deletar+criar, "
              f"{total_new} criar, {total_ok} já OK, {total_err} inconsistentes\n")

        # Exibe por árvore
        for arvore in ARVORES:
            itens = [i for i in plano if i["arvore"] == arvore]
            if not itens:
                continue
            print(f"▶ {arvore}")
            for item in itens:
                if item["acao"] == "ok":
                    print(f"  [OK]   OU={item['nome']},{item['unidade']}")
                elif item["acao"] == "criar_ou":
                    print(f"  [NEW]  OU={item['nome']},{item['unidade']}")
                elif item["acao"] == "deletar_container_criar_ou":
                    print(f"  [FIX]  deletar {item['dn_antigo']}")
                    print(f"         criar   OU={item['nome']},{item['unidade']}")
                else:
                    print(f"  [???]  {item['dn_antigo']} — tipo inesperado")
            print()

        if args.dry_run:
            print("Dry-run: nada foi alterado. Rode com --confirmar.")
            return

        if total_del + total_new == 0:
            print("Nada a fazer. Tudo já está como OU.")
            return

        resp = input(f'Digite "CONVERTER {total_del + total_new} ITENS" para confirmar: ')
        if resp.strip() != f"CONVERTER {total_del + total_new} ITENS":
            print("Cancelado.")
            return

        ok_del, ok_new, erros = 0, 0, []

        # Processa do mais fundo para o mais raso
        plano_ordenado = sorted(plano, key=lambda x: -len(x["unidade"].split(",")))

        for item in plano_ordenado:
            if item["acao"] == "ok":
                continue

            # Deletar o container antigo
            if item["acao"] == "deletar_container_criar_ou":
                dn_antigo = item["dn_antigo"]
                if _tem_filhos(conn, dn_antigo):
                    erros.append((dn_antigo, "tem conteúdo dentro — abortado"))
                    print(f"  [SKIP] {dn_antigo}  (tem filhos)")
                    continue
                if conn.delete(dn_antigo):
                    print(f"  [DEL]  {dn_antigo}")
                    ok_del += 1
                else:
                    erros.append((dn_antigo, f"falha ao deletar: {conn.result}"))
                    print(f"  [ERR]  {dn_antigo}  → {conn.result}")
                    continue

            # Criar OU
            try:
                _criar_ou(conn, item["unidade"], item["nome"])
                print(f"  [NEW]  OU={item['nome']},{item['unidade']}")
                ok_new += 1
            except Exception as e:
                erros.append((item["dn_final"], str(e)))
                print(f"  [ERR]  OU={item['nome']},{item['unidade']}  → {e}")

        print()
        print("=" * 72)
        print("RESUMO")
        print("=" * 72)
        print(f"  Deletados:  {ok_del}")
        print(f"  Criados:    {ok_new}")
        print(f"  Erros:      {len(erros)}")
        for dn, msg in erros:
            print(f"    ✗ {dn}: {msg}")
    finally:
        conn.unbind()


if __name__ == "__main__":
    main()