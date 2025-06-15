import uuid
from datetime import datetime, timezone
from enum import Enum, unique
from typing import Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import func
from sqlmodel import JSON, Column, DateTime, Field, Relationship, SQLModel


@unique
class JobStatus(str, Enum):
    """Enumeration of possible job statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@unique
class JobType(str, Enum):
    """Enumeration of possible job types."""

    SCRAPE = "scrape"
    EMBED = "embed"
    ANALYZE = "analyze"


class JobBase(SQLModel):
    """Base model for scrapping jobs."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    bookmark_id: uuid.UUID = Field(foreign_key="bookmark.id", nullable=False)
    status: JobStatus = Field(default=JobStatus.PENDING, index=True)
    type: JobType = Field(default=JobType.SCRAPE, index=True)
    results: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    completed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Job(JobBase, table=True):
    """Database model for scrapping jobs."""

    __tablename__ = "job"
    bookmark: "Bookmark" = Relationship(back_populates="jobs")
    error_message: str | None = Field(default=None, max_length=1024)


class TagBookmarkAssociation(SQLModel, table=True):
    tag_name: str = Field(foreign_key="tag.name", primary_key=True)
    bookmark_id: uuid.UUID = Field(foreign_key="bookmark.id", primary_key=True)


class BookmarkBase(SQLModel):
    url: str = Field(max_length=1024, index=True)
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)


class Bookmark(BookmarkBase, table=True):
    __tablename__ = "bookmark"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    jobs: list[Job] = Relationship(
        back_populates="bookmark",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    collection_id: uuid.UUID | None = Field(foreign_key="collection.id", nullable=True)
    collection: "Collection" = Relationship(
        back_populates="bookmarks",
    )

    ai_suggestion: Optional["BookmarkAISuggestion"] = Relationship(
        back_populates="bookmark",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    tags: list["Tag"] = Relationship(link_model=TagBookmarkAssociation)


class CollectionBase(SQLModel):
    name: str = Field(max_length=256, index=True)


class Collection(CollectionBase, table=True):
    __tablename__ = "collection"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    bookmarks: list[Bookmark] = Relationship(
        back_populates="collection",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class BookmarkAISuggestion(SQLModel, table=True):
    __tablename__ = "bookmark_ai_suggestion"  # type: ignore

    bookmark_id: uuid.UUID = Field(foreign_key="bookmark.id", primary_key=True)
    bookmark: Bookmark = Relationship(back_populates="ai_suggestion")
    title: str = Field(max_length=256)
    description: str = Field(max_length=1024)
    collection_id: uuid.UUID | None = Field(foreign_key="collection.id", nullable=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tag"  # type: ignore

    name: str = Field(max_length=64, primary_key=True)


class ContentEmbedding(SQLModel, table=True):
    """Database model for storing content embeddings for semantic search."""

    __tablename__ = "content_embedding"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(max_length=1024, index=True)
    content_hash: str = Field(max_length=64, index=True)  # SHA-256 hash of content
    content_preview: str = Field(max_length=500)  # First 500 chars for preview
    embedding: list[float] = Field(
        sa_column=Column(Vector(384))
    )  # 384-dim embeddings from sentence-transformers
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
