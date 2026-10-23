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


def gerar_credenciais() -> tuple[str, str, str]:
    """(segredo do cliente, valor de API_CLIENT_SECRET_HASH, valor de JWT_SECRET_KEY), todos novos."""
    segredo = secrets.token_urlsafe(32)
    return segredo, gerar_hash_segredo(segredo), secrets.token_urlsafe(48)


def main() -> None:
    """
    `python -m app.core.segredo` (no Compose: `docker compose run --rm gerar-segredos`): imprime as credenciais
    de uma instalação. Só vai ao terminal: nada é gravado em arquivo nem em log, e o segredo em claro não é
    mostrado de novo. O hash sai entre aspas simples para o "$" não ser interpolado (Compose, shell).
    """
    segredo, hash_segredo, chave_jwt = gerar_credenciais()
    print("SEGREDO DO CLIENTE (entregue ao cliente; não é mostrado de novo):")
    print(f"  {segredo}")
    print()
    print("Cole no .env:")
    print(f"  API_CLIENT_SECRET_HASH='{hash_segredo}'")
    print(f"  JWT_SECRET_KEY={chave_jwt}")


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


if __name__ == "__main__":
    main()
