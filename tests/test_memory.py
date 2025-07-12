import importlib
import sqlite3
import sys
from pathlib import Path


def test_save_and_load_skills(tmp_path, monkeypatch):
    db_path = tmp_path / "skills.db"
    monkeypatch.setenv("MEMORY_DB_PATH", str(db_path))
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    import memory_core
    importlib.reload(memory_core)

    conn = memory_core.init_db()
    memory_core.save_skill("hello", "say_hello", "echo hello", conn)
    memory_core.save_skill("bye", "say_bye", "echo bye", conn)
    conn.close()

    new_conn = sqlite3.connect(db_path)
    skills = memory_core.load_all_skills(new_conn)
    assert ("hello", "say_hello", "echo hello") in skills
    assert ("bye", "say_bye", "echo bye") in skills

