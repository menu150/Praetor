import os
import sys
import json
import subprocess
import importlib
import pkgutil
from datetime import datetime

import openai
import numpy as np

import memory
from brain_state import COMMANDS, PY_SKILL_RUNNERS, SKILL_LIST

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize persistent memory (SQLite)
conn = memory.init_db()

# Embeddings cache for fuzzy matching
TRIGGER_EMBEDDINGS = {}

from subprocess import DEVNULL

def load_skills(skill_dir="skills"):
    """
    Load skills from JSON files and persistent DB into SKILL_LIST and COMMANDS,
    then build embeddings for each trigger.
    """
    SKILL_LIST.clear()
    COMMANDS.clear()

    # 1) Load from filesystem
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

    # 2) Load from persistent DB
    for trig, action, cmd in memory.load_all_skills(conn):
        skill = {"triggers": [trig], "action": action, "path_or_command": cmd}
        SKILL_LIST.append(skill)
        COMMANDS[trig] = {"action": action, "path_or_command": cmd}

    # 3) Build/refresh embeddings for fuzzy matching
    for trig in COMMANDS:
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
    Dynamically import Python skill modules and register their triggers.
    """
    for _, name, _ in pkgutil.iter_modules([pkg_dir]):
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
    Build the system prompt listing all loaded skills for GPT routing.
    """
    prompt = (
        "You are Praetor, an intelligent AI brain that routes user commands to available system actions.\n\n"
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
        "\nRespond with valid JSON: {\"actions\": [ {\"action\": ..., \"path_or_command\": ...} ] }\n"
    )
    return prompt

def get_gpt_actions(user_input):
    """
    Use GPT to interpret user input into a list of actions.
    """
    system_prompt = build_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_input}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        content = response.choices[0].message.content
    except Exception as e:
        print(f"[⚠️] GPT error: {e}")
        return []

    # Strip Markdown fences and parse JSON
    cleaned = content.strip().lstrip("```json").rstrip("```").strip()
    try:
        result = json.loads(cleaned)
        return result.get("actions", [])
    except json.JSONDecodeError:
        print(f"[⚠️] Failed to parse GPT JSON: {cleaned}")
        return []

def find_best_trigger(user_input, threshold=0.75):
    """
    Find the closest matching trigger via cosine similarity of embeddings.
    """
    try:
        resp = openai.embeddings.create(
            model="text-embedding-3-small",
            input=user_input.lower()
        )
        inp_vec = np.array(resp.data[0].embedding)
    except Exception as e:
        return None

    best_trig, best_score = None, -1.0
    for trig, vec in TRIGGER_EMBEDDINGS.items():
        score = float(np.dot(inp_vec, vec) /
                      (np.linalg.norm(inp_vec) * np.linalg.norm(vec)))
        if score > best_score:
            best_trig, best_score = trig, score

    return best_trig if best_score >= threshold else None

def execute_action(action_cfg):
    """
    Execute a single action dict.
    """
    action = action_cfg.get("action")
    path = action_cfg.get("path_or_command", "")
    print(f"[⚙️] Executing '{action}' -> '{path}'")
    try:
        if action == "say_time":
            now = datetime.now().strftime("%H:%M")
            print(f"[⏰] Current time: {now}")
        elif action == "subprocess":
            subprocess.Popen(
                path.split(),
                stdout=DEVNULL,
                stderr=DEVNULL
            )
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
    Route and execute user commands: Python skills → JSON/DB → fuzzy → GPT.
    """
    text = user_input.strip().lower()
    actions = []

    # 1) Python skills (prefix match)
    for trigger, runner in PY_SKILL_RUNNERS.items():
        if text.startswith(trigger):
            result = runner(user_input)
            actions = result if isinstance(result, list) else [result]
            break

    # 2) Static JSON/DB skills (exact match)
    if not actions and text in COMMANDS:
        actions = [COMMANDS[text]]

    # 3) Fuzzy match on JSON/DB triggers
    if not actions:
        best = find_best_trigger(user_input)
        if best:
            actions = [COMMANDS[best]]

    # 4) Fallback to GPT
    if not actions:
        actions = get_gpt_actions(user_input)

    if not actions:
        print("[❓] No actions returned.")
        return

    for act in actions:
        execute_action(act)

def chat_mode():
    """
    Interactive chat loop.
    """
    print("[💬] Praetor Chat Mode. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("🧠> ")
            if user_input.lower() in ["exit", "quit"]:
                print("[👋] Goodbye.")
                break
            handle_command(user_input)
        except KeyboardInterrupt:
            print("\n[👋] Interrupted. Exiting.")
            break

if __name__ == "__main__":
    load_skills()
    load_py_skills()

    if "--chat" in sys.argv or len(sys.argv) == 1:
        chat_mode()
    else:
        handle_command(sys.argv[1])
