from typing import Any

from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown


class ContentExtractor:
    """Extracts and structures content from HTML documents.

    This class processes BeautifulSoup parsed HTML to extract different types
    of content in a structured format. It handles text extraction, header
    hierarchy, links, and media elements while cleaning unwanted content.

    Attributes:
        soup (BeautifulSoup): The parsed HTML document to extract content from.

    Example:
        ```python
        extractor = ContentExtractor(soup)
        content = extractor.extract()
        print(f"Main text: {content['main_text']}")
        print(f"Headers: {content['headers']}")
        ```
    """

    def __init__(self, soup: BeautifulSoup) -> None:
        """Initialize the content extractor with parsed HTML.

        Args:
            soup (BeautifulSoup): Parsed HTML document to extract content from.
                                 Should contain valid HTML structure for optimal results.
        """
        self.soup = soup

    def extract(self) -> str:
        """
        Extract and return only the clean main text content from the HTML document as Markdown.
        Removes scripts, styles, SVG, pictures, buttons, images, and links before extracting text.
        Returns:
            str: Clean visible text content from the HTML document, converted to Markdown.
        """

        # Remove unwanted elements that don't contribute to content
        for tag in self.soup(
            ["script", "style", "svg", "picture", "button", "img", "link"]
        ):
            tag.decompose()

        # Convert the cleaned HTML to Markdown
        html = str(self.soup)
        markdown = convert_to_markdown(html)

        return markdown
