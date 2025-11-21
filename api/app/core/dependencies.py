"""
Dependências de autenticação reutilizáveis
"""

from typing import Annotated, Generator
from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from app.core.database import engine


def get_session() -> Generator[Session, None, None]:
    """
    Dependency para obter uma sessão do banco de dados

    Yields:
        Session: Sessão do SQLModel
    """
    with Session(engine) as session:
        yield session


async def get_current_user(request: Request) -> str:
    """
    Dependency para obter o usuário atual autenticado pelo middleware

    O middleware AuthenticationMiddleware adiciona user_id ao request.state
    quando o token é válido.

    Args:
        request: Request do FastAPI

    Returns:
        str: User ID (uid) do token

    Raises:
        HTTPException: Se o usuário não estiver autenticado
    """
    # O middleware já validou o token e adicionou o user_id ao request.state
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "Usuário não autenticado",
                "code": "UNAUTHENTICATED"
            }
        )

    return user_id


async def get_optional_user(request: Request) -> str | None:
    """
    Dependency para obter o usuário atual de forma opcional
    Não lança erro se não houver usuário autenticado

    Args:
        request: Request do FastAPI

    Returns:
        str | None: User ID se autenticado, None caso contrário
    """
    return getattr(request.state, "user_id", None)


def is_authenticated(request: Request) -> bool:
    """
    Verifica se a requisição está autenticada

    Args:
        request: Request do FastAPI

    Returns:
        bool: True se autenticado, False caso contrário
    """
    return getattr(request.state, "authenticated", False)


# Type aliases para facilitar o uso nas rotas
CurrentUser = Annotated[str, Depends(get_current_user)]
OptionalUser = Annotated[str | None, Depends(get_optional_user)]
SessionDep = Annotated[Session, Depends(get_session)]
