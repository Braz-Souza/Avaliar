"""
Router para endpoints de sistema (health check, stats, cleanup)
"""

from fastapi import APIRouter, Depends

from app.services.cleanup_service import CleanupService, cleanup_service
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


def get_cleanup_service() -> CleanupService:
    """
    Dependency para obter instância do serviço de limpeza
    
    Returns:
        CleanupService
    """
    return cleanup_service


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
