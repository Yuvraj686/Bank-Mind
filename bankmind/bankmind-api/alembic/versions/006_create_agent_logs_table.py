"""006 create agent_logs table

Revision ID: 006
Revises: 005
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'agent_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('agent_name', sa.String(50), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('message_sent', sa.Text(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('stage_before', sa.String(50), nullable=True),
        sa.Column('stage_after', sa.String(50), nullable=True),
        sa.Column('was_overridden', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('override_note', sa.Text(), nullable=True),
        sa.Column('override_by', sa.String(255), nullable=True),
        sa.Column('override_at', sa.DateTime(), nullable=True),
        sa.Column('llm_raw_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_agent_logs_customer_id', 'agent_logs', ['customer_id'])
    op.create_index('ix_agent_logs_agent_name', 'agent_logs', ['agent_name'])
    op.create_index('ix_agent_logs_created_at', 'agent_logs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_agent_logs_created_at', table_name='agent_logs')
    op.drop_index('ix_agent_logs_agent_name', table_name='agent_logs')
    op.drop_index('ix_agent_logs_customer_id', table_name='agent_logs')
    op.drop_table('agent_logs')
