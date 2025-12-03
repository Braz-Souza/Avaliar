"""
Service para gerenciamento de provas
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.db.models.prova import Prova, ProvaCreate, ProvaUpdate, ProvaRead
from app.db.models.questao import Questao, QuestaoOpcao
from app.services.latex_parser import LaTeXParserService
from app.utils.logger import logger


class ProvaManagerService:
    """
    Serviço responsável pelo gerenciamento de provas (CRUD) usando SQLModel e PostgreSQL
    """

    def __init__(self, db: Session):
        """Inicializa o serviço de gerenciamento de provas com sessão do banco de dados"""
        self.db = db

    async def save_prova(self, prova_data: ProvaCreate, created_by: Optional[UUID] = None) -> ProvaRead:
        """
        Salva uma nova prova no banco de dados e cria questões estruturadas

        Args:
            prova_data: Dados da prova (nome e conteúdo)
            created_by: ID do usuário que criou a prova (opcional)

        Returns:
            ProvaRead com informações da prova salva
        """
        prova = Prova(
            name=prova_data.name,
            content=prova_data.content,
            created_by=created_by
        )

        self.db.add(prova)
        self.db.commit()
        self.db.refresh(prova)

        try:
            questoes_data = LaTeXParserService.parse_to_questoes(prova_data.content)

            if questoes_data:
                for questao_info in questoes_data:
                    questao = Questao(
                        prova_id=prova.id,
                        order=questao_info['order'],
                        text=questao_info['text']
                    )
                    self.db.add(questao)
                    self.db.flush()

                    for opcao_info in questao_info['opcoes']:
                        opcao = QuestaoOpcao(
                            questao_id=questao.id,
                            order=opcao_info['order'],
                            text=opcao_info['text'],
                            is_correct=opcao_info['is_correct']
                        )
                        self.db.add(opcao)

                self.db.commit()
                logger.info(f"Prova saved with {len(questoes_data)} questoes: {prova.id} ({prova.name})")
            else:
                logger.warning(f"Prova saved without questoes (no structured content found): {prova.id} ({prova.name})")
        except Exception as e:
            logger.error(f"Error parsing questoes for prova {prova.id}: {e}")

        self.db.refresh(prova)
        return ProvaRead.from_orm(prova)

    async def list_provas(
        self,
        skip: int = 0,
        limit: int = 100,
        created_by: Optional[UUID] = None
    ) -> List[ProvaRead]:
        """
        Lista provas com paginação e filtro opcional por usuário

        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar
            created_by: ID do usuário para filtrar (opcional)

        Returns:
            Lista de ProvaRead ordenadas por data de modificação
        """
        query = select(Prova).where(Prova.deleted == False)

        if created_by:
            query = query.where(Prova.created_by == created_by)

        query = query.order_by(Prova.modified_at.desc()).offset(skip).limit(limit)

        provas = self.db.exec(query).all()
        result = [ProvaRead.from_orm(prova) for prova in provas]

        logger.debug(f"Listed {len(result)} provas")

        return result

    async def get_prova(self, prova_id: UUID) -> ProvaRead:
        """
        Recupera uma prova específica pelo ID

        Args:
            prova_id: ID da prova

        Returns:
            ProvaRead com dados completos

        Raises:
            HTTPException: Se a prova não for encontrada
        """
        prova = self.db.get(Prova, prova_id)

        if not prova:
            logger.warning(f"Prova not found: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")

        logger.debug(f"Retrieved prova: {prova_id}")

        return ProvaRead.from_orm(prova)

    async def update_prova(self, prova_id: UUID, prova_update: ProvaUpdate) -> ProvaRead:
        """
        Atualiza uma prova existente

        Args:
            prova_id: ID da prova
            prova_update: Dados para atualizar

        Returns:
            ProvaRead com informações atualizadas

        Raises:
            HTTPException: Se a prova não for encontrada
        """
        prova = self.db.get(Prova, prova_id)

        if not prova or prova.deleted:
            logger.warning(f"Prova not found for update: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")

        # Atualizar campos se fornecidos
        if prova_update.name is not None:
            prova.name = prova_update.name
        if prova_update.content is not None:
            prova.content = prova_update.content

        self.db.add(prova)
        self.db.commit()
        self.db.refresh(prova)

        if prova_update.content is not None:
            try:
                old_questoes = self.db.exec(
                    select(Questao).where(Questao.prova_id == prova_id)
                ).all()

                for questao in old_questoes:
                    old_opcoes = self.db.exec(
                        select(QuestaoOpcao).where(QuestaoOpcao.questao_id == questao.id)
                    ).all()
                    for opcao in old_opcoes:
                        self.db.delete(opcao)
                    self.db.delete(questao)

                self.db.commit()

                questoes_data = LaTeXParserService.parse_to_questoes(prova.content)

                if questoes_data:
                    for questao_info in questoes_data:
                        questao = Questao(
                            prova_id=prova.id,
                            order=questao_info['order'],
                            text=questao_info['text']
                        )
                        self.db.add(questao)
                        self.db.flush()

                        for opcao_info in questao_info['opcoes']:
                            opcao = QuestaoOpcao(
                                questao_id=questao.id,
                                order=opcao_info['order'],
                                text=opcao_info['text'],
                                is_correct=opcao_info['is_correct']
                            )
                            self.db.add(opcao)

                    self.db.commit()
                    logger.info(f"Prova updated with {len(questoes_data)} questoes: {prova_id} ({prova.name})")
                else:
                    logger.warning(f"Prova updated without questoes (no structured content found): {prova_id} ({prova.name})")
            except Exception as e:
                logger.error(f"Error parsing questoes for updated prova {prova_id}: {e}")
        else:
            logger.info(f"Prova updated: {prova_id} ({prova.name})")

        self.db.refresh(prova)

        return ProvaRead.from_orm(prova)

    async def delete_prova(self, prova_id: UUID) -> dict:
        """
        Marca uma prova como deletada (soft delete)

        Args:
            prova_id: ID da prova

        Returns:
            Dicionário com mensagem de sucesso

        Raises:
            HTTPException: Se a prova não for encontrada
        """
        prova = self.db.get(Prova, prova_id)

        if not prova or prova.deleted:
            logger.warning(f"Prova not found for deletion: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")

        prova.deleted = True
        self.db.add(prova)
        self.db.commit()

        logger.info(f"Prova marked as deleted: {prova_id}")

        return {"message": "Prova deleted successfully", "id": str(prova_id)}

    async def count_provas(self, created_by: Optional[UUID] = None) -> int:
        """
        Conta o total de provas, opcionalmente filtrando por usuário

        Args:
            created_by: ID do usuário para filtrar (opcional)

        Returns:
            Número total de provas
        """
        query = select(func.count(Prova.id)).where(Prova.deleted == False)

        if created_by:
            query = query.where(Prova.created_by == created_by)

        return self.db.exec(query).one()

    async def get_prova_with_questoes(self, prova_id: UUID) -> dict:
        """
        Recupera uma prova específica com suas questões estruturadas

        Args:
            prova_id: ID da prova

        Returns:
            Dicionário com dados da prova e questões estruturadas

        Raises:
            HTTPException: Se a prova não for encontrada
        """
        prova = self.db.get(Prova, prova_id)

        if not prova or prova.deleted:
            logger.warning(f"Prova not found: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")

        # Buscar questões com opções
        query = select(Questao).where(Questao.prova_id == prova_id).order_by(Questao.order)
        questoes = self.db.exec(query).all()

        questoes_data = []
        for questao in questoes:
            # Buscar opções da questão
            opcoes_query = select(QuestaoOpcao).where(
                QuestaoOpcao.questao_id == questao.id
            ).order_by(QuestaoOpcao.order)
            opcoes = self.db.exec(opcoes_query).all()

            questoes_data.append({
                "id": str(questao.id),
                "order": questao.order,
                "text": questao.text,
                "opcoes": [
                    {
                        "id": str(opcao.id),
                        "order": opcao.order,
                        "text": opcao.text,
                        "is_correct": opcao.is_correct
                    }
                    for opcao in opcoes
                ]
            })

        logger.debug(f"Retrieved prova with {len(questoes_data)} questoes: {prova_id}")

        return {
            "id": str(prova.id),
            "name": prova.name,
            "content": prova.content,
            "created_at": prova.created_at,
            "modified_at": prova.modified_at,
            "created_by": str(prova.created_by) if prova.created_by else None,
            "questoes": questoes_data
        }

    async def save_prova_with_questoes(
        self,
        prova_data: dict,
        created_by: Optional[UUID] = None
    ) -> dict:
        """
        Salva uma prova com questões estruturadas

        Args:
            prova_data: Dados da prova incluindo questões estruturadas
            created_by: ID do usuário que criou a prova (opcional)

        Returns:
            Dicionário com informações da prova salva com questões
        """
        # Criar prova
        prova = Prova(
            name=prova_data["name"],
            content=prova_data.get("content", ""),  # Manter conteúdo para compatibilidade
            created_by=created_by
        )

        self.db.add(prova)
        self.db.commit()
        self.db.refresh(prova)

        # Salvar questões
        questoes_salvas = []
        for idx, questao_data in enumerate(prova_data.get("questoes", [])):
            questao = Questao(
                prova_id=prova.id,
                order=questao_data.get("order", idx + 1),
                text=questao_data["text"]
            )

            self.db.add(questao)
            self.db.commit()
            self.db.refresh(questao)

            # Salvar opções
            opcoes_salvas = []
            for opt_idx, opcao_data in enumerate(questao_data.get("opcoes", [])):
                opcao = QuestaoOpcao(
                    questao_id=questao.id,
                    order=opcao_data.get("order", opt_idx + 1),
                    text=opcao_data["text"],
                    is_correct=opcao_data.get("is_correct", False)
                )

                self.db.add(opcao)
                self.db.commit()
                self.db.refresh(opcao)

                opcoes_salvas.append({
                    "id": str(opcao.id),
                    "order": opcao.order,
                    "text": opcao.text,
                    "is_correct": opcao.is_correct
                })

            questoes_salvas.append({
                "id": str(questao.id),
                "order": questao.order,
                "text": questao.text,
                "opcoes": opcoes_salvas
            })

        # Atualizar conteúdo LaTeX gerado a partir das questões estruturadas
        prova.content = LaTeXParserService.questoes_to_latex(questoes_salvas)
        self.db.add(prova)
        self.db.commit()
        self.db.refresh(prova)

        logger.info(f"Prova saved with questoes: {prova.id} ({prova.name})")

        return {
            "id": str(prova.id),
            "name": prova.name,
            "content": prova.content,
            "created_at": prova.created_at,
            "modified_at": prova.modified_at,
            "created_by": str(prova.created_by) if prova.created_by else None,
            "questoes": questoes_salvas
        }
