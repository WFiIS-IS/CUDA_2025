"""
Model configurations and retrieval functions for LLM operations.

This module centralizes all model names and provides functions to get
specific models for different NLP tasks.
"""

from transformers.pipelines import pipeline

# Model names for different tasks
SENTIMENT_MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
SUMMARIZATION_MODEL = "sshleifer/distilbart-cnn-12-6"
TOPIC_CLASSIFICATION_MODEL = "facebook/bart-large-mnli"

# Global model cache to avoid reloading
_model_cache = {}


def _get_or_create_pipeline(task: str, model: str, **kwargs):
    """Get a cached pipeline or create a new one."""
    cache_key = f"{task}:{model}"
    if cache_key not in _model_cache:
        _model_cache[cache_key] = pipeline(task, model=model, **kwargs)
    return _model_cache[cache_key]


def get_sentiment_model():
    """Get sentiment analysis model pipeline."""
    return _get_or_create_pipeline("sentiment-analysis", SENTIMENT_MODEL)


def get_summarization_model():
    """Get text summarization model pipeline."""
    return _get_or_create_pipeline("summarization", SUMMARIZATION_MODEL)


def get_topic_classification_model():
    """Get topic classification model pipeline."""
    return _get_or_create_pipeline(
        "zero-shot-classification", TOPIC_CLASSIFICATION_MODEL
    )
