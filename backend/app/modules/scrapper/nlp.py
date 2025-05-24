from transformers import pipeline

# Load sentiment-analysis pipeline (this will download the model on first run)
sentiment_analyzer = pipeline('sentiment-analysis')
ner_pipeline = pipeline('ner', grouped_entities=True)
summarizer = pipeline('summarization')
topic_modeler = pipeline('zero-shot-classification')

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
        return summarizer(self.text[:1024], max_length=130, min_length=30, do_sample=False)

    def topic_model(self, candidate_labels=None):
        if candidate_labels is None:
            candidate_labels = ["technology", "health", "finance", "education", "sports", "politics", "entertainment"]
        return topic_modeler(self.text[:512], candidate_labels)
