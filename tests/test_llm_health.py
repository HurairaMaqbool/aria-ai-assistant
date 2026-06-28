from unittest.mock import MagicMock, patch

from aria.llm_health import verify_groq_api_key


def test_verify_groq_empty_key():
    ok, msg = verify_groq_api_key("")
    assert ok is False
    assert "empty" in msg.lower()


@patch("aria.llm_health.requests.get")
def test_verify_groq_success(mock_get):
    mock_get.return_value = MagicMock(status_code=200)
    ok, msg = verify_groq_api_key("test-key")
    assert ok is True
    assert "connected" in msg.lower()


@patch("aria.llm_health.requests.get")
def test_verify_groq_invalid_key(mock_get):
    mock_get.return_value = MagicMock(status_code=401)
    ok, msg = verify_groq_api_key("bad-key")
    assert ok is False
    assert "invalid" in msg.lower()
