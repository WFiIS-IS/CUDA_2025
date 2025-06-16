"""Job management functions for scrapper module."""

import asyncio
import json
import uuid
from typing import Any
from datetime import UTC, datetime, timedelta

from sqlmodel import col, select

from app.db import get_async_session
from app.llm.nlp import NLPLayer
from app.models import Bookmark, BookmarkAISuggestion, Collection, Job, JobStatus
from app.schemas import AnalysisResults

from app.scrapper.content_extractor import ContentExtractor
from app.scrapper.scrapper import Scrapper

from app.llm.embeddings import EmbeddingLayer
from app.models import ContentEmbedding
from sqlmodel import select

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


async def process_url(task_id: str, url: str) -> None:
    """Background task to process URL scraping with timeout.

    Args:
        task_id (str): Unique identifier for the processing task.
        url (str): The URL to process.
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
                collections = await session.exec(select(Collection))
                collections = collections.all()

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

                collection = await session.exec(
                    select(Collection).where(
                        Collection.name == analysis_results.collection
                    )
                )
                collection = collection.first()

                if not collection:
                    print(f"❌ Collection '{analysis_results.collection}' not found. Assigning None.")
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
        break  # Only use first session from generator


async def _process_url(url: str, collections: list[Collection]) -> dict[str, Any]:
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

    collections = [collection.name for collection in collections]

    nlp = NLPLayer(content)
    summary = await nlp.summarize()
    collection = await nlp.collection(collections)
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

    async for session in get_async_session():
        # Check if embedding already exists for this content
        existing_query = select(ContentEmbedding).where(
            ContentEmbedding.content_hash == content_hash,
            ContentEmbedding.url == url,
        )
        existing_embedding = await session.exec(existing_query)
        existing_embedding = existing_embedding.first()

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

        break  # Only use first session from generator
