import re
import time
import urllib.parse

from aria.weather import extract_city, fetch_live_weather

SEARCH_BACKENDS = ("html", "lite", "auto")
SEARCH_REGIONS = ("wt-wt", "us-en", "pk-en", "uk-en")


def build_search_query(text: str) -> str:
    query = text.strip().rstrip("?.!")
    lower = query.lower()

    if re.search(r"(?i)\bhow is\b", query) and re.search(
        r"(?i)\b(prime minister|president|ceo|minister|leader|governor|mayor)\b", query
    ):
        query = re.sub(r"(?i)\bhow is\b", "who is the current", query)

    if re.search(r"(?i)\bweather in\b", lower):
        city_match = re.search(r"(?i)weather in\s+([a-zA-Z\s]+)", query)
        if city_match:
            city = city_match.group(1).strip()
            pak_cities = ("karachi", "lahore", "islamabad", "rawalpindi", "peshawar", "multan", "faisalabad")
            if any(c in city.lower() for c in pak_cities):
                return f"current weather {city} Pakistan today"
            return f"current weather {city} today"

    if "prime minister" in lower and "pakistan" in lower:
        return "current Prime Minister of Pakistan 2026"
    if "prime minister of pakistan" in lower or (
        "prime minister" in lower and "pakistan" not in lower and len(query.split()) <= 8
    ):
        return "current Prime Minister of Pakistan 2026"

    if lower.startswith("search:"):
        return query[7:].strip() or query

    return query


def _format_results(results: list[dict]) -> str:
    if not results:
        return ""
    blocks = []
    for i, item in enumerate(results[:5], 1):
        title = item.get("title", "").strip()
        body = item.get("body", item.get("snippet", "")).strip()
        href = item.get("href", item.get("link", "")).strip()
        if not title and not body:
            continue
        block = f"{i}. **{title}**"
        if body:
            block += f"\n{body}"
        if href:
            block += f"\nSource: {href}"
        blocks.append(block)
    return "\n\n".join(blocks)


def run_web_search(raw_query: str) -> str:
    if extract_city(raw_query):
        live = fetch_live_weather(raw_query)
        if live:
            return f"LIVE WEATHER DATA:\n{live}"

    query = build_search_query(raw_query)

    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    last_error = None
    for backend in SEARCH_BACKENDS:
        for region in SEARCH_REGIONS:
            try:
                with DDGS(timeout=25) as ddgs:
                    kwargs = {"max_results": 5}
                    if backend != "auto":
                        kwargs["backend"] = backend
                    try:
                        results = list(ddgs.text(query, region=region, **kwargs))
                    except TypeError:
                        results = list(ddgs.text(query, **kwargs))
                formatted = _format_results(results)
                if formatted:
                    return formatted
            except Exception as exc:
                last_error = exc
                time.sleep(0.4)

    alt_queries = [
        query,
        build_search_query(raw_query) + " latest",
        raw_query.strip(),
    ]
    seen = set()
    for alt in alt_queries:
        if alt in seen:
            continue
        seen.add(alt)
        try:
            with DDGS(timeout=25) as ddgs:
                results = list(ddgs.text(alt, backend="html", max_results=5))
            formatted = _format_results(results)
            if formatted:
                return formatted
        except Exception as exc:
            last_error = exc

    if last_error:
        return f"Search error: {last_error}"
    return "No results found. Try rephrasing your question."
