"""add_acessos_table

Revision ID: de9c7bc08242
Revises: a29881004b00
Create Date: 2025-11-20 20:10:30.412459

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'de9c7bc08242'
down_revision = 'a29881004b00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Remove columns from acessos table
    op.drop_column('acessos', 'mensagem')
    op.drop_column('acessos', 'user_agent')
    op.drop_column('acessos', 'username')


def downgrade() -> None:
    """Downgrade database schema."""
    # Re-add columns to acessos table
    op.add_column('acessos', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('acessos', sa.Column('user_agent', sa.Text(), nullable=True))
    op.add_column('acessos', sa.Column('mensagem', sa.Text(), nullable=True))