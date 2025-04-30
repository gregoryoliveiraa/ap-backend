"""merge_id_column_migrations

Revision ID: 0d8aa91c90c0
Revises: 60eebd9cbc04, 6eebfd777f69
Create Date: 2025-04-25 11:37:19.190313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d8aa91c90c0'
down_revision: Union[str, None] = ('60eebd9cbc04', '6eebfd777f69')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 