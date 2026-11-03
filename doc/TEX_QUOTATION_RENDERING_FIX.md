# German TeX quotation rendering — AF305 and porting notes

## Required source convention and result

The agreed question-source forms are:

```latex
\glqq Text\grqq{}
\glqq{}Text\grqq{}
```

Both produce **„Text“**. The first space delimits the opening command and is
not displayed; the empty group is the alternative explicit delimiter.
`\glqqText` is a different control word and must not be interpreted as `\glqq`.
For canonical consistency, the user requires an explicit opening delimiter
also before punctuation: AF305 now uses `\glqq ?\grqq{}`.
This is the chosen source convention, not a complete TeX syntax validator.

Expected AF305 output:

> Dieses Blockschaltbild zeigt einen SSB-Sender. Was ist die mit „?“ bezeichnete Stufe?

The canonical separator correction and rebuilt catalogs are recorded in
question-pool Revision_3.0.9, with an accepted manual-correction audit. It changes
no meaning, answer, translation or review status. The existing Revision_3.0.8
German PDF already rendered the quotes correctly; no PDF regeneration was
requested for this source-convention change.

## Generator defects and final correction

The original question converter matched an entire pair only when `\glqq` was
followed by a literal space. When the opening was not matched, the closing
command also remained literal in HTML. It additionally emitted angle quotation
marks `«…»`, which are wrong for these German commands.

Commit `3cea91e` initially broadened recognition to include a bare punctuation
character after the opening command and corrected the output characters.
Following the user's clarification, **only the bare-opening acceptance is
withdrawn**. German output is retained. The converter now:

- requires a space/tab separator or an explicit `{}` after `\glqq`;
- accepts both agreed forms without displaying the command separator;
- emits German U+201E/U+201C quotation marks **„…“**;
- leaves bare `\glqq?`, longer command names and incomplete pairs unchanged;
- preserves protected math, quantity conversion and recursion in underlining.

The closing-command boundary check and support for a closing command before
punctuation/end of text are retained. Spaces following a command delimiter are
consumed; spaces after explicit `{}` remain ordinary text. The converter is
not a complete TeX parser and does not add nested or multiline quotations.
Existing literal French/Italian quotation marks are not rewritten. This is
command-based conversion, not page-language typography selection.

## Files to port to main

1. `convert_latex.py`: final quotation pattern and German replacement symbols.
2. `test/test_convert_latex.py`: accepted separator forms, explicit rejection
   of bare openings and longer commands, math/quantity/underlining regressions.
3. This document and its optional README link.

This fix is independent of the formula font/layout changes. The shared
converter is called in `src/build.py` for current/upstream question and answer
texts, then used in course and slide templates. Check that conversion path
on the target branch; port only the relevant quotation changes, not the entire
Swiss branch. Do not cherry-pick `3cea91e` alone without the follow-up that
withdraws bare-opening support. Also publish the corrected AF305 question source.
No PDF-renderer change is involved. HTML sites must be rebuilt after applying
the changes; no client-side cache key change is needed for server-side conversion.

## Verification — 3 November 2026

Regression tests cover AF305 with the required space, explicit `{}`, bare
opening rejection, longer/incomplete commands, protected math, quantities and
underlining. One pre-existing question-translation test requires special files
and is marked skipped. Exact results and deployment revisions are recorded in
the orchestrator's `TOOLS_AND_COMMANDS_SUMMARY.md`.

From the orchestrator (writes tests only under ignored `tmp/`):

```bash
mkdir -p tmp/revision-3.0.9/pytest
pushd 50ohm-generator >/dev/null
UV_CACHE_DIR=../tmp/uv-cache-generator uv run --locked python -m pytest \
  test/test_convert_latex.py test/test_quote.py test/test_question.py test/test_unit.py \
  --basetemp=../tmp/revision-3.0.9/pytest/run -q
popd >/dev/null
```
