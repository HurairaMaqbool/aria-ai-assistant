import os
import re
import tempfile
import uuid
from datetime import datetime

import chromadb
import docx
import pypdf
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

from aria.config import CHROMA_PATH, MAX_UPLOAD_BYTES

os.makedirs(CHROMA_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
ef = embedding_functions.DefaultEmbeddingFunction()
user_collections: dict = {}
rag_collections: dict = {}


def get_collection(user_id: str):
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
    key = f"memory_{safe_id}"
    if key not in user_collections:
        user_collections[key] = chroma_client.get_or_create_collection(key, embedding_function=ef)
    return user_collections[key]


def save_memory(user_id: str, role: str, content: str) -> None:
    get_collection(user_id).add(
        documents=[f"{role}: {content}"],
        ids=[str(uuid.uuid4())],
        metadatas=[{"role": role, "user_id": user_id, "timestamp": datetime.now().isoformat()}],
    )


def get_memory(user_id: str, query: str, n: int = 4) -> str:
    try:
        col = get_collection(user_id)
        count = col.count()
        if count == 0:
            return ""
        results = col.query(query_texts=[query], n_results=min(n, count))
        return "\n".join(results["documents"][0]) if results["documents"][0] else ""
    except Exception:
        return ""


def clear_memory(user_id: str) -> None:
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
    key = f"memory_{safe_id}"
    try:
        chroma_client.delete_collection(key)
    except Exception:
        pass
    user_collections.pop(key, None)


def get_rag_collection(user_id: str):
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
    key = f"rag_{safe_id}"
    if key not in rag_collections:
        rag_collections[key] = chroma_client.get_or_create_collection(key, embedding_function=ef)
    return rag_collections[key]


def extract_text(filepath: str, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        reader = pypdf.PdfReader(filepath)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    if ext == "docx":
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    if ext == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def remove_rag_document(user_id: str, filename: str) -> None:
    collection = get_rag_collection(user_id)
    try:
        existing = collection.get(where={"source": filename})
        if existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass


def build_rag(user_id: str, text: str, filename: str) -> int:
    remove_rag_document(user_id, filename)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    if not chunks:
        return 0
    collection = get_rag_collection(user_id)
    ids = [f"{filename}_{uuid.uuid4()}" for _ in range(len(chunks))]
    metadatas = [{"source": filename} for _ in range(len(chunks))]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


_GENERIC_DOC = re.compile(
    r"(?i)what(?:'s| is)\s+in|summarize|summarise|summary|content of|tell me about (?:the |my )?(?:file|document|upload)"
)


def search_docs(user_id: str, query: str, k: int = 5) -> str:
    collection = get_rag_collection(user_id)
    try:
        count = collection.count()
        if count == 0:
            return "No documents uploaded yet."
        n_results = min(k, count)
        search_query = query
        if _GENERIC_DOC.search(query):
            n_results = min(max(k, 8), count)
            search_query = "main content summary key topics sections information"
        results = collection.query(query_texts=[search_query], n_results=n_results)
        if not results["documents"][0]:
            return "Nothing found in documents."
        formatted = []
        seen = set()
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            if doc in seen:
                continue
            seen.add(doc)
            src = meta.get("source", "doc")
            formatted.append(f"[{src}]: {doc}")
        header = "UPLOADED DOCUMENT EXCERPTS:\n"
        return header + "\n\n".join(formatted)
    except Exception as exc:
        return f"Error searching documents: {exc}"


def get_uploaded_doc_names(user_id: str) -> list[str]:
    try:
        collection = get_rag_collection(user_id)
        if collection.count() == 0:
            return []
        data = collection.get()
        sources = {
            meta.get("source")
            for meta in (data.get("metadatas") or [])
            if meta and meta.get("source")
        }
        return sorted(sources)
    except Exception:
        return []


def process_uploaded_file(user_id: str, file) -> tuple[bool, str, int]:
    if file.size > MAX_UPLOAD_BYTES:
        return False, f"❌ {file.name} exceeds 10 MB limit.", 0
    suffix = "." + file.name.rsplit(".", 1)[-1].lower()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        text_extracted = extract_text(tmp_path, file.name)
        if not text_extracted.strip():
            return False, f"❌ Could not extract text from {file.name}", 0
        chunks = build_rag(user_id, text_extracted, file.name)
        return True, f"✅ {file.name} processed! ({chunks} chunks)", chunks
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
