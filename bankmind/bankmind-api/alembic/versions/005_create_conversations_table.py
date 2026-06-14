"""005 create conversations table

Revision ID: 005
Revises: 004
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('sender', sa.String(20), nullable=False),
        sa.Column('agent_name', sa.String(50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('channel', sa.String(50), server_default='whatsapp', nullable=False),
        sa.Column('is_simulated', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_conversations_customer_id', 'conversations', ['customer_id'])
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_index('ix_conversations_customer_id', table_name='conversations')
    op.drop_table('conversations')
