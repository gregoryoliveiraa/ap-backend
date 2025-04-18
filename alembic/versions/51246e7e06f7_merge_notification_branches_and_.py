"""Merge notification branches and previous heads

Revision ID: 51246e7e06f7
Revises: 8a72c53f9e1a, create_payment_and_usage_tables, create_usuarios_table, merge_multiple_heads
Create Date: 2025-04-14 18:41:31.051438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51246e7e06f7'
down_revision: Union[str, None] = ('8a72c53f9e1a', 'create_payment_and_usage_tables', 'create_usuarios_table', 'merge_multiple_heads')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 