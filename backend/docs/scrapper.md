# Scrapper Module

## Overview

AI-powered web scraping and content analysis system that extracts, processes, and analyzes web content using machine learning.

## Key Features

- **JavaScript Support**: Renders dynamic content using Playwright
- **Stealth Mode**: Avoids bot detection
- **AI Analysis**: Sentiment, summarization, topic classification, entity recognition
- **Metadata Extraction**: SEO tags, Open Graph, Twitter Cards, Schema.org
- **Content Structuring**: Headers, links, media extraction


## Architecture

- **Scrapper**: Web content fetching with Playwright
- **ContentExtractor**: HTML content structuring  
- **MetadataAnalyzer**: SEO and structured data extraction
- **NLPLayer**: AI-powered text analysis

## ML Models

The module uses pre-trained HuggingFace models (downloaded automatically):

- **Sentiment**: DistilBERT (268MB)
- **NER**: BERT Large (1.33GB)  
- **Summarization**: DistilBART (1.22GB)
- **Topic Classification**: BART Large (1.63GB)

## CLI Tools

Test the scrapper interactively:

```bash
# Interactive URL scraper
uv run python -m app.scrapper.scrape_url_cli

# Sentiment analysis tool  
uv run python -m app.scrapper.sentiment_cli
```

## Performance Notes

- Models are cached after first download
- Text is automatically truncated for optimal performance
- GPU acceleration supported if available
- Async operations for non-blocking I/O

## Dependencies

- `playwright` + `playwright-stealth`: Browser automation
- `beautifulsoup4`: HTML parsing
- `transformers` + `torch`: ML models 