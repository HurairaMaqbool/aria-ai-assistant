import uuid

from aria.memory import build_rag, search_docs


def test_search_docs_returns_excerpts():
    user_id = f"doc_test_{uuid.uuid4().hex[:8]}"
    build_rag(user_id, "Python is a programming language. It is used for AI and web apps.", "notes.txt")
    result = search_docs(user_id, "what is in the file")
    assert "UPLOADED DOCUMENT EXCERPTS" in result
    assert "Python" in result
    assert "notes.txt" in result


def test_search_docs_no_uploads():
    user_id = f"empty_{uuid.uuid4().hex[:8]}"
    result = search_docs(user_id, "what is in the file")
    assert "No documents uploaded yet" in result
