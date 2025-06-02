"""Jobs router for CRUD operations on Job models."""

import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import desc, select

from app.db import DbSession
from app.models import AnalysisResult, EmbeddingResult, Job, JobStatus, JobType

# Create the router instance
router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobStatusResponse(BaseModel):
    """Response model for job status and results."""

    job_id: str
    status: str
    url: str
    type: str
    created_at: str
    completed_at: str | None = None
    error: str | None = None
    result_id: str | None = None


class JobSummary(BaseModel):
    """Summary model for job list."""

    job_id: str
    status: str
    url: str
    type: str
    created_at: str
    completed_at: str | None = None


class JobListResponse(BaseModel):
    """Response model for job list."""

    jobs: list[JobSummary]
    total_jobs: int


@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: DbSession) -> JobStatusResponse:
    """Get the status and results of a job.

    This endpoint allows checking the progress of any job using the job ID.

    Args:
        job_id (str): Unique identifier for the job.
        db (DbSession): Database session dependency.

    Returns:
        JobStatusResponse: Complete job information including results if completed.

    Raises:
        HTTPException: If the job ID is not found.

    Example:
        GET /jobs/job/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    job = await db.get(Job, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get result ID based on job type
    result_id = None
    if job.status == JobStatus.COMPLETED:
        match job.type:
            case JobType.SCRAPPING:
                # Get result ID from AnalysisResult table
                analysis_query = select(AnalysisResult).where(
                    AnalysisResult.url == job.url
                )
                analysis_result = await db.exec(analysis_query)
                analysis_record = analysis_result.first()

                if analysis_record:
                    result_id = str(analysis_record.id)
            case JobType.EMBEDDING:
                # Get result ID from EmbeddingResult table
                embedding_query = select(EmbeddingResult).where(
                    EmbeddingResult.url == job.url
                )
                embedding_result = await db.exec(embedding_query)
                embedding_record = embedding_result.first()

                if embedding_record:
                    result_id = str(embedding_record.id)

    return JobStatusResponse(
        job_id=job_id,
        status=job.status.value,
        url=job.url,
        type=job.type.value,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error=job.error_message,
        result_id=result_id,
    )


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    db: DbSession,
    status: JobStatus | None = Query(None, description="Filter jobs by status"),
    job_type: JobType | None = Query(None, description="Filter jobs by type"),
) -> JobListResponse:
    """List all jobs with optional filtering and sorting.

    Args:
        db (DbSession): Database session dependency.
        status (JobStatus | None): Optional status filter.
        job_type (JobType | None): Optional type filter.

    Returns:
        JobListResponse: List of jobs matching criteria with summary info.
    """
    # Build query with optional filters
    query = select(Job)

    if status is not None:
        query = query.where(Job.status == status)

    if job_type is not None:
        query = query.where(Job.type == job_type)

    query = query.order_by(desc(Job.created_at))

    result = await db.exec(query)
    jobs = result.all()

    # Create job summaries
    job_summaries = []
    for job in jobs:
        job_summaries.append(
            JobSummary(
                job_id=str(job.id),
                status=job.status.value,
                url=job.url,
                type=job.type.value,
                created_at=job.created_at.isoformat(),
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
            )
        )

    return JobListResponse(jobs=job_summaries, total_jobs=len(jobs))


@router.delete("/job/{job_id}")
async def delete_job(job_id: str, db: DbSession) -> dict[str, str]:
    """Delete a completed or failed job.

    Args:
        job_id (str): Unique identifier for the job.
        db (DbSession): Database session dependency.

    Returns:
        Dict[str, str]: Confirmation message.

    Raises:
        HTTPException: If the job ID is not found or job is still processing.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    job = await db.get(Job, job_uuid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.PROCESSING:
        raise HTTPException(
            status_code=400, detail="Cannot delete job that is still processing"
        )

    await db.delete(job)
    await db.commit()

    return {"message": f"Job {job_id} deleted successfully"}
