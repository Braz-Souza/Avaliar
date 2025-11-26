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
echo CORS_ORIGINS=http://localhost,http://<ipmachine> >> .enva

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

#apos isso ainda foi preciso adicionar o user manualmente na tabela ja q o alembic foi deletado, depois melhorar isso

docker exec -it postgres-prod psql -U avaliarsistemadev -d avaliar
INSERT INTO users (username, pin_hash, created_at)
VALUES ('user_admin', '$2a$12$*****HASH*****', '2025-11-21 01:22:36.253 -0
300');

# pra garantir que o front nao vai cair, deixei um script abaixo para rodar sempre

chmod +x start.sh
nohup ./start.sh &
```

```bash
#!/bin/bash

# Script para rodar serve com auto-restart
LOG_FILE="app.log"
PID_FILE="serve.pid"

echo "Iniciando servidor com auto-restart..." | tee -a "$LOG_FILE"

# Função para limpar ao sair
cleanup() {
    echo "Parando servidor..." | tee -a "$LOG_FILE"
    if [ -f "$PID_FILE" ]; then
        kill $(cat "$PID_FILE") 2>/dev/null
        rm -f "$PID_FILE"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Loop infinito para reiniciar
while true; do
    echo "[$(date)] Iniciando aplicação..." | tee -a "$LOG_FILE"

    # Roda o comando e salva o PID
    sudo npx serve ./build/client --single -l 80 >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    # Aguarda o processo terminar
    wait $!
    EXIT_CODE=$?

    echo "[$(date)] Aplicação parou com código $EXIT_CODE" | tee -a "$LOG_FILE"

    # Remove o PID file
    rm -f "$PID_FILE"

    # Aguarda 5 segundos antes de reiniciar
    echo "[$(date)] Reiniciando em 5 segundos..." | tee -a "$LOG_FILE"
    sleep 5
done
```
