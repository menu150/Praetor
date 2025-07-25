#!/usr/bin/env python3
import os
import sys

# Ensure the project root is on the module search path
top = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, top)

# Initialize memory (tables)
from memory.memory_core import init_db, DEFAULT_DB
init_db(db_path=DEFAULT_DB)

# Import and load the Brain modules
from brain import load_skills, load_py_skills
from brain_state import SKILL_LIST, PY_SKILL_RUNNERS

# Load both JSON/DB and Python skills
def main():
    load_skills()
    load_py_skills()

    print("\n=== JSON/DB Skills (loaded from skills table & JSON) ===")
    if SKILL_LIST:
        for skill in SKILL_LIST:
            triggers = skill.get("triggers", [])
            action   = skill.get("action")
            cmd      = skill.get("path_or_command")
            print(f"- Action: {action}\n  Triggers: {triggers}\n  Cmd: {cmd}\n")
    else:
        print("(None loaded)")

    print("\n=== Python Skills (from skills_py/) ===")
    if PY_SKILL_RUNNERS:
        for trig, runner in PY_SKILL_RUNNERS.items():
            print(f"- Trigger: '{trig}' -> Function: {runner.__module__}.{runner.__name__}")
    else:
        print("(None loaded)")

if __name__ == '__main__':
    main()
