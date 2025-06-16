import uuid
from http import HTTPStatus
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Response
from sqlalchemy import func
from sqlmodel import select

from app.core.jobs import process_url
from app.db import DbSession
from app.models import (
    Bookmark,
    BookmarkAISuggestion,
    Collection,
    Job,
    JobStatus,
    Tag,
    TagBookmarkAssociation,
)
from app.schemas import (
    BookmarkAISuggestionPublic,
    BookmarkCreate,
    BookmarkPublic,
    BookmarkUpdate,
    CollectionCreate,
    CollectionPublic,
    JobCreate,
    JobSummaryPublic,
    TagCreate,
    TagPublic,
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
    return CollectionPublic.model_validate(collection, update={"bookmarks_count": 0})


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


@router.put(
    "/bookmarks/{bookmark_id}/",
    response_model=BookmarkPublic,
    tags=["links"],
)
async def update_collection_bookmark(
    bookmark_id: uuid.UUID,
    session: DbSession,
    body: BookmarkUpdate,
    background_tasks: BackgroundTasks,
):
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(bookmark, field, value)
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)

    existing_job = await session.exec(select(Job).where(Job.bookmark_id == bookmark.id))
    job = existing_job.first()
    if not job or job.status == JobStatus.FAILED:
        job_create = JobCreate(url=bookmark.url)
        job = Job.model_validate(job_create, update={"bookmark_id": bookmark.id})
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(process_url, str(job.id), bookmark.url)

    return BookmarkPublic.model_validate(bookmark)


@router.post(
    "/collections/{collection_id}/bookmarks/",
    response_model=BookmarkPublic,
    tags=["links"],
)
async def create_collection_bookmark(
    collection_id: uuid.UUID, session: DbSession, body: BookmarkCreate, background_tasks: BackgroundTasks
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

    existing_job = await session.exec(select(Job).where(Job.bookmark_id == link_entry.id))
    job = existing_job.first()
    if not job or job.status == JobStatus.FAILED:
        job_create = JobCreate(url=link_entry.url)
        job = Job.model_validate(job_create, update={"bookmark_id": link_entry.id})
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(process_url, str(job.id), link_entry.url)

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
async def create_bookmark(session: DbSession, body: BookmarkCreate, background_tasks: BackgroundTasks):
    collection_Id = body.collection_id
    if collection_Id:
        collection = await session.get(Collection, collection_Id)
        if not collection:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Collection with id "{collection_Id}" not found',
            )
    bookmark = Bookmark.model_validate(body,update={"collection_id": collection_Id} )
    bookmark = Bookmark.model_validate(body )
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)


    existing_job = await session.exec(select(Job).where(Job.bookmark_id == bookmark.id))
    job = existing_job.first()
    if not job or job.status == JobStatus.FAILED:
        job_create = JobCreate(url=bookmark.url)
        job = Job.model_validate(job_create, update={"bookmark_id": bookmark.id})
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(process_url, str(job.id), bookmark.url)

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


@router.get("/tags/", response_model=list[TagPublic], tags=["links"])
async def get_all_tags(session: DbSession):
    """Retrieve all tags with their usage count (number of bookmarks per tag)."""
    result = await session.exec(
        select(
            Tag.name.label("tag_name"),
            func.count(TagBookmarkAssociation.bookmark_id).label("usage_count"),
        )
        .outerjoin(TagBookmarkAssociation, Tag.name == TagBookmarkAssociation.tag_name)
        .group_by(Tag.name)
    )
    tags = [
        TagPublic.model_validate({"tag_name": tag_name, "usage_count": usage_count})
        for tag_name, usage_count in result
    ]

    return tags


@router.post("/tags/", response_model=TagPublic, tags=["links"])
async def create_tag(session: DbSession, body: TagCreate):
    tag_name = body.tag
    db_tag = await session.get(Tag, tag_name)
    if db_tag:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f'Tag with name "{tag_name}" already exists',
        )

    tag = Tag(name=tag_name)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    usage_count = await session.exec(
        select(func.count(TagBookmarkAssociation.bookmark_id)).where(
            TagBookmarkAssociation.tag_name == tag.name
        )
    )
    usage_count = usage_count.first()
    return TagPublic.model_validate({"tag_name": tag.name, "usage_count": usage_count})


@router.post("/process_url", response_model=JobSummaryPublic, tags=["processing"])
async def process_url_endpoint(
    background_tasks: BackgroundTasks,
    db: DbSession,
    job_create: JobCreate,
) -> JobSummaryPublic:
    """Submit a URL for scraping and analysis.

    This endpoint accepts a URL and returns a task ID that can be used to
    check the scraping progress and retrieve results asynchronously.

    Args:
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        db (DbSession): Database session dependency.
        url (HttpUrl): The URL to scrape. Must be a valid HTTP/HTTPS URL.

    Returns:
        ScrapingTask: Task information including unique ID for tracking.
                     If a job is already processing for this URL, returns that job's info.

    Example:
        GET /scrapper/scrape?url=https://example.com
    """

    # Check if there is a bookmark for this url
    existing_bookmark = await db.exec(
        select(Bookmark).where(Bookmark.url == job_create.url)
    )
    bookmark = existing_bookmark.first()

    if not bookmark:
        bookmark = Bookmark(url=job_create.url)
        db.add(bookmark)
        await db.commit()
        await db.refresh(bookmark)

    existing_job = await db.exec(select(Job).where(Job.bookmark_id == bookmark.id))
    job = existing_job.first()

    if job and job.status != JobStatus.FAILED:
        return JobSummaryPublic.model_validate(job)

    job = Job.model_validate(job_create, update={"bookmark_id": bookmark.id})

    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(process_url, str(job.id), job_create.url)

    return JobSummaryPublic(
        id=str(job.id),
        status=job.status.value,
        created_at=job.created_at.isoformat(),
        url=job_create.url,
        bookmark_id=str(bookmark.id),
    )


@router.get(
    "/bookmarks/{bookmark_id}/ai-suggestion/",
    response_model=BookmarkAISuggestionPublic | None,
    tags=["links"],
)
async def get_bookmark_ai_suggestion(bookmark_id: uuid.UUID, session: DbSession):
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Bookmark with id "{bookmark_id}" not found',
        )
    ai_suggestion = await session.get(BookmarkAISuggestion, bookmark_id)
    if not ai_suggestion:
        return None

    return BookmarkAISuggestionPublic(
        title=ai_suggestion.title,
        description=ai_suggestion.description,
        collection_id=ai_suggestion.collection_id,
        tags=ai_suggestion.tags
    )
