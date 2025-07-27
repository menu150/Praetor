import os
import sqlite3
import pickle
from datetime import datetime
import openai
import numpy as np

# ─────────────────────────────── BASE CONFIG ───────────────────────────────
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "praetor_memory.db")

# ─────────────────────────────── DB SETUP ───────────────────────────────
def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    # Messages table (acts as log)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace TEXT,
            timestamp TEXT,
            message TEXT,
            embedding BLOB,
            region TEXT
        )
    """)
    # Skills table with enabled toggle
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            trigger TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            path_or_command TEXT,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)
    # Summaries table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            summary TEXT
        )
    """)
    conn.commit()

# ─────────────────────────────── MEMORY IO ───────────────────────────────
def save_message(
    message: str,
    namespace: str = "default",
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
):
    conn = conn or get_connection()
    cur = conn.cursor()

    # Compute embedding
    resp = openai.embeddings.create(input=[message], model=embedding_model)
    emb = resp.data[0].embedding
    blob = sqlite3.Binary(pickle.dumps(emb))

    # Infer region
    region = infer_region_from_text(message)

    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message, embedding, region) VALUES (?, ?, ?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message, blob, region)
    )
    conn.commit()


def load_logs_since(
    cutoff: datetime,
    namespace: str = None,
    conn: sqlite3.Connection = None
) -> list[tuple[str, str]]:
    """
    Return list of (timestamp, message) for logs newer than cutoff. Optionally filter by namespace.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    if namespace:
        cur.execute(
            "SELECT timestamp, message FROM messages WHERE timestamp >= ? AND namespace = ? ORDER BY timestamp ASC",
            (cutoff.isoformat(), namespace)
        )
    else:
        cur.execute(
            "SELECT timestamp, message FROM messages WHERE timestamp >= ? ORDER BY timestamp ASC",
            (cutoff.isoformat(),)
        )
    rows = cur.fetchall()
    return [(row["timestamp"], row["message"]) for row in rows]

# ─────────────────────────────── SUMMARIES ───────────────────────────────
def save_summary(
    summary: str,
    conn: sqlite3.Connection = None
):
    """Save a daily summary into the summaries table."""
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO summaries (timestamp, summary) VALUES (?, ?)",
        (datetime.utcnow().isoformat(), summary)
    )
    conn.commit()

# ─────────────────────────────── RECALL METHODS ───────────────────────────────
def recall_recent(
    limit: int = 5,
    conn: sqlite3.Connection = None
) -> list[str]:
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [r["message"] for r in cur.fetchall()]


def recall_relevant(
    query: str,
    limit: int = 5,
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
) -> list[tuple[str, float]]:
    conn = conn or get_connection()
    cur = conn.cursor()

    # Query embedding
    resp = openai.embeddings.create(input=[query], model=embedding_model)
    q_emb = np.array(resp.data[0].embedding)

    cur.execute("SELECT message, embedding FROM messages")
    rows = cur.fetchall()

    sims = []
    for row in rows:
        mem_emb = pickle.loads(row["embedding"])
        score = float(np.dot(q_emb, mem_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(mem_emb)))
        sims.append((row["message"], score))

    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:limit]

# ─────────────────────────────── SKILLS MANAGEMENT ───────────────────────────────
def load_all_skills(
    conn: sqlite3.Connection = None
) -> list[sqlite3.Row]:
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute("SELECT trigger, action, path_or_command, enabled FROM skills ORDER BY trigger")
    return cur.fetchall()


def set_skill_enabled(
    trigger: str,
    enabled: bool,
    conn: sqlite3.Connection = None
):
    """Enable or disable a skill by trigger."""
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE skills SET enabled = ? WHERE trigger = ?",
        (1 if enabled else 0, trigger)
    )
    conn.commit()

# Auto-init on import
init_db(get_connection())
