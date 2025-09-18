# Avaliar - FastAPI + React

Para rodar ambiente monolitico rodando front e back num unico container utilize o Dockerfile default

```bash
docker build -t avaliar-web:latest .

# Para deixar o container somente com a porta do front aberta
docker run -p 3000:3000 avaliar-web:latest

# Para deixar o container com a porta do front e back aberta
docker run -p 8000:8000 -p 3000:3000 avaliar-web:latest
```

Para rodar em ambientes separados utilize o docker-compose.yml
