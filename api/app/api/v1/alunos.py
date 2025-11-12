"""
Router para endpoints de gerenciamento de alunos

TODAS AS ROTAS REQUEREM AUTENTICAÇÃO (via middleware global)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models.aluno import AlunoCreate, AlunoUpdate, AlunoRead
from app.services.aluno_manager import AlunoManagerService
from app.core.database import get_db
from app.core.dependencies import CurrentUser

router = APIRouter(prefix="/alunos", tags=["Alunos Management"])


def get_aluno_manager(db: Session = Depends(get_db)) -> AlunoManagerService:
    """
    Dependency para obter instância do serviço de alunos com sessão do banco

    Args:
        db: Sessão do banco de dados

    Returns:
        AlunoManagerService com sessão do banco
    """
    return AlunoManagerService(db)


@router.post("", response_model=AlunoRead, status_code=201)
async def create_aluno(
    aluno: AlunoCreate,
    user_id: CurrentUser,
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> AlunoRead:
    """
    Cria um novo aluno - REQUER AUTENTICAÇÃO

    Args:
        aluno: Dados do aluno (nome, email, matricula, turma_ids)
        user_id: ID do usuário autenticado (injetado pelo middleware)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        AlunoRead com informações do aluno criado
    """
    return await manager.create_aluno(aluno)


@router.get("", response_model=List[AlunoRead])
async def list_alunos(
    user_id: CurrentUser,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    nome: Optional[str] = Query(None, description="Nome para filtrar"),
    email: Optional[str] = Query(None, description="Email para filtrar"),
    matricula: Optional[str] = Query(None, description="Matrícula para filtrar"),
    turma_id: Optional[UUID] = Query(None, description="ID da turma para filtrar"),
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> List[AlunoRead]:
    """
    Lista alunos com paginação e filtros opcionais - REQUER AUTENTICAÇÃO

    Args:
        user_id: ID do usuário autenticado (injetado pelo middleware)
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar
        nome: Nome para filtrar (opcional)
        email: Email para filtrar (opcional)
        matricula: Matrícula para filtrar (opcional)
        turma_id: ID da turma para filtrar (opcional)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Lista de AlunoRead
    """
    return await manager.list_alunos(
        skip=skip,
        limit=limit,
        nome=nome,
        email=email,
        matricula=matricula,
        turma_id=turma_id
    )


@router.get("/{aluno_id}", response_model=AlunoRead)
async def get_aluno(
    aluno_id: UUID,
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> AlunoRead:
    """
    Recupera um aluno específico pelo ID

    Args:
        aluno_id: ID do aluno
        manager: Serviço de gerenciamento (injetado)

    Returns:
        AlunoRead com dados completos
    """
    return await manager.get_aluno(aluno_id)


@router.put("/{aluno_id}", response_model=AlunoRead)
async def update_aluno(
    aluno_id: UUID,
    aluno: AlunoUpdate,
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> AlunoRead:
    """
    Atualiza um aluno existente

    Args:
        aluno_id: ID do aluno
        aluno: Novos dados do aluno
        manager: Serviço de gerenciamento (injetado)

    Returns:
        AlunoRead com informações atualizadas
    """
    return await manager.update_aluno(aluno_id, aluno)


@router.delete("/{aluno_id}")
async def delete_aluno(
    aluno_id: UUID,
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> dict:
    """
    Exclui um aluno

    Args:
        aluno_id: ID do aluno
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com mensagem de sucesso
    """
    return await manager.delete_aluno(aluno_id)


@router.post("/{aluno_id}/turmas/{turma_id}", response_model=AlunoRead)
async def add_aluno_to_turma(
    aluno_id: UUID,
    turma_id: UUID,
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> AlunoRead:
    """
    Adiciona um aluno a uma turma

    Args:
        aluno_id: ID do aluno
        turma_id: ID da turma
        manager: Serviço de gerenciamento (injetado)

    Returns:
        AlunoRead com informações atualizadas
    """
    return await manager.add_aluno_to_turma(aluno_id, turma_id)


@router.delete("/{aluno_id}/turmas/{turma_id}", response_model=AlunoRead)
async def remove_aluno_from_turma(
    aluno_id: UUID,
    turma_id: UUID,
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> AlunoRead:
    """
    Remove um aluno de uma turma

    Args:
        aluno_id: ID do aluno
        turma_id: ID da turma
        manager: Serviço de gerenciamento (injetado)

    Returns:
        AlunoRead com informações atualizadas
    """
    return await manager.remove_aluno_from_turma(aluno_id, turma_id)


@router.get("/count/total")
async def count_alunos(
    user_id: CurrentUser,
    nome: Optional[str] = Query(None, description="Nome para filtrar"),
    email: Optional[str] = Query(None, description="Email para filtrar"),
    matricula: Optional[str] = Query(None, description="Matrícula para filtrar"),
    turma_id: Optional[UUID] = Query(None, description="ID da turma para filtrar"),
    manager: AlunoManagerService = Depends(get_aluno_manager)
) -> dict:
    """
    Conta o total de alunos com filtros opcionais - REQUER AUTENTICAÇÃO

    Args:
        user_id: ID do usuário autenticado (injetado pelo middleware)
        nome: Nome para filtrar (opcional)
        email: Email para filtrar (opcional)
        matricula: Matrícula para filtrar (opcional)
        turma_id: ID da turma para filtrar (opcional)
        manager: Serviço de gerenciamento (injetado)

    Returns:
        Dicionário com o total de alunos
    """
    total = await manager.count_alunos(
        nome=nome,
        email=email,
        matricula=matricula,
        turma_id=turma_id
    )
    return {"total": total}
