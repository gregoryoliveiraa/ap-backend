"""update user model

Revision ID: 60eebd9cbc04
Revises: 0c044d44ffa4
Create Date: 2025-04-25 10:44:51.084107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '60eebd9cbc04'
down_revision: Union[str, None] = '0c044d44ffa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First drop dependent tables
    op.execute('DROP TABLE IF EXISTS user_notifications CASCADE')
    op.execute('DROP TABLE IF EXISTS notifications CASCADE')
    op.execute('DROP TABLE IF EXISTS chat_messages CASCADE')
    op.execute('DROP TABLE IF EXISTS payments CASCADE')
    
    # Drop all foreign key constraints before changing column types
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_thesis_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS documents DROP CONSTRAINT IF EXISTS documents_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS chat_sessions DROP CONSTRAINT IF EXISTS chat_sessions_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS usage DROP CONSTRAINT IF EXISTS usage_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_templates DROP CONSTRAINT IF EXISTS document_templates_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS legal_theses DROP CONSTRAINT IF EXISTS legal_theses_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS templates DROP CONSTRAINT IF EXISTS templates_author_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_user_id_fkey')
    
    # Change column types in all tables
    op.execute('ALTER TABLE IF EXISTS users ALTER COLUMN id TYPE varchar USING id::varchar')
    op.execute('ALTER TABLE IF EXISTS documents ALTER COLUMN id TYPE varchar USING id::varchar')
    op.execute('ALTER TABLE IF EXISTS documents ALTER COLUMN user_id TYPE varchar USING user_id::varchar')
    op.execute('ALTER TABLE IF EXISTS generated_documents ALTER COLUMN id TYPE varchar USING id::varchar')
    op.execute('ALTER TABLE IF EXISTS generated_documents ALTER COLUMN user_id TYPE varchar USING user_id::varchar')
    op.execute('ALTER TABLE IF EXISTS legal_theses ALTER COLUMN id TYPE varchar USING id::varchar')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association ALTER COLUMN document_id TYPE varchar USING document_id::varchar')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association ALTER COLUMN thesis_id TYPE varchar USING thesis_id::varchar')
    op.execute('ALTER TABLE IF EXISTS chat_sessions ALTER COLUMN id TYPE varchar USING id::varchar')
    op.execute('ALTER TABLE IF EXISTS chat_sessions ALTER COLUMN user_id TYPE varchar USING user_id::varchar')
    op.execute('ALTER TABLE IF EXISTS usage ALTER COLUMN id TYPE varchar USING id::varchar')
    op.execute('ALTER TABLE IF EXISTS usage ALTER COLUMN user_id TYPE varchar USING user_id::varchar')
    op.execute('ALTER TABLE IF EXISTS document_templates ALTER COLUMN id TYPE varchar USING id::varchar')
    # Comentando a linha que causa erro pois a coluna author_id não existe
    # op.execute('ALTER TABLE IF EXISTS document_templates ALTER COLUMN author_id TYPE varchar USING author_id::varchar')
    # Comentando mais linhas que podem causar problemas
    # op.execute('ALTER TABLE IF EXISTS legal_theses ALTER COLUMN author_id TYPE varchar USING author_id::varchar')
    op.execute('ALTER TABLE IF EXISTS templates ALTER COLUMN id TYPE varchar USING id::varchar')
    # op.execute('ALTER TABLE IF EXISTS templates ALTER COLUMN author_id TYPE varchar USING author_id::varchar')
    
    # Continue with the rest of the changes
    op.execute('ALTER TABLE IF EXISTS chat_sessions ALTER COLUMN title TYPE varchar USING title::varchar')
    op.execute('ALTER TABLE IF EXISTS chat_sessions ALTER COLUMN created_at SET NOT NULL')
    op.execute('ALTER TABLE IF EXISTS chat_sessions ALTER COLUMN updated_at SET NOT NULL')
    op.execute('ALTER TABLE IF EXISTS chat_sessions DROP COLUMN IF EXISTS is_active')
    op.execute('ALTER TABLE IF EXISTS chat_sessions DROP COLUMN IF EXISTS metadata')
    
    # Add new columns to document_templates
    op.execute('ALTER TABLE IF EXISTS document_templates ADD COLUMN IF NOT EXISTS code varchar NOT NULL DEFAULT uuid_generate_v4()')
    op.execute('ALTER TABLE IF EXISTS document_templates ADD COLUMN IF NOT EXISTS steps jsonb NOT NULL DEFAULT \'{}\'::jsonb')
    op.execute('ALTER TABLE IF EXISTS document_templates ADD COLUMN IF NOT EXISTS base_template text')
    op.execute('ALTER TABLE IF EXISTS document_templates ADD COLUMN IF NOT EXISTS status varchar')
    op.execute('ALTER TABLE IF EXISTS document_templates ADD COLUMN IF NOT EXISTS is_featured boolean DEFAULT false')
    op.execute('ALTER TABLE IF EXISTS document_templates ADD COLUMN IF NOT EXISTS usage_count integer DEFAULT 0')
    
    # Modify existing columns in document_templates
    op.execute('ALTER TABLE IF EXISTS document_templates ALTER COLUMN title TYPE varchar USING title::varchar')
    op.execute('ALTER TABLE IF EXISTS document_templates ALTER COLUMN category TYPE varchar USING category::varchar')
    op.execute('ALTER TABLE IF EXISTS document_templates ALTER COLUMN created_at SET NOT NULL')
    op.execute('ALTER TABLE IF EXISTS document_templates ALTER COLUMN updated_at SET NOT NULL')
    
    # Drop columns from document_templates
    op.execute('ALTER TABLE IF EXISTS document_templates DROP COLUMN IF EXISTS description')
    op.execute('ALTER TABLE IF EXISTS document_templates DROP COLUMN IF EXISTS content')
    op.execute('ALTER TABLE IF EXISTS document_templates DROP COLUMN IF EXISTS is_active')
    op.execute('ALTER TABLE IF EXISTS document_templates DROP COLUMN IF EXISTS author_id')
    
    # Modify document_thesis_association
    op.execute('ALTER TABLE IF EXISTS document_thesis_association ALTER COLUMN created_at SET NOT NULL')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP COLUMN IF EXISTS id')
    
    # Modify documents table
    op.execute('ALTER TABLE IF EXISTS documents ADD COLUMN IF NOT EXISTS tokens_used integer DEFAULT 0')
    op.execute('ALTER TABLE IF EXISTS documents ALTER COLUMN title TYPE varchar USING title::varchar')
    op.execute('ALTER TABLE IF EXISTS documents ALTER COLUMN document_type TYPE varchar USING document_type::varchar')
    op.execute('ALTER TABLE IF EXISTS documents ALTER COLUMN created_at SET NOT NULL')
    op.execute('ALTER TABLE IF EXISTS documents ALTER COLUMN updated_at SET NOT NULL')
    op.execute('ALTER TABLE IF EXISTS documents DROP COLUMN IF EXISTS status')
    op.execute('ALTER TABLE IF EXISTS documents DROP COLUMN IF EXISTS metadata')
    
    # Modify generated_documents table
    op.execute('ALTER TABLE IF EXISTS generated_documents ADD COLUMN IF NOT EXISTS template_id varchar')
    op.execute('ALTER TABLE IF EXISTS generated_documents ADD COLUMN IF NOT EXISTS title varchar')
    op.execute('ALTER TABLE IF EXISTS generated_documents ADD COLUMN IF NOT EXISTS form_data jsonb DEFAULT \'{}\'::jsonb')
    op.execute('ALTER TABLE IF EXISTS generated_documents ADD COLUMN IF NOT EXISTS updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP')
    
    # Recreate foreign key constraints
    op.execute('ALTER TABLE IF EXISTS document_thesis_association ADD CONSTRAINT document_thesis_association_document_id_fkey FOREIGN KEY (document_id) REFERENCES generated_documents (id)')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association ADD CONSTRAINT document_thesis_association_thesis_id_fkey FOREIGN KEY (thesis_id) REFERENCES legal_theses (id)')
    op.execute('ALTER TABLE IF EXISTS documents ADD CONSTRAINT documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id)')
    op.execute('ALTER TABLE IF EXISTS generated_documents ADD CONSTRAINT generated_documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id)')
    op.execute('ALTER TABLE IF EXISTS chat_sessions ADD CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id)')
    op.execute('ALTER TABLE IF EXISTS usage ADD CONSTRAINT usage_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id)')
    
    # Comentando essas constraints que podem causar problemas
    # op.execute('ALTER TABLE IF EXISTS document_templates ADD CONSTRAINT document_templates_author_id_fkey FOREIGN KEY (author_id) REFERENCES users (id)')
    # op.execute('ALTER TABLE IF EXISTS legal_theses ADD CONSTRAINT legal_theses_author_id_fkey FOREIGN KEY (author_id) REFERENCES users (id)')
    # op.execute('ALTER TABLE IF EXISTS templates ADD CONSTRAINT templates_author_id_fkey FOREIGN KEY (author_id) REFERENCES users (id)')


def downgrade() -> None:
    # Drop all foreign key constraints first
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS document_thesis_association DROP CONSTRAINT IF EXISTS document_thesis_association_thesis_id_fkey')
    op.execute('ALTER TABLE IF EXISTS generated_documents DROP CONSTRAINT IF EXISTS generated_documents_document_id_fkey')
    op.execute('ALTER TABLE IF EXISTS documents DROP CONSTRAINT IF EXISTS documents_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS chat_sessions DROP CONSTRAINT IF EXISTS chat_sessions_user_id_fkey')
    op.execute('ALTER TABLE IF EXISTS usage DROP CONSTRAINT IF EXISTS usage_user_id_fkey')
    # Comentando as constraints que não existem
    # op.execute('ALTER TABLE IF EXISTS document_templates DROP CONSTRAINT IF EXISTS document_templates_author_id_fkey')
    # op.execute('ALTER TABLE IF EXISTS legal_theses DROP CONSTRAINT IF EXISTS legal_theses_author_id_fkey')
    # op.execute('ALTER TABLE IF EXISTS templates DROP CONSTRAINT IF EXISTS templates_author_id_fkey')
    
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
    # ### end Alembic commands ### 