# skills_py/news_sources.py

import requests
import os

API_KEY = os.getenv("NEWSAPI_API_KEY")
SOURCES_URL = "https://newsapi.org/v2/top-headlines/sources"

def fetch_global_sources():
    resp = requests.get(SOURCES_URL, params={"apiKey": API_KEY})
    data = resp.json()
    return [s["id"] for s in data.get("sources", []) if s.get("id")]

CURATED_SOURCES = [
    "reuters", "bbc-news", "al-jazeera-english", "the-verge", "bloomberg",
    "axios", "techcrunch", "financial-times", "politico"
]

def get_curated_sources():
    return CURATED_SOURCES
