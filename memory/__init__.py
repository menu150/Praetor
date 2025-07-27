from .memory_core import (
    save_message,
    recall_recent,
    recall_relevant,
    get_connection,
    load_all_skills,
)

# ──────────────────── Auto‑init DB on import ────────────────────
# get_connection() will create the file and call init_db(conn) internally
conn = get_connection()  # Now tables are guaranteed to exist
