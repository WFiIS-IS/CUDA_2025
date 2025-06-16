"""Job management functions for scrapper module."""

import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, field_serializer
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import get_db_session_manager
from app.llm.embeddings import EmbeddingLayer
from app.llm.nlp import NLPLayer
from app.models import (
    Bookmark,
    BookmarkAISuggestion,
    Collection,
    ContentEmbedding,
    Job,
    JobStatus,
)
from app.schemas.base import convert_numpy_types
from app.scrapper.content_extractor import ContentExtractor
from app.scrapper.scrapper import Scrapper

JOB_TIMEOUT_SECONDS = 600


class AnalysisResults(BaseModel):
    """Pydantic model for analysis results with automatic type conversion."""

    summary: str
    collection: str
    title: str
    tags: list[str]

    @field_serializer("summary", "collection", "title", "tags")
    def serialize_fields(self, value: Any) -> Any:
        """Custom serializer to handle numpy types."""
        return convert_numpy_types(value)


async def cleanup_orphaned_jobs() -> None:
    """Clean up jobs that are stuck in PROCESSING state from previous app runs."""
    session_manager = get_db_session_manager()
    async with session_manager.get_session() as session:
        try:
            # Find jobs that have been processing for more than timeout duration
            timeout_threshold = datetime.now(UTC) - timedelta(
                seconds=JOB_TIMEOUT_SECONDS
            )

            result = await session.execute(
                select(Job)
                .where(
                    Job.status == JobStatus.PROCESSING,
                    Job.created_at < timeout_threshold,
                )
                .options(
                    selectinload(Job.bookmark),
                )
            )
            orphaned_jobs = result.scalars().all()

            for job in orphaned_jobs:
                print(
                    f"🧹 Cleaning up orphaned job {job.id} for URL: {job.bookmark.url}"
                )
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


async def process_url(task_id: str, url: str) -> None:
    """Background task to process URL scraping with timeout.

    Args:
        task_id (str): Unique identifier for the processing task.
        url (str): The URL to process.
    """
    session_manager = get_db_session_manager()
    async with session_manager.get_session() as session:
        result = await session.execute(
            select(Job)
            .where(Job.id == task_id)
            .options(
                selectinload(Job.bookmark),
            )
        )
        job = result.scalar_one_or_none()
        try:
            # Get the job from database
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
                collections = await session.execute(select(Collection))
                collections = collections.scalars().all()

                results = await asyncio.wait_for(
                    _process_url(url, collections), timeout=JOB_TIMEOUT_SECONDS
                )
                print(f"🧠 Analysis completed for job {task_id}")

                # Convert results using Pydantic for validation and numpy type conversion
                analysis_results = AnalysisResults(**results)
                serializable_results = analysis_results.model_dump()

                print(f"📚 Update bookmark with results: {analysis_results}")

                bookmark = await session.get(Bookmark, job.bookmark_id)

                if not bookmark:
                    print(f"❌ Bookmark {job.bookmark_id} not found in database")
                    return

                collection = await session.execute(
                    select(Collection).where(
                        Collection.name == analysis_results.collection
                    )
                )
                collection = collection.scalars().first()

                if not collection:
                    print(
                        f"❌ Collection '{analysis_results.collection}' not found. Assigning None."
                    )
                    # Do not create a new collection, just assign None
                else:
                    print(f"📂 Using collection: {collection.name}")
                    # bookmark.collection_id = collection.id

                print(f"📖 Bookmark ID: {bookmark.id}")
                print(f"🔖 Bookmark URL: {bookmark.url}")
                print(f"📝 Bookmark Title: {analysis_results.title}")
                print(f"📄 Bookmark Description: {analysis_results.summary}")
                print(f"🏷️ Bookmark Tags: {analysis_results.tags}")
                # bookmark.collection_id = collection.id
                ai_suggestion = BookmarkAISuggestion(
                    title=analysis_results.title,
                    description=analysis_results.summary,
                    bookmark_id=job.bookmark_id,
                    collection_id=collection.id if collection else None,
                    tags=analysis_results.tags,
                )

                session.add(ai_suggestion)
                session.add(bookmark)
                await session.commit()
                await session.refresh(ai_suggestion)
                await session.refresh(bookmark)

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


async def _process_url(url: str, collections: Sequence[Collection]) -> dict[str, Any]:
    """Process a single URL through the complete analysis pipeline.

    This function handles the full scraping and analysis workflow for a given URL,
    including content fetching, parsing, and comprehensive AI-powered analysis.

    Args:
        url (str): The URL to scrape and analyze. Must be a valid HTTP/HTTPS URL.

    Returns:
        dict[str, Any]: Analysis results from ScrapperAnalyzer containing
                       sentiment, summary, topics, meta, and tags data.

    Raises:
        ValueError: If the scrapper fails to fetch content from the URL.
        Exception: If any part of the analysis pipeline fails.

    Note:
        The process includes:
        1. Initialize Scrapper with the URL
        2. Fetch and parse web content using Playwright
        3. Verify content was successfully retrieved
        4. Run complete analysis pipeline (NLP, metadata, content extraction)
        5. Return structured results for further processing
    """
    scrapper = Scrapper(url)
    await scrapper.fetch()

    # Ensure soup is not None after fetch
    if scrapper.soup is None:
        raise ValueError("Failed to fetch content from URL")

    content_extractor = ContentExtractor(scrapper.soup)
    content = content_extractor.extract()

    collection_names = [collection.name for collection in collections]

    nlp = NLPLayer(content)
    summary = await nlp.summarize()
    collection = await nlp.collection(collection_names)
    title = await nlp.title()
    tags = await nlp.tags()

    await _save_embedding(url, content)

    return {
        "summary": summary,
        "collection": collection,
        "title": title,
        "tags": tags,
    }


async def _save_embedding(url: str, content: str) -> list[float]:
    """Create an embedding for the given content and save it to the database.

    Args:
        url: The URL of the content
        content: The text content to embed

    Returns:
        The embedding vector as a list of floats
    """

    # Create embedding layer instance
    embedding_layer = EmbeddingLayer(content)
    content_hash = embedding_layer.get_content_hash()
    session_manager = get_db_session_manager()

    async with session_manager.get_session() as session:
        # Check if embedding already exists for this content
        existing_query = select(ContentEmbedding).where(
            ContentEmbedding.content_hash == content_hash,
            ContentEmbedding.url == url,
        )
        existing_embedding = await session.execute(existing_query)
        existing_embedding = existing_embedding.scalar_one_or_none()

        if existing_embedding:
            print(f"📊 Embedding already exists for URL: {url}")
            return existing_embedding.embedding

        # Create new embedding
        print(f"🤖 Creating embedding for URL: {url}")
        embedding_vector = await embedding_layer.create_embedding()

        # Save to database
        content_embedding = ContentEmbedding(
            url=url,
            content_hash=content_hash,
            content_preview=embedding_layer.get_content_preview(),
            embedding=embedding_vector,
        )

        session.add(content_embedding)
        await session.commit()

        print(f"💾 Embedding saved for URL: {url}")
        return embedding_vector
