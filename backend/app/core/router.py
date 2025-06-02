import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Response
from sqlmodel import select

from app.db import DbSession
from app.models import (
    Collection,
    CollectionCreate,
    CollectionPublic,
    LinkEntry,
    LinkEntryCreate,
    LinkEntryPublic,
)

router = APIRouter()


@router.get("/collections/", response_model=list[CollectionPublic], tags=["links"])
async def read_collections(session: DbSession) -> list[CollectionPublic]:
    """Get all collections."""
    collections = await session.exec(select(Collection))
    return list(collections)


@router.post("/collections/", response_model=CollectionPublic, tags=["links"])
async def create_collection(
    body: CollectionCreate, session: DbSession
) -> CollectionPublic:
    """Create a new collection."""
    collection = Collection.model_validate(body)
    session.add(collection)
    await session.commit()
    await session.refresh(collection)
    return collection


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


@router.get(
    "/collections/{collection_id}/links",
    response_model=list[LinkEntryPublic],
    tags=["links"],
)
async def read_collection_links(collection_id: uuid.UUID, session: DbSession):
    collection = await session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    links = await session.exec(
        select(LinkEntry).where(LinkEntry.collection_id == collection.id)
    )
    return list(links)


@router.post(
    "/collections/{collection_id}/links", response_model=LinkEntryPublic, tags=["links"]
)
async def create_link_entry(
    collection_id: uuid.UUID, session: DbSession, body: LinkEntryCreate
):
    collection = await session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    link_entry = LinkEntry.model_validate(body, update={"collection_id": collection.id})
    session.add(link_entry)
    await session.commit()
    await session.refresh(link_entry)
    return LinkEntryPublic.model_validate(link_entry)
