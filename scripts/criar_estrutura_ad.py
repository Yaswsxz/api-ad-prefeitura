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


def fase1_esqueleto(dry_run: bool = False):
    print("=== FASE 1: esqueleto (Operativos/Inoperantes/Desincorporados + 4 ramos) ===")
    conn = get_connection()
    try:
        for arvore in ARVORES:
            dn_arvore = f"OU={arvore},{settings.AD_PML_BASE}"
            if dry_run:
                print(f"[DRY-RUN] criaria: {dn_arvore}")
            else:
                _criar_container(conn, dn_arvore, arvore)
                print(f"OK  {dn_arvore}")
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