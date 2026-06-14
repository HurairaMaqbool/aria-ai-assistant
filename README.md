# 🤖 Aria — AI Personal Assistant

A professional AI chatbot built with Streamlit, LangGraph & Groq.
Supports **Urdu and English** with memory, web search, math & task management.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🧮 Math | Solve any arithmetic expression |
| ✅ Tasks | Add, complete, delete tasks via chat |
| 🌐 Web Search | Real-time search using DuckDuckGo |
| 🧠 Memory | Remembers conversations with ChromaDB |
| 🌍 Bilingual | Urdu & English auto-detect |
| ⚡ Fast | Powered by Groq ultra-fast inference |

---

## 🚀 Live Demo

👉 [Click here to try Aria live!](https://share.streamlit.io)

---

## 🛠️ Tech Stack

- **Streamlit** — Frontend UI
- **Groq** — LLM (Llama 3.3, Mixtral, Gemma)
- **LangGraph** — AI Agent framework
- **LangChain** — Tool & memory integration
- **ChromaDB** — Vector memory store
- **DuckDuckGo** — Web search engine
- **Python 3.10+**

---

## ⚙️ Run Locally

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
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🔑 Get FREE Groq API Key

1. Go to 👉 [console.groq.com](https://console.groq.com)
2. Sign up free
3. API Keys → Create new key → Copy

---

## 📁 Project Structure
