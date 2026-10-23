import logging
import os
import sys
from contextvars import ContextVar
from pathlib import Path

from app.core.config import settings
from app.core.rotacao import RotacaoSemApagamento

# Identificador da requisição em curso; aparece em toda linha de log.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class _FiltroRequestId(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def _handler_de_arquivo(caminho: Path) -> logging.Handler:
    """Arquivo de log em `logs/`, que vira (sem apagar nada) ao mudar o dia ou passar do teto."""
    if str(caminho) == os.devnull:     # os testes usam isso para não misturar linhas de teste com o log real
        return logging.FileHandler(os.devnull, encoding="utf-8")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    return RotacaoSemApagamento(str(caminho), settings.LOG_MAX_BYTES)


def setup_logging():
    """Configura o sistema de logs da aplicação."""
    logger = logging.getLogger("api_ad")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    filtro = _FiltroRequestId()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(filtro)
    logger.addHandler(console_handler)

    arquivo = settings.arquivo_log
    file_handler = _handler_de_arquivo(arquivo)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(filtro)
    logger.addHandler(file_handler)

    # O log do próprio uvicorn (acessos e erros do servidor) também vai para logs/, na mesma política.
    if str(arquivo) != os.devnull:
        uvicorn_handler = _handler_de_arquivo(arquivo.with_name("uvicorn.log"))
        uvicorn_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                                                       datefmt="%Y-%m-%d %H:%M:%S"))
        for nome in ("uvicorn.error", "uvicorn.access"):
            logging.getLogger(nome).addHandler(uvicorn_handler)

    return logger


logger = setup_logging()
