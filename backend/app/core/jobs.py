"""Job management functions for scrapper module."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlmodel import select

from app.db import get_async_session
from app.models import Job, JobStatus
from app.schemas import AnalysisResults

from ..scrapper.scrape_url_cli import process_url

JOB_TIMEOUT_SECONDS = 600


async def cleanup_orphaned_jobs() -> None:
    """Clean up jobs that are stuck in PROCESSING state from previous app runs."""
    async for session in get_async_session():
        try:
            # Find jobs that have been processing for more than timeout duration
            timeout_threshold = datetime.now(UTC) - timedelta(
                seconds=JOB_TIMEOUT_SECONDS
            )

            query = select(Job).where(
                Job.status == JobStatus.PROCESSING, Job.created_at < timeout_threshold
            )
            result = await session.exec(query)
            orphaned_jobs = result.all()

            for job in orphaned_jobs:
                print(f"🧹 Cleaning up orphaned job {job.id} for URL: {job.url}")
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now(UTC)
                job.error_message = "Job timed out or app was restarted"
                session.add(job)

            if orphaned_jobs:
                await session.commit()
                print(f"✅ Cleaned up {len(orphaned_jobs)} orphaned jobs")
            else:
                print("✅ No orphaned jobs found")

        except Exception as e:
            print(f"❌ Error cleaning up orphaned jobs: {e}")
        break  # Only use first session from generator


async def process_scraping(task_id: str, url: str) -> None:
    """Background task to process URL scraping with timeout.

    Args:
        task_id (str): Unique identifier for the scraping task.
        url (str): The URL to scrape and analyze.
    """
    async for session in get_async_session():
        try:
            # Get the job from database
            job = await session.get(Job, uuid.UUID(task_id))
            if not job:
                print(f"❌ Job {task_id} not found in database")
                return

            print(f"🚀 Starting job {task_id} for URL: {url}")

            # Update job status to processing
            job.status = JobStatus.PROCESSING
            session.add(job)
            await session.commit()
            print(f"⏳ Job {task_id} status updated to PROCESSING")

            # Run URL processing with timeout
            print(
                f"🤖 Running analysis for job {task_id} (timeout: {JOB_TIMEOUT_SECONDS}s)"
            )

            try:
                results = await asyncio.wait_for(
                    process_url(url), timeout=JOB_TIMEOUT_SECONDS
                )
                print(f"🧠 Analysis completed for job {task_id}")

                # Convert results using Pydantic for validation and numpy type conversion
                analysis_results = AnalysisResults(**results)
                serializable_results = analysis_results.model_dump()

                # Update job with results
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now(UTC)
                job.results = serializable_results
                session.add(job)
                await session.commit()
                print(f"🎉 Job {task_id} completed successfully!")

            except asyncio.TimeoutError:
                print(f"⏰ Job {task_id} timed out after {JOB_TIMEOUT_SECONDS} seconds")
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now(UTC)
                job.error_message = f"Job timed out after {JOB_TIMEOUT_SECONDS} seconds"
                session.add(job)
                await session.commit()
                print(f"❌ Job {task_id} marked as FAILED due to timeout")

        except Exception as e:
            print(f"💥 Job {task_id} failed with error: {str(e)}")
            # Update job with error information
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now(UTC)
                job.error_message = str(e)
                session.add(job)
                await session.commit()
                print(f"❌ Job {task_id} marked as FAILED in database")
        break  # Only use first session from generator
