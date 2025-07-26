import requests
import os

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"
PAGE_SIZE = 25  # Safe value (max is 100)

def fetch_news_articles(target_count=50, country="us"):
    articles = []
    page = 1

    while len(articles) < target_count:
        response = requests.get(BASE_URL, params={
            "apiKey": NEWS_API_KEY,
            "country": country,
            "pageSize": PAGE_SIZE,
            "page": page,
        })
        data = response.json()

        if data.get("status") != "ok" or not data.get("articles"):
            break

        articles.extend(data["articles"])

        if len(data["articles"]) < PAGE_SIZE:
            break  # No more articles available

        page += 1

    return articles[:target_count]

def run():
    try:
        print("[📰] Fetching news...")
        articles = fetch_news_articles()

        # Optional: summarize or store here
        for i, article in enumerate(articles[:5], 1):  # Preview top 5
            print(f"{i}. {article['title']} — {article.get('source', {}).get('name')}")

        return {"status": "success", "count": len(articles)}
    except Exception as e:
        print(f"[❌] News skill failed: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    run()
