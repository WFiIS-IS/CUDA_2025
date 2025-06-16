import uuid

from pydantic import Field

from app.schemas.base import BaseSchema


class CollectionBase(BaseSchema):
    """Base schema for collection models."""

    name: str = Field(..., max_length=256, description="The name of the collection.")


class CollectionPublic(CollectionBase):
    """Public schema for collection models."""

    id: uuid.UUID
    bookmarks_count: int = Field(
        ..., ge=0, description="The number of bookmarks in the collection."
    )


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""


class CollectionUpdate(CollectionBase):
    """Schema for updating an existing collection."""
