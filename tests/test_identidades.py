"""Identidades: validação, criar, alterar, bloquear, remover, consultar e listar."""
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.audit_service import Acao
from app.core.arvore import Arvore, Categoria, Ramo, TipoIdentidade, dn_container, rdn_cn
from app.core.atributos import PML_CPF, PML_NAO_HUMANO_TIPO
from app.core.config import settings
from app.core.erros_ad import Codigo, ErroAD
from app.schemas.identidade import HumanoCreate, NaoHumanoCreate
from app.services import identidade_service as svc
from tests.ad_falso import CTX

OP, INO = Arvore.OPERATIVOS, Arvore.INOPERANTES
HUMANO, NAO_HUMANO = TipoIdentidade.HUMANO, TipoIdentidade.NAO_HUMANO


def exige(status):
    return pytest.raises(HTTPException, check=lambda e: e.status_code == status)


def humano(**kw) -> HumanoCreate:
    base = dict(ramo=Ramo.DIRETA, unidade="fazenda", categoria=Categoria.CARREIRA, login="joao.silva",
                nome_completo="Joao Silva", cpf="12345678901")
    return HumanoCreate(**{**base, **kw})


def nao_humano(**kw) -> NaoHumanoCreate:
    base = dict(ramo=Ramo.DIRETA, unidade="fazenda", login="nhu.robo.dois", nome="robodois",
                pml_nao_humano_tipo="bot")
    return NaoHumanoCreate(**{**base, **kw})


# --- validação de entrada (sem AD) ----------------------------------------------------------

def test_categoria_obrigatoria_na_direta_e_proibida_fora():
    with pytest.raises(ValidationError):
        humano(categoria=None)
    with pytest.raises(ValidationError):
        humano(ramo=Ramo.INDIRETA)
    assert humano(ramo=Ramo.INDIRETA, categoria=None).categoria is None


@pytest.mark.parametrize("login", ["Joao.Silva", "joao", "joao.silva.x", "j.silva", "joao_silva", "joao.silvaaaaaaaaaaaaaa"])
def test_login_humano_invalido(login):
    with pytest.raises(ValidationError):
        humano(login=login)


def test_login_humano_aceita_ate_o_limite_do_ad():
    assert humano(login="joaopedro.silvasanta").login == "joaopedro.silvasanta"      # 20 caracteres


@pytest.mark.parametrize("nome", ["joao silva", "Joao", "Jo", "Joao  Silva", "JOAO SILVA", "Joao 3ilva"])
def test_nome_humano_invalido(nome):
    with pytest.raises(ValidationError):
        humano(nome_completo=nome)


@pytest.mark.parametrize("nome", ["João da Silva", "Maria Conceição de Souza", "Ana Lima", "André Souza"])
def test_nome_humano_com_acento_e_particula(nome):
    assert humano(nome_completo=nome).nome_completo == nome


@pytest.mark.parametrize("login,nome", [
    ("sistema.contas", "sistemacontas"), ("nhu.sistema", "sistemacontas"),
    ("nhu.sistema.contas", "Sistema"), ("nhu.sistema.contas", "abc"),
])
def test_nao_humano_invalido(login, nome):
    with pytest.raises(ValidationError):
        nao_humano(login=login, nome=nome)


@pytest.mark.parametrize("unidade", ["direta", "OPERATIVOS", "estagio", "NaoHumanos", "A,OU=B"])
def test_unidade_reservada_ou_com_caractere_de_dn_e_recusada(unidade):
    with pytest.raises(ValidationError):
        humano(unidade=unidade)


# --- criar --------------------------------------------------------------------------------

def test_criar_humano_na_direta_nasce_bloqueado_em_inoperantes_sem_senha(ativos):
    saida = svc.criar_humano(humano(), CTX)
    container = dn_container(INO, Ramo.DIRETA, "FAZENDA", Categoria.CARREIRA)
    assert saida.distinguished_name == f"{rdn_cn('Joao Silva')},{container}"
    assert (saida.arvore, saida.bloqueada, saida.categoria, saida.tipo) == (INO, True, Categoria.CARREIRA, HUMANO)
    conta = ativos.da("joao.silva")
    assert conta["attrs"]["userAccountControl"] == 514 and "senha" not in conta
    assert conta["attrs"]["userPrincipalName"] == f"joao.silva@{settings.AD_UPN_SUFIXO}"
    assert ativos.pml(saida.distinguished_name) == {PML_CPF: "12345678901"}
    assert ativos.auditoria[0][:2] == (Acao.CRIAR_HUMANO, "joao.silva")


def test_criar_fora_da_direta_fica_direto_na_unidade(ativos):
    saida = svc.criar_humano(humano(ramo=Ramo.INDIRETA, unidade="codel", categoria=None, login="eva.nunes"), CTX)
    assert saida.distinguished_name.startswith("CN=Joao Silva,OU=CODEL,OU=Indireta,OU=Humanos,OU=Inoperantes,")
    assert saida.categoria is None


@pytest.mark.parametrize("login", ["ana.lima", "caio.rocha"])
def test_login_existente_em_qualquer_arvore_da_409(ativos, login):
    with exige(409):
        svc.criar_humano(humano(login=login), CTX)
    assert ativos.ops == []


def test_criar_exige_a_unidade_e_a_ou_interna(ativos):
    with exige(404):
        svc.criar_humano(humano(unidade="naoexiste"), CTX)
    del ativos.objs[dn_container(INO, Ramo.DIRETA, "FAZENDA", Categoria.CARREIRA).lower()]
    with exige(409):
        svc.criar_humano(humano(), CTX)
    assert ativos.ops == []


def test_falha_ao_gravar_pml_desfaz_a_criacao_da_conta(ativos):
    antes = ativos.instantaneo()
    ativos.sem_schema.add(PML_CPF)
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        svc.criar_humano(humano(), CTX)
    assert ativos.instantaneo() == antes


def test_criar_com_pml_desligado_nao_grava_e_avisa(ativos, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = svc.criar_humano(humano(), CTX)
    assert saida.avisos and saida.atributos_pml == {} and ativos.pml(saida.distinguished_name) == {}


def test_criar_sem_cpf_nao_grava_pml(ativos):
    svc.criar_humano(humano(cpf=None), CTX)
    assert ativos.atributos_gravados() == []


def test_criar_nao_humano_vai_para_naohumanos_com_o_tipo(ativos):
    saida = svc.criar_nao_humano(nao_humano(), CTX)
    container = dn_container(INO, Ramo.DIRETA, "FAZENDA", None, NAO_HUMANO)
    assert saida.distinguished_name == f"CN=robodois,{container}"
    assert container.startswith("OU=FAZENDA,OU=Direta,OU=NaoHumanos,OU=Inoperantes,")     # direto na unidade, sem OU interna
    assert (saida.tipo, saida.categoria, saida.bloqueada) == (NAO_HUMANO, None, True)
    assert ativos.pml(saida.distinguished_name) == {PML_NAO_HUMANO_TIPO: "bot"}
    assert ativos.auditoria[0][0] is Acao.CRIAR_NAO_HUMANO


def test_criar_nao_humano_fora_da_direta_e_tipo_fora_do_arquivo_de_regras(ativos):
    saida = svc.criar_nao_humano(nao_humano(ramo=Ramo.INDIRETA, unidade="codel"), CTX)
    assert saida.distinguished_name.startswith("CN=robodois,OU=CODEL,OU=Indireta,OU=NaoHumanos,OU=Inoperantes,")
    with exige(422):
        svc.criar_nao_humano(nao_humano(login="nhu.outro.bot", nome="outrobot", pml_nao_humano_tipo="inexistente"), CTX)


# --- alterar ------------------------------------------------------------------------------------

def test_alterar_grava_so_o_que_o_arquivo_de_regras_permite(ativos):
    saida = svc.alterar("ana.lima", HUMANO, {PML_CPF: "999"}, CTX)
    assert ativos.pml(ativos.dn("ana.lima")) == {PML_CPF: "999"} and saida.atributos_pml == {PML_CPF: "999"}
    assert ativos.auditoria[-1][0] is Acao.ALTERAR_IDENTIDADE


def test_alterar_com_null_limpa_o_atributo(ativos):
    saida = svc.alterar("ana.lima", HUMANO, {PML_CPF: None}, CTX)
    assert ativos.pml(ativos.dn("ana.lima")) == {} and saida.atributos_pml == {}


@pytest.mark.parametrize("campos", [
    {"userAccountControl": "512"}, {"sAMAccountName": "x.y"}, {PML_CPF: "1", "mail": "a@b"}, {},
    {PML_NAO_HUMANO_TIPO: "bot"},                      # atributo de não humano num humano
])
def test_alterar_recusa_atributos_fora_da_lista_e_corpo_vazio(ativos, campos):
    with exige(422):
        svc.alterar("ana.lima", HUMANO, campos, CTX)
    assert ativos.ops == []


def test_alterar_recusa_valor_longo(ativos):
    with exige(422):
        svc.alterar("ana.lima", HUMANO, {PML_CPF: "x" * 256}, CTX)


def test_alterar_so_em_operativos_e_pelo_tipo_certo(ativos):
    with exige(409):
        svc.alterar("caio.rocha", HUMANO, {PML_CPF: "1"}, CTX)
    with exige(404):
        svc.alterar("nhu.sistema.contas", HUMANO, {PML_CPF: "1"}, CTX)
    assert ativos.ops == []


def test_alterar_tipo_do_nao_humano_valida_o_enum(ativos):
    with exige(422):
        svc.alterar("nhu.sistema.contas", NAO_HUMANO, {PML_NAO_HUMANO_TIPO: "inexistente"}, CTX)
    saida = svc.alterar("nhu.sistema.contas", NAO_HUMANO, {PML_NAO_HUMANO_TIPO: "impressora"}, CTX)
    assert saida.atributos_pml == {PML_NAO_HUMANO_TIPO: "impressora"}


def test_alterar_com_pml_desligado_nao_grava_e_avisa(ativos, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = svc.alterar("ana.lima", HUMANO, {PML_CPF: "999"}, CTX)
    assert saida.avisos and ativos.ops == [] and saida.atributos_pml == {PML_CPF: "1"}


# --- bloquear e desbloquear no lugar -------------------------------------------------------------

def test_bloquear_nao_move_a_conta_e_preserva_as_flags(ativos):
    dn = ativos.dn("ana.lima")
    saida = svc.bloquear("ana.lima", HUMANO, CTX)
    assert ativos.uac("ana.lima") == 514 and saida.bloqueada and ativos.dn("ana.lima") == dn
    assert ativos.tipos_de_operacao() == ["modify"]
    assert ativos.auditoria[-1][0] is Acao.BLOQUEAR_IDENTIDADE


def test_desbloquear_preserva_as_demais_flags(ativos):
    saida = svc.desbloquear("bia.souza", HUMANO, CTX)
    assert ativos.uac("bia.souza") == 66048 and not saida.bloqueada            # só o bit de bloqueio sai
    assert ativos.auditoria[-1][0] is Acao.DESBLOQUEAR_IDENTIDADE


def test_bloqueio_repetido_da_409(ativos):
    with exige(409):
        svc.bloquear("bia.souza", HUMANO, CTX)
    with exige(409):
        svc.desbloquear("ana.lima", HUMANO, CTX)


@pytest.mark.parametrize("acao", [svc.bloquear, svc.desbloquear])
def test_bloqueio_so_vale_em_operativos(ativos, acao):
    with exige(409):
        acao("caio.rocha", HUMANO, CTX)


def test_bloquear_nao_humano(ativos):
    svc.bloquear("nhu.sistema.contas", NAO_HUMANO, CTX)
    assert ativos.uac("nhu.sistema.contas") == 514


# --- remover ------------------------------------------------------------------------------------------------

def test_remover_so_em_inoperantes_e_audita_o_motivo(ativos):
    with exige(409):
        svc.remover("ana.lima", HUMANO, "duplicada", CTX)
    svc.remover("caio.rocha", HUMANO, "inclusão indevida", CTX)
    assert ativos.da("caio.rocha") is None
    acao, alvo, detalhes = ativos.auditoria[-1]
    assert (acao, alvo, detalhes["motivo"]) == (Acao.REMOVER_IDENTIDADE, "caio.rocha", "inclusão indevida")


# --- consultar e listar ------------------------------------------------------------------------------------------

def test_consultar_devolve_local_estado_e_atributos(ativos):
    saida = svc.consultar("ana.lima", HUMANO)
    assert (saida.arvore, saida.ramo, saida.unidade, saida.categoria) == (OP, Ramo.DIRETA, "FAZENDA", Categoria.CARREIRA)
    assert saida.atributos_pml == {PML_CPF: "1"} and not saida.bloqueada
    assert svc.consultar("bia.souza", HUMANO).bloqueada
    assert svc.consultar("duda.reis", HUMANO).categoria is None


def test_consultar_com_tipo_trocado_ou_inexistente_da_404(ativos):
    for login, tipo in (("nhu.sistema.contas", HUMANO), ("ana.lima", NAO_HUMANO), ("ninguem.aqui", HUMANO)):
        with exige(404):
            svc.consultar(login, tipo)


def test_filtro_de_busca_e_escapado(ativos):
    with exige(404):
        svc.consultar("a*)(uid=*", HUMANO)
    enviado = next(f for f in ativos.filtros if "sAMAccountName=" in f)
    assert "\\2a" in enviado and "\\29" in enviado and "*)(" not in enviado


def lista(tipo=HUMANO, arvore=OP, ramo=None, unidade=None, categoria=None, bloqueada=None, limite=100, deslocamento=0):
    return svc.listar(tipo, arvore, ramo, unidade, categoria, bloqueada, limite, deslocamento)


def logins(saida):
    return [i.login for i in saida.items]


def test_listar_filtra_por_arvore_tipo_categoria_e_bloqueio(ativos):
    assert logins(lista()) == ["ana.lima", "bia.souza", "duda.reis"]
    assert logins(lista(arvore=INO)) == ["caio.rocha"]
    assert logins(lista(tipo=NAO_HUMANO)) == ["nhu.sistema.contas"]
    assert logins(lista(categoria=Categoria.ESTAGIO)) == ["bia.souza"]
    assert logins(lista(bloqueada=True)) == ["bia.souza"]
    assert logins(lista(ramo=Ramo.INDIRETA)) == ["duda.reis"]
    assert logins(lista(ramo=Ramo.DIRETA, unidade="educacao")) == []


def test_listar_pagina_e_valida_filtros(ativos):
    saida = lista(limite=1, deslocamento=1)
    assert (saida.total, logins(saida)) == (3, ["bia.souza"])
    with exige(422):
        lista(unidade="FAZENDA")                         # unidade exige ramo
    with exige(422):
        lista(ramo=Ramo.INDIRETA, categoria=Categoria.ESTAGIO)


# --- isolamento entre humanos e não humanos -------------------------------------------------

def test_bases_de_humanos_e_de_nao_humanos_sao_isoladas(ativos):
    ativos.conta(OP, Ramo.INDIRETA, "CODEL", "nhu.fila.codel", nome="filacodel", pmlNaoHumanoTipo="bot")
    ativos.conta(INO, Ramo.DIRETA, "FAZENDA", "nhu.fila.fazenda", nome="filafazenda", uac=514)
    for chave, objeto in ativos.objs.items():
        if objeto["classe"] != "user":
            continue
        nao_humano = objeto["attrs"]["sAMAccountName"].startswith("nhu.")
        assert ("ou=naohumanos," in chave) is nao_humano and ("ou=humanos," in chave) is not nao_humano
    # a listagem usa a base do tipo: nunca mistura
    assert logins(lista(tipo=HUMANO, ramo=Ramo.INDIRETA)) == ["duda.reis"]
    assert logins(lista(tipo=NAO_HUMANO, ramo=Ramo.INDIRETA)) == ["nhu.fila.codel"]
    assert logins(lista(tipo=NAO_HUMANO, arvore=INO)) == ["nhu.fila.fazenda"]
    assert "nhu.sistema.contas" not in logins(lista(tipo=HUMANO)) and "ana.lima" not in logins(lista(tipo=NAO_HUMANO))
    # a conta é achada pelo login só com o tipo certo
    assert svc.consultar("nhu.fila.codel", NAO_HUMANO).tipo is NAO_HUMANO
    with exige(404):
        svc.consultar("nhu.fila.codel", HUMANO)


def test_nao_humano_da_direta_nao_tem_categoria_e_o_filtro_de_categoria_so_vale_para_humanos(ativos):
    assert logins(lista(tipo=NAO_HUMANO, ramo=Ramo.DIRETA, unidade="fazenda")) == ["nhu.sistema.contas"]
    assert logins(lista(tipo=NAO_HUMANO, categoria=Categoria.CARREIRA)) == []
    assert svc.consultar("nhu.sistema.contas", NAO_HUMANO).categoria is None
