import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db import DbSessionDep
from app.models.core import Collection


class CollectionRepository:
    def __init__(self, session: DbSessionDep):
        self.session = session

    async def get_all(self) -> Sequence[Collection]:
        results = await self.session.execute(
            select(Collection).order_by(Collection.name)
        )
        return results.scalars().all()

    async def get_by_id(self, collection_id: uuid.UUID) -> Collection | None:
        collection = await self.session.execute(
            select(Collection)
            .where(Collection.id == collection_id)
            .options(selectinload(Collection.bookmarks))
        )
        return collection.scalar_one_or_none()

    async def create(self, *, name: str) -> Collection:
        collection = Collection(name=name)
        self.session.add(collection)
        await self.session.commit()
        await self.session.refresh(collection)
        return collection

    async def delete(self, collection_id: uuid.UUID) -> int:
        result = await self.session.execute(
            delete(Collection).where(Collection.id == collection_id)
        )
        return result.rowcount


CollectionRepositoryDep = Annotated[CollectionRepository, Depends(CollectionRepository)]
