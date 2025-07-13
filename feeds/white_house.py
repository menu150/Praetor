import feedparser
from datetime import datetime

WHITE_HOUSE_RSS = "https://www.whitehouse.gov/briefing-room/feed/"

def pull_white_house_feed(limit=10):
    feed = feedparser.parse(WHITE_HOUSE_RSS)
    items = []
    
    for entry in feed.entries[:limit]:
        item = {
            "source": "whitehouse.gov",
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", ""),
            "published": parse_timestamp(entry.get("published", ""))
        }
        items.append(item)
    
    return items

def parse_timestamp(ts_str):
    try:
        return datetime(*entry.published_parsed[:6])
    except:
        return None

# Optional: test run
if __name__ == "__main__":
    data = pull_white_house_feed()
    for item in data:
        print(f"[{item['published']}] {item['title']}")
        print(f"  ↳ {item['summary'][:100]}...\n")
