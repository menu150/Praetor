from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from memory.memory_core import get_connection
import sqlite3

router = APIRouter(prefix="/skills", tags=["skills"])

# Pydantic model for toggling
class SkillToggle(BaseModel):
    trigger: str
    enabled: bool

# DB dependency
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

@router.get("/", response_model=list[SkillToggle])
def list_skills(conn: sqlite3.Connection = Depends(get_db)):
    cur = conn.cursor()
    # Ensure the "enabled" column exists; if not, defaults to True
    cur.execute("PRAGMA table_info(skills)")
    cols = [c[1] for c in cur.fetchall()]
    has_enabled = "enabled" in cols
    rows = cur.execute("SELECT trigger, enabled FROM skills").fetchall() if has_enabled else cur.execute("SELECT trigger, 1 AS enabled FROM skills").fetchall()
    return [SkillToggle(trigger=r["trigger"], enabled=bool(r["enabled"])) for r in rows]

@router.post("/toggle", response_model=SkillToggle)
def toggle_skill(payload: SkillToggle, conn: sqlite3.Connection = Depends(get_db)):
    cur = conn.cursor()
    # Check existence
    cur.execute("SELECT 1 FROM skills WHERE trigger = ?", (payload.trigger,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Skill not found")
    # Add "enabled" column if missing
    cur.execute("PRAGMA table_info(skills)")
    if "enabled" not in [c[1] for c in cur.fetchall()]:
        cur.execute("ALTER TABLE skills ADD COLUMN enabled INTEGER DEFAULT 1")
    # Update flag
    cur.execute(
        "UPDATE skills SET enabled = ? WHERE trigger = ?",
        (1 if payload.enabled else 0, payload.trigger)
    )
    conn.commit()
    return payload
