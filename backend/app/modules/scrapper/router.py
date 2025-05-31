import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from sqlmodel import select

from app.db import DbSession
from app.models import Job, JobCreate, JobStatus

from .analyzer import ScrapperAnalyzer
from .scrapper import Scrapper

# Create the router instance
router = APIRouter(prefix="/scrapper", tags=["scrapper"])


class ScrapingTask(BaseModel):
    """Response model for scraping task creation."""

    task_id: str
    status: str
    message: str
    created_at: str


class TaskStatus(BaseModel):
    """Response model for task status and results."""

    task_id: str
    status: str
    url: str
    created_at: str
    completed_at: str | None = None
    error: str | None = None
    results: dict[str, Any] | None = None


async def process_scraping_task(task_id: str, url: str) -> None:
    """Background task to process URL scraping.

    Args:
        task_id (str): Unique identifier for the scraping task.
        url (str): The URL to scrape and analyze.
    """
    # Import here to avoid circular imports
    from sqlalchemy.orm import sessionmaker
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.db import async_engine

    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Get the job from database
            job = await session.get(Job, uuid.UUID(task_id))
            if not job:
                return

            # Update job status to processing
            job.status = JobStatus.PROCESSING
            session.add(job)
            await session.commit()

            # Initialize scrapper and fetch content
            scrapper = Scrapper(url)
            await scrapper.fetch()

            if scrapper.soup is None:
                raise ValueError("Failed to fetch content from URL")

            # Run complete analysis
            analyzer = ScrapperAnalyzer(scrapper.soup)
            results = await analyzer.analyze()

            # Update job with results
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.results = results
            session.add(job)
            await session.commit()

        except Exception as e:
            # Update job with error information
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.error_message = str(e)
                session.add(job)
                await session.commit()


@router.get("/scrape", response_model=ScrapingTask)
async def scrape_url(
    background_tasks: BackgroundTasks,
    db: DbSession,
    url: HttpUrl = Query(..., description="URL to scrape and analyze"),
) -> ScrapingTask:
    """Submit a URL for scraping and analysis.

    This endpoint accepts a URL and returns a task ID that can be used to
    check the scraping progress and retrieve results asynchronously.

    Args:
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        db (DbSession): Database session dependency.
        url (HttpUrl): The URL to scrape. Must be a valid HTTP/HTTPS URL.

    Returns:
        ScrapingTask: Task information including unique ID for tracking.

    Example:
        GET /scrapper/scrape?url=https://example.com
    """
    # Create new job in database
    job_create = JobCreate(url=str(url))
    job = Job.model_validate(job_create)

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Add background task for processing
    background_tasks.add_task(process_scraping_task, str(job.id), str(url))

    return ScrapingTask(
        task_id=str(job.id),
        status=job.status.value,
        message="Scraping task submitted successfully",
        created_at=job.created_at.isoformat(),
    )


@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str, db: DbSession) -> TaskStatus:
    """Get the status and results of a scraping task.

    This endpoint allows checking the progress of a scraping task using
    the task ID returned from the scrape endpoint.

    Args:
        task_id (str): Unique identifier for the scraping task.
        db (DbSession): Database session dependency.

    Returns:
        TaskStatus: Complete task information including results if completed.

    Raises:
        HTTPException: If the task ID is not found.

    Example:
        GET /scrapper/task/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        job_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    job = await db.get(Job, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatus(
        task_id=task_id,
        status=job.status.value,
        url=job.url,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error=job.error_message,
        results=job.results,
    )


@router.get("/tasks")
async def list_tasks(
    db: DbSession,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """List scraping tasks with pagination.

    Args:
        db (DbSession): Database session dependency.
        limit (int): Maximum number of tasks to return (max 100).
        offset (int): Number of tasks to skip for pagination.

    Returns:
        Dict[str, Any]: Dictionary containing tasks with pagination info.
    """
    # Get total count
    count_query = select(Job)
    result = await db.exec(count_query)
    total_tasks = len(result.all())

    # Get paginated tasks
    query = select(Job).offset(offset).limit(limit).order_by(Job.created_at.desc())
    result = await db.exec(query)
    tasks = result.all()

    return {
        "total_tasks": total_tasks,
        "limit": limit,
        "offset": offset,
        "tasks": [
            {
                "task_id": str(task.id),
                "status": task.status.value,
                "url": task.url,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat()
                if task.completed_at
                else None,
                "has_results": task.results is not None,
            }
            for task in tasks
        ],
    }


@router.delete("/task/{task_id}")
async def delete_task(task_id: str, db: DbSession) -> dict[str, str]:
    """Delete a completed or failed scraping task.

    Args:
        task_id (str): Unique identifier for the scraping task.
        db (DbSession): Database session dependency.

    Returns:
        Dict[str, str]: Confirmation message.

    Raises:
        HTTPException: If the task ID is not found or task is still processing.
    """
    try:
        job_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    job = await db.get(Job, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")

    if job.status == JobStatus.PROCESSING:
        raise HTTPException(
            status_code=400, detail="Cannot delete task that is still processing"
        )

    await db.delete(job)
    await db.commit()

    return {"message": f"Task {task_id} deleted successfully"}
