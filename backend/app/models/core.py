import uuid
from datetime import datetime
from enum import StrEnum, unique

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, JSON, DateTime, Enum, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedUpdatedAtMixin, IdMixin


class Collection(Base, IdMixin):
    """Collection model for grouping bookmarks."""

    __tablename__ = "collection"

    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="collection",
        init=False,
    )


class Bookmark(Base, IdMixin):
    """Bookmark model for storing URLs"""

    __tablename__ = "bookmark"

    url: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(
        String(256), nullable=True, index=True, default=None
    )
    description: Mapped[str | None] = mapped_column(
        String(1024), nullable=True, default=None
    )

    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("collection.id"), nullable=True, default=None
    )
    collection: Mapped[Collection | None] = relationship(
        back_populates="bookmarks", uselist=False, init=False
    )

    ai_suggestion: Mapped["BookmarkAISuggestion | None"] = relationship(
        back_populates="bookmark",
        uselist=False,
        init=False,
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary="tag_bookmark_association",
        back_populates="bookmarks",
        init=False,
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="bookmark",
        init=False,
    )


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


class Tag(Base):
    """Tag model"""

    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)

    bookmarks: Mapped[list[Bookmark]] = relationship(
        secondary="tag_bookmark_association",
        back_populates="tags",
        init=False,
    )


class TagBookmarkAssociation(Base):
    """Association model for many-to-many relationship between tags and bookmarks."""

    __tablename__ = "tag_bookmark_association"

    tag_name: Mapped[str] = mapped_column(ForeignKey("tag.name"), primary_key=True)
    bookmark_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookmark.id"), primary_key=True
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


@unique
class JobStatus(StrEnum):
    """Enumeration of possible job statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@unique
class JobType(StrEnum):
    """Enumeration of possible job types."""

    SCRAPE = "scrape"
    EMBED = "embed"
    ANALYZE = "analyze"


class Job(Base, IdMixin, CreatedUpdatedAtMixin):
    """Database model for background jobs"""

    __tablename__ = "job"

    bookmark_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookmark.id"), nullable=False, index=True
    )
    bookmark: Mapped[Bookmark] = relationship(
        back_populates="jobs", init=False, uselist=False
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        server_default=text(f"'{JobStatus.PENDING.value}'"),
    )
    type: Mapped[JobType] = mapped_column(
        Enum(JobType),
        nullable=False,
        server_default=text(f"'{JobType.SCRAPE.value}'"),
        default=JobType.SCRAPE,
    )
    results: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default=None,
        nullable=True,
    )
