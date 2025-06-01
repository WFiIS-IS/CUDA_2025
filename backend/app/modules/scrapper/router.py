import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from sqlmodel import select

from app.db import DbSession
from app.models import Job, JobCreate, JobStatus

from .jobs import process_scraping

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


class TaskSummary(BaseModel):
    """Summary model for task list."""

    task_id: str
    status: str
    url: str
    created_at: str
    completed_at: str | None = None
    has_results: bool


class TaskListResponse(BaseModel):
    """Response model for task list."""

    tasks: list[TaskSummary]
    total_tasks: int


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
                     If a job is already processing for this URL, returns that job's info.

    Example:
        GET /scrapper/scrape?url=https://example.com
    """
    url_str = str(url)

    # Check if there's already a processing job for this URL
    existing_query = select(Job).where(
        Job.url == url_str, Job.status == JobStatus.PROCESSING
    )
    result = await db.exec(existing_query)
    existing_job = result.first()

    if existing_job:
        # Return existing processing job instead of creating new one
        return ScrapingTask(
            task_id=str(existing_job.id),
            status=existing_job.status.value,
            message="Job is already processing for this URL",
            created_at=existing_job.created_at.isoformat(),
        )

    # Create new job in database
    job_create = JobCreate(url=url_str)
    job = Job.model_validate(job_create)

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Add background task for processing
    background_tasks.add_task(process_scraping, str(job.id), url_str)

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


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    db: DbSession,
    status: JobStatus | None = Query(None, description="Filter tasks by status"),
) -> TaskListResponse:
    """List all scraping tasks with optional filtering and sorting.

    Args:
        db (DbSession): Database session dependency.
        status (JobStatus | None): Optional status filter (PENDING, PROCESSING, COMPLETED, FAILED).
        sort_desc (bool): Sort by created_at descending (newest first) if True, ascending if False.

    Returns:
        TaskListResponse: List of tasks matching criteria with summary info.
    """
    # Build query with optional status filter
    query = select(Job)

    if status is not None:
        query = query.where(Job.status == status)

    query = query.order_by(Job.created_at.desc())

    result = await db.exec(query)
    tasks = result.all()

    task_summaries = [
        TaskSummary(
            task_id=str(task.id),
            status=task.status.value,
            url=task.url,
            created_at=task.created_at.isoformat(),
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            has_results=task.results is not None,
        )
        for task in tasks
    ]

    return TaskListResponse(tasks=task_summaries, total_tasks=len(tasks))


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
