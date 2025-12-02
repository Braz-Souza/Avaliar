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
from .correcao import (
    Correcao, CorrecaoCreate, CorrecaoRead, CorrecaoReadWithDetails,
    CorrecaoResposta, CorrecaoRespostaCreate, CorrecaoRespostaRead
)
from .acesso import Acesso, AcessoCreate, AcessoRead, AcessoReadWithPagination
from .data_prova import DataProva, DataProvaCreate, DataProvaUpdate, DataProvaRead

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
    "AlunoRandomizacaoRead",
    "Correcao",
    "CorrecaoCreate",
    "CorrecaoRead",
    "CorrecaoReadWithDetails",
    "CorrecaoResposta",
    "CorrecaoRespostaCreate",
    "CorrecaoRespostaRead",
    "Acesso",
    "AcessoCreate",
    "AcessoRead",
    "AcessoReadWithPagination",
    "DataProva",
    "DataProvaCreate",
    "DataProvaUpdate",
    "DataProvaRead"
]

# Rebuild models to resolve forward references
AlunoRead.model_rebuild()
ProvaRead.model_rebuild()
QuestaoRead.model_rebuild()
QuestaoOpcaoRead.model_rebuild()
TurmaProvaRead.model_rebuild()
AlunoRandomizacaoRead.model_rebuild()
CorrecaoRead.model_rebuild()
CorrecaoReadWithDetails.model_rebuild()
CorrecaoRespostaRead.model_rebuild()
AcessoRead.model_rebuild()
DataProvaRead.model_rebuild()
