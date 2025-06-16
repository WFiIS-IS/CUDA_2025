from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Import playwright_stealth for stealth mode
from playwright_stealth import stealth_async

# Add imports for new modules


class Scrapper:
    """An asynchronous web scrapper with AI-powered content analysis.

    This class provides comprehensive web scraping capabilities using Playwright
    for JavaScript-rendered pages and BeautifulSoup for HTML parsing. It includes
    stealth features to avoid bot detection and supports full content analysis.

    Attributes:
        url (str): The target URL to scrape.
        soup (Optional[BeautifulSoup]): Parsed HTML content after fetching.

    Example:
        ```python
        scrapper = Scrapper("https://example.com")
        await scrapper.fetch()
        title = await scrapper.get_title()
        text = await scrapper.get_all_text()
        ```
    """

    def __init__(self, url: str) -> None:
        """Initialize the scrapper with a target URL.

        Args:
            url (str): The URL to scrape. Must be a valid HTTP/HTTPS URL.
        """
        self.url = url
        self.soup: BeautifulSoup | None = None

    async def fetch(self) -> BeautifulSoup:
        """Fetch and parse web content using Playwright with stealth mode.

        This method launches a headless Chromium browser with stealth settings,
        navigates to the target URL, waits for the page to fully load, and
        parses the rendered HTML with BeautifulSoup.

        Returns:
            BeautifulSoup: Parsed HTML content ready for analysis.

        Raises:
            Exception: If the page fails to load or parsing fails.

        Note:
            The method automatically applies stealth mode to avoid bot detection
            and waits for network idle state to ensure dynamic content is loaded.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="en-US",
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True,
                bypass_csp=True,
            )
            page = await context.new_page()
            await stealth_async(page)  # Apply stealth mode
            await page.goto(self.url)
            await page.wait_for_load_state("networkidle")
            html = await page.content()
            self.soup = BeautifulSoup(html, "html.parser")
            await browser.close()
        return self.soup

    async def get_title(self) -> str | None:
        """Extract the page title.

        Returns:
            Optional[str]: The page title if found, None otherwise.

        Note:
            Automatically calls fetch() if content hasn't been loaded yet.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup and self.soup.title:
            return self.soup.title.string
        return None

    async def get_links(self) -> list[str]:
        """Extract all hyperlinks from the page.

        Returns:
            list[str]: List of all href attributes from anchor tags.
                      Empty list if no links found or fetch fails.

        Note:
            Automatically calls fetch() if content hasn't been loaded yet.
            Filters out None values and empty href attributes.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup:
            return [
                a.get("href")
                for a in self.soup.find_all("a", href=True)
                if a.get("href")
            ]
        return []

    async def get_all_text(self) -> str:
        """Extract all visible text content from the page.

        This method removes script, style, and SVG elements before extracting
        text to ensure only visible content is returned.

        Returns:
            str: Clean text content with whitespace normalized.
                 Empty string if no content found or fetch fails.

        Note:
            Automatically calls fetch() if content hasn't been loaded yet.
            Text is separated by spaces and stripped of extra whitespace.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup:
            # Remove script and style elements
            for tag in self.soup(["script", "style", "svg"]):
                tag.decompose()
            # Get all visible text
            text = self.soup.get_text(separator=" ", strip=True)
            return text
        return ""

    async def get_all_html(self) -> str:
        """Get cleaned HTML content without scripts and styles.

        Returns:
            str: HTML content with script and style tags removed.
                 Empty string if no content found or fetch fails.

        Note:
            Automatically calls fetch() if content hasn't been loaded yet.
            Useful for further HTML processing while removing dynamic elements.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup:
            for tag in self.soup(["script", "style"]):
                tag.decompose()
            return str(self.soup)
        return ""

    async def get_all_html_cleaned(self) -> str:
        """Get heavily cleaned HTML without scripts, styles, classes, and media.

        This method removes scripts, styles, SVG elements, pictures, buttons,
        images, and links. It also strips class and href attributes from
        remaining elements.

        Returns:
            str: Heavily cleaned HTML content with minimal formatting.
                 Empty string if no content found or fetch fails.

        Note:
            Automatically calls fetch() if content hasn't been loaded yet.
            Best used when you need pure structural content without styling
            or interactive elements.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup:
            for tag in self.soup(
                ["script", "style", "svg", "picture", "button", "img", "link"]
            ):
                tag.decompose()
            # Remove all attributes from tags
            for tag in self.soup.find_all(True):
                if "class" in tag.attrs:
                    del tag.attrs["class"]
                if "href" in tag.attrs:
                    del tag.attrs["href"]
            return str(self.soup)
        return ""


# async def main() -> None:
#     """Demo function showing scrapper usage with multiple URLs.

#     This function demonstrates how to use the Scrapper class with the
#     ScrapperAnalyzer to perform complete content analysis on multiple URLs.
#     """
#     urls = [
#         "https://medium.com/@lautisuarez081/fastapi-best-practices-and-design-patterns-building-quality-python-apis-31774ff3c28a",
#         "https://medium.com/@adinlewakoyejo/under-the-libuv-hood-how-the-node-js-event-loop-works-158347ec2261",
#         "https://medium.com/@francescofranco_39234/object-detection-with-python-and-huggingface-transformers-508794c62456",
#     ]

#     for url in urls:
#         scrapper = Scrapper(url)
#         await scrapper.fetch()
#         analyzer = ScrapperAnalyzer(scrapper.soup)
#         results = await analyzer.analyze()
#         print("Sentiment:", results["sentiment"])


if __name__ == "__main__":
    print("test")
