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
