"""
Rotas para operações com cartão resposta
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict

from app.services.cartao_resposta_service import CartaoRespostaService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cartao-resposta", tags=["Cartão Resposta"])

# Instancia o serviço
cartao_service = CartaoRespostaService()


@router.post("/scan-qrcode")
async def scan_qrcode(file: UploadFile = File(...)) -> JSONResponse:
    """
    Endpoint para ler QR code de imagem do cartão resposta
    
    Args:
        file: Arquivo de imagem contendo o QR code
        
    Returns:
        JSON com os dados extraídos do QR code (matrícula e turma_prova_id)
    """
    try:
        # Valida tipo de arquivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Arquivo deve ser uma imagem"
            )
        
        # Lê o conteúdo do arquivo
        contents = await file.read()
        
        # Valida tamanho do arquivo
        file_size = len(contents)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Arquivo muito grande. Tamanho máximo permitido: {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB"
            )
        
        # Processa QR code
        success, message, data = cartao_service.read_qr_code(contents)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": message,
                "data": data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar QR code: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar QR code: {str(e)}"
        )
