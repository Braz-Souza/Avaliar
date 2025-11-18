"""
Service para gerenciamento de randomização de provas para turmas
"""

import random
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.db.models.turma import Turma
from app.db.models.prova import Prova
from app.db.models.aluno import Aluno
from app.db.models.questao import Questao, QuestaoOpcao
from app.db.models.randomizacao import (
    TurmaProva, TurmaProvaCreate, TurmaProvaRead,
    AlunoRandomizacao, AlunoRandomizacaoCreate, AlunoRandomizacaoRead
)
from app.utils.logger import logger


class RandomizacaoManagerService:
    """
    Serviço responsável pelo gerenciamento de randomização de provas
    """

    def __init__(self, db: Session):
        """
        Inicializa o serviço com sessão do banco

        Args:
            db: Sessão do banco de dados
        """
        self.db = db

    async def link_prova_to_turma(
        self,
        turma_id: UUID,
        prova_id: UUID
    ) -> TurmaProvaRead:
        """
        Liga uma prova a uma turma e cria randomização para cada aluno

        Args:
            turma_id: ID da turma
            prova_id: ID da prova

        Returns:
            TurmaProvaRead com informações da ligação criada

        Raises:
            ValueError: Se turma ou prova não existirem
        """
        # Verificar se turma existe
        turma = self.db.execute(
            select(Turma).where(Turma.id == turma_id)
        ).scalar_one_or_none()

        if not turma:
            raise ValueError(f"Turma com ID {turma_id} não encontrada")

        # Verificar se prova existe e carregar questões
        prova = self.db.execute(
            select(Prova)
            .options(selectinload(Prova.questoes).selectinload(Questao.opcoes))
            .where(Prova.id == prova_id)
        ).scalar_one_or_none()

        if not prova:
            raise ValueError(f"Prova com ID {prova_id} não encontrada")

        if not prova.questoes:
            raise ValueError("Prova não possui questões para randomizar")

        # Verificar se já existe ligação
        existing_link = self.db.execute(
            select(TurmaProva)
            .where(TurmaProva.turma_id == turma_id, TurmaProva.prova_id == prova_id)
        ).scalar_one_or_none()

        if existing_link:
            raise ValueError("Prova já está vinculada a esta turma")

        # Criar ligação turma-prova
        turma_prova = TurmaProva(
            turma_id=turma_id,
            prova_id=prova_id
        )
        self.db.add(turma_prova)
        self.db.flush()  # Obter ID sem commit

        # Carregar alunos da turma
        turma_with_alunos = self.db.execute(
            select(Turma)
            .options(selectinload(Turma.alunos))
            .where(Turma.id == turma_id)
        ).scalar_one()

        if not turma_with_alunos.alunos:
            logger.warning(f"Turma {turma_id} não possui alunos")
        else:
            # Criar randomização para cada aluno
            await self._create_randomizacoes_for_alunos(
                turma_prova.id,
                turma_with_alunos.alunos,
                prova.questoes
            )

        self.db.commit()
        self.db.refresh(turma_prova)

        logger.info(f"Prova {prova_id} vinculada à turma {turma_id} com randomização para {len(turma_with_alunos.alunos)} alunos")

        return TurmaProvaRead(
            id=turma_prova.id,
            turma_id=turma_prova.turma_id,
            prova_id=turma_prova.prova_id,
            created_at=turma_prova.created_at
        )

    async def _create_randomizacoes_for_alunos(
        self,
        turma_prova_id: UUID,
        alunos: List[Aluno],
        questoes: List[Questao]
    ) -> None:
        """
        Cria randomização para uma lista de alunos

        Args:
            turma_prova_id: ID da ligação turma-prova
            alunos: Lista de alunos
            questoes: Lista de questões da prova
        """
        # Preparar dados das questões para randomização
        questoes_data = []
        for questao in questoes:
            questoes_data.append({
                'id': questao.id,
                'opcoes_count': len(questao.opcoes)
            })

        for aluno in alunos:
            # Randomizar ordem das questões
            questoes_order = list(range(len(questoes_data)))
            random.shuffle(questoes_order)

            # Para cada questão, randomizar ordem das alternativas
            alternativas_order = {}
            for i, questao_data in enumerate(questoes_data):
                if questao_data['opcoes_count'] > 0:
                    alternativas_order_original = list(range(questao_data['opcoes_count']))
                    alternativas_randomizadas = alternativas_order_original.copy()
                    random.shuffle(alternativas_randomizadas)
                    alternativas_order[str(questao_data['id'])] = alternativas_randomizadas
                else:
                    alternativas_order[str(questao_data['id'])] = []

            # Criar randomização do aluno
            aluno_randomizacao = AlunoRandomizacao(
                turma_prova_id=turma_prova_id,
                aluno_id=aluno.id,
                questoes_order=questoes_order,
                alternativas_order=alternativas_order
            )
            self.db.add(aluno_randomizacao)

    async def get_turmas_provas(
        self,
        turma_id: Optional[UUID] = None,
        prova_id: Optional[UUID] = None
    ) -> List[TurmaProvaRead]:
        """
        Lista ligações turma-prova com filtros opcionais

        Args:
            turma_id: ID da turma para filtrar (opcional)
            prova_id: ID da prova para filtrar (opcional)

        Returns:
            Lista de TurmaProvaRead
        """
        query = select(TurmaProva).options(
            selectinload(TurmaProva.turma),
            selectinload(TurmaProva.prova)
        )

        if turma_id:
            query = query.where(TurmaProva.turma_id == turma_id)
        if prova_id:
            query = query.where(TurmaProva.prova_id == prova_id)

        result = self.db.execute(query)
        turma_provas = result.scalars().all()

        return [
            TurmaProvaRead(
                id=tp.id,
                turma_id=tp.turma_id,
                prova_id=tp.prova_id,
                created_at=tp.created_at
            )
            for tp in turma_provas
        ]

    async def get_aluno_randomizacoes(
        self,
        turma_prova_id: UUID
    ) -> List[AlunoRandomizacaoRead]:
        """
        Obtém randomizações de todos os alunos de uma turma-prova

        Args:
            turma_prova_id: ID da ligação turma-prova

        Returns:
            Lista de AlunoRandomizacaoRead com dados dos alunos
        """
        randomizacoes = self.db.execute(
            select(AlunoRandomizacao)
            .options(
                selectinload(AlunoRandomizacao.aluno),
                selectinload(AlunoRandomizacao.turma_prova).selectinload(TurmaProva.prova).selectinload(Prova.questoes).selectinload(Questao.opcoes)
            )
            .where(AlunoRandomizacao.turma_prova_id == turma_prova_id)
        ).scalars().all()

        result = []
        for rand in randomizacoes:
            result.append(AlunoRandomizacaoRead(
                id=rand.id,
                turma_prova_id=rand.turma_prova_id,
                aluno_id=rand.aluno_id,
                questoes_order=rand.questoes_order,
                alternativas_order=rand.alternativas_order,
                created_at=rand.created_at
            ))

        return result

    async def get_aluno_randomizacao(
        self,
        aluno_id: UUID,
        prova_id: UUID
    ) -> Optional[AlunoRandomizacaoRead]:
        """
        Obtém randomização específica de um aluno para uma prova

        Args:
            aluno_id: ID do aluno
            prova_id: ID da prova

        Returns:
            AlunoRandomizacaoRead ou None se não encontrado
        """
        randomizacao = self.db.execute(
            select(AlunoRandomizacao)
            .options(
                selectinload(AlunoRandomizacao.aluno),
                selectinload(AlunoRandomizacao.turma_prova).selectinload(TurmaProva.prova).selectinload(Prova.questoes).selectinload(Questao.opcoes)
            )
            .join(TurmaProva)
            .where(
                AlunoRandomizacao.aluno_id == aluno_id,
                TurmaProva.prova_id == prova_id
            )
        ).scalar_one_or_none()

        if not randomizacao:
            return None

        return AlunoRandomizacaoRead(
            id=randomizacao.id,
            turma_prova_id=randomizacao.turma_prova_id,
            aluno_id=randomizacao.aluno_id,
            questoes_order=randomizacao.questoes_order,
            alternativas_order=randomizacao.alternativas_order,
            created_at=randomizacao.created_at
        )

    async def unlink_prova_from_turma(
        self,
        turma_id: UUID,
        prova_id: UUID
    ) -> bool:
        """
        Remove vinculo entre prova e turma (exclui todas as randomizações)

        Args:
            turma_id: ID da turma
            prova_id: ID da prova

        Returns:
            True se removido com sucesso, False se não encontrou
        """
        turma_prova = self.db.execute(
            select(TurmaProva)
            .where(TurmaProva.turma_id == turma_id, TurmaProva.prova_id == prova_id)
        ).scalar_one_or_none()

        if not turma_prova:
            return False

        # Excluir randomizações em cascata
        self.db.delete(turma_prova)
        self.db.commit()

        logger.info(f"Vínculo removido entre turma {turma_id} e prova {prova_id}")
        return True

    async def get_aluno_prova_content(
        self,
        aluno_id: UUID,
        prova_id: UUID
    ) -> str:
        """
        Retorna o conteúdo LaTeX da prova personalizada de um aluno

        Args:
            aluno_id: ID do aluno
            prova_id: ID da prova

        Returns:
            String com o conteúdo LaTeX da prova personalizada

        Raises:
            ValueError: Se randomização não existe para este aluno e prova
        """
        randomizacao = self.db.execute(
            select(AlunoRandomizacao)
            .options(
                selectinload(AlunoRandomizacao.aluno),
                selectinload(AlunoRandomizacao.turma_prova)
                .selectinload(TurmaProva.prova)
                .selectinload(Prova.questoes)
                .selectinload(Questao.opcoes)
            )
            .join(TurmaProva)
            .where(
                AlunoRandomizacao.aluno_id == aluno_id,
                TurmaProva.prova_id == prova_id
            )
        ).scalar_one_or_none()

        if not randomizacao:
            raise ValueError(f"Randomização não encontrada para aluno {aluno_id} e prova {prova_id}")

        prova = randomizacao.turma_prova.prova
        aluno = randomizacao.aluno
        questoes_originais = sorted(prova.questoes, key=lambda q: q.order)

        # Construir documento LaTeX
        latex_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage[margin=2cm]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{enumitem}

\title{""" + prova.name + r"""}
\date{}

\begin{document}

\maketitle

"""
        for idx_personalizado, idx_original in enumerate(randomizacao.questoes_order):
            questao = questoes_originais[idx_original]
            questao_id_str = str(questao.id)

            questao_text = questao.text.replace('*', '').strip()
            latex_content += f"\\textbf{{{idx_personalizado + 1}.}} {questao_text}\n\n"
            latex_content += "\\begin{enumerate}[label=\\alph*)]\n"

            opcoes_originais = sorted(questao.opcoes, key=lambda o: o.order)
            alternativas_order_questao = randomizacao.alternativas_order.get(questao_id_str, [])

            for idx_alt_orig in alternativas_order_questao:
                if idx_alt_orig < len(opcoes_originais):
                    opcao_text = opcoes_originais[idx_alt_orig].text.replace('*', '').strip()
                    latex_content += f"\\item {opcao_text}\n"

            latex_content += "\\end{enumerate}\n\n"
            latex_content += "\\vspace{0.5cm}\n\n"

        latex_content += r"\end{document}"

        return latex_content
