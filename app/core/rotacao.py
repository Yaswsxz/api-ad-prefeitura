"""
Quebra de arquivos de log SEM apagar nada.

O handler da biblioteca padrão não serve: `TimedRotatingFileHandler` remove o destino se ele já
existe e ambos os handlers padrão apagam os arquivos mais antigos acima de `backupCount`. Este
só renomeia, para um nome que ainda não existe, e nunca remove.

O arquivo corrente é sempre `<nome>.log`. Ao virar, passa a `<nome>-AAAA-MM-DD.NNN.log` (a data é a
do último registro gravado; NNN é o primeiro número livre, a partir de 001). A ordem alfabética
`<nome>-*.log` seguida de `<nome>.log` é a ordem cronológica.

Vale para UM processo (como a API roda hoje). Com vários processos escrevendo no mesmo arquivo seria
preciso um rotador externo.
"""
import logging
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Optional

ESPERA_APOS_FALHA_S = 60   # depois de uma falha ao virar, só tenta de novo passado este tempo


class RotacaoSemApagamento(logging.FileHandler):
    def __init__(self, caminho: str, max_bytes: int, agora: Callable[[], datetime] = datetime.now,
                 encoding: str = "utf-8"):
        super().__init__(caminho, encoding=encoding, delay=True)
        self._max_bytes = max_bytes
        self._agora = agora
        self._dia: Optional[date] = self._dia_do_arquivo()
        self._proxima_tentativa = 0.0

    # --- decisão -----------------------------------------------------------------------------

    def _dia_do_arquivo(self) -> Optional[date]:
        try:
            return datetime.fromtimestamp(os.stat(self.baseFilename).st_mtime).date()
        except OSError:
            return None

    def _deve_virar(self, hoje: date) -> bool:
        try:
            tamanho = os.path.getsize(self.baseFilename)
        except OSError:
            return False                                 # ainda não existe: nada a virar
        if tamanho == 0:
            return False
        return (self._dia is not None and self._dia < hoje) or tamanho >= self._max_bytes

    # --- rotação -----------------------------------------------------------------------------

    def _destino_livre(self, dia: date) -> Path:
        base = Path(self.baseFilename)
        n = 1
        while True:
            candidato = base.with_name(f"{base.stem}-{dia:%Y-%m-%d}.{n:03d}{base.suffix}")
            if not candidato.exists():
                return candidato
            n += 1

    def _virar(self, hoje: date) -> None:
        if self.stream:
            self.stream.flush()
            self.stream.close()
            self.stream = None
        os.rename(self.baseFilename, self._destino_livre(self._dia or hoje))

    def emit(self, record: logging.LogRecord) -> None:
        hoje = self._agora().date()
        if time.monotonic() >= self._proxima_tentativa and self._deve_virar(hoje):
            try:
                self._virar(hoje)
            except Exception as e:                       # nunca derruba a aplicação por causa do log
                self._proxima_tentativa = time.monotonic() + ESPERA_APOS_FALHA_S
                print(f"LOG_ROTACAO_FALHOU: {self.baseFilename} ({type(e).__name__}: {e}); "
                      f"segue no mesmo arquivo", file=sys.stderr)
        super().emit(record)                             # reabre o arquivo corrente se preciso
        self._dia = hoje
