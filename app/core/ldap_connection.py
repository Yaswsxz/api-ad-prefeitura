from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional

from ldap3 import NONE, NTLM, Connection, Server
from ldap3.core.exceptions import LDAPException

from app.core.config import settings
from app.core.erros_ad import (
    SIZE_LIMIT_EXCEEDED,
    Codigo,
    ErroAD,
    ErroDominio,
    traduzir_excecao,
    traduzir_resultado,
)
from app.core.logging_config import logger
from app.core.raiz import garantir_dentro, mascarar_dn
from app.core.tls import config_tls, conferir_certificado

OID_PAGINACAO = "1.2.840.113556.1.4.319"
PROVIDENCIA_TLS = "Certificado/StartTLS (ou LDAPS) no controlador de domínio"

# O StartTLS recusado é um estado conhecido da infraestrutura (PERM-T01): com
# AD_ALLOW_INSECURE=true é avisado uma vez por processo, não a cada conexão.
_aviso_sem_tls_emitido = False


def _nomes(atributos: Any) -> tuple[str, ...]:
    """Só NOMES de atributos (nunca valores) para log e interpretação de erros."""
    if not atributos:
        return ()
    if isinstance(atributos, dict):
        return tuple(str(k) for k in atributos)
    if isinstance(atributos, str):
        return (atributos,)
    return tuple(str(a) for a in atributos)


def _classe_do_objeto(object_class: Any, attributes: Any) -> Optional[str]:
    classes = object_class or (attributes or {}).get("objectClass") or []
    if isinstance(classes, str):
        classes = [classes]
    minusculas = {str(c).lower() for c in classes}
    for classe in ("organizationalunit", "user", "container"):
        if classe in minusculas:
            return classe
    return None


class ConexaoAD(Connection):
    """
    Conexão ldap3 que, em TODA operação (leitura ou escrita):
      1. recusa DN fora de OU=DESENVOL, inclusive base de busca vazia e
         `new_superior` fora da raiz;
      2. lê o resultado e, se falhou, traduz o erro do AD, registra uma linha
         de log estruturada e levanta ErroAD.

    A redefinição de senha passa por `modify` com `unicodePwd`, portanto
    também é coberta. O resultado bruto do AD nunca chega ao cliente.
    """

    def _criptografada(self) -> bool:
        return bool(getattr(self.server, "ssl", False) or getattr(self, "tls_started", False))

    def _executar(
        self, operacao: str, alvo: str, atributos: tuple[str, ...],
        chamada: Callable[[], Any], classe: Optional[str] = None,
    ) -> Any:
        try:
            retorno = chamada()
        except LDAPException as e:
            # Falha do próprio cliente (rede, socket, argumento): nunca chega ao
            # AD e não gera `conn.result`. Vira erro de domínio e linha de log.
            raise traduzir_excecao(operacao, e, alvo_mascarado=mascarar_dn(alvo))
        resultado = self.result or {}
        codigo = resultado.get("result")
        if not codigo:
            if operacao != "search":
                # Escrita concluída: mostra no log qual permissão já foi comprovada.
                logger.info(
                    f"AD_OK operacao={operacao} alvo={mascarar_dn(alvo) or '-'} "
                    f"atributos={','.join(atributos) or '-'}"
                )
            return retorno
        if operacao == "search" and codigo == SIZE_LIMIT_EXCEEDED:
            return retorno  # resultado parcial, não é falha
        raise traduzir_resultado(
            operacao, resultado, alvo_mascarado=mascarar_dn(alvo), atributos=atributos,
            classe=classe, criptografada=self._criptografada(),
        )

    # --- escritas --------------------------------------------------------

    def add(self, dn, object_class=None, attributes=None, controls=None):
        garantir_dentro(dn, "add")
        return self._executar(
            "add", dn, _nomes(attributes),
            lambda: super(ConexaoAD, self).add(dn, object_class, attributes, controls),
            classe=_classe_do_objeto(object_class, attributes),
        )

    def modify(self, dn, changes, controls=None):
        garantir_dentro(dn, "modify")
        return self._executar(
            "modify", dn, _nomes(changes),
            lambda: super(ConexaoAD, self).modify(dn, changes, controls),
        )

    def modify_dn(self, dn, relative_dn, delete_old_dn=True, new_superior=None, controls=None):
        garantir_dentro(dn, "modify_dn (origem)")
        if new_superior:
            garantir_dentro(new_superior, "modify_dn (destino)")
        return self._executar(
            "modify_dn", dn, (),
            lambda: super(ConexaoAD, self).modify_dn(
                dn, relative_dn, delete_old_dn, new_superior, controls
            ),
        )

    def delete(self, dn, controls=None):
        garantir_dentro(dn, "delete")
        return self._executar(
            "delete", dn, (),
            lambda: super(ConexaoAD, self).delete(dn, controls),
        )

    # --- leitura ---------------------------------------------------------

    def search(self, search_base, search_filter, *args, **kwargs):
        garantir_dentro(search_base, "search")
        atributos = kwargs.get("attributes")
        if atributos is None and len(args) >= 3:  # search_scope, dereference_aliases, attributes
            atributos = args[2]
        return self._executar(
            "search", search_base, _nomes(atributos),
            lambda: super(ConexaoAD, self).search(search_base, search_filter, *args, **kwargs),
        )


def buscar(conn, base: str, filtro: str, escopo, atributos=None, pagina: int = 500) -> list[dict]:
    """
    Busca paginada (o AD limita cada resposta a 1000 entradas): devolve a lista
    completa de entradas como dicionários {"dn", "attributes"}. Passa pela
    guarda da raiz e pela interpretação de erros da conexão.
    """
    entradas: list[dict] = []
    cookie = None
    while True:
        conn.search(base, filtro, search_scope=escopo, attributes=atributos,
                    paged_size=pagina, paged_cookie=cookie)
        entradas += [r for r in (conn.response or []) if r.get("type") == "searchResEntry"]
        controles = (conn.result or {}).get("controls") or {}
        cookie = controles.get(OID_PAGINACAO, {}).get("value", {}).get("cookie")
        if not cookie:
            return entradas


# =============================================================================
# Abrir a conexão
# =============================================================================

def _usa_ldaps() -> bool:
    return settings.AD_SERVER.lower().startswith("ldaps")


def _nova_conexao() -> ConexaoAD:
    server = Server(
        settings.AD_SERVER,
        use_ssl=_usa_ldaps(),
        tls=config_tls(),
        get_info=NONE,
        connect_timeout=10,
    )
    return ConexaoAD(
        server,
        user=settings.AD_BIND_USER,
        password=settings.AD_BIND_PASSWORD,
        authentication=NTLM,
        auto_bind=False,
        check_names=False,
        receive_timeout=30,
    )


def _encerrar(conn: ConexaoAD) -> None:
    try:
        conn.unbind()
    except LDAPException:
        pass


def _aceitar_conexao_sem_tls(erro: LDAPException) -> None:
    """
    O servidor recusou o StartTLS. Fora do desenvolvimento (AD_ALLOW_INSECURE=false) isso é
    AD_TLS_INDISPONIVEL; em desenvolvimento segue sem criptografia, com um aviso por processo.
    """
    global _aviso_sem_tls_emitido
    if not settings.AD_ALLOW_INSECURE:
        logger.error(
            f"AD_ERRO operacao=start_tls descricao={type(erro).__name__} "
            f"mensagem_ad=\"{str(erro)[:300]}\" providencia=\"{PROVIDENCIA_TLS}\""
        )
        raise ErroDominio(
            "O Active Directory recusou TLS (StartTLS) e a API exige conexão criptografada.",
            codigo=Codigo.AD_TLS_INDISPONIVEL,
            status_code=503,
            detalhes={"providencia": f"{PROVIDENCIA_TLS}."},
        )
    if not _aviso_sem_tls_emitido:
        _aviso_sem_tls_emitido = True
        logger.warning(
            f"AD_ALLOW_INSECURE=true: o AD recusou StartTLS ({type(erro).__name__}); "
            "seguindo SEM criptografia. A redefinição de senha vai falhar. "
            "Pendência de infraestrutura PERM-T01 (certificado no DC). Aviso emitido uma vez por processo."
        )


def _abrir() -> ConexaoAD:
    """Abre a conexão com o canal protegido (LDAPS ou StartTLS), ainda sem autenticar."""
    conn = _nova_conexao()
    conn.open()
    if _usa_ldaps():
        return conn
    try:
        conn.start_tls()
        return conn
    except LDAPException as e:
        _encerrar(conn)
        _aceitar_conexao_sem_tls(e)
    # Só desenvolvimento: a tentativa deixa o socket inutilizável, então abrimos outra, sem TLS.
    conn = _nova_conexao()
    conn.open()
    return conn


def _autenticar(conn: ConexaoAD) -> None:
    if conn.bind():
        return
    resultado = conn.result or {}
    logger.error(
        f"AD_ERRO operacao=bind codigo_ldap={resultado.get('result')} "
        f"descricao={resultado.get('description')} "
        f"mensagem_ad=\"{str(resultado.get('message', ''))[:300]}\""
    )
    _encerrar(conn)
    raise ErroAD(
        "Falha ao autenticar a conta de serviço da API no Active Directory.",
        codigo=Codigo.AD_CREDENCIAL_DE_SERVICO_INVALIDA,
        status_code=502,
        detalhes={"providencia": "Verifique AD_BIND_USER e AD_BIND_PASSWORD "
                                 "(conta bloqueada, expirada ou senha alterada)."},
    )


def get_connection() -> ConexaoAD:
    """
    Abre uma conexão com o Active Directory usando a conta de serviço da API
    (AD_BIND_USER/AD_BIND_PASSWORD) e NTLM. Esta é a única conta autenticada:
    a API não faz bind de contas de usuários do domínio.

    - Não lê rootDSE nem schema (`get_info=NONE`) e não valida nomes de
      atributos no cliente (`check_names=False`). Atenção: com qualquer schema
      carregado, o ldap3 valida os atributos pedidos numa BUSCA mesmo com
      `check_names=False` (operation/search.py), o que barraria os `pml*`
      antes de chegarem ao AD; por isso não há schema. A existência de
      atributos é descoberta pelo erro do AD. Valores em filtros e em DN
      precisam ser escapados pela aplicação.
    - TLS é obrigatório (LDAPS ou StartTLS antes do bind). Se o servidor
      recusar o StartTLS, a conexão falha com AD_TLS_INDISPONIVEL, exceto em
      desenvolvimento com AD_ALLOW_INSECURE=true.
    """
    try:
        conn = _abrir()
        try:
            conferir_certificado(conn)      # antes do bind: a credencial só vai ao servidor confirmado
        except ErroDominio:
            _encerrar(conn)
            raise
        _autenticar(conn)
        return conn
    except LDAPException as e:
        logger.error(f"AD_ERRO operacao=conexao descricao={type(e).__name__} mensagem_ad=\"{str(e)[:300]}\"")
        raise ErroDominio(
            "Não foi possível conectar ao Active Directory.",
            codigo=Codigo.AD_INDISPONIVEL,
            status_code=503,
        )


@contextmanager
def conexao() -> Iterator[ConexaoAD]:
    """Conexão com o AD que sempre é encerrada: `with conexao() as conn: ...`."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.unbind()
