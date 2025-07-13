# api_intel_feed.py (FastAPI compatible example)
from fastapi import FastAPI, Query
from typing import List, Optional
from memory_reader import get_recent_events

app = FastAPI()

@app.get("/api/intel-feed")
def intel_feed(limit: int = 20, classification: Optional[List[str]] = Query(None)):
    filters = {}
    if classification:
        filters["classification"] = classification

    events = get_recent_events(limit=limit, filters=filters)
    return {"items": events}
