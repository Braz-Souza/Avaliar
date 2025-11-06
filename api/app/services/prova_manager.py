"""
Service para gerenciamento de provas
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select, func

from app.db.models.prova import Prova, ProvaCreate, ProvaUpdate, ProvaRead
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
        Salva uma nova prova no banco de dados
        
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
        
        logger.info(f"Prova saved: {prova.id} ({prova.name})")
        
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
        query = select(Prova)
        
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
        
        if not prova:
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
        
        logger.info(f"Prova updated: {prova_id} ({prova.name})")
        
        return ProvaRead.from_orm(prova)
    
    async def delete_prova(self, prova_id: UUID) -> dict:
        """
        Exclui uma prova do banco de dados
        
        Args:
            prova_id: ID da prova
            
        Returns:
            Dicionário com mensagem de sucesso
            
        Raises:
            HTTPException: Se a prova não for encontrada
        """
        prova = self.db.get(Prova, prova_id)
        
        if not prova:
            logger.warning(f"Prova not found for deletion: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")
        
        self.db.delete(prova)
        self.db.commit()
        
        logger.info(f"Prova deleted: {prova_id}")
        
        return {"message": "Prova deleted successfully", "id": str(prova_id)}
    
    async def count_provas(self, created_by: Optional[UUID] = None) -> int:
        """
        Conta o total de provas, opcionalmente filtrando por usuário
        
        Args:
            created_by: ID do usuário para filtrar (opcional)
            
        Returns:
            Número total de provas
        """
        query = select(func.count(Prova.id))
        
        if created_by:
            query = query.where(Prova.created_by == created_by)
        
        return self.db.exec(query).one()
