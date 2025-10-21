"""
Service para gerenciamento de provas
"""

import re
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException

from app.core.config import settings
from app.models.prova import ProvaData, ProvaInfo
from app.utils.logger import logger


class ProvaManagerService:
    """
    Serviço responsável pelo gerenciamento de provas (CRUD)
    """
    
    def __init__(self):
        """Inicializa o serviço de gerenciamento de provas"""
        self.latex_sources_dir = settings.LATEX_SOURCES_DIR
        self.pdf_output_dir = settings.PDF_OUTPUT_DIR
    
    async def save_prova(self, prova: ProvaData) -> ProvaInfo:
        """
        Salva uma nova prova no sistema
        
        Args:
            prova: Dados da prova (nome e conteúdo)
            
        Returns:
            ProvaInfo com informações da prova salva
        """
        # Sanitizar nome do arquivo
        safe_name = self._sanitize_filename(prova.name)
        
        # Criar ID único baseado no nome e timestamp
        prova_id = f"{safe_name}_{int(datetime.now().timestamp())}"
        
        # Salvar conteúdo LaTeX
        latex_file = self.latex_sources_dir / f"{prova_id}.tex"
        latex_file.write_text(prova.content, encoding='utf-8')
        
        logger.info(f"Prova saved: {prova_id} ({prova.name})")
        
        # Retornar informações da prova
        return self._create_prova_info(latex_file, prova_id, prova.name)
    
    async def list_provas(self) -> list[ProvaInfo]:
        """
        Lista todas as provas salvas
        
        Returns:
            Lista de ProvaInfo ordenadas por data de modificação
        """
        provas = []
        
        for latex_file in self.latex_sources_dir.glob("*.tex"):
            prova_id = latex_file.stem
            
            # Extrair nome original do ID (remover timestamp)
            name = self._extract_name_from_id(prova_id)
            
            # Criar info da prova
            prova_info = self._create_prova_info(latex_file, prova_id, name)
            provas.append(prova_info)
        
        # Ordenar por data de modificação (mais recentes primeiro)
        provas.sort(key=lambda p: p.modified_at, reverse=True)
        
        logger.debug(f"Listed {len(provas)} provas")
        
        return provas
    
    async def get_prova(self, prova_id: str) -> ProvaData:
        """
        Recupera uma prova específica pelo ID
        
        Args:
            prova_id: ID da prova
            
        Returns:
            ProvaData com nome e conteúdo
            
        Raises:
            HTTPException: Se a prova não for encontrada
        """
        latex_file = self.latex_sources_dir / f"{prova_id}.tex"
        
        if not latex_file.exists():
            logger.warning(f"Prova not found: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")
        
        # Ler conteúdo
        content = latex_file.read_text(encoding='utf-8')
        
        # Extrair nome do ID
        name = self._extract_name_from_id(prova_id)
        
        logger.debug(f"Retrieved prova: {prova_id}")
        
        return ProvaData(name=name, content=content)
    
    async def update_prova(self, prova_id: str, prova: ProvaData) -> ProvaInfo:
        """
        Atualiza uma prova existente
        
        Args:
            prova_id: ID da prova
            prova: Novos dados da prova
            
        Returns:
            ProvaInfo com informações atualizadas
            
        Raises:
            HTTPException: Se a prova não for encontrada
        """
        latex_file = self.latex_sources_dir / f"{prova_id}.tex"
        
        if not latex_file.exists():
            logger.warning(f"Prova not found for update: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")
        
        # Atualizar conteúdo
        latex_file.write_text(prova.content, encoding='utf-8')
        
        logger.info(f"Prova updated: {prova_id} ({prova.name})")
        
        # Retornar informações atualizadas
        return self._create_prova_info(latex_file, prova_id, prova.name)
    
    async def delete_prova(self, prova_id: str) -> dict:
        """
        Exclui uma prova do sistema
        
        Args:
            prova_id: ID da prova
            
        Returns:
            Dicionário com mensagem de sucesso
            
        Raises:
            HTTPException: Se a prova não for encontrada
        """
        latex_file = self.latex_sources_dir / f"{prova_id}.tex"
        
        if not latex_file.exists():
            logger.warning(f"Prova not found for deletion: {prova_id}")
            raise HTTPException(status_code=404, detail="Prova not found")
        
        # Excluir arquivo LaTeX
        latex_file.unlink()
        
        # Excluir PDF associado se existir
        pdf_file = self.pdf_output_dir / f"{prova_id}.pdf"
        if pdf_file.exists():
            pdf_file.unlink()
            logger.debug(f"Associated PDF deleted: {prova_id}.pdf")
        
        logger.info(f"Prova deleted: {prova_id}")
        
        return {"message": "Prova deleted successfully", "id": prova_id}
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Remove caracteres inválidos do nome do arquivo
        
        Args:
            name: Nome original
            
        Returns:
            Nome sanitizado
        """
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        if not safe_name:
            safe_name = "prova"
        return safe_name
    
    def _extract_name_from_id(self, prova_id: str) -> str:
        """
        Extrai o nome original do ID da prova
        
        Args:
            prova_id: ID no formato nome_timestamp
            
        Returns:
            Nome original (com underscores substituídos por espaços)
        """
        name_parts = prova_id.rsplit('_', 1)
        name = name_parts[0].replace('_', ' ')
        return name
    
    def _create_prova_info(
        self, 
        latex_file: Path, 
        prova_id: str, 
        name: str
    ) -> ProvaInfo:
        """
        Cria objeto ProvaInfo a partir de um arquivo
        
        Args:
            latex_file: Caminho do arquivo .tex
            prova_id: ID da prova
            name: Nome da prova
            
        Returns:
            ProvaInfo com metadados
        """
        stats = latex_file.stat()
        created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
        modified_at = datetime.fromtimestamp(stats.st_mtime).isoformat()
        
        return ProvaInfo(
            id=prova_id,
            name=name,
            created_at=created_at,
            modified_at=modified_at
        )
