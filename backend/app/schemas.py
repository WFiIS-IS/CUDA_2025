import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import Field

from app.models import CollectionBase, JobBase, LinkEntryBase


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


class LinkEntryCreate(LinkEntryBase):
    pass


class LinkEntryUpdate(LinkEntryBase):
    url: str | None = Field(default=None, max_length=1024)  # type: ignore
    title: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=1024)


class LinkEntryPublic(LinkEntryBase):
    id: uuid.UUID


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(CollectionBase):
    name: str | None = Field(default=None, max_length=256)  # type: ignore


class CollectionPublic(CollectionBase):
    id: uuid.UUID
