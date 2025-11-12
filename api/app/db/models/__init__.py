"""
Database models module
"""

from .prova import Prova, ProvaCreate, ProvaUpdate, ProvaRead
from .user import User, UserCreate, UserRead
from .turma import Turma, TurmaCreate, TurmaUpdate, TurmaRead
from .aluno import Aluno, AlunoCreate, AlunoUpdate, AlunoRead

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
    "AlunoRead"
]

# Rebuild models to resolve forward references
AlunoRead.model_rebuild()
