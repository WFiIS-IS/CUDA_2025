"""
HuggingFace Transformers implementation for LLM operations.

Simple implementation using HuggingFace Transformers library.
"""

import asyncio
import logging
from typing import Any

from .llm_models import (
    get_sentiment_model,
    get_summarization_model,
    get_topic_classification_model,
)

logger = logging.getLogger(__name__)


class HuggingFaceLLM:
    """HuggingFace Transformers implementation."""

    def __init__(self) -> None:
        """Initialize HuggingFace LLM."""
        self.max_text_length = 512

    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Analyze sentiment using HuggingFace DistilBERT model."""
        if not text.strip():
            return {"label": "NEUTRAL", "score": 0.0}

        # Truncate text for performance
        truncated_text = text[: self.max_text_length]

        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()

        try:
            pipeline = get_sentiment_model()
            result = await loop.run_in_executor(None, lambda: pipeline(truncated_text))

            if result and len(result) > 0:
                return result[0]
            else:
                return {"label": "NEUTRAL", "score": 0.0}

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.0}

    async def summarize_text(
        self, text: str, max_length: int = 130, min_length: int = 30
    ) -> dict[str, Any]:
        """Generate text summary using HuggingFace DistilBART model."""
        # Use longer text limit for summarization
        truncated_text = text[:1024]

        loop = asyncio.get_event_loop()

        try:
            pipeline = get_summarization_model()
            result = await loop.run_in_executor(
                None,
                lambda: pipeline(
                    truncated_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                ),
            )

            if result and len(result) > 0:
                return result[0]
            else:
                return {"summary_text": ""}

        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return {"summary_text": ""}

    async def classify_topics(
        self, text: str, candidate_labels: list[str] | None = None
    ) -> dict[str, Any]:
        """Classify text topics using HuggingFace BART-MNLI model."""
        if candidate_labels is None:
            candidate_labels = [
                "technology",
                "health",
                "finance",
                "education",
                "sports",
                "politics",
                "entertainment",
            ]

        truncated_text = text[: self.max_text_length]

        loop = asyncio.get_event_loop()

        try:
            pipeline = get_topic_classification_model()
            result = await loop.run_in_executor(
                None, lambda: pipeline(truncated_text, candidate_labels)
            )

            return result

        except Exception as e:
            logger.error(f"Topic classification failed: {e}")
            return {"sequence": truncated_text, "labels": [], "scores": []}


# Legacy compatibility functions for backward compatibility
async def analyze_sentiment(text: str) -> Any:
    """Legacy function for backward compatibility."""
    llm = HuggingFaceLLM()
    return await llm.analyze_sentiment(text)


class NLPLayer:
    """Legacy NLP layer for backward compatibility."""

    def __init__(self, text: str) -> None:
        """Initialize the NLP layer with text content."""
        self.text = text
        self._llm = HuggingFaceLLM()

    async def sentiment(self) -> Any:
        """Analyze sentiment of the text content."""
        return await self._llm.analyze_sentiment(self.text)

    async def summarize(self) -> Any:
        """Generate a summary of the text content."""
        result = await self._llm.summarize_text(self.text)
        return [result]

    async def topic_model(self, candidate_labels: list[str] | None = None) -> Any:
        """Classify the text content into topic categories."""
        return await self._llm.classify_topics(self.text, candidate_labels)
