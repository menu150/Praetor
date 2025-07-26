#!/usr/bin/env python3
"""
Simple scheduler to run the news fetcher every 15 minutes.
"""
import time
import logging
import sys
from skills_py.news import run_news_fetch

# ─── Logging Setup ─────────────────────────────────────────────────
logger = logging.getLogger("news_scheduler")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ─── Scheduler Loop ────────────────────────────────────────────────
FETCH_INTERVAL = 15 * 60  # seconds

def main():
    logger.info("Starting news scheduler (interval: %d seconds)", FETCH_INTERVAL)
    try:
        while True:
            logger.info("Running scheduled news fetch...")
            try:
                run_news_fetch()
                logger.info("Fetch complete.")
            except Exception as e:
                logger.error("Error during news fetch: %s", e)
            time.sleep(FETCH_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted; exiting.")

if __name__ == '__main__':
    main()
