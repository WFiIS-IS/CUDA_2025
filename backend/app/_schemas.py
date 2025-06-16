import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel

from app.models import JobBase


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


class SearchPublic(BaseModel):
    """Public model for search results."""

    results: list[str]

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
