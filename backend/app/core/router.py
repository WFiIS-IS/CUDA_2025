import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import func
from sqlmodel import select

from app.db import DbSession
from app.models import (
    Bookmark,
    Collection,
)
from app.schemas import (
    BookmarkCreate,
    BookmarkPublic,
    CollectionCreate,
    CollectionPublic,
)

router = APIRouter()


@router.get("/collections/", response_model=list[CollectionPublic], tags=["links"])
async def read_collections(session: DbSession) -> list[CollectionPublic]:
    """Get all collections."""
    # Additionaly get the number of bookmarks in each collection

    collections = await session.exec(
        select(Collection, func.count(Bookmark.id).label("bookmarks_count"))
        .outerjoin(Bookmark, Bookmark.collection_id == Collection.id)
        .group_by(Collection)
    )
    return [
        CollectionPublic.model_validate(collection, update={"bookmarks_count": count})
        for collection, count in collections
    ]


@router.post("/collections/", response_model=CollectionPublic, tags=["links"])
async def create_collection(
    body: CollectionCreate, session: DbSession
) -> CollectionPublic:
    """Create a new collection."""
    collection = Collection.model_validate(body)
    session.add(collection)
    await session.commit()
    await session.refresh(collection)
    return CollectionPublic.model_computed_fields(
        collection, update={"bookmarks_count": 0}
    )


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
    "/collections/{collection_id}/bookmarks",
    response_model=list[BookmarkPublic],
    tags=["links"],
)
async def read_collection_bookmarks(collection_id: uuid.UUID, session: DbSession):
    collection = await session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    bookmarks = await session.exec(
        select(Bookmark).where(Bookmark.collection_id == collection.id)
    )
    return list(bookmarks)


@router.post(
    "/collections/{collection_id}/bookmarks",
    response_model=BookmarkPublic,
    tags=["links"],
)
async def create_collection_bookmark(
    collection_id: uuid.UUID, session: DbSession, body: BookmarkCreate
):
    collection = await session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    link_entry = Bookmark.model_validate(body, update={"collection_id": collection.id})
    session.add(link_entry)
    await session.commit()
    await session.refresh(link_entry)
    return BookmarkPublic.model_validate(link_entry)


@router.get("/bookmarks", response_model=list[BookmarkPublic], tags=["links"])
async def read_all_bookmarks(session: DbSession):
    bookmarks = await session.exec(select(Bookmark))
    return list(bookmarks)


@router.post(
    "/bookmarks",
    response_model=BookmarkPublic,
    tags=["links"],
)
async def create_bookmark(session: DbSession, body: BookmarkCreate):
    bookmark = Bookmark.model_validate(body, update={"collection_id": None})
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)
    return BookmarkPublic.model_validate(bookmark)
