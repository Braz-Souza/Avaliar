"""
SQLModel for Prova (exam/test) management
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class ProvaBase(SQLModel):
    """Base model for Prova with common fields"""
    name: str = Field(index=True, description="Name of prova")
    content: str = Field(
        sa_column=Column(Text),
        description="LaTeX content of prova"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Timestamp when prova was created"
    )
    modified_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        ),
        description="Timestamp when prova was last modified"
    )
    created_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        description="ID of user who created this prova"
    )
    deleted: bool = Field(
        default=False,
        description="Soft delete flag - if True, prova is hidden from queries"
    )


class Prova(ProvaBase, table=True):
    """Prova table model"""
    __tablename__ = "provas"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
        description="Unique identifier for prova"
    )

    # Relationships
    creator: Optional["User"] = Relationship(
        back_populates="provas",
        sa_relationship_kwargs={"lazy": "select"}
    )
    questoes: List["Questao"] = Relationship(
        back_populates="prova",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan"
        }
    )


class ProvaCreate(ProvaBase):
    """Schema for creating a new prova"""
    pass


class ProvaUpdate(SQLModel):
    """Schema for updating an existing prova"""
    name: Optional[str] = Field(default=None, description="Updated name of prova")
    content: Optional[str] = Field(default=None, description="Updated LaTeX content")


class ProvaRead(ProvaBase):
    """Schema for reading prova data"""
    id: UUID = Field(description="Unique identifier for prova")
