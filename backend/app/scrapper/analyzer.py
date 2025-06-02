from typing import Any

from bs4 import BeautifulSoup

from app.scrapper.content_extractor import ContentExtractor
from app.scrapper.metadata_analyzer import MetadataAnalyzer


class ScrapperAnalyzer:
    """Orchestrates the complete content analysis pipeline.

    This class integrates content extraction, NLP analysis, and metadata processing
    to provide comprehensive insights about web content. It combines multiple analysis
    components to generate tags and structured information from HTML content.

    Attributes:
        soup (BeautifulSoup): Parsed HTML content to analyze.

    Example:
        ```python
        analyzer = ScrapperAnalyzer(soup)
        results = await analyzer.analyze()
        print(f"Sentiment: {results['sentiment']}")
        print(f"Tags: {results['tags']}")
        ```
    """

    def __init__(self, soup: BeautifulSoup) -> None:
        """Initialize the analyzer with parsed HTML content.

        Args:
            soup (BeautifulSoup): Parsed HTML content from a web page.
                                 Should be created using BeautifulSoup with
                                 properly rendered HTML content.
        """
        self.soup = soup

    async def analyze(self) -> dict[str, Any]:
        """Run the complete content analysis pipeline.

        This method orchestrates all analysis components to extract and process
        web content. It performs content extraction, NLP analysis, metadata
        processing, and tag generation in a coordinated pipeline.

        Returns:
            dict[str, Any]: Comprehensive analysis results containing:
                - sentiment (dict): Sentiment analysis with label and score
                - summary (list): Generated text summaries
                - topics (dict): Topic classification with labels and scores
                - ner (list): Named entity recognition results
                - meta (dict): Metadata including SEO tags and structured data
                - tags (list): Combined tags from all analysis sources

        Raises:
            Exception: If any analysis component fails or if the soup is invalid.

        Note:
            The analysis pipeline includes:
            1. Content extraction (text, headers, links, media)
            2. NLP processing (sentiment, NER, summarization, topics)
            3. Metadata analysis (SEO, Open Graph, Twitter Cards, Schema.org)
            4. Tag generation from multiple sources
        """
        from app.scrapper.nlp import NLPLayer

        # 1. Content Extraction
        extractor = ContentExtractor(self.soup)
        content: dict[str, Any] = extractor.extract()
        main_text: str = content["main_text"]

        # 2. NLP Layer - AI-powered text analysis
        nlp = NLPLayer(main_text)
        sentiment: Any = await nlp.sentiment()
        ner: Any = await nlp.ner()
        summary: Any = await nlp.summarize()
        topics: Any = await nlp.topic_model()

        # 3. Metadata Analyzer - SEO and structured data
        meta: dict[str, Any] = MetadataAnalyzer(self.soup).extract()

        # 4. Tag Generation - Combine insights from all sources
        tags: set[str] = set()

        # Extract tags from topic classification
        if isinstance(topics, dict) and "labels" in topics:
            labels: Any = topics["labels"]
            if isinstance(labels, list):
                tags.update(str(label) for label in labels)  # type: ignore

        # Extract entity words from NER results
        if isinstance(ner, list):
            entity_words = [
                str(ent.get("word", ""))  # type: ignore
                for ent in ner  # type: ignore
                if isinstance(ent, dict)
                and ent.get("entity_group") in ["PER", "ORG", "LOC"]  # type: ignore
            ]
            tags.update(entity_words)

        # Extract keywords from metadata
        if meta.get("keywords"):
            keywords_str = str(meta["keywords"])
            keywords_list = [kw.strip() for kw in keywords_str.split(",")]
            tags.update(keywords_list)

        # 5. Return comprehensive analysis results
        return {
            "sentiment": sentiment,
            "summary": summary,
            "topics": topics,
            "ner": ner,
            "meta": meta,
            "tags": list(tags),
        }
