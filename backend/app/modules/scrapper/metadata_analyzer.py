import json
from typing import Any

from bs4 import BeautifulSoup


class MetadataAnalyzer:
    """Extracts metadata and structured data from HTML documents.

    This class specializes in extracting various types of metadata including
    SEO tags, Open Graph protocol data, Twitter Cards, and Schema.org
    structured data. It provides comprehensive metadata analysis for web content.

    Attributes:
        soup (BeautifulSoup): The parsed HTML document to analyze for metadata.

    Example:
        ```python
        analyzer = MetadataAnalyzer(soup)
        metadata = analyzer.extract()
        print(f"Title: {metadata['title']}")
        print(f"Open Graph: {metadata['og']}")
        ```
    """

    def __init__(self, soup: BeautifulSoup) -> None:
        """Initialize the metadata analyzer with parsed HTML.

        Args:
            soup (BeautifulSoup): Parsed HTML document to extract metadata from.
                                 Should contain valid HTML with meta tags for
                                 optimal metadata extraction.
        """
        self.soup = soup

    def extract(self) -> dict[str, Any]:
        """Extract all types of metadata from the HTML document.

        This method performs comprehensive metadata extraction including SEO
        meta tags, Open Graph protocol data, Twitter Cards, and JSON-LD
        structured data following Schema.org standards.

        Returns:
            dict[str, Any]: Comprehensive metadata containing:
                - title (str|None): Page title from <title> tag
                - description (str|None): Meta description content
                - keywords (str|None): Meta keywords content
                - og (dict): Open Graph protocol data with og: prefixed properties
                - twitter (dict): Twitter Cards data with twitter: prefixed properties
                - schemas (list): Parsed JSON-LD structured data objects

        Note:
            The extraction process:
            1. Extracts basic SEO meta tags (title, description, keywords)
            2. Processes Open Graph meta properties (og:title, og:description, etc.)
            3. Extracts Twitter Cards meta properties (twitter:card, twitter:title, etc.)
            4. Parses JSON-LD script tags for Schema.org structured data
            5. Handles malformed JSON gracefully with error recovery
        """
        meta: dict[str, Any] = {}

        # Extract basic SEO meta tags
        meta["title"] = self.soup.title.string if self.soup.title else None

        # Extract meta description with safe attribute access
        description_tag = self.soup.find("meta", attrs={"name": "description"})
        meta["description"] = (
            description_tag.get("content") if description_tag else None
        )

        # Extract meta keywords with safe attribute access
        keywords_tag = self.soup.find("meta", attrs={"name": "keywords"})
        meta["keywords"] = keywords_tag.get("content") if keywords_tag else None

        # Extract Open Graph protocol data
        meta["og"] = {
            tag.get("property"): tag.get("content")
            for tag in self.soup.find_all("meta", property=True)
            if tag.get("property", "").startswith("og:")
        }

        # Extract Twitter Cards metadata
        meta["twitter"] = {
            tag.get("name"): tag.get("content")
            for tag in self.soup.find_all("meta", attrs={"name": True})
            if tag.get("name", "").startswith("twitter:")
        }

        # Extract Schema.org JSON-LD structured data
        schemas: list[dict[str, Any]] = []
        for script in self.soup.find_all("script", type="application/ld+json"):
            try:
                if script.string:
                    # Parse JSON-LD content and add to schemas list
                    schema_data = json.loads(script.string)
                    schemas.append(schema_data)
            except (json.JSONDecodeError, TypeError):
                # Skip malformed JSON-LD data and continue processing
                continue

        meta["schemas"] = schemas

        return meta
