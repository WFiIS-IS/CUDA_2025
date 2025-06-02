"""Search router for vector similarity search using embeddings."""

import random
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import select

from app.db import DbSession
from app.models import AnalysisResult, EmbeddingResult

# Create the router instance
router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    """Request model for vector search."""

    query: str
    limit: int = 10


class SearchResult(BaseModel):
    """Individual search result with similarity score."""

    embedding_id: str
    url: str
    similarity_score: float
    text_chunks: list[str] | None = None
    chunk_metadata: list[dict[str, Any]] | None = None
    analysis_summary: str | None = None
    analysis_keywords: list[str] | None = None
    created_at: str


class SearchResponse(BaseModel):
    """Response model for vector search results."""

    query: str
    results: list[SearchResult]
    total_results: int


class EmbeddingResultResponse(BaseModel):
    """Response model for embedding result."""

    id: str
    url: str
    embedding_dimension: int
    text_chunks: list[str] | None = None
    chunk_metadata: list[dict[str, Any]] | None = None
    extra_data: dict[str, Any] | None = None
    created_at: str


class EmbeddingResultListResponse(BaseModel):
    """Response model for embedding results list."""

    results: list[EmbeddingResultResponse]
    total_results: int


async def create_query_embedding(query_text: str) -> list[float]:
    """Create embedding vector for query text.

    TODO: Replace with actual embedding model (OpenAI, HuggingFace, etc.)
    This should use the same embedding model used for document embeddings.

    Args:
        query_text: Text to create embedding for

    Returns:
        1536-dimensional embedding vector
    """
    # For now, create a dummy embedding
    # In production, this should use the same embedding service as the documents
    embedding = [random.uniform(-1, 1) for _ in range(1536)]
    return embedding


@router.post("/vector", response_model=SearchResponse)
async def vector_search(
    search_request: SearchRequest,
    db: DbSession,
) -> SearchResponse:
    """Perform vector similarity search on embeddings.

    This endpoint creates an embedding for the query text and finds the most
    similar document embeddings using cosine similarity.

    Args:
        search_request: Search parameters including query text and limit
        db: Database session dependency

    Returns:
        SearchResponse: List of most similar documents with similarity scores

    Example:
        POST /search/vector
        {
            "query": "artificial intelligence trends",
            "limit": 5
        }
    """
    # Create embedding for query text
    query_embedding = await create_query_embedding(search_request.query)

    # Convert to string format for SQL query
    query_vector_str = "[" + ",".join(map(str, query_embedding)) + "]"

    # Perform vector similarity search using pgvector
    # Using cosine distance operator (<->) for similarity
    similarity_query = text("""
        SELECT 
            er.id,
            er.url,
            er.text_chunks,
            er.chunk_metadata,
            er.extra_data,
            er.created_at,
            (er.embedding <-> :query_vector) as distance
        FROM embedding_result er
        ORDER BY er.embedding <-> :query_vector
        LIMIT :limit
    """)

    # Execute raw SQL query with parameters
    result = await db.execute(
        similarity_query,
        {"query_vector": query_vector_str, "limit": search_request.limit},
    )

    raw_results = result.fetchall()

    # Fetch corresponding analysis results for additional context
    search_results = []
    for row in raw_results:
        # Get analysis result for additional context
        analysis_query = select(AnalysisResult).where(AnalysisResult.url == row.url)
        analysis_result = await db.exec(analysis_query)
        analysis_record = analysis_result.first()

        # Convert distance to similarity score (1 - distance for cosine)
        # Note: Cosine distance ranges from 0 (identical) to 2 (opposite)
        similarity_score = max(0, 1 - (row.distance / 2))

        search_results.append(
            SearchResult(
                embedding_id=str(row.id),
                url=row.url,
                similarity_score=round(similarity_score, 4),
                text_chunks=row.text_chunks,
                chunk_metadata=row.chunk_metadata,
                analysis_summary=analysis_record.summary if analysis_record else None,
                analysis_keywords=analysis_record.keywords if analysis_record else None,
                created_at=row.created_at.isoformat(),
            )
        )

    return SearchResponse(
        query=search_request.query,
        results=search_results,
        total_results=len(search_results),
    )


@router.get("/similar/{embedding_id}", response_model=SearchResponse)
async def find_similar_embeddings(
    embedding_id: str,
    db: DbSession,
    limit: int = Query(
        10, description="Maximum number of similar results to return", ge=1, le=50
    ),
) -> SearchResponse:
    """Find embeddings similar to a specific embedding by ID.

    Args:
        embedding_id: ID of the embedding to find similar items for
        db: Database session dependency
        limit: Maximum number of results to return

    Returns:
        SearchResponse: List of most similar embeddings

    Example:
        GET /search/similar/123e4567-e89b-12d3-a456-426614174000?limit=5
    """
    # Get the source embedding
    source_embedding = await db.get(EmbeddingResult, embedding_id)
    if not source_embedding:
        raise HTTPException(status_code=404, detail="Embedding not found")

    # Convert embedding to string format for SQL query
    source_vector_str = "[" + ",".join(map(str, source_embedding.embedding)) + "]"

    # Find similar embeddings (excluding the source embedding itself)
    similarity_query = text("""
        SELECT 
            er.id,
            er.url,
            er.text_chunks,
            er.chunk_metadata,
            er.extra_data,
            er.created_at,
            (er.embedding <-> :source_vector) as distance
        FROM embedding_result er
        WHERE er.id != :source_id
        ORDER BY er.embedding <-> :source_vector
        LIMIT :limit
    """)

    # Execute raw SQL query with parameters
    result = await db.execute(
        similarity_query,
        {"source_vector": source_vector_str, "source_id": embedding_id, "limit": limit},
    )

    raw_results = result.fetchall()

    # Process results similar to vector_search
    search_results = []
    for row in raw_results:
        # Get analysis result for additional context
        analysis_query = select(AnalysisResult).where(AnalysisResult.url == row.url)
        analysis_result = await db.exec(analysis_query)
        analysis_record = analysis_result.first()

        # Convert distance to similarity score
        similarity_score = max(0, 1 - (row.distance / 2))

        search_results.append(
            SearchResult(
                embedding_id=str(row.id),
                url=row.url,
                similarity_score=round(similarity_score, 4),
                text_chunks=row.text_chunks,
                chunk_metadata=row.chunk_metadata,
                analysis_summary=analysis_record.summary if analysis_record else None,
                analysis_keywords=analysis_record.keywords if analysis_record else None,
                created_at=row.created_at.isoformat(),
            )
        )

    return SearchResponse(
        query=f"Similar to embedding {embedding_id}",
        results=search_results,
        total_results=len(search_results),
    )


@router.get("/embedding/{embedding_id}", response_model=EmbeddingResultResponse)
async def get_embedding_result(
    embedding_id: str, db: DbSession
) -> EmbeddingResultResponse:
    """Get a specific embedding result by ID.

    Args:
        embedding_id (str): Unique identifier for the embedding result.
        db (DbSession): Database session dependency.

    Returns:
        EmbeddingResultResponse: Complete embedding result information.

    Raises:
        HTTPException: If the embedding ID is not found.

    Example:
        GET /search/embedding/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        result_uuid = uuid.UUID(embedding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid embedding ID format")

    embedding_result = await db.get(EmbeddingResult, result_uuid)
    if not embedding_result:
        raise HTTPException(status_code=404, detail="Embedding result not found")

    return EmbeddingResultResponse(
        id=str(embedding_result.id),
        url=embedding_result.url,
        embedding_dimension=len(embedding_result.embedding)
        if embedding_result.embedding is not None
        else 0,
        text_chunks=embedding_result.text_chunks,
        chunk_metadata=embedding_result.chunk_metadata,
        extra_data=embedding_result.extra_data,
        created_at=embedding_result.created_at.isoformat(),
    )


@router.delete("/embedding/{embedding_id}")
async def delete_embedding_result(embedding_id: str, db: DbSession) -> dict[str, str]:
    """Delete an embedding result.

    Args:
        embedding_id (str): Unique identifier for the embedding result.
        db (DbSession): Database session dependency.

    Returns:
        Dict[str, str]: Confirmation message.

    Raises:
        HTTPException: If the embedding ID is not found.
    """
    try:
        result_uuid = uuid.UUID(embedding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid embedding ID format")

    embedding_result = await db.get(EmbeddingResult, result_uuid)
    if not embedding_result:
        raise HTTPException(status_code=404, detail="Embedding result not found")

    await db.delete(embedding_result)
    await db.commit()

    return {"message": f"Embedding result {embedding_id} deleted successfully"}
