"""
Arquivo de regras (config/regras.toml): atributos mutáveis por PATCH e tipos de
conta não humana. Carregado e validado na subida; um
arquivo ausente ou inválido impede a API de subir.
"""
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.erros_ad import ErroConfiguracao

_RAIZ_PROJETO = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Regras:
    mutaveis_humano: tuple[str, ...]
    mutaveis_nao_humano: tuple[str, ...]
    tipos_nao_humano: tuple[str, ...]

    def mutaveis(self, nao_humano: bool) -> tuple[str, ...]:
        return self.mutaveis_nao_humano if nao_humano else self.mutaveis_humano


_regras: Optional[Regras] = None


def _lista_de_textos(valor, onde: str) -> tuple[str, ...]:
    if not isinstance(valor, list) or not all(isinstance(v, str) and v.strip() for v in valor):
        raise ErroConfiguracao(f"{onde} deve ser uma lista de textos não vazios")
    return tuple(v.strip() for v in valor)


def interpretar(texto: str, origem: str = "regras") -> Regras:
    """Valida o conteúdo (TOML) do arquivo de regras; `origem` só aparece nas mensagens de erro."""
    try:
        dados = tomllib.loads(texto)
    except tomllib.TOMLDecodeError as e:
        raise ErroConfiguracao(f"Arquivo de regras inválido ({origem}): {e}") from e

    mutaveis = dados.get("atributos_mutaveis", {})
    tipos = _lista_de_textos(dados.get("nao_humano", {}).get("tipos"), "[nao_humano] tipos")
    if not tipos:
        raise ErroConfiguracao("[nao_humano] tipos não pode ser vazio")
    return Regras(
        mutaveis_humano=_lista_de_textos(mutaveis.get("humano", []), "[atributos_mutaveis] humano"),
        mutaveis_nao_humano=_lista_de_textos(mutaveis.get("nao_humano", []), "[atributos_mutaveis] nao_humano"),
        tipos_nao_humano=tipos,
    )


def carregar(caminho: Optional[str] = None) -> Regras:
    """Lê e valida o arquivo de regras; guarda o resultado para `regras()`."""
    global _regras
    arquivo = Path(caminho or settings.API_REGRAS_FILE)
    if not arquivo.is_absolute():
        arquivo = _RAIZ_PROJETO / arquivo
    try:
        texto = arquivo.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ErroConfiguracao(f"Arquivo de regras não encontrado: {arquivo}") from e
    except OSError as e:
        raise ErroConfiguracao(f"Arquivo de regras inválido ({arquivo}): {e}") from e
    _regras = interpretar(texto, str(arquivo))
    return _regras


def regras() -> Regras:
    """Regras já carregadas (carrega na primeira chamada)."""
    return _regras or carregar()
