# Backend

## Installing dependencies

```sh
uv sync
```

## Running project

```sh
just
```

or

```sh
uv run python -m app
```

## Adding dependencies

```sh
uv add ...
```

## Scrapper Module

AI-powered web scraping and content analysis with machine learning capabilities.

### Quick Start

```bash
# Interactive CLI tool
uv run python -m app.scrapper.scrape_url_cli
```

```python
# Programmatic usage
from app.scrapper.scrapper import Scrapper
from app.scrapper.analyzer import ScrapperAnalyzer

scrapper = Scrapper("https://example.com")
await scrapper.fetch()

analyzer = ScrapperAnalyzer(scrapper.soup)
results = await analyzer.analyze()
```


See `docs/scrapper.md` for detailed information and examples.
