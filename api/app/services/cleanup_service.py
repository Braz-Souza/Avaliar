"""
Service para limpeza de PDFs temporários
"""

import asyncio
from pathlib import Path
from datetime import datetime, timedelta

from app.core.config import settings
from app.utils.logger import logger


class CleanupService:
    """
    Serviço responsável pela limpeza de PDFs temporários
    """
    
    def __init__(self):
        """Inicializa o serviço de limpeza"""
        self.temp_pdf_dir = settings.TEMP_PDF_DIR
        self.ttl_minutes = settings.TEMP_PDF_TTL_MINUTES
        self.max_pdfs = settings.MAX_TEMP_PDFS
        self.cleanup_interval = settings.CLEANUP_INTERVAL_MINUTES
    
    def cleanup_temp_pdfs(self) -> int:
        """
        Remove PDFs temporários que excederam o TTL ou limite de quantidade
        
        Returns:
            Número de PDFs removidos
        """
        try:
            now = datetime.now()
            removed_count = 0
            
            # Listar todos os PDFs temporários com suas datas de modificação
            temp_pdfs = []
            for pdf_file in self.temp_pdf_dir.glob("*.pdf"):
                mtime = datetime.fromtimestamp(pdf_file.stat().st_mtime)
                temp_pdfs.append((pdf_file, mtime))
            
            # Ordenar por data (mais antigos primeiro)
            temp_pdfs.sort(key=lambda x: x[1])
            
            # Remover PDFs expirados (baseado em TTL)
            ttl_threshold = now - timedelta(minutes=self.ttl_minutes)
            for pdf_file, mtime in temp_pdfs[:]:
                if mtime < ttl_threshold:
                    pdf_file.unlink()
                    temp_pdfs.remove((pdf_file, mtime))
                    removed_count += 1
                    logger.info(f"Removed expired temp PDF: {pdf_file.name}")
            
            # Remover excesso de PDFs (baseado em quantidade máxima)
            if len(temp_pdfs) > self.max_pdfs:
                excess = len(temp_pdfs) - self.max_pdfs
                for pdf_file, _ in temp_pdfs[:excess]:
                    pdf_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed excess temp PDF: {pdf_file.name}")
            
            if removed_count > 0:
                logger.info(f"Cleanup completed: {removed_count} temp PDFs removed")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return 0
    
    async def periodic_cleanup(self):
        """
        Task em background que executa limpeza periódica
        """
        logger.info(
            f"Started periodic cleanup (interval: {self.cleanup_interval} min, "
            f"TTL: {self.ttl_minutes} min)"
        )
        
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval * 60)
                self.cleanup_temp_pdfs()
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {str(e)}")
    
    def get_temp_pdf_stats(self) -> dict:
        """
        Retorna estatísticas sobre PDFs temporários
        
        Returns:
            Dicionário com estatísticas
        """
        temp_pdfs = list(self.temp_pdf_dir.glob("*.pdf"))
        
        if not temp_pdfs:
            return {
                "count": 0,
                "size_mb": 0,
                "oldest_age_minutes": None
            }
        
        # Calcular tamanho total
        temp_size = sum(f.stat().st_size for f in temp_pdfs)
        
        # Calcular idade do PDF mais antigo
        now = datetime.now()
        oldest_mtime = min(datetime.fromtimestamp(f.stat().st_mtime) for f in temp_pdfs)
        oldest_age = (now - oldest_mtime).total_seconds() / 60  # em minutos
        
        return {
            "count": len(temp_pdfs),
            "size_mb": round(temp_size / (1024 * 1024), 2),
            "oldest_age_minutes": round(oldest_age, 2)
        }
    
    def get_saved_pdf_stats(self) -> dict:
        """
        Retorna estatísticas sobre PDFs salvos
        
        Returns:
            Dicionário com estatísticas
        """
        saved_pdfs = list(settings.PDF_OUTPUT_DIR.glob("*.pdf"))
        
        if not saved_pdfs:
            return {
                "count": 0,
                "size_mb": 0
            }
        
        # Calcular tamanho total
        saved_size = sum(f.stat().st_size for f in saved_pdfs)
        
        return {
            "count": len(saved_pdfs),
            "size_mb": round(saved_size / (1024 * 1024), 2)
        }


# Instância global do serviço de limpeza
cleanup_service = CleanupService()
