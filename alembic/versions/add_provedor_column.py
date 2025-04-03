"""add provedor column

Revision ID: add_provedor_column
Revises: add_uso_api_table_only
Create Date: 2024-04-01 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_provedor_column'
down_revision = 'add_uso_api_table_only'
branch_labels = None
depends_on = None

def upgrade():
    # Add provedor column to mensagens_chat table
    op.add_column('mensagens_chat', sa.Column('provedor', sa.String(length=50), nullable=True))

def downgrade():
    # Remove provedor column from mensagens_chat table
    op.drop_column('mensagens_chat', 'provedor') 