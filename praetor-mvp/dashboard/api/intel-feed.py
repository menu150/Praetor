# api_intel_feed.py (FastAPI compatible example)
from fastapi import FastAPI, Query
from typing import List, Optional
from praetor.memory. memory_reader import get_recent_events
import logging

logger = logging.getLogger(_name_)

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
    """
    Returns a list of all unique 'classification' values from the events data.
    """
    events = get_recent_events(limit=1000)  # Consider making this limit configurable or dynamic
    classifications = sorted(list(set(event.get("classification") for event in events if event.get("classification"))))
    return {"classifications": classifications}
