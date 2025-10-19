# =============================================================================
# MULTI-STAGE DOCKERFILE PARA PRODUÇÃO
# =============================================================================

# =============================================================================
# STAGE 1: BUILD DO FRONTEND REACT
# =============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/front

# Copy package files for better caching
COPY front/package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY front/ ./

# Build React application
RUN npm run build

# =============================================================================
# STAGE 2: CONFIGURAÇÃO DO BACKEND PYTHON COM UV
# =============================================================================
FROM python:3.12-slim AS backend

# Install system dependencies including LaTeX
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy Python configuration files
COPY pyproject.toml uv.lock ./

# Install Python dependencies with uv
RUN uv sync --frozen --no-dev

# Copy backend source code
COPY main.py ./
COPY static/ ./static/

# Copy built React files from frontend stage
COPY --from=frontend-builder /app/front/build/ ./front/build/

# Create directory for PDF outputs
RUN mkdir -p static/pdfs

# Expose port
EXPOSE 4200

# Run with uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4200"]
