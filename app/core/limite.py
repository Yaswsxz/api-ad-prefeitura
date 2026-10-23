"""
Limite de tentativas falhas de autenticação. Em memória e por processo: com mais
de um processo, cada um conta as suas. Só falhas contam; um sucesso zera a contagem da chave.
"""
import math
import threading
import time
from collections import deque
from typing import Callable

from app.core.config import settings


class LimiteDeFalhas:
    def __init__(self, maximo: int, janela: float, relogio: Callable[[], float] = time.monotonic,
                 capacidade: int = 10_000):
        self.maximo, self.janela, self._relogio, self._capacidade = maximo, janela, relogio, capacidade
        self._falhas: dict[str, deque[float]] = {}
        self._trava = threading.Lock()

    def _recentes(self, chave: str, agora: float) -> deque[float]:
        fila = self._falhas.get(chave)
        if fila is None:
            return deque()
        while fila and agora - fila[0] >= self.janela:
            fila.popleft()
        if not fila:
            del self._falhas[chave]
        return fila

    def segundos_restantes(self, chave: str) -> int:
        """0 se a chave pode tentar; senão, quanto falta para a tentativa mais antiga sair da janela."""
        with self._trava:
            agora = self._relogio()
            fila = self._recentes(chave, agora)
            if len(fila) < self.maximo:
                return 0
            return max(1, math.ceil(fila[len(fila) - self.maximo] + self.janela - agora))

    def registrar_falha(self, chave: str) -> None:
        with self._trava:
            agora = self._relogio()
            self._recentes(chave, agora)
            if chave not in self._falhas and len(self._falhas) >= self._capacidade:
                del self._falhas[next(iter(self._falhas))]      # descarta a chave mais antiga
            self._falhas.setdefault(chave, deque()).append(agora)

    def zerar(self, chave: str) -> None:
        with self._trava:
            self._falhas.pop(chave, None)

    def limpar(self) -> None:
        with self._trava:
            self._falhas.clear()


# O IP tem limite maior que o cliente: um servidor (o front-end) pode ser o único IP de muitos acessos.
por_cliente = LimiteDeFalhas(settings.AUTH_MAX_FALHAS, settings.AUTH_JANELA_SEGUNDOS)
por_ip = LimiteDeFalhas(settings.AUTH_MAX_FALHAS * 4, settings.AUTH_JANELA_SEGUNDOS)
