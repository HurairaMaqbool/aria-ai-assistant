import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("ARIA_DATA_DIR", str(ROOT_DIR)))
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
CHROMA_PATH = str(DATA_DIR / "chroma_data")
DB_PATH = str(DATA_DIR / "aria_pro.db")
ALLOWED_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]
GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"
LLM_MAX_RETRIES = 3
LLM_RETRY_DELAY_SEC = 1.5
SESSION_PARAM = "uid"


def get_groq_api_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    try:
        import streamlit as st

        return st.secrets.get("GROQ_API_KEY", "").strip()
    except Exception:
        return ""


def normalize_model(model_name: str | None) -> str:
    if model_name in ALLOWED_MODELS:
        return model_name
    return ALLOWED_MODELS[0]


GROQ_API_KEY = get_groq_api_key()
