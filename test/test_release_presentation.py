import json
from pathlib import Path

import pytest

from src.config import Config

GENERATOR_ROOT = Path(__file__).resolve().parents[1]


def test_release_configuration_defaults_to_inactive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_root = tmp_path / "config"
    config_root.mkdir()
    (config_root / "config.json").write_text(
        json.dumps({"input": "input/de", "questions_upstream": "upstream.json"}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = Config()

    assert config.release_id is None
    assert config.beta is False
    assert config.feedback_url is None


def test_release_configuration_rejects_invalid_boolean() -> None:
    with pytest.raises(ValueError, match="Invalid boolean value"):
        Config._parse_bool("sometimes")


def test_release_inclusion_points_are_conditional() -> None:
    page = (GENERATOR_ROOT / "templates/html/page.html").read_text(encoding="utf-8")
    slide = (GENERATOR_ROOT / "templates/slide/slide.html").read_text(encoding="utf-8")

    assert 'import beta_control, language_controls with context' in page
    assert '{{ beta_control() }}' in page
    assert '{{ language_controls() }}' in page
    assert 'assets/language-switch.js' in page
    assert '{% if release_id %}' in page
    assert '{% include "html/release-footer.html" %}' in page
    assert '{% if release_id %}' in slide
    assert '{% include "slide/release-overlay.html" %}' in slide
