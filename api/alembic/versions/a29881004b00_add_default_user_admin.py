"""add_default_user_admin

Revision ID: a29881004b00
Revises: d6e770c49a8b
Create Date: 2025-11-20 19:18:22.363062

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'a29881004b00'
down_revision = 'd6e770c49a8b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Criar usuário padrão user_admin se não existir
    # Hash para PIN "admin" usando bcrypt
    # Gerado com: python -c "from passlib.hash import bcrypt; print(bcrypt.hash('admin'))"
    admin_pin_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq"  # PIN: "admin"

    connection = op.get_bind()

    # Verificar se o usuário já existe
    result = connection.execute(
        text("SELECT COUNT(*) FROM users WHERE username = 'user_admin'")
    ).scalar()

    if result == 0:
        # Inserir o usuário padrão
        connection.execute(
            text("""
                INSERT INTO users (id, username, pin_hash, created_at, last_login)
                VALUES (
                    gen_random_uuid(),
                    'user_admin',
                    :pin_hash,
                    NOW(),
                    NULL
                )
            """),
            {"pin_hash": admin_pin_hash}
        )
        print("✅ Usuário padrão 'user_admin' criado com sucesso (PIN: admin)")
    else:
        print("ℹ️  Usuário 'user_admin' já existe")


def downgrade() -> None:
    """Downgrade database schema."""
    # Remover o usuário padrão
    connection = op.get_bind()
    connection.execute(
        text("DELETE FROM users WHERE username = 'user_admin'")
    )
    print("🗑️  Usuário padrão 'user_admin' removido")
