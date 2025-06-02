"""Task management functions for job processing."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from sqlmodel import select

from app.db import get_async_session
from app.models import (
    AnalysisResult,
    EmbeddingResult,
    Job,
    JobCreate,
    JobStatus,
    JobType,
)

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


async def create_dummy_embeddings(text_chunks: list[str]) -> list[list[float]]:
    """Create dummy embeddings for text chunks.

    TODO: Replace with actual embedding model (OpenAI, HuggingFace, etc.)

    Args:
        text_chunks: List of text chunks to embed

    Returns:
        List of 1536-dimensional embedding vectors
    """
    import random

    embeddings = []
    for _ in text_chunks:
        # Create random 1536-dimensional vector (matching OpenAI embedding size)
        embedding = [random.uniform(-1, 1) for _ in range(1536)]
        embeddings.append(embedding)

    return embeddings


async def process_embedding_task(task_id: str, url: str) -> None:
    """Background task to create embeddings from analysis results.

    Args:
        task_id (str): Unique identifier for the embedding task.
        url (str): The URL to create embeddings for.
    """
    async for session in get_async_session():
        try:
            # Get the embedding task from database
            task = await session.get(Job, uuid.UUID(task_id))
            if not task:
                print(f"❌ Embedding task {task_id} not found in database")
                return

            print(f"🚀 Starting embedding task {task_id} for URL: {url}")

            # Update task status to processing
            task.status = JobStatus.PROCESSING
            session.add(task)
            await session.commit()
            print(f"⏳ Embedding task {task_id} status updated to PROCESSING")

            # Get the analysis result to create embeddings from
            analysis_query = select(AnalysisResult).where(AnalysisResult.url == url)
            analysis_result = await session.exec(analysis_query)
            analysis_record = analysis_result.first()

            if not analysis_record:
                task.status = JobStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.error_message = "No analysis result found for this URL"
                session.add(task)
                await session.commit()
                print(f"❌ Embedding task {task_id} failed: No analysis result found")
                return

            try:
                # Prepare text chunks for embedding
                text_chunks = []
                chunk_metadata = []

                # Add summary if available
                if analysis_record.summary:
                    text_chunks.append(analysis_record.summary)
                    chunk_metadata.append({"type": "summary", "source": "analysis"})

                # Add keywords as a combined chunk if available
                if analysis_record.keywords:
                    keywords_text = ", ".join(analysis_record.keywords)
                    text_chunks.append(keywords_text)
                    chunk_metadata.append({"type": "keywords", "source": "analysis"})

                # Add categories as a combined chunk if available
                if analysis_record.categories:
                    categories_text = ", ".join(analysis_record.categories)
                    text_chunks.append(categories_text)
                    chunk_metadata.append({"type": "categories", "source": "analysis"})

                # Extract additional text from extra_data if available
                if analysis_record.extra_data and isinstance(
                    analysis_record.extra_data, dict
                ):
                    full_results = analysis_record.extra_data.get("full_results", {})

                    # Add NER entities if available
                    ner_data = full_results.get("ner", [])
                    if ner_data:
                        entities_text = ", ".join(
                            [
                                entity.get("text", "")
                                for entity in ner_data
                                if entity.get("text")
                            ]
                        )
                        if entities_text:
                            text_chunks.append(entities_text)
                            chunk_metadata.append({"type": "entities", "source": "ner"})

                if not text_chunks:
                    task.status = JobStatus.FAILED
                    task.completed_at = datetime.now(UTC)
                    task.error_message = "No text content found to create embeddings"
                    session.add(task)
                    await session.commit()
                    print(f"❌ Embedding task {task_id} failed: No text content found")
                    return

                print(f"🤖 Creating embeddings for {len(text_chunks)} text chunks")

                # Create embeddings (using dummy function for now)
                embeddings = await create_dummy_embeddings(text_chunks)

                # For now, we'll store the first embedding as the main embedding
                # In a real implementation, you might want to average them or store multiple
                main_embedding = embeddings[0] if embeddings else []

                print(f"🧠 Embeddings created for task {task_id}")

                # Create EmbeddingResult record
                embedding_result = EmbeddingResult(
                    url=url,
                    embedding=main_embedding,
                    text_chunks=text_chunks,
                    chunk_metadata=chunk_metadata,
                    extra_data={
                        "embedding_count": len(embeddings),
                        "total_chunks": len(text_chunks),
                        "source_analysis_id": str(analysis_record.id),
                    },
                )

                session.add(embedding_result)

                # Update task status to completed
                task.status = JobStatus.COMPLETED
                task.completed_at = datetime.now(UTC)
                session.add(task)

                await session.commit()
                print(
                    f"🎉 Embedding task {task_id} completed successfully! Embeddings saved to database."
                )

            except Exception as e:
                print(f"💥 Embedding task {task_id} failed with error: {str(e)}")
                task.status = JobStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.error_message = str(e)
                session.add(task)
                await session.commit()

        except Exception as e:
            print(f"💥 Embedding task {task_id} failed with error: {str(e)}")
            # Update task with error information
            if task:
                task.status = JobStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.error_message = str(e)
                session.add(task)
                await session.commit()
                print(f"❌ Embedding task {task_id} marked as FAILED in database")
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

                # Create embedding job and start embedding task
                print(f"🔗 Creating embedding job for URL: {url}")
                embedding_job_create = JobCreate(url=url, type=JobType.EMBEDDING)
                embedding_job = Job.model_validate(embedding_job_create)

                session.add(embedding_job)
                await session.commit()
                await session.refresh(embedding_job)

                print(f"🚀 Starting embedding task {embedding_job.id}")
                # Start embedding task in background
                asyncio.create_task(process_embedding_task(str(embedding_job.id), url))

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
