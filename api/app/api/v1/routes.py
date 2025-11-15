"""
Agregador de rotas da API v1
"""

from fastapi import APIRouter

from app.api.v1 import auth, latex, provas, system, exam_corrector, turmas, alunos, questoes

# Router principal da API v1
api_router = APIRouter(prefix="/api")

# Incluir todos os routers v1
api_router.include_router(auth.router)
api_router.include_router(latex.router)
api_router.include_router(provas.router)
api_router.include_router(system.router)
api_router.include_router(exam_corrector.router)
api_router.include_router(turmas.router)
api_router.include_router(alunos.router)
api_router.include_router(questoes.router)
