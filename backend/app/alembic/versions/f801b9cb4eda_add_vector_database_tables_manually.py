"""add vector database tables manually

Revision ID: f801b9cb4eda
Revises: 3d1b3bfa60b6
Create Date: 2025-06-02 01:59:54.298720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'f801b9cb4eda'
down_revision: Union[str, None] = '3d1b3bfa60b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable the vector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create enum types if they don't exist
    op.execute("DO $$ BEGIN CREATE TYPE jobtype AS ENUM ('SCRAPPING', 'EMBEDDING'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Rename old table to new table
    op.execute('ALTER TABLE scrapper_job RENAME TO job')
    
    # Add type column to job table
    op.add_column('job', sa.Column('type', sa.Enum('SCRAPPING', 'EMBEDDING', name='jobtype'), nullable=True))
    
    # Set default type for existing jobs
    op.execute("UPDATE job SET type = 'SCRAPPING' WHERE type IS NULL")
    
    # Make type column not null
    op.alter_column('job', 'type', nullable=False)
    
    # Remove results column
    op.drop_column('job', 'results')
    
    # Create analysis_result table
    op.create_table('analysis_result',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('analysis_type', sa.String(length=64), nullable=False),
        sa.Column('summary', sa.String(length=2048), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('categories', sa.JSON(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analysis_result_analysis_type', 'analysis_result', ['analysis_type'])
    op.create_index('ix_analysis_result_url', 'analysis_result', ['url'])
    
    # Create embedding_result table
    op.create_table('embedding_result',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=False),
        sa.Column('text_chunks', sa.JSON(), nullable=True),
        sa.Column('chunk_metadata', sa.JSON(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embedding_result_url', 'embedding_result', ['url'])
    
    # Update indexes for job table
    op.create_index('ix_job_type', 'job', ['type'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new tables
    op.drop_table('embedding_result')
    op.drop_table('analysis_result')
    
    # Drop type index
    op.drop_index('ix_job_type')
    
    # Add back results column
    op.add_column('job', sa.Column('results', sa.JSON(), nullable=True))
    
    # Drop type column
    op.drop_column('job', 'type')
    
    # Rename table back
    op.execute('ALTER TABLE job RENAME TO scrapper_job')
    
    # Drop types
    op.execute('DROP TYPE IF EXISTS jobtype')
    
    # Drop vector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
