"""Add user_notifications table

Revision ID: 6410d7d03de7
Revises: 193e7a475f77
Create Date: 2025-04-14 19:09:52.109136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '6410d7d03de7'
down_revision: Union[str, None] = '193e7a475f77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_notifications_notification_id', table_name='user_notifications')
    op.drop_index('ix_user_notifications_user_id', table_name='user_notifications')
    op.drop_table('user_notifications')
    op.drop_table('payments')
    op.drop_table('chat_messages')
    op.drop_index('ix_notifications_target_role', table_name='notifications')
    op.drop_index('ix_notifications_title', table_name='notifications')
    op.drop_table('notifications')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notifications',
    sa.Column('id', sa.NUMERIC(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), nullable=False),
    sa.Column('message', sa.TEXT(), nullable=False),
    sa.Column('type', sa.VARCHAR(length=50), nullable=False),
    sa.Column('target_all', sa.BOOLEAN(), nullable=True),
    sa.Column('target_role', sa.VARCHAR(length=50), nullable=True),
    sa.Column('target_users', sqlite.JSON(), nullable=True),
    sa.Column('expiry_date', sa.DATETIME(), nullable=True),
    sa.Column('action_link', sa.VARCHAR(length=500), nullable=True),
    sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_title', 'notifications', ['title'], unique=False)
    op.create_index('ix_notifications_target_role', 'notifications', ['target_role'], unique=False)
    op.create_table('chat_messages',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('session_id', sa.VARCHAR(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('role', sa.VARCHAR(), nullable=False),
    sa.Column('tokens_used', sa.INTEGER(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('provider', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('user_id', sa.VARCHAR(), nullable=False),
    sa.Column('amount', sa.FLOAT(), nullable=False),
    sa.Column('payment_method', sa.VARCHAR(), nullable=False),
    sa.Column('status', sa.VARCHAR(), nullable=False),
    sa.Column('card_last_digits', sa.VARCHAR(), nullable=True),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('updated_at', sa.DATETIME(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_notifications',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('user_id', sa.VARCHAR(), nullable=False),
    sa.Column('notification_id', sa.NUMERIC(), nullable=False),
    sa.Column('read', sa.BOOLEAN(), nullable=True),
    sa.Column('delivered', sa.BOOLEAN(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_notifications_user_id', 'user_notifications', ['user_id'], unique=False)
    op.create_index('ix_user_notifications_notification_id', 'user_notifications', ['notification_id'], unique=False)
    # ### end Alembic commands ### 