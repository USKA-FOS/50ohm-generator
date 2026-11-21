"""Integration regressions for upstream class badges and optional pool input."""
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from jinja2 import ChoiceLoader, DictLoader

from src.build import Build
from src.config import Config

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("setting", [{}, {"questions_upstream": None}, {"questions_upstream": "old.json"}])
def test_optional_upstream_pool(tmp_path, monkeypatch, setting):
    (tmp_path / "config").mkdir()
    (tmp_path / "config/config.json").write_text(json.dumps({"input": "input/de", **setting}))
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OHM_QUESTIONS_UPSTREAM", raising=False)
    conf = Config()
    expected = Path("input/de/contents/questions/old.json") if setting.get("questions_upstream") else None
    assert conf.p_data_fragenkatalog_upstream == expected


@pytest.mark.parametrize("language", ["de", "fr", "it"])
def test_entrypoint_retains_localized_course_titles(monkeypatch, language):
    import src.build
    import src.config

    builder = MagicMock()
    monkeypatch.setattr(src.config, "Config", lambda **kw: SimpleNamespace(language=language))
    monkeypatch.setattr(src.build, "Build", lambda conf: builder)
    monkeypatch.setattr("sys.argv", ["build.py"])
    runpy.run_path(str(ROOT / "build.py"), run_name="__main__")
    titles = {"de": "Upgrade-Kurs auf HB9", "fr": "Cours de mise à niveau vers HB9", "it": "Corso di aggiornamento a HB9"}
    calls = builder.build_unified_edition.call_args_list
    assert [call.args[1] for call in calls] == ["A", "NE", "NEA"]
    assert calls[0].args[2] == titles[language]
    assert all(call.args[3] == {"N": "HB3", "E": "HB3", "A": "HB9"} for call in calls)
    builder.build_question_index.assert_called_once()


@pytest.mark.parametrize("language", ["de", "fr", "it"])
def test_badges_numbering_and_formula_layout_in_all_editions(tmp_path, monkeypatch, language):
    source = tmp_path / language
    for rel in ["toc", "contents/questions", "contents/sections", "contents/slides"]:
        (source / rel).mkdir(parents=True, exist_ok=True)
    sections = [{"ident": level, "title": level, "class": level, "video_url": None} for level in "NEA"]
    chapters = [{"ident": "chapter" + level, "title": "Chapter " + level, "abstract": "", "video_url": None, "sections": [section]} for level, section in zip("NEA", sections)]
    (source / "toc/HB.json").write_text(json.dumps({"abstract": "", "chapters": chapters}))
    (source / "contents/questions/fragenkatalog3b.json").write_text('{"sections": []}')
    for level in "NEA":
        (source / f"contents/sections/{level}.md").write_text("$U = R I$.\n")
        (source / f"contents/slides/{level}.md").write_text("Example\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OHM_QUESTIONS_UPSTREAM", raising=False)
    conf = Config(content_path=str(source), build_path=str(tmp_path / "output"))
    conf.config["repo_base_url"] = None
    conf.p_templates = ROOT / "templates"
    builder = Build(conf)
    builder.env.loader = ChoiceLoader([DictLoader({"html/page.html": "{{ content }}", "slide/slide.html": "{{ content }}"}), builder.env.loader])
    for edition in ["A", "NE", "NEA"]:
        builder.build_unified_edition("HB.json", edition, "Localized " + language, {"N": "HB3", "E": "HB3", "A": "HB9"})
        for index, level in enumerate("NEA", 1):
            chapter = (conf.p_build / f"{edition}_chapter_chapter{level}.html").read_text()
            badge = "HB9" if level == "A" else "HB3"
            assert f'>{index}. Chapter {level}</h1>' in chapter
            assert f'class="badge {badge}"' in chapter
            section = conf.p_build / f"{edition}_{level}.html"
            assert section.exists() is (level in edition)
            if section.exists():
                html = section.read_text()
                assert f'>{index}.1 {level}<span class="badge {badge}"' in html
                assert 'class="formula-block"' in html
        index_html = (conf.p_build / f"{edition}_course_index.html").read_text()
        if edition != "NEA":
            assert "(HB3)" in index_html if edition == "A" else "(HB9)" in index_html
