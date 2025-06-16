__all__ = ["Job", "JobStatus", "JobType"]

import uuid
from datetime import datetime
from enum import StrEnum, unique

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedUpdatedAtMixin, IdMixin
from app.models.core import Bookmark


@unique
class JobStatus(StrEnum):
    """Enumeration of possible job statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@unique
class JobType(StrEnum):
    """Enumeration of possible job types."""

    SCRAPE = "scrape"
    EMBED = "embed"
    ANALYZE = "analyze"


class Job(Base, IdMixin, CreatedUpdatedAtMixin):
    """Database model for background jobs"""

    __tablename__ = "job"

    bookmark_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookmark.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bookmark: Mapped[Bookmark] = relationship(
        back_populates="jobs", init=False, uselist=False
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        server_default=text(f"'{JobStatus.PENDING.value}'"),
    )
    type: Mapped[JobType] = mapped_column(
        Enum(JobType),
        nullable=False,
        server_default=text(f"'{JobType.SCRAPE.value}'"),
        default=JobType.SCRAPE,
    )
    results: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
    error_message: Mapped[str | None] = mapped_column(
        nullable=True,
        default=None,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default=None,
        nullable=True,
    )
