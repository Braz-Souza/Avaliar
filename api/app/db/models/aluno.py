"""
SQLModel for Aluno (student) management
"""

from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

if TYPE_CHECKING:
    from .turma import TurmaRead


class AlunoBase(SQLModel):
    """Base model for Aluno with common fields"""
    nome: str = Field(description="Name of the student")
    email: str = Field(
        unique=True,
        index=True,
        description="Unique email of the student"
    )
    matricula: str = Field(
        unique=True,
        index=True,
        description="Unique registration number of the student"
    )


class Aluno(AlunoBase, table=True):
    """Aluno table model"""
    __tablename__ = "alunos"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default='gen_random_uuid()'),
        description="Unique identifier for aluno"
    )

    # Relationships
    turmas: List["Turma"] = Relationship(
        back_populates="alunos",
        sa_relationship_kwargs={
            "lazy": "select",
            "secondary": "turma_aluno"
        }
    )


class AlunoCreate(AlunoBase):
    """Schema for creating a new aluno"""
    turma_ids: List[UUID] = Field(description="List of turma IDs this student belongs to")


class AlunoUpdate(SQLModel):
    """Schema for updating an existing aluno"""
    nome: Optional[str] = Field(default=None, description="Updated name of the student")
    email: Optional[str] = Field(default=None, description="Updated email of the student")
    matricula: Optional[str] = Field(default=None, description="Updated registration number of the student")
    turma_ids: Optional[List[UUID]] = Field(default=None, description="Updated list of turma IDs")


class AlunoRead(AlunoBase):
    """Schema for reading aluno data"""
    id: UUID = Field(description="Unique identifier for aluno")
    turmas: List["TurmaRead"] = Field(default=[], description="List of turmas this student belongs to")
