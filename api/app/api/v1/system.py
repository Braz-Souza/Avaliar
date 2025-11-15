"""
Router para endpoints de sistema (health check, stats, cleanup)
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.services.cleanup_service import CleanupService, cleanup_service
from app.services.migration_service import MigrationService
from app.core.config import settings
from app.core.database import get_db
from app.utils.logger import logger

router = APIRouter(prefix="/system", tags=["System"])


def get_cleanup_service() -> CleanupService:
    """
    Dependency para obter instância do serviço de limpeza

    Returns:
        CleanupService
    """
    return cleanup_service


def get_migration_service(db: Session = Depends(get_db)) -> MigrationService:
    """
    Dependency para obter instância do serviço de migração

    Args:
        db: Sessão do banco de dados

    Returns:
        MigrationService
    """
    return MigrationService(db)


@router.get("/health")
async def health_check(
    cleanup: CleanupService = Depends(get_cleanup_service)
) -> dict:
    """
    Endpoint para verificar se a API está funcionando

    Args:
        cleanup: Serviço de limpeza (injetado)

    Returns:
        Dicionário com status e estatísticas básicas
    """
    temp_stats = cleanup.get_temp_pdf_stats()
    saved_stats = cleanup.get_saved_pdf_stats()

    return {
        "status": "healthy",
        "temp_pdfs": temp_stats["count"],
        "saved_pdfs": saved_stats["count"],
        "temp_pdf_ttl_minutes": settings.TEMP_PDF_TTL_MINUTES,
        "max_temp_pdfs": settings.MAX_TEMP_PDFS
    }


@router.post("/cleanup")
async def manual_cleanup(
    cleanup: CleanupService = Depends(get_cleanup_service)
) -> dict:
    """
    Endpoint para executar limpeza manual de PDFs temporários

    Args:
        cleanup: Serviço de limpeza (injetado)

    Returns:
        Dicionário com resultado da limpeza
    """
    removed = cleanup.cleanup_temp_pdfs()
    remaining = cleanup.get_temp_pdf_stats()["count"]

    return {
        "success": True,
        "removed_count": removed,
        "remaining_temp_pdfs": remaining
    }


@router.get("/stats")
async def get_stats(
    cleanup: CleanupService = Depends(get_cleanup_service)
) -> dict:
    """
    Retorna estatísticas detalhadas sobre armazenamento

    Args:
        cleanup: Serviço de limpeza (injetado)

    Returns:
        Dicionário com estatísticas completas
    """
    temp_stats = cleanup.get_temp_pdf_stats()
    saved_stats = cleanup.get_saved_pdf_stats()

    return {
        "temp_pdfs": temp_stats,
        "saved_pdfs": saved_stats,
        "config": {
            "ttl_minutes": settings.TEMP_PDF_TTL_MINUTES,
            "max_temp_pdfs": settings.MAX_TEMP_PDFS,
            "cleanup_interval_minutes": settings.CLEANUP_INTERVAL_MINUTES
        }
    }


@router.get("/migration/status")
async def get_migration_status(
    migration: MigrationService = Depends(get_migration_service)
) -> dict:
    """
    Verifica o status da migração de dados para o novo formato estruturado

    Args:
        migration: Serviço de migração (injetado)

    Returns:
        Dicionário com status da migração
    """
    return migration.get_migration_status()


@router.post("/migration/run")
async def run_migration(
    migration: MigrationService = Depends(get_migration_service)
) -> dict:
    """
    Executa a migração de dados existentes para o novo formato estruturado

    Args:
        migration: Serviço de migração (injetado)

    Returns:
        Dicionário com resultado da migração
    """
    logger.info("Starting data migration...")
    result = migration.migrate_all_provas_to_questoes()
    logger.info(f"Migration completed: {result}")

    return {
        "success": True,
        "migration_result": result
    }
