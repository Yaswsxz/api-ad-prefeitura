"""Identificador de requisição: gerado ou aceito do cliente, devolvido no cabeçalho e nos logs."""
import re
import uuid

from fastapi import FastAPI, Request

from app.core.erros_ad import resposta_inesperada
from app.core.logging_config import request_id_var

CABECALHO = "X-Request-ID"
_VALIDO = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


def instalar_request_id(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id(request: Request, call_next):
        recebido = request.headers.get(CABECALHO, "")
        identificador = recebido if _VALIDO.match(recebido) else uuid.uuid4().hex
        token = request_id_var.set(identificador)
        try:
            try:
                resposta = await call_next(request)
            except Exception as e:
                # Montada aqui, ainda com o identificador no escopo, para ele constar do corpo e do log.
                resposta = resposta_inesperada(request, e)
        finally:
            request_id_var.reset(token)
        resposta.headers[CABECALHO] = identificador
        return resposta
