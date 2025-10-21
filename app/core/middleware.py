"""
Configuração de middlewares da aplicação
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_middleware(app: FastAPI) -> None:
    """
    Configura todos os middlewares da aplicação
    
    Args:
        app: Instância do FastAPI
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )
