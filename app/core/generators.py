import re
import secrets
import string
import unicodedata


def remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def gerar_login(primeiro_nome: str, ultimo_nome: str) -> str:
    """Gera login no formato primeiro.ultimo, minúsculo e sem acentos/espaços."""
    primeiro = remover_acentos(primeiro_nome).strip().lower()
    ultimo = remover_acentos(ultimo_nome).strip().lower()
    primeiro = re.sub(r"[^a-z]", "", primeiro)
    ultimo = re.sub(r"[^a-z]", "", ultimo)
    return f"{primeiro}.{ultimo}"


def gerar_senha(tamanho: int = 8) -> str:
    """
    Gera senha aleatória atendendo aos requisitos padrão de complexidade
    do Active Directory (maiúscula, minúscula, número e símbolo).
    """
    maiusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    numeros = string.digits
    simbolos = "!@#$%&*"

    senha = [
        secrets.choice(maiusculas),
        secrets.choice(minusculas),
        secrets.choice(numeros),
        secrets.choice(simbolos),
    ]
    todos = maiusculas + minusculas + numeros + simbolos
    senha += [secrets.choice(todos) for _ in range(tamanho - len(senha))]
    secrets.SystemRandom().shuffle(senha)
    return "".join(senha)
