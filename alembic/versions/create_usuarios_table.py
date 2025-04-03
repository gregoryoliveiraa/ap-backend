"""create usuarios table

Revision ID: create_usuarios_table
Revises: add_provedor_column
Create Date: 2024-04-01 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_usuarios_table'
down_revision = 'add_provedor_column'
branch_labels = None
depends_on = None

def upgrade():
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('nome_completo', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=512), nullable=False),
        sa.Column('numero_oab', sa.String(length=50), nullable=True),
        sa.Column('estado_oab', sa.String(length=2), nullable=True),
        sa.Column('verificado', sa.Boolean(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=True),
        sa.Column('ultima_atualizacao', sa.DateTime(), nullable=True),
        sa.Column('creditos_disponiveis', sa.Integer(), nullable=True),
        sa.Column('plano', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios') 