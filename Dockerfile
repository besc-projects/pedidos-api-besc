FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instala só o necessário para compilar psycopg2 e outras libs C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala uv
RUN pip install --no-cache-dir uv

# Copia só os arquivos de lock primeiro (melhor cache)
COPY pyproject.toml uv.lock ./

# Instala dependências (inclui as de produção)
RUN uv sync --frozen --no-dev

# Copia o código
COPY . .

# Porta é ignorada pelo Cloud Run, mas deixa aí por clareza
EXPOSE 8000

# ←←← A MÁGICA ESTÁ AQUI
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]