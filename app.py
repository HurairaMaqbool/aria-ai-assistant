import streamlit as st
import markdown
import os
import re
import uuid
import time
import ast
import operator as op
import chromadb
import pypdf
import docx
from chromadb.utils import embedding_functions
from datetime import datetime
from sqlalchemy import create_engine, text
from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from typing import TypedDict, Annotated, Sequence
from duckduckgo_search import DDGS
import operator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# ---- Config ----
st.set_page_config(
    page_title="Aria AI Pro",
    page_icon="🤖",
    layout="wide"
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ---- CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #07060f !important;
        background-image: radial-gradient(circle at 50% 15%, #19143c 0%, #07060f 70%) !important;
        color: #e2e8f0 !important;
    }
    
    .main {
        background: transparent !important;
    }
    
    /* Hide Streamlit default components */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stFooter"] { display: none !important; }
    
    /* Remove padding from main area */
    .block-container {
        padding-top: 20px !important;
        padding-bottom: 80px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 950px !important;
        margin: 0 auto !important;
    }
    
    /* Styled scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #07060f;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.3);
        border-radius: 9999px;
        border: 2px solid #07060f;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.6);
    }
    
    /* Sidebar premium styles */
    [data-testid="stSidebar"] {
        background-color: rgba(7, 6, 15, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding: 20px 15px !important;
    }
    
    /* Brand logo with version badge */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 24px;
        padding: 5px 0;
    }
    .brand-icon {
        font-size: 1.6rem;
        animation: rotate-gently 6s infinite linear;
    }
    @keyframes rotate-gently {
        0% { transform: rotate(0deg); }
        50% { transform: rotate(10deg); }
        100% { transform: rotate(0deg); }
    }
    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .version-badge {
        background: rgba(168, 85, 247, 0.15);
        border: 1px solid rgba(168, 85, 247, 0.3);
        color: #c084fc;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    /* Info chips in sidebar */
    .info-chips {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 16px;
    }
    .info-chip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
    }
    .info-chip-label {
        color: #94a3b8;
    }
    .info-chip-value {
        color: #c084fc;
        font-weight: 600;
    }
    
    /* Red-tinted clear conversation button */
    .clear-btn-container button {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #fca5a5 !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 15px !important;
    }
    .clear-btn-container button:hover {
        background: rgba(239, 68, 68, 0.2) !important;
        border-color: rgba(239, 68, 68, 0.6) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }
    
    /* Selectbox premium overrides */
    div[data-testid="stSelectbox"] [data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    div[data-testid="stSelectbox"] label {
        color: #94a3b8 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.9rem !important;
    }
    
    /* Checkbox list overrides */
    div[data-testid="stCheckbox"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(139, 92, 246, 0.1) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stCheckbox"]:hover {
        border-color: rgba(139, 92, 246, 0.4) !important;
        background-color: rgba(139, 92, 246, 0.05) !important;
        transform: translateX(2px) !important;
    }
    div[data-testid="stCheckbox"] label span {
        color: #e2e8f0 !important;
        font-size: 14px !important;
    }
    
    /* File uploader override */
    div[data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed rgba(139, 92, 246, 0.2) !important;
        border-radius: 12px !important;
        padding: 10px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(139, 92, 246, 0.5) !important;
        background-color: rgba(139, 92, 246, 0.03) !important;
    }
    div[data-testid="stFileUploader"] label {
        color: #94a3b8 !important;
        font-size: 13px !important;
    }
    
    /* Header Banner styling */
    .header-banner {
        background: rgba(15, 10, 30, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(139, 92, 246, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .header-main {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        flex-wrap: wrap;
        gap: 16px;
    }
    .header-title-section h1 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header-subtitle {
        margin: 6px 0 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }
    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.25);
        padding: 6px 12px;
        border-radius: 9999px;
    }
    .status-pulse {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 8px #22c55e;
        display: inline-block;
        animation: status-pulse-anim 2s infinite;
    }
    @keyframes status-pulse-anim {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.5; }
        100% { transform: scale(1); opacity: 1; }
    }
    .status-text {
        color: #4ade80;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .chips-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .cap-chip {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #cbd5e1;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        transition: all 0.2s ease;
    }
    .cap-chip:hover {
        background: rgba(139, 92, 246, 0.15);
        border-color: rgba(139, 92, 246, 0.35);
        color: #ffffff;
        transform: translateY(-1px);
    }
    
    /* Welcome screen empty state */
    .welcome-hero {
        text-align: center;
        margin-top: 40px;
        margin-bottom: 40px;
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .glowing-avatar {
        font-size: 3.5rem;
        width: 80px;
        height: 80px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.2) 0%, rgba(99, 102, 241, 0.05) 70%);
        border: 2px solid rgba(168, 85, 247, 0.4);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.3);
        animation: pulse-glow 3s infinite;
    }
    @keyframes pulse-glow {
        0% { transform: scale(1); box-shadow: 0 0 25px rgba(168, 85, 247, 0.3); }
        50% { transform: scale(1.04); box-shadow: 0 0 35px rgba(168, 85, 247, 0.5); }
        100% { transform: scale(1); box-shadow: 0 0 25px rgba(168, 85, 247, 0.3); }
    }
    .welcome-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .welcome-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* 2x2 grid starter cards targeting Streamlit buttons */
    .starter-grid {
        margin-bottom: 40px;
    }
    .starter-grid div[data-testid="stButton"] button {
        background: rgba(15, 10, 30, 0.45) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 14px !important;
        color: #cbd5e1 !important;
        padding: 18px !important;
        height: auto !important;
        text-align: left !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 6px !important;
        min-height: 100px !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    .starter-grid div[data-testid="stButton"] button:hover {
        border-color: rgba(168, 85, 247, 0.5) !important;
        background: rgba(25, 15, 45, 0.55) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.15) !important;
        color: #ffffff !important;
    }
    .starter-grid div[data-testid="stButton"] button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Chat messages wrapper */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 40px;
    }
    
    /* Chat bubbles styling */
    .msg-row {
        display: flex;
        width: 100%;
        margin-bottom: 18px;
        animation: slideUpFade 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-row {
        justify-content: flex-end;
    }
    .aria-row {
        justify-content: flex-start;
        gap: 12px;
    }
    .msg-bubble {
        max-width: 80%;
        padding: 14px 20px;
        border-radius: 18px;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .user-bubble {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: #ffffff;
        border-top-right-radius: 4px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
    }
    .aria-bubble {
        background: rgba(15, 10, 30, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        color: #f1f5f9;
        border: 1px solid rgba(139, 92, 246, 0.15);
        border-left: 4px solid #a855f7;
        border-top-left-radius: 4px;
    }
    .aria-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(168, 85, 247, 0.3);
        flex-shrink: 0;
    }
    .aria-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        color: #c084fc;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .msg-meta {
        font-size: 0.7rem;
        color: #64748b;
        margin-top: 6px;
        text-align: right;
    }
    .user-bubble .msg-meta {
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* Styling Markdown elements inside bot bubbles */
    .aria-bubble p {
        margin-bottom: 10px;
    }
    .aria-bubble p:last-child {
        margin-bottom: 0;
    }
    .aria-bubble strong {
        color: #d8b4fe !important;
        font-weight: 600;
    }
    .aria-bubble a {
        color: #a855f7 !important;
        text-decoration: underline;
    }
    .aria-bubble pre {
        background: #090712 !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        overflow-x: auto !important;
        margin: 10px 0 !important;
    }
    .aria-bubble code {
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.88em !important;
        background: #090712;
        padding: 2px 6px;
        border-radius: 4px;
        color: #f1f5f9 !important;
    }
    .aria-bubble pre code {
        padding: 0;
        background: transparent;
        font-size: 0.85em !important;
    }
    .aria-bubble ul, .aria-bubble ol {
        margin-left: 20px !important;
        margin-bottom: 10px !important;
    }
    .aria-bubble li {
        margin-bottom: 4px !important;
    }
    .aria-bubble table {
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
    }
    .aria-bubble th, .aria-bubble td {
        border: 1px solid rgba(139, 92, 246, 0.15);
        padding: 8px 12px;
        text-align: left;
    }
    .aria-bubble th {
        background: rgba(139, 92, 246, 0.1);
        color: #d8b4fe;
    }
    
    /* Expander styling updates */
    div[data-testid="stExpander"] {
        background: rgba(15, 10, 30, 0.35) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
    }
    div[data-testid="stExpander"] details summary {
        color: #cbd5e1 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 500 !important;
    }
    div[data-testid="stExpander"] details summary:hover {
        color: #c084fc !important;
    }
    
    /* Chat Input Overrides */
    div[data-testid="stChatInputContainer"] {
        background: rgba(7, 6, 15, 0.96) !important;
        backdrop-filter: blur(12px) !important;
        border-top: 1px solid rgba(139, 92, 246, 0.15) !important;
        padding-top: 16px !important;
        padding-bottom: 28px !important;
    }
    div[data-testid="stChatInput"] {
        max-width: 900px !important;
        margin: 0 auto !important;
        background: transparent !important;
    }
    div[data-testid="stChatInput"] > div {
        background: rgba(15, 10, 30, 0.6) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 14px !important;
        padding: 6px 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stChatInput"] > div:hover {
        border-color: rgba(168, 85, 247, 0.4) !important;
        box-shadow: 0 4px 25px rgba(139, 92, 246, 0.1) !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #a855f7 !important;
        background: rgba(15, 10, 30, 0.8) !important;
        box-shadow: 0 0 16px rgba(168, 85, 247, 0.3), 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        caret-color: #a855f7 !important;
    }
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2) !important;
    }
    div[data-testid="stChatInput"] button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 6px 18px rgba(168, 85, 247, 0.4) !important;
    }
    div[data-testid="stChatInput"] button:active {
        transform: translateY(0) scale(1) !important;
    }
    
    /* Fixed Floating Chat Footer */
    .chat-footer {
        position: fixed;
        bottom: 6px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 0.7rem;
        color: #475569;
        z-index: 999999;
        pointer-events: none;
        font-family: 'Inter', sans-serif;
    }
    
    /* Responsive stacking adjustments */
    @media (max-width: 768px) {
        .header-main {
            flex-direction: column;
            align-items: flex-start;
        }
        .header-title-section h1 {
            font-size: 1.8rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---- Database ----
engine = create_engine("sqlite:///aria_pro.db")

def init_db():
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

def db_save_chat(user_id, role, content):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO chats (id,user_id,role,content,timestamp) VALUES (:id,:user_id,:role,:content,:ts)"),
            {"id": str(uuid.uuid4()), "user_id": user_id, "role": role, "content": content, "ts": datetime.now().isoformat()})
        conn.commit()

def db_add_task(user_id, task):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO tasks (id,user_id,task,done,created_at) VALUES (:id,:uid,:task,0,:ts)"),
            {"id": str(uuid.uuid4()), "uid": user_id, "task": task, "ts": datetime.now().isoformat()})
        conn.commit()

def db_get_tasks(user_id):
    with engine.connect() as conn:
        return conn.execute(text("SELECT id,task,done FROM tasks WHERE user_id=:uid ORDER BY created_at DESC"),
            {"uid": user_id}).fetchall()

def db_complete_task(user_id, task_name):
    with engine.connect() as conn:
        conn.execute(text("UPDATE tasks SET done=1 WHERE user_id=:uid AND LOWER(task) LIKE :t"),
            {"uid": user_id, "t": f"%{task_name.lower()}%"})
        conn.commit()

def db_add_note(user_id, title, content):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO notes (id,user_id,title,content,created_at) VALUES (:id,:uid,:title,:content,:ts)"),
            {"id": str(uuid.uuid4()), "uid": user_id, "title": title, "content": content, "ts": datetime.now().isoformat()})
        conn.commit()

def db_get_notes(user_id):
    with engine.connect() as conn:
        return conn.execute(text("SELECT title,content FROM notes WHERE user_id=:uid ORDER BY created_at DESC"),
            {"uid": user_id}).fetchall()

# ---- Memory ----
chroma_client = chromadb.Client()
ef = embedding_functions.DefaultEmbeddingFunction()
user_collections = {}

def get_collection(user_id):
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', user_id)
    key = f"memory_{safe_id}"
    if key not in user_collections:
        user_collections[key] = chroma_client.get_or_create_collection(key, embedding_function=ef)
    return user_collections[key]

def save_memory(user_id, role, content):
    get_collection(user_id).add(
        documents=[f"{role}: {content}"],
        ids=[str(uuid.uuid4())],
        metadatas=[{"role": role, "user_id": user_id, "timestamp": datetime.now().isoformat()}]
    )

def get_memory(user_id, query, n=4):
    try:
        col = get_collection(user_id)
        count = col.count()
        if count == 0: return ""
        results = col.query(query_texts=[query], n_results=min(n, count))
        return "\n".join(results["documents"][0]) if results["documents"][0] else ""
    except:
        return ""

# ---- RAG ----
# We use ChromaDB which is already installed and doesn't require PyTorch or FAISS
rag_collections = {}

def get_rag_collection(user_id):
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', user_id)
    key = f"rag_{safe_id}"
    if key not in rag_collections:
        rag_collections[key] = chroma_client.get_or_create_collection(key, embedding_function=ef)
    return rag_collections[key]

def extract_text(filepath, filename):
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        reader = pypdf.PdfReader(filepath)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    elif ext == "docx":
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

def build_rag(user_id, text, filename):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    
    collection = get_rag_collection(user_id)
    ids = [f"{filename}_{uuid.uuid4()}" for _ in range(len(chunks))]
    metadatas = [{"source": filename} for _ in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    return len(chunks)

def search_docs(user_id, query, k=3):
    collection = get_rag_collection(user_id)
    try:
        count = collection.count()
        if count == 0:
            return "No documents uploaded yet."
        
        results = collection.query(
            query_texts=[query],
            n_results=min(k, count)
        )
        if not results["documents"][0]:
            return "Nothing found in documents."
            
        formatted = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            src = meta.get("source", "doc")
            formatted.append(f"[{src}]: {doc}")
            
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error searching documents: {e}"

# ---- Security ----
BLOCKED = ["ignore previous instructions","ignore all instructions","reveal system prompt",
           "forget everything","you are now","act as","jailbreak","dan mode"]

def sanitize(text):
    if not text or not text.strip(): return False, "Empty input."
    if len(text) > 2000: return False, "Too long (max 2000 chars)."
    text_lower = text.lower()
    for p in BLOCKED:
        if p in text_lower: return False, "⚠️ Suspicious input blocked."
    return True, re.sub(r'<[^>]+>', '', text).strip()

request_log = {}
def rate_limit(user_id, max_req=15, window=60):
    now = time.time()
    if user_id not in request_log: request_log[user_id] = []
    request_log[user_id] = [t for t in request_log[user_id] if now - t < window]
    if len(request_log[user_id]) >= max_req: return False
    request_log[user_id].append(now)
    return True

# ---- Tools ----
SAFE_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
            ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg}

def _safe_eval(node):
    if isinstance(node, ast.Num): return node.n
    elif isinstance(node, ast.BinOp): return SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp): return SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsafe")

current_uid = ["default"]

@tool
def calculator(expression: str) -> str:
    """Safe math calculator. Input: expression like '25*48'"""
    try:
        return f"Result: {_safe_eval(ast.parse(expression, mode='eval').body)}"
    except Exception as e:
        return f"Error: {e}"

@tool
def add_task(task: str) -> str:
    """Add a task to your list."""
    db_add_task(current_uid[0], task)
    return f"✅ Task added: '{task}'"

@tool
def list_tasks(dummy: str = "") -> str:
    """Show all your tasks."""
    rows = db_get_tasks(current_uid[0])
    if not rows: return "No tasks yet!"
    pending = [r[1] for r in rows if r[2] == 0]
    done = [r[1] for r in rows if r[2] == 1]
    out = ""
    if pending: out += "📋 Pending:\n" + "\n".join(f"  • {t}" for t in pending)
    if done: out += "\n✅ Done:\n" + "\n".join(f"  • {t}" for t in done)
    return out

@tool
def complete_task(task_name: str) -> str:
    """Mark task as done. Input: task name"""
    db_complete_task(current_uid[0], task_name)
    return f"✅ Done: '{task_name}'"

@tool
def save_note(note_input: str) -> str:
    """Save a note. Format: 'Title: Content'"""
    if ":" in note_input:
        title, content = note_input.split(":", 1)
    else:
        title, content = "Note", note_input
    db_add_note(current_uid[0], title.strip(), content.strip())
    return f"📝 Note saved: '{title.strip()}'"

@tool
def list_notes(dummy: str = "") -> str:
    """Show all your notes."""
    notes = db_get_notes(current_uid[0])
    if not notes: return "No notes yet."
    return "📝 Notes:\n" + "\n".join(f"• {n[0]}: {n[1][:80]}" for n in notes)

@tool
def web_search(query: str) -> str:
    """Search internet. Input: search query"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results: return "No results."
        return "\n\n".join(f"**{r['title']}**\n{r['body']}" for r in results)
    except Exception as e:
        return f"Search error: {e}"

@tool
def search_my_documents(query: str) -> str:
    """Search uploaded documents. Input: your question"""
    return search_docs(current_uid[0], query)

ALL_TOOLS = [calculator, add_task, list_tasks, complete_task,
             save_note, list_notes, web_search, search_my_documents]

# ---- LLM + Agent ----
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
llm_with_tools = llm.bind_tools(ALL_TOOLS)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: str

SYSTEM = """You are Aria — a smart AI Personal Assistant.

TOOLS: calculator, add_task, list_tasks, complete_task, save_note, list_notes, web_search, search_my_documents

RULES:
- Use calculator for ALL math
- Use task tools for tasks
- Use search_my_documents for uploaded doc questions
- Use web_search for current info
- ONE tool call at a time
- Be concise and helpful
- Respond in user's language (English/Urdu both ok)"""

def call_llm(state):
    messages = state["messages"]
    user_id = state.get("user_id", "default")
    last_msg = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
    memory = get_memory(user_id, last_msg)
    system = SYSTEM + (f"\n\nPast context:\n{memory}" if memory else "")
    
    # Load dynamically selected model
    model_name = st.session_state.get("selected_model_name", "llama-3.3-70b-versatile")
    dynamic_llm = ChatGroq(model=model_name, api_key=GROQ_API_KEY)
    dynamic_llm_with_tools = dynamic_llm.bind_tools(ALL_TOOLS)
    
    response = dynamic_llm_with_tools.invoke([SystemMessage(content=system)] + list(messages))
    return {"messages": [response], "user_id": user_id}

def should_continue(state):
    last = state["messages"][-1]
    return "tools" if (hasattr(last, "tool_calls") and last.tool_calls) else END

tool_node = ToolNode(ALL_TOOLS)
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tools", tool_node)
graph.set_entry_point("llm")
graph.add_conditional_edges("llm", should_continue)
graph.add_edge("tools", "llm")
agent = graph.compile()

def run_agent(user_input, user_id="default"):
    current_uid[0] = user_id
    ok, clean = sanitize(user_input)
    if not ok: return f"⚠️ {clean}"
    if not rate_limit(user_id): return "⚠️ Too many requests. Wait 1 minute."
    save_memory(user_id, "user", clean)
    db_save_chat(user_id, "user", clean)
    try:
        result = agent.invoke({"messages": [HumanMessage(content=clean)], "user_id": user_id})
        response = result["messages"][-1].content
    except Exception as e:
        response = f"Error: {e}"
    save_memory(user_id, "assistant", response)
    db_save_chat(user_id, "assistant", response)
    return response

# ---- Streamlit UI ----
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_uploaded" not in st.session_state:
    st.session_state.docs_uploaded = []

USER_ID = st.session_state.user_id

# Check if a prompt chip was clicked and needs execution
if "prompt_input" in st.session_state and st.session_state.prompt_input:
    prompt = st.session_state.prompt_input
    st.session_state.prompt_input = None # reset
    timestamp_user = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp_user})
    with st.spinner("Aria is thinking..."):
        response = run_agent(prompt, USER_ID)
    timestamp_assistant = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp_assistant})
    st.rerun()

# ---- Sidebar ----
with st.sidebar:
    # Branded Top with icon + name + version badge
    st.markdown("""
    <div class="sidebar-brand">
        <span class="brand-icon">🤖</span>
        <span class="brand-name">Aria Pro</span>
        <span class="version-badge">v2.0</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:11px; color:#64748b; margin-top: -15px; margin-bottom: 15px;'>Session: {USER_ID}</div>", unsafe_allow_html=True)
    
    # Model selector
    st.selectbox(
        "🤖 Select Model",
        options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0,
        key="selected_model_name"
    )
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    # Info chips for memory count and search engine
    mem_count = 0
    try:
        mem_count = get_collection(USER_ID).count()
    except Exception:
        pass
        
    st.markdown(f"""
    <div class="info-chips">
        <div class="info-chip">
            <span class="info-chip-label">🧠 Memory Count</span>
            <span class="info-chip-value">{mem_count} items</span>
        </div>
        <div class="info-chip">
            <span class="info-chip-label">🔍 Search Engine</span>
            <span class="info-chip-value">DuckDuckGo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Red-tinted "Clear conversation" button
    st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.divider()

    # Task board with Pending / Completed sections
    st.markdown("### 📋 Task Board")
    tasks = db_get_tasks(USER_ID)
    pending_tasks = [(r[0], r[1]) for r in tasks if r[2] == 0]
    
    st.markdown("#### Pending Tasks")
    if pending_tasks:
        for tid, task_text in pending_tasks:
            # Checkbox to complete task directly in the sidebar
            if st.checkbox(task_text, key=f"sb_task_{tid}"):
                db_complete_task(USER_ID, task_text)
                st.sidebar.success(f"Completed: {task_text}")
                st.rerun()
    else:
        st.caption("No pending tasks. Tell Aria: 'add task: XYZ'")
        
    # Collapsible Completed Tasks
    completed_tasks = [(r[0], r[1]) for r in tasks if r[2] == 1]
    if completed_tasks:
        with st.expander("✅ Completed Tasks"):
            for _, task_text in completed_tasks:
                st.markdown(f"~~{task_text}~~")
                
    st.divider()

    # Styled Document upload section
    st.markdown("### 📎 Upload Document")
    uploaded = st.file_uploader(
        "Upload PDF/DOCX/TXT for RAG",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded:
        for file in uploaded:
            if file.name not in st.session_state.docs_uploaded:
                with st.spinner(f"Processing {file.name}..."):
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file.name.split(".")[-1]) as tmp:
                        tmp.write(file.read())
                        tmp_path = tmp.name
                    text_extracted = extract_text(tmp_path, file.name)
                    if text_extracted.strip():
                        chunks = build_rag(USER_ID, text_extracted, file.name)
                        st.session_state.docs_uploaded.append(file.name)
                        st.sidebar.success(f"✅ {file.name} processed! ({chunks} chunks)")
                        st.rerun()
                    else:
                        st.sidebar.error(f"❌ Could not extract text from {file.name}")
                        
    # Show uploaded files list
    if st.session_state.docs_uploaded:
        with st.expander("📚 Uploaded Files"):
            for doc in st.session_state.docs_uploaded:
                st.markdown(f"• 📄 {doc}")

    st.divider()

    # Notes count badge & expander
    notes = db_get_notes(USER_ID)
    notes_count = len(notes)
    with st.expander(f"📝 Saved Notes ({notes_count})"):
        if notes:
            for title, content in notes:
                st.markdown(f"**{title}**")
                st.caption(content)
                st.divider()
        else:
            st.caption("No notes saved yet. Tell Aria: 'save note: Title: Content'")

# ---- Main Content Area ----

# Header Banner
st.markdown(f"""
<div class="header-banner">
    <div class="header-main">
        <div class="header-title-section">
            <h1>Aria AI Pro</h1>
            <p class="header-subtitle">LangGraph + Groq-powered Assistant with Memory & Tools</p>
        </div>
        <div class="status-badge">
            <span class="status-pulse"></span>
            <span class="status-text">Online & Ready</span>
        </div>
    </div>
    <div class="chips-container">
        <span class="cap-chip">🔢 Math</span>
        <span class="cap-chip">📋 Tasks</span>
        <span class="cap-chip">🌐 Web Search</span>
        <span class="cap-chip">🧠 Memory</span>
        <span class="cap-chip">🗣️ Urdu/English</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Scrollable chat area wrapper
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Loop and render messages as custom styled HTML bubbles
for msg in st.session_state.messages:
    ts_val = msg.get("timestamp", "")
    ts_html = f'<div class="msg-meta">🕒 {ts_val}</div>' if ts_val else ''
    
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-row user-row">
            <div class="msg-bubble user-bubble">
                <div class="msg-content">{msg['content']}</div>
                {ts_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Convert markdown content to HTML
        msg_html = markdown.markdown(msg['content'], extensions=['fenced_code', 'tables'])
        st.markdown(f"""
        <div class="msg-row aria-row">
            <div class="aria-avatar">🤖</div>
            <div class="msg-bubble aria-bubble">
                <div class="aria-label">Aria</div>
                <div class="msg-content">{msg_html}</div>
                {ts_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Empty welcome state if no message exists
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-hero">
        <div class="glowing-avatar">🤖</div>
        <h2 class="welcome-title">Assalam o Alaikum! Main Aria hoon</h2>
        <p class="welcome-subtitle">A professional, production-grade assistant. Ask me anything or choose a starter card below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render 2x2 grid of starter cards
    st.markdown('<div class="starter-grid">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Solve Mathematics\n\nWhat is the value of 234 * 56?", key="starter_1", use_container_width=True):
            st.session_state.prompt_input = "What is 234 * 56?"
            st.rerun()
        if st.button("🌐 Search Web\n\nFind the latest artificial intelligence news", key="starter_2", use_container_width=True):
            st.session_state.prompt_input = "Search: latest AI news"
            st.rerun()
    with col2:
        if st.button("📋 Study LangGraph\n\nAdd task to study LangGraph tools and memory", key="starter_3", use_container_width=True):
            st.session_state.prompt_input = "Add task: Study LangGraph"
            st.rerun()
        if st.button("📝 Save Ideas\n\nSave note: Project Ideas: Build a custom Streamlit UI", key="starter_4", use_container_width=True):
            st.session_state.prompt_input = "Save note: Project Ideas: Build a custom Streamlit UI"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Fixed bottom chat input bar
if prompt := st.chat_input("Ask Aria anything..."):
    timestamp_user = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp_user})
    
    with st.spinner("Aria is thinking..."):
        response = run_agent(prompt, USER_ID)
        
    timestamp_assistant = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp_assistant})
    st.rerun()

# Floating Chat Footer (shows current model name and disclaimer)
selected_model = st.session_state.get("selected_model_name", "llama-3.3-70b-versatile")
st.markdown(f"""
<div class="chat-footer">
    Model: {selected_model} | Aria AI Pro can make mistakes. Verify important info.
</div>
""", unsafe_allow_html=True)
