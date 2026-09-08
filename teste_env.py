from app.core.config import settings

print("=== DEBUG DAS VARIAVEIS DO .env ===")
print(f"SERVIDOR: {settings.AD_SERVER}")
print(f"USUARIO: {settings.AD_BIND_USER}")
print(f"SENHA: {settings.AD_BIND_PASSWORD}")
print(f"BASE DN: {settings.AD_BASE_DN}")
print(f"DOMINIO: {settings.AD_DOMAIN}")
print("====================================")
