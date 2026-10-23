import secrets
import string

TAMANHO_SENHA_PADRAO = 12
TAMANHO_SENHA_MIN = 8     # garante folga para as 4 classes de caracteres
TAMANHO_SENHA_MAX = 64


def gerar_senha(tamanho: int = TAMANHO_SENHA_PADRAO) -> str:
    """
    Gera senha aleatória atendendo aos requisitos padrão de complexidade
    do Active Directory (maiúscula, minúscula, número e símbolo).
    Usada na ativação e na redefinição de senha de identidades.
    """
    if not TAMANHO_SENHA_MIN <= tamanho <= TAMANHO_SENHA_MAX:
        raise ValueError(f"tamanho da senha deve estar entre {TAMANHO_SENHA_MIN} e {TAMANHO_SENHA_MAX}")
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
