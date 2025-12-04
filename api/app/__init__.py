"""
App module - aplicação FastAPI

Este módulo contém o application factory pattern para criar instâncias
da aplicação FastAPI com toda a configuração necessária.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.middleware import setup_middleware
from app.core.events import startup_handler, shutdown_handler
from app.core.auth import auth
from app.api.v1.routes import api_router


def create_app() -> FastAPI:
    """
    Factory para criar a aplicação FastAPI configurada
    
    Returns:
        FastAPI: Aplicação configurada e pronta para uso
    """
    # Criar aplicação
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        description="API para criação e gerenciamento de provas com compilação LaTeX",
        max_upload_size=settings.MAX_UPLOAD_SIZE
    )
    
    # Configurar autenticação (AuthX error handlers)
    auth.handle_errors(app)
    
    # Configurar middlewares (CORS, etc)
    setup_middleware(app)
    
    # Configurar event handlers
    app.add_event_handler("startup", startup_handler)
    app.add_event_handler("shutdown", shutdown_handler)
    
    # Montar arquivos estáticos do React
    if settings.REACT_BUILD_DIR.exists():
        assets_dir = settings.REACT_BUILD_DIR / "assets"
        if assets_dir.exists():
            app.mount(
                "/assets", 
                StaticFiles(directory=str(assets_dir)), 
                name="assets"
            )
        app.mount(
            "/static", 
            StaticFiles(directory=str(settings.REACT_BUILD_DIR)), 
            name="static"
        )
    
    # Incluir routers da API
    app.include_router(api_router)

    return app
