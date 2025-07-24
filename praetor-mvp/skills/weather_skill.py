import requests
import datetime
import os
import json

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Set this in your .env file
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city: str) -> dict:
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial"  # or "metric" for Celsius
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "timestamp": str(datetime.datetime.now())
        }
    else:
        return {"error": f"Failed to get weather for {city}", "status": response.status_code}

# Example usage:
if __name__ == "__main__":
    result = get_weather("Chicago")
    print(json.dumps(result, indent=2))
