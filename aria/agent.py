import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from aria.config import GROQ_API_KEY, LLM_MAX_RETRIES, LLM_RETRY_DELAY_SEC, normalize_model
from aria.context import reset_request_context, set_request_context
from aria.db import db_save_chat
from aria.intent import detect_intent, is_document_question, is_groq_tool_error
from aria.memory import get_memory, save_memory
from aria.profile import format_profile_answer, is_name_question, save_profile_facts
from aria.prompts import build_system_prompt, get_synthesis_instruction
from aria.security import rate_limit, sanitize
from aria.tools import (
    add_task,
    calculator,
    complete_task,
    delete_task,
    list_notes,
    list_tasks,
    save_note,
    search_my_documents,
    web_search,
)

SYSTEM = build_system_prompt()

TOOL_MAP = {
    "calculator": calculator,
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "save_note": save_note,
    "list_notes": list_notes,
    "web_search": web_search,
    "search_my_documents": search_my_documents,
}


def _run_tool(intent: str, params: dict) -> str:
    tool = TOOL_MAP[intent]
    return tool.invoke(params)


def _synthesize(
    user_input: str,
    user_id: str,
    model_name: str,
    tool_result: str | None = None,
    *,
    from_documents: bool = False,
) -> str:
    system = SYSTEM
    if not from_documents:
        memory = get_memory(user_id, user_input)
        if memory:
            system += f"\n\nPast context:\n{memory}"
    if tool_result is not None:
        if from_documents or "UPLOADED DOCUMENT EXCERPTS" in tool_result:
            label = "UPLOADED DOCUMENT EXCERPTS"
            instruction = get_synthesis_instruction("document")
        elif "LIVE WEATHER" in tool_result:
            label = "LIVE DATA"
            instruction = get_synthesis_instruction("weather")
        else:
            label = "WEB SEARCH"
            instruction = get_synthesis_instruction("web")
        system += f"\n\n=== {label} ===\n{tool_result}\n=== END ===\n{instruction}"

    llm = ChatGroq(
        model=normalize_model(model_name),
        api_key=GROQ_API_KEY,
        temperature=0.1,
        max_retries=2,
    )
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_input)])
    content = getattr(response, "content", None)
    return content if content else str(response)


def _plain_chat(user_input: str, user_id: str, model_name: str) -> str:
    return _synthesize(user_input, user_id, model_name, tool_result=None)


def run_agent(user_input: str, user_id: str = "default", model_name: str | None = None) -> str:
    ok, clean = sanitize(user_input)
    if not ok:
        return f"⚠️ {clean}"
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY is missing. Add it to `.env` or `.streamlit/secrets.toml` and restart the app."
    if not rate_limit(user_id):
        return "⚠️ Too many requests. Wait 1 minute."

    model = normalize_model(model_name)
    user_token, model_token = set_request_context(user_id, model)
    try:
        save_memory(user_id, "user", clean)
        db_save_chat(user_id, "user", clean)
        save_profile_facts(user_id, clean)

        if is_name_question(clean):
            profile_mem = get_memory(user_id, "user name profile")
            direct = format_profile_answer(profile_mem)
            if direct:
                save_memory(user_id, "assistant", direct)
                db_save_chat(user_id, "assistant", direct)
                return direct
            if not profile_mem:
                response = (
                    "Abhi mujhe aapka naam nahi pata. Please bata dein: "
                    "'mera naam Huraira hai' — phir main yaad rakh loonga."
                )
                save_memory(user_id, "assistant", response)
                db_save_chat(user_id, "assistant", response)
                return response

        intent, params = detect_intent(clean)
        if intent == "chat" and is_document_question(clean):
            intent = "search_my_documents"
            params = {"query": clean}
        response = ""
        last_error = None

        for attempt in range(LLM_MAX_RETRIES):
            try:
                if intent == "chat":
                    response = _plain_chat(clean, user_id, model)
                elif intent in ("list_tasks", "list_notes"):
                    response = _run_tool(intent, params)
                elif intent == "calculator":
                    response = _run_tool(intent, params)
                elif intent in ("add_task", "complete_task", "delete_task", "save_note"):
                    response = _run_tool(intent, params)
                elif intent in ("web_search", "search_my_documents"):
                    tool_result = _run_tool(intent, params)
                    response = _synthesize(
                        clean,
                        user_id,
                        model,
                        tool_result=tool_result,
                        from_documents=(intent == "search_my_documents"),
                    )
                else:
                    response = _plain_chat(clean, user_id, model)
                break
            except Exception as exc:
                last_error = exc
                if is_groq_tool_error(exc) and intent == "chat" and attempt == 0:
                    intent = "web_search"
                    params = {"query": clean}
                    continue
                if attempt < LLM_MAX_RETRIES - 1:
                    time.sleep(LLM_RETRY_DELAY_SEC * (attempt + 1))

        if not response and last_error:
            if intent != "web_search":
                try:
                    tool_result = web_search.invoke({"query": clean})
                    response = _synthesize(clean, user_id, model, tool_result=tool_result)
                except Exception:
                    response = f"Sorry, I couldn't complete that request. Please try rephrasing your question."
            else:
                response = f"Sorry, I couldn't complete that request. ({last_error})"

        save_memory(user_id, "assistant", response)
        db_save_chat(user_id, "assistant", response)
        return response
    finally:
        reset_request_context(user_token, model_token)
