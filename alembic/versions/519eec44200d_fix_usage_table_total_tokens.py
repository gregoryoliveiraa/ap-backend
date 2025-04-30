"""fix usage table total_tokens

Revision ID: 519eec44200d
Revises: 0d8aa91c90c0
Create Date: 2025-04-25 15:25:47.265050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '519eec44200d'
down_revision: Union[str, None] = '0d8aa91c90c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 