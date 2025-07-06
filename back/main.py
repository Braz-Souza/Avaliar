from fastapi import FastAPI
from app.routers.auth import authentication_router
from app.routers.questoes import questoes_router

app = FastAPI(
    root_path="/avaliar-back",
    docs_url="/docs",
    openapi_url="/openapi.json",
    title="Avaliar - API",
    description="A API para a plataforma de produção e avaliação de provas Avaliar",
    version="0.0.0",
    openapi_version="3.1.0"
)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

app.include_router(authentication_router, tags=["auth"])
app.include_router(questoes_router, tags=["questoes"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
