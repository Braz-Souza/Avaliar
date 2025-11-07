"""
Service para compilação de documentos LaTeX
"""

import subprocess
import tempfile
import uuid
from pathlib import Path
from datetime import datetime
import shutil

from app.core.config import settings
from app.models.latex import CompilationResult
from app.utils.logger import logger


class LaTeXCompilerService:
    """
    Serviço responsável pela compilação de documentos LaTeX em PDF
    """

    def __init__(self):
        """Inicializa o serviço de compilação"""
        self.temp_dir = settings.TEMP_PDF_DIR
        self.pdf_metadata: dict[str, dict] = {}

    async def compile(
        self,
        latex_content: str,
        filename: str = "document"
    ) -> CompilationResult:
        """
        Compila código LaTeX para PDF usando pdflatex

        Args:
            latex_content: Código LaTeX a ser compilado
            filename: Nome base do arquivo (sem extensão)

        Returns:
            CompilationResult com sucesso/erro e logs
        """
        compile_id = self._generate_compile_id()

        # Log do conteúdo LaTeX para debug
        logger.debug(f"Compiling LaTeX for {filename}, content length: {len(latex_content)}")
        logger.debug(f"LaTeX content preview: {latex_content[:200]}...")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / f"{filename}.tex"

            try:
                tex_file.write_text(latex_content, encoding='utf-8')
                logger.debug(f"LaTeX file written to: {tex_file}")
            except Exception as e:
                logger.error(f"Failed to write LaTeX file: {e}")
                return CompilationResult(
                    success=False,
                    error=f"Failed to write LaTeX file: {str(e)}",
                    logs=[]
                )

            try:
                result = await self._run_pdflatex(tex_file, temp_path)

                pdf_file = temp_path / f"{filename}.pdf"

                if pdf_file.exists():
                    return self._handle_success(pdf_file, compile_id, filename, result)
                else:
                    return self._handle_failure(temp_path, filename, result)

            except subprocess.TimeoutExpired:
                logger.warning(f"LaTeX compilation timeout for {filename}")
                return CompilationResult(
                    success=False,
                    error=f"Compilation timeout ({settings.LATEX_TIMEOUT_SECONDS}s exceeded)",
                    logs=[]
                )
            except FileNotFoundError:
                logger.error("pdflatex not found in system")
                return CompilationResult(
                    success=False,
                    error="pdflatex not found. Please install LaTeX distribution (TeX Live, MiKTeX, etc.)",
                    logs=[]
                )
            except Exception as e:
                logger.error(f"Compilation error: {str(e)}")
                return CompilationResult(
                    success=False,
                    error=f"Compilation error: {str(e)}",
                    logs=[]
                )

    async def _run_pdflatex(self, tex_file: Path, output_dir: Path):
        """
        Executa pdflatex no arquivo .tex

        Args:
            tex_file: Caminho do arquivo .tex
            output_dir: Diretório de saída

        Returns:
            CompletedProcess com resultado da execução
        """
        result = None
        for run_number in range(settings.LATEX_COMPILE_RUNS):
            result = subprocess.run(
                [
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory', str(output_dir),
                    str(tex_file)
                ],
                capture_output=True,
                text=True,
                timeout=settings.LATEX_TIMEOUT_SECONDS
            )
            logger.debug(f"pdflatex run {run_number + 1}/{settings.LATEX_COMPILE_RUNS}")

        return result

    def _generate_compile_id(self) -> str:
        """
        Gera ID único para compilação temporária

        Returns:
            ID único no formato temp_XXXXXXXXXXXX
        """
        return f"{settings.TEMP_PDF_PREFIX}{uuid.uuid4().hex[:12]}"

    def _handle_success(
        self,
        pdf_file: Path,
        compile_id: str,
        filename: str,
        result
    ) -> CompilationResult:
        """
        Processa compilação bem-sucedida

        Args:
            pdf_file: Caminho do PDF gerado
            compile_id: ID da compilação
            filename: Nome do arquivo
            result: Resultado do subprocess

        Returns:
            CompilationResult de sucesso
        """
        output_pdf = self.temp_dir / f"{compile_id}.pdf"
        shutil.copy2(pdf_file, output_pdf)

        self.pdf_metadata[compile_id] = {
            "created_at": datetime.now(),
            "filename": filename
        }

        logger.info(f"LaTeX compiled successfully: {compile_id} ({filename})")

        return CompilationResult(
            success=True,
            pdfUrl=f"/latex/pdfs/temp/{compile_id}.pdf",
            logs=result.stdout.split('\n') if result.stdout else []
        )

    def _handle_failure(
        self,
        temp_path: Path,
        filename: str,
        result
    ) -> CompilationResult:
        """
        Processa falha na compilação

        Args:
            temp_path: Diretório temporário da compilação
            filename: Nome do arquivo
            result: Resultado do subprocess

        Returns:
            CompilationResult de erro
        """
        error_logs = self._collect_error_logs(temp_path, filename, result)

        # Salvar conteúdo LaTeX problemático para debug
        try:
            failed_tex = temp_path / f"{filename}.tex"
            if failed_tex.exists():
                debug_file = settings.LATEX_SOURCES_DIR / f"failed_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
                shutil.copy2(failed_tex, debug_file)
                logger.debug(f"Failed LaTeX content saved to: {debug_file}")
        except Exception as e:
            logger.error(f"Failed to save debug LaTeX file: {e}")

        logger.warning(f"LaTeX compilation failed for {filename} (exit code: {result.returncode})")

        return CompilationResult(
            success=False,
            error=f"PDF compilation failed. Exit code: {result.returncode}",
            logs=error_logs
        )

    def _collect_error_logs(
        self,
        temp_path: Path,
        filename: str,
        result
    ) -> list[str]:
        """
        Coleta logs de erro da compilação

        Args:
            temp_path: Diretório temporário da compilação
            filename: Nome do arquivo
            result: Resultado do subprocess

        Returns:
            Lista de linhas de log
        """
        all_logs = []

        # Adicionar informações de debug
        all_logs.extend([
            f"=== COMPILATION DEBUG INFO ===",
            f"Exit code: {result.returncode}",
            f"Working directory: {temp_path}",
            f"Filename: {filename}",
            ""
        ])

        # Tentar ler arquivo de log do LaTeX
        log_file = temp_path / f"{filename}.log"
        if log_file.exists():
            all_logs.extend(["=== LOG FILE ==="])
            all_logs.extend(
                log_file.read_text(encoding='utf-8', errors='ignore').split('\n')
            )

        # Adicionar stdout
        if result.stdout:
            all_logs.extend(["=== STDOUT ==="])
            all_logs.extend(result.stdout.split('\n'))

        # Adicionar stderr
        if result.stderr:
            all_logs.extend(["=== STDERR ==="])
            all_logs.extend(result.stderr.split('\n'))

        return all_logs if all_logs else ["No compilation output available"]

    def get_metadata(self, compile_id: str) -> dict | None:
        """
        Obtém metadados de um PDF compilado

        Args:
            compile_id: ID da compilação

        Returns:
            Dicionário com metadados ou None
        """
        return self.pdf_metadata.get(compile_id)

    def generate_answer_sheet_latex(self, latex_content: str) -> str:
        """
        Gera código LaTeX para cartão resposta baseado no conteúdo da prova

        Args:
            latex_content: Código LaTeX da prova original

        Returns:
            Código LaTeX do cartão resposta
        """
        import re

        # Extrair questões do conteúdo LaTeX
        questions = []

        # Padrão para questões de múltipla escolha AMC (simples e múltipla)
        question_pattern = r'\\begin\{(?:question|questionmult)\}\{([^}]*)\}.*?\\end\{(?:question|questionmult)\}'
        question_matches = re.finditer(question_pattern, latex_content, re.DOTALL)

        for idx, match in enumerate(question_matches, start=1):
            question_name = match.group(1) or f"Q{idx}"

            # Contar número de alternativas
            choices_pattern = r'\\(?:correct|wrong)?choice'
            choices = len(re.findall(choices_pattern, match.group(0)))

            if choices > 0:
                questions.append({
                    'number': idx,
                    'name': question_name,
                    'choices': choices
                })

        # Se não encontrou questões com padrão AMC, tentar padrão genérico
        if not questions:
            # Tentar encontrar enumerações com itens
            enum_pattern = r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}'
            enum_matches = re.finditer(enum_pattern, latex_content, re.DOTALL)

            for enum_match in enum_matches:
                items = re.findall(r'\\item', enum_match.group(1))
                if items:
                    # Assumir 5 alternativas por questão (padrão)
                    for i in range(len(items)):
                        questions.append({
                            'number': len(questions) + 1,
                            'name': f'Q{len(questions) + 1}',
                            'choices': 5
                        })

        # Se ainda não encontrou, criar template básico com 10 questões
        if not questions:
            questions = [
                {'number': i, 'name': f'Q{i}', 'choices': 5}
                for i in range(1, 11)
            ]

        # Gerar LaTeX do cartão resposta
        answer_sheet_latex = r'''\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage[margin=2cm]{geometry}
\usepackage{array}
\usepackage{multirow}
\usepackage{hhline}

\title{Cartão Resposta}
\author{}
\date{}

\begin{document}

\begin{center}
{\LARGE \textbf{CARTÃO RESPOSTA}}
\end{center}

\vspace{0.5cm}

\noindent
\begin{tabular}{|p{6cm}|p{9cm}|}
\hline
\textbf{Nome:} & \\
\hline
\textbf{Matricula:} & \\
\hline
\textbf{Data:} & \\
\hline
\end{tabular}

\vspace{1cm}

\noindent
\textbf{Instruções:}
\begin{itemize}
\item Preencha completamente o círculo correspondente à alternativa escolhida
\item Use caneta preta ou azul
\item Não rasure o cartão
\item Marque apenas uma alternativa por questão
\end{itemize}

\vspace{0.5cm}

'''

        # Calcular o número máximo de alternativas
        max_choices = max([q['choices'] for q in questions]) if questions else 5
        # Garantir pelo menos 3 alternativas e no máximo 10
        max_choices = max(3, min(max_choices, 10))

        # Gerar letras das alternativas
        choices_letters = [chr(65 + i) for i in range(max_choices)]  # A, B, C, D, E, F, G...

        # Determinar quantas colunas de questões cabem
        # Se tiver até 5 alternativas, colocar 3 colunas de questões
        # Se tiver 6-8 alternativas, colocar 2 colunas
        # Se tiver mais de 8, colocar 1 coluna
        if max_choices <= 5:
            question_columns = 3
        elif max_choices <= 8:
            question_columns = 2
        else:
            question_columns = 1

        # Calcular quantas questões por coluna
        questions_per_column = (len(questions) + question_columns - 1) // question_columns

        # Reorganizar questões em colunas
        question_matrix = []
        for row_idx in range(questions_per_column):
            row = []
            for col_idx in range(question_columns):
                q_idx = col_idx * questions_per_column + row_idx
                if q_idx < len(questions):
                    row.append(questions[q_idx])
                else:
                    row.append(None)  # Célula vazia
            question_matrix.append(row)

        # Adicionar grade de respostas
        answer_sheet_latex += r'\begin{center}' + '\n'

        # Definir formato das colunas: Q + alternativas para cada coluna de questões
        col_format = '|'
        for _ in range(question_columns):
            col_format += 'c|' + 'c|' * max_choices

        answer_sheet_latex += r'\begin{tabular}{' + col_format + '}\n'
        answer_sheet_latex += r'\hline' + '\n'

        # Cabeçalho da tabela (apenas uma vez no topo)
        header_row = ''
        for col_idx in range(question_columns):
            if col_idx > 0:
                header_row += ' & '
            header_row += r'\textbf{Q}'
            for letter in choices_letters:
                header_row += f' & \\textbf{{{letter}}}'
        header_row += r' \\' + '\n'
        answer_sheet_latex += header_row
        answer_sheet_latex += r'\hline' + '\n'

        # Linhas com as questões
        for row in question_matrix:
            data_row = ''
            for col_idx, q in enumerate(row):
                if col_idx > 0:
                    data_row += ' & '

                if q is not None:
                    # Número da questão
                    data_row += str(q['number'])

                    # Círculos para as alternativas
                    for i in range(max_choices):
                        if i < q['choices']:
                            data_row += r' & $\bigcirc$'
                        else:
                            data_row += r' & '
                else:
                    # Célula vazia
                    data_row += ' & ' + ' & '.join([''] * max_choices)

            data_row += r' \\' + '\n'
            answer_sheet_latex += data_row
            answer_sheet_latex += r'\hline' + '\n'

        answer_sheet_latex += r'\end{tabular}' + '\n'
        answer_sheet_latex += r'\end{center}' + '\n'

        answer_sheet_latex += r'''
\vspace{1cm}

\noindent
\textbf{Observações:}
\begin{itemize}
\item Confira se o número de questões corresponde ao da prova
\item Em caso de dúvida, consulte o professor
\end{itemize}

\end{document}
'''

        return answer_sheet_latex

    async def compile_answer_sheet(
        self,
        latex_content: str,
        filename: str = "cartao_resposta"
    ) -> CompilationResult:
        """
        Compila cartão resposta a partir do conteúdo LaTeX da prova

        Args:
            latex_content: Código LaTeX da prova original
            filename: Nome base do arquivo (sem extensão)

        Returns:
            CompilationResult com sucesso/erro e logs
        """
        answer_sheet_latex = self.generate_answer_sheet_latex(latex_content)
        return await self.compile(answer_sheet_latex, filename)
