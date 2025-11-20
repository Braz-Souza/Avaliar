"""
SQLModel for Correcao (exam correction) management
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

if TYPE_CHECKING:
    from .aluno import Aluno, AlunoRead
    from .turma import Turma, TurmaRead
    from .prova import Prova, ProvaRead
    from .user import User, UserRead


class CorrecaoBase(SQLModel):
    """Base model for Correcao with common fields"""
    aluno_id: UUID = Field(
        foreign_key="alunos.id",
        description="ID do aluno que fez a prova"
    )
    turma_id: UUID = Field(
        foreign_key="turmas.id",
        description="ID da turma em que a prova foi aplicada"
    )
    prova_id: UUID = Field(
        foreign_key="provas.id",
        description="ID da prova que foi corrigida"
    )
    corrigido_por: UUID = Field(
        foreign_key="users.id",
        description="ID do usuário que fez a correção"
    )
    data_correcao: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Data e hora em que a correção foi realizada"
    )
    nota: Optional[float] = Field(
        default=None,
        description="Nota final da prova (calculada automaticamente)"
    )
    total_questoes: Optional[int] = Field(
        default=None,
        description="Total de questões da prova"
    )
    acertos: Optional[int] = Field(
        default=None,
        description="Total de acertos do aluno"
    )


class Correcao(CorrecaoBase, table=True):
    """Correcao table model"""
    __tablename__ = "correcoes"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
        description="Unique identifier for correcao"
    )

    # Relationships
    aluno: Optional["Aluno"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    turma: Optional["Turma"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    prova: Optional["Prova"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    corretor: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
    respostas: List["CorrecaoResposta"] = Relationship(
        back_populates="correcao",
        sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"}
    )


class CorrecaoRespostaBase(SQLModel):
    """Base model for CorrecaoResposta with common fields"""
    correcao_id: UUID = Field(
        foreign_key="correcoes.id",
        description="ID da correção a que esta resposta pertence"
    )
    questao_numero: int = Field(
        description="Número da questão (1, 2, 3, etc.)"
    )
    resposta_marcada: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10)),
        description="Resposta marcada pelo aluno (A, B, C, D, E, etc. ou '?' se não marcou)"
    )
    resposta_correta: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10)),
        description="Resposta correta da questão (A, B, C, D, E, etc.)"
    )
    esta_correta: Optional[bool] = Field(
        default=None,
        description="Se a resposta do aluno está correta"
    )


class CorrecaoResposta(CorrecaoRespostaBase, table=True):
    """CorrecaoResposta table model - stores individual answers for each question"""
    __tablename__ = "correcao_respostas"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()),
        description="Unique identifier for correcao resposta"
    )

    # Relationships
    correcao: Optional["Correcao"] = Relationship(
        back_populates="respostas",
        sa_relationship_kwargs={"lazy": "joined"}
    )


class CorrecaoCreate(CorrecaoBase):
    """Schema for creating a new correcao"""
    pass


class CorrecaoRespostaCreate(CorrecaoRespostaBase):
    """Schema for creating a new correcao resposta"""
    pass


class CorrecaoRespostaRead(CorrecaoRespostaBase):
    """Schema for reading correcao resposta data"""
    id: UUID = Field(description="Unique identifier for correcao resposta")


class CorrecaoRead(CorrecaoBase):
    """Schema for reading correcao data with all relationships"""
    id: UUID = Field(description="Unique identifier for correcao")
    respostas: List[CorrecaoRespostaRead] = Field(
        default_factory=list,
        description="Lista de respostas da correção"
    )


class CorrecaoReadWithDetails(CorrecaoRead):
    """Schema for reading correcao data with detailed relationships"""
    aluno: Optional["AlunoRead"] = None
    turma: Optional["TurmaRead"] = None
    prova: Optional["ProvaRead"] = None
    corretor: Optional["UserRead"] = None


# Forward references will be resolved by model_rebuild in __init__.py
