# =============================================================================
# IMPORTS E CONFIGURAÇÕES INICIAIS
# =============================================================================

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import tempfile
from pathlib import Path
import shutil
import os

# =============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO FASTAPI
# =============================================================================

app = FastAPI(
    title="Avaliar API", 
    version="0.0.0", 
    docs_url="/api/docs"
)

# =============================================================================
# MODELOS PYDANTIC PARA VALIDAÇÃO DE DADOS
# =============================================================================

class LaTeXCompileRequest(BaseModel):
    """Modelo para requisição de compilação LaTeX"""
    latex: str
    filename: str = "document"

class CompilationResult(BaseModel):
    """Modelo para resultado da compilação LaTeX"""
    success: bool
    pdfUrl: str = None
    error: str = None
    logs: list[str] = []

class ProvaData(BaseModel):
    """Modelo para dados de uma prova"""
    name: str
    content: str

class ProvaInfo(BaseModel):
    """Modelo para informações resumidas de uma prova"""
    id: str
    name: str
    created_at: str
    modified_at: str

# =============================================================================
# CONFIGURAÇÃO DE MIDDLEWARES
# =============================================================================

# CORS middleware - permite requisições de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TROCAR DEPOIS EM PRODUÇÃO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS E DIRETÓRIOS
# =============================================================================

# Diretório onde estão os arquivos buildados do React
REACT_BUILD_DIR = Path("./front/build/client")

# Diretório para armazenar os PDFs gerados
PDF_OUTPUT_DIR = Path("./static/pdfs")
PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Diretório para armazenar os arquivos LaTeX fonte das provas
LATEX_SOURCES_DIR = Path("./static/latex_sources")
LATEX_SOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Mount dos arquivos estáticos do React (CSS, JS, imagens, etc.)
if REACT_BUILD_DIR.exists():
    # Mount específico para assets do React (referenciados como /assets/ no index.html)
    assets_dir = REACT_BUILD_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    
    # Mount geral para arquivos estáticos (favicon, etc.)
    app.mount("/static", StaticFiles(directory=str(REACT_BUILD_DIR), html=True), name="static")

# =============================================================================
# ROTAS DE SISTEMA E HEALTH CHECK
# =============================================================================

@app.get("/api/health")
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {"status": "healthy"}

# =============================================================================
# ROTAS DA API - COMPILAÇÃO LaTeX
# =============================================================================

@app.post("/api/compile-latex")
async def compile_latex(request: LaTeXCompileRequest):
    """
    Compila código LaTeX para PDF usando pdflatex
    
    Args:
        request: Objeto contendo o código LaTeX e nome do arquivo
        
    Returns:
        CompilationResult: Resultado da compilação com sucesso/erro e logs
    """
    # Use filename as compile ID to reuse same file
    compile_id = request.filename

    # Create temporary directory for compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write LaTeX content to file
        tex_file = temp_path / f"{request.filename}.tex"
        tex_file.write_text(request.latex, encoding='utf-8')

        try:
            # Run pdflatex compilation
            # Run twice to ensure proper cross-references
            for _ in range(2):
                result = subprocess.run([
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory', str(temp_path),
                    str(tex_file)
                ], capture_output=True, text=True, timeout=30)

            # Check if PDF was generated
            pdf_file = temp_path / f"{request.filename}.pdf"

            if pdf_file.exists():
                # Copy PDF to static directory
                output_pdf = PDF_OUTPUT_DIR / f"{compile_id}.pdf"
                shutil.copy2(pdf_file, output_pdf)

                # Return success with PDF URL
                return CompilationResult(
                    success=True,
                    pdfUrl=f"/api/pdfs/{compile_id}.pdf",
                    logs=result.stdout.split('\n') if result.stdout else []
                )
            else:
                # Compilation failed
                error_logs = []

                # Try to read log file for more details
                log_file = temp_path / f"{request.filename}.log"
                if log_file.exists():
                    error_logs = log_file.read_text(encoding='utf-8', errors='ignore').split('\n')
                else:
                    error_logs = []

                # Include both stdout and stderr for debugging
                all_logs = []
                if result.stdout:
                    all_logs.extend(["=== STDOUT ==="] + result.stdout.split('\n'))
                if result.stderr:
                    all_logs.extend(["=== STDERR ==="] + result.stderr.split('\n'))
                if error_logs:
                    all_logs.extend(["=== LOG FILE ==="] + error_logs)

                return CompilationResult(
                    success=False,
                    error=f"PDF compilation failed. Exit code: {result.returncode}",
                    logs=all_logs if all_logs else ["No compilation output available"]
                )

        except subprocess.TimeoutExpired:
            return CompilationResult(
                success=False,
                error="Compilation timeout (30 seconds exceeded)",
                logs=[]
            )
        except FileNotFoundError:
            return CompilationResult(
                success=False,
                error="pdflatex not found. Please install LaTeX distribution (TeX Live, MiKTeX, etc.)",
                logs=[]
            )
        except Exception as e:
            return CompilationResult(
                success=False,
                error=f"Compilation error: {str(e)}",
                logs=[]
            )

@app.get("/api/pdfs/{filename}")
async def get_pdf(filename: str):
    """
    Serve os arquivos PDF compilados
    
    Args:
        filename: Nome do arquivo PDF a ser servido
        
    Returns:
        FileResponse: Arquivo PDF com headers apropriados
    """
    pdf_path = PDF_OUTPUT_DIR / filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=str(pdf_path),
        media_type='application/pdf',
        filename=filename,
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache",
            "X-Frame-Options": "ALLOWALL"
        }
    )

# =============================================================================
# ROTAS DA API - GERENCIAMENTO DE PROVAS
# =============================================================================

@app.post("/api/provas")
async def save_prova(prova: ProvaData):
    """
    Salva uma prova (conteúdo LaTeX) no servidor
    
    Args:
        prova: Dados da prova (nome e conteúdo)
        
    Returns:
        ProvaInfo: Informações da prova salva
    """
    import re
    from datetime import datetime
    
    # Sanitize filename
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', prova.name)
    if not safe_name:
        safe_name = "prova"
    
    # Create unique ID based on name and timestamp
    prova_id = f"{safe_name}_{int(datetime.now().timestamp())}"
    
    # Save LaTeX content
    latex_file = LATEX_SOURCES_DIR / f"{prova_id}.tex"
    latex_file.write_text(prova.content, encoding='utf-8')
    
    # Get file stats
    stats = latex_file.stat()
    created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
    modified_at = datetime.fromtimestamp(stats.st_mtime).isoformat()
    
    return ProvaInfo(
        id=prova_id,
        name=prova.name,
        created_at=created_at,
        modified_at=modified_at
    )

@app.get("/api/provas")
async def list_provas():
    """
    Lista todas as provas salvas
    
    Returns:
        list[ProvaInfo]: Lista de informações das provas
    """
    from datetime import datetime
    
    provas = []
    
    for latex_file in LATEX_SOURCES_DIR.glob("*.tex"):
        prova_id = latex_file.stem
        
        # Extract original name from ID (remove timestamp)
        name_parts = prova_id.rsplit('_', 1)
        name = name_parts[0].replace('_', ' ')
        
        # Get file stats
        stats = latex_file.stat()
        created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
        modified_at = datetime.fromtimestamp(stats.st_mtime).isoformat()
        
        provas.append(ProvaInfo(
            id=prova_id,
            name=name,
            created_at=created_at,
            modified_at=modified_at
        ))
    
    # Sort by modification date (newest first)
    provas.sort(key=lambda p: p.modified_at, reverse=True)
    
    return provas

@app.get("/api/provas/{prova_id}")
async def get_prova(prova_id: str):
    """
    Recupera o conteúdo de uma prova salva
    
    Args:
        prova_id: ID da prova
        
    Returns:
        ProvaData: Dados da prova
    """
    latex_file = LATEX_SOURCES_DIR / f"{prova_id}.tex"
    
    if not latex_file.exists():
        raise HTTPException(status_code=404, detail="Prova not found")
    
    content = latex_file.read_text(encoding='utf-8')
    
    # Extract name from ID
    name_parts = prova_id.rsplit('_', 1)
    name = name_parts[0].replace('_', ' ')
    
    return ProvaData(name=name, content=content)

@app.put("/api/provas/{prova_id}")
async def update_prova(prova_id: str, prova: ProvaData):
    """
    Atualiza uma prova existente
    
    Args:
        prova_id: ID da prova
        prova: Novos dados da prova
        
    Returns:
        ProvaInfo: Informações atualizadas da prova
    """
    from datetime import datetime
    
    latex_file = LATEX_SOURCES_DIR / f"{prova_id}.tex"
    
    if not latex_file.exists():
        raise HTTPException(status_code=404, detail="Prova not found")
    
    # Update content
    latex_file.write_text(prova.content, encoding='utf-8')
    
    # Get updated stats
    stats = latex_file.stat()
    created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
    modified_at = datetime.fromtimestamp(stats.st_mtime).isoformat()
    
    return ProvaInfo(
        id=prova_id,
        name=prova.name,
        created_at=created_at,
        modified_at=modified_at
    )

@app.delete("/api/provas/{prova_id}")
async def delete_prova(prova_id: str):
    """
    Exclui uma prova salva
    
    Args:
        prova_id: ID da prova
        
    Returns:
        dict: Mensagem de sucesso
    """
    latex_file = LATEX_SOURCES_DIR / f"{prova_id}.tex"
    
    if not latex_file.exists():
        raise HTTPException(status_code=404, detail="Prova not found")
    
    # Delete LaTeX file
    latex_file.unlink()
    
    # Delete associated PDF if exists
    pdf_file = PDF_OUTPUT_DIR / f"{prova_id}.pdf"
    if pdf_file.exists():
        pdf_file.unlink()
    
    return {"message": "Prova deleted successfully", "id": prova_id}

# =============================================================================
# ROTAS DO FRONTEND - SERVINDO A APLICAÇÃO REACT
# =============================================================================

@app.get("/")
async def serve_react_root():
    """
    Serve a aplicação React na rota raiz
    
    Returns:
        FileResponse: Arquivo index.html do React ou página de erro
    """
    index_path = REACT_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return HTMLResponse(
            content="<h1>React app not built</h1><p>Please run 'npm run build' in the front/ directory.</p>",
            status_code=404
        )

@app.get("/{full_path:path}")
async def serve_react_app(request: Request, full_path: str):
    """
    Serve a aplicação React para todas as rotas não-API.
    Isso permite o roteamento client-side da SPA (Single Page Application).
    
    Args:
        request: Objeto da requisição HTTP
        full_path: Caminho completo da URL requisitada
        
    Returns:
        FileResponse: Arquivo index.html do React para permitir client-side routing
    """
    # Não intercepta rotas da API
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    # Não intercepta arquivos estáticos (são servidos pelo mount)
    if full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Static file not found")
        
    # Serve o index.html do React para todas as outras rotas (SPA routing)
    index_path = REACT_BUILD_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return HTMLResponse(
            content="<h1>React app not built</h1><p>Please run 'npm run build' in the front/ directory.</p>",
            status_code=404
        )

# =============================================================================
# CONFIGURAÇÃO DE EXECUÇÃO DO SERVIDOR
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    # Porta configurável via variável de ambiente, padrão 4200 para desenvolvimento
    port = int(os.getenv("API_PORT", "4200"))
    # Executa o servidor em modo desenvolvimento com auto-reload
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)