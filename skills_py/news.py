import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests

from memory.summarizer import summarize_article  # Update if your function name is different
from memory.memory_core import save_message  # Assumes save_message(conn, source, content, tags)
from memory.db import get_connection  # Or however you get a DB connection

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"
PAGE_SIZE = 25  # Max 100 per page, 25 for safer pagination

def fetch_news_articles(target_count=50, country="us"):
    articles = []
    page = 1

    while len(articles) < target_count:
        res = requests.get(BASE_URL, params={
            "apiKey": NEWS_API_KEY,
            "country": country,
            "pageSize": PAGE_SIZE,
            "page": page,
        })
        data = res.json()

        if data.get("status") != "ok":
            print(f"[❌] Error from NewsAPI: {data}")
            break

        fetched = data.get("articles", [])
        if not fetched:
            break

        articles.extend(fetched)
        if len(fetched) < PAGE_SIZE:
            break

        page += 1

    return articles[:target_count]

def run():
    try:
        print("[📰] Fetching up to 50 news articles...")
        articles = fetch_news_articles()

        conn = get_connection()
        stored = 0

        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            content = f"{title}\n\n{description}"
            if not content.strip():
                continue

            summary = summarize_article(content)
            if not summary:
                continue

            # Store summary into memory
            save_message(conn, source="news", content=summary, tags=["news", "summary"])
            stored += 1

        print(f"[✅] Fetched {len(articles)} articles, stored {stored} summaries to memory.")
        return {"status": "success", "fetched": len(articles), "stored": stored}

    except Exception as e:
        print(f"[❌] News skill failed: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    run()
