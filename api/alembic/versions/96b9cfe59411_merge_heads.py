"""merge_heads

Revision ID: 96b9cfe59411
Revises: 4bc74ec62569, add_randomizacao_tables
Create Date: 2025-11-16 17:04:42.358424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96b9cfe59411'
down_revision = ('4bc74ec62569', 'add_randomizacao_tables')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    pass


def downgrade() -> None:
    """Downgrade database schema."""
    pass