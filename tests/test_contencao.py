"""
Contenção na raiz OU=DESENVOL e interpretação dos erros do AD.
Nenhum teste abre conexão: a ConexaoAD é criada sem rede e a guarda age antes dela.
"""
import json
import logging

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from ldap3 import MODIFY_REPLACE, Server
from ldap3.core.exceptions import LDAPCommunicationError, LDAPException

from app.core.erros_ad import (
    Codigo, ErroAD, ErroDominio, ErroForaDaRaiz, registrar_handlers, tratar_erros,
    traduzir_resultado,
)
from app.core.ldap_connection import ConexaoAD
from app.core.raiz import RAIZ_LDAP, dn_dentro, garantir_dentro, mascarar_dn
from app.services.base_ad import reverter

DENTRO = f"OU=PML,{RAIZ_LDAP}"
FORA = "OU=PML,OU=OUTRA,DC=londrina,DC=pr,DC=gov,DC=br"


# --- a raiz, por componentes de DN --------------------------------------------------

@pytest.mark.parametrize("dn", [RAIZ_LDAP, DENTRO, f"cn=x,ou=pml,{RAIZ_LDAP.lower()}"])
def test_dentro_da_raiz(dn):
    assert dn_dentro(dn)


@pytest.mark.parametrize("dn", [
    "", "   ", "lixo",
    "DC=londrina,DC=pr,DC=gov,DC=br",
    "OU=PML,DC=londrina,DC=pr,DC=gov,DC=br",
    FORA,
    "OU=DESENVOL-X,DC=londrina,DC=pr,DC=gov,DC=br",      # contém o nome, mas não é a raiz
    f"{RAIZ_LDAP},OU=ESTRANHA",                           # a raiz não é o sufixo
])
def test_fora_da_raiz(dn):
    assert not dn_dentro(dn)


def test_garantir_dentro_levanta_403():
    garantir_dentro(DENTRO, "teste")
    for dn in (FORA, None, ""):
        with pytest.raises(ErroForaDaRaiz) as e:
            garantir_dentro(dn, "teste")
        assert e.value.status_code == 403 and e.value.codigo == Codigo.FORA_DA_RAIZ


def test_mascarar_dn_esconde_so_o_nome_de_pessoa():
    assert mascarar_dn(f"CN=Ana Lima,OU=Carreira,{DENTRO}") == f"CN=<nome>,OU=Carreira,OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
    assert mascarar_dn("") == "" and mascarar_dn("lixo") == "<dn-invalido>"


# --- a guarda na conexão (age antes de qualquer rede) --------------------------------

@pytest.fixture
def conn():
    return ConexaoAD(Server("ldap://localhost"), user="u", password="p", check_names=False)


@pytest.mark.parametrize("chamada", [
    lambda c: c.add(FORA, attributes={"ou": "X"}),
    lambda c: c.modify(FORA, {"description": [(MODIFY_REPLACE, ["x"])]}),
    lambda c: c.delete(FORA),
    lambda c: c.search(FORA, "(objectClass=*)"),
    lambda c: c.search("", "(objectClass=*)"),
    lambda c: c.modify_dn(FORA, "OU=X", new_superior=DENTRO),
    lambda c: c.modify_dn(DENTRO, "OU=X", new_superior=FORA),
])
def test_conexao_recusa_dn_fora_da_raiz(conn, chamada):
    with pytest.raises(ErroForaDaRaiz):
        chamada(conn)


# --- o resultado de cada operação ---------------------------------------------------------

def test_sucesso_devolve_o_retorno_e_registra_ad_ok(conn, caplog):
    conn.result = {"result": 0}
    assert conn._executar("modify", f"CN=Ana,{DENTRO}", ("pmlCpf",), lambda: "ok") == "ok"
    assert "AD_OK operacao=modify" in caplog.text and "pmlCpf" in caplog.text and "Ana" not in caplog.text


def test_falha_do_ad_vira_erro_sem_vazar_o_resultado_bruto(conn, caplog):
    conn.result = {"result": 50, "description": "insufficientAccessRights", "message": "TEXTO-INTERNO-DO-AD"}
    with pytest.raises(ErroAD) as e:
        conn._executar("modify", f"CN=Fulano,{DENTRO}", ("pmlCpf",), lambda: False)
    assert (e.value.status_code, e.value.codigo) == (502, Codigo.AD_PERMISSAO_NEGADA)
    assert "TEXTO-INTERNO" not in json.dumps({"m": e.value.mensagem, "d": e.value.detalhes})
    assert "AD_ERRO operacao=modify" in caplog.text and "Fulano" not in caplog.text


def test_busca_com_limite_de_tamanho_nao_e_falha(conn):
    conn.result = {"result": 4}
    assert conn._executar("search", DENTRO, (), lambda: [1]) == [1]


@pytest.mark.parametrize("excecao,status,codigo", [
    (LDAPCommunicationError("rede"), 503, Codigo.AD_INDISPONIVEL),
    (LDAPException("outra"), 500, Codigo.ERRO_LDAP_CLIENTE),
])
def test_falha_do_cliente_ldap(conn, excecao, status, codigo):
    def chamada():
        raise excecao
    with pytest.raises(ErroDominio) as e:
        conn._executar("search", DENTRO, (), chamada)
    assert (e.value.status_code, e.value.codigo) == (status, codigo)


# --- tabela: código LDAP -> erro da API e permissão a pedir ---------------------------------

PERM, SCHEMA, TLS = Codigo.AD_PERMISSAO_NEGADA, Codigo.AD_SCHEMA_INCOMPLETO, Codigo.AD_TLS_INDISPONIVEL

TABELA = [
    # operação, código LDAP, atributos, classe, criptografada, HTTP, código da API, trecho da providência
    ("add", 50, ("ou",), "organizationalunit", True, 502, PERM, "Organizational Unit"),
    ("add", 50, ("sAMAccountName",), "user", True, 502, PERM, "Create User"),
    ("modify", 50, ("unicodePwd",), None, True, 502, PERM, "Reset Password"),
    ("modify", 50, ("userAccountControl",), None, True, 502, PERM, "userAccountControl"),
    ("modify", 50, ("pmlCpf",), None, True, 502, PERM, "pmlCpf"),
    ("modify_dn", 50, (), None, True, 502, PERM, "Create child objects"),
    ("delete", 50, (), None, True, 502, PERM, "Delete"),
    ("search", 50, (), None, True, 502, PERM, "List contents"),
    ("modify", 16, ("pmlCpf",), None, True, 502, SCHEMA, "schema"),
    ("modify", 17, ("pmlCpf",), None, True, 502, SCHEMA, "schema"),
    ("add", 21, ("pmlCpf",), None, True, 502, SCHEMA, "schema"),
    ("add", 65, ("pmlCpf",), None, True, 502, SCHEMA, "classe auxiliar"),
    ("modify", 53, ("unicodePwd",), None, False, 503, TLS, "StartTLS"),
    ("modify", 53, ("unicodePwd",), None, True, 502, Codigo.AD_OPERACAO_RECUSADA, "política de senha"),
    ("modify", 8, ("unicodePwd",), None, True, 503, TLS, "StartTLS"),
    ("modify", 13, ("unicodePwd",), None, True, 503, TLS, "StartTLS"),
    ("add", 19, ("sAMAccountName",), "user", True, 409, Codigo.AD_CONFLITO, "sAMAccountName"),
    ("add", 68, (), None, True, 409, Codigo.JA_EXISTE, None),
    ("modify", 32, (), None, True, 404, Codigo.NAO_ENCONTRADO, None),
    ("delete", 66, (), None, True, 409, Codigo.OU_NAO_VAZIA, None),
    ("modify", 1, (), None, True, 502, Codigo.AD_ERRO, "Código LDAP 1"),
]


@pytest.mark.parametrize("operacao,codigo_ldap,atributos,classe,criptografada,status,codigo,trecho", TABELA)
def test_interpretacao_do_erro_do_ad(operacao, codigo_ldap, atributos, classe, criptografada, status, codigo, trecho):
    erro = traduzir_resultado(
        operacao, {"result": codigo_ldap, "description": "d", "message": "MENSAGEM-DO-AD"},
        alvo_mascarado="OU=X", atributos=atributos, classe=classe, criptografada=criptografada,
    )
    assert (erro.status_code, erro.codigo) == (status, codigo)
    if trecho:
        assert trecho in erro.detalhes["providencia"]
    assert "MENSAGEM-DO-AD" not in erro.mensagem + json.dumps(erro.detalhes)


def test_corpo_do_erro_de_dominio():
    app = FastAPI()
    registrar_handlers(app)

    @app.get("/x")
    def x():
        raise ErroAD("negado", codigo=PERM, status_code=502, detalhes={"providencia": "p"})

    r = TestClient(app).get("/x")
    assert r.status_code == 502
    assert r.json() == {"codigo": PERM, "mensagem": "negado", "detalhes": {"providencia": "p"}}


# --- tratar_erros e reverter ----------------------------------------------------------------

def test_tratar_erros():
    @tratar_erros
    def devolve():
        return 1

    @tratar_erros
    def http():
        raise HTTPException(status_code=409, detail="x")

    @tratar_erros
    def ldap():
        raise LDAPException("rede")

    @tratar_erros
    def inesperada():
        raise ValueError("bug")

    assert devolve() == 1
    for funcao, status in ((http, 409), (ldap, 503), (inesperada, 500)):
        with pytest.raises(HTTPException) as e:
            funcao()
        assert e.value.status_code == status


def test_reverter_registra_inconsistencia_so_se_o_desfazer_falhar(caplog):
    reverter(lambda: None, "não aparece")
    assert "INCONSISTENTE" not in caplog.text

    def falha():
        raise ErroAD("negado", codigo=PERM, status_code=502)

    reverter(falha, "não foi possível desfazer")
    assert f"INCONSISTENTE: não foi possível desfazer [{PERM}]" in caplog.text
