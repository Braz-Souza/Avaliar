"""
Service para gerenciamento de alunos
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.db.models.aluno import Aluno, AlunoCreate, AlunoUpdate, AlunoRead
from app.db.models.turma import Turma
from app.utils.logger import logger


class AlunoManagerService:
    """
    Serviço responsável pelo gerenciamento de alunos (CRUD) usando SQLModel e PostgreSQL
    """

    def __init__(self, db: Session):
        """Inicializa o serviço de gerenciamento de alunos com sessão do banco de dados"""
        self.db = db

    async def create_aluno(self, aluno_data: AlunoCreate) -> AlunoRead:
        """
        Cria um novo aluno no banco de dados

        Args:
            aluno_data: Dados do aluno (nome, email, matricula, turma_ids)

        Returns:
            AlunoRead com informações do aluno criado

        Raises:
            HTTPException: Se nenhuma turma válida for fornecida
        """
        # Verificar se as turmas existem
        if not aluno_data.turma_ids:
            raise HTTPException(status_code=400, detail="Aluno must belong to at least one turma")

        turmas = self.db.exec(select(Turma).where(Turma.id.in_(aluno_data.turma_ids))).all()
        if len(turmas) != len(aluno_data.turma_ids):
            raise HTTPException(status_code=400, detail="One or more turma IDs are invalid")

        aluno = Aluno(
            nome=aluno_data.nome,
            email=aluno_data.email if aluno_data.email else None,
            matricula=aluno_data.matricula
        )

        # Adicionar turmas ao aluno
        aluno.turmas = turmas

        self.db.add(aluno)
        self.db.commit()
        self.db.refresh(aluno)

        logger.info(f"Aluno created: {aluno.id} ({aluno.nome} - {aluno.matricula})")

        return AlunoRead.from_orm(aluno)

    async def list_alunos(
        self,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        matricula: Optional[str] = None,
        turma_id: Optional[UUID] = None
    ) -> List[AlunoRead]:
        """
        Lista alunos com paginação e filtros opcionais

        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar
            nome: Nome para filtrar (opcional)
            email: Email para filtrar (opcional)
            matricula: Matrícula para filtrar (opcional)
            turma_id: ID da turma para filtrar (opcional)

        Returns:
            Lista de AlunoRead
        """
        query = select(Aluno)

        if nome:
            query = query.where(Aluno.nome.ilike(f"%{nome}%"))
        if email:
            query = query.where(Aluno.email.ilike(f"%{email}%"))
        if matricula:
            query = query.where(Aluno.matricula.ilike(f"%{matricula}%"))
        if turma_id:
            query = query.join(Aluno.turmas).where(Turma.id == turma_id)

        query = query.order_by(Aluno.nome).offset(skip).limit(limit)

        alunos = self.db.exec(query).all()
        result = [AlunoRead.from_orm(aluno) for aluno in alunos]

        logger.debug(f"Listed {len(result)} alunos")

        return result

    async def get_aluno(self, aluno_id: UUID) -> AlunoRead:
        """
        Recupera um aluno específico pelo ID

        Args:
            aluno_id: ID do aluno

        Returns:
            AlunoRead com dados completos

        Raises:
            HTTPException: Se o aluno não for encontrado
        """
        aluno = self.db.get(Aluno, aluno_id)

        if not aluno:
            logger.warning(f"Aluno not found: {aluno_id}")
            raise HTTPException(status_code=404, detail="Aluno not found")

        logger.debug(f"Retrieved aluno: {aluno_id}")

        return AlunoRead.from_orm(aluno)

    async def update_aluno(self, aluno_id: UUID, aluno_update: AlunoUpdate) -> AlunoRead:
        """
        Atualiza um aluno existente

        Args:
            aluno_id: ID do aluno
            aluno_update: Dados para atualizar

        Returns:
            AlunoRead com informações atualizadas

        Raises:
            HTTPException: Se o aluno não for encontrado ou turmas inválidas
        """
        aluno = self.db.get(Aluno, aluno_id)

        if not aluno:
            logger.warning(f"Aluno not found for update: {aluno_id}")
            raise HTTPException(status_code=404, detail="Aluno not found")

        # Atualizar campos se fornecidos
        if aluno_update.nome is not None:
            aluno.nome = aluno_update.nome
        if aluno_update.email is not None:
            aluno.email = aluno_update.email
        if aluno_update.matricula is not None:
            aluno.matricula = aluno_update.matricula

        # Atualizar turmas se fornecidas
        if aluno_update.turma_ids is not None:
            if not aluno_update.turma_ids:
                raise HTTPException(status_code=400, detail="Aluno must belong to at least one turma")

            turmas = self.db.exec(select(Turma).where(Turma.id.in_(aluno_update.turma_ids))).all()
            if len(turmas) != len(aluno_update.turma_ids):
                raise HTTPException(status_code=400, detail="One or more turma IDs are invalid")

            aluno.turmas = turmas

        self.db.add(aluno)
        self.db.commit()
        self.db.refresh(aluno)

        logger.info(f"Aluno updated: {aluno_id} ({aluno.nome} - {aluno.matricula})")

        return AlunoRead.from_orm(aluno)

    async def delete_aluno(self, aluno_id: UUID) -> dict:
        """
        Exclui um aluno do banco de dados

        Args:
            aluno_id: ID do aluno

        Returns:
            Dicionário com mensagem de sucesso

        Raises:
            HTTPException: Se o aluno não for encontrado
        """
        aluno = self.db.get(Aluno, aluno_id)

        if not aluno:
            logger.warning(f"Aluno not found for deletion: {aluno_id}")
            raise HTTPException(status_code=404, detail="Aluno not found")

        self.db.delete(aluno)
        self.db.commit()

        logger.info(f"Aluno deleted: {aluno_id}")

        return {"message": "Aluno deleted successfully", "id": str(aluno_id)}

    async def add_aluno_to_turma(self, aluno_id: UUID, turma_id: UUID) -> AlunoRead:
        """
        Adiciona um aluno a uma turma

        Args:
            aluno_id: ID do aluno
            turma_id: ID da turma

        Returns:
            AlunoRead com informações atualizadas

        Raises:
            HTTPException: Se aluno ou turma não forem encontrados
        """
        aluno = self.db.get(Aluno, aluno_id)
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno not found")

        turma = self.db.get(Turma, turma_id)
        if not turma:
            raise HTTPException(status_code=404, detail="Turma not found")

        # Verificar se o aluno já está na turma
        if turma in aluno.turmas:
            raise HTTPException(status_code=400, detail="Aluno already belongs to this turma")

        aluno.turmas.append(turma)
        self.db.add(aluno)
        self.db.commit()
        self.db.refresh(aluno)

        logger.info(f"Aluno {aluno_id} added to turma {turma_id}")

        return AlunoRead.from_orm(aluno)

    async def remove_aluno_from_turma(self, aluno_id: UUID, turma_id: UUID) -> AlunoRead:
        """
        Remove um aluno de uma turma

        Args:
            aluno_id: ID do aluno
            turma_id: ID da turma

        Returns:
            AlunoRead com informações atualizadas

        Raises:
            HTTPException: Se aluno ou turma não forem encontrados, ou se aluno não estiver na turma
        """
        aluno = self.db.get(Aluno, aluno_id)
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno not found")

        turma = self.db.get(Turma, turma_id)
        if not turma:
            raise HTTPException(status_code=404, detail="Turma not found")

        # Verificar se o aluno está na turma
        if turma not in aluno.turmas:
            raise HTTPException(status_code=400, detail="Aluno does not belong to this turma")

        # Verificar se o aluno ficará sem turmas
        if len(aluno.turmas) == 1:
            raise HTTPException(status_code=400, detail="Aluno must belong to at least one turma")

        aluno.turmas.remove(turma)
        self.db.add(aluno)
        self.db.commit()
        self.db.refresh(aluno)

        logger.info(f"Aluno {aluno_id} removed from turma {turma_id}")

        return AlunoRead.from_orm(aluno)

    async def count_alunos(
        self,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        matricula: Optional[str] = None,
        turma_id: Optional[UUID] = None
    ) -> int:
        """
        Conta o total de alunos, opcionalmente filtrando

        Args:
            nome: Nome para filtrar (opcional)
            email: Email para filtrar (opcional)
            matricula: Matrícula para filtrar (opcional)
            turma_id: ID da turma para filtrar (opcional)

        Returns:
            Número total de alunos
        """
        query = select(func.count(Aluno.id))

        if nome:
            query = query.where(Aluno.nome.ilike(f"%{nome}%"))
        if email:
            query = query.where(Aluno.email.ilike(f"%{email}%"))
        if matricula:
            query = query.where(Aluno.matricula.ilike(f"%{matricula}%"))
        if turma_id:
            query = query.join(Aluno.turmas).where(Turma.id == turma_id)

        return self.db.exec(query).one()
