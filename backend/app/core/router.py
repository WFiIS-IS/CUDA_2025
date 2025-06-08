import uuid
from http import HTTPStatus
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import func
from sqlmodel import select

from app.db import DbSession
from app.models import (
    Bookmark,
    Collection,
    Tag,
    TagBookmarkAssociation,
)
from app.schemas import (
    BookmarkCreate,
    BookmarkPublic,
    CollectionCreate,
    CollectionPublic,
    TagCreate,
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


@router.get(
    "/collections/{collection_id}/", response_model=CollectionPublic, tags=["links"]
)
async def read_collection(collection_id: uuid.UUID, session: DbSession):
    collection = await session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    bookmarks_count = await session.exec(
        select(func.count(Bookmark.id)).where(Bookmark.collection_id == collection_id)
    )
    bookmarks_count = bookmarks_count.first()
    return CollectionPublic.model_validate(
        collection, update={"bookmarks_count": bookmarks_count}
    )


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
    "/collections/{collection_id}/", response_model=CollectionPublic, tags=["links"]
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
    "/collections/{collection_id}/bookmarks/",
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
    "/collections/{collection_id}/bookmarks/",
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


@router.get("/bookmarks/", response_model=list[BookmarkPublic], tags=["links"])
async def read_all_bookmarks(
    session: DbSession,
    collection_id: uuid.UUID | None | Literal["null"] = Query(
        default=None,
        alias="collectionId",
    ),
):
    if collection_id is None:
        result = await session.exec(select(Bookmark))
    elif collection_id == "null":
        result = await session.exec(
            select(Bookmark).where(Bookmark.collection_id == None)  # noqa: E711
        )
    else:
        result = await session.exec(
            select(Bookmark).where(Bookmark.collection_id == collection_id)
        )
    return list(result)


@router.post(
    "/bookmarks/",
    response_model=BookmarkPublic,
    tags=["links"],
)
async def create_bookmark(session: DbSession, body: BookmarkCreate):
    bookmark = Bookmark.model_validate(body, update={"collection_id": None})
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)
    return BookmarkPublic.model_validate(bookmark)


@router.delete("/bookmarks/{bookmark_id}/", tags=["links"])
async def delete_bookmark(bookmark_id: uuid.UUID, session: DbSession):
    """Delete a bookmark by its ID."""
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )
    await session.delete(bookmark)
    await session.commit()
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/bookmarks/{bookmark_id}/tags/", response_model=list[str], tags=["links"])
async def get_bookmark_tags(bookmark_id: uuid.UUID, session: DbSession):
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    tag_assocs = await session.exec(
        select(TagBookmarkAssociation.tag_name).where(
            TagBookmarkAssociation.bookmark_id == bookmark_id
        )
    )
    return list(tag_assocs)


@router.post("/bookmarks/{bookmark_id}/tags/", response_model=list[str], tags=["links"])
async def add_tag_to_bookmark(
    bookmark_id: uuid.UUID,
    tag_create: TagCreate,
    session: DbSession = None,
):
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    tag_name = tag_create.tag

    db_tag = await session.get(Tag, tag_name)
    if not db_tag:
        db_tag = Tag(name=tag_name)
        session.add(db_tag)
        await session.commit()
        await session.refresh(db_tag)

    assoc = await session.exec(
        select(TagBookmarkAssociation).where(
            TagBookmarkAssociation.bookmark_id == bookmark_id,
            TagBookmarkAssociation.tag_name == tag_name,
        )
    )
    if not assoc.first():
        session.add(TagBookmarkAssociation(bookmark_id=bookmark_id, tag_name=tag_name))
        await session.commit()

    tag_assocs = await session.exec(
        select(TagBookmarkAssociation.tag_name).where(
            TagBookmarkAssociation.bookmark_id == bookmark_id
        )
    )
    return list(tag_assocs)


@router.delete(
    "/bookmarks/{bookmark_id}/tags/{tag_name}/",
    response_model=list[str],
    tags=["links"],
)
async def remove_tag_from_bookmark(
    bookmark_id: uuid.UUID, tag_name: str, session: DbSession
):
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    assoc = await session.exec(
        select(TagBookmarkAssociation).where(
            TagBookmarkAssociation.bookmark_id == bookmark_id,
            TagBookmarkAssociation.tag_name == tag_name,
        )
    )
    assoc_obj = assoc.first()

    if not assoc_obj:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Tag with name "{tag_name}" not found for bookmark with id "{bookmark_id}"',
        )

    await session.delete(assoc_obj)
    await session.commit()

    tag_assocs = await session.exec(
        select(TagBookmarkAssociation.tag_name).where(
            TagBookmarkAssociation.bookmark_id == bookmark_id
        )
    )
    return list(tag_assocs)
