# =============================================================================
# MULTI-STAGE DOCKERFILE PARA PRODUÇÃO
# =============================================================================

# =============================================================================
# STAGE 1: BUILD DO FRONTEND REACT
# =============================================================================
FROM node:18-alpine AS frontend-builder

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
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-latex-extra \
        auto-multiple-choice && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY main.py ./

COPY app/ ./app/

RUN mkdir -p static/

COPY --from=frontend-builder /app/front/build/ ./front/build/

RUN mkdir -p static/pdfs

EXPOSE 4200

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4200"]
