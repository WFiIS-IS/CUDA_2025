__all__ = ["Tag", "TagBookmarkAssociation"]

import uuid
from dataclasses import field

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.models.base import Base
from app.models.core import Bookmark


class Tag(Base):
    """Tag model"""

    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)

    bookmarks: Mapped[list[Bookmark]] = relationship(
        secondary="tag_bookmark_association",
        back_populates="tags",
        init=False,
    )
    usage_count: Mapped[int] = field(init=False)


class TagBookmarkAssociation(Base):
    """Association model for many-to-many relationship between tags and bookmarks."""

    __tablename__ = "tag_bookmark_association"

    tag_name: Mapped[str] = mapped_column(
        ForeignKey("tag.name", ondelete="CASCADE"), primary_key=True
    )
    bookmark_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookmark.id", ondelete="CASCADE"), primary_key=True
    )


Tag.usage_count = column_property(
    select(func.count("*"))
    .where(TagBookmarkAssociation.tag_name == Tag.name)
    .correlate_except(Tag)
    .scalar_subquery(),
    init=False,
)
