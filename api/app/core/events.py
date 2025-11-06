"""
Event handlers para startup e shutdown da aplicação
"""

import asyncio

from app.services.cleanup_service import cleanup_service
from app.core.database import create_db_and_tables
from app.utils.logger import logger
# Import models to ensure they are registered with SQLModel
from app.db.models import User, Prova


async def startup_handler() -> None:
    """
    Handler executado ao iniciar a aplicação
    """
    logger.info("Application starting up...")
    
    # Inicializar tabelas do banco de dados
    try:
        create_db_and_tables()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
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
