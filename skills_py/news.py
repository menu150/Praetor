# /skills_py/news.py

import requests
from memory.memory_core import save_message  # or your memory write method

API_KEY = "your-newsapi-key"
NEWS_URL = "https://newsapi.org/v2/top-headlines"

def run_news_fetch():
    params = {
        "country": "us",
        "category": "general",
        "apiKey": API_KEY
    }
    response = requests.get(NEWS_URL, params=params)
    data = response.json()

    articles = data.get("articles", [])
    for article in articles:
        title = article["title"]
        summary = article.get("description", "")
        url = article.get("url", "")
        save_message("news", f"{title}\n{summary}\n{url}")

    return f"[📰] Fetched {len(articles)} news headlines."

triggers = ["news", "headlines", "what's in the news"]
