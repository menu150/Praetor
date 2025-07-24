# memory_store.py
import os
import json
import logging
from datetime import datetime

logger = logging.getlogger(_name_)

def store_rss_entry(item, namespace="white_house"):
    timestamp = datetime.now().isoformat()
    fname = f"memory/data/{namespace}_{timestamp}_{item['id']}.json"
    os.makedirs(os.path.dirname(fname), exist_ok=True)

    with open(fname, "w") as f:
        json.dump(item, f, indent=2, ensure_ascii=False)
