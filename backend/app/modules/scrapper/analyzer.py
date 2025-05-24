from .content_extractor import ContentExtractor
from .nlp import NLPLayer
from .metadata_analyzer import MetadataAnalyzer

class ScrapperAnalyzer:
    """
    Orchestrates the full pipeline: content extraction, NLP, metadata analysis, and tag extraction.
    """
    def __init__(self, soup):
        self.soup = soup

    async def analyze(self):
        # 1. Content Extraction
        extractor = ContentExtractor(self.soup)
        content = extractor.extract()
        main_text = content["main_text"]
        # 2. NLP Layer
        nlp = NLPLayer(main_text)
        sentiment = nlp.sentiment()
        ner = nlp.ner()
        summary = nlp.summarize()
        topics = nlp.topic_model()
        # 3. Metadata Analyzer
        meta = MetadataAnalyzer(self.soup).extract()
        # 4. Compose tags (topics, NER, meta keywords, etc.)
        tags = set()
        if isinstance(topics, dict) and "labels" in topics:
            tags.update(topics["labels"])
        if isinstance(ner, list):
            tags.update([ent["word"] for ent in ner if ent.get("entity_group") == "PER" or ent.get("entity_group") == "ORG" or ent.get("entity_group") == "LOC"])
        if meta.get("keywords"):
            tags.update(meta["keywords"].split(","))
        # 5. Return all results
        return {
            "sentiment": sentiment,
            "summary": summary,
            "topics": topics,
            "ner": ner,
            "meta": meta,
            "tags": list(tags)
        }
