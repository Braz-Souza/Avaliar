"""
Service para parsing de conteúdo LaTeX em questões estruturadas
"""

from typing import List


class LaTeXParserService:
    """
    Serviço responsável por fazer parsing de conteúdo LaTeX
    e converter para formato estruturado de questões
    """

    @staticmethod
    def parse_to_questoes(latex_content: str) -> List[dict]:
        """
        Converte conteúdo LaTeX para formato estruturado de questões

        Args:
            latex_content: Conteúdo LaTeX da prova no formato:
                Q: Pergunta aqui?
                a) Opção A
                b) Opção B *
                c) Opção C

        Returns:
            Lista de dicionários com informações das questões e opções
        """
        questoes = []
        lines = latex_content.split('\n')
        current_questao = None
        questao_order = 0
        opcao_order = 0

        for line in lines:
            trimmed = line.strip()

            if trimmed.startswith('Q:'):
                if current_questao:
                    questoes.append(current_questao)

                questao_order += 1
                current_questao = {
                    "order": questao_order,
                    "text": trimmed[2:].strip(),
                    "opcoes": []
                }
                opcao_order = 0

            elif trimmed.startswith('QM:'):
                if current_questao:
                    questoes.append(current_questao)

                questao_order += 1
                current_questao = {
                    "order": questao_order,
                    "text": trimmed[3:].strip(),
                    "opcoes": []
                }
                opcao_order = 0

            elif trimmed.startswith(('a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)', 'j)')):
                if current_questao:
                    has_asterisk = trimmed.endswith('*')
                    text = trimmed[2:].strip().replace('*$', '').strip()
                    opcao_order += 1

                    is_correct = has_asterisk
                    if any(op['is_correct'] for op in current_questao['opcoes']):
                        is_correct = False

                    current_questao['opcoes'].append({
                        "order": opcao_order,
                        "text": text,
                        "is_correct": is_correct
                    })

        if current_questao:
            questoes.append(current_questao)

        return questoes

    @staticmethod
    def questoes_to_latex(questoes: List[dict]) -> str:
        """
        Converte questões estruturadas para formato LaTeX

        Args:
            questoes: Lista de questões com opções no formato:
                {
                    "text": "Pergunta?",
                    "opcoes": [
                        {"order": 1, "text": "Opção A", "is_correct": False},
                        {"order": 2, "text": "Opção B", "is_correct": True}
                    ]
                }

        Returns:
            String no formato LaTeX
        """
        latex_parts = []

        for questao in questoes:
            latex_parts.append(f"Q: {questao['text']}")

            for opcao in questao['opcoes']:
                letter = chr(97 + opcao['order'] - 1)
                asterisk = " *" if opcao['is_correct'] else ""
                latex_parts.append(f"{letter}) {opcao['text']}{asterisk}")

        return "\n\n".join(latex_parts)
