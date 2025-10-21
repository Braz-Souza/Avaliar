"""
Configuração de middlewares da aplicação
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.auth import auth


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticação global
    
    Requer autenticação JWT para todas as rotas da API,
    exceto rotas públicas definidas em PUBLIC_ROUTES
    """
    
    # Rotas que não requerem autenticação
    PUBLIC_ROUTES = {
        "/api/auth/login",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/health",
        "/api/system/health",
        "/api/system/info",
    }
    
    # Prefixos de rotas públicas (frontend, assets, etc)
    PUBLIC_PREFIXES = (
        "/assets/",
        "/static/",
        "/_app/",
    )
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa cada requisição verificando autenticação
        
        Args:
            request: Requisição HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response da requisição
        """
        # Permitir rotas públicas
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # Verificar se é uma rota da API que precisa de autenticação
        if request.url.path.startswith("/api/"):
            try:
                # Extrair token do header Authorization
                authorization = request.headers.get("Authorization")
                
                if not authorization:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": {
                                "message": "Token de autenticação não fornecido",
                                "code": "MISSING_TOKEN"
                            }
                        }
                    )
                
                # Verificar formato "Bearer <token>"
                if not authorization.startswith("Bearer "):
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": {
                                "message": "Formato de token inválido. Use: Bearer <token>",
                                "code": "INVALID_TOKEN_FORMAT"
                            }
                        }
                    )
                
                # Extrair e validar token
                token_value = authorization.replace("Bearer ", "")
                
                # Criar objeto RequestToken manualmente
                from authx import RequestToken
                token = RequestToken(
                    token=token_value,
                    csrf=None,
                    location="headers"
                )
                
                # Verificar token e obter payload decodificado
                payload = auth.verify_token(token=token)
                
                # Token válido, adicionar informações do usuário ao request
                request.state.user_id = payload.sub
                request.state.authenticated = True
                
            except Exception as e:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": {
                            "message": "Token inválido ou expirado",
                            "error": str(e),
                            "code": "INVALID_TOKEN"
                        }
                    }
                )
        
        return await call_next(request)
    
    def _is_public_route(self, path: str) -> bool:
        """
        Verifica se a rota é pública
        
        Args:
            path: Caminho da rota
            
        Returns:
            bool: True se a rota for pública
        """
        # Verificar rotas exatas
        if path in self.PUBLIC_ROUTES:
            return True
        
        # Verificar prefixos
        if path.startswith(self.PUBLIC_PREFIXES):
            return True
        
        # Rotas que não começam com /api/ são públicas (frontend)
        if not path.startswith("/api/"):
            return True
        
        return False


def setup_middleware(app: FastAPI) -> None:
    """
    Configura todos os middlewares da aplicação
    
    Args:
        app: Instância do FastAPI
    """
    # CORS middleware (deve ser adicionado primeiro)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )
    
    # Middleware de autenticação global
    app.add_middleware(AuthenticationMiddleware)
