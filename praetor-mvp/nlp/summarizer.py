# summarizer.py
import openai
import os
import logging

logger = logging.getLogger(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def log_event_json(event_type, message, data=None):
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "message": message,
        "data": data or {}
    }
    with open("logs/analyst_events.jsonl", "a") as log_file:
        log_file.write(json.dumps(event) + "\n")

def summarize_rss_item(item):
    prompt = f"""
You are an intelligence analyst. Summarize the following official government news article in 2-3 sentences, focusing on geopolitical, policy, or strategic impact. Include only verifiable information.

Title: {item['title']}
Source: {item['source']}
Content: {item['summary']}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a strategic summarizer for an AI geopolitical engine."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"[SUMMARY ERROR] {str(e)}"
