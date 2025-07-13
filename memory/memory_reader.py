# memory_reader.py
import os
import json
from datetime import datetime

def get_recent_events(directory="memory/data", limit=20, filters=None):
    filters = filters or {}
    events = []

    for filename in sorted(os.listdir(directory), reverse=True):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r") as f:
                    item = json.load(f)
                    if apply_filters(item, filters):
                        events.append(item)
                        if len(events) >= limit:
                            break
            except Exception:
                continue

    return events

def apply_filters(item, filters):
    for key, value in filters.items():
        if key not in item:
            return False
        if isinstance(value, list):
            if not any(v in item[key] for v in value):
                return False
        elif item[key] != value:
            return False
    return True
