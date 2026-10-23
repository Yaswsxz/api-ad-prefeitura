"""Destituir, ativar e transferir sobre o AD em memória."""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app.main as principal
from app.audit_service import Acao
from app.core.arvore import Arvore, Categoria, Ramo, TipoIdentidade, dn_container, dn_unidade
from app.core.atributos import ATIVADO, DESTITUIDO, TRANSFERIDO, PML_CPF
from app.core.config import settings
from app.core.erros_ad import Codigo, ErroAD
from app.schemas.estrutura import AtoUnidade
from app.schemas.identidade import (
    AtivacaoOut, AtivarHumano, AtivarNaoHumano, RedefinirSenha, SenhaRedefinidaOut,
    TransferirHumano, TransferirNaoHumano,
)
from app.services import identidade_ciclo as ciclo
from tests.ad_falso import CTX, erro_ad
from tests.conftest import SEGREDO_DE_TESTE

OP, INO, DESINC = Arvore.OPERATIVOS, Arvore.INOPERANTES, Arvore.DESINCORPORADOS
HUMANO, NAO_HUMANO = TipoIdentidade.HUMANO, TipoIdentidade.NAO_HUMANO
ATO = AtoUnidade(instrumento="Portaria 10/2026")


def exige(status):
    return pytest.raises(HTTPException, check=lambda e: e.status_code == status)


def container(arvore, ramo=Ramo.DIRETA, unidade="FAZENDA", categoria=Categoria.CARREIRA):
    return dn_container(arvore, ramo, unidade, categoria)


def seed_desincorporada(ad):
    """Unidade ANTIGA: só no espelho de Inoperantes e em Desincorporados (não existe em Operativos)."""
    ad.unidade(INO, Ramo.DIRETA, "ANTIGA")
    ad.unidade(DESINC, Ramo.DIRETA, "ANTIGA")


# =============================================================================
# Destituir
# =============================================================================

def test_destituir_grava_bloqueia_e_move_para_a_mesma_ou_em_inoperantes(ativos):
    saida = ciclo.destituir("ana.lima", HUMANO, ATO, CTX)
    assert ativos.tipos_de_operacao() == ["modify", "modify", "modify_dn"]
    assert ativos.atributos_gravados() == [DESTITUIDO.nomes, ("userAccountControl",)]
    assert saida.distinguished_name == f"CN=ana.lima,{container(INO)}"
    assert (saida.arvore, saida.bloqueada, saida.categoria) == (INO, True, Categoria.CARREIRA)
    assert ativos.uac("ana.lima") == 514
    assert saida.atributos_pml[DESTITUIDO.instrumento] == "Portaria 10/2026"
    acao, alvo, detalhes = ativos.auditoria[-1]
    assert (acao, detalhes["arvore_anterior"]) == (Acao.DESTITUIR_IDENTIDADE, "Operativos")


def test_destituir_conta_ja_bloqueada_nao_regrava_o_uac(ativos):
    ciclo.destituir("bia.souza", HUMANO, ATO, CTX)
    assert ativos.atributos_gravados() == [DESTITUIDO.nomes] and ativos.uac("bia.souza") == 66050


def test_destituir_preserva_o_lugar_de_nao_humano_e_de_outro_ramo(ativos):
    nao_humano = ciclo.destituir("nhu.sistema.contas", NAO_HUMANO, ATO, CTX)
    assert nao_humano.distinguished_name == f"CN=sistemacontas,{dn_container(INO, Ramo.DIRETA, 'FAZENDA', None, NAO_HUMANO)}"
    assert "OU=NaoHumanos,OU=Inoperantes," in nao_humano.distinguished_name
    indireta = ciclo.destituir("duda.reis", HUMANO, ATO, CTX)
    assert indireta.distinguished_name == f"CN=duda.reis,{dn_container(INO, Ramo.INDIRETA, 'CODEL')}"


def test_destituir_conta_de_unidade_desincorporada_vai_para_o_espelho(ativos):
    seed_desincorporada(ativos)
    ativos.conta(DESINC, Ramo.DIRETA, "ANTIGA", "edu.dias", categoria=Categoria.CARREIRA, uac=514)
    saida = ciclo.destituir("edu.dias", HUMANO, ATO, CTX)
    assert saida.distinguished_name == f"CN=edu.dias,{container(INO, unidade='ANTIGA')}" and saida.arvore == INO


def test_destituir_quem_ja_esta_em_inoperantes_da_409(ativos):
    with exige(409):
        ciclo.destituir("caio.rocha", HUMANO, ATO, CTX)
    assert ativos.ops == []


def test_destituir_com_destino_ausente_nao_altera_nada(ativos):
    del ativos.objs[container(INO).lower()]
    with exige(409):
        ciclo.destituir("ana.lima", HUMANO, ATO, CTX)
    assert ativos.ops == []


def test_destituir_sem_schema_nao_altera_nada(ativos):
    ativos.sem_schema.add(DESTITUIDO.instrumento)
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        ciclo.destituir("ana.lima", HUMANO, ATO, CTX)
    assert ativos.ops == [] and ativos.uac("ana.lima") == 512


def test_destituir_com_pml_desligado_executa_o_resto_e_avisa(ativos, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = ciclo.destituir("ana.lima", HUMANO, ATO, CTX)
    assert ativos.tipos_de_operacao() == ["modify", "modify_dn"] and saida.avisos


def test_destituir_falha_ao_mover_mantem_a_conta_bloqueada_e_pode_repetir(ativos, caplog):
    original = ativos.dn("ana.lima")
    ativos.falhas[("modify_dn", 1)] = erro_ad()
    with pytest.raises(ErroAD):
        ciclo.destituir("ana.lima", HUMANO, ATO, CTX)
    assert ativos.uac("ana.lima") == 514 and ativos.dn("ana.lima") == original and "INCONSISTENTE" in caplog.text
    assert ciclo.destituir("ana.lima", HUMANO, ATO, CTX).arvore == INO


# =============================================================================
# Ativar
# =============================================================================

def ativar(**kw) -> AtivarHumano:
    return AtivarHumano(instrumento="Portaria 30/2026", **kw)


def test_ativar_define_senha_grava_move_e_habilita_nesta_ordem(ativos):
    saida = ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.tipos_de_operacao() == ["modify", "modify", "modify_dn", "modify"]
    assert ativos.atributos_gravados() == [("unicodePwd", "pwdLastSet"), ATIVADO.nomes, ("userAccountControl",)]
    assert saida.distinguished_name == f"CN=caio.rocha,{container(OP)}"
    assert (saida.arvore, saida.bloqueada, saida.categoria) == (OP, False, Categoria.CARREIRA)
    assert ativos.uac("caio.rocha") == 512
    assert saida.senha_inicial == ativos.da("caio.rocha")["senha"] and len(saida.senha_inicial) == 12
    assert saida.atributos_pml[ATIVADO.instrumento] == "Portaria 30/2026"
    acao, _, detalhes = ativos.auditoria[-1]
    assert acao is Acao.ATIVAR_IDENTIDADE and detalhes["troca_obrigatoria"] is True and detalhes["tamanho_senha"] == 12


def test_ativar_humano_exige_a_troca_da_senha_no_proximo_logon(ativos):
    ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.da("caio.rocha")["attrs"]["pwdLastSet"] == 0


def test_ativar_com_tamanho_de_senha_informado(ativos):
    saida = ciclo.ativar_humano("caio.rocha", ativar(tamanho_senha=24), CTX)
    assert len(saida.senha_inicial) == 24 and ativos.auditoria[-1][2]["tamanho_senha"] == 24


def test_ativar_humano_com_senha_sem_expiracao_de_fora_da_api_nao_forca_a_troca(ativos):
    # o AD recusa pwdLastSet=0 junto com "senha não expira"; a flag posta por fora é respeitada
    ativos.conta(INO, Ramo.DIRETA, "FAZENDA", "gil.paes", categoria=Categoria.CARREIRA, uac=514 | 65536)
    ciclo.ativar_humano("gil.paes", ativar(), CTX)
    assert ativos.atributos_gravados()[0] == ("unicodePwd",) and "pwdLastSet" not in ativos.da("gil.paes")["attrs"]
    assert ativos.auditoria[-1][2]["troca_obrigatoria"] is False


def test_ativar_preserva_as_flags_e_limpa_o_passwd_notreqd(ativos):
    # bloqueada (2) + PASSWD_NOTREQD (32) + senha não expira (65536) + conta normal (512)
    ativos.conta(INO, Ramo.DIRETA, "FAZENDA", "eli.cruz", categoria=Categoria.ESTAGIO, uac=2 | 32 | 65536 | 512)
    ciclo.ativar_humano("eli.cruz", ativar(), CTX)
    assert ativos.uac("eli.cruz") == 65536 | 512


def test_ativar_nunca_registra_a_senha(ativos, caplog):
    saida = ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert saida.senha_inicial not in caplog.text and saida.senha_inicial not in repr(ativos.auditoria)


def test_ativar_com_destino_informado(ativos):
    saida = ciclo.ativar_humano("caio.rocha", ativar(
        ramo_destino=Ramo.DIRETA, unidade_destino="educacao", categoria_destino=Categoria.COMISSIONADO), CTX)
    assert saida.distinguished_name == f"CN=caio.rocha,{container(OP, unidade='EDUCACAO', categoria=Categoria.COMISSIONADO)}"
    assert (saida.unidade, saida.categoria) == ("EDUCACAO", Categoria.COMISSIONADO)


def test_ativar_unidade_de_origem_desincorporada_exige_destino(ativos):
    seed_desincorporada(ativos)
    ativos.conta(INO, Ramo.DIRETA, "ANTIGA", "fabio.melo", categoria=Categoria.CARREIRA, uac=514)
    ativos.ops.clear()
    with exige(422):
        ciclo.ativar_humano("fabio.melo", ativar(), CTX)
    assert ativos.ops == []
    saida = ciclo.ativar_humano("fabio.melo", ativar(
        ramo_destino=Ramo.DIRETA, unidade_destino="fazenda", categoria_destino=Categoria.CARREIRA), CTX)
    assert (saida.unidade, saida.arvore) == ("FAZENDA", OP)


def test_ativar_nao_humano_vai_para_naohumanos(ativos):
    ativos.conta(INO, Ramo.DIRETA, "FAZENDA", "nhu.robo.um", nome="robozinho", uac=514, pmlNaoHumanoTipo="bot")
    saida = ciclo.ativar_nao_humano("nhu.robo.um", AtivarNaoHumano(instrumento="Portaria 30/2026"), CTX)
    assert saida.distinguished_name == f"CN=robozinho,{dn_container(OP, Ramo.DIRETA, 'FAZENDA', None, NAO_HUMANO)}"
    assert "OU=NaoHumanos,OU=Operativos," in saida.distinguished_name
    assert saida.categoria is None and saida.senha_inicial


def test_ativar_nao_humano_nao_troca_a_senha_e_ela_nao_expira(ativos):
    ativos.conta(INO, Ramo.DIRETA, "FAZENDA", "nhu.robo.um", nome="robozinho", uac=514)
    ciclo.ativar_nao_humano("nhu.robo.um", AtivarNaoHumano(instrumento="Portaria 30/2026"), CTX)
    assert ativos.atributos_gravados()[0] == ("unicodePwd",) and "pwdLastSet" not in ativos.da("nhu.robo.um")["attrs"]
    assert ativos.uac("nhu.robo.um") == 512 | 65536
    assert ativos.auditoria[-1][2]["troca_obrigatoria"] is False


def test_ativar_so_a_partir_de_inoperantes(ativos):
    with exige(409):
        ciclo.ativar_humano("ana.lima", ativar(), CTX)
    assert ativos.ops == []


def test_ativar_destino_inexistente_ou_com_ou_interna_ausente_nao_altera_nada(ativos):
    with exige(404):
        ciclo.ativar_humano("caio.rocha", ativar(
            ramo_destino=Ramo.DIRETA, unidade_destino="naoexiste", categoria_destino=Categoria.CARREIRA), CTX)
    del ativos.objs[container(OP).lower()]
    with exige(409):
        ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.ops == []


def test_ativar_sem_tls_nao_altera_nada(ativos):
    original = ativos.dn("caio.rocha")
    ativos.sem_tls = True
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_TLS_INDISPONIVEL):
        ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.ops == [] and ativos.uac("caio.rocha") == 514 and ativos.dn("caio.rocha") == original


def test_ativar_sem_schema_deixa_a_conta_bloqueada_em_inoperantes(ativos):
    original = ativos.dn("caio.rocha")
    ativos.sem_schema.add(ATIVADO.instrumento)
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.uac("caio.rocha") == 514 and ativos.dn("caio.rocha") == original
    assert "modify_dn" not in ativos.tipos_de_operacao()


def test_ativar_falha_ao_habilitar_devolve_a_conta_bloqueada_a_inoperantes(ativos):
    original = ativos.dn("caio.rocha")
    ativos.falhas[("modify", 3)] = erro_ad()                # senha (1), pml (2), UAC (3)
    with pytest.raises(ErroAD):
        ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.uac("caio.rocha") == 514 and ativos.dn("caio.rocha") == original


def test_ativar_se_o_desfazer_falhar_registra_inconsistencia(ativos, caplog):
    ativos.falhas[("modify", 3)] = erro_ad()
    ativos.falhas[("modify_dn", 2)] = erro_ad()
    with pytest.raises(ErroAD):
        ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert "INCONSISTENTE" in caplog.text and ativos.uac("caio.rocha") == 514      # segue bloqueada


def test_ativar_com_pml_desligado_executa_o_resto_e_avisa(ativos, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = ciclo.ativar_humano("caio.rocha", ativar(), CTX)
    assert ativos.atributos_gravados() == [("unicodePwd", "pwdLastSet"), ("userAccountControl",)]
    assert saida.avisos and saida.senha_inicial


def test_ativar_valida_o_destino_no_corpo():
    for invalido in (
        dict(ramo_destino=Ramo.DIRETA),                                                    # falta a unidade
        dict(unidade_destino="fazenda"),                                                   # falta o ramo
        dict(ramo_destino=Ramo.DIRETA, unidade_destino="fazenda"),                         # falta a categoria
        dict(ramo_destino=Ramo.INDIRETA, unidade_destino="codel", categoria_destino=Categoria.ESTAGIO),
        dict(categoria_destino=Categoria.ESTAGIO),                                         # categoria sem destino
    ):
        with pytest.raises(ValidationError):
            ativar(**invalido)
    assert ativar(ramo_destino=Ramo.INDIRETA, unidade_destino="codel").unidade_destino == "CODEL"
    assert ativar().ramo_destino is None


def test_tamanho_da_senha_fica_entre_8_e_64_e_o_padrao_e_12():
    assert ativar().tamanho_senha == 12 and RedefinirSenha(motivo="Senha perdida").tamanho_senha == 12
    for ok in (8, 64):
        assert ativar(tamanho_senha=ok).tamanho_senha == ok
    for invalido in (7, 65, 0, -1):
        with pytest.raises(ValidationError):
            ativar(tamanho_senha=invalido)
        with pytest.raises(ValidationError):
            AtivarNaoHumano(instrumento="Portaria 30/2026", tamanho_senha=invalido)
        with pytest.raises(ValidationError):
            RedefinirSenha(motivo="Senha perdida", tamanho_senha=invalido)


def test_rota_de_ativar_devolve_a_senha_sem_cache(monkeypatch):
    def falso(login, dados, ctx):
        return AtivacaoOut(login=login, nome="X", tipo=HUMANO, ramo=Ramo.DIRETA, unidade="FAZENDA",
                           categoria=Categoria.CARREIRA, arvore=OP, bloqueada=False,
                           distinguished_name="CN=X", senha_inicial="Senha#Unica1")
    monkeypatch.setattr(ciclo, "ativar_humano", falso)
    client = TestClient(principal.app)
    token = client.post("/auth/token", json={"client_id": "cliente-de-teste",
                                             "client_secret": SEGREDO_DE_TESTE}).json()["access_token"]
    r = client.post("/identidade/humanos/caio.rocha/ativar", json={"instrumento": "Portaria 30/2026"},
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200 and r.json()["senha_inicial"] == "Senha#Unica1"
    assert r.headers["cache-control"] == "no-store" and r.json()["ramo"] == "direta"


# =============================================================================
# Redefinir senha
# =============================================================================

def redefinir(**kw) -> RedefinirSenha:
    return RedefinirSenha(motivo="Senha perdida pelo servidor", **kw)


def test_redefinir_senha_de_humano_gera_define_e_exige_a_troca(ativos, caplog):
    saida = ciclo.redefinir_senha_humano("ana.lima", redefinir(), CTX)
    assert ativos.atributos_gravados() == [("unicodePwd", "pwdLastSet")]
    conta = ativos.da("ana.lima")
    assert conta["attrs"]["pwdLastSet"] == 0 and saida.senha_nova == conta["senha"] and len(saida.senha_nova) == 12
    assert (saida.arvore, saida.bloqueada, saida.login) == (OP, False, "ana.lima") and ativos.uac("ana.lima") == 512
    acao, alvo, detalhes = ativos.auditoria[-1]
    assert (acao, alvo) == (Acao.REDEFINIR_SENHA, "ana.lima")
    assert detalhes == {"motivo": "Senha perdida pelo servidor", "tamanho_senha": 12, "troca_obrigatoria": True}
    assert saida.senha_nova not in caplog.text and saida.senha_nova not in repr(ativos.auditoria)


def test_redefinir_senha_com_tamanho_informado(ativos):
    saida = ciclo.redefinir_senha_humano("ana.lima", redefinir(tamanho_senha=30), CTX)
    assert len(saida.senha_nova) == 30 and ativos.auditoria[-1][2]["tamanho_senha"] == 30


def test_redefinir_senha_nao_muda_o_bloqueio(ativos):
    saida = ciclo.redefinir_senha_humano("bia.souza", redefinir(), CTX)   # bloqueada, com "senha não expira"
    assert saida.bloqueada and ativos.uac("bia.souza") == 66050
    assert ativos.atributos_gravados() == [("unicodePwd",)] and ativos.auditoria[-1][2]["troca_obrigatoria"] is False


def test_redefinir_senha_de_nao_humano_garante_a_flag_e_nao_troca(ativos):
    ciclo.redefinir_senha_nao_humano("nhu.sistema.contas", redefinir(), CTX)
    assert ativos.atributos_gravados() == [("userAccountControl",), ("unicodePwd",)]     # flag antes da senha
    assert ativos.uac("nhu.sistema.contas") == 512 | 65536
    assert "pwdLastSet" not in ativos.da("nhu.sistema.contas")["attrs"]
    assert ativos.auditoria[-1][2]["troca_obrigatoria"] is False


def test_redefinir_senha_de_nao_humano_que_ja_tem_a_flag_so_troca_a_senha(ativos):
    ativos.conta(OP, Ramo.DIRETA, "FAZENDA", "nhu.robo.dois", nome="robodois", uac=512 | 65536)
    ativos.ops.clear()
    ciclo.redefinir_senha_nao_humano("nhu.robo.dois", redefinir(), CTX)
    assert ativos.atributos_gravados() == [("unicodePwd",)]


def test_redefinir_senha_so_em_operativos(ativos):
    seed_desincorporada(ativos)
    ativos.conta(DESINC, Ramo.DIRETA, "ANTIGA", "hugo.neto", categoria=Categoria.CARREIRA, uac=514)
    ativos.ops.clear()
    for login in ("caio.rocha", "hugo.neto"):                              # Inoperantes e Desincorporados
        with exige(409):
            ciclo.redefinir_senha_humano(login, redefinir(), CTX)
    assert ativos.ops == []


def test_redefinir_senha_de_conta_inexistente_ou_de_outro_tipo(ativos):
    with exige(404):
        ciclo.redefinir_senha_humano("quem.nao", redefinir(), CTX)
    with exige(404):
        ciclo.redefinir_senha_humano("nhu.sistema.contas", redefinir(), CTX)
    with exige(404):
        ciclo.redefinir_senha_nao_humano("ana.lima", redefinir(), CTX)
    assert ativos.ops == []


def test_redefinir_senha_sem_tls_nao_altera_nada(ativos):
    ativos.sem_tls = True
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_TLS_INDISPONIVEL):
        ciclo.redefinir_senha_humano("ana.lima", redefinir(), CTX)
    assert ativos.ops == [] and "senha" not in ativos.da("ana.lima")


def test_redefinir_senha_recusada_pelo_ad_nao_devolve_senha(ativos):
    ativos.falhas[("modify", 1)] = erro_ad()
    with pytest.raises(ErroAD):
        ciclo.redefinir_senha_humano("ana.lima", redefinir(), CTX)
    assert "senha" not in ativos.da("ana.lima")


def test_rota_de_redefinir_devolve_a_senha_sem_cache(monkeypatch):
    def falso(login, dados, ctx):
        assert dados.motivo == "Senha perdida" and dados.tamanho_senha == 20
        return SenhaRedefinidaOut(login=login, nome="X", tipo=HUMANO, ramo=Ramo.DIRETA, unidade="FAZENDA",
                                  categoria=Categoria.CARREIRA, arvore=OP, bloqueada=False,
                                  distinguished_name="CN=X", senha_nova="Senha#Nova123")
    monkeypatch.setattr(ciclo, "redefinir_senha_humano", falso)
    client = TestClient(principal.app)
    token = client.post("/auth/token", json={"client_id": "cliente-de-teste",
                                             "client_secret": SEGREDO_DE_TESTE}).json()["access_token"]
    cabecalho = {"Authorization": f"Bearer {token}"}
    r = client.post("/identidade/humanos/ana.lima/redefinir-senha",
                    json={"motivo": "Senha perdida", "tamanho_senha": 20}, headers=cabecalho)
    assert r.status_code == 200 and r.json()["senha_nova"] == "Senha#Nova123"
    assert r.headers["cache-control"] == "no-store"
    assert client.post("/identidade/humanos/ana.lima/redefinir-senha", json={}, headers=cabecalho).status_code == 422
    assert client.post("/identidade/humanos/ana.lima/redefinir-senha", json={"motivo": "ok"},
                       headers=cabecalho).status_code == 422                        # motivo curto demais
    assert client.post("/identidade/humanos/ana.lima/redefinir-senha",
                       json={"motivo": "Senha perdida"}).status_code == 401


# =============================================================================
# Transferir
# =============================================================================

def transf(**kw) -> TransferirHumano:
    base = dict(instrumento="Portaria 20/2026", ramo_destino=Ramo.DIRETA, unidade_destino="educacao",
                categoria_destino=Categoria.COMISSIONADO)
    return TransferirHumano(**{**base, **kw})


def test_transferir_muda_unidade_e_categoria_mantendo_login_e_estado(ativos):
    saida = ciclo.transferir_humano("ana.lima", transf(), CTX)
    assert ativos.tipos_de_operacao() == ["modify_dn", "modify"]                    # move, depois pml
    assert saida.distinguished_name == f"CN=ana.lima,{container(OP, unidade='EDUCACAO', categoria=Categoria.COMISSIONADO)}"
    assert (saida.unidade, saida.categoria, saida.arvore, saida.login) == ("EDUCACAO", Categoria.COMISSIONADO, OP, "ana.lima")
    assert ativos.uac("ana.lima") == 512                                            # estado preservado
    assert saida.atributos_pml[TRANSFERIDO.instrumento] == "Portaria 20/2026"
    assert saida.atributos_pml[PML_CPF] == "1"                                      # o que já tinha continua
    assert ativos.auditoria[-1][0] is Acao.TRANSFERIR_IDENTIDADE


def test_transferir_para_outro_ramo_perde_a_categoria_e_vice_versa(ativos):
    saida = ciclo.transferir_humano(
        "ana.lima", transf(ramo_destino=Ramo.INDIRETA, unidade_destino="codel", categoria_destino=None), CTX)
    assert saida.distinguished_name == f"CN=ana.lima,{dn_container(OP, Ramo.INDIRETA, 'CODEL')}"
    assert (saida.ramo, saida.categoria) == (Ramo.INDIRETA, None)
    volta = ciclo.transferir_humano("ana.lima", transf(unidade_destino="fazenda", categoria_destino=Categoria.ESTAGIO), CTX)
    assert volta.distinguished_name == f"CN=ana.lima,{container(OP, categoria=Categoria.ESTAGIO)}"
    assert volta.categoria is Categoria.ESTAGIO


def test_transferir_valida_o_destino_no_corpo():
    with pytest.raises(ValidationError):
        TransferirHumano(instrumento="Portaria 1")                                   # destino é obrigatório
    with pytest.raises(ValidationError):
        transf(categoria_destino=None)                                               # Direta exige categoria
    with pytest.raises(ValidationError):
        transf(ramo_destino=Ramo.INDIRETA, unidade_destino="codel")                  # fora da Direta não há categoria


def test_transferir_nao_humano_vai_para_naohumanos_do_destino(ativos):
    dados = TransferirNaoHumano(instrumento="Portaria 20/2026", ramo_destino=Ramo.DIRETA, unidade_destino="educacao")
    saida = ciclo.transferir_nao_humano("nhu.sistema.contas", dados, CTX)
    assert saida.distinguished_name == f"CN=sistemacontas,{dn_container(OP, Ramo.DIRETA, 'EDUCACAO', None, NAO_HUMANO)}"
    assert saida.categoria is None


def test_transferir_nao_humano_exige_o_lado_nao_humanos_do_destino(ativos):
    del ativos.objs[dn_unidade(OP, Ramo.DIRETA, "EDUCACAO", NAO_HUMANO).lower()]
    dados = TransferirNaoHumano(instrumento="Portaria 20/2026", ramo_destino=Ramo.DIRETA, unidade_destino="educacao")
    with exige(404):
        ciclo.transferir_nao_humano("nhu.sistema.contas", dados, CTX)
    assert ativos.ops == []


def test_transferir_humano_entre_ramos_continua_no_lado_humanos(ativos):
    dados = TransferirHumano(instrumento="Portaria 21/2026", ramo_destino=Ramo.INDIRETA, unidade_destino="codel")
    saida = ciclo.transferir_humano("ana.lima", dados, CTX)
    assert saida.distinguished_name == f"CN=ana.lima,{dn_container(OP, Ramo.INDIRETA, 'CODEL')}"
    assert "OU=Humanos,OU=Operativos," in saida.distinguished_name and saida.categoria is None


def test_transferir_so_a_partir_de_operativos(ativos):
    with exige(409):
        ciclo.transferir_humano("caio.rocha", transf(), CTX)
    assert ativos.ops == []


def test_transferir_recusa_destino_inexistente_mesmo_lugar_e_ou_interna_ausente(ativos):
    with exige(404):
        ciclo.transferir_humano("ana.lima", transf(unidade_destino="naoexiste"), CTX)
    with exige(409):
        ciclo.transferir_humano("ana.lima", transf(unidade_destino="fazenda", categoria_destino=Categoria.CARREIRA), CTX)
    del ativos.objs[container(OP, unidade="EDUCACAO", categoria=Categoria.COMISSIONADO).lower()]
    with exige(409):
        ciclo.transferir_humano("ana.lima", transf(), CTX)
    assert ativos.ops == []


def test_transferir_sem_schema_desfaz_o_movimento(ativos):
    original = ativos.dn("ana.lima")
    ativos.sem_schema.add(TRANSFERIDO.instrumento)
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        ciclo.transferir_humano("ana.lima", transf(), CTX)
    assert ativos.tipos_de_operacao() == ["modify_dn", "modify_dn"] and ativos.dn("ana.lima") == original


def test_transferir_se_o_desfazer_falhar_registra_inconsistencia(ativos, caplog):
    ativos.sem_schema.add(TRANSFERIDO.instrumento)
    ativos.falhas[("modify_dn", 2)] = erro_ad()
    with pytest.raises(ErroAD, check=lambda e: e.codigo == Codigo.AD_SCHEMA_INCOMPLETO):
        ciclo.transferir_humano("ana.lima", transf(), CTX)
    assert "INCONSISTENTE" in caplog.text


def test_transferir_com_pml_desligado_so_move_e_avisa(ativos, monkeypatch):
    monkeypatch.setattr(settings, "PML_GRAVAR", False)
    saida = ciclo.transferir_humano("ana.lima", transf(), CTX)
    assert ativos.tipos_de_operacao() == ["modify_dn"] and saida.avisos


def test_transferir_falha_ao_mover_nao_deixa_rastro(ativos):
    original = ativos.dn("ana.lima")
    ativos.falhas[("modify_dn", 1)] = erro_ad()
    with pytest.raises(ErroAD):
        ciclo.transferir_humano("ana.lima", transf(), CTX)
    assert ativos.ops == [] and ativos.dn("ana.lima") == original
