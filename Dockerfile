# API de Identidades no Active Directory (PML) — imagem de execução.
# Base oficial slim (Debian), não alpine: cryptography, pycryptodome, pydantic-core, httptools etc. têm wheels
# manylinux para Python 3.12 e instalam sem compilador. O nome é totalmente qualificado para valer também no
# Podman (sem prompt de short-name). Config, logs e .env vêm do host (docker-compose.yml).
FROM docker.io/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências antes do código: a camada só é refeita quando o requirements.txt muda.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/
COPY config/ config/

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
