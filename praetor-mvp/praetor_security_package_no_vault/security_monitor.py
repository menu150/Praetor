#!/usr/bin/env python3
import time, json, requests
from pathlib import Path

CONFIG_PATH = "/opt/praetor/security_config.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def tail_file(path):
    with open(path, 'r') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

def monitor_logs():
    config = load_config()
    endpoint = config.get("praetor_api", "http://localhost:8000/api/security-events")
    logs = ["/var/log/auth.log", "/var/log/fail2ban.log"]
    tails = [tail_file(log) for log in logs if Path(log).exists()]
    for lines in zip(*tails):
        for line in lines:
            try:
                payload = {"event": line.strip(), "source": "security_monitor"}
                requests.post(endpoint, json=payload)
            except:
                pass

if __name__ == "__main__":
    monitor_logs()
