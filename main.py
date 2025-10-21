import uvicorn
from app import create_app
from app.core.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.API_wPORT,
        reload=settings.DEBUG
    )
