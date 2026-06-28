import time

import requests

from aria.config import GROQ_MODELS_URL


def verify_groq_api_key(api_key: str, timeout: int = 10) -> tuple[bool, str]:
    if not api_key:
        return False, "API key is empty"
    try:
        response = requests.get(
            GROQ_MODELS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        if response.status_code == 200:
            return True, "Groq API connected"
        if response.status_code == 401:
            return False, "Invalid Groq API key"
        return False, f"Groq API returned status {response.status_code}"
    except requests.RequestException as exc:
        return False, f"Cannot reach Groq API: {exc}"


def cached_groq_status(api_key: str, cache_seconds: int = 300) -> tuple[bool, str]:
    now = time.time()
    cached = getattr(cached_groq_status, "_cache", None)
    if cached and cached["key"] == api_key and now - cached["ts"] < cache_seconds:
        return cached["ok"], cached["msg"]
    ok, msg = verify_groq_api_key(api_key)
    cached_groq_status._cache = {"key": api_key, "ok": ok, "msg": msg, "ts": now}
    return ok, msg
