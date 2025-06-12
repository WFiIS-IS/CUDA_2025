"""
Semantic search functionality using vector embeddings.

This module provides semantic search capabilities to find relevant content
based on vector similarity using pgvector.
"""

import asyncio
from typing import Any

from sqlalchemy import text, func
from sqlmodel import select

from app.db import get_async_session
from app.llm.embeddings import EmbeddingLayer
from app.models import ContentEmbedding


class SemanticSearch:
    """Handle semantic search operations using vector embeddings."""

    def __init__(self, query: str) -> None:
        """Initialize with search query.

        Args:
            query: The search query string
        """
        self.query = query

    async def search(
        self, limit: int = 10, similarity_threshold: float = 0.5
    ) -> list[dict[str, Any]]:
        """Search for semantically similar content.

        Args:
            limit: Maximum number of results to return
            similarity_threshold: Minimum cosine similarity threshold (0-1)

        Returns:
            List of dictionaries containing search results with similarity scores
        """
        if not self.query.strip():
            return []

        # Create embedding for the search query
        embedding_layer = EmbeddingLayer(self.query)
        query_embedding = await embedding_layer.create_embedding()

        async for session in get_async_session():
            computed_column = ContentEmbedding.embedding.cosine_distance(query_embedding)
            
            search_sql_query = select(ContentEmbedding).where(computed_column >= similarity_threshold).order_by(computed_column.asc()).limit(limit)
            
            result = await session.exec(search_sql_query)

            return [row.url for row in result]


    async def find_similar_content(
        self, url: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Find content similar to a given URL.

        Args:
            url: The URL to find similar content for
            limit: Maximum number of results to return

        Returns:
            List of similar content entries
        """
        async for session in get_async_session():
            try:
                # Get the embedding for the given URL
                query = select(ContentEmbedding).where(ContentEmbedding.url == url)
                result = await session.exec(query)
                source_embedding = result.first()

                if not source_embedding:
                    print(f"🔍 No embedding found for URL: {url}")
                    return []

                # Convert vector to string format for pgvector
                vector_str = f"[{','.join(map(str, source_embedding.embedding))}]"

                # Find similar content using the embedding
                similarity_query = text("""
                    SELECT 
                        id,
                        url,
                        content_hash,
                        content_preview,
                        created_at,
                        1 - (embedding <=> $1::vector) AS similarity
                    FROM content_embedding
                    WHERE url != $2
                    ORDER BY embedding <=> $1::vector
                    LIMIT :limit
                """)

                result = await session.execute(
                    similarity_query,
                    [
                        vector_str,
                        url,
                        limit,
                    ]
                )

                similar_results = []
                for row in result:
                    similar_results.append(
                        {
                            "id": str(row.id),
                            "url": row.url,
                            "content_hash": row.content_hash,
                            "content_preview": row.content_preview,
                            "similarity": float(row.similarity),
                            "created_at": row.created_at.isoformat()
                            if row.created_at
                            else None,
                        }
                    )

                return similar_results

            except Exception as e:
                print(f"❌ Error finding similar content for URL {url}: {e}")
                return []
            break  # Only use first session from generator
