"""
Recria a árvore do PML no AD com os tipos corretos:

    OU=PML
     +-- OU=Operativos
     |    +-- OU=Direta
     |    |     +-- OU=FAZENDA
     |    |     |     +-- CN=Estagio          (container)
     |    |     |     +-- CN=Carreira         (container)
     |    |     |     +-- CN=Comissionados    (container)
     |    |     |     +-- CN=NaoHumanos       (container)
     |    |     +-- OU=EDUCACAO
     |    |     +-- ...
     |    +-- OU=Indireta
     |    +-- OU=Terceirizadas
     |    +-- OU=Prepostos
     +-- OU=Inoperantes        (espelho 1:1 de Operativos)
     +-- OU=Desincorporados    (sem ramos fixos; nascem sob demanda)

Uso:
    py -3.11 scripts/criar_estrutura_ad.py --dry-run
    py -3.11 scripts/criar_estrutura_ad.py
"""

import sys
sys.path.insert(0, ".")

import argparse
from fastapi import HTTPException

from app.core.config import settings
from app.core.ldap_connection import get_connection
from app.schemas.estrutura import RamoOU


# =============================================================================
# Configuração
# =============================================================================

ARVORES_ESPELHADAS = ["Operativos", "Inoperantes"]
ARVORES_EXTRA = ["Desincorporados"]
RAMOS = [RamoOU.DIRETA, RamoOU.INDIRETA, RamoOU.TERCEIRIZADAS, RamoOU.PREPOSTOS]

SUBCONTAINERS_DIRETA = ["Estagio", "Carreira", "Comissionados", "NaoHumanos"]

UNIDADES = {
    RamoOU.DIRETA: [
        ("FAZENDA",        "Secretaria Municipal da Fazenda"),
        ("EDUCACAO",       "Secretaria Municipal de Educação"),
        ("PLANEJAMENTO",   "Secretaria Municipal de Planejamento, Orçamento e Tecnologia"),
        ("PROCURADORIA",   "Procuradoria-Geral do Município"),
        ("OUVIDORIA",      "Ouvidoria-Geral do Município"),
        ("SAUDE",          "Secretaria Municipal de Saúde"),
    ],
    RamoOU.INDIRETA: [
        ("CODEL",     "Companhia de Desenvolvimento de Londrina"),
        ("CMTU",      "Companhia Municipal de Trânsito e Urbanização"),
        ("COHAB",     "Companhia de Habitação de Londrina"),
        ("ACESF",     "Administração dos Cemitérios e Serviços Funerários de Londrina"),
        ("CAAPSML",   "Caixa de Assistência, Aposentadoria e Pensões dos Servidores do Município de Londrina"),
        ("FEL",       "Fundação de Esportes de Londrina"),
        ("IPPUL",     "Instituto de Pesquisa e Planejamento Urbano de Londrina"),
        ("AMS",       "Autarquia Municipal de Saúde"),
        ("SERCONTEL", "Sercomtel S.A."),
    ],
    RamoOU.TERCEIRIZADAS: [],
    RamoOU.PREPOSTOS: [
        ("CARTORIO SEGUNDO", "Cartório do Segundo Ofício"),
    ],
}


# =============================================================================
# Helpers — agora com CN= ou OU= conforme o tipo
# =============================================================================

def _existe(conn, parent_dn: str, nome: str) -> bool:
    """Verifica filho direto com CN=<nome> OU OU=<nome>."""
    conn.search(
        search_base=parent_dn,
        search_filter=f"(|(cn={nome})(ou={nome}))",
        search_scope="LEVEL",
    )
    return len(conn.entries) > 0


def _criar_ou(conn, parent_dn: str, nome: str, extras: dict = None) -> str:
    """Cria uma OU (organizationalUnit) sob parent_dn. Devolve o DN criado."""
    dn = f"OU={nome},{parent_dn}"
    attrs = {
        "objectClass": ["top", "organizationalUnit"],
        "ou": nome,
    }
    if extras:
        attrs.update(extras)

    ok = conn.add(dn, attributes=attrs)
    if not ok:
        raise HTTPException(status_code=500, detail=f"Falha ao criar OU '{dn}': {conn.result}")
    return dn


def _criar_container(conn, parent_dn: str, nome: str) -> str:
    """Cria um container (objectClass=container). Usado só nos 4 subcontainers da Direta."""
    dn = f"CN={nome},{parent_dn}"
    ok = conn.add(dn, attributes={
        "objectClass": ["top", "container"],
        "cn": nome,
    })
    if not ok:
        raise HTTPException(status_code=500, detail=f"Falha ao criar container '{dn}': {conn.result}")
    return dn


def _garantir_ou(conn, parent_dn: str, nome: str, dry_run: bool, extras: dict = None,
                 prefixo_log: str = "  ") -> bool:
    if _existe(conn, parent_dn, nome):
        print(f"{prefixo_log}[OK]   OU={nome}  (já existe em {parent_dn})")
        return False
    if dry_run:
        print(f"{prefixo_log}[DRY]  criaria OU={nome},{parent_dn}")
        return False
    _criar_ou(conn, parent_dn, nome, extras)
    print(f"{prefixo_log}[NEW]  OU={nome},{parent_dn}")
    return True

def _garantir_container(conn, parent_dn: str, nome: str, dry_run: bool, prefixo_log: str = "  ") -> bool:
    if _existe(conn, parent_dn, nome):
        print(f"{prefixo_log}[OK]   CN={nome}  (já existe em {parent_dn})")
        return False
    if dry_run:
        print(f"{prefixo_log}[DRY]  criaria CN={nome},{parent_dn}")
        return False
    _criar_container(conn, parent_dn, nome)
    print(f"{prefixo_log}[NEW]  CN={nome},{parent_dn}")
    return True


def garantir_pml(conn, dry_run: bool) -> bool:
    """
    Garante que o próprio OU=PML existe (cria se tiver sido apagado).
    Extrai o RDN e o pai a partir de settings.AD_PML_BASE.
    """
    base = settings.AD_PML_BASE            # ex: "OU=PML,OU=DESENVOL,DC=londrina,..."
    partes = base.split(",", 1)

    if len(partes) < 2:
        print(f"  [ERR] AD_PML_BASE inválido (sem pai): {base}")
        return False

    rdn, parent = partes[0].strip(), partes[1].strip()
    if "=" not in rdn:
        print(f"  [ERR] Primeiro componente inválido em AD_PML_BASE: {rdn}")
        return False

    _, nome = rdn.split("=", 1)             # "PML"

    if _existe(conn, parent, nome):
        print(f"  [OK]   {rdn},{parent}  (já existe)")
        return False

    if dry_run:
        print(f"  [DRY]  criaria {rdn},{parent}")
        return False

    _criar_ou(conn, parent, nome)
    print(f"  [NEW]  {rdn},{parent}")
    return True


# =============================================================================
# Fase 1 — Esqueleto
# =============================================================================

def garantir_esqueleto(conn, dry_run: bool) -> int:
    print("=" * 72)
    print("FASE 1 — Esqueleto (árvores e ramos, tudo OU)")
    print("=" * 72)

    criados = 0

    for arvore in ARVORES_ESPELHADAS + ARVORES_EXTRA:
        print(f"\n▶ {arvore}")
        if _garantir_ou(conn, settings.AD_PML_BASE, arvore, dry_run):
            criados += 1

        if arvore == "Desincorporados":
            continue  # não tem ramos fixos

        parent = f"OU={arvore},{settings.AD_PML_BASE}"
        for ramo in RAMOS:
            if _garantir_ou(conn, parent, ramo.value, dry_run, prefixo_log="    "):
                criados += 1

    return criados


# =============================================================================
# Fase 2 — Unidades + subcontainers
# =============================================================================

def garantir_unidades(conn, dry_run: bool) -> dict:
    print()
    print("=" * 72)
    print("FASE 2 — Unidades (OU) + subcontainers (CN, só na Direta)")
    print("=" * 72)

    resultado = {"criadas": [], "existentes": [], "erros": []}

    for ramo, unidades in UNIDADES.items():
        if not unidades:
            print(f"\n▶ {ramo.value}: (nenhuma unidade cadastrada ainda)")
            continue

        print(f"\n▶ {ramo.value} ({len(unidades)} unidades)")
        parent_op = f"OU={ramo.value},OU=Operativos,{settings.AD_PML_BASE}"
        parent_inop = f"OU={ramo.value},OU=Inoperantes,{settings.AD_PML_BASE}"

        for nome, descricao in unidades:
            existe_op = _existe(conn, parent_op, nome)
            existe_inop = _existe(conn, parent_inop, nome)

            if existe_op and existe_inop:
                print(f"    [OK]   {nome}")
                resultado["existentes"].append(f"{ramo.value}/{nome}")
                continue

            if dry_run:
                if not existe_op:
                    print(f"    [DRY]  criaria OU={nome},{parent_op}  (+ subcontainers)")
                if not existe_inop:
                    print(f"    [DRY]  criaria OU={nome},{parent_inop}  (+ subcontainers)")
                continue

            # Cria cada um que falta
            try:
                for existe, parent, arvore in [
                    (existe_op, parent_op, "Operativos"),
                    (existe_inop, parent_inop, "Inoperantes"),
                ]:
                    if existe:
                        continue
                    # Atributo pmlNomeOrgao ainda não existe no schema do AD.
                    # Criamos sem ele; quando o schema for estendido, usamos o PATCH /estrutura/unidades/<ramo>/<nome>.
                    extras = None
                    dn_unidade = _criar_ou(conn, parent, nome, extras)
                    print(f"    [NEW]  OU={nome},{parent}")

                    # Só Direta tem os 4 subcontainers
                    if ramo == RamoOU.DIRETA:
                        for sub in SUBCONTAINERS_DIRETA:
                            if not _existe(conn, dn_unidade, sub):
                                _criar_container(conn, dn_unidade, sub)
                                print(f"           └─ CN={sub}")

                resultado["criadas"].append(f"{ramo.value}/{nome}")
            except HTTPException as e:
                print(f"    [ERR]  {nome}: {e.detail}")
                resultado["erros"].append(f"{ramo.value}/{nome}: {e.detail}")
            except Exception as e:
                print(f"    [ERR]  {nome}: {e}")
                resultado["erros"].append(f"{ramo.value}/{nome}: {e}")

    return resultado


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Cria a árvore do PML com OUs")
    parser.add_argument("--dry-run", action="store_true", help="Só mostra")
    parser.add_argument("--so-esqueleto", action="store_true", help="Só Fase 1")
    args = parser.parse_args()

    print()
    if args.dry_run:
        print("╔" + "═" * 70 + "╗")
        print("║  MODO DRY-RUN — nada será criado no AD                          ║")
        print("╚" + "═" * 70 + "╝")
    print(f"  AD_PML_BASE = {settings.AD_PML_BASE}")
    print(f"  AD_SERVER   = {settings.AD_SERVER}\n")

    conn = get_connection()
    try:
        print("=" * 72)
        print("FASE 0 — Garantir OU=PML")
        print("=" * 72)
        garantir_pml(conn, dry_run=args.dry_run)   # ← NOVO

        criados = garantir_esqueleto(conn, dry_run=args.dry_run)
        resultado = {"criadas": [], "existentes": [], "erros": []}
        if not args.so_esqueleto:
            resultado = garantir_unidades(conn, dry_run=args.dry_run)
    finally:
        conn.unbind()

    print()
    print("=" * 72)
    print("RESUMO")
    print("=" * 72)
    if args.dry_run:
        print("  Dry-run — nada foi alterado.")
    else:
        print(f"  Esqueleto: {criados} OUs criadas")
        print(f"  Unidades:  {len(resultado['criadas'])} criadas, "
              f"{len(resultado['existentes'])} já existiam, "
              f"{len(resultado['erros'])} erros")
        if resultado["erros"]:
            for e in resultado["erros"]:
                print(f"    ✗ {e}")
    print()


if __name__ == "__main__":
    main()