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
```

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

OMRChecker:
Para rodar a correção foi utilizado OMRChecker como solução simples e eficaz, para configurar é preciso utilizar o comando setup.sh dentro da pasta de correção

```bash
cd api/correction
./setup.sh
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

## Configuração VPS

### SETUP INICIAL

```bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install -y \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-latex-extra \
        auto-multiple-choice
sudo apt install -y build-essential
sudo apt install -y git
sudo apt install -y python3-venv
sudo apt-get install -y psmisc

# se nao tiver docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
# fi

mkdir -p ~/postgres-docker/{data,logs,config}
cd ~/postgres-docker
nano docker-compose.yml
```

```yml
services:
  postgres:
    image: postgres:15
    container_name: postgres-prod
    restart: always
    environment:
      POSTGRES_USER: avaliarsistemadev
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: avaliar
    ports:
      - "5432:5432"
    volumes:
      - ./data:/var/lib/postgresql/data
```

```bash
echo POSTGRES_PASSWORD=$(openssl rand -hex 32) > .env

docker compose up -d

cd

git clone https://github.com/Braz-Souza/Avaliar Avaliar
cd ~/Avaliar/api
# git checkout production OU git checkout staging

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

echo LOGIN_PIN=000000 > .env
echo JWT_SECRET_KEY=$(uv run python -c "import secrets; print(secrets.token_urlsafe(32))") >> .env
echo DATABASE_URL=postgresql://avaliarsistemadev:<INSERIRSENHAAQUI>@localhost:5434/avaliar >> .env
echo CORS_ORIGINS=http://localhost,http://<ipmachine> >> .env # NO MOMENTO DEIXEI COMO CORS_ORIGIN=*

cd correction
rm -rf OMRChecker
./setup.sh

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
nvm install v22
```

#### CONFIG DO NGINX

```bash

sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/avaliar
```

```nginx
server {
    listen 80;
    server_name url.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/avaliar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo tail -f /var/log/nginx/error.log
sudo apt install python3 python3-dev python3-venv libaugeas-dev gcc
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
sudo certbot --nginx
```


### Continuous Development

```bash
cd ~/Avaliar
git pull
cd ~/Avaliar/api
fuser -k 8000/tcp || true
uv python install 3.12
uv python pin 3.12
uv sync
uv run alembic upgrade head
nohup uv run main.py > app.log 2>&1 &
cd ~/Avaliar/front
fuser -k 3000/tcp || true
nvm use v22
npm install
npm run build
nohup npm start > app.log 2>&1 &
```

## Comandos para config no ambiente vps

Necessário ja ter o docker instalado
```bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install -y \
        texlive-latex-base \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-latex-extra \
        auto-multiple-choice
sudo apt install -y build-essential
sudo apt install python3.11-venv
sudo apt install libzbar0 libzbar-dev

mkdir -p ~/postgres-docker/{data,logs,config}
cd ~/postgres-docker
nano docker-compose.yml
```

Colocar o texto abaixo:
```yml
services:
  postgres:
    image: postgres:15
    container_name: postgres-prod
    restart: always
    environment:
      POSTGRES_USER: avaliarsistemadev
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: avaliar
    ports:
      - "5434:5432" # DEIXEI 5433 POIS JA TINHA OUTRO BANCO LA
    volumes:
      - ./data:/var/lib/postgresql/data
```

```bash
echo POSTGRES_PASSWORD=$(openssl rand -hex 32) > .env

docker compose up -d

git clone https://github.com/Braz-Souza/Avaliar
cd Avaliar
cd api
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

echo LOGIN_PIN=000000 > .env
echo JWT_SECRET_KEY=$(uv run python -c "import secrets; print(secrets.token_urlsafe(32))") >> .env
echo DATABASE_URL=postgresql://avaliarsistemadev:<INSERIRSENHAAQUI>@localhost:5434/avaliar >> .env
echo CORS_ORIGINS=http://localhost,http://<ipmachine> >> .env

uv python install 3.12
uv python pin 3.12
uv sync
uv run alembic upgrade head

# provavel que deu erro ja que configurei um pouco errado, para fix
rm alembic/versions/*.py
uv run alembic revision --autogenerate -m "initial schema"
sed -i '2i import sqlmodel' alembic/versions/cf9e70613fd9_initial_schema.py
sed -i "s/server_default='gen_random_uuid()'/server_default=sa.text('gen_random_uuid()')/g" alembic/versions/e9d10bc2a568_initial_schema.py
uv run alembic upgrade head

cd correction
rm -rf OMRChecker
./setup.sh

cd ..

nohup uv run main.py > app.log 2>&1 &

cd ~/Avaliar/front
echo VITE_API_BASE_URL=http://localhost:8000/api > .env
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
nvm install v22
nvm use v22
npm i

# NO MEU CASO, TIVE QUE TROCAR O ENDPOINT API localhost em todos arquivos para o ip da maquina da api

npm run build
nohup npm start > app.log 2>&1 &
``` 
