"""
Router para endpoints de compilação LaTeX
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from app.models.latex import LaTeXCompileRequest, CompilationResult
from app.services.latex_compiler import LaTeXCompilerService
from app.core.config import settings

router = APIRouter(prefix="/latex", tags=["LaTeX Compilation"])


def get_compiler_service() -> LaTeXCompilerService:
    """
    Dependency para obter instância do serviço de compilação

    Returns:
        LaTeXCompilerService
    """
    return LaTeXCompilerService()


@router.post("/compile", response_model=CompilationResult)
async def compile_latex(
    request: LaTeXCompileRequest,
    compiler: LaTeXCompilerService = Depends(get_compiler_service)
) -> CompilationResult:
    """
    Compila código LaTeX para PDF usando pdflatex

    Args:
        request: Requisição com código LaTeX e nome do arquivo
        compiler: Serviço de compilação (injetado)

    Returns:
        CompilationResult com sucesso/erro e logs
    """
    return await compiler.compile(request.latex, request.filename)


@router.post("/compile-answer-sheet", response_model=CompilationResult)
async def compile_answer_sheet(
    request: LaTeXCompileRequest,
    compiler: LaTeXCompilerService = Depends(get_compiler_service)
) -> CompilationResult:
    """
    Compila cartão resposta baseado no código LaTeX da prova

    Args:
        request: Requisição com código LaTeX da prova
        compiler: Serviço de compilação (injetado)

    Returns:
        CompilationResult com sucesso/erro e logs
    """
    return await compiler.compile_answer_sheet(request.latex, "cartao_resposta")


@router.get("/pdfs/temp/{filename}")
async def get_temp_pdf(filename: str) -> FileResponse:
    """
    Serve arquivos PDF temporários (compilações não salvas)

    Args:
        filename: Nome do arquivo PDF temporário

    Returns:
        FileResponse com o PDF

    Raises:
        HTTPException: Se o PDF não for encontrado ou expirou
    """
    pdf_path = settings.TEMP_PDF_DIR / filename

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Temporary PDF not found or expired"
        )

    return FileResponse(
        path=str(pdf_path),
        media_type='application/pdf',
        filename=filename,
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Frame-Options": "ALLOWALL"
        }
    )


@router.get("/pdfs/{filename}")
async def get_saved_pdf(filename: str) -> FileResponse:
    """
    Serve arquivos PDF de provas salvas

    Args:
        filename: Nome do arquivo PDF

    Returns:
        FileResponse com o PDF

    Raises:
        HTTPException: Se o PDF não for encontrado
    """
    pdf_path = settings.PDF_OUTPUT_DIR / filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=str(pdf_path),
        media_type='application/pdf',
        filename=filename,
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "public, max-age=3600",
            "X-Frame-Options": "ALLOWALL"
        }
    )
