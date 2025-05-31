from typing import Any

from transformers.pipelines import pipeline

# Initialize ML models with explicit model specifications for reproducibility
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)
ner_pipeline = pipeline(
    "ner",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    aggregation_strategy="simple",
)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
topic_modeler = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def analyze_sentiment(text: str) -> Any:
    """Analyze sentiment of text using HuggingFace Transformers.

    This function uses a pre-trained DistilBERT model to classify the sentiment
    of the input text as POSITIVE, NEGATIVE, or NEUTRAL with confidence scores.

    Args:
        text (str): The text to analyze for sentiment. Should be meaningful text
                   content for best results.

    Returns:
        Any: Sentiment analysis result containing:
            - label (str): "POSITIVE", "NEGATIVE", or "NEUTRAL"
            - score (float): Confidence score between 0 and 1

    Note:
        - Text is automatically truncated to 512 characters for performance
        - Empty or whitespace-only text returns neutral sentiment
        - Uses DistilBERT model optimized for English text

    Example:
        ```python
        result = analyze_sentiment("This is a great product!")
        print(f"Sentiment: {result['label']}, Score: {result['score']}")
        ```
    """
    if not text.strip():
        return {"label": "NEUTRAL", "score": 0.0}
    result = sentiment_analyzer(text[:512])  # Limit to 512 chars for performance
    return result[0] if result else {"label": "NEUTRAL", "score": 0.0}


class NLPLayer:
    """Natural Language Processing layer using HuggingFace Transformers.

    This class provides comprehensive NLP capabilities including sentiment analysis,
    named entity recognition, text summarization, and topic classification using
    state-of-the-art pre-trained models from HuggingFace.

    Attributes:
        text (str): The text content to process and analyze.

    Models Used:
        - Sentiment: distilbert-base-uncased-finetuned-sst-2-english (268MB)
        - NER: bert-large-cased-finetuned-conll03-english (1.33GB)
        - Summarization: sshleifer/distilbart-cnn-12-6 (1.22GB)
        - Topic Classification: facebook/bart-large-mnli (1.63GB)

    Example:
        ```python
        nlp = NLPLayer("Your text content here")
        sentiment = nlp.sentiment()
        entities = nlp.ner()
        summary = nlp.summarize()
        topics = nlp.topic_model()
        ```
    """

    def __init__(self, text: str) -> None:
        """Initialize the NLP layer with text content.

        Args:
            text (str): The text content to analyze. Should be meaningful text
                       for optimal analysis results across all NLP tasks.
        """
        self.text = text

    def sentiment(self) -> Any:
        """Analyze sentiment of the text content.

        Returns:
            Any: Sentiment analysis result with label and confidence score.
                 Format: {"label": "POSITIVE|NEGATIVE|NEUTRAL", "score": float}

        Note:
            Uses the same analysis function as analyze_sentiment() with
            automatic text truncation to 512 characters for performance.
        """
        return analyze_sentiment(self.text)

    def ner(self) -> Any:
        """Extract named entities from the text content.

        Identifies and classifies named entities in the text including persons (PER),
        organizations (ORG), locations (LOC), and miscellaneous entities (MISC).

        Returns:
            Any: List of named entity objects containing:
                - word (str): The identified entity text
                - entity_group (str): Entity type (PER, ORG, LOC, MISC)
                - confidence (float): Confidence score for the classification
                - start/end (int): Character positions in the text

        Note:
            - Text is truncated to 512 characters for performance
            - Uses BERT Large model with CoNLL-03 fine-tuning
            - Aggregation strategy "simple" groups subword tokens

        Example Result:
            ```python
            [
                {
                    "word": "Apple Inc.",
                    "entity_group": "ORG",
                    "confidence": 0.9998,
                    "start": 0,
                    "end": 10
                }
            ]
            ```
        """
        return ner_pipeline(self.text[:512])

    def summarize(self) -> Any:
        """Generate a summary of the text content.

        Creates a concise summary of the input text using a fine-tuned BART model
        optimized for summarization tasks.

        Returns:
            Any: Summarization result containing:
                - summary_text (str): The generated summary

        Note:
            - Text is truncated to 1024 characters for processing
            - Summary length: 30-130 tokens
            - Uses deterministic generation (do_sample=False)
            - DistilBART model optimized for CNN/DailyMail dataset

        Example Result:
            ```python
            [{"summary_text": "This article discusses..."}]
            ```
        """
        return summarizer(
            self.text[:1024], max_length=130, min_length=30, do_sample=False
        )

    def topic_model(self, candidate_labels: list[str] | None = None) -> Any:
        """Classify the text content into topic categories.

        Uses zero-shot classification to categorize the text into predefined
        or custom topic labels using a BART model fine-tuned on MNLI.

        Args:
            candidate_labels (Optional[list[str]]): Custom topic categories to classify into.
                                                   If None, uses default categories:
                                                   ["technology", "health", "finance", "education",
                                                    "sports", "politics", "entertainment"]

        Returns:
            Any: Topic classification result containing:
                - sequence (str): The input text (truncated)
                - labels (list[str]): Topic categories ranked by confidence
                - scores (list[float]): Confidence scores for each label

        Note:
            - Text is truncated to 512 characters for performance
            - Labels are ranked from highest to lowest confidence
            - Scores sum to approximately 1.0 across all labels

        Example Result:
            ```python
            {
                "sequence": "This article about AI...",
                "labels": ["technology", "education", "finance"],
                "scores": [0.8234, 0.1201, 0.0565]
            }
            ```
        """
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
        return topic_modeler(self.text[:512], candidate_labels)
