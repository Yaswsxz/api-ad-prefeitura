"""Vocabulário da árvore (app/core/arvore.py): nomes, DNs montados e DNs lidos."""
import pytest

from app.core.arvore import (
    HUMANO, NAO_HUMANO, NOMES_RESERVADOS, OUS_INTERNAS_DIRETA, Arvore, Categoria, LocalIdentidade, Ramo,
    TipoIdentidade, dn_container, dn_ramo, dn_tipo, dn_unidade, dns_da_unidade, local_da_identidade,
    local_da_unidade, ou_interna, rdn_cn,
)
from app.core.config import settings

PML = settings.AD_PML_BASE


def test_nomes_fixos_da_estrutura():
    assert OUS_INTERNAS_DIRETA == ("Estagio", "Carreira", "Comissionados")      # sem NaoHumanos
    assert NOMES_RESERVADOS == {
        "OPERATIVOS", "INOPERANTES", "DESINCORPORADOS", "HUMANOS", "NAOHUMANOS", "DIRETA", "INDIRETA",
        "TERCEIRIZADAS", "PREPOSTOS", "ESTAGIO", "CARREIRA", "COMISSIONADOS",
    }


@pytest.mark.parametrize("ramo,ou", [
    (Ramo.DIRETA, "Direta"), (Ramo.INDIRETA, "Indireta"),
    (Ramo.TERCEIRIZADA, "Terceirizadas"), (Ramo.PREPOSTO, "Prepostos"),
])
def test_ramo_tem_slug_na_api_e_nome_no_ad(ramo, ou):
    assert ramo.ou == ou and Ramo.da_ou(ou.upper()) is ramo


def test_tipo_tem_nome_no_ad():
    assert (HUMANO.ou, NAO_HUMANO.ou) == ("Humanos", "NaoHumanos")
    assert TipoIdentidade.da_ou("HUMANOS") is HUMANO and TipoIdentidade.da_ou("naohumanos") is NAO_HUMANO
    assert TipoIdentidade.da_ou("Direta") is None


def test_montagem_de_dns():
    assert dn_tipo(Arvore.OPERATIVOS, HUMANO) == f"OU=Humanos,OU=Operativos,{PML}"
    assert dn_unidade(Arvore.OPERATIVOS, Ramo.DIRETA, "FAZENDA") == f"OU=FAZENDA,OU=Direta,OU=Humanos,OU=Operativos,{PML}"
    assert dn_unidade(Arvore.OPERATIVOS, Ramo.DIRETA, "FAZENDA", NAO_HUMANO) == \
        f"OU=FAZENDA,OU=Direta,OU=NaoHumanos,OU=Operativos,{PML}"
    assert dn_ramo(Arvore.DESINCORPORADOS, Ramo.PREPOSTO, NAO_HUMANO) == \
        f"OU=Prepostos,OU=NaoHumanos,OU=Desincorporados,{PML}"
    assert dns_da_unidade(Arvore.INOPERANTES, Ramo.INDIRETA, "CODEL") == (
        f"OU=CODEL,OU=Indireta,OU=Humanos,OU=Inoperantes,{PML}",
        f"OU=CODEL,OU=Indireta,OU=NaoHumanos,OU=Inoperantes,{PML}",
    )
    assert rdn_cn("Ana Lima") == "CN=Ana Lima"


def test_container_de_cada_tipo_e_ramo():
    base_h = f"OU=FAZENDA,OU=Direta,OU=Humanos,OU=Inoperantes,{PML}"
    assert dn_container(Arvore.INOPERANTES, Ramo.DIRETA, "FAZENDA", Categoria.COMISSIONADO) == f"OU=Comissionados,{base_h}"
    # não humano da Direta: direto na unidade, mesmo que se passe categoria; nunca há OU de categoria nele
    assert dn_container(Arvore.INOPERANTES, Ramo.DIRETA, "FAZENDA", None, NAO_HUMANO) == \
        f"OU=FAZENDA,OU=Direta,OU=NaoHumanos,OU=Inoperantes,{PML}"
    assert dn_container(Arvore.INOPERANTES, Ramo.DIRETA, "FAZENDA", Categoria.CARREIRA, NAO_HUMANO) == \
        f"OU=FAZENDA,OU=Direta,OU=NaoHumanos,OU=Inoperantes,{PML}"
    assert dn_container(Arvore.INOPERANTES, Ramo.INDIRETA, "CODEL") == \
        f"OU=CODEL,OU=Indireta,OU=Humanos,OU=Inoperantes,{PML}"


def test_ou_interna_so_existe_para_humano_da_direta():
    assert ou_interna(Ramo.DIRETA, HUMANO, Categoria.ESTAGIO) == "Estagio"
    assert ou_interna(Ramo.DIRETA, NAO_HUMANO, None) is None
    assert ou_interna(Ramo.INDIRETA, HUMANO, None) is None


def test_nomes_de_dn_sao_escapados():
    assert r"OU=A\,B," in dn_unidade(Arvore.OPERATIVOS, Ramo.DIRETA, "A,B")
    assert rdn_cn("Silva, Ana") == r"CN=Silva\, Ana"


CASOS = [
    (a, t, r, c)
    for a in Arvore for t in TipoIdentidade for r in Ramo
    for c in ([*Categoria] if (t is HUMANO and r is Ramo.DIRETA) else [None])
]


@pytest.mark.parametrize("arvore,tipo,ramo,categoria", CASOS)
def test_ler_o_dn_desfaz_a_montagem(arvore, tipo, ramo, categoria):
    dn = f"{rdn_cn('x')},{dn_container(arvore, ramo, 'FAZENDA', categoria, tipo)}"
    assert local_da_identidade(dn) == LocalIdentidade(arvore, tipo, ramo, "FAZENDA", categoria)


def test_local_da_identidade_recusa_dns_fora_do_formato():
    assert local_da_identidade(dn_unidade(Arvore.OPERATIVOS, Ramo.DIRETA, "FAZENDA")) is None
    assert local_da_identidade(f"CN=x,OU=U,OU=Direta,OU=Humanos,OU=Outra,{PML}") is None
    # formato antigo (sem o nível do tipo) e nível a mais
    assert local_da_identidade(f"CN=x,OU=Carreira,OU=U,OU=Direta,OU=Operativos,{PML}") is None
    assert local_da_identidade(f"CN=x,OU=Carreira,OU=U,OU=Indireta,OU=Humanos,OU=Operativos,{PML}") is None
    assert local_da_identidade(f"CN=x,OU=Carreira,OU=U,OU=Direta,OU=NaoHumanos,OU=Operativos,{PML}") is None
    # humano da Direta fora de uma OU de categoria
    assert local_da_identidade(f"CN=x,OU=Outra,OU=U,OU=Direta,OU=Humanos,OU=Operativos,{PML}") is None
    assert local_da_identidade(f"CN=x,OU=U,OU=Direta,OU=Humanos,OU=Operativos,{PML}") is None


@pytest.mark.parametrize("arvore,tipo,ramo", [(a, t, r) for a in Arvore for t in TipoIdentidade for r in Ramo])
def test_local_da_unidade(arvore, tipo, ramo):
    assert local_da_unidade(dn_unidade(arvore, ramo, "FAZENDA", tipo)) == (arvore, ramo, tipo)


def test_local_da_unidade_ignora_o_que_nao_e_unidade():
    unidade = dn_unidade(Arvore.OPERATIVOS, Ramo.DIRETA, "FAZENDA")
    assert local_da_unidade(dn_ramo(Arvore.OPERATIVOS, Ramo.DIRETA)) is None
    assert local_da_unidade(dn_tipo(Arvore.OPERATIVOS, HUMANO)) is None
    assert local_da_unidade(f"OU=Carreira,{unidade}") is None
    assert local_da_unidade(f"CN=x,OU=Carreira,{unidade}") is None
    assert local_da_unidade(f"OU=FAZENDA,OU=Direta,OU=Operativos,{PML}") is None      # formato antigo
