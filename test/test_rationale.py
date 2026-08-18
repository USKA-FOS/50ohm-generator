import pytest


def test_rationale_text_accepts_list_or_string():
    pytest.importorskip("mistletoe")
    from src.build import Build

    build = Build.__new__(Build)
    assert build._Build__rationale_text(["One", "Two"]) == "One; Two"
    assert build._Build__rationale_text("One; Two") == "One; Two"
    assert build._Build__rationale_text(None) is None
