"""
Erros de domínio e interpretação dos resultados do AD.

`ErroDominio` herda de `HTTPException` de propósito: os serviços têm
`except HTTPException: raise`, então estes erros atravessam o código sem virar
500 genérico. O resultado bruto do AD (`conn.result`) nunca vai ao cliente:
ele é traduzido aqui, registrado em log e devolvido como {codigo, mensagem,
detalhes}, com a providência que o responsável deve pedir à Infraestrutura.
"""
import functools
from typing import Any, Iterable, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ldap3.core.exceptions import LDAPCommunicationError, LDAPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging_config import logger, request_id_var


class Codigo:
    """Códigos estáveis de erro devolvidos ao cliente."""
    ERRO_INTERNO = "ERRO_INTERNO"
    ERRO_HTTP = "ERRO_HTTP"
    REQUISICAO_INVALIDA = "REQUISICAO_INVALIDA"
    NAO_AUTENTICADO = "NAO_AUTENTICADO"
    PROIBIDO = "PROIBIDO"
    METODO_NAO_PERMITIDO = "METODO_NAO_PERMITIDO"
    CONFLITO = "CONFLITO"
    VALIDACAO = "VALIDACAO"
    MUITAS_TENTATIVAS = "MUITAS_TENTATIVAS"
    FORA_DA_RAIZ = "FORA_DA_RAIZ"
    AD_PERMISSAO_NEGADA = "AD_PERMISSAO_NEGADA"
    AD_SCHEMA_INCOMPLETO = "AD_SCHEMA_INCOMPLETO"
    AD_TLS_INDISPONIVEL = "AD_TLS_INDISPONIVEL"
    AD_CERTIFICADO_NAO_CONFERE = "AD_CERTIFICADO_NAO_CONFERE"
    AUDITORIA_INDISPONIVEL = "AUDITORIA_INDISPONIVEL"
    AD_OPERACAO_RECUSADA = "AD_OPERACAO_RECUSADA"
    AD_CONFLITO = "AD_CONFLITO"
    AD_ERRO = "AD_ERRO"
    AD_INDISPONIVEL = "AD_INDISPONIVEL"
    AD_CREDENCIAL_DE_SERVICO_INVALIDA = "AD_CREDENCIAL_DE_SERVICO_INVALIDA"
    ERRO_LDAP_CLIENTE = "ERRO_LDAP_CLIENTE"
    JA_EXISTE = "JA_EXISTE"
    NAO_ENCONTRADO = "NAO_ENCONTRADO"
    OU_NAO_VAZIA = "OU_NAO_VAZIA"


class ErroDominio(HTTPException):
    """Erro com código estável: {"codigo", "mensagem", "detalhes"}."""

    def __init__(
        self,
        mensagem: str,
        *,
        codigo: str = Codigo.ERRO_INTERNO,
        headers: Optional[dict[str, str]] = None,
        status_code: int = 500,
        detalhes: Optional[dict[str, Any]] = None,
    ):
        self.codigo = codigo
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        super().__init__(status_code=status_code, detail=mensagem, headers=headers)


class ErroForaDaRaiz(ErroDominio):
    """A operação alcançaria um DN fora de OU=DESENVOL."""

    def __init__(self, mensagem: str, *, detalhes: Optional[dict[str, Any]] = None):
        super().__init__(mensagem, codigo=Codigo.FORA_DA_RAIZ, status_code=403, detalhes=detalhes)


class ErroAD(ErroDominio):
    """Falha devolvida pelo Active Directory, já interpretada."""


class ErroConfiguracao(RuntimeError):
    """Configuração inválida na inicialização: a API não deve subir."""


# Códigos de resultado LDAP usados na interpretação.
INSUFFICIENT_ACCESS = 50
NO_SUCH_ATTRIBUTE = 16
UNDEFINED_ATTRIBUTE_TYPE = 17
INVALID_ATTRIBUTE_SYNTAX = 21
OBJECT_CLASS_VIOLATION = 65
UNWILLING_TO_PERFORM = 53
STRONGER_AUTH_REQUIRED = 8
CONFIDENTIALITY_REQUIRED = 13
CONSTRAINT_VIOLATION = 19
ENTRY_ALREADY_EXISTS = 68
NO_SUCH_OBJECT = 32
NOT_ALLOWED_ON_NON_LEAF = 66
SIZE_LIMIT_EXCEEDED = 4  # busca com resultado parcial: não é erro


def _providencia_50(operacao: str, atributos: tuple[str, ...], classe: Optional[str], escopo: str) -> str:
    attrs = {a.lower() for a in atributos}
    onde = f"em {escopo}" if escopo else "na OU alvo"
    if operacao == "add":
        if classe == "organizationalunit":
            return f"Create Organizational Unit objects {onde} (e nas OUs filhas) para a conta da API."
        if classe == "user":
            return f"Create User objects {onde} para a conta da API."
        return f"Create child objects {onde} para a conta da API (classe: {classe or 'não identificada'})."
    if operacao == "modify":
        if "unicodepwd" in attrs:
            extra = f" e Write pwdLastSet {onde}" if "pwdlastset" in attrs else ""
            return f"Direito estendido Reset Password sobre os usuários da sub-árvore{extra}."
        if "useraccountcontrol" in attrs:
            return f"Write userAccountControl (conjunto de propriedades Account Restrictions) {onde}."
        nomes = ", ".join(atributos) or "os atributos alterados"
        return f"Write dos atributos {nomes} {onde} (ou do conjunto de propriedades que os contém)."
    if operacao == "modify_dn":
        return (f"Delete (ou Delete child objects) na origem e Create child objects no destino, "
                f"para mover objetos {onde}.")
    if operacao == "delete":
        return f"Delete no objeto (ou Delete child objects no pai) {onde}."
    if operacao == "search":
        return f"List contents e Read property {onde}."
    return f"Permissão correspondente à operação '{operacao}' {onde}."


def traduzir_resultado(
    operacao: str,
    resultado: dict,
    *,
    alvo_mascarado: str,
    atributos: Iterable[str] = (),
    classe: Optional[str] = None,
    criptografada: bool = True,
) -> ErroAD:
    """
    Traduz o resultado de uma operação LDAP que falhou em um ErroAD e registra
    UMA linha de log estruturada (só nomes de atributos, nunca valores).
    """
    atributos = tuple(str(a) for a in atributos)
    codigo_ldap = resultado.get("result")
    descricao = str(resultado.get("description", ""))
    mensagem_ad = str(resultado.get("message", ""))[:300]
    pml = [a for a in atributos if a.lower().startswith("pml")]

    providencia = ""
    if codigo_ldap == INSUFFICIENT_ACCESS:
        status, codigo = 502, Codigo.AD_PERMISSAO_NEGADA
        texto = "O Active Directory recusou a operação por falta de permissão da conta da API."
        providencia = _providencia_50(operacao, atributos, classe, alvo_mascarado)
    elif codigo_ldap in (NO_SUCH_ATTRIBUTE, UNDEFINED_ATTRIBUTE_TYPE, INVALID_ATTRIBUTE_SYNTAX):
        status, codigo = 502, Codigo.AD_SCHEMA_INCOMPLETO
        if pml:
            texto = f"O atributo {', '.join(pml)} não existe no schema do Active Directory."
            providencia = ("A Infraestrutura precisa criar o(s) atributo(s) no schema "
                           "(pedido de extensão do schema).")
        else:
            texto = "O Active Directory não reconhece um dos atributos informados."
            providencia = f"Verifique os atributos enviados: {', '.join(atributos) or 'não identificados'}."
    elif codigo_ldap == OBJECT_CLASS_VIOLATION:
        status, codigo = 502, Codigo.AD_SCHEMA_INCOMPLETO
        texto = "O Active Directory recusou os atributos por violação de classe de objeto."
        providencia = ("Atributo ou classe não permitida no objeto: a classe auxiliar que contém "
                       "o atributo pode não estar associada a este tipo de objeto.")
    elif codigo_ldap in (STRONGER_AUTH_REQUIRED, CONFIDENTIALITY_REQUIRED) or (
        codigo_ldap == UNWILLING_TO_PERFORM and "unicodepwd" in {a.lower() for a in atributos}
        and not criptografada
    ):
        status, codigo = 503, Codigo.AD_TLS_INDISPONIVEL
        texto = "O Active Directory exige conexão criptografada para esta operação."
        providencia = "Certificado/StartTLS (ou LDAPS) no controlador de domínio."
    elif codigo_ldap == UNWILLING_TO_PERFORM:
        status, codigo = 502, Codigo.AD_OPERACAO_RECUSADA
        texto = "O Active Directory recusou a operação (unwillingToPerform)."
        providencia = "Verifique a política de senha do domínio e as regras do objeto envolvido."
    elif codigo_ldap == CONSTRAINT_VIOLATION:
        status, codigo = 409, Codigo.AD_CONFLITO
        texto = "O Active Directory recusou por restrição (valor duplicado ou política violada)."
        providencia = "sAMAccountName ou userPrincipalName já usado no domínio, ou política de senha."
    elif codigo_ldap == ENTRY_ALREADY_EXISTS:
        status, codigo = 409, Codigo.JA_EXISTE
        texto = "O objeto já existe no Active Directory."
    elif codigo_ldap == NO_SUCH_OBJECT:
        status, codigo = 404, Codigo.NAO_ENCONTRADO
        texto = "O objeto ou a OU informada não existe no Active Directory."
    elif codigo_ldap == NOT_ALLOWED_ON_NON_LEAF:
        status, codigo = 409, Codigo.OU_NAO_VAZIA
        texto = "A OU possui objetos dentro e não pode ser removida."
    else:
        status, codigo = 502, Codigo.AD_ERRO
        texto = "O Active Directory devolveu um erro não esperado."
        providencia = f"Código LDAP {codigo_ldap} ({descricao}); veja o log."

    logger.error(
        f"AD_ERRO operacao={operacao} codigo_ldap={codigo_ldap} descricao={descricao} "
        f"alvo={alvo_mascarado or '-'} atributos={','.join(atributos) or '-'} "
        f"codigo_api={codigo} providencia=\"{providencia}\" mensagem_ad=\"{mensagem_ad}\""
    )
    detalhes: dict[str, Any] = {
        "operacao": operacao,
        "codigo_ldap": codigo_ldap,
        "descricao_ldap": descricao,
    }
    if providencia:
        detalhes["providencia"] = providencia
    return ErroAD(texto, codigo=codigo, status_code=status, detalhes=detalhes)


def traduzir_excecao(operacao: str, exc: Exception, *, alvo_mascarado: str = "") -> ErroDominio:
    """
    Traduz uma exceção do próprio cliente ldap3 (que nunca chegou ao AD e não
    tem `conn.result`) em erro de domínio, registrando a linha de log.
    """
    tipo = type(exc).__name__
    if isinstance(exc, LDAPCommunicationError):
        status, codigo = 503, Codigo.AD_INDISPONIVEL
        texto = "Falha de comunicação com o Active Directory."
    else:
        status, codigo = 500, Codigo.ERRO_LDAP_CLIENTE
        texto = "Erro interno na biblioteca LDAP ao preparar a operação."
    logger.error(
        f"AD_ERRO operacao={operacao} excecao={tipo} alvo={alvo_mascarado or '-'} "
        f"codigo_api={codigo} mensagem=\"{str(exc)[:300]}\""
    )
    return ErroDominio(texto, codigo=codigo, status_code=status,
                       detalhes={"operacao": operacao, "excecao": tipo})


def tratar_erros(funcao):
    """
    Decorador dos serviços: erros HTTP e de domínio passam; falha do cliente LDAP vira 503
    e qualquer outra exceção vira 500, ambas registradas com o nome da operação.
    """
    @functools.wraps(funcao)
    def envolvida(*args, **kwargs):
        try:
            return funcao(*args, **kwargs)
        except HTTPException:
            raise
        except LDAPException as e:
            logger.error(f"Erro LDAP em {funcao.__name__}: {e}")
            raise ErroDominio("Erro de comunicação com o Active Directory",
                              codigo=Codigo.AD_INDISPONIVEL, status_code=503) from e
        except Exception as e:
            logger.error(f"Erro inesperado em {funcao.__name__}: {e}")
            raise ErroDominio("Erro interno ao processar a solicitação",
                              codigo=Codigo.ERRO_INTERNO, status_code=500) from e
    return envolvida


CODIGO_POR_STATUS = {
    400: Codigo.REQUISICAO_INVALIDA, 401: Codigo.NAO_AUTENTICADO, 403: Codigo.PROIBIDO,
    404: Codigo.NAO_ENCONTRADO, 405: Codigo.METODO_NAO_PERMITIDO, 409: Codigo.CONFLITO,
    422: Codigo.VALIDACAO, 429: Codigo.MUITAS_TENTATIVAS, 500: Codigo.ERRO_INTERNO,
    503: Codigo.AD_INDISPONIVEL,
}


def _resposta(status: int, codigo: str, mensagem: str, detalhes: Optional[dict] = None,
              headers: Optional[dict] = None) -> JSONResponse:
    """Corpo único de erro: {codigo, mensagem, detalhes}; com o request_id, se houver."""
    detalhes = dict(detalhes or {})
    identificador = request_id_var.get()
    if identificador != "-":
        detalhes.setdefault("request_id", identificador)
    return JSONResponse(
        status_code=status, headers=headers,
        content={"codigo": codigo, "mensagem": mensagem, "detalhes": detalhes},
    )


async def _tratar_erro_dominio(request: Request, exc: ErroDominio) -> JSONResponse:
    return _resposta(exc.status_code, exc.codigo, exc.mensagem, exc.detalhes, exc.headers)


async def _tratar_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    codigo = CODIGO_POR_STATUS.get(exc.status_code, Codigo.ERRO_HTTP)
    mensagem = exc.detail if isinstance(exc.detail, str) else "Erro na requisição"
    return _resposta(exc.status_code, codigo, mensagem, headers=exc.headers)


async def _tratar_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Só campo e mensagem: o valor enviado (`input`) não é devolvido, pois pode ser dado pessoal.
    erros = [{"campo": ".".join(str(parte) for parte in e["loc"]), "mensagem": e["msg"]} for e in exc.errors()]
    return _resposta(422, Codigo.VALIDACAO, "Dados da requisição inválidos", {"erros": erros})


def resposta_inesperada(request: Request, exc: Exception) -> JSONResponse:
    """500 para exceção não tratada (log com o tipo, sem expor detalhes ao cliente)."""
    logger.error(f"Erro inesperado em {request.method} {request.url.path}: {type(exc).__name__}: {exc}")
    return _resposta(500, Codigo.ERRO_INTERNO, "Erro interno ao processar a solicitação")


async def _tratar_inesperado(request: Request, exc: Exception) -> JSONResponse:
    return resposta_inesperada(request, exc)


def registrar_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ErroDominio, _tratar_erro_dominio)
    app.add_exception_handler(StarletteHTTPException, _tratar_http)
    app.add_exception_handler(RequestValidationError, _tratar_validacao)
    app.add_exception_handler(Exception, _tratar_inesperado)
