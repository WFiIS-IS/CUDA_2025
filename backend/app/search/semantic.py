"""
Semantic search functionality using vector embeddings.

This module provides semantic search capabilities to find relevant content
based on vector similarity using pgvector.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.db import DbSessionDep
from app.llm.embeddings import EmbeddingLayer
from app.models import ContentEmbedding


class SemanticSearch:
    """Handle semantic search operations using vector embeddings."""

    def __init__(self, session: DbSessionDep) -> None:
        """Initialize with search query.

        Args:
            query: The search query string
        """
        self.session = session

    async def search(
        self, query: str, limit: int = 10, similarity_threshold: float = 0.8
    ):
        """Search for semantically similar content.

        Args:
            limit: Maximum number of results to return
            similarity_threshold: Minimum cosine similarity threshold (0-1)

        Returns:
            List of dictionaries containing search results with similarity scores
        """
        if not query.strip():
            return []

        # Create embedding for the search query
        embedding_layer = EmbeddingLayer(query)
        query_embedding = await embedding_layer.create_embedding()

        search_sql_query = (
            select(
                ContentEmbedding,
                ContentEmbedding.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .filter(
                ContentEmbedding.embedding.cosine_distance(query_embedding)
                < similarity_threshold
            )
            .order_by("distance")
            .limit(limit)
        )

        result = await self.session.execute(search_sql_query)
        result = result.scalars().all()

        return [row.url for row in result]


SemanticSearchDep = Annotated[SemanticSearch, Depends(SemanticSearch)]
