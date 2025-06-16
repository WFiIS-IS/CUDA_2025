__all__ = ["Base", "IdMixin", "CreatedUpdatedAtMixin"]

import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""


class IdMixin(MappedAsDataclass):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        init=False,
    )


class CreatedUpdatedAtMixin(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        insert_default=datetime.now(UTC),
        server_default=text("(now() AT TIME ZONE 'UTC')"),
        init=False,
        default=None,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        insert_default=datetime.now(UTC),
        server_default=text("(now() AT TIME ZONE 'UTC')"),
        onupdate=datetime.now(UTC),
        init=False,
        default=None,
    )
