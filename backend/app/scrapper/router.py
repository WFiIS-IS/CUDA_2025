import uuid
from http import HTTPStatus

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Response
from sqlmodel import select

from app.db import DbSession
from app.models import Job, JobStatus
from app.schemas import JobCreate, JobListPublic, JobPublic, JobSummaryPublic

from .jobs import process_scraping

# Create the router instance
router = APIRouter(prefix="/scrapper", tags=["scrapper"])


@router.get("/scrape", response_model=JobSummaryPublic)
async def scrape_url(
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

    # Check if there's already a processing job for this URL
    existing_query = select(Job).where(
        Job.url == job_create.url, Job.status == JobStatus.PROCESSING
    )
    result = await db.exec(existing_query)
    existing_job = result.first()

    if existing_job:
        # Return existing processing job instead of creating new one
        return JobSummaryPublic.model_validate(existing_job)
    # Create new job in database
    job = Job.model_validate(job_create)

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Add background task for processing
    background_tasks.add_task(process_scraping, str(job.id), job_create.url)

    return JobSummaryPublic(
        id=str(job.id),
        status=job.status.value,
        created_at=job.created_at.isoformat(),
        url=job_create.url,
    )


@router.get("/task/{task_id}", response_model=JobPublic)
async def get_task_status(task_id: str, db: DbSession) -> JobPublic:
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

    return JobPublic.model_validate(job)


@router.get("/tasks", response_model=JobListPublic)
async def list_tasks(
    db: DbSession,
    status: JobStatus | None = Query(None, description="Filter tasks by status"),
) -> JobListPublic:
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
        JobPublic.model_validate(task)  # Convert each job to public model
        for task in tasks
    ]

    return JobListPublic(jobs=task_summaries, total_jobs=len(tasks))


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

    return Response(status_code=HTTPStatus.NO_CONTENT)
