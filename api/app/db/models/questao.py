"""
SQLModel for Questao (question) management
"""

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class QuestaoBase(SQLModel):
    """Base model for Questao with common fields"""
    order: int = Field(
        description="Order of the question in the exam"
    )
    text: str = Field(
        sa_column=Column(Text),
        description="Question text"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when question was created"
    )
    modified_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when question was last modified"
    )


class Questao(QuestaoBase, table=True):
    """Questao table model"""
    __tablename__ = "questoes"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
        description="Unique identifier for questao"
    )

    prova_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("provas.id", ondelete="CASCADE")),
        description="ID of the prova this question belongs to"
    )

    # Relationships
    prova: "Prova" = Relationship(
        back_populates="questoes",
        sa_relationship_kwargs={"lazy": "select"}
    )
    opcoes: List["QuestaoOpcao"] = Relationship(
        back_populates="questao",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan"
        }
    )


class QuestaoCreate(QuestaoBase):
    """Schema for creating a new questao"""
    prova_id: UUID = Field(description="ID of the prova this question belongs to")


class QuestaoUpdate(SQLModel):
    """Schema for updating an existing questao"""
    order: Optional[int] = Field(default=None, description="Updated order of the question")
    text: Optional[str] = Field(default=None, description="Updated question text")


class QuestaoRead(QuestaoBase):
    """Schema for reading questao data"""
    id: UUID = Field(description="Unique identifier for questao")
    prova_id: UUID = Field(description="ID of the prova this question belongs to")
    opcoes: List["QuestaoOpcaoRead"] = []


class QuestaoOpcaoBase(SQLModel):
    """Base model for QuestaoOpcao with common fields"""
    order: int = Field(
        description="Order of the option in the question"
    )
    text: str = Field(
        sa_column=Column(Text),
        description="Option text"
    )
    is_correct: bool = Field(
        default=False,
        description="Whether this option is the correct answer"
    )


class QuestaoOpcao(QuestaoOpcaoBase, table=True):
    """QuestaoOpcao table model"""
    __tablename__ = "questao_opcoes"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
        description="Unique identifier for questao opcao"
    )

    questao_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("questoes.id", ondelete="CASCADE")),
        description="ID of the questao this option belongs to"
    )

    # Relationships
    questao: Questao = Relationship(
        back_populates="opcoes",
        sa_relationship_kwargs={"lazy": "select"}
    )


class QuestaoOpcaoCreate(QuestaoOpcaoBase):
    """Schema for creating a new questao opcao"""
    questao_id: UUID = Field(description="ID of the questao this option belongs to")


class QuestaoOpcaoUpdate(SQLModel):
    """Schema for updating an existing questao opcao"""
    order: Optional[int] = Field(default=None, description="Updated order of the option")
    text: Optional[str] = Field(default=None, description="Updated option text")
    is_correct: Optional[bool] = Field(default=None, description="Updated correct flag")


class QuestaoOpcaoRead(QuestaoOpcaoBase):
    """Schema for reading questao opcao data"""
    id: UUID = Field(description="Unique identifier for questao opcao")
    questao_id: UUID = Field(description="ID of the questao this option belongs to")


# Import to avoid circular imports
from app.db.models.prova import Prova
