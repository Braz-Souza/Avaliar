"""
Service para gerenciamento de turmas
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.db.models.turma import Turma, TurmaCreate, TurmaUpdate, TurmaRead
from app.utils.logger import logger


class TurmaManagerService:
    """
    Serviço responsável pelo gerenciamento de turmas (CRUD) usando SQLModel e PostgreSQL
    """

    def __init__(self, db: Session):
        """Inicializa o serviço de gerenciamento de turmas com sessão do banco de dados"""
        self.db = db

    async def create_turma(self, turma_data: TurmaCreate) -> TurmaRead:
        """
        Cria uma nova turma no banco de dados

        Args:
            turma_data: Dados da turma (ano, materia, curso, periodo)

        Returns:
            TurmaRead com informações da turma criada
        """
        turma = Turma(
            ano=turma_data.ano,
            materia=turma_data.materia,
            curso=turma_data.curso,
            periodo=turma_data.periodo
        )

        self.db.add(turma)
        self.db.commit()
        self.db.refresh(turma)

        logger.info(f"Turma created: {turma.id} ({turma.materia} - {turma.curso})")

        return TurmaRead.from_orm(turma)

    async def list_turmas(
        self,
        skip: int = 0,
        limit: int = 100,
        ano: Optional[int] = None,
        materia: Optional[str] = None,
        curso: Optional[str] = None
    ) -> List[TurmaRead]:
        """
        Lista turmas com paginação e filtros opcionais

        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar
            ano: Ano para filtrar (opcional)
            materia: Matéria para filtrar (opcional)
            curso: Curso para filtrar (opcional)

        Returns:
            Lista de TurmaRead
        """
        query = select(Turma)

        if ano:
            query = query.where(Turma.ano == ano)
        if materia:
            query = query.where(Turma.materia.ilike(f"%{materia}%"))
        if curso:
            query = query.where(Turma.curso.ilike(f"%{curso}%"))

        query = query.order_by(Turma.ano.desc(), Turma.materia).offset(skip).limit(limit)

        turmas = self.db.exec(query).all()
        result = [TurmaRead.from_orm(turma) for turma in turmas]

        logger.debug(f"Listed {len(result)} turmas")

        return result

    async def get_turma(self, turma_id: UUID) -> TurmaRead:
        """
        Recupera uma turma específica pelo ID

        Args:
            turma_id: ID da turma

        Returns:
            TurmaRead com dados completos

        Raises:
            HTTPException: Se a turma não for encontrada
        """
        turma = self.db.get(Turma, turma_id)

        if not turma:
            logger.warning(f"Turma not found: {turma_id}")
            raise HTTPException(status_code=404, detail="Turma not found")

        logger.debug(f"Retrieved turma: {turma_id}")

        return TurmaRead.from_orm(turma)

    async def update_turma(self, turma_id: UUID, turma_update: TurmaUpdate) -> TurmaRead:
        """
        Atualiza uma turma existente

        Args:
            turma_id: ID da turma
            turma_update: Dados para atualizar

        Returns:
            TurmaRead com informações atualizadas

        Raises:
            HTTPException: Se a turma não for encontrada
        """
        turma = self.db.get(Turma, turma_id)

        if not turma:
            logger.warning(f"Turma not found for update: {turma_id}")
            raise HTTPException(status_code=404, detail="Turma not found")

        # Atualizar campos se fornecidos
        if turma_update.ano is not None:
            turma.ano = turma_update.ano
        if turma_update.materia is not None:
            turma.materia = turma_update.materia
        if turma_update.curso is not None:
            turma.curso = turma_update.curso
        if turma_update.periodo is not None:
            turma.periodo = turma_update.periodo

        self.db.add(turma)
        self.db.commit()
        self.db.refresh(turma)

        logger.info(f"Turma updated: {turma_id} ({turma.materia} - {turma.curso})")

        return TurmaRead.from_orm(turma)

    async def delete_turma(self, turma_id: UUID) -> dict:
        """
        Exclui uma turma do banco de dados

        Args:
            turma_id: ID da turma

        Returns:
            Dicionário com mensagem de sucesso

        Raises:
            HTTPException: Se a turma não for encontrada
        """
        turma = self.db.get(Turma, turma_id)

        if not turma:
            logger.warning(f"Turma not found for deletion: {turma_id}")
            raise HTTPException(status_code=404, detail="Turma not found")

        self.db.delete(turma)
        self.db.commit()

        logger.info(f"Turma deleted: {turma_id}")

        return {"message": "Turma deleted successfully", "id": str(turma_id)}

    async def count_turmas(
        self,
        ano: Optional[int] = None,
        materia: Optional[str] = None,
        curso: Optional[str] = None
    ) -> int:
        """
        Conta o total de turmas, opcionalmente filtrando

        Args:
            ano: Ano para filtrar (opcional)
            materia: Matéria para filtrar (opcional)
            curso: Curso para filtrar (opcional)

        Returns:
            Número total de turmas
        """
        query = select(func.count(Turma.id))

        if ano:
            query = query.where(Turma.ano == ano)
        if materia:
            query = query.where(Turma.materia.ilike(f"%{materia}%"))
        if curso:
            query = query.where(Turma.curso.ilike(f"%{curso}%"))

        return self.db.exec(query).one()
