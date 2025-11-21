"""
SQLModel for Access Log (Registro de Acessos)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, INET


class AcessoBase(SQLModel):
    """Base model for Acesso with common fields"""
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,  # IPv6 max length
        description="IP address of the access attempt"
    )
    sucesso: bool = Field(
        default=False,
        description="Whether the login attempt was successful"
    )
    data_hora: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Timestamp of the access attempt"
    )


class Acesso(AcessoBase, table=True):
    """Acesso table model - logs all login attempts"""
    __tablename__ = "acessos"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
        description="Unique identifier for access log"
    )


class AcessoCreate(AcessoBase):
    """Schema for creating a new access log"""
    pass


class AcessoRead(AcessoBase):
    """Schema for reading access log data"""
    id: UUID

    class Config:
        from_attributes = True


class AcessoReadWithPagination(SQLModel):
    """Schema for paginated access log response"""
    total: int
    items: list[AcessoRead]
    page: int
    page_size: int

    class Config:
        from_attributes = True
