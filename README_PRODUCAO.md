# 🚀 Avaliar - Sistema de Gestão de Provas (Produção)

## 📋 Visão Geral

O Avaliar é um sistema completo para criação e gerenciamento de provas acadêmicas, construído com FastAPI (backend) e React (frontend), com armazenamento em PostgreSQL.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  API (FastAPI)                                      │   │
│  │  ┌─────────────────────────────────────────────────────┐      │   │
│  │  │  Serviços (ProvaManagerService)              │   │   │
│  │  │  ┌─────────────────────────────────────┐          │   │   │
│  │  │  │  PostgreSQL (Banco de Dados)        │   │   │   │
│  │  │  │  ┌─────────────────────────────┐          │   │   │   │
│  │  │  │  │  LaTeX Compiler          │   │   │   │
│  │  │  │  └─────────────────────────────┘          │   │   │   │
│  │  │  └─────────────────────────────────────────────┘          │   │   │
│  │  └─────────────────────────────────────────────────────────────┘          │   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🗄️ Tecnologias

- **Backend**: FastAPI, Python 3.12, SQLModel, PostgreSQL
- **Frontend**: React, TypeScript, Vite
- **Banco de Dados**: PostgreSQL 15
- **Compilação**: LaTeX com pdfLaTeX
- **Autenticação**: JWT com AuthX
- **Containerização**: Docker e Docker Compose

## 🚀 Implantação

### Pré-requisitos

1. **Docker e Docker Compose**
   ```bash
   # Instalação
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker
   
   # Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)-linux-x86_64" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **PostgreSQL**
   - Instalar PostgreSQL 15+ (se não usar Docker)
   - Criar banco de dados `avaliar`
   - Criar usuário `avaliador` com permissões adequadas

3. **Variáveis de Ambiente**
   - Copiar `.env.example` para `.env`
   - Configurar `DATABASE_URL`, `JWT_SECRET_KEY`, `LOGIN_PIN`

### Implantação com Docker

1. **Preparar Ambiente**
   ```bash
   # Clonar repositório
   git clone <repositorio>
   cd avaliar
   
   # Configurar variáveis de ambiente
   cp .env.example .env
   # Editar .env com valores de produção
   ```

2. **Iniciar Serviços**
   ```bash
   # Iniciar PostgreSQL (se não usar Docker)
   sudo systemctl start postgresql
   
   # Iniciar aplicação com Docker Compose
   docker-compose -f docker-compose.yml up -d
   ```

3. **Migração do Banco**
   ```bash
   # Executar migrações do Alembic
   docker-compose exec backend alembic upgrade head
   
   # Migrar arquivos LaTeX existentes (se aplicável)
   docker-compose exec backend python scripts/migrate_latex_files.py
   ```

4. **Verificar Implantação**
   ```bash
   # Verificar status dos serviços
   docker-compose ps
   
   # Verificar logs
   docker-compose logs backend
   
   # Testar API
   curl http://localhost:8000/api/health
   ```

## 📁 Estrutura de Arquivos

```
avaliar/
├── app/                    # Backend FastAPI
│   ├── api/               # Endpoints da API
│   │   └── v1/         # Versão 1 da API
│   ├── core/               # Configurações e utilitários
│   │   ├── auth.py         # Autenticação JWT
│   │   ├── config.py       # Configurações
│   │   ├── database.py     # Conexão com PostgreSQL
│   │   └── events.py       # Eventos de startup/shutdown
│   ├── db/                 # Modelos SQLModel
│   │   └── models/         # Modelos de dados
│   │       ├── prova.py     # Modelo Prova
│   │       └── user.py      # Modelo User
│   └── services/            # Lógica de negócio
│       ├── latex_compiler.py  # Compilação LaTeX
│       └── prova_manager.py  # Gerenciamento de provas
├── front/                  # Frontend React
│   ├── src/               # Código fonte
│   ├── public/             # Arquivos estáticos
│   ├── package.json        # Dependências
│   └── Dockerfile          # Build do container
├── static/                  # Arquivos estáticos
│   ├── latex_sources/      # Fontes LaTeX (legado)
│   └── pdfs/              # PDFs compilados
├── scripts/                 # Scripts utilitários
│   └── migrate_latex_files.py  # Migração de dados
├── docker-compose.yml        # Orquestração dos serviços
├── Dockerfile               # Build do backend
├── .env.example             # Modelo de variáveis
└── README.md               # Documentação
```

## 🔐 Configuração

### Variáveis de Ambiente (.env)

```bash
# Configurações do Banco de Dados
DATABASE_URL=postgresql://avaliador:senha_segura@localhost:5432/avaliar
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=false

# Configurações de Migração
ALEMBIC_DATABASE_URL=postgresql://avaliador:senha_segura@localhost:5432/avaliar

# Configurações de Autenticação
JWT_SECRET_KEY=sua_chave_secreta_aqui
JWT_ALGORITHM=HS256
JWT_TOKEN_LOCATION=["headers"]
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOGIN_PIN=seu_pin_seguro_aqui

# Configurações da Aplicação
DEBUG=false
API_PORT=8000
```

## 🔧 Manutenção

### Backup do Banco de Dados

```bash
# Backup completo
docker-compose exec postgres pg_dump -U avaliador -d avaliar > backup_$(date +%Y%m%d_%H%M%S).sql

# Restauração
docker-compose exec -T postgres psql -U avaliador -d avaliar < backup_20240101_120000.sql
```

### Logs e Monitoramento

```bash
# Logs do backend
docker-compose logs -f backend

# Logs do PostgreSQL
docker-compose logs -f postgres

# Monitoramento de recursos
docker stats
```

## 🧪 Testes

### Testes de API

```bash
# Teste de saúde
curl http://localhost:8000/api/health

# Teste de autenticação
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"pin": "seu_pin"}'

# Listar provas
curl -X GET "http://localhost:8000/api/provas" \
  -H "Authorization: Bearer <token_jwt>"
```

### Testes de Compilação

```bash
# Testar compilação LaTeX
docker-compose exec backend python -c "
from app.services.latex_compiler import LaTeXCompilerService
compiler = LaTeXCompilerService()
result = await compiler.compile_latex('\\\\section{Test}', 'test_content')
print(f'Compilation result: {result}')
"
```

## 🚨 Solução de Problemas

### Problemas Comuns

1. **Conexão com Banco Recusada**
   - Verificar se PostgreSQL está rodando
   - Verificar string de conexão no `.env`
   - Verificar se usuário e senha estão corretos

2. **Migrações Falhando**
   - Verificar logs de erro do Alembic
   - Executar `alembic current` para verificar estado
   - Reverter migração se necessário: `alembic downgrade -1`

3. **Compilação LaTeX Falhando**
   - Verificar se pdfLaTeX está instalado no container
   - Verificar sintaxe do LaTeX
   - Analisar logs de erro do compilador

4. **Autenticação Falhando**
   - Verificar se `JWT_SECRET_KEY` está configurado
   - Verificar se `LOGIN_PIN` está correto
   - Limpar tokens expirados

### Comandos Úteis

```bash
# Reiniciar serviços
docker-compose restart

# Reconstruir e iniciar
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Acessar terminal do container
docker-compose exec backend bash

# Verificar status do banco
docker-compose exec postgres psql -U avaliador -d avaliar -c "\dt"

# Executar migração específica
docker-compose exec backend alembic upgrade <revision_id>

# Limpar PDFs temporários
docker-compose exec backend python -c "
from app.services.cleanup_service import cleanup_service
removed = cleanup_service.cleanup_temp_pdfs()
print(f'Removed {removed} temp PDFs')
"
```

## 📞 Suporte

### Documentação Adicional

- [API Documentation](./docs/api.md)
- [Guia de Desenvolvimento](./docs/development.md)
- [Guia de Implantação](./docs/deployment.md)
- [Troubleshooting](./docs/troubleshooting.md)

### Contato

- **Desenvolvimento**: [dev@avaliar.com](mailto:dev@avaliar.com)
- **Suporte**: [suporte@avaliar.com](mailto:suporte@avaliar.com)
- **Issues**: [GitHub Issues](https://github.com/avaliar/avaliar/issues)

---

**Versão**: 1.0.0  
**Última Atualização**: 2024-01-01  
**Status**: ✅ Produção