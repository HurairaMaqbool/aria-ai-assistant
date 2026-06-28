from unittest.mock import MagicMock, patch

from aria.search import build_search_query, run_web_search, _format_results


def test_format_results():
    text = _format_results([{"title": "Test", "body": "Body text", "href": "https://x.com"}])
    assert "Test" in text
    assert "Body text" in text


def test_build_query_fixes_how_is():
    q = build_search_query("HOW IS PRIME MINISTER OF PAKISTAN")
    assert "who is" in q.lower() or "prime minister" in q.lower()


@patch("ddgs.DDGS")
def test_run_web_search_returns_formatted(mock_ddgs_cls):
    mock_ddgs = MagicMock()
    mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
    mock_ddgs.text.return_value = [
        {"title": "Shehbaz Sharif", "body": "Prime Minister of Pakistan", "href": "https://example.com"}
    ]
    result = run_web_search("prime minister of pakistan")
    assert "Shehbaz" in result or "Prime Minister" in result
