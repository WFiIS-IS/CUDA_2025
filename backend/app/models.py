import uuid
from datetime import datetime, timezone
from enum import Enum, unique
from typing import Optional

from sqlalchemy import func
from sqlmodel import JSON, Column, DateTime, Field, Relationship, SQLModel


@unique
class JobStatus(str, Enum):
    """Enumeration of possible job statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobBase(SQLModel):
    """Base model for scrapping jobs."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(max_length=1024, index=True)
    status: JobStatus = Field(default=JobStatus.PENDING, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    completed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Job(JobBase, table=True):
    """Database model for scrapping jobs."""

    __tablename__ = "scrapper_job"

    results: dict | None = Field(default=None, sa_column=Column(JSON))
    error_message: str | None = Field(default=None, max_length=1024)


class TagLinkAssociation(SQLModel, table=True):
    tag_name: str = Field(foreign_key="tag.name", primary_key=True)
    link_id: uuid.UUID = Field(foreign_key="link_entry.id", primary_key=True)


class LinkEntryBase(SQLModel):
    url: str = Field(max_length=1024, index=True)
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)


class LinkEntry(LinkEntryBase, table=True):
    __tablename__ = "link_entry"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    collection_id: uuid.UUID = Field(foreign_key="collection.id", nullable=False)
    collection: "Collection" = Relationship(
        back_populates="links",
    )

    ai_suggestion: Optional["LinkAISuggestion"] = Relationship(
        back_populates="link",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    tags: list["Tag"] = Relationship(link_model=TagLinkAssociation)


class CollectionBase(SQLModel):
    name: str = Field(max_length=256, index=True)


class Collection(CollectionBase, table=True):
    __tablename__ = "collection"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    links: list[LinkEntry] = Relationship(
        back_populates="collection",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class LinkAISuggestion(SQLModel, table=True):
    __tablename__ = "link_ai_suggestion"  # type: ignore

    link_id: uuid.UUID = Field(foreign_key="link_entry.id", primary_key=True)
    link: LinkEntry = Relationship(back_populates="ai_suggestion")
    title: str = Field(max_length=256)
    description: str = Field(max_length=1024)


class Tag(SQLModel, table=True):
    __tablename__ = "tag"  # type: ignore

    name: str = Field(max_length=64, primary_key=True)
