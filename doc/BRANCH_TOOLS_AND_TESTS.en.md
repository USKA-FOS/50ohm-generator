# Tools and tests added in our generator branch

Snapshot: **23 November 2026**.
Repository: `USKA-FOS/50ohm-generator`.
Branch: `design/object-centric-canonical` at
after the formula experiment withdrawal (recovery checkpoint `c9d2e9d`).
Comparison: `origin/main` at `b5d5ea6e0b4f1b54b22bf74f9faa54a4f7b51938`.

This register documents supporting tools and automated checks, their purpose,
implementing commits and execution requirements.

## 1. Added tools

### Local review-build script

**File.** `build_local_review_site.sh`.

**Purpose.** Build a selected language, or all three languages, using the
corresponding local configuration and an optional fixed seed.

**Motivation.** Provide a repeatable way to inspect local language builds and
keep randomized answer order stable during comparisons.

**Commits.** `d19021d`: script and seed support; `f31cee7`: workspace-path
adjustment.

**Inputs and effects.** Accepts `[de|fr|it|all]` and an optional seed. Reads
language configurations from `../sites/app/config/<language>.json`, copies the
selected configuration to the generator's `config/config.json`, and runs the
builder. It writes build outputs and replaces the active local configuration.
The configured directories must exist before use. Its recorded paths reflect
its original workspace layout.

The experimental formula inventory/preview tool is retained only on
`fix/formula-presentation` at `fa6ca9f`. See
[withdrawal record](FORMULA_EXPERIMENT_WITHDRAWAL.en.md).

## 2. Added Python tests

The branch adds **13 test functions**, producing **38 collected cases** through
parameterization.

| File                                | Added functions | Added cases | Purpose                                                                                                                                       | Implementing commits                                                                          |
| ----------------------------------- | --------------: | ----------: | --------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `test/test_rationale.py`            |               1 |           1 | String, list and absent rationale handling                                                                                                    | `e366905`                                                                                     |
| `test/test_release_presentation.py` |               5 |           7 | Configuration defaults, boolean validation, conditional release/review controls and generated shuffle setting                                 | `1009f32`, `bcfe2ed`, `913b3d7`, `487465a`, `19af725`, `c5900b0`; fixture update in `69bec73` |
| `test/test_convert_latex.py`        |               3 |          15 | Quotation-command delimiters, incomplete/other commands, protected math and existing conversion behavior                                      | `3cea91e`, `01c6ebc`, `d9dcae2`                                                               |
| `test/test_nonbreaking_spaces.py`   |               1 |           6 | Unicode nonbreaking and narrow nonbreaking spaces around ellipses in HTML and LaTeX                                                           | `825686d`                                                                                     |
| `test/test_main_sync.py`            |               3 |           9 | Optional comparison catalog, localized entrypoint titles and miniature course builds across languages and editions                            | `69bec73`                                                                                     |
| **Total**                           |          **13** |      **38** |                                                                                                                                               |                                                                                               |

The tests in `test_main_sync.py` actually exercise the builder and its templates:
small DE/FR/IT datasets are built for A, NE and NEA, checking numbering, badges,
section selection, disabled-course labels and legacy inline formula markup.

### Adapted existing Python tests

| File | Adjustment | Reason | Commits |
| --- | --- | --- | --- |
| `test/test_quote.py` | Update expected HTML quotations to Swiss angle quotation marks | Match the selected publication convention | `d9dcae2` |

These adaptations are not counted as additional test functions.

## 3. Added JavaScript and browser tests

The branch adds **5 cases** in two files.

| File | Cases | Purpose | Commit |
| --- | ---: | --- | --- |
| `test/language-switch.test.cjs` | 4 | Preserve page/query/anchor and deployment prefix, restore scroll position, respect modified clicks and handle unavailable storage | `bcfe2ed` |
| `test/latex-unit-macros.test.cjs` | 1 | Render representative canonical quantities and unit macros with the bundled KaTeX | `19af725` |
| **Total** | **5** | | |

## 4. Running the checks

From the orchestration workspace, keep caches and diagnostics in its ignored
`tmp/` directory.

### Python suite

```bash
mkdir -p tmp/generator-tests/pytest
pushd 50ohm-generator >/dev/null
TMPDIR=../tmp/generator-tests/pytest \
UV_CACHE_DIR=../tmp/uv-cache-generator \
uv run --locked python -m pytest -q \
  -o cache_dir=../tmp/generator-tests/pytest-cache
popd >/dev/null
```

### JavaScript checks without a browser

```bash
pushd 50ohm-generator >/dev/null
node --test test/language-switch.test.cjs \
  test/latex-unit-macros.test.cjs
popd >/dev/null
```

## 5. Current test status

The complete Python run after withdrawal reports:

- **83 passed**;
- **8 failed**;
- **3 skipped**.

The same eight failures were recorded before the latest main synchronization.
They concern inherited caption tests whose label configuration or expected
output was not updated when interface text was externalized:

```text
test/test_hierarchical_numbering.py::test_hierarchical_picture_numbering
test/test_hierarchical_numbering.py::test_hierarchical_photo_numbering
test/test_hierarchical_numbering.py::test_hierarchical_table_numbering
test/test_hierarchical_numbering.py::test_mixed_figure_types_share_counter
test/test_hierarchical_numbering.py::test_slide_renderer_adds_s_suffix
test/test_hierarchical_numbering.py::test_fallback_numbering_without_context
test/test_photo.py::test_photo_html
test/test_picture.py::test_picture_html
```

Their correction has been deferred. They remain visible test debt rather than
being removed from the suite. The before/after comparison and latest test logs
are retained in the orchestration workspace under
`tmp/generator-main-sync-20261121/`. Withdrawal verification is retained in
`tmp/formula-withdrawal-20261123/`; the five remaining JavaScript checks also pass.
