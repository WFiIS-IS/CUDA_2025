import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from app.db import DbSessionDep
from app.models.core import Bookmark


class BookmarkRepository:
    def __init__(self, session: DbSessionDep):
        self.session = session

    async def get_all(self) -> Sequence[Bookmark]:
        results = await self.session.execute(select(Bookmark).order_by(Bookmark.url))
        return results.scalars().all()

    async def get_by_collection_id(
        self, collection_id: uuid.UUID | None
    ) -> Sequence[Bookmark]:
        bookmarks = await self.session.execute(
            select(Bookmark).where(Bookmark.collection_id == collection_id)
        )
        return bookmarks.scalars().all()

    async def get_by_id(self, bookmark_id: uuid.UUID) -> Bookmark | None:
        result = await self.session.execute(
            select(Bookmark)
            .where(Bookmark.id == bookmark_id)
            .options(
                selectinload(Bookmark.collection),
                selectinload(Bookmark.ai_suggestion),
                selectinload(Bookmark.tags),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        url: str,
        title: str | None,
        description: str | None,
        collection_id: uuid.UUID | None,
    ) -> Bookmark:
        bookmark = Bookmark(
            url=url,
            title=title,
            description=description,
            collection_id=collection_id,
        )
        self.session.add(bookmark)
        await self.session.commit()
        await self.session.refresh(
            bookmark, ["collection", "ai_suggestion", "tags", "id"]
        )
        return bookmark

    async def delete(self, bookmark_id: uuid.UUID) -> int:
        result = await self.session.execute(
            delete(Bookmark).where(Bookmark.id == bookmark_id)
        )
        await self.session.commit()
        return result.rowcount

    async def update(
        self,
        bookmark_id: uuid.UUID,
        *,
        url: str,
        title: str | None,
        description: str | None,
        collection_id: uuid.UUID | None,
    ):
        result = await self.session.execute(
            update(Bookmark)
            .where(Bookmark.id == bookmark_id)
            .values(
                url=url,
                title=title,
                description=description,
                collection_id=collection_id,
            )
        )
        await self.session.commit()
        return result.rowcount


BookmarkRepositoryDep = Annotated[BookmarkRepository, Depends(BookmarkRepository)]
