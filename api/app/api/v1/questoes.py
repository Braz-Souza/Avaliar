"""
API endpoints for questao (question) management
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.db.models.questao import (
    QuestaoCreate, QuestaoUpdate, QuestaoRead,
    QuestaoOpcaoCreate, QuestaoOpcaoUpdate, QuestaoOpcaoRead
)
from app.services.questao_manager import QuestaoManagerService

router = APIRouter(prefix="/questoes", tags=["questoes"])


@router.post("/", response_model=QuestaoRead)
async def create_questao(
    questao_data: QuestaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new questao"""
    service = QuestaoManagerService(db)
    return await service.create_questao(questao_data)


@router.get("/prova/{prova_id}", response_model=List[QuestaoRead])
async def list_questoes_by_prova(
    prova_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all questoes for a specific prova"""
    service = QuestaoManagerService(db)
    return await service.list_questoes(prova_id)


@router.get("/{questao_id}", response_model=QuestaoRead)
async def get_questao(
    questao_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific questao by ID"""
    service = QuestaoManagerService(db)
    return await service.get_questao(questao_id)


@router.put("/{questao_id}", response_model=QuestaoRead)
async def update_questao(
    questao_id: UUID,
    questao_update: QuestaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a questao"""
    service = QuestaoManagerService(db)
    return await service.update_questao(questao_id, questao_update)


@router.delete("/{questao_id}")
async def delete_questao(
    questao_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a questao"""
    service = QuestaoManagerService(db)
    return await service.delete_questao(questao_id)


# QuestaoOpcao endpoints
@router.post("/{questao_id}/opcoes", response_model=QuestaoOpcaoRead)
async def create_opcao(
    questao_id: UUID,
    opcao_data: QuestaoOpcaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new opcao for a questao"""
    # Ensure the opcao is linked to the correct questao
    opcao_data.questao_id = questao_id
    service = QuestaoManagerService(db)
    return await service.create_opcao(opcao_data)


@router.get("/{questao_id}/opcoes", response_model=List[QuestaoOpcaoRead])
async def list_opcoes_by_questao(
    questao_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all opcoes for a specific questao"""
    service = QuestaoManagerService(db)
    return await service.list_opcoes(questao_id)


@router.put("/opcoes/{opcao_id}", response_model=QuestaoOpcaoRead)
async def update_opcao(
    opcao_id: UUID,
    opcao_update: QuestaoOpcaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an opcao"""
    service = QuestaoManagerService(db)
    return await service.update_opcao(opcao_id, opcao_update)


@router.delete("/opcoes/{opcao_id}")
async def delete_opcao(
    opcao_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an opcao"""
    service = QuestaoManagerService(db)
    return await service.delete_opcao(opcao_id)
