import uuid
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from sqlmodel import Field

from app.models import BookmarkBase, CollectionBase, JobBase


class JobCreate(BaseModel):
    url: str = Field(
        ..., max_length=1024, description="The URL to scrape for job information."
    )


class JobSummaryPublic(JobBase):
    """Public model for job information without sensitive data."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class JobPublic(JobBase):
    """Public model for job information with all details."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    error: str | None = None
    results: dict[str, Any] | None = None


class JobListPublic(BaseModel):
    """Public model for a list of jobs."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    jobs: list[JobPublic] = Field(default_factory=list)
    total_jobs: int = Field(default=0, ge=0)


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BookmarkBase):
    url: str | None = Field(default=None, max_length=1024)  # type: ignore
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)


class BookmarkPublic(BookmarkBase):
    id: uuid.UUID


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(CollectionBase):
    name: str | None = Field(default=None, max_length=256)  # type: ignore


class CollectionPublic(CollectionBase):
    id: uuid.UUID


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

    sentiment: dict[str, Any]
    summary: list[dict[str, Any]]
    topics: dict[str, Any]
    meta: dict[str, Any]
    tags: list[str]

    @field_serializer("sentiment", "summary", "topics", "meta", "tags")
    def serialize_fields(self, value: Any) -> Any:
        """Custom serializer to handle numpy types."""
        return convert_numpy_types(value)
