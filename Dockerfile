# =============================================================================
# MULTI-STAGE DOCKERFILE PARA PRODUÇÃO
# =============================================================================

# =============================================================================
# STAGE 1: BUILD DO FRONTEND REACT
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/front

COPY front/package*.json ./

RUN npm ci

COPY front/ ./

RUN npm run build

# =============================================================================
# STAGE 2: CONFIGURAÇÃO DO BACKEND PYTHON COM UV
# =============================================================================
FROM python:3.12-slim AS backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl perl wget ca-certificates \
        postgresql-client \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-latex-extra \
        auto-multiple-choice && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY api/pyproject.toml api/uv.lock ./

RUN uv sync --frozen --no-dev

COPY api/main.py ./

COPY api/app/ ./app/

COPY api/alembic.ini ./
COPY api/alembic/ ./alembic/

RUN mkdir -p static/

COPY --from=frontend-builder /app/front/build/ ./front/build/

RUN mkdir -p static/pdfs

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
