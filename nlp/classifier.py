# classifier.py
def classify_event(item):
    prompt = f"""
Classify the following government news article into one or more of the following categories:
- geopolitical
- domestic policy
- foreign policy
- military
- economy
- legal/judicial
- environment
- cybersecurity
- disinformation
- health/public safety

Return the list of categories as a JSON array.

Title: {item['title']}
Summary: {item.get('ai_summary') or item['summary']}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a policy analyst classifying news for a geopolitical AI system."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100
        )
        return eval(response.choices[0].message['content'].strip())
    except Exception as e:
        return [f"[CLASSIFICATION ERROR] {str(e)}"]
