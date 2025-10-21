"""
Event handlers para startup e shutdown da aplicação
"""

import asyncio

from app.services.cleanup_service import cleanup_service
from app.utils.logger import logger


async def startup_handler() -> None:
    """
    Handler executado ao iniciar a aplicação
    """
    logger.info("Application starting up...")
    
    # Executar limpeza inicial de PDFs temporários
    removed = cleanup_service.cleanup_temp_pdfs()
    logger.info(f"Initial cleanup: {removed} temp PDFs removed")
    
    # Iniciar tarefa de limpeza periódica em background
    asyncio.create_task(cleanup_service.periodic_cleanup())
    
    logger.info("Application startup complete")


async def shutdown_handler() -> None:
    """
    Handler executado ao encerrar a aplicação
    """
    logger.info("Application shutting down...")
    
    # Executar limpeza final (opcional)
    # cleanup_service.cleanup_temp_pdfs()
    
    logger.info("Application shutdown complete")
