"""Task management functions for job processing."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlmodel import select

from app.db import get_async_session
from app.models import AnalysisResult, Job, JobStatus

from ..scrapper.models import AnalysisResults
from ..scrapper.scrape_url_cli import process_url

# Task timeout in seconds (10 minutes)
TASK_TIMEOUT_SECONDS = 600


async def cleanup_orphaned_tasks() -> None:
    """Clean up tasks that are stuck in PROCESSING state from previous app runs."""
    async for session in get_async_session():
        try:
            # Find tasks that have been processing for more than timeout duration
            timeout_threshold = datetime.now(UTC) - timedelta(
                seconds=TASK_TIMEOUT_SECONDS
            )

            query = select(Job).where(
                Job.status == JobStatus.PROCESSING, Job.created_at < timeout_threshold
            )
            result = await session.exec(query)
            orphaned_tasks = result.all()

            for task in orphaned_tasks:
                print(f"🧹 Cleaning up orphaned task {task.id} for URL: {task.url}")
                task.status = JobStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.error_message = "Task timed out or app was restarted"
                session.add(task)

            if orphaned_tasks:
                await session.commit()
                print(f"✅ Cleaned up {len(orphaned_tasks)} orphaned tasks")
            else:
                print("✅ No orphaned tasks found")

        except Exception as e:
            print(f"❌ Error cleaning up orphaned tasks: {e}")
        break  # Only use first session from generator


async def process_scraping_task(task_id: str, url: str) -> None:
    """Background task to process URL scraping with timeout.

    Args:
        task_id (str): Unique identifier for the scraping task.
        url (str): The URL to scrape and analyze.
    """
    async for session in get_async_session():
        try:
            # Get the task from database
            task = await session.get(Job, uuid.UUID(task_id))
            if not task:
                print(f"❌ Task {task_id} not found in database")
                return

            print(f"🚀 Starting task {task_id} for URL: {url}")

            # Update task status to processing
            task.status = JobStatus.PROCESSING
            session.add(task)
            await session.commit()
            print(f"⏳ Task {task_id} status updated to PROCESSING")

            # Run URL processing with timeout
            print(
                f"🤖 Running analysis for task {task_id} (timeout: {TASK_TIMEOUT_SECONDS}s)"
            )

            try:
                results = await asyncio.wait_for(
                    process_url(url), timeout=TASK_TIMEOUT_SECONDS
                )
                print(f"🧠 Analysis completed for task {task_id}")

                # Convert results using Pydantic for validation and numpy type conversion
                analysis_results = AnalysisResults(**results)
                serializable_results = analysis_results.model_dump()

                # Create AnalysisResult record
                analysis_result = AnalysisResult(
                    url=url,
                    analysis_type="web_scraping",
                    summary=serializable_results.get("summary", [{}])[0].get("text", "")
                    if serializable_results.get("summary")
                    else None,
                    keywords=serializable_results.get("tags", []),
                    categories=list(serializable_results.get("topics", {}).keys()),
                    sentiment_score=serializable_results.get("sentiment", {}).get(
                        "compound", None
                    ),
                    confidence_score=serializable_results.get("sentiment", {}).get(
                        "confidence", None
                    ),
                    extra_data={
                        "full_results": serializable_results,
                        "ner": serializable_results.get("ner", []),
                        "meta": serializable_results.get("meta", {}),
                    },
                )

                session.add(analysis_result)

                # Update task status to completed
                task.status = JobStatus.COMPLETED
                task.completed_at = datetime.now(UTC)
                session.add(task)

                await session.commit()
                print(
                    f"🎉 Task {task_id} completed successfully! Analysis saved to database."
                )

            except asyncio.TimeoutError:
                print(
                    f"⏰ Task {task_id} timed out after {TASK_TIMEOUT_SECONDS} seconds"
                )
                task.status = JobStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.error_message = (
                    f"Task timed out after {TASK_TIMEOUT_SECONDS} seconds"
                )
                session.add(task)
                await session.commit()
                print(f"❌ Task {task_id} marked as FAILED due to timeout")

        except Exception as e:
            print(f"💥 Task {task_id} failed with error: {str(e)}")
            # Update task with error information
            if task:
                task.status = JobStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.error_message = str(e)
                session.add(task)
                await session.commit()
                print(f"❌ Task {task_id} marked as FAILED in database")
        break  # Only use first session from generator
