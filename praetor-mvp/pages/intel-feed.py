from fastapi import FastAPI, Query
from typing import List, Optional
from praetor.memory.memory_reader import get_recent_events
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/api/intel-feed")
def intel_feed(limit: int = 20, classification: Optional[List[str]] = Query(None)):
    filters = {}
    if classification:
        filters["classification"] = classification

    logger.info(f"Fetching {limit} events with filters: {filters}")
    events = get_recent_events(limit=limit, filters=filters)
    return {"items": events}
