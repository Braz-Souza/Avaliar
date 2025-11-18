"""add_unique_constraints_to_randomizacao_tables

Revision ID: d6e770c49a8b
Revises: 96b9cfe59411
Create Date: 2025-11-16 17:04:52.813939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6e770c49a8b'
down_revision = '96b9cfe59411'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Add unique constraint to turma_provas to prevent duplicate turma-prova links
    op.create_unique_constraint(
        'uq_turma_provas_turma_id_prova_id',
        'turma_provas',
        ['turma_id', 'prova_id']
    )

    # Add unique constraint to aluno_randomizacoes to prevent duplicate randomizations
    op.create_unique_constraint(
        'uq_aluno_randomizacoes_turma_prova_id_aluno_id',
        'aluno_randomizacoes',
        ['turma_prova_id', 'aluno_id']
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Remove unique constraints
    op.drop_constraint('uq_aluno_randomizacoes_turma_prova_id_aluno_id', 'aluno_randomizacoes', type_='unique')
    op.drop_constraint('uq_turma_provas_turma_id_prova_id', 'turma_provas', type_='unique')