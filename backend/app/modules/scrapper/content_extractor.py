from bs4 import BeautifulSoup
from typing import Dict, Any

class ContentExtractor:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def extract(self) -> Dict[str, Any]:
        # Extract main text
        for tag in self.soup(["script", "style", "svg", "picture", "button", "img", 'link']):
            tag.decompose()
        main_text = self.soup.get_text(separator=" ", strip=True)
        # Extract headers
        headers = {f"h{i}": [h.get_text(strip=True) for h in self.soup.find_all(f"h{i}")] for i in range(1, 7)}
        # Extract links
        links = [a.get("href") for a in self.soup.find_all("a", href=True)]
        # Extract media (img src, video src)
        images = [img.get("src") for img in self.soup.find_all("img", src=True)]
        videos = [video.get("src") for video in self.soup.find_all("video", src=True)]
        return {
            "main_text": main_text,
            "headers": headers,
            "links": links,
            "images": images,
            "videos": videos
        }
