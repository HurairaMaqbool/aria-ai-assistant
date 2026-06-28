<div align="center">

<img src="https://img.shields.io/badge/version-4.0-blueviolet?style=for-the-badge" alt="Version"/>

# ✦ Aria AI Pro

### Bilingual AI Personal Assistant — Powered by LangGraph & Groq

*Math · Web Search · Tasks · Notes · Document Q&A · Persistent Memory*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Framework-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Ultra_Fast_LLM-F55036?style=flat-square)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-43_passed-22c55e?style=flat-square)](tests/)

<br/>

[📧 Email](mailto:hurairac37@gmail.com) &nbsp;·&nbsp; [💼 Fiverr](https://www.fiverr.com/huraira_maqbool) &nbsp;·&nbsp; [🔗 LinkedIn](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)

</div>

---

## 🌟 Overview

**Aria AI Pro** is a production-grade, bilingual AI personal assistant built on a **LangGraph multi-agent architecture** with Groq's ultra-fast LLM inference. It handles natural language in both **English and Urdu**, maintains persistent memory across sessions, and ships with a full toolkit — web search, math, tasks, notes, and document Q&A — all inside a clean Streamlit UI.

> ⚙️ **Everything is configurable from one file:** `settings.toml` — models, prompts, UI text, limits, and more. No need to touch source code.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🧠 **Persistent Memory** | ChromaDB vector store on disk — Aria remembers across sessions |
| 💬 **Chat History** | SQLite-backed messages, fully restored on page refresh |
| 🌍 **Bilingual** | Responds naturally in English or Urdu |
| ⚡ **Ultra-Fast Inference** | Groq API — Llama 3.3 70B, Llama 3.1 8B, Gemma 2 9B |
| 🌐 **Live Web Search** | DuckDuckGo search with multi-region support — no extra API key |
| 🧮 **Math Solver** | Safe AST-based calculator for arithmetic and expressions |
| ✅ **Task Manager** | Add, complete, and delete tasks via chat or sidebar |
| 📝 **Notes** | Save and retrieve notes through natural conversation |
| 📎 **Document Q&A** | Upload PDF / DOCX / TXT and query with RAG search |
| 🛡️ **Security Layer** | Input sanitization, HTML bleaching, rate limiting, jailbreak blocking |

---

## 🏗️ Architecture

```
User Input (Streamlit UI)
        │
        ▼
┌───────────────────────────────────┐
│         LangGraph Agent           │
│   LLM (Groq) ⇄ ToolNode (tools)  │
└───────────────────────────────────┘
          │
   ┌──────┼──────────┬───────────────┐
   ▼      ▼          ▼               ▼
SQLite  ChromaDB  DuckDuckGo      Safe Math
(chats, (memory +  (web search)   (AST eval)
 tasks,  RAG docs)
 notes)
```

The agent is a **ReAct loop** — it reasons, picks a tool, gets a result, and synthesizes a final response. All state (chat, tasks, notes, memory) is persisted across restarts.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit |
| **Agent Framework** | LangGraph + LangChain |
| **LLM Provider** | Groq (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `gemma2-9b-it`) |
| **Memory & RAG** | ChromaDB `PersistentClient` |
| **Database** | SQLite (`aria_pro.db`) |
| **Web Search** | DuckDuckGo Search API |
| **Security** | `bleach`, rate limiting, blocked-phrase filter |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/HurairaMaqbool/aria-ai-assistant.git
cd aria-ai-assistant
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 3. Add Your Groq API Key

**Option A — `.env` file (recommended for local dev):**

```bash
cp .env.example .env
# Open .env and set:
# GROQ_API_KEY=your_key_here
```

**Option B — Streamlit secrets (for Streamlit Cloud):**

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_groq_api_key_here"
```

> 🔑 Get a free key at [console.groq.com](https://console.groq.com)

### 4. (Optional) Pre-download Embedding Model

```bash
python download_model.py
```

### 5. Run the App

```bash
streamlit run app.py

# Or with the project launcher:
venv\Scripts\python run.py    # Windows
.\run.bat                      # Windows shortcut
```

---

## ⚙️ Configuration — `settings.toml`

Almost everything is configurable from a single file at the project root: **`settings.toml`**. Edit it and restart — no code changes needed.

| Section | What You Can Change |
|---------|---------------------|
| `[app]` | App name, version, page title, icon |
| `[llm]` | Default model, temperature, retries, model list |
| `[limits]` | Upload size, input length, rate limits, search result counts |
| `[memory]` | Document chunk size and overlap for RAG |
| `[search]` | Web search backends, regions, timeout |
| `[weather]` | Pakistan cities list, API timeout |
| `[security]` | Blocked jailbreak phrases |
| `[paths]` | Database filename, ChromaDB folder |
| `[ui]` | Welcome text, chat placeholder, starter buttons, chips |
| `[prompts]` | System prompt, few-shots, synthesis rules |
| `[messages]` | Error messages (API key missing, rate limit, etc.) |

### Examples

**Change the default LLM:**
```toml
[llm]
default_model = "llama-3.1-8b-instant"
temperature = 0.2
```

**Change the welcome message:**
```toml
[ui]
welcome_title = "Hello — I'm Aria"
chat_placeholder = "Type your message…"
```

**Customize AI behavior:**
```toml
[prompts]
system = """
You are Aria, a professional AI assistant. Always respond concisely.
"""
```

### Files Kept Separate (by design)

| File | Purpose |
|------|---------|
| `.env` | `GROQ_API_KEY` — never put secrets in `settings.toml` |
| `.streamlit/config.toml` | UI theme colors |
| `aria/ui/styles.css` | Advanced CSS styling |

---

## 📁 Project Structure

```
aria-ai-assistant/
├── app.py                   # Streamlit entry point
├── run.py                   # App launcher script
├── settings.toml            # ✅ Master config — edit here
├── aria/
│   ├── agent.py             # LangGraph ReAct agent
│   ├── config.py            # Settings loader & constants
│   ├── db.py                # SQLite persistence (chats, tasks, notes)
│   ├── memory.py            # ChromaDB memory + RAG ingestion
│   ├── security.py          # Sanitization & rate limiting
│   ├── tools.py             # All agent tools
│   ├── llm_health.py        # Groq API health check
│   ├── session.py           # Persistent session via URL param
│   └── ui/                  # Streamlit UI components & CSS
├── tests/                   # pytest test suite (43 tests)
├── .github/workflows/ci.yml # CI pipeline
├── download_model.py        # Pre-download ChromaDB embeddings
├── verify_project.py        # Project integrity check
├── requirements.txt
├── .env.example
├── aria_pro.db              # Created at runtime
├── chroma_data/             # Created at runtime
└── README.md
```

---

## 🧪 Testing

```bash
pytest tests/ -v            # Run full test suite
python verify_project.py    # Project integrity check
```

43 tests cover: settings load, tool execution, memory search, security filters, and DB persistence.

---

## 💬 Example Interactions

```
User:  "What's 234 * 56?"
Aria:  "Result: 13104"

User:  "Add task: submit assignment by Friday"
Aria:  "✅ Task added: 'submit assignment by Friday'"

User:  "Search for latest AI research"
Aria:  [web_search] Returns summarized live results

User:  "Search my document for revenue summary"
Aria:  [search_my_documents] Returns top matching chunks from uploaded file

User:  "مجھے کل کا موسم بتاؤ"
Aria:  [Responds in Urdu with weather info]
```

---

## 🗺️ Roadmap

- [ ] Voice input / output support
- [ ] Multi-user session isolation
- [ ] WhatsApp / Telegram integration
- [ ] Agentic email drafting tool
- [ ] Plugin system for custom tools

---

## 🤝 Built By

**Huraira Maqbool** — AI Engineer specializing in agentic systems, RAG pipelines & multi-agent architectures.

[![Email](https://img.shields.io/badge/Email-hurairac37@gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:hurairac37@gmail.com)
[![Fiverr](https://img.shields.io/badge/Fiverr-huraira__maqbool-1DBF73?style=flat-square&logo=fiverr&logoColor=white)](https://www.fiverr.com/huraira_maqbool)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-huraira--maqbool-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)
[![GitHub](https://img.shields.io/badge/GitHub-HurairaMaqbool-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/HurairaMaqbool)

---

<div align="center">

⭐ **If this project helped you, please star the repo — it means a lot!**

</div>
