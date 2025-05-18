from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.models import *  # noqa: F401, F403

async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session: type[AsyncSession] = sessionmaker(
        bind=async_engine,  # type: ignore
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_async_session)]


async def create_db_and_table() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
