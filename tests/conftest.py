"""
Ambiente de teste: valores fixos, independentes do .env real, e nenhum acesso
ao Active Directory. As variáveis são definidas ANTES de importar a
aplicação, porque `Settings` falha na importação sem elas.
"""
import hashlib
import os

SEGREDO_DE_TESTE = "segredo-de-teste-longo-e-aleatorio"
_SALT = bytes.fromhex("00112233445566778899aabbccddeeff")
_ITERACOES = 1000
_HASH = hashlib.pbkdf2_hmac("sha256", SEGREDO_DE_TESTE.encode(), _SALT, _ITERACOES).hex()

os.environ["API_LOG_FILE"] = os.devnull   # o log real (logs/api_ad.log) é só de execuções reais
os.environ["AUDITORIA_CONTINGENCIA_FILE"] = os.devnull
os.environ["PML_GRAVAR"] = "true"   # os testes não herdam o valor do .env real
os.environ["AD_UPN_SUFIXO"] = "londrina.pr.gov.br"
os.environ["API_REGRAS_FILE"] = "config/regras.toml"
os.environ["AMBIENTE"] = "dev"
os.environ["AD_PML_BASE"] = "OU=PML,OU=DESENVOL,DC=londrina,DC=pr,DC=gov,DC=br"
os.environ["JWT_SECRET_KEY"] = "chave-jwt-somente-para-testes-0123456789abcdef"
os.environ["API_CLIENT_ID"] = "cliente-de-teste"
os.environ["API_CLIENT_SECRET_HASH"] = f"pbkdf2_sha256${_ITERACOES}${_SALT.hex()}${_HASH}"
# Arquivo em logs/teste (dentro do projeto, ignorado pelo git); SQLite em memória não atravessa threads.
os.environ["DATABASE_URL"] = "sqlite:///logs/teste/teste_auditoria.db"


# =============================================================================
# Fixtures: um AD em memória no lugar da conexão real
# =============================================================================
import pytest  # noqa: E402


@pytest.fixture
def ad(monkeypatch):
    """AD em memória (tests/ad_falso.py) com as OUs fixas; a auditoria vai para `ad.auditoria`."""
    from app.core import ldap_connection
    from app.services import estrutura_service, identidade_ciclo, identidade_service
    from tests.ad_falso import ADFalso

    falso = ADFalso()
    monkeypatch.setattr(ldap_connection, "get_connection", lambda: falso)

    def executar_auditado(ctx, acao, alvo, inicial, operacao):
        """Só o que o serviço faz: roda a operação e guarda (ação, alvo, detalhes) se deu certo."""
        resultado, detalhes = operacao()
        falso.auditoria.append((acao, alvo, {**inicial, **detalhes}))
        return resultado

    for modulo in (estrutura_service, identidade_service, identidade_ciclo):
        monkeypatch.setattr(modulo, "executar_auditado", executar_auditado)
    return falso


@pytest.fixture
def ativos(ad):
    """O AD falso com unidades FAZENDA, EDUCACAO (Direta) e CODEL (Indireta) e algumas contas."""
    from tests.ad_falso import semear_identidades
    return semear_identidades(ad)


@pytest.fixture(autouse=True)
def _sem_bloqueio_de_login():
    """O limite de falhas de /auth/token é global; cada teste começa sem ninguém bloqueado."""
    from app.core import limite
    limite.por_cliente.limpar()
    limite.por_ip.limpar()
