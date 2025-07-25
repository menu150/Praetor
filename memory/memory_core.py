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
            message TEXT,
            embedding BLOB
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

def recall_recent(limit: int = 5, conn=None) -> list[str]:
    """
    Return the last `limit` messages (most‐recent recency).
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [r["message"] for r in cur.fetchall()]

def recall_relevant(
    query: str,
    limit: int = 5,
    conn=None,
    embedding_model="text-embedding-ada-002"
) -> list[tuple[str,float]]:
    """
    Embed the query, compute cosine similarity against stored memory embeddings,
    and return the top‐`limit` messages with their scores.
    """
    from openai import Embedding
    import numpy as np

    conn = conn or get_connection()
    # 1) embed the query
    resp = Embedding.create(input=[query], model=embedding_model)
    q_emb = np.array(resp["data"][0]["embedding"])

    # 2) fetch all stored embeddings and messages
    cur = conn.cursor()
    cur.execute("SELECT id, message, embedding FROM messages")
    rows = cur.fetchall()

    # 3) compute similarity
    sims = []
    for row in rows:
        mem_emb = np.frombuffer(row["embedding"], dtype=np.float32)
        score = float(np.dot(q_emb, mem_emb) /
                      (np.linalg.norm(q_emb) * np.linalg.norm(mem_emb)))
        sims.append((row["message"], score))

    # 4) pick top‐ranked
    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:limit]
