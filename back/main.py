from fastapi import FastAPI
from app.routers.questoes import questoes_router

app = FastAPI()

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001, log_level="info")
