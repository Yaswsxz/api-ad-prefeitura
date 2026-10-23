"""Unidades sobre o AD em memória: nenhum acesso ao Active Directory."""
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.audit_service import Acao
from app.core.arvore import (
    HUMANO, NAO_HUMANO, OUS_INTERNAS_DIRETA, Arvore, Categoria, Ramo, dn_arvore, dn_ramo, dn_tipo, dn_unidade,
    dns_da_unidade,
)
from app.core.atributos import DESINCORPORADO, PML_NOME_ORGAO, REINCORPORADO
from app.core.config import settings
from app.core.erros_ad import Codigo, ErroAD
from app.schemas.estrutura import AtoUnidade, OUCreate, OUUpdate
from app.services import estrutura_service as svc
from tests.ad_falso import CTX, erro_ad

OP, INO, DESINC = Arvore.OPERATIVOS, Arvore.INOPERANTES, Arvore.DESINCORPORADOS
ATO = AtoUnidade(instrumento="Decreto 10/2026")


def criar(ad, ramo=Ramo.DIRETA, nome="fazenda", **kw):
    return svc.criar_ou(ramo, OUCreate(nome=nome, **kw), CTX)


def exige(status):
    return pytest.raises(HTTPException, check=lambda e: e.status_code == status)


def apagar_com_filhos(ad, dn):
    """Remove do AD falso o nó e tudo o que há abaixo dele."""
    for chave in [k for k in ad.objs if k == dn.lower() or k.endswith("," + dn.lower())]:
        del ad.objs[chave]


def filhos(ad, dn):
    return [k for k in ad.objs if k.endswith("," + dn.lower())]


# --- criar ------------------------------------------------------------------------

def test_criar_na_direta_cria_os_quatro_lados_com_categorias_so_em_humanos(ad):
    saida = criar(ad, pml_nome_orgao="Secretaria da Fazenda")
    for arvore in (OP, INO):
        for tipo in (HUMANO, NAO_HUMANO):
            unidade = dn_unidade(arvore, Ramo.DIRETA, "FAZENDA", tipo)
            assert unidade.lower() in ad.objs
            assert ad.pml(unidade) == {PML_NOME_ORGAO: "Secretaria da Fazenda"}
        humanos, nao_humanos = dns_da_unidade(arvore, Ramo.DIRETA, "FAZENDA")
        assert sorted(filhos(ad, humanos)) == sorted(f"ou={i},{humanos}".lower() for i in OUS_INTERNAS_DIRETA)
        assert filhos(ad, nao_humanos) == []                       # sem OU NaoHumanos nem categorias
    assert saida.distinguished_name_operativos == dn_unidade(OP, Ramo.DIRETA, "FAZENDA")
    assert saida.distinguished_name_inoperantes == dn_unidade(INO, Ramo.DIRETA, "FAZENDA")
    assert saida.distinguished_name_operativos_nao_humanos == dn_unidade(OP, Ramo.DIRETA, "FAZENDA", NAO_HUMANO)
    assert saida.distinguished_name_inoperantes_nao_humanos == dn_unidade(INO, Ramo.DIRETA, "FAZENDA", NAO_HUMANO)
    assert [(a, alvo) for a, alvo, _ in ad.auditoria] == [(Acao.CRIAR_UNIDADE, "FAZENDA")]


def test_criar_fora_da_direta_nao_tem_ous_internas_em_nenhum_lado(ad):
    criar(ad, Ramo.INDIRETA, "codel")
    for arvore in (OP, INO):
        for dn in dns_da_unidade(arvore, Ramo.INDIRETA, "CODEL"):
            assert dn.lower() in ad.objs and filhos(ad, dn) == []


def test_criar_cria_os_nos_fixos_que_faltarem(ad):
    for tipo in (HUMANO, NAO_HUMANO):
        apagar_com_filhos(ad, dn_tipo(INO, tipo))                  # Inoperantes/<tipo> e seus ramos
    criar(ad, Ramo.PREPOSTO, "cartorio")
    for tipo in (HUMANO, NAO_HUMANO):
        assert dn_tipo(INO, tipo).lower() in ad.objs and dn_ramo(INO, Ramo.PREPOSTO, tipo).lower() in ad.objs
        assert dn_unidade(INO, Ramo.PREPOSTO, "CARTORIO", tipo).lower() in ad.objs


def test_pml_nome_orgao_assume_o_nome_quando_omitido(ad):
    assert criar(ad).pml_nome_orgao == "FAZENDA"


@pytest.mark.parametrize("arvore,ramo", [(OP, Ramo.DIRETA), (INO, Ramo.INDIRETA), (DESINC, Ramo.PREPOSTO)])
def test_nome_em_uso_em_qualquer_ramo_ou_arvore_da_409_sem_escrever(ad, arvore, ramo):
    ad.unidade(arvore, ramo, "FAZENDA")
    with exige(409):
        criar(ad, Ramo.TERCEIRIZADA, "fazenda")
    assert ad.ops == []


def test_arvore_ausente_da_409_sem_escrever(ad):
    del ad.objs[dn_arvore(INO).lower()]
    with exige(409):
        criar(ad)
    assert ad.ops == []


def test_falha_ao_gravar_pml_desfaz_toda_a_criacao(ad):
    antes = ad.instantaneo()
    ad.sem_schema.add(PML_NOME_ORGAO)
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        criar(ad)
    assert ad.instantaneo() == antes
    adds, deletes = [o[1] for o in ad.ops if o[0] == "add"], [o[1] for o in ad.ops if o[0] == "delete"]
    assert deletes == adds[::-1]                      # do mais novo para o mais antigo


@pytest.mark.parametrize("n", [5, 6, 10])
def test_falha_no_meio_da_criacao_desfaz_o_que_foi_criado(ad, n):
    antes = ad.instantaneo()
    # 1-4: unidade Humanos + 3 categorias; 5: unidade NaoHumanos (Operativos); 6-10: o mesmo em Inoperantes
    ad.falhas[("add", n)] = erro_ad()
    with pytest.raises(ErroAD):
        criar(ad)
    assert ad.instantaneo() == antes


def test_se_o_desfazer_falhar_registra_inconsistencia_e_mantem_a_causa(ad, caplog):
    ad.sem_schema.add(PML_NOME_ORGAO)
    ad.falhas[("delete", 1)] = erro_ad()
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        criar(ad)
    assert "INCONSISTENTE" in caplog.text


def test_criar_com_pml_desligado_cria_tudo_sem_pml_e_avisa(ad, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = criar(ad)
    assert ad.pml(dn_unidade(OP, Ramo.DIRETA, "FAZENDA")) == {} and saida.avisos


# --- alterar ------------------------------------------------------------------------

@pytest.fixture
def com_unidade(ad):
    ad.espelhar(Ramo.DIRETA, "FAZENDA", **{PML_NOME_ORGAO: "Antigo"})
    return ad


def alterar(valor="Novo nome"):
    return svc.alterar_ou(Ramo.DIRETA, "FAZENDA", OUUpdate(pml_nome_orgao=valor), CTX)


def lados():
    return [dn for a in (OP, INO) for dn in dns_da_unidade(a, Ramo.DIRETA, "FAZENDA")]


def test_alterar_grava_nos_quatro_lados(com_unidade):
    saida = alterar()
    for dn in lados():
        assert com_unidade.pml(dn) == {PML_NOME_ORGAO: "Novo nome"}
    assert saida.distinguished_name_operativos_nao_humanos == dn_unidade(OP, Ramo.DIRETA, "FAZENDA", NAO_HUMANO)
    assert com_unidade.auditoria[0][0] is Acao.ALTERAR_UNIDADE


@pytest.mark.parametrize("n", [2, 3, 4])
def test_falha_em_um_lado_restaura_os_anteriores(com_unidade, n):
    com_unidade.falhas[("modify", n)] = erro_ad()
    with pytest.raises(ErroAD):
        alterar()
    for dn in lados():
        assert com_unidade.pml(dn) == {PML_NOME_ORGAO: "Antigo"}


def test_falha_no_primeiro_nao_tenta_restaurar(com_unidade):
    com_unidade.falhas[("modify", 1)] = erro_ad()
    with pytest.raises(ErroAD):
        alterar()
    assert com_unidade.ops == []


def test_alterar_exige_a_unidade_em_operativos_e_o_espelho(ad):
    ad.unidade(DESINC, Ramo.DIRETA, "FAZENDA")
    with exige(404):                                  # desincorporada não é alterável
        alterar()
    ad.unidade(OP, Ramo.DIRETA, "FAZENDA")
    with exige(409):                                  # falta o espelho em Inoperantes
        alterar()
    ad.unidade(INO, Ramo.DIRETA, "FAZENDA")
    del ad.objs[dn_unidade(INO, Ramo.DIRETA, "FAZENDA", NAO_HUMANO).lower()]
    with exige(409):                                  # espelho incompleto: falta o lado NaoHumanos
        alterar()


def test_alterar_com_pml_desligado_nao_grava_e_avisa(com_unidade, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    assert alterar().avisos and com_unidade.ops == []


def test_validacao_do_nome_da_unidade():
    for nome in ("A,OU=B", "FAZ*ENDA", "DIRETA", "naohumanos", "x", "x" * 65):
        with pytest.raises(ValidationError):
            OUCreate(nome=nome)
    assert OUCreate(nome="  educação ").nome == "EDUCAÇÃO"


# --- consultar e listar --------------------------------------------------------------------

def test_consultar_mostra_as_arvores_e_prefere_o_valor_de_operativos(com_unidade):
    com_unidade.objs[dn_unidade(INO, Ramo.DIRETA, "FAZENDA").lower()]["attrs"][PML_NOME_ORGAO] = "Outro"
    saida = svc.consultar_unidade(Ramo.DIRETA, " fazenda ")
    assert saida.nome == "FAZENDA" and saida.arvores == [INO, OP]
    assert saida.pml_nome_orgao == "Antigo"
    assert saida.distinguished_names[OP] == dn_unidade(OP, Ramo.DIRETA, "FAZENDA")
    assert saida.distinguished_names_nao_humanos[OP] == dn_unidade(OP, Ramo.DIRETA, "FAZENDA", NAO_HUMANO)


def test_consultar_ramo_errado_ou_inexistente_da_404_e_ou_interna_nao_e_unidade(com_unidade):
    for ramo, nome in ((Ramo.INDIRETA, "FAZENDA"), (Ramo.DIRETA, "NAOEXISTE"), (Ramo.DIRETA, "CARREIRA"),
                       (Ramo.DIRETA, "HUMANOS")):
        with exige(404):
            svc.consultar_unidade(ramo, nome)


def test_listar_ordena_e_pagina(ad):
    for nome in ("CC", "AA", "BB"):
        ad.unidade(OP, Ramo.DIRETA, nome)
    saida = svc.listar_unidades(Ramo.DIRETA, OP, limite=2, deslocamento=1)
    assert (saida.total, [i.nome for i in saida.items]) == (3, ["BB", "CC"])
    assert svc.listar_unidades(Ramo.DIRETA, INO, 10, 0).items == []


# --- desincorporar e reincorporar -----------------------------------------------------

@pytest.fixture
def com_contas(com_unidade):
    com_unidade.conta(OP, Ramo.DIRETA, "FAZENDA", "ana.lima", categoria=Categoria.CARREIRA)
    com_unidade.conta(OP, Ramo.DIRETA, "FAZENDA", "bia.souza", categoria=Categoria.ESTAGIO, uac=514)  # já bloqueada
    com_unidade.conta(OP, Ramo.DIRETA, "FAZENDA", "nhu.sistema.contas")
    com_unidade.ops.clear()
    return com_unidade


def desincorporar():
    return svc.desincorporar_unidade(Ramo.DIRETA, "fazenda", ATO, CTX)


def test_desincorporar_grava_bloqueia_e_move_nessa_ordem(com_contas):
    saida = desincorporar()
    # pml nos dois lados, bloqueio das duas contas habilitadas (uma humana, uma não humana) e os dois moves
    assert com_contas.tipos_de_operacao() == ["modify"] * 4 + ["modify_dn"] * 2
    assert com_contas.atributos_gravados() == [DESINCORPORADO.nomes, DESINCORPORADO.nomes,
                                               ("userAccountControl",), ("userAccountControl",)]
    assert sorted(saida.contas) == ["ana.lima", "nhu.sistema.contas"]          # a já bloqueada não conta
    assert [com_contas.uac(c) for c in ("ana.lima", "bia.souza", "nhu.sistema.contas")] == [514, 514, 514]
    humanos, nao_humanos = dns_da_unidade(DESINC, Ramo.DIRETA, "FAZENDA")
    assert humanos.lower() in com_contas.objs and nao_humanos.lower() in com_contas.objs
    assert com_contas.dn("ana.lima").endswith(humanos) and com_contas.dn("nhu.sistema.contas").endswith(nao_humanos)
    assert (saida.distinguished_name, saida.distinguished_name_nao_humanos) == (humanos, nao_humanos)
    for dn in (humanos, nao_humanos):
        assert com_contas.pml(dn)[DESINCORPORADO.instrumento] == "Decreto 10/2026"
    for dn in dns_da_unidade(OP, Ramo.DIRETA, "FAZENDA"):                         # saiu de Operativos
        assert dn.lower() not in com_contas.objs
    for dn in dns_da_unidade(INO, Ramo.DIRETA, "FAZENDA"):                        # o espelho fica
        assert dn.lower() in com_contas.objs
    assert com_contas.auditoria[0][0] is Acao.DESINCORPORAR_UNIDADE


def test_desincorporar_cria_os_ramos_fixos_se_faltarem(com_contas):
    for tipo in (HUMANO, NAO_HUMANO):
        del com_contas.objs[dn_ramo(DESINC, Ramo.DIRETA, tipo).lower()]
    desincorporar()
    for dn in dns_da_unidade(DESINC, Ramo.DIRETA, "FAZENDA"):
        assert dn.lower() in com_contas.objs


def test_desincorporar_sem_schema_nao_altera_nada(com_contas):
    antes = com_contas.instantaneo()
    com_contas.sem_schema.add(DESINCORPORADO.instrumento)
    with pytest.raises(ErroAD):
        desincorporar()
    assert com_contas.instantaneo() == antes


def test_falha_ao_bloquear_deixa_falha_segura_e_repetir_e_seguro(com_contas, caplog):
    com_contas.falhas[("modify", 4)] = erro_ad()           # pml (2), ana (3), nhu (4: falha)
    with pytest.raises(ErroAD):
        desincorporar()
    assert (com_contas.uac("ana.lima"), com_contas.uac("nhu.sistema.contas")) == (514, 512)
    assert "INCONSISTENTE" in caplog.text
    saida = desincorporar()
    assert saida.contas == ["nhu.sistema.contas"]          # ana já estava bloqueada


def test_falha_ao_mover_mantem_as_contas_bloqueadas(com_contas, caplog):
    com_contas.falhas[("modify_dn", 1)] = erro_ad()
    with pytest.raises(ErroAD):
        desincorporar()
    assert com_contas.uac("ana.lima") == 514 and "INCONSISTENTE" in caplog.text
    for dn in dns_da_unidade(OP, Ramo.DIRETA, "FAZENDA"):
        assert dn.lower() in com_contas.objs


def test_falha_no_segundo_move_devolve_o_primeiro_lado(com_contas, caplog):
    com_contas.falhas[("modify_dn", 2)] = erro_ad()        # o lado Humanos não consegue sair
    with pytest.raises(ErroAD):
        desincorporar()
    for dn in dns_da_unidade(OP, Ramo.DIRETA, "FAZENDA"):  # os dois lados seguem juntos em Operativos
        assert dn.lower() in com_contas.objs
    for dn in dns_da_unidade(DESINC, Ramo.DIRETA, "FAZENDA"):
        assert dn.lower() not in com_contas.objs
    assert "INCONSISTENTE" in caplog.text                  # as contas ficaram bloqueadas (falha segura)
    assert com_contas.dn("nhu.sistema.contas").endswith(dn_unidade(OP, Ramo.DIRETA, "FAZENDA", NAO_HUMANO))


def test_se_o_retorno_do_primeiro_lado_falhar_registra_inconsistencia(com_contas, caplog):
    com_contas.falhas[("modify_dn", 2)] = erro_ad()
    com_contas.falhas[("modify_dn", 3)] = erro_ad()
    with pytest.raises(ErroAD):
        desincorporar()
    assert "o lado NaoHumanos da unidade 'FAZENDA' foi movido" in caplog.text


def test_desincorporar_com_pml_desligado_executa_o_resto_e_avisa(com_contas, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = desincorporar()
    assert com_contas.tipos_de_operacao() == ["modify", "modify", "modify_dn", "modify_dn"] and saida.avisos


def test_desincorporar_exige_operativos_e_destino_livre(com_contas):
    with exige(404):
        svc.desincorporar_unidade(Ramo.DIRETA, "NAOEXISTE", ATO, CTX)
    com_contas.unidade(DESINC, Ramo.DIRETA, "FAZENDA")
    com_contas.ops.clear()
    with exige(409):
        desincorporar()
    assert com_contas.ops == []


def test_desincorporar_unidade_sem_o_lado_nao_humanos_da_409_sem_escrever(com_contas):
    del com_contas.objs[dn_unidade(OP, Ramo.DIRETA, "FAZENDA", NAO_HUMANO).lower()]
    com_contas.ops.clear()
    with exige(409):
        desincorporar()
    assert com_contas.ops == []


def reincorporar():
    return svc.reincorporar_unidade(Ramo.DIRETA, "fazenda", ATO, CTX)


def test_ciclo_desincorporar_e_reincorporar_desbloqueia_todas_as_contas(com_contas):
    desincorporar()
    com_contas.ops.clear()
    saida = reincorporar()
    assert com_contas.tipos_de_operacao() == ["modify", "modify", "modify_dn", "modify_dn", "modify", "modify", "modify"]
    assert com_contas.atributos_gravados()[:2] == [REINCORPORADO.nomes, REINCORPORADO.nomes]
    assert sorted(saida.contas) == ["ana.lima", "bia.souza", "nhu.sistema.contas"]   # inclusive a que já estava bloqueada
    assert {com_contas.uac(c) for c in ("ana.lima", "bia.souza", "nhu.sistema.contas")} == {512}
    humanos, nao_humanos = dns_da_unidade(OP, Ramo.DIRETA, "FAZENDA")
    assert (saida.distinguished_name, saida.distinguished_name_nao_humanos) == (humanos, nao_humanos)
    assert com_contas.dn("ana.lima").endswith(humanos) and com_contas.dn("nhu.sistema.contas").endswith(nao_humanos)
    for dn in dns_da_unidade(DESINC, Ramo.DIRETA, "FAZENDA"):
        assert dn.lower() not in com_contas.objs
    assert com_contas.auditoria[-1][0] is Acao.REINCORPORAR_UNIDADE


def test_reincorporar_exige_desincorporada_e_destino_livre(com_contas):
    with exige(404):                                       # ainda está em Operativos
        reincorporar()
    desincorporar()
    com_contas.unidade(OP, Ramo.DIRETA, "FAZENDA")
    with exige(409):                                       # o nome já existe em Operativos
        reincorporar()


def test_reincorporar_cria_os_ramos_de_operativos_se_faltarem(com_contas):
    desincorporar()
    for tipo in (HUMANO, NAO_HUMANO):
        del com_contas.objs[dn_ramo(OP, Ramo.DIRETA, tipo).lower()]
    reincorporar()
    for dn in dns_da_unidade(OP, Ramo.DIRETA, "FAZENDA"):
        assert dn.lower() in com_contas.objs


def test_reincorporar_falha_no_meio_do_desbloqueio_registra_inconsistencia(com_contas, caplog):
    desincorporar()                                        # 4 modify: pml (2) e as duas contas
    com_contas.falhas[("modify", 8)] = erro_ad()           # reincorporar: pml (5, 6), 1ª conta (7), 2ª conta (8)
    with pytest.raises(ErroAD):
        reincorporar()
    assert "INCONSISTENTE" in caplog.text
    assert dn_unidade(OP, Ramo.DIRETA, "FAZENDA").lower() in com_contas.objs     # a unidade já voltou
