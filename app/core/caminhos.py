"""
Onde ficam os arquivos de log e de auditoria: tudo dentro de `logs/`, no projeto.
Caminhos relativos valem a partir da RAIZ DO PROJETO, não do diretório corrente.
"""
import os
from datetime import datetime
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]


def resolver(caminho: str) -> Path:
    """Caminho absoluto: o informado, ou o relativo à raiz do projeto."""
    p = Path(caminho)
    return p if p.is_absolute() else RAIZ_PROJETO / p


def com_sufixo_do_mes(base: Path, quando: datetime) -> Path:
    """`auditoria_contingencia.jsonl` -> `auditoria_contingencia-2026-10.jsonl` (um arquivo por mês)."""
    if str(base) == os.devnull:
        return base
    return base.with_name(f"{base.stem}-{quando:%Y-%m}{base.suffix}")
