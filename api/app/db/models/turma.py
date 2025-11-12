"""
SQLModel for Turma (class) management
"""

from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


# Association table for many-to-many relationship between Turma and Aluno
turma_aluno_association = Table(
    "turma_aluno",
    SQLModel.metadata,
    Column("turma_id", PG_UUID(as_uuid=True), ForeignKey("turmas.id"), primary_key=True),
    Column("aluno_id", PG_UUID(as_uuid=True), ForeignKey("alunos.id"), primary_key=True),
)


class TurmaBase(SQLModel):
    """Base model for Turma with common fields"""
    ano: int = Field(description="Year of the class")
    materia: str = Field(description="Subject of the class")
    curso: str = Field(description="Course of the class")
    periodo: int = Field(description="Period of the class")


class Turma(TurmaBase, table=True):
    """Turma table model"""
    __tablename__ = "turmas"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default='gen_random_uuid()'),
        description="Unique identifier for turma"
    )

    # Relationships
    alunos: List["Aluno"] = Relationship(
        back_populates="turmas",
        sa_relationship_kwargs={
            "lazy": "select",
            "secondary": turma_aluno_association
        }
    )


class TurmaCreate(TurmaBase):
    """Schema for creating a new turma"""
    pass


class TurmaUpdate(SQLModel):
    """Schema for updating an existing turma"""
    ano: Optional[int] = Field(default=None, description="Updated year of the class")
    materia: Optional[str] = Field(default=None, description="Updated subject of the class")
    curso: Optional[str] = Field(default=None, description="Updated course of the class")
    periodo: Optional[int] = Field(default=None, description="Updated period of the class")


class TurmaRead(TurmaBase):
    """Schema for reading turma data"""
    id: UUID = Field(description="Unique identifier for turma")
