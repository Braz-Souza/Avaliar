"""
Modelos Pydantic para compilação LaTeX
"""

from pydantic import BaseModel


class LaTeXCompileRequest(BaseModel):
    """
    Modelo para requisição de compilação LaTeX
    
    Attributes:
        latex: Código LaTeX a ser compilado
        filename: Nome do arquivo (sem extensão)
    """
    latex: str
    filename: str = "document"


class CompilationResult(BaseModel):
    """
    Modelo para resultado da compilação LaTeX
    
    Attributes:
        success: Indica se a compilação foi bem-sucedida
        pdfUrl: URL do PDF gerado (None em caso de erro)
        error: Mensagem de erro (None em caso de sucesso)
        logs: Lista de linhas de log da compilação
    """
    success: bool
    pdfUrl: str | None = None
    error: str | None = None
    logs: list[str] = []
