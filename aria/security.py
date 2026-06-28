import html
import re
import time

import bleach
import markdown

MAX_INPUT_LENGTH = 2000
BLOCKED = [
    "ignore previous instructions",
    "ignore all instructions",
    "reveal system prompt",
    "forget everything",
    "you are now dan",
    "jailbreak",
    "dan mode",
]
BLEACH_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    "p", "br", "pre", "code", "table", "thead", "tbody", "tr", "th", "td",
    "h1", "h2", "h3", "h4", "ul", "ol", "li", "strong", "em", "a", "blockquote",
}
BLEACH_ATTRS = {"a": ["href", "title"]}

request_log: dict[str, list[float]] = {}


def render_user_content(text_content: str) -> str:
    return html.escape(text_content).replace("\n", "<br>")


def render_assistant_content(text_content: str) -> str:
    try:
        raw_html = markdown.markdown(
            text_content, extensions=["fenced_code", "tables", "nl2br"]
        )
    except Exception:
        raw_html = markdown.markdown(
            text_content, extensions=["fenced_code", "tables"]
        )
    return bleach.clean(raw_html, tags=BLEACH_TAGS, attributes=BLEACH_ATTRS, strip=True)


def sanitize(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "Empty input."
    if len(text) > MAX_INPUT_LENGTH:
        return False, "Too long (max 2000 chars)."
    text_lower = text.lower()
    for phrase in BLOCKED:
        if phrase in text_lower:
            return False, "⚠️ Suspicious input blocked."
    return True, re.sub(r"<[^>]+>", "", text).strip()


def rate_limit(user_id: str, max_req: int = 15, window: int = 60) -> bool:
    now = time.time()
    if user_id not in request_log:
        request_log[user_id] = []
    request_log[user_id] = [t for t in request_log[user_id] if now - t < window]
    if len(request_log[user_id]) >= max_req:
        return False
    request_log[user_id].append(now)
    return True
