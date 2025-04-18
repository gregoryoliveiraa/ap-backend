"""Add role column and notification tables

Revision ID: 8a72c53f9e1a
Revises: add_uso_api_table
Create Date: 2023-10-27 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8a72c53f9e1a'
down_revision = 'add_uso_api_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column to users table if it doesn't exist already
    op.execute("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='role')")
    result = op.get_bind().fetchone()
    
    if not result[0]:
        op.add_column('users', sa.Column('role', sa.String(20), nullable=True))
        op.execute("UPDATE users SET role = 'user'")
        op.alter_column('users', 'role', nullable=False, server_default='user')

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('target_users', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('target_role', sa.String(20), nullable=True),
        sa.Column('target_all', sa.Boolean(), default=False),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('action_link', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_notifications table
    op.create_table(
        'user_notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('notification_id', sa.String(), nullable=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('delivered', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id and notification_id
    op.create_index('ix_user_notifications_user_id', 'user_notifications', ['user_id'], unique=False)
    op.create_index('ix_user_notifications_notification_id', 'user_notifications', ['notification_id'], unique=False)
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop user_notifications table
    op.drop_table('user_notifications')
    
    # Drop notifications table
    op.drop_table('notifications')
    
    # Check if role column exists and drop it
    op.execute("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='role')")
    result = op.get_bind().fetchone()
    
    if result[0]:
        op.drop_column('users', 'role') 