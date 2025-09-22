from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import tempfile
from pathlib import Path
import shutil

app = FastAPI(title="Avaliar API", version="0.0.0")

class LaTeXCompileRequest(BaseModel):
    latex: str
    filename: str = "document"

class CompilationResult(BaseModel):
    success: bool
    pdfUrl: str = None
    error: str = None
    logs: list[str] = []

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "running..."}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

# Create output directory for PDFs
PDF_OUTPUT_DIR = Path("./static/pdfs")
PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/api/compile-latex")
async def compile_latex(request: LaTeXCompileRequest):
    """Compile LaTeX to PDF using pdflatex"""

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
    """Serve compiled PDF files"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)