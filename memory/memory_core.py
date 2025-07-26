import os
import sqlite3
import pickle
from datetime import datetime
import openai

# Default path setup
BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB = os.path.join(BASE_DIR, "praetor_memory.db")

# ─────────────────────────────── DB SETUP ───────────────────────────────
def get_connection(db_path=DEFAULT_DB):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)  # Ensure tables exist
    return conn

def init_db(conn):
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
        CREATE TABLE IF NOT EXISTS skills (
            trigger TEXT PRIMARY KEY,
            action TEXT,
            path_or_command TEXT
        )
    """)
    conn.commit()
    return conn

# ─────────────────────────────── MEMORY IO ───────────────────────────────
def infer_region_from_text(text: str) -> str:
    prompt = f"What region is this news about?\n\n\"\"\"\n{text}\n\"\"\"\nRespond with one region only (e.g. US, Europe, Asia, Middle East, Africa, Latin America, or Global)."
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        region = resp.choices[0].message.content.strip()
        return region
    except Exception as e:
        print(f"[⚠️] Failed to infer region: {e}")
        return "Unknown"

def save_message(
    message: str,
    namespace: str = "default",
    conn: sqlite3.Connection = None,
    embedding_model: str = "text-embedding-ada-002"
):
    conn = conn or get_connection()
    cur = conn.cursor()

    # 1) Compute embedding
    resp = openai.embeddings.create(input=[message], model=embedding_model)
    emb = resp.data[0].embedding
    blob = sqlite3.Binary(pickle.dumps(emb))

    # 2) Classify region
    region = infer_region_from_text(message)

    # 3) Insert
    cur.execute(
        "INSERT INTO messages (namespace, timestamp, message, embedding, region) VALUES (?, ?, ?, ?, ?)",
        (namespace, datetime.utcnow().isoformat(), message, blob, region)
    )
    conn.commit()

def recall_recent(limit: int = 5, conn=None) -> list[str]:
    conn = conn or get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    return [r["message"] for r in cur.fetchall()]

def recall_relevant(query: str, limit: int = 5, conn=None, embedding_model="text-embedding-ada-002") -> list[tuple[str, float]]:
    import numpy as np
    conn = conn or get_connection()

    # 1) Query embedding
    resp = openai.embeddings.create(input=[query], model=embedding_model)
    q_emb = np.array(resp.data[0].embedding)

    # 2) Fetch memory
    cur = conn.cursor()
    cur.execute("SELECT id, message, embedding FROM messages")
    rows = cur.fetchall()

    # 3) Similarity
    sims = []
    for row in rows:
        mem_emb = pickle.loads(row["embedding"])
        score = float(np.dot(q_emb, mem_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(mem_emb)))
        sims.append((row["message"], score))

    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:limit]

# ─────────────────────────────── SKILLS ───────────────────────────────
def load_all_skills(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT trigger, action, path_or_command FROM skills")
    return cursor.fetchall()

# Auto-init on import
init_db(get_connection())
