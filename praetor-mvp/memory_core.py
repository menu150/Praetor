import os
import sqlite3
from datetime import datetime

DB_PATH = os.getenv("MEMORY_DB_PATH", "praetor_memory.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Skills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger TEXT UNIQUE,
            action TEXT,
            path_or_command TEXT
        )
    """)

    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            content TEXT
        )
    """)

    # Summaries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            summary TEXT
        )
    """)

    # (Planned) Embeddings table for semantic recall
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            content TEXT,
            embedding BLOB
        )
    """)

    conn.commit()
    return conn

# ---------- Skill Handling ----------

def save_skill(trigger, action, command, conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO skills (trigger, action, path_or_command) VALUES (?, ?, ?)",
        (trigger, action, command)
    )
    conn.commit()

def load_all_skills(conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT trigger, action, path_or_command FROM skills")
    return cursor.fetchall()

# ---------- Logs ----------

def save_log(message, conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (timestamp, content) VALUES (?, ?)",
        (datetime.now().isoformat(), message)
    )
    conn.commit()

def load_logs_since(cutoff_dt, conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, content FROM logs WHERE timestamp >= ? ORDER BY timestamp ASC",
        (cutoff_dt.isoformat(),)
    )
    return cursor.fetchall()

# ---------- Summaries ----------

def save_summary(summary_text, conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memory_summaries (timestamp, summary) VALUES (?, ?)",
        (datetime.now().isoformat(), summary_text)
    )
    conn.commit()

def load_recent_summaries(limit=10, conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, summary FROM memory_summaries ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    return cursor.fetchall()

# ---------- (Planned) Embedding Functions ----------

def save_embedding(content, vector_bytes, conn=None):
    conn = conn or init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memory_embeddings (timestamp, content, embedding) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), content, vector_bytes)
    )
    conn.commit()

def search_embeddings(query_vector, top_n=5, conn=None):
    # Placeholder for future: cosine similarity search over stored embeddings
    raise NotImplementedError("Semantic search not yet implemented.")


