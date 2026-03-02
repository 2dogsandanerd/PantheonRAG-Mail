"""add_multi_tenancy_tables

Revision ID: 2154bffc74db
Revises: f19f5eb501f4
Create Date: 2025-11-20 20:08:27.050206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2154bffc74db'
down_revision: Union[str, Sequence[str], None] = 'f19f5eb501f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create new tables
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('subscription_tier', sa.Enum('FREE', 'PRO', 'ENTERPRISE', name='subscriptiontier'), nullable=True),
        sa.Column('subscription_status', sa.Enum('ACTIVE', 'SUSPENDED', 'CANCELLED', name='subscriptionstatus'), nullable=True),
        sa.Column('max_collections', sa.Integer(), nullable=True),
        sa.Column('max_queries_per_day', sa.Integer(), nullable=True),
        sa.Column('max_api_keys', sa.Integer(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)
    op.create_index(op.f('ix_tenants_name'), 'tenants', ['name'], unique=True)

    op.create_table('collection_acl',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('collection_name', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('allowed_roles', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('collection_name', 'tenant_id', name='uix_collection_tenant')
    )
    op.create_index(op.f('ix_collection_acl_id'), 'collection_acl', ['id'], unique=False)

    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('key_prefix', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('scopes', sa.JSON(), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)

    op.create_table('tenant_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('query_count', sa.Integer(), nullable=True),
        sa.Column('document_count', sa.Integer(), nullable=True),
        sa.Column('token_usage', sa.BigInteger(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'date', name='uix_tenant_date')
    )
    op.create_index(op.f('ix_tenant_usage_id'), 'tenant_usage', ['id'], unique=False)

    op.create_table('query_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_query_feedbacks_conversation_id'), 'query_feedbacks', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_query_feedbacks_id'), 'query_feedbacks', ['id'], unique=False)
    op.create_index(op.f('ix_query_feedbacks_user_id'), 'query_feedbacks', ['user_id'], unique=False)

    # 2. Modify users table using batch operations (SQLite compatible)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('role', sa.Enum('ADMIN', 'USER', 'READONLY', name='userrole'), nullable=True))
        batch_op.create_foreign_key('fk_users_tenant_id', 'tenants', ['tenant_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_tenant_id', type_='foreignkey')
        batch_op.drop_column('role')
        batch_op.drop_column('tenant_id')

    op.drop_index(op.f('ix_query_feedbacks_user_id'), table_name='query_feedbacks')
    op.drop_index(op.f('ix_query_feedbacks_id'), table_name='query_feedbacks')
    op.drop_index(op.f('ix_query_feedbacks_conversation_id'), table_name='query_feedbacks')
    op.drop_table('query_feedbacks')
    
    op.drop_index(op.f('ix_tenant_usage_id'), table_name='tenant_usage')
    op.drop_table('tenant_usage')
    
    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_table('api_keys')
    
    op.drop_index(op.f('ix_collection_acl_id'), table_name='collection_acl')
    op.drop_table('collection_acl')
    
    op.drop_index(op.f('ix_tenants_name'), table_name='tenants')
    op.drop_index(op.f('ix_tenants_id'), table_name='tenants')
    op.drop_table('tenants')
