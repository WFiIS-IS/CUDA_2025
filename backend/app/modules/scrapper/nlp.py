from transformers import pipeline

# Explicitly specify model names for caching and reproducibility
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


def analyze_sentiment(text: str):
    """
    Analyze sentiment of the given text using HuggingFace Transformers.
    Returns a dictionary with label and score.
    """
    if not text.strip():
        return {"label": "NEUTRAL", "score": 0.0}
    result = sentiment_analyzer(text[:512])  # Limit to 512 chars for performance
    return result[0] if result else {"label": "NEUTRAL", "score": 0.0}


class NLPLayer:
    def __init__(self, text: str):
        self.text = text

    def sentiment(self):
        return analyze_sentiment(self.text)

    def ner(self):
        return ner_pipeline(self.text[:512])

    def summarize(self):
        return summarizer(
            self.text[:1024], max_length=130, min_length=30, do_sample=False
        )

    def topic_model(self, candidate_labels=None):
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
