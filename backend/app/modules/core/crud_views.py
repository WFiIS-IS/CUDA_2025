from fastapi import APIRouter
from sqlmodel import select

from app.db import DbSession
from app.models import Collection, CollectionPublic

collection_routes = APIRouter()


@collection_routes.get("/", response_model=list[CollectionPublic])
async def read_collections(session: DbSession) -> list[CollectionPublic]:
    """Get all collections."""
    collections = await session.exec(select(Collection))
    return [CollectionPublic.model_validate(collection) for collection in collections]
