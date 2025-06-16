from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select

from app.db import DbSessionDep
from app.models.tag import Tag


class TagsRepository:
    def __init__(self, session: DbSessionDep):
        self.session = session

    async def get_all(self) -> Sequence[Tag]:
        results = await self.session.execute(select(Tag).order_by(Tag.name))
        return results.scalars().all()

    async def get_by_name(self, name: str) -> Tag | None:
        result = await self.session.execute(select(Tag).where(Tag.name == name))
        return result.scalar_one_or_none()

    async def create(self, *, name: str) -> Tag:
        tag = Tag(name=name)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def delete(self, tag_name: str) -> int:
        result = await self.session.execute(delete(Tag).where(Tag.name == tag_name))
        return result.rowcount


TagsRepositoryDep = Annotated[TagsRepository, Depends(TagsRepository)]
