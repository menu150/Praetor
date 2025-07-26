import os
import sqlite3
import pickle
from datetime import datetime
import numpy as np
import openai

# Constants
BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB = os.path.join(BASE_DIR, "praetor_memory.db")
EMBEDDING_MODEL = "text-embedding-ada-002"

# ──────────────────────────────────────────────────────────────────────────────
def get_connection(db_path=DEFAULT_DB):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)  # Ensure schema on connect
    return conn

def init_db(conn=None, db_path=DEFAULT_DB):
    conn = conn or get_connection(db_path)
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
    conn.commit()
    return conn

# ──────────────────────────────────────────────────────────────────────────────
def classify_region_from_text(text: str) -> str:
    """
    Use GPT to classify the geographic region of this message.
    Returns: e.g., 'US', 'Europe', 'Global', 'Middle East', 'Asia', etc.
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Classify the dominant geographical region of this news article. Respond with just one region like: US, Europe, Global, Middle East, Asia, Africa, Latin America, etc."},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[⚠️] Region classification failed: {e}")
        return "Unknown"

# ──────────────────────────────────────────────────────────────────────────────
def save_message(
    message: str,
    namespace: str = "default",
    conn: sqlite3.Connection = None,
    embedding_model: str = EMBEDDING_MODEL
):
    """
    Persist a message + its embedding to the messages table.
    Auto-classifies the message's region using GPT.
    """
    conn = conn or get_connection()
    cur = conn.cursor()

    # 1) Compute embedding
    resp = openai.embeddings.create(input=[message], model=embedding_model)
    emb = resp.data[0].embedding
    blob = sqlite3.Binary(pickle.dumps(emb))

    # 2) Auto classify region
    region = classify_region_from_text(message)

    # 3) Insert
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message, embedding, region) VALUES (?, ?, ?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message, blob, region)
    )
    conn.commit()

# ──────────────────────────────────────────────────────────────────────────────
def load_all_skills(conn):
    cur = conn.cursor()
    cur.execute("SELECT trigger, action, path_or_command FROM skills")
    return cur.fetchall()

def recall_recent(limit: int = 5, conn=None) -> list[str]:
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [r["message"] for r in cur.fetchall()]

def recall_relevant(
    query: str,
    limit: int = 5,
    conn=None,
    embedding_model=EMBEDDING_MODEL
) -> list[tuple[str, float]]:
    from openai import embeddings
    conn = conn or get_connection()

    # Embed query
    resp = openai.embeddings.create(input=[query], model=embedding_model)
    q_emb = np.array(resp.data[0].embedding)

    # Pull embeddings from DB
    cur = conn.cursor()
    cur.execute("SELECT message, embedding FROM messages")
    rows = cur.fetchall()

    # Cosine similarity
    sims = []
    for row in rows:
        mem_emb = np.frombuffer(pickle.loads(row["embedding"]), dtype=np.float32)
        score = float(np.dot(q_emb, mem_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(mem_emb)))
        sims.append((row["message"], score))

    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:limit]
