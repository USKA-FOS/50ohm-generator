"""Conservative presentation classification; never edits a mathematical body."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config/formula-layout.json"


@dataclass(frozen=True)
class MathSpan:
    start: int
    end: int
    body: str
    display: bool


def escaped(text: str, position: int) -> bool:
    count = 0
    while position and text[position - 1] == "\\":
        position -= 1
        count += 1
    return bool(count % 2)


def math_spans(text: str) -> tuple[list[MathSpan], bool]:
    """Scan supported delimiters, respecting escaped dollars and TeX braces."""
    spans = []
    index = 0
    while index < len(text):
        opening = next((x for x in ("$$", "$", r"\[", r"\(")
                        if text.startswith(x, index) and not escaped(text, index)), None)
        if opening is None:
            index += 1
            continue
        closing = {"$$": "$$", "$": "$", r"\[": r"\]", r"\(": r"\)"}[opening]
        start = index
        index += len(opening)
        body_start = index
        depth = 0
        while index < len(text):
            if not escaped(text, index):
                if depth == 0 and text.startswith(closing, index):
                    spans.append(MathSpan(start, index + len(closing), text[body_start:index],
                                          opening in ("$$", r"\[")))
                    index += len(closing)
                    break
                if text[index] == "{":
                    depth += 1
                elif text[index] == "}":
                    depth -= 1
                    if depth < 0:
                        return spans, True
            index += 1
        else:
            return spans, True
    return spans, False


def classify(text: str, language: str = "de", *, context: str = "prose", config=None) -> dict:
    if config is None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    spans, malformed = math_spans(text)
    result = {"rule": "no_math", "layout": "text", "formula_count": len(spans),
              "ambiguous": False, "bodies": [s.body for s in spans]}
    if malformed:
        result.update(rule="unbalanced_delimiters", layout="preserve", ambiguous=True)
        return result
    if not spans:
        return result
    if context != "prose":
        result.update(rule="question_or_answer_inline", layout="inline")
        return result
    if re.search(r"<[^>]+>|`", text):
        result.update(rule="markup_requires_review", layout="preserve", ambiguous=True)
        return result
    if context != "prose":
        result.update(rule="question_or_answer_inline", layout="inline")
        return result
    prefix = text[:spans[0].start].strip()
    suffix = text[spans[-1].end:].strip()
    punctuation = config["terminal_punctuation"]
    suffix_ok = not suffix or (len(suffix) == 1 and suffix in punctuation)
    gaps = [text[a.end:b.start].strip() for a, b in zip(spans, spans[1:])]
    if all(span.display for span in spans) and not prefix and suffix_ok and all(not gap for gap in gaps):
        result.update(rule="explicit_display_sequence", layout="block")
        return result
    if not prefix and suffix_ok:
        if len(spans) == 1:
            rule = "explicit_display" if spans[0].display else ("punctuated_formula" if suffix else "single_formula")
            result.update(rule=rule, layout="block")
            return result
        connectors = config["connectors"].get(language, [])
        if all(gap.casefold() in connectors for gap in gaps):
            result.update(rule="connected_formula_group", layout="block")
            return result
        if any(len(gap) > 32 for gap in gaps):
            result.update(rule="formula_in_prose", layout="inline")
            return result
        result.update(rule="unrecognized_formula_connector", layout="preserve", ambiguous=True)
        return result
    result.update(rule="formula_in_prose", layout="inline")
    return result


def display_html(text: str, classification: dict) -> str:
    """Keep each body intact and outside text (including punctuation) verbatim."""
    spans, malformed = math_spans(text)
    if malformed or classification["layout"] != "block":
        raise ValueError("Only a validated math block may be promoted")
    # Put group connectors in separate text nodes, not inside \text{...}.
    pieces = []
    previous = 0
    for index, span in enumerate(spans):
        pieces.append(text[previous:span.start])
        suffix = text[span.end:] if index == len(spans) - 1 else ""
        pieces.append('<span class="formula-item">\\[' + span.body + '\\]' + suffix + '</span>')
        previous = span.end
    return '<div class="formula-block" data-formula-rule="' + classification["rule"] + '">' + ''.join(pieces) + '</div>\n'
