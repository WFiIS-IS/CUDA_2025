import uuid
from datetime import datetime

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import Field

from app.models import CollectionBase, JobBase, LinkEntryBase


class JobCreate(JobBase):
    """Model for creating new jobs."""

    pass


class JobPublic(JobBase):
    """Public model for job information without sensitive data."""

    id: uuid.UUID
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


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
