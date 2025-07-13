# summarizer.py
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

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
