# Avaliar

## Desenvolvimento Local

Primeiro configurar a database localmente depois rodar a api depois o front.
Preciso ter o pdflatex e o auto-multiple-choice no sistema e para isso basta:
```bash
sudo apt-get install -y \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-latex-extra \
        auto-multiple-choice

API:

```bash
cd api
export API_PORT=8000
export DEBUG=True
uv run main.py
```

Alembic (Migrações do Banco de Dados):

```bash
cd api
uv run alembic upgrade head
```

FRONT:

```bash
cd front
npm i
npm run build
npm run start
```



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
