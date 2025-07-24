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

def save_message(message: str, namespace: str = "default", conn=None):
    """
    Persist a message to the messages table.
    """
    # make sure table exists
    conn = init_db(conn)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message) VALUES (?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message)
    )
    conn.commit()
