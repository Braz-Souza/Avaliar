"""
Service para gerenciamento de randomização de provas para turmas
"""

import random
import io
import zipfile
from typing import List, Optional, Tuple
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

    async def get_turma_prova(self, turma_prova_id: UUID) -> Optional[TurmaProvaRead]:
        """
        Obtém uma ligação turma-prova específica

        Args:
            turma_prova_id: ID da ligação turma-prova

        Returns:
            TurmaProvaRead ou None se não encontrado
        """
        turma_prova = self.db.execute(
            select(TurmaProva).where(TurmaProva.id == turma_prova_id)
        ).scalar_one_or_none()

        if not turma_prova:
            return None

        return TurmaProvaRead(
            id=turma_prova.id,
            turma_id=turma_prova.turma_id,
            prova_id=turma_prova.prova_id,
            created_at=turma_prova.created_at
        )

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
            .join(AlunoRandomizacao.aluno)
            .options(
                selectinload(AlunoRandomizacao.aluno),
                selectinload(AlunoRandomizacao.turma_prova)
                    .selectinload(TurmaProva.prova)
                    .selectinload(Prova.questoes)
                    .selectinload(Questao.opcoes)
            )
            .where(AlunoRandomizacao.turma_prova_id == turma_prova_id)
            .order_by(Aluno.nome)
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
        turma_prova_id: UUID
    ) -> str:
        """
        Retorna o conteúdo LaTeX da prova personalizada de um aluno

        Args:
            aluno_id: ID do aluno
            turma_prova_id: ID da prova

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
            .join(AlunoRandomizacao.turma_prova)
            .where(
                AlunoRandomizacao.aluno_id == aluno_id,
                AlunoRandomizacao.turma_prova_id == turma_prova_id
            )
        ).scalar_one_or_none()

        if not randomizacao:
            raise ValueError(f"Randomização não encontrada para aluno {aluno_id} e turma_prova {turma_prova_id}")

        prova = randomizacao.turma_prova.prova
        aluno = randomizacao.aluno
        questoes_originais = sorted(prova.questoes, key=lambda q: q.order)

        latex_content = r"""\documentclass[a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=2cm]{geometry}
\usepackage{enumitem}
\usepackage{array}

\begin{document}

\noindent
\begin{tabular}{|p{0.15\textwidth}|p{0.78\textwidth}|}
\hline
\textbf{PROVA} & \textbf{"""+ prova.name + r"""} \\
\hline
\textbf{ALUNO} & \textbf{"""+ aluno.nome + r"""} \\
\hline
\textbf{MATRICULA} & \textbf{"""+ aluno.matricula + r"""} \\
\hline

\textbf{DATA} & \textbf{} \\
\hline
\end{tabular}

\vspace{0.2cm}

\noindent
\begin{tabular}{|p{0.08\textwidth}|p{0.27\textwidth}|p{0.16\textwidth}|p{0.16\textwidth}|p{0.06\textwidth}|p{0.10\textwidth}|}
\hline
\end{tabular}

\vspace{0.5cm}

"""
        for idx_personalizado, idx_original in enumerate(randomizacao.questoes_order):
            questao = questoes_originais[idx_original]
            questao_id_str = str(questao.id)

            questao_text = questao.text.replace('*', '').strip()
            latex_content += f"\\noindent\\textbf{{{idx_personalizado + 1}.}} {questao_text}\n\n"
            latex_content += "\\begin{enumerate}[label=\\alph*), leftmargin=1cm, itemsep=0pt, topsep=2pt]\n"

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

    async def get_all_alunos_prova_pdfs(
        self,
        turma_prova_id: UUID,
        latex_compiler
    ) -> Tuple[List[dict], str]:
        """
        Retorna lista de dados dos alunos e seus PDFs para um turma_prova_id

        Args:
            turma_prova_id: ID da ligação turma-prova
            latex_compiler: Instância do LaTeXCompilerService

        Returns:
            Tuple com lista de dicionários contendo (aluno_nome, aluno_matricula, pdf_bytes)
            e o nome da prova

        Raises:
            ValueError: Se turma_prova_id não existir
        """
        turma_prova = self.db.execute(
            select(TurmaProva)
            .options(
                selectinload(TurmaProva.prova).selectinload(Prova.questoes).selectinload(Questao.opcoes),
                selectinload(TurmaProva.turma),
                selectinload(TurmaProva.randomizacoes).selectinload(AlunoRandomizacao.aluno)
            )
            .where(TurmaProva.id == turma_prova_id)
        ).scalar_one_or_none()

        if not turma_prova:
            raise ValueError(f"TurmaProva com ID {turma_prova_id} não encontrada")

        if not turma_prova.randomizacoes:
            raise ValueError("Nenhuma randomização encontrada para esta turma-prova")

        prova_nome = turma_prova.prova.name
        alunos_pdfs = []

        for randomizacao in turma_prova.randomizacoes:
            aluno = randomizacao.aluno

            try:
                latex_content = await self.get_aluno_prova_content(
                    aluno_id=aluno.id,
                    prova_id=turma_prova.prova_id
                )

                success, pdf_bytes, error = await latex_compiler.compile_to_bytes(
                    latex_content=latex_content,
                    filename=f"prova_{aluno.matricula}"
                )

                if success:
                    alunos_pdfs.append({
                        'aluno_nome': aluno.nome,
                        'aluno_matricula': aluno.matricula,
                        'pdf_bytes': pdf_bytes
                    })
                else:
                    logger.error(f"Erro ao compilar PDF para aluno {aluno.nome} ({aluno.matricula}): {error}")
            except Exception as e:
                logger.error(f"Erro ao gerar PDF para aluno {aluno.nome} ({aluno.matricula}): {str(e)}")
                continue

        return alunos_pdfs, prova_nome

    async def create_zip_with_all_pdfs(
        self,
        turma_prova_id: UUID,
        latex_compiler
    ) -> Tuple[bytes, str]:
        """
        Cria um arquivo ZIP contendo todos os PDFs das provas dos alunos

        Args:
            turma_prova_id: ID da ligação turma-prova
            latex_compiler: Instância do LaTeXCompilerService

        Returns:
            Tuple com bytes do arquivo ZIP e nome sugerido para o arquivo

        Raises:
            ValueError: Se turma_prova_id não existir ou não houver PDFs gerados
        """
        alunos_pdfs, prova_nome = await self.get_all_alunos_prova_pdfs(
            turma_prova_id=turma_prova_id,
            latex_compiler=latex_compiler
        )

        if not alunos_pdfs:
            raise ValueError("Nenhum PDF foi gerado com sucesso")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for aluno_data in alunos_pdfs:
                filename = f"{aluno_data['aluno_matricula']}_{aluno_data['aluno_nome'].replace(' ', '_')}.pdf"
                zip_file.writestr(filename, aluno_data['pdf_bytes'])

        zip_bytes = zip_buffer.getvalue()

        zip_filename = f"provas_{prova_nome.replace(' ', '_')}.zip"

        logger.info(f"ZIP criado com {len(alunos_pdfs)} PDFs para turma_prova {turma_prova_id}")

        return zip_bytes, zip_filename

    async def get_correct_answers_for_aluno(
        self,
        aluno_id: UUID,
        prova_id: UUID
    ) -> dict[int, str]:
        """
        Obtém as respostas corretas personalizadas para um aluno específico
        baseado na randomização de questões e alternativas.

        Args:
            aluno_id: ID do aluno
            prova_id: ID da prova

        Returns:
            Dicionário mapeando número da questão (1-indexed) para letra da resposta correta (A, B, C, etc.)
            Exemplo: {1: 'A', 2: 'C', 3: 'B', ...}

        Raises:
            ValueError: Se randomização não existir para este aluno e prova
        """
        # Buscar a randomização completa com todos os relacionamentos necessários
        randomizacao_completa = self.db.execute(
            select(AlunoRandomizacao)
            .options(
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

        if not randomizacao_completa:
            raise ValueError(f"Randomização não encontrada para aluno {aluno_id} e prova {prova_id}")

        prova = randomizacao_completa.turma_prova.prova
        questoes_originais = sorted(prova.questoes, key=lambda q: q.order)

        # Criar dicionário de respostas corretas conforme a ordem personalizada
        correct_answers = {}

        for idx_personalizado, idx_original in enumerate(randomizacao_completa.questoes_order):
            questao = questoes_originais[idx_original]
            questao_id_str = str(questao.id)

            # Obter opções ordenadas originalmente
            opcoes_originais = sorted(questao.opcoes, key=lambda o: o.order)

            # Encontrar qual opção é correta na ordem original
            opcao_correta_idx_original = None
            for idx, opcao in enumerate(opcoes_originais):
                if opcao.is_correct:
                    opcao_correta_idx_original = idx
                    break

            if opcao_correta_idx_original is None:
                logger.warning(f"Questão {questao.id} não possui opção correta marcada")
                continue

            # Obter a ordem das alternativas randomizadas para esta questão
            alternativas_order_questao = randomizacao_completa.alternativas_order.get(questao_id_str, [])

            # Encontrar a posição da opção correta na ordem randomizada
            if opcao_correta_idx_original in alternativas_order_questao:
                posicao_randomizada = alternativas_order_questao.index(opcao_correta_idx_original)
                # Converter índice para letra (0=A, 1=B, 2=C, etc.)
                letra_correta = chr(65 + posicao_randomizada)  # 65 é o código ASCII de 'A'
                correct_answers[idx_personalizado + 1] = letra_correta

        logger.info(f"Respostas corretas obtidas para aluno {aluno_id} e prova {prova_id}: {len(correct_answers)} questões")

        return correct_answers
