"""
Service for managing access logs (Acessos)
"""

from typing import Optional
from sqlmodel import Session
from fastapi import Request

from app.db.models.acesso import Acesso, AcessoCreate


class AcessoService:
    """Service for managing access logs"""

    @staticmethod
    def get_client_ip(request: Request) -> Optional[str]:
        """
        Extract client IP address from request

        Args:
            request: FastAPI request object

        Returns:
            Client IP address or None
        """
        # Try to get real IP from X-Forwarded-For header (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        # Try X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client host
        if request.client:
            return request.client.host

        return None

    @staticmethod
    def registrar_acesso(
        session: Session,
        request: Request,
        sucesso: bool
    ) -> Acesso:
        """
        Register an access attempt in the database

        Args:
            session: Database session
            request: FastAPI request object
            sucesso: Whether the login was successful

        Returns:
            Created Acesso object
        """
        ip_address = AcessoService.get_client_ip(request)

        acesso_data = AcessoCreate(
            ip_address=ip_address,
            sucesso=sucesso
        )

        acesso = Acesso.model_validate(acesso_data)
        session.add(acesso)
        session.commit()
        session.refresh(acesso)

        return acesso

