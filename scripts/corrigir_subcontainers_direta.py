"""
Corrige os 4 subcontainers fixos da Direta (Estagio, Carreira,
Comissionados, NaoHumanos).

Regra alvo:
    OU=Direta (em Operativos e Inoperantes)
      └── OU=<UNIDADE>
            ├── CN=Estagio         (container)
            ├── CN=Carreira        (container)
            ├── CN=Comissionados   (container)
            └── CN=NaoHumanos      (container)

O script é idempotente e cobre 3 cenários por subcontainer:
  1. Existe como OU (errado)     → deleta a OU e cria o container
  2. Existe como CN (container)  → pula
  3. Não existe                  → cria o container

Uso:
    py -3.11 scripts/corrigir_subcontainers_direta.py --dry-run
    py -3.11 scripts/corrigir_subcontainers_direta.py --confirmar
"""

import sys
sys.path.insert(0, ".")

import argparse
from app.core.config import settings
from app.core.ldap_connection import get_connection


SUBCONTAINERS = ["Estagio", "Carreira", "Comissionados", "NaoHumanos"]
ARVORES = ["Operativos", "Inoperantes"]


# =============================================================================
# Helpers de checagem
# =============================================================================

def _listar_unidades_direta(conn, arvore: str):
    """
    Lista os DNs das unidades (filhas diretas de OU=Direta) na árvore dada.
    Ex: ['OU=FAZENDA,OU=Direta,OU=Operativos,OU=PML,...', ...]
    """
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
    Procura um filho direto com cn=<nome> OU ou=<nome> sob unidade_dn.
    Devolve (dn, objectClass) ou (None, None) se não achar.
    """
    conn.search(
        search_base=unidade_dn,
        search_filter=f"(|(cn={nome})(ou={nome}))",
        search_scope="LEVEL",
        attributes=["distinguishedName", "objectClass"],
    )
    if not conn.entries:
        return None, None
    e = conn.entries[0]
    return str(e.entry_dn), [str(c).lower() for c in e.objectClass]


def _tem_filhos(conn, dn: str) -> bool:
    conn.search(search_base=dn, search_filter="(objectClass=*)", search_scope="LEVEL")
    return len(conn.entries) > 0


def _criar_container(conn, parent_dn: str, nome: str) -> None:
    dn = f"CN={nome},{parent_dn}"
    ok = conn.add(dn, attributes={
        "objectClass": ["top", "container"],
        "cn": nome,
    })
    if not ok:
        raise RuntimeError(f"Falha ao criar container '{dn}': {conn.result}")


# =============================================================================
# Planejamento das ações
# =============================================================================

def planejar(conn):
    """
    Percorre todas as unidades da Direta (em Operativos e Inoperantes) e
    planeja o que fazer para cada um dos 4 subcontainers.

    Devolve uma lista de dicts:
      {
        "arvore":    "Operativos" | "Inoperantes",
        "unidade":   "OU=FAZENDA,OU=Direta,...",
        "nome":      "Estagio",
        "acao":      "deletar_ou_criar_container" | "criar_container" | "ok",
        "dn_ou":     DN antigo (se houver OU para deletar)
        "dn_final":  DN final esperado (container)
      }
    """
    plano = []

    for arvore in ARVORES:
        unidades = _listar_unidades_direta(conn, arvore)
        for unidade_dn in unidades:
            for nome in SUBCONTAINERS:
                dn_atual, classes = _buscar_subcontainer(conn, unidade_dn, nome)
                dn_final = f"CN={nome},{unidade_dn}"

                if dn_atual is None:
                    # Não existe nada → cria como container
                    plano.append({
                        "arvore": arvore, "unidade": unidade_dn,
                        "nome": nome, "acao": "criar_container",
                        "dn_ou": None, "dn_final": dn_final,
                    })
                elif "organizationalunit" in classes:
                    # Existe como OU → deleta e recria
                    plano.append({
                        "arvore": arvore, "unidade": unidade_dn,
                        "nome": nome, "acao": "deletar_ou_criar_container",
                        "dn_ou": dn_atual, "dn_final": dn_final,
                    })
                elif "container" in classes:
                    # Já é container → nada a fazer
                    plano.append({
                        "arvore": arvore, "unidade": unidade_dn,
                        "nome": nome, "acao": "ok",
                        "dn_ou": None, "dn_final": dn_atual,
                    })
                else:
                    # Existe, mas é outro tipo (raro) — sinaliza
                    plano.append({
                        "arvore": arvore, "unidade": unidade_dn,
                        "nome": nome, "acao": "inconsistente",
                        "dn_ou": dn_atual, "dn_final": dn_final,
                    })

    return plano


# =============================================================================
# Execução
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Corrige subcontainers da Direta")
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

        # Agrupa para exibir
        por_arvore = {}
        for item in plano:
            por_arvore.setdefault(item["arvore"], []).append(item)

        total_del = sum(1 for i in plano if i["acao"] == "deletar_ou_criar_container")
        total_new = sum(1 for i in plano if i["acao"] == "criar_container")
        total_ok  = sum(1 for i in plano if i["acao"] == "ok")
        total_err = sum(1 for i in plano if i["acao"] == "inconsistente")

        print(f"Plano: {total_del} deletar+criar, "
              f"{total_new} criar, {total_ok} já OK, {total_err} inconsistentes\n")

        # Exibe por árvore
        for arvore in ARVORES:
            if arvore not in por_arvore:
                continue
            print(f"▶ {arvore}")
            for item in por_arvore[arvore]:
                acao = item["acao"]
                if acao == "ok":
                    print(f"  [OK]   CN={item['nome']},{item['unidade']}")
                elif acao == "criar_container":
                    print(f"  [NEW]  CN={item['nome']},{item['unidade']}")
                elif acao == "deletar_ou_criar_container":
                    print(f"  [FIX]  deletar {item['dn_ou']}")
                    print(f"         criar   CN={item['nome']},{item['unidade']}")
                else:
                    print(f"  [???]  {item['dn_ou']} — tipo inesperado")
            print()

        if args.dry_run:
            print("Dry-run: nada foi alterado. Rode com --confirmar.")
            return

        if total_del + total_new == 0:
            print("Nada a fazer. Tudo já está no formato correto.")
            return

        resp = input(f'Digite "CORRIGIR {total_del + total_new} ITENS" para confirmar: ')
        if resp.strip() != f"CORRIGIR {total_del + total_new} ITENS":
            print("Cancelado.")
            return

        ok_del, ok_new, erros = 0, 0, []

        # Processa do mais fundo para o mais raso (evita erro de delete com filho)
        plano_ordenado = sorted(plano, key=lambda x: -len(x["unidade"].split(",")))

        for item in plano_ordenado:
            if item["acao"] == "ok":
                continue

            # Deletar a OU, se aplicável
            if item["acao"] == "deletar_ou_criar_container":
                dn_ou = item["dn_ou"]
                if _tem_filhos(conn, dn_ou):
                    erros.append((dn_ou, "tem conteúdo dentro — abortado"))
                    print(f"  [SKIP] {dn_ou}  (tem filhos)")
                    continue
                if conn.delete(dn_ou):
                    print(f"  [DEL]  {dn_ou}")
                    ok_del += 1
                else:
                    erros.append((dn_ou, f"falha ao deletar: {conn.result}"))
                    print(f"  [ERR]  {dn_ou}  → {conn.result}")
                    continue

            # Criar container
            try:
                _criar_container(conn, item["unidade"], item["nome"])
                print(f"  [NEW]  CN={item['nome']},{item['unidade']}")
                ok_new += 1
            except Exception as e:
                erros.append((item["dn_final"], str(e)))
                print(f"  [ERR]  CN={item['nome']},{item['unidade']}  → {e}")

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