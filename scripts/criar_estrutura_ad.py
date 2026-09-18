"""
Monta a árvore nova dentro do PML no AD, em duas fases:

  FASE 1 — esqueleto (containers vazios):
      PML (assume que já existe)
       +-- Operativos
       |    +-- Direta / Indireta / Terceirizadas / Prepostos
       +-- Inoperantes
       |    +-- Direta / Indireta / Terceirizadas / Prepostos
       +-- Desincorporados
            (sem os 4 ramos pré-criados — cada um nasce sozinho só quando
             a primeira unidade daquele ramo for realmente desincorporada)

  FASE 2 — unidades conhecidas dentro de Operativos/Inoperantes
      (Fazenda, CODEL, Cartório Segundo etc. — usa criar_ou(), que já
      cria a unidade nas duas árvores ao mesmo tempo e, para Direta,
      já cria os 4 subcontainers Estagio/Carreira/Comissionados/NaoHumanos).

Roda direto contra o AD, sem passar pela API HTTP (mesmo padrão dos
outros scripts em scripts/).

Uso:
    py -3.11 scripts/criar_estrutura_ad.py --dry-run   (só mostra o que faria)
    py -3.11 scripts/criar_estrutura_ad.py              (cria de verdade)
    py -3.11 scripts/criar_estrutura_ad.py --so-esqueleto   (fase 1 apenas, sem criar unidades)
"""

import sys
import argparse

sys.path.insert(0, ".")  # garante que "app" seja importável rodando da raiz do projeto

from fastapi import HTTPException

from app.core.config import settings
from app.core.ldap_connection import get_connection
from app.services.estrutura_service import _criar_container, criar_ou
from app.schemas.estrutura import RamoOU, OUCreate

ARVORES = ["Operativos", "Inoperantes", "Desincorporados"]
RAMOS = [r.value for r in RamoOU]  # Direta, Indireta, Terceirizadas, Prepostos

# Unidades conhecidas até agora — ajuste/complete conforme for confirmando
# mais órgãos com o supervisor. Formato: (nome_cn, pml_nome_orgao_descritivo)
UNIDADES = {
    RamoOU.DIRETA: [
        ("FAZENDA", "Secretaria Municipal da Fazenda"),
        ("EDUCACAO", "Secretaria Municipal de Educação"),
        ("PLANEJAMENTO", "Secretaria Municipal de Planejamento, Orçamento e Tecnologia"),
        ("PROCURADORIA", "Procuradoria-Geral do Município"),
        ("OUVIDORIA", "Ouvidoria-Geral do Município"),
        ("SAUDE", "Secretaria Municipal de Saúde"),
    ],
    RamoOU.INDIRETA: [
        ("CODEL", "Companhia de Desenvolvimento de Londrina"),
        ("CMTU", "Companhia Municipal de Trânsito e Urbanização"),
        ("COHAB", "Companhia de Habitação de Londrina"),
        ("ACESF", "Administração dos Cemitérios e Serviços Funerários de Londrina"),
        ("CAAPSML", "Caixa de Assistência, Aposentadoria e Pensões dos Servidores do Município de Londrina"),
        ("FEL", "Fundação de Esportes de Londrina"),
        ("IPPUL", "Instituto de Pesquisa e Planejamento Urbano de Londrina"),
        ("AMS", "Autarquia Municipal de Saúde"),
        ("SERCONTEL", "Sercomtel S.A."),
    ],
    RamoOU.TERCEIRIZADAS: [
        # ainda não temos nenhuma confirmada — adicionar aqui quando souberem
    ],
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

            # Desincorporados não recebe os 4 ramos pré-criados — cada ramo
            # só nasce ali quando a 1ª unidade daquele tipo for desincorporada
            # de verdade (mover_ou_desincorporar cuida disso sozinho).
            if arvore == "Desincorporados":
                continue

            for ramo in RAMOS:
                dn_ramo = f"OU={ramo},{dn_arvore}"
                if dry_run:
                    print(f"[DRY-RUN] criaria: {dn_ramo}")
                else:
                    _criar_container(conn, dn_ramo, ramo)
                    print(f"OK  {dn_ramo}")
    finally:
        conn.unbind()
    print()


def fase2_unidades(dry_run: bool = False):
    print("=== FASE 2: unidades dentro de Operativos/Inoperantes ===")
    total_ok = 0
    total_erro = 0

    for ramo, unidades in UNIDADES.items():
        for nome, pml_nome_orgao in unidades:
            if dry_run:
                print(f"[DRY-RUN] criaria: {ramo.value}/{nome} ({pml_nome_orgao})")
                continue

            try:
                dados = OUCreate(nome=nome, pml_nome_orgao=pml_nome_orgao)
                resultado = criar_ou(ramo, dados, operator="bootstrap-script")
                print(f"OK  {ramo.value:15s} {resultado.nome:20s} -> {resultado.distinguished_name_operativos}")
                total_ok += 1
            except HTTPException as e:
                if e.status_code == 409:
                    print(f"JÁ EXISTE  {ramo.value:15s} {nome}")
                else:
                    print(f"ERRO ({e.status_code})  {ramo.value:15s} {nome}: {e.detail}")
                    total_erro += 1
            except Exception as e:
                print(f"ERRO INESPERADO  {ramo.value:15s} {nome}: {e}")
                total_erro += 1

    if not dry_run:
        print(f"\nConcluído: {total_ok} criadas, {total_erro} erros.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Só mostra o que seria criado, sem tocar no AD")
    parser.add_argument("--so-esqueleto", action="store_true", help="Roda só a fase 1 (esqueleto), sem criar unidades")
    args = parser.parse_args()

    fase1_esqueleto(dry_run=args.dry_run)
    if not args.so_esqueleto:
        fase2_unidades(dry_run=args.dry_run)
