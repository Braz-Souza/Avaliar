"""
Service para correção de provas usando OpenCV

Este serviço analisa imagens de provas escaneadas e detecta respostas
marcadas, comparando com o gabarito para calcular a nota.
"""

import random


class ExamCorrectorService:
    """
    Serviço responsável pela correção automática de provas usando OpenCV
    """

    def __init__(self):
        """Inicializa o serviço de correção"""


    def validate_answer_key(self, answer_key, num_options: int) -> bool:
        """
        Validação simples do gabarito.

        Aceita lista (ex: ['A','B',...]) ou dict (ex: {0: 'A', 1: 'B', ...}).
        Verifica se cada resposta está entre as primeiras `num_options` letras (A..E).
        Retorna True se válido, False caso contrário.
        """
        valid_options = ['A', 'B', 'C', 'D', 'E'][:max(0, int(num_options))]

        if isinstance(answer_key, dict):
            # valores podem estar como ints ou strings; convert para string maiúscula
            answers = list(answer_key.values())
        elif isinstance(answer_key, list):
            answers = answer_key
        else:
            return False

        for a in answers:
            if a is None:
                continue
            if not isinstance(a, str):
                return False
            if a.upper() not in valid_options:
                return False

        return True

    def process_exam_image(self, image_data: bytes, answer_key_list, num_questions: int, num_options: int):
        """Placeholder temporário - retorna valores fixos"""
        return {
            "total": num_questions,
            "correct": 0,
            "wrong": 0,
            "blank": num_questions,
            "score": 0,
            "score_percentage": 0.0,
            "details": [
                {"question": i, "detected": None, "correct_answer": "", "status": "blank"}
                for i in range(num_questions)
            ]
        }
# Instância singleton do serviço
exam_corrector_service = ExamCorrectorService()
