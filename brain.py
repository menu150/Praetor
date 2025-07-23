import os
import sys
import json
import subprocess
import importlib
import pkgutil
from datetime import datetime
from skills.weather_skill import get_weather
import openai
import numpy as np

# Memory core imports
from memory.memory_core import get_connection, load_all_skills
from brain_state import COMMANDS, PY_SKILL_RUNNERS, SKILL_LIST

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize persistent memory (SQLite)
conn = get_connection()

# Embeddings cache for fuzzy matching
TRIGGER_EMBEDDINGS = {}

# Shortcut for subprocess silence
from subprocess import DEVNULL

def load_skills(skill_dir="skills"):
    """
    Load JSON-defined skills from disk and from the database.
    Populates SKILL_LIST and COMMANDS.
    """
    SKILL_LIST.clear()
    COMMANDS.clear()

    # Load file-based JSON skills
    if os.path.isdir(skill_dir):
        for filename in os.listdir(skill_dir):
            if filename.endswith(".json"):
                path = os.path.join(skill_dir, filename)
                try:
                    with open(path, "r") as f:
                        skill = json.load(f)
                    SKILL_LIST.append(skill)
                    for trigger in skill.get("triggers", []):
                        COMMANDS[trigger.lower()] = {
                            "action": skill["action"],
                            "path_or_command": skill.get("path_or_command", "")
                        }
                except Exception as e:
                    print(f"[⚠️] Failed to load {filename}: {e}")

    # Load DB-backed skills
    for trig, action, cmd in load_all_skills(conn):
        skill = {"triggers": [trig], "action": action, "path_or_command": cmd}
        SKILL_LIST.append(skill)
        COMMANDS[trig.lower()] = {"action": action, "path_or_command": cmd}

    # Precompute embeddings for fuzzy match
    for trig in list(COMMANDS.keys()):
        if trig not in TRIGGER_EMBEDDINGS:
            try:
                resp = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=trig
                )
                vec = np.array(resp.data[0].embedding)
                TRIGGER_EMBEDDINGS[trig] = vec
            except Exception as e:
                print(f"[⚠️] Embedding error for '{trig}': {e}")


def load_py_skills(pkg_dir="skills_py"):
    """
    Dynamically import Python skills modules under skills_py/.
    Each module must define `triggers` list and a `run()` function.
    """
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


def build_system_prompt():
    """
    Construct a system prompt listing all loaded skills for the LLM.
    """
    prompt = (
        "You are Praetor, an AI brain routing user commands to system actions.\n\n"
        "Available JSON/DB skills:\n"
    )
    for skill in SKILL_LIST:
        triggers = skill.get("triggers", [])
        cmd = skill.get("path_or_command", "")
        prompt += f"- {skill['action']}: triggers {triggers}, executes '{cmd}'\n"

    prompt += "\nAvailable Python skills (prefix-match):\n"
    for key, runner in PY_SKILL_RUNNERS.items():
        prompt += f"- '{key}' -> module {runner.__module__}\n"

    prompt += (
        "\nRespond with JSON exactly like: {\"actions\": [ {\"action\": ..., \"path_or_command\": ...} ] }"
    )
    return prompt


def get_gpt_actions(user_input):
    """
    Ask the LLM to choose actions based on the system prompt and user_input.
    Returns a list of action dicts.
    """
    system_prompt = build_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_input}
    ]
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        content = resp.choices[0].message.content
    except Exception as e:
        print(f"[⚠️] GPT error: {e}")
        return []

    cleaned = content.strip().lstrip("```json").rstrip("```").strip()
    try:
        result = json.loads(cleaned)
        return result.get("actions", [])
    except json.JSONDecodeError:
        print(f"[⚠️] Failed to parse GPT JSON: {cleaned}")
        return []


def execute_action(action_cfg):
    """
    Execute a single action dict returned by get_gpt_actions().
    """
    action = action_cfg.get("action")
    path = action_cfg.get("path_or_command", "")
    print(f"[⚙️] Executing '{action}' -> '{path}'")
    try:
        if action == "say_time":
            now = datetime.now().strftime("%H:%M")
            print(f"[⏰] Current time: {now}")
        elif action == "subprocess":
            subprocess.Popen(path.split(), stdout=DEVNULL, stderr=DEVNULL)
        elif action == "system":
            subprocess.run(path, shell=True, check=True)
        elif action == "script":
            subprocess.run(["bash", path], check=True)
        else:
            print(f"[❌] Unknown action '{action}'")
    except Exception as e:
        print(f"[⚠️] Execution error: {e}")


def handle_command(user_input):
    """
    Top‑level entry: sends user_input to the LLM, then runs all chosen actions.
    """
    actions = get_gpt_actions(user_input)
    if not actions:
        print("[❓] No actions returned.")
        return
    for act in actions:
        execute_action(act)


if __name__ == "__main__":
    load_skills()
    load_py_skills()
    print("[✅] Brain module loaded. Use handle_command() or your API to invoke it.")
