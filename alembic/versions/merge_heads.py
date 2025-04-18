"""Merge multiple heads

Revision ID: merge_multiple_heads
Revises: 8a72c53f9e1a, create_payment_and_usage_tables, create_usuarios_table
Create Date: 2023-10-28 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_multiple_heads'
down_revision = None
branch_labels = None
depends_on = ('8a72c53f9e1a', 'create_payment_and_usage_tables', 'create_usuarios_table')


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 