import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB = os.path.join(BASE_DIR, "praetor_memory.db")

def init_db(conn=None, db_path="praetor_memory.db"):
    """
    Ensure the messages table exists.
    """
    conn = conn or get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace TEXT,
            timestamp TEXT,
            message TEXT
        )
    """)
    conn.commit()
    return conn

def get_connection(db_path="DEFAULT_DB"):
    """
    Return a sqlite3 connection to the memory database,
    and ensure all tables are present.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # ─── auto–create the messages table ──────────────────
    init_db(conn)
    return conn

def load_all_skills(conn):
    """
    Load all skills from the skills table and return a list of tuples
    (trigger, action, path_or_command).
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT trigger, action, path_or_command FROM skills"
    )
    return cursor.fetchall()

def save_message(message: str, namespace: str = "default", conn=None,db_path=DEFAULT_DB):
    print(f"[DEBUG] save_message called → namespace={namespace!r}, message={message!r}")
    """
    Persist a message to the messages table.
    """
    conn = conn or get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message) VALUES (?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message)
    )
    conn.commit()
# ─── auto-create messages table on module import ───────────────────
# this runs as soon as anything “import memory.memory_core”
init_db()
