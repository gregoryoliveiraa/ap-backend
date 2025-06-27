"""add_cpf_cnpj_field_only

Revision ID: ea79298dd495
Revises: 638e0eb9ccb1
Create Date: 2025-06-26 23:35:10.677476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea79298dd495'
down_revision: Union[str, None] = '638e0eb9ccb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 