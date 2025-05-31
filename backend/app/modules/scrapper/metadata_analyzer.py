from typing import Any

from bs4 import BeautifulSoup


class MetadataAnalyzer:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def extract(self) -> dict[str, Any]:
        meta = {}
        # SEO tags
        meta["title"] = self.soup.title.string if self.soup.title else None
        meta["description"] = (
            self.soup.find("meta", attrs={"name": "description"}).get("content")
            if self.soup.find("meta", attrs={"name": "description"})
            else None
        )
        meta["keywords"] = (
            self.soup.find("meta", attrs={"name": "keywords"}).get("content")
            if self.soup.find("meta", attrs={"name": "keywords"})
            else None
        )
        # Open Graph
        meta["og"] = {
            tag.get("property"): tag.get("content")
            for tag in self.soup.find_all("meta", property=True)
            if tag.get("property", "").startswith("og:")
        }
        # Twitter Cards
        meta["twitter"] = {
            tag.get("name"): tag.get("content")
            for tag in self.soup.find_all("meta", attrs={"name": True})
            if tag.get("name", "").startswith("twitter:")
        }
        # Schema.org (JSON-LD)
        schemas = []
        for script in self.soup.find_all("script", type="application/ld+json"):
            try:
                import json

                schemas.append(json.loads(script.string))
            except Exception:
                continue
        meta["schemas"] = schemas
        return meta
