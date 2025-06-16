"""switch_to_sqlalchemy_models

Revision ID: 20f1ef876c36
Revises: 95518561bc41
Create Date: 2025-06-16 18:31:58.926430

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20f1ef876c36'
down_revision: Union[str, None] = '95518561bc41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.create_table('tag_bookmark_association',
    sa.Column('tag_name', sa.String(length=64), nullable=False),
    sa.Column('bookmark_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['bookmark_id'], ['bookmark.id'], ),
    sa.ForeignKeyConstraint(['tag_name'], ['tag.name'], ),
    sa.PrimaryKeyConstraint('tag_name', 'bookmark_id')
    )
    op.drop_table('tagbookmarkassociation')
    op.create_index(op.f('ix_bookmark_title'), 'bookmark', ['title'], unique=False)
    op.alter_column('bookmark_ai_suggestion', 'tags',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=False)
    op.add_column('content_embedding', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False))
    op.alter_column('content_embedding', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=384),
               nullable=False)
    op.alter_column('content_embedding', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.add_column('job', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False))
    op.alter_column('job', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.drop_index('ix_job_status', table_name='job')
    op.drop_index('ix_job_type', table_name='job')
    op.create_index(op.f('ix_job_bookmark_id'), 'job', ['bookmark_id'], unique=False)
    op.drop_column('job', 'error_message')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
    op.add_column('job', sa.Column('error_message', sa.VARCHAR(length=1024), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_job_bookmark_id'), table_name='job')
    op.create_index('ix_job_type', 'job', ['type'], unique=False)
    op.create_index('ix_job_status', 'job', ['status'], unique=False)
    op.alter_column('job', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    op.drop_column('job', 'updated_at')
    op.alter_column('content_embedding', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('content_embedding', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=384),
               nullable=True)
    op.drop_column('content_embedding', 'updated_at')
    op.alter_column('bookmark_ai_suggestion', 'tags',
               existing_type=postgresql.ARRAY(sa.VARCHAR()),
               nullable=True)
    op.drop_index(op.f('ix_bookmark_title'), table_name='bookmark')
    op.create_table('tagbookmarkassociation',
    sa.Column('tag_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('bookmark_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['bookmark_id'], ['bookmark.id'], name='tagbookmarkassociation_bookmark_id_fkey'),
    sa.ForeignKeyConstraint(['tag_name'], ['tag.name'], name='tagbookmarkassociation_tag_name_fkey'),
    sa.PrimaryKeyConstraint('tag_name', 'bookmark_id', name='tagbookmarkassociation_pkey')
    )
    op.drop_table('tag_bookmark_association')
