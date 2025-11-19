"""
Router para endpoints de compilação LaTeX e geração de cartão resposta
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from app.models.latex import LaTeXCompileRequest, CompilationResult
from app.services.latex_compiler import LaTeXCompilerService
from app.services.cartao_resposta_service import CartaoRespostaService
from app.services.gabarito_service import GabaritoService
from app.core.config import settings

router = APIRouter(prefix="/latex", tags=["LaTeX Compilation"])


def get_compiler_service() -> LaTeXCompilerService:
    """
    Dependency para obter instância do serviço de compilação

    Returns:
        LaTeXCompilerService
    """
    return LaTeXCompilerService()


def get_cartao_service() -> CartaoRespostaService:
    """
    Dependency para obter instância do serviço de cartão resposta

    Returns:
        CartaoRespostaService
    """
    return CartaoRespostaService()


def get_gabarito_service() -> GabaritoService:
    """
    Dependency para obter instância do serviço de gabarito

    Returns:
        GabaritoService
    """
    return GabaritoService()


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
    cartao_service: CartaoRespostaService = Depends(get_cartao_service)
) -> CompilationResult:
    """
    Gera cartão resposta em PDF a partir de template HTML

    Args:
        cartao_service: Serviço de cartão resposta (injetado)

    Returns:
        CompilationResult com sucesso/erro e caminho do PDF
    """
    success, message, pdf_path = cartao_service.generate_pdf()

    if not success or not pdf_path:
        return CompilationResult(
            success=False,
            pdfUrl=None,
            error=message,
            logs=[message]
        )

    # Retorna o nome do arquivo para ser acessado via endpoint /pdfs/temp/
    pdf_filename = pdf_path.name

    return CompilationResult(
        success=True,
        pdfUrl=f"/api/latex/pdfs/temp/{pdf_filename}",
        error=None,
        logs=["Cartão resposta gerado com sucesso"]
    )


@router.post("/compile-answer-key", response_model=CompilationResult)
async def compile_answer_key(
    request: LaTeXCompileRequest,
    compiler: LaTeXCompilerService = Depends(get_compiler_service),
    gabarito_service: GabaritoService = Depends(get_gabarito_service)
) -> CompilationResult:
    """
    Gera gabarito em PDF a partir do código LaTeX da prova (HTML com respostas marcadas)

    Args:
        request: Requisição com código LaTeX da prova
        compiler: Serviço de compilação (injetado)
        gabarito_service: Serviço de gabarito (injetado)

    Returns:
        CompilationResult com sucesso/erro e caminho do PDF
    """
    # Extrair as respostas corretas do LaTeX
    questions = compiler._extract_questions_from_latex(request.latex, include_correct_answers=True)

    # Converter para o formato {número_questão: letra_correta}
    correct_answers = {}
    options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    for q in questions:
        if 'correct_answers' in q and q['correct_answers']:
            # Pegar a primeira resposta correta (no caso de múltipla escolha, pegar só a primeira)
            correct_idx = q['correct_answers'][0]
            if correct_idx < len(options):
                correct_answers[q['number']] = options[correct_idx]

    # Gerar o PDF do gabarito
    success, message, pdf_path = gabarito_service.generate_pdf(
        correct_answers=correct_answers,
        filename=request.filename
    )

    if not success or not pdf_path:
        return CompilationResult(
            success=False,
            pdfUrl=None,
            error=message,
            logs=[message]
        )

    # Retorna o nome do arquivo para ser acessado via endpoint /pdfs/temp/
    pdf_filename = pdf_path.name

    return CompilationResult(
        success=True,
        pdfUrl=f"/api/latex/pdfs/temp/{pdf_filename}",
        error=None,
        logs=["Gabarito gerado com sucesso", f"Questões com respostas: {len(correct_answers)}"]
    )


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
