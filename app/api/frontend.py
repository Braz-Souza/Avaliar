"""
Router para servir a aplicação React (frontend)
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from app.core.config import settings

router = APIRouter(tags=["Frontend"])


@router.get("/", response_class=HTMLResponse)
async def serve_react_root():
    """
    Serve a aplicação React na rota raiz
    
    Returns:
        FileResponse com index.html ou página de erro
    """
    index_path = settings.REACT_BUILD_DIR / "index.html"
    
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return HTMLResponse(
            content="<h1>React app not built</h1>"
                   "<p>Please run 'npm run build' in the front/ directory.</p>",
            status_code=404
        )


@router.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(request: Request, full_path: str):
    """
    Serve a aplicação React para todas as rotas não-API.
    Isso permite o roteamento client-side da SPA (Single Page Application).
    
    Args:
        request: Objeto da requisição HTTP
        full_path: Caminho completo da URL requisitada
        
    Returns:
        FileResponse com index.html para permitir client-side routing
        
    Raises:
        HTTPException: Se a rota for API ou arquivo estático não encontrado
    """
    # Não intercepta rotas da API
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    # Não intercepta arquivos estáticos (são servidos pelo mount)
    if full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Static file not found")
    
    # Serve o index.html do React para todas as outras rotas (SPA routing)
    index_path = settings.REACT_BUILD_DIR / "index.html"
    
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return HTMLResponse(
            content="<h1>React app not built</h1>"
                   "<p>Please run 'npm run build' in the front/ directory.</p>",
            status_code=404
        )
