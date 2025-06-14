import uuid
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel

from app.models import BookmarkBase, CollectionBase, JobBase


class JobCreate(BaseModel):
    url: str = Field(
        ..., max_length=1024, description="The URL to scrape for job information."
    )

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class JobSummaryPublic(JobBase):
    """Public model for job information without sensitive data."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class JobPublic(JobBase):
    """Public model for job information with all details."""

    error: str | None = None
    results: dict[str, Any] | None = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class JobListPublic(BaseModel):
    """Public model for a list of jobs."""

    jobs: list[JobPublic] = Field(default_factory=list)
    total_jobs: int = Field(default=0, ge=0)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class BookmarkCreate(BookmarkBase):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    collection_id: uuid.UUID | None = Field(default=None)


class BookmarkUpdate(BookmarkBase):
    url: str | None = Field(default=None, max_length=1024)  # type: ignore
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)
    collection_id: uuid.UUID | None = Field(default=None)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class BookmarkPublic(BookmarkBase):
    id: uuid.UUID
    collection_id: uuid.UUID | None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CollectionCreate(CollectionBase):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CollectionUpdate(CollectionBase):
    name: str | None = Field(default=None, max_length=256)  # type: ignore

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CollectionPublic(CollectionBase):
    id: uuid.UUID
    bookmarks_count: int = Field(ge=0)

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


def convert_numpy_types(obj: Any) -> Any:
    """Recursively convert numpy types to native Python types for JSON serialization.

    Args:
        obj: Object that may contain numpy types

    Returns:
        Object with numpy types converted to native Python types
    """
    if isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj


class AnalysisResults(BaseModel):
    """Pydantic model for analysis results with automatic type conversion."""

    summary: str
    collection: str
    title: str
    tags: list[str]

    @field_serializer("summary", "collection", "title", "tags")
    def serialize_fields(self, value: Any) -> Any:
        """Custom serializer to handle numpy types."""
        return convert_numpy_types(value)


class TagCreate(BaseModel):
    tag: str = Field(
        ...,
        description="The tag to add to the bookmark.",
        pattern=r"^[a-z0-9\-_]+$",
        min_length=1,
        max_length=64,
    )


class TagPublic(BaseModel):
    tag_name: str
    usage_count: int

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SearchPublic(BaseModel):
    """Public model for search results."""

    results: list[str]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
