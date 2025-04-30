"""update id columns to string

Revision ID: 6eebfd777f69
Revises: 0c044d44ffa4
Create Date: 2024-04-25 12:34:56.789012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6eebfd777f69'
down_revision: Union[str, None] = '0c044d44ffa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop all foreign key constraints first
    op.execute('ALTER TABLE IF EXISTS user_notifications DROP CONSTRAINT IF EXISTS user_notifications_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS user_notifications DROP CONSTRAINT IF EXISTS user_notifications_notification_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_thesis_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS documents DROP CONSTRAINT IF EXISTS documents_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS chat_sessions DROP CONSTRAINT IF EXISTS chat_sessions_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS usage DROP CONSTRAINT IF EXISTS usage_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_templates DROP CONSTRAINT IF EXISTS document_templates_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS legal_theses DROP CONSTRAINT IF EXISTS legal_theses_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS templates DROP CONSTRAINT IF EXISTS templates_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS jurisprudencia_buscas DROP CONSTRAINT IF EXISTS jurisprudencia_buscas_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS jurisprudencia_buscas DROP CONSTRAINT IF EXISTS jurisprudencia_buscas_usuario_id_fkey')
    op.execute('ALTER TABLE IF EXISTS payments DROP CONSTRAINT IF EXISTS payments_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS chat_messages DROP CONSTRAINT IF EXISTS chat_messages_session_id_fkey')
    
    # Drop all tables in the correct order
    op.execute('DROP TABLE IF EXISTS user_notifications CASCADE')
    op.execute('DROP TABLE IF EXISTS notifications CASCADE')
    op.execute('DROP TABLE IF EXISTS chat_messages CASCADE')
    op.execute('DROP TABLE IF EXISTS chat_sessions CASCADE')
    op.execute('DROP TABLE IF EXISTS payments CASCADE')
    op.execute('DROP TABLE IF EXISTS usage CASCADE')
    op.execute('DROP TABLE IF EXISTS document_thesis_association CASCADE')
    op.execute('DROP TABLE IF EXISTS generated_documents CASCADE')
    op.execute('DROP TABLE IF EXISTS documents CASCADE')
    op.execute('DROP TABLE IF EXISTS document_templates CASCADE')
    op.execute('DROP TABLE IF EXISTS legal_theses CASCADE')
    op.execute('DROP TABLE IF EXISTS templates CASCADE')
    op.execute('DROP TABLE IF EXISTS jurisprudencia_resultados CASCADE')
    op.execute('DROP TABLE IF EXISTS jurisprudencia_buscas CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    
    # Recreate tables with string IDs
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('oab_number', sa.String(), nullable=True),
        sa.Column('estado_oab', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('plan', sa.String(), nullable=True),
        sa.Column('token_credits', sa.Integer(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('available_credits', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    op.create_table('documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('document_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('base_template', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint(None, 'document_templates', ['code'])
    
    op.create_table('generated_documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('template_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('form_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['document_templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('legal_theses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('law_area', sa.String(), nullable=False),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('legal_grounds', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('variables', sa.Text(), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('usage',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('available_tokens', sa.Integer(), nullable=True),
        sa.Column('total_documents', sa.Integer(), nullable=True),
        sa.Column('chat_history', sa.JSON(), nullable=True),
        sa.Column('document_history', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('jurisprudencia_buscas',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('usuario_id', sa.String(), nullable=True),
        sa.Column('termos_busca', sa.Text(), nullable=False),
        sa.Column('filtros', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('resultados_encontrados', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jurisprudencia_buscas_id'), 'jurisprudencia_buscas', ['id'], unique=False)
    
    op.create_table('jurisprudencia_resultados',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('busca_id', sa.String(), nullable=True),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('tribunal', sa.String(length=50), nullable=False),
        sa.Column('numero_processo', sa.String(length=100), nullable=True),
        sa.Column('data_julgamento', sa.DateTime(), nullable=True),
        sa.Column('relator', sa.String(length=100), nullable=True),
        sa.Column('ementa', sa.Text(), nullable=False),
        sa.Column('inteiro_teor', sa.Text(), nullable=True),
        sa.Column('url_original', sa.String(length=255), nullable=True),
        sa.Column('relevancia', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['busca_id'], ['jurisprudencia_buscas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jurisprudencia_resultados_id'), 'jurisprudencia_resultados', ['id'], unique=False)
    
    op.create_table('document_thesis_association',
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('thesis_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['generated_documents.id'], ),
        sa.ForeignKeyConstraint(['thesis_id'], ['legal_theses.id'], ),
        sa.PrimaryKeyConstraint('document_id', 'thesis_id')
    )
    
    op.create_table('chat_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('chat_messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('payment_details', sa.JSON(), nullable=True),
        sa.Column('plan_id', sa.String(), nullable=True),
        sa.Column('tokens_added', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('user_notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('notification_id', sa.String(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop all foreign key constraints first
    op.execute('ALTER TABLE IF EXISTS user_notifications DROP CONSTRAINT IF EXISTS user_notifications_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS user_notifications DROP CONSTRAINT IF EXISTS user_notifications_notification_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_thesis_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS documents DROP CONSTRAINT IF EXISTS documents_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS chat_sessions DROP CONSTRAINT IF EXISTS chat_sessions_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS usage DROP CONSTRAINT IF EXISTS usage_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_templates DROP CONSTRAINT IF EXISTS document_templates_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS legal_theses DROP CONSTRAINT IF EXISTS legal_theses_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS templates DROP CONSTRAINT IF EXISTS templates_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS jurisprudencia_buscas DROP CONSTRAINT IF EXISTS jurisprudencia_buscas_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS jurisprudencia_buscas DROP CONSTRAINT IF EXISTS jurisprudencia_buscas_usuario_id_fkey')
    op.execute('ALTER TABLE IF EXISTS payments DROP CONSTRAINT IF EXISTS payments_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS chat_messages DROP CONSTRAINT IF EXISTS chat_messages_session_id_fkey')
    
    # Drop all tables in the correct order
    op.execute('DROP TABLE IF EXISTS user_notifications CASCADE')
    op.execute('DROP TABLE IF EXISTS notifications CASCADE')
    op.execute('DROP TABLE IF EXISTS chat_messages CASCADE')
    op.execute('DROP TABLE IF EXISTS chat_sessions CASCADE')
    op.execute('DROP TABLE IF EXISTS payments CASCADE')
    op.execute('DROP TABLE IF EXISTS usage CASCADE')
    op.execute('DROP TABLE IF EXISTS document_thesis_association CASCADE')
    op.execute('DROP TABLE IF EXISTS generated_documents CASCADE')
    op.execute('DROP TABLE IF EXISTS documents CASCADE')
    op.execute('DROP TABLE IF EXISTS document_templates CASCADE')
    op.execute('DROP TABLE IF EXISTS legal_theses CASCADE')
    op.execute('DROP TABLE IF EXISTS templates CASCADE')
    op.execute('DROP TABLE IF EXISTS jurisprudencia_resultados CASCADE')
    op.execute('DROP TABLE IF EXISTS jurisprudencia_buscas CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE') 