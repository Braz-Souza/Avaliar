from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.questoes import Questao
from app.utils.questoes import (
    clear_questoes_db,
    add_questoes_db,
    show_questao_db,
    show_questoes_db
)
from app.routers.auth import User, get_current_active_user
import json
    
questoes_router = APIRouter()

@questoes_router.get("/questoes/id/{questaoID}", response_model=list[Questao])
async def get_questao(questaoID: int):
    q = show_questao_db(questaoID=questaoID)
    return q

@questoes_router.get("/questoes/enunciado/{enunciado}", response_model=list[Questao])
async def get_questao(enunciado: str):
    q = show_questao_db(enunciado=enunciado)
    return q

@questoes_router.get("/questoes/alternativa/{alternativa}", response_model=list[Questao])
async def get_questao(alternativa: str):
    q = show_questao_db(alternativa=alternativa)
    return q

@questoes_router.get("/questoes/", response_model=list[Questao])
async def get_questoes():
    q = show_questoes_db()
    return q

@questoes_router.post("/questoes/")
async def create_questao(request: Questao, _: Annotated[User, Depends(get_current_active_user)]):
    add_questoes_db(
        request.questaoID, 
        request.enunciado, 
        json.dumps(request.alternativas)
    )

@questoes_router.post("/questoes/clear")
async def clear_questoes(_: Annotated[User, Depends(get_current_active_user)]):
    clear_questoes_db()
