from __future__ import annotations

import uuid

from sqlmodel import Field, Relationship, SQLModel

SHORT_TEXT_LENGTH = 256
LONG_TEXT_LENGTH = 1024


class TagLinkAssociation(SQLModel, table=True):
    tag_name: str = Field(foreign_key="tag.name", primary_key=True)
    tag: Tag = Relationship(back_populates="links")

    link_id: uuid.UUID = Field(foreign_key="linkentry.id", primary_key=True)
    link: LinkEntry = Relationship(back_populates="tags")


class LinkEntry(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(max_length=LONG_TEXT_LENGTH)
    title: str | None = Field(default=None, max_length=SHORT_TEXT_LENGTH)
    description: str | None = Field(default=None, max_length=LONG_TEXT_LENGTH)

    collection_id: uuid.UUID = Field(foreign_key="collection.id", nullable=False)
    collection: Collection = Relationship(
        back_populates="links",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    ai_suggestion: LinkAISuggestion | None = Relationship(
        back_populates="link",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    tags: list[Tag] = Relationship(link_model=TagLinkAssociation)


class Collection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=SHORT_TEXT_LENGTH)
    links: list[LinkEntry] = Relationship(
        back_populates="collection",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class LinkAISuggestion(SQLModel, table=True):
    link_id: uuid.UUID = Field(foreign_key="linkentry.id", primary_key=True)
    link: LinkEntry = Relationship(back_populates="suggestion")
    title: str = Field(max_length=SHORT_TEXT_LENGTH)
    description: str = Field(max_length=LONG_TEXT_LENGTH)


class Tag(SQLModel, table=True):
    name: str = Field(max_length=64, primary_key=True)
