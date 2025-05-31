from typing import Any

from bs4 import BeautifulSoup


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

    def extract(self) -> dict[str, Any]:
        """Extract all content types from the HTML document.

        This method performs comprehensive content extraction including text,
        headers, links, and media elements. It automatically cleans the content
        by removing scripts, styles, and other non-content elements.

        Returns:
            dict[str, Any]: Structured content containing:
                - main_text (str): Clean visible text content
                - headers (dict): Header hierarchy (h1-h6) with text content
                - links (list): All hyperlink URLs from anchor tags
                - images (list): All image source URLs
                - videos (list): All video source URLs

        Note:
            The extraction process:
            1. Removes scripts, styles, SVG, pictures, buttons, images, and links
            2. Extracts clean text with normalized whitespace
            3. Builds header hierarchy from h1-h6 tags
            4. Collects all valid hyperlinks and media sources
            5. Filters out None values and empty URLs
        """
        # Remove unwanted elements that don't contribute to content
        for tag in self.soup(
            ["script", "style", "svg", "picture", "button", "img", "link"]
        ):
            tag.decompose()

        # Extract clean main text content
        main_text = self.soup.get_text(separator=" ", strip=True)

        # Extract header hierarchy (h1 through h6)
        headers = {
            f"h{i}": [h.get_text(strip=True) for h in self.soup.find_all(f"h{i}")]
            for i in range(1, 7)
        }

        # Extract all hyperlinks, filtering out None values
        links = [
            a.get("href") for a in self.soup.find_all("a", href=True) if a.get("href")
        ]

        # Extract media sources (images and videos)
        images = [
            img.get("src")
            for img in self.soup.find_all("img", src=True)
            if img.get("src")
        ]
        videos = [
            video.get("src")
            for video in self.soup.find_all("video", src=True)
            if video.get("src")
        ]

        return {
            "main_text": main_text,
            "headers": headers,
            "links": links,
            "images": images,
            "videos": videos,
        }
