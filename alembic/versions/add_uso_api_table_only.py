"""add uso_api table only

Revision ID: add_uso_api_table_only
Revises: add_uso_api_table
Create Date: 2024-04-01 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_uso_api_table_only'
down_revision = 'add_uso_api_table'
branch_labels = None
depends_on = None

def upgrade():
    # Create uso_api table
    op.create_table(
        'uso_api',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('tipo_operacao', sa.String(length=100), nullable=False),
        sa.Column('tokens_entrada', sa.Integer(), nullable=False),
        sa.Column('tokens_saida', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=False),
        sa.Column('recurso_acessado', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uso_api_id'), 'uso_api', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_uso_api_id'), table_name='uso_api')
    op.drop_table('uso_api') 