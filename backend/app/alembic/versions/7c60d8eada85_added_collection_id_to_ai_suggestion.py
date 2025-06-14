"""added_collection_id_to_ai_suggestion

Revision ID: 7c60d8eada85
Revises: a3af78866c8e
Create Date: 2025-06-15 18:09:06.814391

"""
from typing import Sequence, Union
import sqlmodel.sql.sqltypes

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c60d8eada85'
down_revision: Union[str, None] = 'a3af78866c8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookmark_ai_suggestion', sa.Column('collection_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'bookmark_ai_suggestion', 'collection', ['collection_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bookmark_ai_suggestion', type_='foreignkey')
    op.drop_column('bookmark_ai_suggestion', 'collection_id')
    # ### end Alembic commands ###
