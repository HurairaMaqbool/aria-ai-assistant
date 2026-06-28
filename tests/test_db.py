from aria.db import db_add_task, db_clear_chats, db_ensure_user, db_get_tasks, db_load_chats, db_save_chat


def test_chat_roundtrip():
    uid = "user_test1234"
    db_ensure_user(uid)
    db_clear_chats(uid)
    db_save_chat(uid, "user", "hello")
    db_save_chat(uid, "assistant", "hi there")
    messages = db_load_chats(uid)
    assert len(messages) == 2
    assert messages[0]["content"] == "hello"
    assert messages[1]["role"] == "assistant"


def test_task_add_and_list():
    uid = "user_tasktest"
    db_ensure_user(uid)
    db_add_task(uid, "Write tests")
    tasks = db_get_tasks(uid)
    assert any(t[1] == "Write tests" for t in tasks)
