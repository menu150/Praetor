import os
import sqlite3
import pickle
from datetime import datetime
import openai

# Default DB path
BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB = os.path.join(BASE_DIR, "praetor_memory.db")

# ─────────────────────────────── DB SETUP ───────────────────────────────
def get_connection(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    """
    Return a sqlite3 connection to the memory database and ensure tables exist.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> sqlite3.Connection:
    """
    Initialize database tables for messages, summaries, and skills.
    """
    cur = conn.cursor()
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            summary TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            trigger TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            path_or_command TEXT,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()
    return conn


# ─────────────────────────────── REGION INFERENCE ───────────────────────────────
def infer_region_from_text(text: str) -> str:
    """
    Use GPT to infer the geographic region for a given text snippet.
    """
    prompt = (
        f"What region is this message about?\n\n'''{text}'''" 
        "\nRespond with one region only (US, Europe, Asia, Middle East, Africa, Latin America, or Global)."
    )
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[⚠️] Region inference failed: {e}")
        return "Unknown"


# ─────────────────────────────── MEMORY IO ───────────────────────────────
def save_message(
    message: str,
    namespace: str = "default",
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
) -> None:
    """
    Compute the embedding for `message`, infer its region, and store it.
    """
    conn = conn or get_connection()
    cur = conn.cursor()

    # 1) Compute embedding
    resp = openai.embeddings.create(input=[message], model=embedding_model)
    emb = resp.data[0].embedding
    blob = sqlite3.Binary(pickle.dumps(emb))

    # 2) Infer region
    region = infer_region_from_text(message)

    # 3) Insert record
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message, embedding, region) VALUES (?, ?, ?, ?, ?)"
        , (namespace, datetime.utcnow().isoformat(), message, blob, region)
    )
    conn.commit()


def recall_recent(limit: int = 5, conn: sqlite3.Connection = None) -> list[str]:
    """
    Return the most recent `limit` messages.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [row[0] for row in cur.fetchall()]


def recall_relevant(
    query: str,
    limit: int = 5,
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
) -> list[tuple[str, float]]:
    """
    Return up to `limit` messages most semantically similar to `query`.
    """
    import numpy as np
    conn = conn or get_connection()

    # Query embedding
    resp = openai.embeddings.create(input=[query], model=embedding_model)
    q_emb = np.array(resp.data[0].embedding)

    # Fetch all memories
    cur = conn.cursor()
    cur.execute("SELECT message, embedding FROM messages")
    rows = cur.fetchall()

    # Compute cosine similarity
    sims = []
    for row in rows:
        mem_emb = pickle.loads(row[1])
        mem_vec = np.array(mem_emb)
        score = float(np.dot(q_emb, mem_vec) / (np.linalg.norm(q_emb) * np.linalg.norm(mem_vec)))
        sims.append((row[0], score))
    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:limit]


# ─────────────────────────────── SUMMARIZER HELPERS ───────────────────────────────
def load_logs_since(cutoff: datetime, conn: sqlite3.Connection = None) -> list[tuple[str, str]]:
    """
    Return all (timestamp, message) entries with timestamp >= cutoff.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, message FROM messages WHERE timestamp >= ? ORDER BY id ASC",
        (cutoff.isoformat(),)
    )
    return [(row[0], row[1]) for row in cur.fetchall()]


def save_summary(summary: str, conn: sqlite3.Connection = None) -> None:
    """
    Persist a daily summary into the summaries table.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO summaries (timestamp, summary) VALUES (?, ?)",
        (datetime.utcnow().isoformat(), summary)
    )
    conn.commit()


# ─────────────────────────────── SKILLS ───────────────────────────────
def load_all_skills(conn: sqlite3.Connection = None) -> list[sqlite3.Row]:
    """
    Return all enabled skills from the skills table.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT trigger, action, path_or_command FROM skills WHERE enabled=1"
    )
    return cur.fetchall()


def add_skill(
    trigger: str,
    action: str,
    path_or_command: str = "",
    enabled: bool = True,
    conn: sqlite3.Connection = None
) -> None:
    """
    Add or update a skill, toggled on/off by `enabled`.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO skills (trigger, action, path_or_command, enabled) VALUES (?, ?, ?, ?)",
        (trigger, action, path_or_command, int(enabled))
    )
    conn.commit()


def toggle_skill(trigger: str, enabled: bool, conn: sqlite3.Connection = None) -> None:
    """
    Enable or disable a skill by its trigger.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE skills SET enabled = ? WHERE trigger = ?",
        (int(enabled), trigger)
    )
    conn.commit()


def get_skills(enabled_only: bool = True, conn: sqlite3.Connection = None):
    """
    Return all skills; filter to enabled only if requested.
    """
    conn = conn or get_connection()
    cur = conn.cursor()
    if enabled_only:
        cur.execute("SELECT trigger, action, path_or_command FROM skills WHERE enabled=1")
    else:
        cur.execute("SELECT trigger, action, path_or_command, enabled FROM skills")
    return cur.fetchall()

# ─────────────────────────────── AUTO-INIT ───────────────────────────────
# Ensure DB is initialized on import
get_connection()
