import asyncio

from app.modules.scrapper.analyzer import ScrapperAnalyzer
from app.modules.scrapper.scrapper import Scrapper


def print_results(results):
    print(f"Sentiment: {results['sentiment']}")
    # Uncomment below to see more details
    # print(f"Summary: {results['summary']}")
    # print(f"NER: {results['ner']}")
    # print(f"Topics: {results['topics']}")
    # print(f"Meta: {results['meta']}")
    # print(f"Tags: {results['tags']}")


async def process_url(url: str):
    scrapper = Scrapper(url)
    await scrapper.fetch()
    analyzer = ScrapperAnalyzer(scrapper.soup)
    results = await analyzer.analyze()
    print_results(results)
    return reusults


def main():
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
