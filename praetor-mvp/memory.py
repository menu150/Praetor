# Place this in your root or /core/ folder

import os
import json
import datetime

MEMORY_DIR = "./memory_logs"
os.makedirs(MEMORY_DIR, exist_ok=True)

def memory_write(entry: dict):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(MEMORY_DIR, f"{timestamp}.json")
    with open(filename, "w") as f:
        json.dump(entry, f, indent=2)
    return filename

def memory_read(keyword: str):
    results = []
    for file in os.listdir(MEMORY_DIR):
        if file.endswith(".json"):
            with open(os.path.join(MEMORY_DIR, file), "r") as f:
                entry = json.load(f)
                if keyword.lower() in json.dumps(entry).lower():
                    results.append(entry)
    return results
