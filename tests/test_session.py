from aria.session import VALID_UID


def test_valid_uid_pattern():
    assert VALID_UID.match("user_ab12cd34")
    assert not VALID_UID.match("user_bad!")
    assert not VALID_UID.match("admin")
