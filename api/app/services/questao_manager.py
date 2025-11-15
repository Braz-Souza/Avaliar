"""
Service para gerenciamento de questões e opções
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.db.models.questao import (
    Questao, QuestaoCreate, QuestaoUpdate, QuestaoRead,
    QuestaoOpcao, QuestaoOpcaoCreate, QuestaoOpcaoUpdate, QuestaoOpcaoRead
)
from app.utils.logger import logger


class QuestaoManagerService:
    """
    Serviço responsável pelo gerenciamento de questões e opções (CRUD) usando SQLModel e PostgreSQL
    """

    def __init__(self, db: Session):
        """Inicializa o serviço de gerenciamento de questões com sessão do banco de dados"""
        self.db = db

    async def create_questao(self, questao_data: QuestaoCreate) -> QuestaoRead:
        """
        Cria uma nova questão no banco de dados

        Args:
            questao_data: Dados da questão (prova_id, order, text)

        Returns:
            QuestaoRead com informações da questão criada
        """
        # Verificar se já existe uma questão com a mesma ordem na mesma prova
        existing_questao = self.db.exec(
            select(Questao).where(
                Questao.prova_id == questao_data.prova_id,
                Questao.order == questao_data.order
            )
        ).first()

        if existing_questao:
            raise HTTPException(
                status_code=400,
                detail=f"Question with order {questao_data.order} already exists in this prova"
            )

        questao = Questao(**questao_data.dict())
        self.db.add(questao)
        self.db.commit()
        self.db.refresh(questao)

        logger.info(f"Questao created: {questao.id} (order: {questao.order})")

        return QuestaoRead.from_orm(questao)

    async def list_questoes(self, prova_id: UUID) -> List[QuestaoRead]:
        """
        Lista todas as questões de uma prova em ordem

        Args:
            prova_id: ID da prova

        Returns:
            Lista de QuestaoRead ordenadas por order
        """
        query = select(Questao).where(Questao.prova_id == prova_id).order_by(Questao.order)
        questoes = self.db.exec(query).all()
        result = [QuestaoRead.from_orm(questao) for questao in questoes]

        logger.debug(f"Listed {len(result)} questoes for prova {prova_id}")

        return result

    async def get_questao(self, questao_id: UUID) -> QuestaoRead:
        """
        Recupera uma questão específica pelo ID

        Args:
            questao_id: ID da questão

        Returns:
            QuestaoRead com dados completos

        Raises:
            HTTPException: Se a questão não for encontrada
        """
        questao = self.db.get(Questao, questao_id)

        if not questao:
            logger.warning(f"Questao not found: {questao_id}")
            raise HTTPException(status_code=404, detail="Questao not found")

        logger.debug(f"Retrieved questao: {questao_id}")

        return QuestaoRead.from_orm(questao)

    async def update_questao(self, questao_id: UUID, questao_update: QuestaoUpdate) -> QuestaoRead:
        """
        Atualiza uma questão existente

        Args:
            questao_id: ID da questão
            questao_update: Dados para atualizar

        Returns:
            QuestaoRead com informações atualizadas

        Raises:
            HTTPException: Se a questão não for encontrada
        """
        questao = self.db.get(Questao, questao_id)

        if not questao:
            logger.warning(f"Questao not found for update: {questao_id}")
            raise HTTPException(status_code=404, detail="Questao not found")

        # Atualizar campos se fornecidos
        update_data = questao_update.dict(exclude_unset=True)
        if 'order' in update_data:
            # Verificar se já existe uma questão com a nova ordem
            existing_questao = self.db.exec(
                select(Questao).where(
                    Questao.prova_id == questao.prova_id,
                    Questao.order == update_data['order'],
                    Questao.id != questao_id
                )
            ).first()

            if existing_questao:
                raise HTTPException(
                    status_code=400,
                    detail=f"Question with order {update_data['order']} already exists in this prova"
                )

        for field, value in update_data.items():
            setattr(questao, field, value)

        self.db.add(questao)
        self.db.commit()
        self.db.refresh(questao)

        logger.info(f"Questao updated: {questao_id}")

        return QuestaoRead.from_orm(questao)

    async def delete_questao(self, questao_id: UUID) -> dict:
        """
        Exclui uma questão do banco de dados (e suas opções por CASCADE)

        Args:
            questao_id: ID da questão

        Returns:
            Dicionário com mensagem de sucesso

        Raises:
            HTTPException: Se a questão não for encontrada
        """
        questao = self.db.get(Questao, questao_id)

        if not questao:
            logger.warning(f"Questao not found for deletion: {questao_id}")
            raise HTTPException(status_code=404, detail="Questao not found")

        self.db.delete(questao)
        self.db.commit()

        logger.info(f"Questao deleted: {questao_id}")

        return {"message": "Questao deleted successfully", "id": str(questao_id)}

    # Métodos para opções de questões

    async def create_opcao(self, opcao_data: QuestaoOpcaoCreate) -> QuestaoOpcaoRead:
        """
        Cria uma nova opção para uma questão

        Args:
            opcao_data: Dados da opção

        Returns:
            QuestaoOpcaoRead com informações da opção criada
        """
        # Verificar se já existe uma opção com a mesma ordem na mesma questão
        existing_opcao = self.db.exec(
            select(QuestaoOpcao).where(
                QuestaoOpcao.questao_id == opcao_data.questao_id,
                QuestaoOpcao.order == opcao_data.order
            )
        ).first()

        if existing_opcao:
            raise HTTPException(
                status_code=400,
                detail=f"Option with order {opcao_data.order} already exists in this questao"
            )

        opcao = QuestaoOpcao(**opcao_data.dict())
        self.db.add(opcao)
        self.db.commit()
        self.db.refresh(opcao)

        logger.info(f"QuestaoOpcao created: {opcao.id} (order: {opcao.order})")

        return QuestaoOpcaoRead.from_orm(opcao)

    async def list_opcoes(self, questao_id: UUID) -> List[QuestaoOpcaoRead]:
        """
        Lista todas as opções de uma questão em ordem

        Args:
            questao_id: ID da questão

        Returns:
            Lista de QuestaoOpcaoRead ordenadas por order
        """
        query = select(QuestaoOpcao).where(
            QuestaoOpcao.questao_id == questao_id
        ).order_by(QuestaoOpcao.order)

        opcoes = self.db.exec(query).all()
        result = [QuestaoOpcaoRead.from_orm(opcao) for opcao in opcoes]

        logger.debug(f"Listed {len(result)} opcoes for questao {questao_id}")

        return result

    async def update_opcao(self, opcao_id: UUID, opcao_update: QuestaoOpcaoUpdate) -> QuestaoOpcaoRead:
        """
        Atualiza uma opção existente

        Args:
            opcao_id: ID da opção
            opcao_update: Dados para atualizar

        Returns:
            QuestaoOpcaoRead com informações atualizadas
        """
        opcao = self.db.get(QuestaoOpcao, opcao_id)

        if not opcao:
            logger.warning(f"QuestaoOpcao not found for update: {opcao_id}")
            raise HTTPException(status_code=404, detail="QuestaoOpcao not found")

        # Se estiver marcando como correta, desmarcar outras opções
        update_data = opcao_update.dict(exclude_unset=True)
        if update_data.get('is_correct'):
            # Desmarcar outras opções corretas da mesma questão
            self.db.exec(
                select(QuestaoOpcao).where(
                    QuestaoOpcao.questao_id == opcao.questao_id,
                    QuestaoOpcao.id != opcao_id
                )
            ).all()

            for other_opcao in self.db.exec(
                select(QuestaoOpcao).where(
                    QuestaoOpcao.questao_id == opcao.questao_id,
                    QuestaoOpcao.id != opcao_id
                )
            ).all():
                other_opcao.is_correct = False
                self.db.add(other_opcao)

        for field, value in update_data.items():
            setattr(opcao, field, value)

        self.db.add(opcao)
        self.db.commit()
        self.db.refresh(opcao)

        logger.info(f"QuestaoOpcao updated: {opcao_id}")

        return QuestaoOpcaoRead.from_orm(opcao)

    async def delete_opcao(self, opcao_id: UUID) -> dict:
        """
        Exclui uma opção do banco de dados

        Args:
            opcao_id: ID da opção

        Returns:
            Dicionário com mensagem de sucesso
        """
        opcao = self.db.get(QuestaoOpcao, opcao_id)

        if not opcao:
            logger.warning(f"QuestaoOpcao not found for deletion: {opcao_id}")
            raise HTTPException(status_code=404, detail="QuestaoOpcao not found")

        self.db.delete(opcao)
        self.db.commit()

        logger.info(f"QuestaoOpcao deleted: {opcao_id}")

        return {"message": "QuestaoOpcao deleted successfully", "id": str(opcao_id)}
