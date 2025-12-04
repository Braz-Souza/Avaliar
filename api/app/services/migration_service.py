"""
Service para migração de dados existentes para o novo formato estruturado
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from app.db.models.prova import Prova
from app.db.models.questao import Questao, QuestaoOpcao
from app.utils.logger import logger


class MigrationService:
    """
    Serviço responsável por migrar dados existentes para o novo formato estruturado
    """

    def __init__(self, db: Session):
        """Inicializa o serviço de migração com sessão do banco de dados"""
        self.db = db

    def migrate_all_provas_to_questoes(self) -> dict:
        """
        Migra todas as provas existentes para o novo formato estruturado

        Returns:
            Dicionário com estatísticas da migração
        """
        provas = self.db.exec(select(Prova).where(Prova.deleted == False)).all()

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for prova in provas:
            try:
                # Verificar se já tem questões estruturadas
                existing_questoes = self.db.exec(
                    select(Questao).where(Questao.prova_id == prova.id)
                ).all()

                if existing_questoes:
                    logger.info(f"Skipping prova {prova.id} - already has questoes")
                    skipped_count += 1
                    continue

                # Converter conteúdo LaTeX para questões estruturadas
                questoes_data = self._parse_latex_to_questoes(prova.content)

                if not questoes_data:
                    logger.warning(f"Skipping prova {prova.id} - no questoes found in content")
                    skipped_count += 1
                    continue

                # Salvar questões estruturadas
                for questao_info in questoes_data:
                    questao = Questao(
                        prova_id=prova.id,
                        order=questao_info['order'],
                        text=questao_info['text']
                    )
                    self.db.add(questao)
                    self.db.flush()  # Obter o ID da questão

                    # Salvar opções
                    for opcao_info in questao_info['opcoes']:
                        opcao = QuestaoOpcao(
                            questao_id=questao.id,
                            order=opcao_info['order'],
                            text=opcao_info['text'],
                            is_correct=opcao_info['is_correct']
                        )
                        self.db.add(opcao)

                self.db.commit()
                migrated_count += 1
                logger.info(f"Migrated prova {prova.id}: {len(questoes_data)} questoes")

            except Exception as e:
                logger.error(f"Error migrating prova {prova.id}: {str(e)}")
                error_count += 1
                self.db.rollback()

        return {
            "total_provas": len(provas),
            "migrated_count": migrated_count,
            "skipped_count": skipped_count,
            "error_count": error_count
        }

    def _parse_latex_to_questoes(self, latex_content: str) -> List[dict]:
        """
        Converte conteúdo LaTeX para formato estruturado de questões

        Args:
            latex_content: Conteúdo LaTeX da prova

        Returns:
            Lista de dicionários com informações das questões
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
                # Converter QM: para Q: (simples)
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

                    # Para questões múltiplas, manter apenas primeira opção correta
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

    def get_migration_status(self) -> dict:
        """
        Verifica o status da migração

        Returns:
            Dicionário com estatísticas do status atual
        """
        total_provas = len(self.db.exec(select(Prova).where(Prova.deleted == False)).all())
        provas_com_questoes = 0

        for prova in self.db.exec(select(Prova).where(Prova.deleted == False)).all():
            questoes_count = len(self.db.exec(
                select(Questao).where(Questao.prova_id == prova.id)
            ).all())

            if questoes_count > 0:
                provas_com_questoes += 1

        return {
            "total_provas": total_provas,
            "provas_com_questoes": provas_com_questoes,
            "provas_sem_questoes": total_provas - provas_com_questoes,
            "migration_needed": total_provas - provas_com_questoes > 0
        }
