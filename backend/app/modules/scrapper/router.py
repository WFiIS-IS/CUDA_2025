import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import HttpUrl
from sqlmodel import desc, select

from app.db import DbSession
from app.models import AnalysisResult, Job, JobCreate, JobStatus, JobType

from ..jobs.tasks import process_scraping_task
from .models import AnalysisResultListResponse, AnalysisResultResponse, ScrapingTask

# Create the router instance
router = APIRouter(prefix="/scrapper", tags=["scrapper"])


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
            job_id=str(existing_job.id),
            status=existing_job.status.value,
            message="Job is already processing for this URL",
            created_at=existing_job.created_at.isoformat(),
        )

    # Create new job in database with SCRAPPING type
    job_create = JobCreate(url=url_str, type=JobType.SCRAPPING)
    job = Job.model_validate(job_create)

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Add background task for processing
    background_tasks.add_task(process_scraping_task, str(job.id), url_str)

    return ScrapingTask(
        job_id=str(job.id),
        status=job.status.value,
        message="Scraping task submitted successfully",
        created_at=job.created_at.isoformat(),
    )


@router.get("/analysis-result/{result_id}", response_model=AnalysisResultResponse)
async def get_analysis_result(result_id: str, db: DbSession) -> AnalysisResultResponse:
    """Get a specific analysis result by ID.

    Args:
        result_id (str): Unique identifier for the analysis result.
        db (DbSession): Database session dependency.

    Returns:
        AnalysisResultResponse: Complete analysis result information.

    Raises:
        HTTPException: If the result ID is not found.

    Example:
        GET /scrapper/analysis-result/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        result_uuid = uuid.UUID(result_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid result ID format")

    analysis_result = await db.get(AnalysisResult, result_uuid)
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    return AnalysisResultResponse(
        id=str(analysis_result.id),
        url=analysis_result.url,
        analysis_type=analysis_result.analysis_type,
        summary=analysis_result.summary,
        keywords=analysis_result.keywords,
        categories=analysis_result.categories,
        sentiment_score=analysis_result.sentiment_score,
        confidence_score=analysis_result.confidence_score,
        extra_data=analysis_result.extra_data,
        created_at=analysis_result.created_at.isoformat(),
    )


@router.get("/analysis-results", response_model=AnalysisResultListResponse)
async def list_analysis_results(
    db: DbSession,
    analysis_type: str | None = Query(None, description="Filter by analysis type"),
    url: str | None = Query(None, description="Filter by URL"),
    limit: int = Query(
        50, description="Maximum number of results to return", ge=1, le=100
    ),
    offset: int = Query(0, description="Number of results to skip", ge=0),
) -> AnalysisResultListResponse:
    """List analysis results with optional filtering and pagination.

    Args:
        db (DbSession): Database session dependency.
        analysis_type (str | None): Optional analysis type filter.
        url (str | None): Optional URL filter.
        limit (int): Maximum number of results to return.
        offset (int): Number of results to skip for pagination.

    Returns:
        AnalysisResultListResponse: List of analysis results matching criteria.
    """
    # Build query with optional filters
    query = select(AnalysisResult)

    if analysis_type is not None:
        query = query.where(AnalysisResult.analysis_type == analysis_type)

    if url is not None:
        query = query.where(AnalysisResult.url == url)

    query = query.order_by(desc(AnalysisResult.created_at)).offset(offset).limit(limit)

    result = await db.exec(query)
    analysis_results = result.all()

    # Convert to response format
    result_responses = []
    for analysis_result in analysis_results:
        result_responses.append(
            AnalysisResultResponse(
                id=str(analysis_result.id),
                url=analysis_result.url,
                analysis_type=analysis_result.analysis_type,
                summary=analysis_result.summary,
                keywords=analysis_result.keywords,
                categories=analysis_result.categories,
                sentiment_score=analysis_result.sentiment_score,
                confidence_score=analysis_result.confidence_score,
                extra_data=analysis_result.extra_data,
                created_at=analysis_result.created_at.isoformat(),
            )
        )

    return AnalysisResultListResponse(
        results=result_responses, total_results=len(analysis_results)
    )


@router.delete("/analysis-result/{result_id}")
async def delete_analysis_result(result_id: str, db: DbSession) -> dict[str, str]:
    """Delete an analysis result.

    Args:
        result_id (str): Unique identifier for the analysis result.
        db (DbSession): Database session dependency.

    Returns:
        Dict[str, str]: Confirmation message.

    Raises:
        HTTPException: If the result ID is not found.
    """
    try:
        result_uuid = uuid.UUID(result_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid result ID format")

    analysis_result = await db.get(AnalysisResult, result_uuid)
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    await db.delete(analysis_result)
    await db.commit()

    return {"message": f"Analysis result {result_id} deleted successfully"}
