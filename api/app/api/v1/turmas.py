"""
Router para endpoints de gerenciamento de turmas

TODAS AS ROTAS REQUEREM AUTENTICAÇÃO (via middleware global)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models.turma import TurmaCreate, TurmaUpdate, TurmaRead
from app.services.turma_manager import TurmaManagerService
from app.core.database import get_db
from app.core.dependencies import CurrentUser

router = APIRouter(prefix="/turmas", tags=["Turmas Management"])


def get_turma_manager(db: Session = Depends(get_db)) -> TurmaManagerService:
    """
    Dependency para obter instância do serviço de turmas com sessão do banco

    Args:
        db: Sessão do banco de dados

    Returns:
        TurmaManagerService com sessão do banco
    """
    return TurmaManagerService(db)


@router.post("", response_model=TurmaRead, status_code=201)
async def create_turma(
    turma: TurmaCreate,
    user_id: CurrentUser,
    manager: TurmaManagerService = Depends(get_turma_manager)
) -> TurmaRead:
    """
    Cria uma nova turma - REQUER AUTENTICAÇÃO

    Args:
        turma: Dados da turma (ano, materia, curso, periodo)
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        TurmaRead com informações da turma criada
    """
    return await manager.create_turma(turma)


@router.get("", response_model=List[TurmaRead])
async def list_turmas(
    user_id: CurrentUser,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    ano: Optional[int] = Query(None, description="Ano para filtrar"),
    materia: Optional[str] = Query(None, description="Matéria para filtrar"),
    curso: Optional[str] = Query(None, description="Curso para filtrar"),
    manager: TurmaManagerService = Depends(get_turma_manager)
) -> List[TurmaRead]:
    """
    Lista turmas com paginação e filtros opcionais - REQUER AUTENTICAÇÃO

    Args:
        user_id: ID do usuário autenticado (injetado pelo middleware)
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar
        ano: Ano para filtrar (opcional)
        materia: Matéria para filtrar (opcional)
        curso: Curso para filtrar (opcional)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Lista de TurmaRead
    """
    return await manager.list_turmas(
        skip=skip,
        limit=limit,
        ano=ano,
        materia=materia,
        curso=curso
    )


@router.get("/{turma_id}", response_model=TurmaRead)
async def get_turma(
    turma_id: UUID,
    manager: TurmaManagerService = Depends(get_turma_manager)
) -> TurmaRead:
    """
    Recupera uma turma específica pelo ID

    Args:
        turma_id: ID da turma
        manager: Serviço de gerenciamento (injetado)

    Returns:
        TurmaRead com dados completos
    """
    return await manager.get_turma(turma_id)


@router.put("/{turma_id}", response_model=TurmaRead)
async def update_turma(
    turma_id: UUID,
    turma: TurmaUpdate,
    manager: TurmaManagerService = Depends(get_turma_manager)
) -> TurmaRead:
    """
    Atualiza uma turma existente

    Args:
        turma_id: ID da turma
        turma: Novos dados da turma
        manager: Serviço de gerenciamento (injetado)

    Returns:
        TurmaRead com informações atualizadas
    """
    return await manager.update_turma(turma_id, turma)


@router.delete("/{turma_id}")
async def delete_turma(
    turma_id: UUID,
    manager: TurmaManagerService = Depends(get_turma_manager)
) -> dict:
    """
    Exclui uma turma

    Args:
        turma_id: ID da turma
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com mensagem de sucesso
    """
    return await manager.delete_turma(turma_id)


@router.get("/count/total")
async def count_turmas(
    user_id: CurrentUser,
    ano: Optional[int] = Query(None, description="Ano para filtrar"),
    materia: Optional[str] = Query(None, description="Matéria para filtrar"),
    curso: Optional[str] = Query(None, description="Curso para filtrar"),
    manager: TurmaManagerService = Depends(get_turma_manager)
) -> dict:
    """
    Conta o total de turmas com filtros opcionais - REQUER AUTENTICAÇÃO

    Args:
        user_id: ID do usuário autenticado (injetado pelo middleware)
        ano: Ano para filtrar (opcional)
        materia: Matéria para filtrar (opcional)
        curso: Curso para filtrar (opcional)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com o total de turmas
    """
    total = await manager.count_turmas(ano=ano, materia=materia, curso=curso)
    return {"total": total}
