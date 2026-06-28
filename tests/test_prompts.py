from aria.prompts import build_system_prompt, get_synthesis_instruction


def test_system_has_few_shots():
    prompt = build_system_prompt()
    assert "FEW-SHOT EXAMPLES" in prompt
    assert "Prime Minister of Pakistan" in prompt
    assert "weather in karachi" in prompt
    assert "what is in the file" in prompt


def test_document_instruction():
    text = get_synthesis_instruction("document")
    assert "document" in text.lower()
    assert "chat history" in text.lower()


def test_weather_instruction():
    text = get_synthesis_instruction("weather")
    assert "temperature" in text.lower() or "°C" in text
