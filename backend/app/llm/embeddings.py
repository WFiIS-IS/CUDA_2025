"""
Content embedding functionality using sentence transformers.

This module provides functionality to create and manage content embeddings
for semantic search capabilities.
"""

import asyncio
import hashlib
import logging
from typing import Any

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Global model instance for reuse
_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """Get or create the sentence transformer model."""
    global _embedding_model
    if _embedding_model is None:
        # Using all-MiniLM-L6-v2 which produces 384-dimensional embeddings
        # This is a good balance between quality and speed
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


class EmbeddingLayer:
    """Handle content embedding operations."""

    def __init__(self, content: str) -> None:
        """Initialize with content to embed.

        Args:
            content: The text content to create embeddings for
        """
        self.content = content
        self.content_hash = self._generate_content_hash()
        self.content_preview = content[:500] if content else ""

    def _generate_content_hash(self) -> str:
        """Generate SHA-256 hash of content for deduplication."""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    async def create_embedding(self) -> list[float]:
        """Create embedding vector for the content.

        Returns:
            List of float values representing the content embedding
        """
        if not self.content.strip():
            # Return zero vector for empty content
            return [0.0] * 384

        # Truncate content to reasonable length for embedding
        # Most sentence transformers work best with shorter texts
        truncated_content = self.content[:8192]  # Keep reasonable limit

        loop = asyncio.get_event_loop()

        try:
            model = get_embedding_model()
            # Run embedding creation in thread pool to avoid blocking
            embedding = await loop.run_in_executor(
                None, lambda: model.encode(truncated_content, convert_to_tensor=False)
            )

            # Convert numpy array to list of floats
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            # Return zero vector on error
            return [0.0] * 384

    def get_content_hash(self) -> str:
        """Get the SHA-256 hash of the content."""
        return self.content_hash

    def get_content_preview(self) -> str:
        """Get preview of the content (first 500 characters)."""
        return self.content_preview
