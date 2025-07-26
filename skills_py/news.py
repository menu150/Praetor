import os
import requests
from memory.memory_core import save_message
from skills_py.summarizer import summarize_rss_item
from skills_py.news_sources import fetch_global_sources, get_curated_sources

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("NEWSAPI_API_KEY")

if not API_KEY:
    logger.error("Environment variable NEWSAPI_API_KEY is not set.")
    raise RuntimeError("Missing NEWSAPI_API_KEY")

def run_news_fetch():
    logger.info("Starting news fetch...")
    all_sources = list(set(fetch_global_sources() + get_curated_sources()))

    for source_id in all_sources:
        try:
            logger.info(f"Fetching from source: {source_id}")
            resp = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "apiKey": API_KEY,
                    "sources": source_id,
                    "pageSize": 20
                }
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])

            for article in articles:
                title = (article.get("title") or "").strip()
                desc = (article.get("description") or "").strip()
                url = (article.get("url") or "").strip()

                if not title:
                    continue

                content_to_summarize = f"{title}\n{desc}"
                summary = summarize_rss_item(content_to_summarize)
                message = f"{summary}\n\n{url}"
                save_message(message, namespace="news")

        except Exception as e:
            logger.warning(f"Failed to fetch from {source_id}: {e}")

    logger.info("✅ News fetch complete.")
    return True

if __name__ == "__main__":
    run_news_fetch()
