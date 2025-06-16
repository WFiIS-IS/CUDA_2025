from pydantic import Field

from app.schemas.base import BaseSchema


class TagPublic(BaseSchema):
    """Schema for public representation of a tag."""

    tag_name: str = Field(
        ...,
        description="The name of the tag, which is unique and used to identify the tag.",
    )
    usage_count: int = Field(
        ...,
        description="The number of times the tag has been used across all posts.",
        ge=0,
    )


class TagCreate(BaseSchema):
    """Schema for creating a new tag."""

    tag: str = Field(
        ...,
        description="The tag to add to the bookmark.",
        pattern=r"^[a-z0-9\-_]+$",
        min_length=1,
        max_length=64,
        examples=["example-tag", "another-tag", "tag_with_numbers_123"],
    )
