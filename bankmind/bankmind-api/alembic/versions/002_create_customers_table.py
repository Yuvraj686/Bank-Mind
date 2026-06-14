"""002 create customers table

Revision ID: 002
Revises: 001
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'customers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('occupation', sa.String(255), nullable=False),
        sa.Column('income_monthly', sa.Float(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('website_visits', sa.Integer(), server_default='0', nullable=False),
        sa.Column('pages_viewed', sa.String(500), nullable=True),
        sa.Column('stage', sa.String(50), server_default='lead', nullable=False),
        sa.Column('lead_score', sa.Float(), nullable=True),
        sa.Column('kyc_status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('kyc_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('account_number', sa.String(50), nullable=True),
        sa.Column('features_adopted', JSONB(), server_default='{}', nullable=True),
        sa.Column('last_life_event_detected', sa.String(255), nullable=True),
        sa.Column('last_life_event_at', sa.DateTime(), nullable=True),
        sa.Column('currently_processing', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_customers_stage', 'customers', ['stage'])


def downgrade() -> None:
    op.drop_index('ix_customers_stage', table_name='customers')
    op.drop_table('customers')
