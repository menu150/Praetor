import os, httpx, openai

NEWSAPI_KEY   = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not NEWSAPI_KEY or not OPENAI_API_KEY:
    raise RuntimeError("Missing NEWSAPI_KEY or OPENAI_API_KEY in .env")

openai.api_key = OPENAI_API_KEY

def fetch(region: str, n: int = 5) -> float:
    # 1) Pull headlines
    resp = httpx.get(
        "https://newsapi.org/v2/top-headlines",
        params={"q": region, "pageSize": n, "language": "en", "apiKey": NEWSAPI_KEY},
        timeout=10
    ).json()
    titles = [a["title"] for a in resp.get("articles", []) if a.get("title")]
    if not titles:
        return 0.5

    # 2) Ask OpenAI for sentiment
    prompt = (
        "Rate the overall sentiment of these headlines from 0 (very neg) to 1 (very pos)."
        "\n\n" + "\n".join(f"- {t}" for t in titles)
    )
    chat = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    ).choices[0].message.content

    # 3) Parse result
    try:
        data = __import__("json").loads(chat)
        return float(data.get("average_sentiment", 0.5))
    except:
        return 0.5
