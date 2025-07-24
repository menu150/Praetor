import sqlite3


def get_connection(db_path="praetor_memory.db"):
    """
    Return a sqlite3 connection to the memory database.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
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
