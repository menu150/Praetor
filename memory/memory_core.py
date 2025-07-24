import sqlite3
from datetime import datetime

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

def get_connection(db_path="praetor_memory.db"):
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

def save_message(message: str, namespace: str = "default", conn=None):
    """
    Persist a message to the messages table.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message) VALUES (?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message)
    )
    conn.commit()
