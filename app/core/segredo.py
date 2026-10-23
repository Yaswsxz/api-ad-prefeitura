"""
Hash do segredo do cliente da API. Módulo sem dependência da
configuração, para poder gerar o hash ANTES de o .env estar preenchido.
"""
import hashlib
import hmac
import secrets

_ITERACOES = 600_000


def gerar_hash_segredo(segredo: str, iteracoes: int = _ITERACOES) -> str:
    """
    Gera o valor de API_CLIENT_SECRET_HASH a partir do segredo do cliente:
    pbkdf2_sha256$<iteracoes>$<salt_hex>$<hash_hex>. Use um segredo aleatório
    longo (ex.: secrets.token_urlsafe(32)); o segredo em si nunca vai ao .env.
    """
    salt = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac("sha256", segredo.encode("utf-8"), salt, iteracoes)
    return f"pbkdf2_sha256${iteracoes}${salt.hex()}${derivado.hex()}"


def verificar_segredo(segredo: str, hash_armazenado: str) -> bool:
    """Compara o segredo informado com o hash configurado, em tempo constante."""
    try:
        _, iteracoes, salt_hex, esperado_hex = hash_armazenado.split("$")
        derivado = hashlib.pbkdf2_hmac(
            "sha256", segredo.encode("utf-8"), bytes.fromhex(salt_hex), int(iteracoes)
        )
        return hmac.compare_digest(derivado.hex(), esperado_hex)
    except (ValueError, TypeError):
        return False
