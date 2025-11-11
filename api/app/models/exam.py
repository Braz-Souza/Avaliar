"""
Modelos Pydantic para correção de provas
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class QuestionDetail(BaseModel):
    """
    Detalhes de uma questão corrigida
    """
    question: int = Field(..., description="Número da questão")
    detected: Optional[str] = Field(None, description="Resposta detectada na prova")
    correct_answer: str = Field(..., description="Resposta correta do gabarito")
    status: str = Field(..., description="Status: correct, wrong ou blank")


class ExamCorrectionResult(BaseModel):
    """
    Resultado da correção de uma prova
    """
    total: int = Field(..., description="Total de questões")
    correct: int = Field(..., description="Questões corretas")
    wrong: int = Field(..., description="Questões erradas")
    blank: int = Field(..., description="Questões em branco")
    score: int = Field(..., description="Pontuação (questões corretas)")
    score_percentage: float = Field(..., description="Percentual de acerto")
    details: List[QuestionDetail] = Field(..., description="Detalhes de cada questão")
    exam_id: Optional[int] = Field(None, description="ID da prova (em lote)")
    error: Optional[str] = Field(None, description="Mensagem de erro, se houver")


class BatchExamCorrectionRequest(BaseModel):
    """
    Request para correção de múltiplas provas em lote
    """
    answer_key: List[str] = Field(
        ...,
        description="Gabarito da prova",
        min_length=1
    )
    num_questions: int = Field(
        ...,
        description="Número de questões na prova",
        gt=0
    )
    num_options: int = Field(
        default=5,
        description="Número de opções por questão",
        ge=2,
        le=5
    )

    @field_validator('answer_key')
    @classmethod
    def validate_answer_key(cls, v: List[str]) -> List[str]:
        """Valida se as respostas estão no formato correto"""
        valid_options = ['A', 'B', 'C', 'D', 'E']
        for answer in v:
            if answer not in valid_options:
                raise ValueError(f"Resposta inválida: {answer}. Use apenas A, B, C, D ou E")
        return v
