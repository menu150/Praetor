# skills_py/news.py

import requests
import logging
from memory.memory_core import save_message

API_KEY = "a6894f6c-bfed-4145-afde-850a5c55fc12
NEWS_URL = "https://newsapi.org/v2/top-headlines"

# Configure basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def run_news_fetch():
    """
    Fetch top headlines from NewsAPI and persist them to memory,
    logging each step.
    """
    params = {
        "country": "us",
        "category": "general",
        "apiKey": API_KEY
    }
    logger.info("Starting news fetch...")
    try:
        response = requests.get(NEWS_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error("Error fetching news: %s", e)
        return f"[📰] Error fetching news: {e}"

    articles = data.get("articles", [])
    logger.info("Fetched %d articles", len(articles))

    for article in articles:
        title = article.get("title", "No Title")
        summary = article.get("description", "")
        url = article.get("url", "")

        # Persist the news item to memory
        save_message(message=f"{title}\n{summary}\n{url}", namespace="news")
        logger.info("Saved article: %s", title)

    return f"[📰] Fetched and saved {len(articles)} news headlines."


# Triggers for invoking this skill
triggers = ["news", "headlines", "what's in the news"]
