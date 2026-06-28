import ast

from aria.tools import _safe_eval


def test_calculator_multiply():
    node = ast.parse("234*56", mode="eval").body
    assert _safe_eval(node) == 13104


def test_calculator_addition():
    node = ast.parse("10+5", mode="eval").body
    assert _safe_eval(node) == 15
