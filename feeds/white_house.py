# feeds/white_house.py
import feedparser
from datetime import datetime
from summarizer import summarize_rss_item
from classifier import classify_event
from memory.memory_store import store_rss_entry
import uuid

WHITE_HOUSE_RSS = "https://www.whitehouse.gov/news/feed/"

def pull_white_house_feed(limit=5):
    feed = feedparser.parse(WHITE_HOUSE_RSS)
    for entry in feed.entries[:limit]:
        item = {
            "id": str(uuid.uuid4()),
            "source": "whitehouse.gov",
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", ""),
            "published": parse_timestamp(entry.get("published_parsed", None))
        }

        item["ai_summary"] = summarize_rss_item(item)
        item["classification"] = classify_event(item)

        store_rss_entry(item, namespace="white_house")

def parse_timestamp(ts_struct):
    if ts_struct:
        return datetime(*ts_struct[:6]).isoformat()
    return None

if __name__ == "__main__":
    pull_white_house_feed()
