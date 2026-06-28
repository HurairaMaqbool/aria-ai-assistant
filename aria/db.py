import uuid
from datetime import datetime

from sqlalchemy import create_engine, text

from aria.config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}")


def init_db() -> None:
    with engine.connect() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS users
            (id TEXT PRIMARY KEY, username TEXT UNIQUE, created_at TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS chats
            (id TEXT PRIMARY KEY, user_id TEXT, role TEXT, content TEXT, timestamp TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS tasks
            (id TEXT PRIMARY KEY, user_id TEXT, task TEXT, done INTEGER DEFAULT 0, created_at TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS notes
            (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, content TEXT, created_at TEXT)"""))
        conn.commit()


init_db()


def db_ensure_user(user_id: str) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("INSERT OR IGNORE INTO users (id, username, created_at) VALUES (:id, :name, :ts)"),
            {"id": user_id, "name": user_id, "ts": datetime.now().isoformat()},
        )
        conn.commit()


def db_save_chat(user_id: str, role: str, content: str) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO chats (id,user_id,role,content,timestamp) VALUES (:id,:user_id,:role,:content,:ts)"),
            {"id": str(uuid.uuid4()), "user_id": user_id, "role": role, "content": content, "ts": datetime.now().isoformat()},
        )
        conn.commit()


def db_load_chats(user_id: str, limit: int = 200) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT role, content, timestamp FROM chats WHERE user_id=:uid ORDER BY timestamp ASC LIMIT :lim"),
            {"uid": user_id, "lim": limit},
        ).fetchall()
    messages = []
    for role, content, ts in rows:
        try:
            timestamp = datetime.fromisoformat(ts).strftime("%I:%M %p")
        except (TypeError, ValueError):
            timestamp = ""
        messages.append({"role": role, "content": content, "timestamp": timestamp})
    return messages


def db_clear_chats(user_id: str) -> None:
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM chats WHERE user_id=:uid"), {"uid": user_id})
        conn.commit()


def db_add_task(user_id: str, task: str) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO tasks (id,user_id,task,done,created_at) VALUES (:id,:uid,:task,0,:ts)"),
            {"id": str(uuid.uuid4()), "uid": user_id, "task": task, "ts": datetime.now().isoformat()},
        )
        conn.commit()


def db_get_tasks(user_id: str):
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT id,task,done FROM tasks WHERE user_id=:uid ORDER BY created_at DESC"),
            {"uid": user_id},
        ).fetchall()


def db_complete_task(user_id: str, task_name: str) -> None:
    task_lower = task_name.lower().strip()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, task FROM tasks WHERE user_id=:uid AND done=0"),
            {"uid": user_id},
        ).fetchall()
        exact = [r for r in rows if r[1].lower().strip() == task_lower]
        if exact:
            conn.execute(text("UPDATE tasks SET done=1 WHERE id=:id"), {"id": exact[0][0]})
            conn.commit()
            return
        partial = [r for r in rows if task_lower in r[1].lower()]
        if len(partial) == 1:
            conn.execute(text("UPDATE tasks SET done=1 WHERE id=:id"), {"id": partial[0][0]})
            conn.commit()


def db_complete_task_by_id(user_id: str, task_id: str) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE tasks SET done=1 WHERE user_id=:uid AND id=:id"),
            {"uid": user_id, "id": task_id},
        )
        conn.commit()


def db_delete_task(user_id: str, task_name: str) -> bool:
    task_lower = task_name.lower().strip()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, task FROM tasks WHERE user_id=:uid AND done=0"),
            {"uid": user_id},
        ).fetchall()
        exact = [r for r in rows if r[1].lower().strip() == task_lower]
        target = exact[0][0] if exact else None
        if not target:
            partial = [r for r in rows if task_lower in r[1].lower()]
            if len(partial) == 1:
                target = partial[0][0]
        if target:
            conn.execute(text("DELETE FROM tasks WHERE id=:id"), {"id": target})
            conn.commit()
            return True
    return False


def db_add_note(user_id: str, title: str, content: str) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO notes (id,user_id,title,content,created_at) VALUES (:id,:uid,:title,:content,:ts)"),
            {"id": str(uuid.uuid4()), "uid": user_id, "title": title, "content": content, "ts": datetime.now().isoformat()},
        )
        conn.commit()


def db_get_notes(user_id: str):
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT title,content FROM notes WHERE user_id=:uid ORDER BY created_at DESC"),
            {"uid": user_id},
        ).fetchall()
