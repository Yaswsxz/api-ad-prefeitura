"""
Valida, sem AD, a massa da campanha de aceitação (tests/aceitacao/massa/*.tsv) contra as regras
reais da API: se a massa é inválida, a campanha falharia no AD por erro nosso, não da API.
"""
import csv
import unicodedata
from collections import Counter
from pathlib import Path

import pytest

from app.core.arvore import NOMES_RESERVADOS, Categoria, Ramo
from app.core.regras import regras
from app.schemas.estrutura import OUCreate
from app.schemas.identidade import HumanoCreate, NaoHumanoCreate

MASSA = Path(__file__).resolve().parent / "aceitacao" / "massa"


def ler(arquivo: str) -> list[dict]:
    with open(MASSA / arquivo, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


UNIDADES = ler("unidades.tsv")
IDENTIDADES = ler("identidades.tsv")
HUMANOS = [i for i in IDENTIDADES if i["tipo"] == "humano"]
NAO_HUMANOS = [i for i in IDENTIDADES if i["tipo"] == "naohumano"]


def test_unidades_por_ramo():
    assert Counter(u["ramo"] for u in UNIDADES) == {"direta": 3, "indireta": 3, "preposto": 2, "terceirizada": 2}


@pytest.mark.parametrize("u", UNIDADES, ids=lambda u: u["nome"])
def test_unidade_valida_realista_e_de_uma_palavra(u):
    assert OUCreate(nome=u["nome"], pml_nome_orgao=u["pml_nome_orgao"]).nome == u["nome"]
    nome = u["nome"]
    assert nome.isalpha() and nome.isupper() and nome.isascii()          # uma palavra, sem acento nem cedilha
    assert nome not in NOMES_RESERVADOS
    assert Ramo(u["ramo"])


def test_nomes_de_unidade_e_codigos_sao_unicos():
    assert len({u["nome"] for u in UNIDADES}) == len(UNIDADES) == 10
    assert len({u["cod"] for u in UNIDADES}) == 10 and all(len(u["cod"]) == 4 for u in UNIDADES)


def test_totais_da_matriz():
    assert (len(HUMANOS), len(NAO_HUMANOS), len(IDENTIDADES)) == (32, 40, 72)


def test_logins_unicos_e_dentro_do_limite_do_ad():
    logins = [i["login"] for i in IDENTIDADES]
    assert len(set(logins)) == len(logins)
    assert max(map(len, logins)) <= 20


@pytest.mark.parametrize("i", HUMANOS, ids=lambda i: i["login"])
def test_humano_valido_pelo_schema_da_api(i):
    categoria = None if i["categoria"] == "-" else Categoria(i["categoria"])
    humano = HumanoCreate(
        ramo=Ramo(i["ramo"]), unidade=i["unidade"], categoria=categoria, login=i["login"],
        nome_completo=i["nome"], cpf=None if i["cpf"] == "-" else i["cpf"],
    )
    assert unicodedata.normalize("NFC", i["nome"]) == i["nome"] == humano.nome_completo


@pytest.mark.parametrize("i", NAO_HUMANOS, ids=lambda i: i["login"])
def test_nao_humano_valido_pelo_schema_da_api(i):
    NaoHumanoCreate(ramo=Ramo(i["ramo"]), unidade=i["unidade"], login=i["login"], nome=i["nome"],
                    pml_nao_humano_tipo=i["tipo_nh"])
    assert i["tipo_nh"] in regras().tipos_nao_humano


def test_matriz_por_unidade():
    tipos = set(regras().tipos_nao_humano)
    for u in UNIDADES:
        humanos = [i for i in HUMANOS if i["unidade"] == u["nome"]]
        assert all(i["ramo"] == u["ramo"] for i in humanos)
        if u["ramo"] == "direta":
            assert Counter(i["categoria"] for i in humanos) == {"estagio": 2, "carreira": 2, "comissionado": 2}
        else:
            assert len(humanos) == 2 and {i["categoria"] for i in humanos} == {"-"}
        assert {i["tipo_nh"] for i in NAO_HUMANOS if i["unidade"] == u["nome"]} == tipos
        assert sum(1 for i in NAO_HUMANOS if i["unidade"] == u["nome"]) == len(tipos)


def test_so_o_primeiro_humano_de_cada_par_tem_cpf():
    com_cpf = [i for i in HUMANOS if i["cpf"] != "-"]
    assert len(com_cpf) == 16 and all(i["cpf"] == "00000000000" for i in com_cpf)
