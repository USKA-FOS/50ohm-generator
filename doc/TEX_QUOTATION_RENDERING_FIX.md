# German TeX quotation rendering — AF305 regression

## Problem and cause

AF305 contains valid TeX in the German canonical question:

```latex
Dieses Blockschaltbild zeigt einen SSB-Sender. Was ist die mit \glqq?\grqq{} bezeichnete Stufe?
```

The generated course and slide HTML displayed the commands literally.
`convert_latex.py` recognised the entire quotation pair only if `\glqq`
was followed by a literal space. A question mark already delimits a TeX
control word, so that requirement was incorrect. Because conversion matches
both commands together, failure at the opening command also left the closing
command unchanged. Neither source command is invalid.

There was a second defect: recognised pairs were converted into French/Swiss
angle quotation marks. The German commands must produce **„…“**, as explicitly
confirmed by the user. AF305 must read:

> Dieses Blockschaltbild zeigt einen SSB-Sender. Was ist die mit „?“ bezeichnete Stufe?

The existing German Revision_3.0.8 PDF was checked with `pdftotext` and already
contains the correct German quotation marks. No canonical or PDF correction
is needed.

## Correction

- Accept punctuation directly after `\glqq`, as in `\glqq?\grqq{}`.
- Accept an explicit empty delimiter group: `\glqq{}TEXT\grqq{}`.
- Accept `\grqq` at the end of text or before punctuation without requiring
  an empty group or a space.
- Check control-word boundaries so commands such as `\glqqTEXT` or
  `\grqqOther` are not misidentified.
- Emit German low opening and high closing double quotation marks, U+201E
  and U+201C, rather than U+00AB/U+00BB.
- Preserve the existing protected math branch, quantity conversion, and
  recursive conversion inside underlined text.

Spaces that delimit control words are consumed; spaces after an explicit
`{}` group remain text. For example `\glqq TEXT\grqq weiter` produces
`„TEXT“weiter`, whereas `\glqq TEXT\grqq{} weiter` preserves the word space.
This follows the existing TeX convention rather than introducing extra spaces.
The converter remains a lightweight preprocessor, not a complete TeX parser;
this patch does not add nested or multiline quotation parsing.

This is command-based conversion: `\glqq`/`\grqq` are German commands wherever
used. This patch does not choose quotation styles from a page language or
rewrite existing literal French/Italian quotation marks.

## Files to port to main

The standalone fix consists of:

1. `convert_latex.py`: quotation pattern and replacement characters.
2. `test/test_convert_latex.py`: regression cases for AF305, command delimiters,
   unchanged incomplete/unknown commands and math, quantities and underlining.
3. This note, optionally linked from the target README.

It has no dependency on the recent formula font/layout changes. The shared
question converter is called in `src/build.py` for current/upstream question
and answer texts; its output feeds course and slide templates. When porting,
check that the target branch still uses this conversion path. Apply the small
quotation fix without replacing unrelated converter rules or importing the
entire Swiss branch. No canonical import or PDF change is part of the patch.
Regenerate the HTML sites after applying it; already published files are
not altered by editing the generator. No client-side cache key change is
required because conversion is performed at build time.

## Verification — 3 November 2026

20 targeted tests pass; one existing question-translation test is explicitly
skipped because it requires special files. The real canonical AF305 text also
converts to the exact sentence above. Tests cover both legacy space-delimited
forms and punctuation/brace-delimited forms. No full site build or deployment
was performed in this sequence.

From the orchestrator (writes test artifacts only under ignored `tmp/`):

```bash
mkdir -p tmp/af305-quotes-20261103/pytest
pushd 50ohm-generator >/dev/null
UV_CACHE_DIR=../tmp/uv-cache-generator uv run --locked python -m pytest \
  test/test_convert_latex.py test/test_quote.py test/test_question.py test/test_unit.py \
  --basetemp=../tmp/af305-quotes-20261103/pytest/run2 -q
popd >/dev/null
```
