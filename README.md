<div align="center">

# 🤖 Aria — Bilingual AI Personal Assistant

**A production-grade AI agent built with LangGraph, Groq & ChromaDB**  
Supports Urdu & English with persistent memory, web search, math, tasks, notes, and document Q&A.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Framework-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Ultra_Fast_LLM-F55036?style=flat-square)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[📧 Contact](mailto:hurairac37@gmail.com) · [💼 Hire Me](https://fiverr.com/huraira_maqbool)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Persistent Memory** | ChromaDB vector store on disk (`chroma_data/`) |
| 💬 **Chat History** | SQLite-backed messages restored on refresh |
| 🌍 **Bilingual** | Responds in English or Urdu |
| ⚡ **Ultra-Fast** | Groq inference (Llama 3.3 / Llama 3.1 / Gemma 2) |
| 🌐 **Live Web Search** | DuckDuckGo search, no extra API key |
| 🧮 **Math Solver** | Safe AST-based calculator |
| ✅ **Task Manager** | Add, complete, delete tasks via chat or sidebar |
| 📝 **Notes** | Save and list notes through conversation |
| 📎 **Document Q&A** | Upload PDF/DOCX/TXT for RAG search |

---

## 🏗️ Architecture

```
User Input (Streamlit UI)
        │
        ▼
┌───────────────────────────────┐
│      LangGraph Agent          │
│  LLM (Groq) ⇄ ToolNode        │
└───────────────────────────────┘
        │
   ┌────┴────┬──────────┬────────────┐
   ▼         ▼          ▼            ▼
 SQLite   ChromaDB   DuckDuckGo   Safe Math
 (chats,   (memory +              (AST eval)
  tasks,    RAG docs)
  notes)
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Agent:** LangGraph + LangChain tools
- **LLM:** Groq (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `gemma2-9b-it`)
- **Memory & RAG:** ChromaDB (`PersistentClient`)
- **Database:** SQLite (`aria_pro.db`)
- **Security:** Input sanitization, bleach HTML output, rate limiting

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/HurairaMaqbool/aria-ai-assistant.git
cd aria-ai-assistant
```

### 2. Create a virtual environment (recommended on Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install dependencies (if not using venv)

```bash
pip install -r requirements.txt
```

Optional — pre-download the ChromaDB embedding model:

```bash
python download_model.py
```

### 4. Add your Groq API key

**Option A — `.env` file (recommended for local dev):**

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=...
```

**Option B — Streamlit secrets (for Streamlit Cloud):**

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_groq_api_key_here"
```

> 🔑 Get a free key: [console.groq.com](https://console.groq.com)

### 5. Run the app

```bash
streamlit run app.py
```

Or with the project venv:

```bash
venv\Scripts\python run.py
```

---

## 📁 Project Structure

```
aria-ai-assistant/
├── app.py                  # Streamlit entry point
├── run.py                  # App launcher
├── aria/                   # Core package
│   ├── agent.py            # LangGraph agent
│   ├── config.py           # Settings & API key
│   ├── db.py               # SQLite persistence
│   ├── memory.py           # ChromaDB memory + RAG
│   ├── security.py         # Sanitization & rate limits
│   ├── tools.py            # Agent tools
│   ├── llm_health.py       # Groq API health check
│   ├── session.py          # Persistent session via URL
│   └── ui/                 # Streamlit UI
├── tests/                  # pytest suite
├── .github/workflows/ci.yml
├── download_model.py
├── verify_project.py
├── requirements.txt
├── .env.example
├── aria_pro.db             # Created at runtime
├── chroma_data/            # Created at runtime
├── LICENSE
└── README.md
```

---

## 🧪 Testing

```bash
pytest tests/ -v
python verify_project.py
```

---

## 💬 Example Interactions

```
User:  "What's 234 * 56?"
Aria:  [calculator] "Result: 13104"

User:  "Add task: submit assignment by Friday"
Aria:  "✅ Task added: 'submit assignment by Friday'"

User:  "Search my document for revenue summary"
Aria:  [search_my_documents] Returns relevant chunks from uploaded files
```

---

## 🤝 Connect

Built by **Huraira Maqbool** — AI Engineer  
📧 [hurairac37@gmail.com](mailto:hurairac37@gmail.com) · 💼 [Fiverr](https://www.fiverr.com/huraira_maqbool) · 🔗 [LinkedIn](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)
