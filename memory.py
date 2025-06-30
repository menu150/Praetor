import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "praetor_memory.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS skills (
      trigger TEXT PRIMARY KEY,
      action   TEXT NOT NULL,
      command  TEXT NOT NULL
    )
    """)
    conn.commit()
    return conn

def load_all_skills(conn):
    c = conn.cursor()
    c.execute("SELECT trigger, action, command FROM skills")
    return c.fetchall()  # list of (trigger, action, command)

def save_skill(conn, trigger, action, command):
    c = conn.cursor()
    c.execute(
      "INSERT OR REPLACE INTO skills(trigger, action, command) VALUES (?,?,?)",
      (trigger, action, command)
    )
    conn.commit()
# Create a module‐level connection for ease of import
conn = init_db()
