"""
HuggingFace Transformers implementation for LLM operations.

Simple implementation using HuggingFace Transformers library.
"""

import asyncio
import logging
from typing import Any

from sqlmodel import select

from app.db import get_async_session
from app.models import Tag

from .llm_models import (
    get_collection_model,
    get_sentiment_model,
    get_summarization_model,
    get_tags_model,
    get_title_model,
)

logger = logging.getLogger(__name__)


class NLPLayer:
    """Gemini implementation."""

    def __init__(self, text: str) -> None:
        """Initialize HuggingFace LLM."""
        self.max_text_length = 512
        self.text = text

    async def sentiment(self) -> dict[str, Any]:
        """Analyze sentiment using HuggingFace DistilBERT model."""
        if not self.text.strip():
            return {"label": "NEUTRAL", "score": 0.0}

        # Truncate text for performance
        truncated_text = self.text[: self.max_text_length]

        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()

        try:
            pipeline = get_sentiment_model()
            result = await loop.run_in_executor(None, lambda: pipeline(truncated_text))

            if result and len(result) > 0:
                return result
            else:
                return {"label": "NEUTRAL", "score": 0.0}

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.0}

    async def summarize(
        self, max_length: int = 130, min_length: int = 30
    ) -> dict[str, Any]:
        """Generate text summary using HuggingFace DistilBART model."""
        # Use longer text limit for summarization
        truncated_text = self.text[:1024]

        loop = asyncio.get_event_loop()

        pipeline = get_summarization_model()
        result = await loop.run_in_executor(
            None,
            lambda: pipeline(truncated_text),
        )

        return result

    async def collection(
        self, candidate_topics: list[str] | None = None
    ) -> dict[str, Any]:
        """Classify text topics using HuggingFace BART-MNLI model."""

        truncated_text = self.text[: self.max_text_length]

        loop = asyncio.get_event_loop()

        pipeline = get_collection_model(candidate_topics)
        result = await loop.run_in_executor(None, lambda: pipeline(truncated_text))

        return result

    async def title(self) -> str:
        """Generate a title for the given text."""

        truncated_text = self.text[:1024]

        loop = asyncio.get_event_loop()

        pipeline = get_title_model()
        result = await loop.run_in_executor(
            None,
            lambda: pipeline(truncated_text),
        )

        return result

    async def tags(self) -> list[str]:
        """
        Suggest tags for the given text using the collection model and all tags from the database.
        Uses async for session in get_async_session() for DB access. Does NOT use DbSession.
        """

        async for session in get_async_session():
            result = await session.exec(select(Tag.name))

            all_tags = list(result)
            truncated_text = self.text[: self.max_text_length]
            tags_model = get_tags_model(all_tags)
            # Use default arguments to bind variables in lambda
            loop = asyncio.get_event_loop()
            tags_result = await loop.run_in_executor(
                None,
                lambda tags_model=tags_model, truncated_text=truncated_text: tags_model(truncated_text),
            )
            print(f"=====================Tags result: {tags_result}")
            return tags_result

        return []

