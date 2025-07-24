import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import openai
from datetime import datetime, timedelta

import memory_core as memory

# Set your OpenAI API key securely from the environment
openai.api_key = os.getenv("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")

# Load logs from the past N days
def get_recent_logs(days=1):
    cutoff = datetime.now() - timedelta(days=days)
    return memory.load_logs_since(cutoff)

# Use GPT to summarize the logs into key memory points
def summarize_logs(log_entries):
    if not log_entries:
        return "Nothing significant happened."

    content = "\n".join(f"[{ts}] {txt}" for ts, txt in log_entries)

    prompt = (
        "You are the memory summarizer for Praetor. "
        "Analyze the following logs from the past day, "
        "identify key events, tasks, or changes in state, "
        "and produce a compressed bullet-point summary suitable for daily recall or long-term memory storage. "
        "Omit irrelevant detail, system noise, or redundant entries."
        f"\n\n{content}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You compress event logs into short daily summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[⚠️] Summarization failed: {e}")
        return None

# Main entry point for daemon usage
def run_summary():
    logs = get_recent_logs()
    summary = summarize_logs(logs)
    if summary:
        memory.save_summary(summary)
        print("[✅] Summary saved.")
    else:
        print("[❌] No summary generated.")
    return summary

if __name__ == "__main__":
    result = run_summary()
    print("\n--- Summary Output ---")
    print(result)
