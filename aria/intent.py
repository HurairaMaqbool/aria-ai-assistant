import re

WEB_TRIGGERS = re.compile(
    r"(?i)\b("
    r"who is|who was|who are|what is the|what's the|how is|how's|"
    r"current|latest|today|right now|this week|this year|in 20\d{2}|"
    r"prime minister|president|ceo of|news about|weather in|weather for|"
    r"stock price|live score|tell me about|look up|"
    r"search web|search:|find online|temperature in"
    r")\b"
)

MATH_OPERATORS = re.compile(r"\d+\s*[\+\-\*\/×÷\^]\s*\d+")
MATH_WORDS = re.compile(r"(?i)\b(calculate|compute|solve)\b")
PURE_MATH = re.compile(r"(?i)^(?:what is|what's)?\s*[\d\s\.\+\-\*\/\(\)]+$")

TASK_ADD = re.compile(r"(?i)^(?:add task|add a task)[:\s]+(.+)$")
TASK_COMPLETE = re.compile(r"(?i)^(?:complete task|mark done|finish task)[:\s]+(.+)$")
TASK_DELETE = re.compile(r"(?i)^(?:delete task|remove task)[:\s]+(.+)$")
TASK_LIST = re.compile(r"(?i)^(list tasks|show tasks|my tasks|tasks list)$")
NOTE_SAVE = re.compile(r"(?i)^(?:save note|add note)[:\s]+(.+)$")
NOTE_LIST = re.compile(r"(?i)^(list notes|show notes|my notes)$")
DOC_SEARCH = re.compile(
    r"(?i)(?:"
    r"\b(?:in|from|about|read|search|check|summarize|summarise|explain|tell me about)\s+"
    r"(?:the\s+|my\s+)?(?:uploaded\s+)?(?:file|document|doc|pdf|upload)\b|"
    r"\b(?:what(?:'s| is)|whats)\s+in\s+(?:the\s+|my\s+)?(?:uploaded\s+)?(?:file|document|doc|pdf)\b|"
    r"\b(?:file|document|doc|pdf|upload)\s+(?:content|summary|say|says|contains|about)\b|"
    r"\b(?:in my document|my documents|uploaded file|uploaded doc|from my pdf|in the pdf)\b|"
    r"\bwhat\s+(?:does|do)\s+(?:the\s+|my\s+)?(?:file|document|doc|pdf)\s+say\b|"
    r"\b(?:according to|based on)\s+(?:the\s+|my\s+)?(?:document|file|pdf|upload)\b"
    r")"
)


def is_document_question(text: str) -> bool:
    return bool(DOC_SEARCH.search(text.strip()))


def _normalize_math_expr(text: str) -> str:
    expr = text.strip()
    expr = re.sub(r"(?i)^(?:what is|what's|calculate|compute|solve)\s*", "", expr).strip()
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    expr = re.sub(r"(?i)(\d+)\s*times\s*(\d+)", r"\1*\2", expr)
    expr = re.sub(r"(?i)(\d+)\s*multiplied by\s*(\d+)", r"\1*\2", expr)
    expr = re.sub(r"(?i)(\d+)\s*plus\s*(\d+)", r"\1+\2", expr)
    expr = re.sub(r"(?i)(\d+)\s*minus\s*(\d+)", r"\1-\2", expr)
    expr = re.sub(r"(?i)(\d+)\s*divided by\s*(\d+)", r"\1/\2", expr)
    return re.sub(r"\s+", "", expr).strip("?.!")


def _is_math_question(text: str) -> bool:
    if WEB_TRIGGERS.search(text):
        return False
    cleaned = text.strip().rstrip("?.!")
    if MATH_OPERATORS.search(cleaned):
        return True
    if MATH_WORDS.search(cleaned):
        return True
    if PURE_MATH.match(cleaned):
        return True
    return False


def detect_intent(text: str) -> tuple[str, dict]:
    cleaned = text.strip()

    if m := TASK_ADD.match(cleaned):
        return "add_task", {"task": m.group(1).strip()}
    if m := TASK_COMPLETE.match(cleaned):
        return "complete_task", {"task_name": m.group(1).strip()}
    if m := TASK_DELETE.match(cleaned):
        return "delete_task", {"task_name": m.group(1).strip()}
    if TASK_LIST.match(cleaned):
        return "list_tasks", {}
    if m := NOTE_SAVE.match(cleaned):
        return "save_note", {"note_input": m.group(1).strip()}
    if NOTE_LIST.match(cleaned):
        return "list_notes", {}

    if is_document_question(cleaned):
        return "search_my_documents", {"query": cleaned}

    if cleaned.lower().startswith("search:"):
        return "web_search", {"query": cleaned[7:].strip() or cleaned}

    if WEB_TRIGGERS.search(cleaned):
        return "web_search", {"query": cleaned}

    if _is_math_question(cleaned):
        expr = _normalize_math_expr(cleaned)
        if expr and re.search(r"\d", expr):
            return "calculator", {"expression": expr}

    return "chat", {}


def is_groq_tool_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "tool_use_failed" in msg or "failed to call a function" in msg
