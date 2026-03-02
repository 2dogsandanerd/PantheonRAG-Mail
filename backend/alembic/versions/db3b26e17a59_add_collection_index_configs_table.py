"""Add collection_index_configs table

Revision ID: db3b26e17a59
Revises: 
Create Date: 2025-11-04 10:32:55.586708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db3b26e17a59'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.dialects import sqlite
    # Create table
    op.create_table(
        'collection_index_configs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('collection_name', sa.String(255), unique=True, nullable=False),
        sa.Column('index_strategy', sa.String(50), nullable=False),
        sa.Column('data_type', sa.String(50), nullable=False),
        sa.Column('embedding_model', sa.String(255)),
        sa.Column('embedding_provider', sa.String(50)),
        sa.Column('embedding_dimensions', sa.Integer()),
        sa.Column('chunk_size', sa.Integer(), default=500),
        sa.Column('chunk_overlap', sa.Integer(), default=50),
        sa.Column('source_file_path', sa.String(512)),
        sa.Column('connection_string', sa.Text()),
        sa.Column('table_schema', sqlite.JSON()),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('enabled_for_drafts', sa.Boolean(), default=True),
        sa.Column('weight', sa.Float(), default=1.0),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('last_used', sa.DateTime(timezone=True)),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('avg_relevance', sa.Float(), default=0.0)
    )

    # Create indexes
    op.create_index('idx_collection_name', 'collection_index_configs', ['collection_name'])
    op.create_index('idx_enabled_for_drafts', 'collection_index_configs', ['enabled_for_drafts'])


def downgrade() -> None:
    from sqlalchemy.dialects import sqlite
    op.drop_index('idx_enabled_for_drafts')
    op.drop_index('idx_collection_name')
    op.drop_table('collection_index_configs')
