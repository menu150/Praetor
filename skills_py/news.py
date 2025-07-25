# skills_py/news.py

import os
import logging
import requests

from memory.memory_core import save_message

# ─── Logger setup ───────────────────────────────────────────────────
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ─── Configuration ──────────────────────────────────────────────────
API_KEY = os.getenv("NEWSAPI_API_KEY")
if not API_KEY:
    logger.error("Environment variable NEWSAPI_API_KEY is not set.")
    raise RuntimeError("Missing NEWSAPI_API_KEY")

NEWS_URL = "https://newsapi.org/v2/top-headlines"


def run_news_fetch():
    logger.info("Starting news fetch...")
    params = {
        "country": "us",
        "category": "general",
        "apiKey": API_KEY
    }

    try:
        response = requests.get(NEWS_URL, params=params)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return

    data = response.json()
    articles = data.get("articles", [])

    for article in articles:
        title   = (article.get("title") or "").strip()
        summary = (article.get("description") or "").strip()
        url     = (article.get("url") or "").strip()
        message = f"{title}\n{summary}\n{url}"

        save_message(message, namespace="news")
        logger.info(f"Saved article: {title}")

    logger.info(f"Fetched and stored {len(articles)} articles.")


# List of triggers for the Brain’s dynamic loader
triggers = ["news", "headlines", "what's in the news"]
