"""
LLM (Large Language Model) module for handling AI-powered text processing.

Simple module for LLM operations including:
- Sentiment analysis
- Text summarization
- Topic classification

Provides clean functions without unnecessary overhead.
"""

from .llm_models import (
    get_sentiment_model,
    get_summarization_model,
    get_topic_classification_model,
)
from .nlp import HuggingFaceLLM, NLPLayer, analyze_sentiment

__all__ = [
    # Model retrieval functions
    "get_sentiment_model",
    "get_summarization_model",
    "get_topic_classification_model",
    # Implementation
    "HuggingFaceLLM",
    # Legacy compatibility
    "NLPLayer",
    "analyze_sentiment",
]
