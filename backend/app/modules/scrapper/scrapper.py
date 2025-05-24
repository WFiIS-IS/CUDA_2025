import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Import playwright_stealth for stealth mode
from playwright_stealth import stealth_async

from .analyzer import ScrapperAnalyzer

# Add imports for new modules
from .content_extractor import ContentExtractor
from .metadata_analyzer import MetadataAnalyzer
from .nlp import NLPLayer


class Scrapper:
    """
    An asynchronous web scrapper that uses Playwright to fetch and parse HTML content from a given URL, supporting JavaScript-rendered pages.
    Uses extra stealth by applying playwright-stealth plugin and modifying browser context and user agent.
    """

    def __init__(self, url: str):
        self.url = url
        self.soup = None

    async def fetch(self):
        """
        Uses Playwright to launch a headless browser with stealth settings, navigate to the URL, and parse the rendered HTML with BeautifulSoup.
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

    async def get_title(self):
        """
        Returns the title of the web page.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup and self.soup.title:
            return self.soup.title.string
        return None

    async def get_links(self):
        """
        Returns a list of all hyperlinks (anchor tags) on the page.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup:
            return [a.get("href") for a in self.soup.find_all("a", href=True)]
        return []

    async def get_all_text(self):
        """
        Returns all visible text nodes from the HTML, concatenated as a single string.
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

    # add async method to return all html
    async def get_all_html(self):
        """
        Returns all HTML content from the page.
        """
        if self.soup is None:
            await self.fetch()
        if self.soup:
            for tag in self.soup(["script", "style"]):
                tag.decompose()
            return str(self.soup)
        return ""

    # get all html without tags, styles, and scripts and classes
    async def get_all_html_cleaned(self):
        """
        Returns all HTML content from the page without tags, styles, scripts, and classes.
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

    async def main():
        scrapper = Scrapper(
            "https://medium.com/@lautisuarez081/fastapi-best-practices-and-design-patterns-building-quality-python-apis-31774ff3c28a"
        )
        await scrapper.fetch()
        analyzer = ScrapperAnalyzer(scrapper.soup)
        results = await analyzer.analyze()
        print("Tags:", results["tags"])
        print("Sentiment:", results["sentiment"])
        print("Summary:", results["summary"])
        print("NER:", results["ner"])
        print("Topics:", results["topics"])
        print("Meta:", results["meta"])

    if __name__ == "__main__":
        asyncio.run(main())
