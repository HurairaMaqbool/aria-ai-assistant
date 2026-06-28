from aria.profile import extract_profile_facts, format_profile_answer, is_name_question


def test_name_question_urdu():
    assert is_name_question("mara name kia ha")


def test_extract_name_and_student():
    facts = extract_profile_facts("mara name huraira how ma bs ai ka student ho")
    assert any("Huraira" in f for f in facts)
    assert any("BS AI" in f for f in facts)


def test_format_profile_answer():
    ans = format_profile_answer("User's name is Huraira. User is a BS AI student.")
    assert "Huraira" in ans
    assert "BS AI" in ans
