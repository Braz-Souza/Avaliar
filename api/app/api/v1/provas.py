"""
Router para endpoints de gerenciamento de provas

TODAS AS ROTAS REQUEREM AUTENTICAÇÃO (via middleware global)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models.prova import ProvaCreate, ProvaUpdate, ProvaRead
from app.services.prova_manager import ProvaManagerService
from app.core.database import get_db
from app.core.dependencies import CurrentUser

router = APIRouter(prefix="/provas", tags=["Provas Management"])


def get_prova_manager(db: Session = Depends(get_db)) -> ProvaManagerService:
    """
    Dependency para obter instância do serviço de provas com sessão do banco

    Args:
        db: Sessão do banco de dados

    Returns:
        ProvaManagerService com sessão do banco
    """
    return ProvaManagerService(db)


@router.post("", response_model=ProvaRead, status_code=201)
async def save_prova(
    prova: ProvaCreate,
    user_id: CurrentUser,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> ProvaRead:
    """
    Salva uma nova prova no servidor - REQUER AUTENTICAÇÃO

    Args:
        prova: Dados da prova (nome e conteúdo)
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        ProvaRead com informações da prova salva
    """
    # Don't pass created_by since current auth uses username strings, not UUIDs
    return await manager.save_prova(prova, created_by=None)


@router.get("", response_model=List[ProvaRead])
async def list_provas(
    user_id: CurrentUser,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> List[ProvaRead]:
    """
    Lista provas com paginação - REQUER AUTENTICAÇÃO

    Args:
        user_id: ID do usuário autenticado (injetado pelo middleware)
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Lista de ProvaRead ordenadas por data de modificação
    """
    # Don't filter by created_by since current auth uses username strings, not UUIDs
    return await manager.list_provas(skip=skip, limit=limit, created_by=None)


@router.get("/{prova_id}", response_model=ProvaRead)
async def get_prova(
    prova_id: UUID,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> ProvaRead:
    """
    Recupera o conteúdo de uma prova salva

    Args:
        prova_id: ID da prova
        manager: Serviço de gerenciamento (injetado)

    Returns:
        ProvaRead com dados completos
    """
    return await manager.get_prova(prova_id)


@router.put("/{prova_id}", response_model=ProvaRead)
async def update_prova(
    prova_id: UUID,
    prova: ProvaUpdate,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> ProvaRead:
    """
    Atualiza uma prova existente

    Args:
        prova_id: ID da prova
        prova: Novos dados da prova
        manager: Serviço de gerenciamento (injetado)

    Returns:
        ProvaRead com informações atualizadas
    """
    return await manager.update_prova(prova_id, prova)


@router.delete("/{prova_id}")
async def delete_prova(
    prova_id: UUID,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> dict:
    """
    Exclui uma prova salva

    Args:
        prova_id: ID da prova
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com mensagem de sucesso
    """
    return await manager.delete_prova(prova_id)


@router.get("/{prova_id}/questoes")
async def get_prova_with_questoes(
    prova_id: UUID,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> dict:
    """
    Recupera uma prova com suas questões estruturadas

    Args:
        prova_id: ID da prova
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com dados da prova e questões estruturadas
    """
    return await manager.get_prova_with_questoes(prova_id)


@router.post("/com-questoes", response_model=dict)
async def save_prova_with_questoes(
    prova_data: dict,
    user_id: CurrentUser,
    manager: ProvaManagerService = Depends(get_prova_manager)
) -> dict:
    """
    Salva uma nova prova com questões estruturadas

    Args:
        prova_data: Dados da prova incluindo questões estruturadas
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com informações da prova salva com questões
    """
    # Don't pass created_by since current auth uses username strings, not UUIDs
    return await manager.save_prova_with_questoes(prova_data, created_by=None)
