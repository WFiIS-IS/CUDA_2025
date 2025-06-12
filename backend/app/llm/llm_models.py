"""
Model configurations and retrieval functions for LLM operations.

This module centralizes all model names and provides functions to get
specific models for different NLP tasks.
"""

import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def gemini_request(prompt, task):
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {"contents": [{"parts": [{"text": f"{task}: {prompt}"}]}]}
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    response.raise_for_status()

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def get_sentiment_model():
    def sentiment(text):
        result = gemini_request(
            text,
            'Sentiment analysis (return JSON: {"label": <LABEL>, "score": <PROBABILITY between 0 and 1>})',
        )
        # Wyciągnij czysty JSON z odpowiedzi
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                # Zamień wszystkie klucze na lower-case
                data = {k.lower(): v for k, v in data.items()}
                return {
                    "label": str(data.get("label", "")).upper(),
                    "score": float(data.get("score", 1.0)),
                }
            except Exception:
                pass
        return {"label": result.strip().upper(), "score": 1.0}

    return sentiment


def get_summarization_model():
    def summarize(text):
        return gemini_request(
            text,
            "Summarize text and return as a string with max 200 words. If text is too short, return as it is. If you can't summarize, return as it is.",
        )

    return summarize


_topic_history = set()


def get_collection_model(candidate_labels=None):
    def classify(text):
        global _topic_history
        # Połącz aktualnych kandydatów z historią
        candidates = set(candidate_labels or [])
        candidates.update(_topic_history)
        candidates_list = list(candidates)
        candidates_str = (
            ", ".join(f'"{c}"' for c in candidates_list) if candidates_list else "None"
        )

        prompt = (
            "Classify the main topic of the following text. "
            f"Choose from these example topics: [{candidates_str}]. "
            "Check for appropriate topic. If none fit, create new vague topic."
            "Return as a string with best topic."
            f'\n\nText: "{text}"'
        )
        result = gemini_request("", prompt)
        topic = result.strip()
        if topic:
            _topic_history.add(topic)
        return topic

    return classify


def get_title_model():
    def title(text):
        return gemini_request(
            text,
            "Create a title for the following text. Title must be max 10 words. If text is too short, return as it is. If you can't create a title, return as it is.",
        )

    return title
