import json
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

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
    assert config.generator_status is True
    assert config.review_workflow is False
    assert config.shuffle_answers is False


def test_release_configuration_rejects_invalid_boolean() -> None:
    with pytest.raises(ValueError, match="Invalid boolean value"):
        Config._parse_bool("sometimes")


def test_release_inclusion_points_are_conditional() -> None:
    page = (GENERATOR_ROOT / "templates/html/page.html").read_text(encoding="utf-8")
    slide = (GENERATOR_ROOT / "templates/slide/slide.html").read_text(encoding="utf-8")

    assert 'import beta_control, language_controls with context' in page
    assert '{{ beta_control() }}' in page
    assert '{{ language_controls() }}' in page
    assert '{% if generator_status %}' in page
    assert '{% include "html/generator_status.html" %}' in page
    assert 'assets/language-switch.js' in page
    assert '{% if release_id %}' in page
    assert '{% include "html/release-footer.html" %}' in page
    assert '{% if release_id %}' in slide
    assert '{% include "slide/release-overlay.html" %}' in slide


@pytest.mark.parametrize("enabled", [False, True])
def test_review_controls_are_explicitly_enabled(enabled: bool) -> None:
    env = Environment(loader=FileSystemLoader(GENERATOR_ROOT / "templates"))
    env.globals.update(ui=lambda key: '"Message"', review_workflow=enabled)
    common = {
        "edition": "HB", "name": "Course", "number": 1,
        "chapter": {"ident": "chapter", "title": "Chapter", "abstract": "", "sections": [], "video_url": None},
        "section": {"ident": "section", "title": "Section", "content": "Content", "video_url": None},
        "section_id": 1, "markdown": "section.md", "repo": "https://example.invalid/repo",
    }
    chapter = env.get_template("html/chapter.html").render(**common)
    section = env.get_template("html/section.html").render(**common)

    assert ("/review_workflow/api/chapter-widget/" in chapter) is enabled
    assert ("/review_workflow/api/widget/" in section) is enabled
    assert ('id="github-edit-button"' in section) is enabled
    assert ('href="diff.html?file=section.md"' in section) is enabled


@pytest.mark.parametrize("enabled", [False, True])
def test_browser_answer_shuffle_asset(tmp_path, enabled):
    from types import SimpleNamespace
    from src.build import Build

    assets = tmp_path / "source-assets"
    assets.mkdir()
    source = (GENERATOR_ROOT / "assets/script.js").read_text(encoding="utf-8")
    (assets / "script.js").write_text(source, encoding="utf-8")
    builder = Build.__new__(Build)
    builder.config = SimpleNamespace(
        p_assets=assets, p_build=tmp_path / "output",
        p_build_assets=tmp_path / "output/assets", shuffle_answers=enabled,
    )
    builder.build_assets()
    output = (builder.config.p_build_assets / "script.js").read_text(encoding="utf-8")
    assert output == f"window.OHM_SHUFFLE_ANSWERS = {str(enabled).lower()};\n" + source
    assert (assets / "script.js").read_text(encoding="utf-8") == source
