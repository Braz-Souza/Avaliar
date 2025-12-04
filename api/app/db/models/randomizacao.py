"""
SQLModel for randomization management
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text, DateTime, ForeignKey, JSON, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class TurmaProvaBase(SQLModel):
    """Base model for TurmaProva with common fields"""
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text('now()')),
        description="Timestamp when the exam was linked to the class"
    )


class TurmaProva(TurmaProvaBase, table=True):
    """TurmaProva table model - links exams to classes"""
    __tablename__ = "turma_provas"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        description="Unique identifier for turma-prova relationship"
    )

    turma_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="CASCADE")),
        description="ID of the turma"
    )

    prova_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("provas.id", ondelete="CASCADE")),
        description="ID of the prova"
    )

    # Relationships
    turma: "Turma" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
    prova: "Prova" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )
    randomizacoes: List["AlunoRandomizacao"] = Relationship(
        back_populates="turma_prova",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan"
        }
    )


class TurmaProvaCreate(TurmaProvaBase):
    """Schema for creating a new turma-prova link"""
    turma_id: UUID = Field(description="ID of the turma")
    prova_id: UUID = Field(description="ID of the prova")


class TurmaProvaRead(TurmaProvaBase):
    """Schema for reading turma-prova data"""
    id: UUID = Field(description="Unique identifier for turma-prova relationship")
    turma_id: UUID = Field(description="ID of the turma")
    prova_id: UUID = Field(description="ID of the prova")
    data: Optional[date] = Field(default=None, description="Date when the exam is scheduled")


class AlunoRandomizacaoBase(SQLModel):
    """Base model for AlunoRandomizacao with common fields"""
    questoes_order: List[int] = Field(
        sa_column=Column(JSON),
        description="List of question IDs in randomized order"
    )
    alternativas_order: dict = Field(
        sa_column=Column(JSON),
        description="Dictionary mapping question IDs to their alternative order"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text('now()')),
        description="Timestamp when the randomization was created"
    )


class AlunoRandomizacao(AlunoRandomizacaoBase, table=True):
    """AlunoRandomizacao table model - stores randomization for each student"""
    __tablename__ = "aluno_randomizacoes"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        description="Unique identifier for aluno randomization"
    )

    turma_prova_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("turma_provas.id", ondelete="CASCADE")),
        description="ID of the turma-prova relationship"
    )

    aluno_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("alunos.id", ondelete="CASCADE")),
        description="ID of the aluno"
    )

    # Relationships
    turma_prova: TurmaProva = Relationship(
        back_populates="randomizacoes",
        sa_relationship_kwargs={"lazy": "select"}
    )
    aluno: "Aluno" = Relationship(
        sa_relationship_kwargs={"lazy": "select"}
    )


class AlunoRandomizacaoCreate(AlunoRandomizacaoBase):
    """Schema for creating a new aluno randomization"""
    turma_prova_id: UUID = Field(description="ID of the turma-prova relationship")
    aluno_id: UUID = Field(description="ID of the aluno")


class AlunoRandomizacaoRead(AlunoRandomizacaoBase):
    """Schema for reading aluno randomization data"""
    id: UUID = Field(description="Unique identifier for aluno randomization")
    turma_prova_id: UUID = Field(description="ID of the turma-prova relationship")
    aluno_id: UUID = Field(description="ID of the aluno")


# Import to avoid circular imports
from app.db.models.turma import Turma
from app.db.models.prova import Prova
from app.db.models.aluno import Aluno
