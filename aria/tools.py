import ast
import operator as op

from langchain.tools import tool

from aria.context import get_active_user_id
from aria.db import (
    db_add_note,
    db_add_task,
    db_complete_task,
    db_delete_task,
    db_get_notes,
    db_get_tasks,
)
from aria.memory import search_docs

SAFE_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsafe")


@tool
def calculator(expression: str) -> str:
    """Safe math calculator. Input: expression like '25*48'"""
    try:
        return f"Result: {_safe_eval(ast.parse(expression, mode='eval').body)}"
    except Exception as exc:
        return f"Error: {exc}"


@tool
def add_task(task: str) -> str:
    """Add a task to your list."""
    db_add_task(get_active_user_id(), task)
    return f"✅ Task added: '{task}'"


@tool
def list_tasks(dummy: str = "") -> str:
    """Show all your tasks."""
    rows = db_get_tasks(get_active_user_id())
    if not rows:
        return "No tasks yet!"
    pending = [r[1] for r in rows if r[2] == 0]
    done = [r[1] for r in rows if r[2] == 1]
    out = ""
    if pending:
        out += "📋 Pending:\n" + "\n".join(f"  • {t}" for t in pending)
    if done:
        out += "\n✅ Done:\n" + "\n".join(f"  • {t}" for t in done)
    return out


@tool
def complete_task(task_name: str) -> str:
    """Mark task as done. Input: task name"""
    db_complete_task(get_active_user_id(), task_name)
    return f"✅ Done: '{task_name}'"


@tool
def delete_task(task_name: str) -> str:
    """Delete a pending task. Input: task name"""
    if db_delete_task(get_active_user_id(), task_name):
        return f"🗑️ Task deleted: '{task_name}'"
    return f"Could not find pending task: '{task_name}'"


@tool
def save_note(note_input: str) -> str:
    """Save a note. Format: 'Title: Content'"""
    if ":" in note_input:
        title, content = note_input.split(":", 1)
    else:
        title, content = "Note", note_input
    db_add_note(get_active_user_id(), title.strip(), content.strip())
    return f"📝 Note saved: '{title.strip()}'"


@tool
def list_notes(dummy: str = "") -> str:
    """Show all your notes."""
    notes = db_get_notes(get_active_user_id())
    if not notes:
        return "No notes yet."
    return "📝 Notes:\n" + "\n".join(f"• {n[0]}: {n[1][:80]}" for n in notes)


from aria.search import run_web_search


@tool
def web_search(query: str) -> str:
    """Search internet. Input: search query"""
    return run_web_search(query)


@tool
def search_my_documents(query: str) -> str:
    """Search uploaded documents. Input: your question"""
    return search_docs(get_active_user_id(), query)


ALL_TOOLS = [
    calculator,
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    save_note,
    list_notes,
    web_search,
    search_my_documents,
]
