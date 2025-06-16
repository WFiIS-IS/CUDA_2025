import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedUpdatedAtMixin, IdMixin
from app.models.core import Bookmark


class BookmarkAISuggestion(Base):
    """Bookmark AI Suggestion model for storing AI-generated suggestions."""

    __tablename__ = "bookmark_ai_suggestion"

    bookmark_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookmark.id"), primary_key=True
    )
    bookmark: Mapped[Bookmark] = relationship(
        back_populates="ai_suggestions", uselist=False, init=False
    )

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("collection.id"), nullable=True, default=None
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(64)), default=list, init=False, server_default=text("{}")
    )


class ContentEmbedding(Base, IdMixin, CreatedUpdatedAtMixin):
    """Database model for storing content embeddings for semantic search."""

    __tablename__ = "content_embedding"

    url: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content_preview: Mapped[str] = mapped_column(String(500))
    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False,
    )
