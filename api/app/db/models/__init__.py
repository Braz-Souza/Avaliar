"""
Database models module
"""

from .prova import Prova, ProvaCreate, ProvaUpdate, ProvaRead
from .user import User, UserCreate, UserRead
from .turma import Turma, TurmaCreate, TurmaUpdate, TurmaRead
from .aluno import Aluno, AlunoCreate, AlunoUpdate, AlunoRead
from .questao import (
    Questao, QuestaoCreate, QuestaoUpdate, QuestaoRead,
    QuestaoOpcao, QuestaoOpcaoCreate, QuestaoOpcaoUpdate, QuestaoOpcaoRead
)

__all__ = [
    "Prova",
    "ProvaCreate",
    "ProvaUpdate",
    "ProvaRead",
    "User",
    "UserCreate",
    "UserRead",
    "Turma",
    "TurmaCreate",
    "TurmaUpdate",
    "TurmaRead",
    "Aluno",
    "AlunoCreate",
    "AlunoUpdate",
    "AlunoRead",
    "Questao",
    "QuestaoCreate",
    "QuestaoUpdate",
    "QuestaoRead",
    "QuestaoOpcao",
    "QuestaoOpcaoCreate",
    "QuestaoOpcaoUpdate",
    "QuestaoOpcaoRead"
]

# Rebuild models to resolve forward references
AlunoRead.model_rebuild()
ProvaRead.model_rebuild()
QuestaoRead.model_rebuild()
QuestaoOpcaoRead.model_rebuild()
