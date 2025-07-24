import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_recent_events(directory="memory/data", limit=20, filters=None):
    """
    Load recent events from JSON files in a directory,
    applying optional filters, and return up to 'limit' items.
    """
    filters = filters or {}
    events = []

    # Iterate over files in descending order
    for filename in sorted(os.listdir(directory), reverse=True):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r") as f:
                item = json.load(f)
        except Exception as e:
            logger.warning(f"[READ ERROR] {e} in {filepath}")
            continue

        # Apply filters if available, otherwise include all items
        try:
            if apply_filters(item, filters):
                events.append(item)
        except NameError:
            events.append(item)

        if len(events) >= limit:
            break

    return events
