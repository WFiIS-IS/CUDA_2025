import asyncio
from typing import Any

from app.modules.scrapper.analyzer import ScrapperAnalyzer
from app.modules.scrapper.scrapper import Scrapper


def print_results(results: dict[str, Any]) -> None:
    """Print formatted analysis results to console.

    This function displays the sentiment analysis results in a user-friendly format.
    Additional result types are commented out but can be enabled for more detailed output.

    Args:
        results (dict[str, Any]): Analysis results from ScrapperAnalyzer containing
                                 sentiment, summary, NER, topics, meta, and tags data.

    Note:
        Currently only displays sentiment results. Uncomment other print statements
        to see additional analysis details including summary, NER, topics, metadata, and tags.
    """
    print(f"Sentiment: {results['sentiment']}")
    # Uncomment below to see more details
    # print(f"Summary: {results['summary']}")
    # print(f"NER: {results['ner']}")
    # print(f"Topics: {results['topics']}")
    # print(f"Meta: {results['meta']}")
    # print(f"Tags: {results['tags']}")


async def process_url(url: str) -> None:
    """Process a single URL through the complete analysis pipeline.

    This function handles the full scraping and analysis workflow for a given URL,
    including content fetching, parsing, and comprehensive AI-powered analysis.

    Args:
        url (str): The URL to scrape and analyze. Must be a valid HTTP/HTTPS URL.

    Raises:
        ValueError: If the scrapper fails to fetch content from the URL.
        Exception: If any part of the analysis pipeline fails.

    Note:
        The process includes:
        1. Initialize Scrapper with the URL
        2. Fetch and parse web content using Playwright
        3. Verify content was successfully retrieved
        4. Run complete analysis pipeline (NLP, metadata, content extraction)
        5. Display formatted results
    """
    scrapper = Scrapper(url)
    await scrapper.fetch()

    # Ensure soup is not None after fetch
    if scrapper.soup is None:
        raise ValueError("Failed to fetch content from URL")

    analyzer = ScrapperAnalyzer(scrapper.soup)
    results = await analyzer.analyze()
    print_results(results)


def main() -> None:
    """Interactive CLI tool for web scraping and content analysis.

    This function provides a command-line interface for testing the scrapper
    functionality. Users can input URLs interactively and see analysis results
    in real-time. The tool continues running until the user types 'exit' or 'quit'.

    Features:
        - Interactive URL input
        - Real-time processing and analysis
        - Error handling with user-friendly messages
        - Graceful exit commands
        - Input validation (skips empty inputs)

    Usage:
        Run the script and enter URLs when prompted. Type 'exit' or 'quit' to stop.

    Note:
        Each URL is processed independently using asyncio for optimal performance.
        Large ML models are loaded on first use and cached for subsequent requests.
    """
    print("Paste a URL to scrape and analyze sentiment. Type 'exit' or 'quit' to stop.")
    while True:
        url = input("URL: ").strip()
        if url.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not url:
            continue
        try:
            asyncio.run(process_url(url))
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
