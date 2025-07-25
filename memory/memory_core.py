import os
import sqlite3
import pickle
from datetime import datetime

import numpy as np
import openai

# ─── Constants & Paths ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
DEFAULT_DB = os.path.join(BASE_DIR, "praetor_memory.db")

# ─── Schema Initialization ──────────────────────────────────────────
def init_db(conn=None, db_path=DEFAULT_DB):
    """
    Ensure the messages table exists (with an embedding BLOB column).
    """
    conn = conn or sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace TEXT,
            timestamp TEXT,
            message   TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    return conn

# ─── Connection Factory ─────────────────────────────────────────────
def get_connection(db_path=DEFAULT_DB):
    """
    Return a sqlite3 connection to the memory database,
    auto-creating tables as needed.
    """
    return init_db(sqlite3.connect(db_path), db_path)

# ─── Skill Loader (unchanged) ───────────────────────────────────────
def load_all_skills(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT trigger, action, path_or_command FROM skills"
    )
    return cursor.fetchall()

# ─── Message Persistence ────────────────────────────────────────────
def save_message(
    message: str,
    namespace: str = "default",
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
):
    """
    Persist a message + its embedding to the messages table.
    """
    conn = conn or get_connection()
    cur  = conn.cursor()

    # 1) Compute embedding for the message
    resp = openai.Embedding.create(input=[message], model=embedding_model)
    emb  = np.array(resp["data"][0]["embedding"], dtype=np.float32)
    blob = sqlite3.Binary(pickle.dumps(emb))

    # 2) Insert row
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message, embedding) VALUES (?, ?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message, blob)
    )
    conn.commit()

# ─── Recall APIs ────────────────────────────────────────────────────
def recall_recent(limit: int = 5, conn: sqlite3.Connection = None) -> list[str]:
    """
    Return the last `limit` messages (by insertion order).
    """
    conn = conn or get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [r["message"] for r in cur.fetchall()]

def recall_relevant(
    query: str,
    limit: int = 5,
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
) -> list[tuple[str, float]]:
    """
    Embed the query, compute cosine-similarity against stored embeddings,
    and return the top-`limit` messages with their similarity scores.
    """
    conn = conn or get_connection()
    cur  = conn.cursor()

    # 1) Embed the query
    resp = openai.Embedding.create(input=[query], model=embedding_model)
    q_emb = np.array(resp["data"][0]["embedding"], dtype=np.float32)

    # 2) Fetch stored embeddings
    cur.execute("SELECT message, embedding FROM messages WHERE embedding IS NOT NULL")
    sims = []
    for msg, emb_blob in cur.fetchall():
        mem_emb = pickle.loads(emb_blob)
        score   = float(np.dot(q_emb, mem_emb) /
                        (np.linalg.norm(q_emb) * np.linalg.norm(mem_emb)))
        sims.append((msg, score))

    # 3) Return top-N by score
    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:limit]

# ─── Auto-init on import ────────────────────────────────────────────
init_db()
