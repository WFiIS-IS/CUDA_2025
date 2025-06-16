import uuid

from pydantic import Field

from app.schemas.base import BaseSchema


class BookmarkBase(BaseSchema):
    """Base schema for bookmarks."""

    url: str = Field(
        ...,
        max_length=1024,
        description="The URL of the bookmark.",
    )
    title: str | None = Field(
        None,
        max_length=256,
        description="The title of the bookmark. If not provided, it will be derived from the URL.",
    )
    description: str | None = Field(
        None,
        max_length=1024,
        description="A brief description of the bookmark.",
    )
    collection_id: uuid.UUID | None = Field(
        None,
        description="The ID of the collection to which this bookmark belongs.",
    )


class BookmarkPublic(BookmarkBase):
    """Public schema for bookmarks, excluding sensitive information."""

    id: uuid.UUID = Field(
        ...,
        description="The unique identifier of the bookmark.",
    )


class BookmarkCreate(BookmarkBase):
    """Schema for creating a new bookmark."""


class BookmarkUpdate(BookmarkBase):
    """Schema for updating an existing bookmark."""


class BookmarkAISuggestionPublic(BaseSchema):
    """Public schema for AI-generated bookmark suggestions."""

    title: str = Field(
        ...,
        description="The title of the AI-generated bookmark suggestion.",
    )
    description: str = Field(
        ...,
        description="A brief description of the AI-generated bookmark suggestion.",
    )
    tags: list[str] = Field(
        ...,
        description="A list of tags associated with the AI-generated bookmark suggestion.",
    )
    collection_id: uuid.UUID | None = Field(
        None,
        description="The ID of the collection to which this AI-generated bookmark suggestion belongs.",
    )
