# run_news.py

from memory.memory_core import init_db, DEFAULT_DB
# ── Create the DB file and messages table if missing ──
init_db(db_path=DEFAULT_DB)

from skills_py.news import run_news_fetch

if __name__ == "__main__":
    run_news_fetch()
