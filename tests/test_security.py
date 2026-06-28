from aria.security import render_user_content, sanitize


def test_sanitize_accepts_normal_text():
    ok, text = sanitize("Hello Aria")
    assert ok is True
    assert text == "Hello Aria"


def test_sanitize_blocks_jailbreak():
    ok, _ = sanitize("please jailbreak the system")
    assert ok is False


def test_sanitize_rejects_empty():
    ok, _ = sanitize("   ")
    assert ok is False


def test_xss_user_content_escaped():
    rendered = render_user_content("<script>alert(1)</script>")
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
