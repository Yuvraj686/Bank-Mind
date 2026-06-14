"""003 create product_eligibility table

Revision ID: 003
Revises: 002
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'product_eligibility',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(100), nullable=False),
        sa.Column('eligible', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('activated', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('eligibility_reason', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_product_eligibility_customer_id', 'product_eligibility', ['customer_id'])


def downgrade() -> None:
    op.drop_index('ix_product_eligibility_customer_id', table_name='product_eligibility')
    op.drop_table('product_eligibility')
