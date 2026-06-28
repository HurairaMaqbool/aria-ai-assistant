import json
import re
import urllib.parse
import urllib.request

WEATHER_CITY = re.compile(r"(?i)weather(?:\s+in|\s+for)?\s+([a-zA-Z\s]+)")


def extract_city(raw_query: str) -> str | None:
    m = WEATHER_CITY.search(raw_query.strip())
    if not m:
        return None
    city = m.group(1).strip().rstrip("?.!")
    pak_cities = ("karachi", "lahore", "islamabad", "rawalpindi", "peshawar", "multan", "faisalabad")
    if any(c in city.lower() for c in pak_cities) and "pakistan" not in city.lower():
        city = f"{city}, Pakistan"
    return city


def fetch_live_weather(raw_query: str) -> str | None:
    city = extract_city(raw_query)
    if not city:
        return None
    try:
        encoded = urllib.parse.quote(city)
        req = urllib.request.Request(
            f"https://wttr.in/{encoded}?format=j1",
            headers={"User-Agent": "Aria-AI-Assistant/1.0"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        cur = data["current_condition"][0]
        area = data["nearest_area"][0]
        place = area["areaName"][0]["value"]
        region = area.get("region", [{}])[0].get("value", "")
        country = area.get("country", [{}])[0].get("value", "")
        location = ", ".join(p for p in (place, region, country) if p)
        temp_c = cur["temp_C"]
        feels = cur["FeelsLikeC"]
        desc = cur["weatherDesc"][0]["value"]
        humidity = cur["humidity"]
        wind = cur["windspeedKmph"]
        return (
            f"Location: {location}\n"
            f"Temperature: {temp_c}°C (feels like {feels}°C)\n"
            f"Conditions: {desc}\n"
            f"Humidity: {humidity}%\n"
            f"Wind: {wind} km/h"
        )
    except Exception:
        return None
