__all__ = ["DbSessionDep", "get_db_session_manager", "DbSessionManager"]

import contextlib
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from settings import get_settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DbSessionManager:
    expire_on_commit: bool = False

    def __init__(self, dsn: str | None = None):
        settings = get_settings()

        self.engine = create_async_engine(
            dsn or str(settings.SQLALCHEMY_DATABASE_URI), echo=True
        )
        self.async_sessionmaker = async_sessionmaker(
            bind=self.engine, expire_on_commit=self.expire_on_commit
        )

    @contextlib.asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.async_sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@lru_cache
def get_db_session_manager(dsn: str | None = None) -> DbSessionManager:
    return DbSessionManager(dsn)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    db_session_manager = get_db_session_manager()
    async with db_session_manager.get_session() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_session)]
