#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import importlib
import pkgutil
from datetime import datetime
from subprocess import DEVNULL

import openai
import numpy as np

# ─── Memory Core Imports ───────────────────────────────────────────
from memory.memory_core import (
    get_connection,
    load_all_skills,
    recall_recent,
    recall_relevant,
)

# ─── Skill Imports ─────────────────────────────────────────────────
from skills_py.weather import run as get_weather  # adjust import path if needed

# ─── Brain-State Constants ────────────────────────────────────────
from brain_state import COMMANDS, PY_SKILL_RUNNERS, SKILL_LIST

# ─── OpenAI Setup ─────────────────────────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

# ─── Initialize Persistent Memory ─────────────────────────────────
conn = get_connection()  # auto-creates DB/tables in memory/praetor_memory.db

# ─── Preload & Cache Trigger Embeddings ───────────────────────────
TRIGGER_EMBEDDINGS = {}
for trigger, action, cmd in load_all_skills(conn):
    try:
        resp = openai.embeddings.create(input=[trigger], model="text-embedding-ada-002")
        emb_list = resp.data[0].embedding  # list of floats
        vec = np.array(emb_list, dtype=float)
        TRIGGER_EMBEDDINGS[trigger] = vec
    except Exception as e:
        print(f"[⚠️] Embedding error for '{trigger}': {e}")

# ─── Load JSON/DB Skills ──────────────────────────────────────────
def load_skills(skill_dir="skills"):
    SKILL_LIST.clear()
    COMMANDS.clear()

    # File-based JSON skills
    if os.path.isdir(skill_dir):
        for filename in os.listdir(skill_dir):
            if filename.endswith(".json"):
                path = os.path.join(skill_dir, filename)
                try:
                    with open(path, "r") as f:
                        skill = json.load(f)
                    SKILL_LIST.append(skill)
                    for trig in skill.get("triggers", []):
                        COMMANDS[trig.lower()] = {
                            "action": skill["action"],
                            "path_or_command": skill.get("path_or_command", "")
                        }
                except Exception as e:
                    print(f"[⚠️] Failed to load {filename}: {e}")

    # DB-backed skills
    for trig, action, cmd in load_all_skills(conn):
        skill = {"triggers": [trig], "action": action, "path_or_command": cmd}
        SKILL_LIST.append(skill)
        COMMANDS[trig.lower()] = {"action": action, "path_or_command": cmd}

    # Precompute embeddings for fuzzy match on any new triggers
    for trig in list(COMMANDS.keys()):
        if trig not in TRIGGER_EMBEDDINGS:
            try:
                resp = openai.embeddings.create(input=[trig], model="text-embedding-ada-002")
                emb_list = resp.data[0].embedding
                vec = np.array(emb_list, dtype=float)
                TRIGGER_EMBEDDINGS[trig] = vec
            except Exception as e:
                print(f"[⚠️] Embedding error for '{trig}': {e}")

# ─── Load Python Skills ────────────────────────────────────────────
def load_py_skills(pkg_dir="skills_py"):
    for finder, name, ispkg in pkgutil.iter_modules([pkg_dir]):
        try:
            module = importlib.import_module(f"{pkg_dir}.{name}")
            if hasattr(module, "triggers") and hasattr(module, "run"):
                for trig in module.triggers:
                    key = trig.lower()
                    PY_SKILL_RUNNERS[key] = module.run
                    print(f"[🐍PY SKILL] Registered trigger: '{key}' from module: {name}")
        except Exception as e:
            print(f"[⚠️] Failed to load Python skill '{name}': {e}")

# ─── Build Prompt & Invoke LLM ─────────────────────────────────────
def build_system_prompt(user_input: str):
    """
    Construct a system prompt that injects both recent and relevant memories
    and lists available skills.
    """
    # 1) Fetch memory snippets
    recent   = recall_recent(limit=3)
    relevant = recall_relevant(query=user_input, limit=3)

    # 2) Format into bullet blocks
    recent_block   = "\n".join(f"- {m}" for m in recent) or "*(no recent memories)*"
    relevant_block = "\n".join(f"- {m} (score {s:.2f})" for m, s in relevant) or "*(no relevant memories)*"

    # 3) Assemble prompt lines
    prompt_lines = [
        "You are Praetor, a memory-aware AI assistant.",
        "",
        "Recent memories (most recent first):",
        recent_block,
        "",
        "Contextually relevant memories:",
        relevant_block,
        "",
        "Available skills:",
    ]
    for skill in SKILL_LIST:
        triggers = skill.get("triggers", [])
        cmd      = skill.get("path_or_command", "")
        prompt_lines.append(
            f"- {skill['action']}: triggers {triggers}, executes '{cmd}'"
        )

    prompt_lines.append("")
    prompt_lines.append('Respond with JSON exactly like: {"actions": [{"action": ..., "path_or_command": ...}]}')

    # 4) Join into one big prompt string
    return "\n".join(prompt_lines)

# ─── Invoke LLM and Execute Actions ─────────────────────────────────

def get_gpt_actions(user_input: str):
    system_prompt = build_system_prompt(user_input)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_input},
    ]
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        content = resp.choices[0].message.content.strip().lstrip("```json").rstrip("```")
        return json.loads(content).get("actions", [])
    except Exception as e:
        print(f"[⚠️] GPT error: {e}")
        return []

# ─── Execute an Action ────────────────────────────────────────────

def execute_action(action_cfg: dict):
    action = action_cfg.get("action")
    payload = action_cfg.get("path_or_command", "")
    print(f"[⚙️] Executing '{action}'")

    try:
        if action == "say_time":
            now = datetime.now().strftime("%H:%M")
            print(f"[⏰] Current time: {now}")

        elif action == "subprocess":
            subprocess.Popen(payload.split(), stdout=DEVNULL, stderr=DEVNULL)

        elif action == "system":
            subprocess.run(payload, shell=True, check=True)

        elif action == "script":
            subprocess.run(["bash", payload], check=True)

        elif action == "summarize":
            # If the brain asks to summarize, just print the summary text
            print("[📝 Summary]")
            print(payload)

        else:
            print(f"[❌] Unknown action '{action}'")

    except Exception as e:
        print(f"[⚠️] Execution error: {e}")
# ----Handle User Command ──────────────────────────────────────────
def handle_command(user_input: str):
    actions = get_gpt_actions(user_input)
    if not actions:
        print("[❓] No actions returned.")
        return
    for act in actions:
        execute_action(act)

# ─── Entry Point ───────────────────────────────────────────────────
if __name__ == "__main__":
    load_skills()
    load_py_skills()
    print("[✅] Brain module loaded. Use handle_command() to invoke.")
