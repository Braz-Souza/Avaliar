"""
SQLModel for DataProva (exam date) management
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class DataProvaBase(SQLModel):
    """Base model for DataProva with common fields"""
    turma_id: UUID = Field(
        foreign_key="turmas.id",
        description="ID of the turma"
    )
    prova_id: UUID = Field(
        foreign_key="provas.id",
        description="ID of the prova"
    )
    data: date = Field(
        sa_column=Column(Date),
        description="Date when the exam is scheduled"
    )


class DataProva(DataProvaBase, table=True):
    """DataProva table model"""
    __tablename__ = "data_prova"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
        description="Unique identifier for data_prova"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Timestamp when data_prova was created"
    )
    modified_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Timestamp when data_prova was last modified"
    )


class DataProvaCreate(DataProvaBase):
    """Schema for creating a new DataProva"""
    pass


class DataProvaUpdate(SQLModel):
    """Schema for updating a DataProva"""
    turma_id: Optional[UUID] = None
    prova_id: Optional[UUID] = None
    data: Optional[date] = None


class DataProvaRead(DataProvaBase):
    """Schema for reading a DataProva"""
    id: UUID
    created_at: datetime
    modified_at: datetime
