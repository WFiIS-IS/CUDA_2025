__all__ = [
    "Collection",
    "Bookmark",
]

import typing
import uuid
from dataclasses import field

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.models.base import Base, IdMixin

if typing.TYPE_CHECKING:
    from app.models.ai import BookmarkAISuggestion
    from app.models.job import Job
    from app.models.tag import Tag


class Collection(Base, IdMixin):
    """Collection model for grouping bookmarks."""

    __tablename__ = "collection"

    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="collection",
        init=False,
    )
    bookmarks_count: Mapped[int] = field(init=False)


class Bookmark(Base, IdMixin):
    """Bookmark model for storing URLs"""

    __tablename__ = "bookmark"

    url: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(
        String(256), nullable=True, index=True, default=None
    )
    description: Mapped[str | None] = mapped_column(
        String(1024), nullable=True, default=None
    )

    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("collection.id", ondelete="SET NULL"), nullable=True, default=None
    )
    collection: Mapped["Collection | None"] = relationship(
        back_populates="bookmarks", uselist=False, init=False
    )

    ai_suggestion: Mapped["BookmarkAISuggestion | None"] = relationship(
        back_populates="bookmark",
        uselist=False,
        init=False,
        cascade="all, delete",
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary="tag_bookmark_association",
        back_populates="bookmarks",
        init=False,
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="bookmark",
        init=False,
    )


Collection.bookmarks_count = column_property(
    select(func.count(Bookmark.id))
    .where(Bookmark.collection_id == Collection.id)
    .correlate_except(Bookmark)
    .scalar_subquery(),
    init=False,
)
