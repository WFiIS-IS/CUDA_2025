"""Data models and utilities for scrapper module."""

from typing import Any

import numpy as np
from pydantic import BaseModel, field_serializer


def convert_numpy_types(obj: Any) -> Any:
    """Recursively convert numpy types to native Python types for JSON serialization.

    Args:
        obj: Object that may contain numpy types

    Returns:
        Object with numpy types converted to native Python types
    """
    if isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj


class AnalysisResults(BaseModel):
    """Pydantic model for analysis results with automatic type conversion."""

    sentiment: dict[str, Any]
    summary: list[dict[str, Any]]
    topics: dict[str, Any]
    ner: list[dict[str, Any]]
    meta: dict[str, Any]
    tags: list[str]

    @field_serializer("sentiment", "summary", "topics", "ner", "meta", "tags")
    def serialize_fields(self, value: Any) -> Any:
        """Custom serializer to handle numpy types."""
        return convert_numpy_types(value)


class ScrapingTask(BaseModel):
    """Response model for scraping task creation."""

    job_id: str
    status: str
    message: str
    created_at: str


class AnalysisResultResponse(BaseModel):
    """Response model for analysis result."""

    id: str
    url: str
    analysis_type: str
    summary: str | None = None
    keywords: list[str] | None = None
    categories: list[str] | None = None
    sentiment_score: float | None = None
    confidence_score: float | None = None
    extra_data: dict[str, Any] | None = None
    created_at: str


class AnalysisResultListResponse(BaseModel):
    """Response model for analysis results list."""

    results: list[AnalysisResultResponse]
    total_results: int
