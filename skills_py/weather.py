import re
from skills.weather_skill import get_weather  # Make sure this exists in /skills

triggers = ["weather", "forecast", "temperature"]

# extracts from prompt
import spacy
nlp = spacy.load("en_core_web_sm")

def extract_city(user_input: str) -> str:
    doc = nlp(user_input)
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):  # GPE = Geo-Political Entity
            return ent.text
    return "Chicago"  # fallback


def run(user_input: str) -> dict:
    city = extract_city(user_input)
    result = get_weather(city)
    result["queried_city"] = city
    print(f"[🌤️] Weather result for {city}: {result}")
    return result
