<div align="center">

# 🤖 Aria — Bilingual AI Personal Assistant

**A production-grade AI agent built with LangGraph, Groq & ChromaDB**  
Supports Urdu & English with persistent memory, web search, math, and task management.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Framework-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Ultra_Fast_LLM-F55036?style=flat-square)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[🚀 Live Demo](https://your-demo-link.streamlit.app) · [📧 Contact](mailto:hurairac37@gmail.com) · [💼 Hire Me](https://fiverr.com/huraira_maqbool)

</div>

---

## ✨ What Makes Aria Different

| Feature | Description |
|---------|-------------|
| 🧠 **Persistent Memory** | Remembers past conversations using ChromaDB vector store |
| 🌍 **Bilingual** | Auto-detects Urdu & English — responds in the same language |
| ⚡ **Ultra-Fast** | Groq inference (Llama 3.3 / Mixtral / Gemma) — sub-second responses |
| 🌐 **Live Web Search** | Real-time DuckDuckGo search, no API key required |
| 🧮 **Math Solver** | Evaluates any arithmetic expression via chat |
| ✅ **Task Manager** | Add, complete, and delete tasks through natural conversation |

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────┐
│           LangGraph Agent               │
│                                         │
│   ┌──────────┐    ┌──────────────────┐  │
│   │  Router  │───▶│  Tool Selector   │  │
│   └──────────┘    └──────────────────┘  │
│                          │               │
│          ┌───────────────┼──────────────┐│
│          ▼               ▼              ▼│
│   [Web Search]    [Calculator]    [Tasks]│
└─────────────────────────────────────────┘
         │
         ▼
   ChromaDB Memory  ←─── Store context
         │
         ▼
   Groq LLM Response
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Agent Framework:** LangGraph
- **LLM Provider:** Groq (Llama 3.3 70B, Mixtral 8x7B, Gemma)
- **Memory:** ChromaDB (vector store)
- **Embeddings:** LangChain + HuggingFace
- **Tools:** DuckDuckGo Search, Python eval (math), custom task manager
- **Language:** Python 3.10+

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/HurairaMaqbool/aria-ai-assistant.git
cd aria-ai-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key
```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_groq_api_key_here"
```

> 🔑 **Get a FREE Groq API key:** [console.groq.com](https://console.groq.com) → Sign up → API Keys → Create

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
aria-ai-assistant/
├── app.py                  # Main Streamlit app
├── untitled30.py           # LangGraph agent logic
├── aria_pro.db             # ChromaDB persistent memory
├── requirements.txt        # Dependencies
└── .gitignore
```

---

## 💬 Example Interactions

```
User:  "What's the weather in Karachi today?"
Aria:  [searches web] "Karachi is currently 33°C with clear skies..."

User:  "میرا نام کیا ہے؟"  (What is my name?)
Aria:  [queries memory] "آپ کا نام ہے..."  (Responds in Urdu)

User:  "Add task: submit assignment by Friday"
Aria:  "✅ Task added: submit assignment by Friday"
```

---

## 🤝 Connect

Built by **Huraira Maqbool** — AI Engineer  
📧 [hurairac37@gmail.com](mailto:hurairac37@gmail.com) · 💼 [Fiverr](https://www.fiverr.com/huraira_maqbool) · 🔗 [LinkedIn](https://www.linkedin.com/in/huraira-maqbool-b696a5277/)
