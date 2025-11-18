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
from .randomizacao import (
    TurmaProva, TurmaProvaCreate, TurmaProvaRead,
    AlunoRandomizacao, AlunoRandomizacaoCreate, AlunoRandomizacaoRead
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
    "QuestaoOpcaoRead",
    "TurmaProva",
    "TurmaProvaCreate",
    "TurmaProvaRead",
    "AlunoRandomizacao",
    "AlunoRandomizacaoCreate",
    "AlunoRandomizacaoRead"
]

# Rebuild models to resolve forward references
AlunoRead.model_rebuild()
ProvaRead.model_rebuild()
QuestaoRead.model_rebuild()
QuestaoOpcaoRead.model_rebuild()
TurmaProvaRead.model_rebuild()
AlunoRandomizacaoRead.model_rebuild()
