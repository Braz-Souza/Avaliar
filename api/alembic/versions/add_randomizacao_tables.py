"""Add randomizacao tables

Revision ID: add_randomizacao_tables
Revises: 0363b596667a
Create Date: 2025-11-16 16:28:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_randomizacao_tables'
down_revision = '0363b596667a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create turma_provas table
    op.create_table(
        'turma_provas',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('func.now()'), nullable=True),
        sa.Column('turma_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prova_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['prova_id'], ['provas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_turma_provas_turma_id'), 'turma_provas', ['turma_id'], unique=False)
    op.create_index(op.f('ix_turma_provas_prova_id'), 'turma_provas', ['prova_id'], unique=False)

    # Create aluno_randomizacoes table
    op.create_table(
        'aluno_randomizacoes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('questoes_order', sa.JSON(), nullable=False),
        sa.Column('alternativas_order', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('func.now()'), nullable=True),
        sa.Column('turma_prova_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('aluno_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['alunos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['turma_prova_id'], ['turma_provas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aluno_randomizacoes_turma_prova_id'), 'aluno_randomizacoes', ['turma_prova_id'], unique=False)
    op.create_index(op.f('ix_aluno_randomizacoes_aluno_id'), 'aluno_randomizacoes', ['aluno_id'], unique=False)


def downgrade() -> None:
    # Drop aluno_randomizacoes table
    op.drop_index(op.f('ix_aluno_randomizacoes_aluno_id'), table_name='aluno_randomizacoes')
    op.drop_index(op.f('ix_aluno_randomizacoes_turma_prova_id'), table_name='aluno_randomizacoes')
    op.drop_table('aluno_randomizacoes')

    # Drop turma_provas table
    op.drop_index(op.f('ix_turma_provas_prova_id'), table_name='turma_provas')
    op.drop_index(op.f('ix_turma_provas_turma_id'), table_name='turma_provas')
    op.drop_table('turma_provas')
