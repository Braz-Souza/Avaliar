"""
Agregador de rotas da API v1
"""

from fastapi import APIRouter

from app.api.v1 import auth, latex, provas, system

# Router principal da API v1
api_router = APIRouter()

# Incluir todos os routers v1
api_router.include_router(auth.router)
api_router.include_router(latex.router)
api_router.include_router(provas.router)
api_router.include_router(system.router)
