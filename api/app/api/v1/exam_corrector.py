"""
Router para endpoints de correção automática de provas com OpenCV
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import json

from app.models.exam import (
    ExamCorrectionResult,
    QuestionDetail
)
from app.services.exam_corrector import ExamCorrectorService, exam_corrector_service
from app.utils.logger import logger
from app.core.config import settings

router = APIRouter(prefix="/exam-corrector", tags=["Exam Correction"])


def get_exam_corrector() -> ExamCorrectorService:
    """
    Dependency para obter instância do serviço de correção

    Returns:
        ExamCorrectorService
    """
    return exam_corrector_service


@router.post("/correct", response_model=ExamCorrectionResult)
async def correct_exam(
    file: UploadFile = File(..., description="Imagem da prova escaneada"),
    answer_key: str = Form(..., description="Gabarito em JSON (ex: {0: 1, 1: 0...)"),
    num_questions: int = Form(..., description="Número de questões"),
    num_options: int = Form(5, description="Número de opções por questão (2-5)"),
    corrector: ExamCorrectorService = Depends(get_exam_corrector)
) -> ExamCorrectionResult:
    """
    Corrige uma prova a partir de uma imagem escaneada

    Aceita uma imagem da prova, o gabarito e parâmetros de configuração,
    e retorna o resultado da correção automática usando OpenCV.

    Args:
        file: Imagem da prova (JPG, PNG, etc)
        answer_key: Gabarito em formato JSON string
        num_questions: Total de questões
        num_options: Opções por questão (padrão 5)
        corrector: Serviço de correção (injetado)

    Returns:
        ExamCorrectionResult com detalhes da correção

    Raises:
        HTTPException: Se houver erro no processamento
    """
    try:
        # Validar tipo de arquivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Arquivo deve ser uma imagem (JPG, PNG, etc)"
            )
        
        # Ler conteúdo do arquivo para validar tamanho
        contents = await file.read()
        file_size = len(contents)
        
        # Validar tamanho do arquivo
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Arquivo muito grande. Tamanho máximo permitido: {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB"
            )
        
        # Resetar o ponteiro do arquivo para o início
        await file.seek(0)

        # Parsear gabarito do JSON
        try:
            answer_key_list = json.loads(answer_key)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Gabarito deve estar em formato JSON válido"
            )

        # Validar gabarito
        if not corrector.validate_answer_key(answer_key_list, num_options):
            raise HTTPException(
                status_code=400,
                detail=f"Gabarito inválido. Use apenas as primeiras {num_options} letras (A-E)"
            )

        # Validar número de questões
        if len(answer_key_list) != num_questions:
            raise HTTPException(
                status_code=400,
                detail=f"Gabarito tem {len(answer_key_list)} respostas, mas num_questions é {num_questions}"
            )

        # Ler imagem
        image_data = await file.read()

        if len(image_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Imagem vazia"
            )

        logger.info(f"Corrigindo prova: {file.filename}, {num_questions} questões")

        # Processar prova
        result = corrector.process_exam_image(
            image_data,
            answer_key_list,
            num_questions,
            num_options
        )

        # Converter para modelo Pydantic
        details = [QuestionDetail(**d) for d in result["details"]]

        return ExamCorrectionResult(
            total=result["total"],
            correct=result["correct"],
            wrong=result["wrong"],
            blank=result["blank"],
            score=result["score"],
            score_percentage=result["score_percentage"],
            details=details
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao corrigir prova: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar prova: {str(e)}"
        )