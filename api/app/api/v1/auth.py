"""
Rotas de autenticação
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.auth import auth
from app.core.dependencies import CurrentUser
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    password: str


class TokenResponse(BaseModel):
    """Schema para resposta de token"""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Schema para resposta genérica"""
    message: str


class UserInfoResponse(BaseModel):
    """Schema para informações do usuário"""
    user_id: str
    authenticated: bool


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    """
    Endpoint de login - ROTA PÚBLICA
    
    Args:
        credentials: Credenciais do usuário (password)
        
    Returns:
        TokenResponse: Token de acesso JWT
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    # TODO: Implementar validação real com banco de dados
    # Este é apenas um exemplo básico
    if credentials.password == settings.LOGIN_PIN:
        # Since we only use PIN, create token with a default user ID
        token = auth.create_access_token(uid="user_admin")
        return TokenResponse(access_token=token)
    
    raise HTTPException(
        status_code=401,
        detail={"message": "Credenciais inválidas"}
    )


@router.get("/me", response_model=UserInfoResponse)
def get_current_user_info(user_id: CurrentUser):
    """
    Retorna informações do usuário autenticado - ROTA PROTEGIDA
    
    O middleware já validou o token, apenas retornamos as informações.
    
    Args:
        user_id: ID do usuário extraído do token pelo middleware
        
    Returns:
        UserInfoResponse: Informações do usuário
    """
    return UserInfoResponse(
        user_id=user_id,
        authenticated=True
    )


@router.get("/protected", response_model=MessageResponse)
def get_protected(user_id: CurrentUser):
    """
    Endpoint protegido - exemplo - ROTA PROTEGIDA
    
    Args:
        user_id: ID do usuário extraído do token pelo middleware
        
    Returns:
        MessageResponse: Mensagem de sucesso
    """
    return MessageResponse(
        message=f"Olá {user_id}! Você está autenticado."
    )
