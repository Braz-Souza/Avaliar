# Avaliar

## Desenvolvimento Local

Primeiro configurar a database localmente depois rodar a api depois o front. 

API:

```bash
cd api
export API_PORT=8000
export DEBUG=True
uv run main.py
```

FRONT:

```bash
cd front
npm i
npm run build
cd ..
uv run main.py
```

```bash
# Desenvolvimento (com reload)
uv run uvicorn main:app --reload

# Ou usando o script Python
uv run python main.py

# Produção
uv run uvicorn main:app --host 0.0.0.0 --port 4200 --workers 4
```

A aplicação estará disponível em: `http://localhost:4200`

## Configuração Docker - Atualmente ainda nao configurei o dockerfile perfeitamente

```bash
docker build -t avaliar-web:latest .

# Para rodar o container (aplicação completa - frontend + backend)
docker run -p 4200:4200 --name avaliar avaliar-web:latest

# Para parar e deletar o container permitindo rodar novamente
docker rm -f avaliar
```

### Endpoints disponíveis:
- **Frontend**: `http://localhost:4200/` - Interface React da aplicação
- **API Docs**: `http://localhost:4200/api/docs` - Documentação interativa da API (Swagger)
- **Health Check**: `http://localhost:4200/api/health` - Verificação de status da API

Para rodar em ambientes separados utilize o docker-compose.yml
