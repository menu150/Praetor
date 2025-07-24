from fastapi import FastAPI, Query
from typing import List, Optional
from memory.memory_reader import get_recent_events
from skills_py import news, finance
import logging

# Proper logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/api/intel-feed")
def intel_feed(limit: int = 20, classification: Optional[List[str]] = Query(None)):
    filters = {}
    if classification:
        filters["classification"] = classification

    logger.info(f"Fetching {limit} events with filters: {filters}")
    events = get_recent_events(limit=limit, filters=filters)
    return {"items": events}

@app.get("/api/intel-feed/classifications")
def get_classifications():
    events = get_recent_events(limit=1000)
    classifications = sorted(list(set(
        event.get("classification") for event in events if event.get("classification")
    )))
    return {"classifications": classifications}

@app.get("/api/skill/news")
def skill_news(q: str = "latest headlines"):
    result = news.run(q)
    logger.info(f"[NewsAgent] Query: {q} → {result}")
    return result

@app.get("/api/skill/finance")
def skill_finance(q: str = "AAPL"):
    result = finance.run(q)
    logger.info(f"[FinanceAgent] Query: {q} → {result}")
    return result
