import html
from datetime import datetime
from pathlib import Path

import streamlit as st

from aria.agent import run_agent
from aria.config import ALLOWED_MODELS, GROQ_API_KEY, normalize_model
from aria.db import (
    db_clear_chats,
    db_complete_task_by_id,
    db_ensure_user,
    db_get_notes,
    db_get_tasks,
    db_load_chats,
)
from aria.llm_health import cached_groq_status
from aria.memory import clear_memory, get_collection, get_uploaded_doc_names, process_uploaded_file
from aria.security import render_assistant_content, render_user_content
from aria.session import get_or_create_user_id

MODEL_LABELS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B — Best quality",
    "llama-3.1-8b-instant": "Llama 3.1 8B — Fastest",
    "gemma2-9b-it": "Gemma 2 9B — Balanced",
}

STARTER_PROMPTS = [
    ("Math", "What is 234 * 56?", "starter_1"),
    ("Web Search", "Search: latest AI news", "starter_2"),
    ("Add Task", "Add task: Study LangGraph", "starter_3"),
    ("Save Note", "Save note: Project Ideas: Build a custom UI", "starter_4"),
]


def _sidebar_section(title: str) -> None:
    st.markdown(
        f'<div class="sidebar-section"><span class="section-dot"></span>{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )

STYLES = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")


CHAT_INPUT_FIX = """
<style id="aria-chat-input-fix">
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    caret-color: #38bdf8 !important;
}
[data-testid="stChatInput"] > div {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
}
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"] {
    background-color: #070b14 !important;
}
</style>
"""


def inject_styles() -> None:
    st.markdown(f"<style>{STYLES}</style>", unsafe_allow_html=True)


def inject_chat_input_fix() -> None:
    """Inject after chat input so it overrides Streamlit defaults."""
    st.markdown(CHAT_INPUT_FIX, unsafe_allow_html=True)


def _connection_pill(ok: bool, message: str) -> str:
    if not GROQ_API_KEY:
        return (
            '<div class="status-pill status-pill-offline">'
            '<span class="pill-dot pill-dot-red"></span>API key not configured</div>'
        )
    if ok:
        return (
            f'<div class="status-pill status-pill-online">'
            f'<span class="pill-dot pill-dot-green"></span>{html.escape(message)}</div>'
        )
    return (
        f'<div class="status-pill status-pill-warn">'
        f'<span class="pill-dot pill-dot-amber"></span>{html.escape(message)}</div>'
    )


def render_sidebar(user_id: str) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="aria-logo">A</div>
                <div class="brand-text">
                    <span class="brand-name">Aria Pro</span>
                    <span class="brand-tagline">AI Personal Assistant</span>
                </div>
                <span class="version-badge">v4.0</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-card">
                <div class="sidebar-card-title">Your Session</div>
                <div class="session-id">{html.escape(user_id)}</div>
                <div class="session-hint">Bookmark this page — your chats, tasks &amp; docs stay linked to this session.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-card-title">Model</div>', unsafe_allow_html=True)
        st.selectbox(
            "Model",
            options=ALLOWED_MODELS,
            format_func=lambda m: MODEL_LABELS.get(m, m),
            index=0,
            key="selected_model_name",
            label_visibility="collapsed",
        )
        if GROQ_API_KEY:
            ok, msg = cached_groq_status(GROQ_API_KEY)
            st.markdown(_connection_pill(ok, msg), unsafe_allow_html=True)
        else:
            st.markdown(_connection_pill(False, ""), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        mem_count = doc_count = task_count = 0
        try:
            mem_count = get_collection(user_id).count()
        except Exception:
            pass
        doc_count = len(st.session_state.get("docs_uploaded", []))
        task_count = len([t for t in db_get_tasks(user_id) if t[2] == 0])

        st.markdown(
            f"""
            <div class="sidebar-card">
                <div class="sidebar-card-title">Workspace</div>
                <div class="stat-grid">
                    <div class="stat-box"><div class="stat-value">{mem_count}</div><div class="stat-label">Memories</div></div>
                    <div class="stat-box"><div class="stat-value">{doc_count}</div><div class="stat-label">Documents</div></div>
                    <div class="stat-box"><div class="stat-value">{task_count}</div><div class="stat-label">Tasks</div></div>
                    <div class="stat-box"><div class="stat-value">{len(st.session_state.get("messages", []))}</div><div class="stat-label">Messages</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            db_clear_chats(user_id)
            clear_memory(user_id)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        _sidebar_section("Tasks")
        tasks = db_get_tasks(user_id)
        pending_tasks = [(r[0], r[1]) for r in tasks if r[2] == 0]
        if pending_tasks:
            for tid, task_text in pending_tasks:
                if st.checkbox(task_text, key=f"sb_task_{tid}"):
                    db_complete_task_by_id(user_id, tid)
                    st.rerun()
        else:
            st.caption("No pending tasks")

        completed = [(r[0], r[1]) for r in tasks if r[2] == 1]
        if completed:
            with st.expander(f"Completed ({len(completed)})"):
                for _, task_text in completed:
                    st.markdown(f"~~{html.escape(task_text)}~~")

        st.divider()
        _sidebar_section("Documents")
        uploaded = st.file_uploader(
            "Upload PDF, DOCX or TXT",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded:
            processed_any = False
            for file in uploaded:
                if file.name in st.session_state.docs_uploaded:
                    continue
                with st.spinner(f"Indexing {file.name}…"):
                    ok, message, _ = process_uploaded_file(user_id, file)
                if ok:
                    st.session_state.docs_uploaded.append(file.name)
                    processed_any = True
                else:
                    st.toast(message, icon="⚠️")
            if processed_any:
                st.toast("Document indexed successfully", icon="✅")
                st.rerun()

        if st.session_state.docs_uploaded:
            with st.expander(f"Uploaded ({len(st.session_state.docs_uploaded)})"):
                for doc in st.session_state.docs_uploaded:
                    st.markdown(
                        f'<div class="doc-chip"><span class="doc-chip-icon">📄</span>{html.escape(doc)}</div>',
                        unsafe_allow_html=True,
                    )

        st.divider()
        _sidebar_section("Notes")
        notes = db_get_notes(user_id)
        with st.expander(f"All notes ({len(notes)})"):
            if notes:
                for title, content in notes:
                    st.markdown(f"**{html.escape(title)}**")
                    st.caption(content[:200] + ("…" if len(content) > 200 else ""))
            else:
                st.caption("No notes yet")


def render_header(is_online: bool, message_count: int, model: str) -> None:
    status_class = "status-badge" if is_online else "status-badge status-badge-error"
    pulse = "status-pulse" if is_online else "status-pulse status-pulse-error"
    status_text = "Online" if is_online else "Offline"
    model_label = html.escape(MODEL_LABELS.get(model, model))

    st.markdown(
        f"""
        <div class="header-banner">
            <div class="header-main">
                <div class="header-title-section">
                    <h1><span>Aria AI Pro</span></h1>
                    <p class="header-subtitle">Math, web search, tasks, notes &amp; document Q&amp;A — powered by Groq.</p>
                </div>
                <div class="header-meta">
                    <div class="{status_class}">
                        <span class="{pulse}"></span>
                        <span class="status-text">{status_text}</span>
                    </div>
                    <div class="header-stats">
                        <span><strong>{message_count}</strong> messages</span>
                        <span class="header-stats-sep">·</span>
                        <span>{model_label}</span>
                    </div>
                </div>
            </div>
            <div class="chips-container">
                <span class="cap-chip">Calculator</span>
                <span class="cap-chip">Tasks &amp; Notes</span>
                <span class="cap-chip">Live Search</span>
                <span class="cap-chip">Document Q&amp;A</span>
                <span class="cap-chip">Urdu / English</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_messages() -> None:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        ts = msg.get("timestamp", "")
        ts_html = f'<div class="msg-meta">{html.escape(ts)}</div>' if ts else ""
        if msg["role"] == "user":
            body = render_user_content(msg["content"])
            st.markdown(
                f'<div class="msg-row user-row"><div class="msg-bubble user-bubble"><div class="msg-content">{body}</div>{ts_html}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            body = render_assistant_content(msg["content"])
            st.markdown(
                f'<div class="msg-row aria-row"><div class="aria-avatar">✦</div>'
                f'<div class="msg-bubble aria-bubble"><div class="aria-label">Aria</div>'
                f'<div class="msg-content">{body}</div>{ts_html}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def render_welcome() -> None:
    st.markdown(
        """
        <div class="welcome-hero">
            <div class="glowing-avatar">✦</div>
            <h2 class="welcome-title">Assalam o Alaikum — I'm Aria</h2>
            <p class="welcome-subtitle">Your professional AI workspace. Ask questions, upload documents, or use a quick action below.</p>
        </div>
        <div class="feature-row">
            <span class="feature-pill"><span class="feature-pill-dot"></span>Groq LLM</span>
            <span class="feature-pill"><span class="feature-pill-dot"></span>Memory</span>
            <span class="feature-pill"><span class="feature-pill-dot"></span>Document Q&amp;A</span>
            <span class="feature-pill"><span class="feature-pill-dot"></span>Bilingual</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="starter-grid">', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (title, prompt, key) in enumerate(STARTER_PROMPTS):
        with cols[i % 2]:
            if st.button(f"{title}\n{prompt[:40]}{'…' if len(prompt) > 40 else ''}", key=key, use_container_width=True):
                st.session_state.prompt_input = prompt
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_footer(model: str) -> None:
    st.markdown(
        f"""
        <div class="chat-footer">
            <div class="footer-inner">
                <span class="footer-pill footer-pill-accent">{html.escape(MODEL_LABELS.get(model, model))}</span>
                <span>Aria can make mistakes — verify important information</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_prompt_input(user_id: str) -> None:
    if not st.session_state.get("prompt_input"):
        return
    prompt = st.session_state.prompt_input
    st.session_state.prompt_input = None
    model = normalize_model(st.session_state.get("selected_model_name"))
    ts = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": ts})
    with st.spinner("Aria is thinking…"):
        response = run_agent(prompt, user_id, model)
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": datetime.now().strftime("%I:%M %p")})
    st.rerun()


def init_session_state(user_id: str) -> None:
    db_ensure_user(user_id)
    if "messages_loaded" not in st.session_state:
        st.session_state.messages = db_load_chats(user_id)
        st.session_state.messages_loaded = True
    if "docs_uploaded" not in st.session_state:
        st.session_state.docs_uploaded = get_uploaded_doc_names(user_id)


def render_app() -> None:
    inject_styles()
    user_id = get_or_create_user_id()
    init_session_state(user_id)
    handle_prompt_input(user_id)
    render_sidebar(user_id)

    model = normalize_model(st.session_state.get("selected_model_name"))
    groq_ok = bool(GROQ_API_KEY)
    if GROQ_API_KEY:
        groq_ok, _ = cached_groq_status(GROQ_API_KEY)

    render_header(groq_ok, len(st.session_state.messages), model)
    render_messages()
    if not st.session_state.messages:
        render_welcome()

    if prompt := st.chat_input("Ask Aria anything…"):
        ts = datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": ts})
        with st.spinner("Aria is thinking…"):
            response = run_agent(prompt, user_id, model)
        st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": datetime.now().strftime("%I:%M %p")})
        st.rerun()

    inject_chat_input_fix()
    render_footer(model)
