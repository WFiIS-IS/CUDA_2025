import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Response
from sqlmodel import select

from app.db import DbSession
from app.models import Collection, CollectionCreate, CollectionPublic

router = APIRouter()


@router.get("/collections/", response_model=list[CollectionPublic], tags=["links"])
async def read_collections(session: DbSession) -> list[CollectionPublic]:
    """Get all collections."""
    collections = await session.exec(select(Collection))
    return [CollectionPublic.model_validate(collection) for collection in collections]


@router.post("/collections/", response_model=CollectionPublic, tags=["links"])
async def create_collection(
    body: CollectionCreate, session: DbSession
) -> CollectionPublic:
    """Create a new collection."""
    collection = Collection.model_validate(body)
    session.add(collection)
    await session.commit()
    await session.refresh(collection)
    return CollectionPublic.model_validate(collection)


@router.delete(
    "/collections/{collection_id}", response_model=CollectionPublic, tags=["links"]
)
async def delete_collection(collection_id: uuid.UUID, session: DbSession):
    """Delete a collection."""
    collection = await session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    await session.delete(collection)
    await session.commit()
    return Response(status_code=HTTPStatus.NO_CONTENT)
