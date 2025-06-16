import uuid
from http import HTTPStatus
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Response
from sqlalchemy import select

from app.core.jobs import process_url
from app.db import DbSessionDep
from app.models.job import Job, JobStatus
from app.repositories.bookmarks import BookmarkRepositoryDep
from app.repositories.collections import CollectionRepositoryDep
from app.repositories.tags import TagsRepositoryDep
from app.schemas.bookmark import (
    BookmarkAISuggestionPublic,
    BookmarkCreate,
    BookmarkPublic,
    BookmarkUpdate,
)
from app.schemas.collection import CollectionCreate, CollectionPublic
from app.schemas.tag import TagCreate, TagPublic

router = APIRouter()


@router.get(
    "/collections/", response_model=list[CollectionPublic], tags=["collections"]
)
async def read_collections(
    collection_repository: CollectionRepositoryDep,
) -> list[CollectionPublic]:
    """Get all collections."""
    collections_list = await collection_repository.get_all()

    return [
        CollectionPublic.model_validate(collection) for collection in collections_list
    ]


@router.get(
    "/collections/{collection_id}/",
    response_model=CollectionPublic,
    tags=["collections"],
)
async def read_collection(
    collection_id: uuid.UUID, collection_repository: CollectionRepositoryDep
):
    """Get a collection by its ID."""
    collection = await collection_repository.get_by_id(collection_id)
    if collection is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )

    return CollectionPublic.model_validate(collection)


@router.post("/collections/", response_model=CollectionPublic, tags=["collections"])
async def create_collection(
    body: CollectionCreate, collection_repository: CollectionRepositoryDep
) -> CollectionPublic:
    """Create a new collection."""
    collection = await collection_repository.create(
        **body.model_dump(exclude_unset=True)
    )
    return CollectionPublic.model_validate(collection)


@router.delete(
    "/collections/{collection_id}/",
    response_model=CollectionPublic,
    tags=["collections"],
)
async def delete_collection(
    collection_id: uuid.UUID, collection_repository: CollectionRepositoryDep
):
    """Delete a collection."""
    delete_count = await collection_repository.delete(collection_id)
    if delete_count == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/bookmarks/", response_model=list[BookmarkPublic], tags=["bookmarks"])
async def read_all_bookmarks(
    bookmark_repository: BookmarkRepositoryDep,
    collection_id: uuid.UUID | None | Literal["null"] = Query(
        default=None,
        alias="collectionId",
    ),
):
    """Get all bookmarks, optionally filtered by collection ID."""
    if collection_id is None:
        result = await bookmark_repository.get_all()
    elif collection_id == "null":
        result = await bookmark_repository.get_by_collection_id(None)
    else:
        result = await bookmark_repository.get_by_collection_id(collection_id)
    return [BookmarkPublic.model_validate(bookmark) for bookmark in result]


@router.get(
    "/collections/{collection_id}/bookmarks/",
    response_model=list[BookmarkPublic],
    tags=["bookmarks"],
)
async def read_collection_bookmarks(
    collection_id: uuid.UUID, collection_repository: CollectionRepositoryDep
):
    """Get all bookmarks in a specific collection."""
    collection = await collection_repository.get_by_id(collection_id)
    if collection is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )

    return [
        BookmarkPublic.model_validate(bookmark) for bookmark in collection.bookmarks
    ]


@router.post(
    "/collections/{collection_id}/bookmarks/",
    response_model=BookmarkPublic,
    tags=["bookmarks"],
)
async def create_collection_bookmark(
    collection_id: uuid.UUID,
    body: BookmarkCreate,
    bookmark_repository: BookmarkRepositoryDep,
    collection_repository: CollectionRepositoryDep,
    session: DbSessionDep,
    background_tasks: BackgroundTasks,
):
    """Create a new bookmark in a specific collection."""
    collection = await collection_repository.get_by_id(collection_id)
    if collection is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Collection with id "{collection_id}" not found',
        )
    bookmark = await bookmark_repository.create(
        **body.model_dump(exclude_unset=True, exclude={"collection_id"}),
        collection_id=collection_id,
    )

    existing_job = await session.execute(
        select(Job).where(Job.bookmark_id == bookmark.id)
    )
    job = existing_job.scalar_one_or_none()
    if not job or job.status == JobStatus.FAILED:
        job = Job(bookmark_id=bookmark.id)
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(process_url, str(job.id), bookmark.url)

    return BookmarkPublic.model_validate(bookmark)


@router.put(
    "/bookmarks/{bookmark_id}/",
    response_model=BookmarkPublic,
    tags=["bookmarks"],
)
async def update_collection_bookmark(
    bookmark_id: uuid.UUID,
    body: BookmarkUpdate,
    bookmark_repository: BookmarkRepositoryDep,
    session: DbSessionDep,
    background_tasks: BackgroundTasks,
):
    """Update an existing bookmark."""
    updated_count = await bookmark_repository.update(
        bookmark_id, **body.model_dump(exclude_unset=True)
    )
    if updated_count == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )
    bookmark = await bookmark_repository.get_by_id(bookmark_id)
    if bookmark is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    existing_job = await session.execute(
        select(Job).where(Job.bookmark_id == bookmark.id)
    )
    job = existing_job.scalar_one_or_none()
    if not job or job.status == JobStatus.FAILED:
        job = Job(bookmark_id=bookmark.id)
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(process_url, str(job.id), bookmark.url)

    return BookmarkPublic.model_validate(bookmark)


@router.post(
    "/bookmarks/",
    response_model=BookmarkPublic,
    tags=["bookmarks"],
)
async def create_bookmark(
    body: BookmarkCreate,
    bookmark_repository: BookmarkRepositoryDep,
    collection_repository: CollectionRepositoryDep,
    session: DbSessionDep,
    background_tasks: BackgroundTasks,
):
    """Create a new bookmark."""
    collection_id = body.collection_id
    if collection_id:
        collection = await collection_repository.get_by_id(collection_id)
        if collection is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Collection with id "{collection_id}" not found',
            )
    bookmark = await bookmark_repository.create(
        **body.model_dump(exclude_unset=True),
    )

    existing_job = await session.execute(
        select(Job).where(Job.bookmark_id == bookmark.id)
    )
    job = existing_job.scalar_one_or_none()
    if not job or job.status == JobStatus.FAILED:
        job = Job(bookmark_id=bookmark.id)
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(process_url, str(job.id), bookmark.url)

    return BookmarkPublic.model_validate(bookmark)


@router.delete("/bookmarks/{bookmark_id}/", tags=["bookmarks"])
async def delete_bookmark(
    bookmark_id: uuid.UUID, bookmark_repository: BookmarkRepositoryDep
):
    """Delete a bookmark by its ID."""
    delete_count = await bookmark_repository.delete(bookmark_id)
    if delete_count == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/bookmarks/{bookmark_id}/tags/", response_model=list[str], tags=["tags"])
async def get_bookmark_tags(
    bookmark_id: uuid.UUID, bookmark_repository: BookmarkRepositoryDep
):
    """Get all tags associated with a specific bookmark."""
    bookmark = await bookmark_repository.get_by_id(bookmark_id)
    if bookmark is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    return [tag.name for tag in bookmark.tags]


@router.get("/tags/", response_model=list[TagPublic], tags=["tags"])
async def get_all_tags(tag_repository: TagsRepositoryDep):
    """Retrieve all tags with their usage count (number of bookmarks per tag)."""
    tags = await tag_repository.get_all()

    return [TagPublic(tag_name=tag.name, usage_count=tag.usage_count) for tag in tags]


@router.post("/bookmarks/{bookmark_id}/tags/", response_model=list[str], tags=["tags"])
async def add_tag_to_bookmark(
    bookmark_id: uuid.UUID,
    tag_create: TagCreate,
    tag_repository: TagsRepositoryDep,
    bookmark_repository: BookmarkRepositoryDep,
    session: DbSessionDep,
):
    """Add a tag to a specific bookmark."""
    bookmark = await bookmark_repository.get_by_id(bookmark_id)
    if bookmark is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    tag = await tag_repository.get_by_name(tag_create.tag)
    if not tag:
        tag = await tag_repository.create(name=tag_create.tag)
    bookmark.tags.append(tag)
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark, ["tags"])

    return [tag.name for tag in bookmark.tags]


@router.delete(
    "/bookmarks/{bookmark_id}/tags/{tag_name}/",
    response_model=list[str],
    tags=["tags"],
)
async def remove_tag_from_bookmark(
    bookmark_id: uuid.UUID,
    tag_name: str,
    session: DbSessionDep,
    bookmark_repository: BookmarkRepositoryDep,
):
    """Remove a tag from a specific bookmark."""
    bookmark = await bookmark_repository.get_by_id(bookmark_id)
    if bookmark is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )

    bookmark.tags = [tag for tag in bookmark.tags if tag.name != tag_name]
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark, ["tags"])

    return [tag.name for tag in bookmark.tags]


@router.post("/tags/", response_model=TagPublic, tags=["tags"])
async def create_tag(body: TagCreate, tag_repository: TagsRepositoryDep):
    """Create a new tag."""
    tag_name = body.tag
    tag = await tag_repository.get_by_name(tag_name)
    if tag:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f'Tag with name "{tag_name}" already exists',
        )
    tag = await tag_repository.create(name=tag_name)
    return TagPublic(tag_name=tag.name, usage_count=tag.usage_count)


@router.get(
    "/bookmarks/{bookmark_id}/ai-suggestion/",
    response_model=BookmarkAISuggestionPublic | None,
    tags=["ai"],
)
async def get_bookmark_ai_suggestion(
    bookmark_id: uuid.UUID, bookmark_repository: BookmarkRepositoryDep
):
    """Get AI-generated suggestion for a bookmark."""
    bookmark = await bookmark_repository.get_by_id(bookmark_id)
    if bookmark is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )
    ai_suggestion = bookmark.ai_suggestion

    if ai_suggestion is None:
        return None

    return BookmarkAISuggestionPublic(
        title=ai_suggestion.title,
        description=ai_suggestion.description,
        collection_id=ai_suggestion.collection_id,
        tags=ai_suggestion.tags,
    )
