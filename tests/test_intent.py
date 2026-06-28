import re

from aria.intent import WEB_TRIGGERS, detect_intent, is_document_question, _normalize_math_expr, _is_math_question
from aria.search import build_search_query


def test_web_search_prime_minister():
    intent, params = detect_intent("HOW IS PRIME MINISTER OF PAKISTAN")
    assert intent == "web_search"
    assert "pakistan" in params["query"].lower() or "minister" in params["query"].lower()


def test_pm_2026_not_calculator():
    intent, _ = detect_intent("HOW IS PRIME MINISTER OF PAKISTAN in 2026")
    assert intent == "web_search"


def test_weather_karachi_intent():
    intent, _ = detect_intent("weather in karachi")
    assert intent == "web_search"


def test_build_query_pm():
    q = build_search_query("HOW IS PRIME MINISTER OF PAKISTAN")
    assert "prime minister" in q.lower()
    assert "pakistan" in q.lower()


def test_build_query_weather():
    q = build_search_query("weather in karachi")
    assert "karachi" in q.lower()
    assert "weather" in q.lower()


def test_calculator_intent():
    intent, params = detect_intent("What is 234 * 56?")
    assert intent == "calculator"
    assert "234" in params["expression"]


def test_add_task_intent():
    intent, params = detect_intent("Add task: Study LangGraph")
    assert intent == "add_task"
    assert params["task"] == "Study LangGraph"


def test_plain_chat():
    intent, _ = detect_intent("Hello, how are you?")
    assert intent == "chat"


def test_search_prefix():
    intent, params = detect_intent("Search: latest AI news")
    assert intent == "web_search"
    assert "AI news" in params["query"]


def test_normalize_math():
    assert _normalize_math_expr("234 times 56") == "234*56"


def test_year_alone_not_math():
    assert not _is_math_question("in 2026")


def test_document_question_in_file():
    intent, params = detect_intent("what is in the file")
    assert intent == "search_my_documents"
    assert params["query"] == "what is in the file"


def test_document_question_uploaded_doc():
    intent, _ = detect_intent("what is in the document that i can uplode")
    assert intent == "search_my_documents"


def test_document_question_from_pdf():
    intent, _ = detect_intent("summarize my pdf")
    assert intent == "search_my_documents"


def test_is_document_question():
    assert is_document_question("what is in the file")
    assert not is_document_question("Hello, how are you?")
