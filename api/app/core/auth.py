"""
Módulo de autenticação usando AuthX
"""

from authx import AuthX, AuthXConfig
from app.core.config import settings


def create_auth() -> AuthX:
    """
    Factory para criar instância do AuthX configurado
    
    Returns:
        AuthX: Instância configurada do AuthX
    """
    config = AuthXConfig(
        JWT_ALGORITHM=settings.JWT_ALGORITHM,
        JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
        JWT_TOKEN_LOCATION=settings.JWT_TOKEN_LOCATION,
    )
    
    return AuthX(config=config)


# Instância global de autenticação
auth = create_auth()
