import re

from aria.memory import save_memory

NAME_INTRO = re.compile(
    r"(?i)(?:mara name|mera naam|my name is|call me|i am|i'm)\s+([A-Za-z]+)"
)
NAME_ASK = re.compile(r"(?i)(?:mara|mera)\s+(?:name|naam)\s+(?:kia|kya|hai|hain|ha)\b")
STUDENT_INTRO = re.compile(r"(?i)\b(bs\s*ai|b\.s\.?\s*ai)\b.*\bstudent\b|\bstudent\b.*\b(bs\s*ai|b\.s\.?\s*ai)\b")


def extract_profile_facts(text: str) -> list[str]:
    facts = []
    if m := NAME_INTRO.search(text):
        facts.append(f"User's name is {m.group(1).capitalize()}")
    if STUDENT_INTRO.search(text) or re.search(r"(?i)bs ai ka student", text):
        facts.append("User is a BS AI student")
    return facts


def is_name_question(text: str) -> bool:
    return bool(NAME_ASK.search(text.strip()))


def save_profile_facts(user_id: str, text: str) -> None:
    facts = extract_profile_facts(text)
    if facts:
        save_memory(user_id, "profile", ". ".join(facts))


def format_profile_answer(profile_memory: str) -> str | None:
    if not profile_memory:
        return None
    lower = profile_memory.lower()
    if "name is" in lower:
        name_match = re.search(r"(?i)user's name is\s+([A-Za-z]+)", profile_memory)
        name = name_match.group(1) if name_match else "unknown"
        if "bs ai" in lower:
            return f"Aapka naam **{name}** hai, aur aap BS AI ke student hain."
        return f"Aapka naam **{name}** hai."
    return None
