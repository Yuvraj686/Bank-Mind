"""007 seed demo banker

Revision ID: 007
Revises: 006
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa
import uuid
import bcrypt

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

DEMO_EMAIL = 'admin@bankmind.ai'
DEMO_PASSWORD = 'demo123'


def upgrade() -> None:
    password_hash = bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt(rounds=12)).decode()
    op.execute(
        sa.text(
            "INSERT INTO bankers (id, name, email, password_hash, role, created_at) "
            "VALUES (:id, :name, :email, :password_hash, :role, now()) "
            "ON CONFLICT (email) DO NOTHING"
        ).bindparams(
            id=str(uuid.uuid4()),
            name="Demo Banker",
            email=DEMO_EMAIL,
            password_hash=password_hash,
            role="admin",
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM bankers WHERE email = :email").bindparams(email=DEMO_EMAIL)
    )
