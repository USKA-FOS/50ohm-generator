# Website formulas: situation analysis and rendering strategy

This document explains the problem, its causes, the chosen presentation policy
and the corrections implemented in the normal 50ohm generator. Validation
counts and working-file locations are supporting evidence in the appendices,
not the specification itself.

The implementation is in generator commit `3618738`, following the clean
recovery baseline `c5900b0`. It was used for
`beta-2026-10-30-QP_Revision_3.0.8` (site-release commit `9c7bd63d3`).

## 1. The problem to solve

The website uses sans-serif running text. A short variable, value or expression
inside a sentence should fit naturally into that sentence: a compatible family,
a comparable visual size and an appropriate baseline. Previously, some formulas
introduced a conspicuous font change or appeared larger than their surroundings.

A separate issue affected equations that authors had placed on their own lines.
Visually similar equations could use different families, sizes and fraction
layouts, even on the same page. Some subsequently wrapped after relation signs
such as `=`, although the available line could accommodate the whole equation.

There are therefore three distinct concerns:

1. **Context:** is this expression part of a sentence or a standalone equation?
2. **Typography:** which family, shape and size should that context use?
3. **Layout:** how much width does the equation receive, and where may it break?

A CSS font substitution alone cannot resolve all three.

The PDF question catalogue uses a serif text face and has a different rendering
pipeline. Its formulas do not present the same contrast with running text.
No PDF font or generation change was requested for this work.

## 2. Analysis of the previous situation

### 2.1 A concrete example: NE_spitze_effektiv_wert

The page revealed an inconsistent distinction between source syntax and intended
visual context. These are the relevant source shapes, abbreviated only where
that does not affect the explanation:

| Source shape | Intended context | Previous treatment | Reason |
|---|---|---|---|
| `$U_{eff} = \frac{\hat{U}}{\sqrt{2}}$ oder $\hat{U} = U_{eff}\cdot\sqrt{2}$` | Standalone group of two equations | Inline formulas inside a paragraph | The detector accepted only a single formula occupying the complete source line |
| `$\hat U = \qty{230}{\volt}\cdot\sqrt 2 \approx \qty{325}{\volt}$.` | Standalone calculation, with punctuation | Inline formula inside a paragraph | The period outside the closing `$` prevented recognition as a formula block |
| `$U_\text{SS} = 2\cdot\qty{230}{\volt}\cdot\sqrt 2 \approx \qty{651}{\volt}$` | Standalone calculation | Display formula | It matched the single-formula-only line rule |
| A sentence containing `$\qty{230}{\volt}$` | Expression within prose | Inline formula | This was the correct classification |

A paragraph on its own line is not necessarily display math in the generated
HTML. The original block detector required a very specific source form. A final
period or the word “oder” was enough to make otherwise comparable equations
follow different rendering paths.

### 2.2 Inline and display math are not merely different alignments

KaTeX has separate inline and display modes. They affect layout and the initial
mathematical style, including fractions and large operators. Changing a formula
from inline to display therefore does more than centre it.

In the old page, the two inline calculations and the display calculation did
not share that style. Differences between their mathematical structures —
fractions, accents, plain numbers and formatted quantities — made the visual
inconsistency even more obvious. There were not three independent math engines;
there were different contexts and partial style overrides within one pipeline.

In this generator, `assets/latex.js` is local integration code calling KaTeX.
Its filename does not mean that a second library named LaTeX.js is rendering
these expressions alongside KaTeX.

### 2.3 Broad CSS overrides mixed font families and local sizes

The old stylesheet targeted formulas under paragraphs, questions and lists.
It replaced the family of `.katex` and `.mathnormal` with generic `sans-serif`
and fixed the outer formula size to `1rem`.

This had two consequences:

- **Partial family replacement:** some letters followed the replacement family,
  while units, accents, symbols or other parts could retain KaTeX families.
  The result was not necessarily one coherent mathematical font system.
- **Size detached from context:** `rem` is relative to the document root. It does
  not automatically follow a smaller answer, a larger passage or another local
  text size. A fixed root-relative size cannot ensure integration everywhere.

There is also a distinction between three independent typographical properties:
family (serif/sans), shape (upright/italic), and weight (regular/bold).
Selecting sans-serif must not inadvertently make variables upright. Conversely,
selecting italic must not silently turn units into variables.

KaTeX positions glyphs, accents, indices and fractions using font metrics.
Forcing the surrounding Inter font onto all its internal spans was therefore
rejected as the general solution: it could improve apparent similarity while
making mathematical positioning less reliable.

### 2.4 Narrow previews and equation wrapping obscured the result

The first comparison placed Before and After in side-by-side frames, giving
each approximately half of the available browser width. This was an unsuitable
basis for deciding whether a standalone equation fitted on a website line.

Separately, an existing `white-space: normal` rule allowed KaTeX display content
to wrap between its root segments, often around relation signs. Shrinking flex
items could make those breaks happen even when the outer container had room.
A correct display classification alone did not prevent this layout defect.

The missing space after answer prefixes was another independent CSS problem:
`A:`/`B:`/`C:`/`D:` pseudo-elements did not guarantee a following space.
It required an explicit spacing correction, not a change to the formula source.

### 2.5 The first inventory also had extraction errors

The initial `unbalanced_delimiters` results did not prove that formulas were
broken. The audit was examining individual HTML-parser data callbacks rather
than the complete text nodes seen by the browser.

Entity references such as `&amp;` and `&lt;` split parser callbacks. A formula
could consequently be inspected as two incomplete fragments, even though the
browser saw one balanced expression. JavaScript containing `$` was also being
mistaken for mathematical prose.

All 174 distinct alerts examined were explained by these two causes: 30 script
fragments and 144 entity-split fragments. The correct response was to fix the
extractor. Adding dollars or braces to canonical content on that evidence would
have corrupted valid input.

## 3. Requirements and boundaries

The chosen solution must:

- distinguish prose expressions from standalone equations deterministically;
- integrate inline expressions with sans-serif running text;
- give comparable standalone equations a consistent serif mathematical rendering;
- preserve mathematical content, punctuation, order and deliberate multiline layout;
- preserve the source's distinctions between variables, upright labels and units;
- avoid unnecessary canonical changes and differences that complicate DARC sync;
- work for DE, FR and IT through explicit configuration rather than language guesses;
- report uncertain cases without inventing corrections or aborting an entire build;
- remain separate from PDF generation and the previous slide presentation profile.

This is a rendering policy, not a new mathematical notation policy. Determining
whether an index denotes a variable, a physical quantity or a descriptive label
still requires knowing its meaning. This work does not automatically decide that
`L`, for example, means load rather than inductance, or rewrite its source style.

## 4. The chosen approach

### 4.1 Classify context before applying typography

Existing bare-formula block tokens retain their block treatment. For additional
cases, the HTML renderer classifies the complete rendered paragraph, rather
than promoting whichever source line happens to look mathematical.

| Paragraph content | Decision | Preservation rule |
|---|---|---|
| One mathematical expression alone | Display block | Preserve the body unchanged |
| One expression followed only by a single permitted punctuation mark | Display block | Keep punctuation outside the mathematical body |
| Expressions separated only by configured connectors | Display group | Keep each body and the connector text separately |
| Existing consecutive explicit display expressions | Separate display rows | Preserve their deliberate separation |
| A sentence containing one or more expressions | Inline | Preserve the surrounding prose |
| Question or answer field | Keep its existing inline/explicit-display context | Do not centre an answer merely because it contains only a formula |
| Mixed markup, genuinely unbalanced input or an unrecognized short separator | Preserve and report | Do not guess a correction |

Connectors are explicit configuration: German `oder`, `und`, `bzw.`; French
`ou`, `et`, `soit`; Italian `o`, `oppure`, `e`. Allowed final punctuation is
also configured. No AI or semantic interpretation is used for classification.

For example, the two U_eff/Û expressions become one display group with “oder”
between them, and the 325 V calculation becomes a display block with its final
period retained. The 230 V value in a sentence remains inline. The 651 V
calculation keeps its display status.

### 4.2 Give inline and display contexts their own presentation

| Property | Inline expression | Standalone equation |
|---|---|---|
| Visual family | Native mathematical sans where supported | Native mathematical serif |
| Size | Relative to local text (`1em`) | Consistent display size (`1.1em`) |
| Position | Within the sentence and its baseline | On its own line, centred when it fits |
| Variables and units | Preserve shape distinctions | Preserve the same distinctions |
| Font metrics | Use supported renderer font commands | Retain the renderer's mathematical metrics |

The inline target is visual compatibility with the prose, not an unsupported
promise that every mathematical glyph will be drawn in exactly the Inter font.
Latin variable atoms use native sans-italic presentation; upright quantities,
labels and units retain an upright presentation. Specialised source fonts and
unknown constructions are protected rather than interpreted semantically.
Greek letters or special glyphs may use the renderer's native fallback.

These choices balance integration with reliable mathematical layout. They avoid
both an uncontrolled mix of arbitrary CSS families and a wholesale replacement
of the rendering engine.

### 4.3 Keep a standalone equation intact within the available width

Display equations use the full content line. Their items do not shrink, and
ordinary KaTeX segment boundaries are not allowed to introduce automatic breaks
at `=` or similar operators.

If a complete equation really exceeds the viewport, its container provides
horizontal scrolling. It is neither cut nor reduced until the text becomes
unreadably small. Explicit author-created multiline structures and consecutive
display rows are retained; they are not flattened into one line.

The comparison follows the same principle: Before and After are selected by
buttons and each receives the full preview width. The answer prefixes contain
an explicit nonbreaking space, so adjacent math does not remove their spacing.

### 4.4 Make classification errors visible without modifying the source

The inventory now coalesces adjacent entity/data callbacks into complete browser
text nodes. It excludes script/style and code-like contents from math analysis.
Actual markup boundaries remain meaningful; fragments are not joined across
unrelated elements just to balance their delimiters.

The report retains source locations, classifications, exact fragments, hashes
and ambiguity reasons. A detected ambiguity is material for inspection, not
authorization to rewrite canonical. The renderer likewise keeps malformed
historical expressions in their previous representation rather than making a
whole site build fail during this presentation step.

## 5. Corrections implemented and why

| Area | Previous problem | Correction |
|---|---|---|
| Paragraph renderer | Punctuation and connectors prevented display classification | Apply the configured paragraph classification and emit explicit block/group markup |
| Formula markup | CSS relied indirectly on surrounding paragraph/list elements | Give display groups and items stable presentation classes |
| Browser integration | One broad rendering/style path for both contexts | Render display math first, then inline math without reprocessing generated KaTeX |
| Inline typography | Arbitrary CSS family substitutions on internal glyphs | Select supported native font commands and keep local relative size |
| Display typography | Comparable standalone equations used different styles | Use native serif display math consistently for recognized blocks |
| Equation layout | Wrapping at relation signs and shrinking items | Use full-width containers, nowrap and non-shrinking items; scroll only when necessary |
| Answer prefixes | No guaranteed space after the colon | Add a nonbreaking space after A:/B:/C:/D: |
| Inventory | Script dollars and split entity callbacks produced false alerts | Exclude non-content nodes and coalesce actual text nodes |
| Preview | Half-width panels distorted line-fit assessment | Switch full-width Before/After views using the same sample IDs |
| Asset delivery | Browsers could retain old CSS/JavaScript | Version affected URLs with `formula-layout-1` |

These changes alter generated presentation. They do not change stored formula
bodies or automatically align translated wording. Custom raw-HTML includes or
unrecognized structures can retain their existing layout and remain subject
to inspection; this is not a claim of automatic interpretation of every possible
DarcDown/HTML construction.

## 6. Alternatives considered and remaining limits

**Changing every source formula** was rejected as the general solution. Most
of the observed differences came from classification and presentation, not a
need to rewrite the German catalogue. Unnecessary source edits would complicate
synchronization and could introduce translation or notation differences.

**Using one universal CSS font override** was rejected because it does not
resolve inline/display classification and can bypass the engine's glyph metrics.
**Using serif everywhere on the website** would preserve conventional math
fonts but leave the original contrast within sans-serif prose unresolved.
**Replacing KaTeX or changing PDF typography** was unnecessary for this scope.

The retained solution does not determine mathematical equivalence, correct a
formula's meaning, infer the role of an index, guarantee an all-Inter formula,
or replace human visual review. Detection tests and browser checks complement
that review; they do not prove the correctness of every equation.

## Appendix A — Implementation map

| File | Responsibility |
|---|---|
| `config/formula-layout.json` | Per-language connectors and permitted punctuation |
| `renderer/formula_layout.py` | Delimiter-aware classification and body-preserving block markup |
| `renderer/fifty_ohm_html_renderer.py` | Apply classification to ordinary page paragraphs and formula tokens |
| `renderer/fifty_ohm_html_slide_renderer.py` | Keep the slide renderer opted out |
| `assets/formula-inline.js` | Supported native inline font selection and compatibility macros |
| `assets/latex.js` | Separate display and inline rendering passes |
| `assets/style-course.css` | Contextual sizing, block width/overflow and answer-label spacing |
| `templates/html/page.html` | Enable the normal-page profile and load/version its assets |
| `tools/audit_formula_layout.py` | Read-only inventory and reproducible comparison pages |

The bundled engine is KaTeX **0.13.11**. Commands shown by current online
documentation must not be assumed to exist in that version. The inline-only
`\mathsfit` compatibility macro uses supported `\textsf`/`\textit` stacking.
Variable atoms are grouped so unbraced accents and subscripts retain their
arguments. Explicit specialised fonts, quantity arguments, environment names
and unknown command arguments are protected from ordinary-variable conversion.
The canonical formula is not rewritten; the transformation is scoped to browser
presentation. Unsupported Greek/special glyphs keep native fallback metrics.

The normal HTML template enables `data-formula-presentation="contextual"`.
Display expressions are consumed before the inline pass; the second pass ignores
existing `.katex` trees. Pages outside that profile retain the previous rendering
branch. This scope separation is why PDF and slide changes were not required.

## Appendix B — Reference inventory and validation results

These figures describe the frozen development inventory, not a fresh scan of
the currently published release. They document the evidence used to choose and
verify the corrections.

All retained results are under the orchestrator's ignored directory
`tmp/formula-presentation-20261030/`:

| Path | Purpose |
|---|---|
| `index.html` | Full-width Before/After switch and example selector |
| `report-v3.json`, `report-v3.md` | Corrected inventory and summary |
| `before-detector-fixed/` | Historical rendering with frozen baseline assets |
| `after-detector-fixed/` | Proposed normal-generator rendering |
| `detector-fix-validation.json` | Source/asset/browser/test verification |
| `cleanup-manifest.json` | Inventory of removed obsolete outputs and caches |

The report scans 3,540 pages, 12,736 distinct fragments and 26,180 occurrences.
There are 137 variants and 307 selected examples, including every mathematical
fragment on the reported German page. There are zero unbalanced-delimiter flags.
829 distinct prose fragments qualify for promotion. Preserved mixed-markup or
separator cases are inventory findings, not necessarily source errors.

Both preview states use the same report and sample IDs. Before assets were
copied from the frozen original and verified by hash, never recreated from the
corrected assets. Browser checks found zero KaTeX errors in both selected
previews. The three reported equations use consistent serif display mode.
All source-page hashes remained unchanged. Visual acceptance belongs to the user.

Obsolete intermediate reports, previews, browser profiles and test caches were
removed on request; their names and report hashes remain in the cleanup manifest.
No provider response, checkpoint, human review or canonical import audit was in
that cleanup scope.

## Appendix C — Operational commands

From the orchestrator; these commands write diagnostics only. Existing report
and preview destinations refuse overwrite: use a new run directory for a new
inventory. `--assets-from` reuses a known historical asset set. For reproduction
without that working copy, historical assets can be reconstructed from baseline
`c5900b0` using `git archive`, without checking out or changing the active branch.

```bash
pushd 50ohm-generator >/dev/null
run_dir='../tmp/formula-presentation-new'
UV_CACHE_DIR=../tmp/uv-cache-generator uv run --locked python tools/audit_formula_layout.py scan \
  --site-root ../50ohm-site-releases --output "$run_dir/report.json"
UV_CACHE_DIR=../tmp/uv-cache-generator uv run --locked python tools/audit_formula_layout.py preview \
  --report "$run_dir/report.json" --phase before \
  --assets-from ../tmp/formula-presentation-20261030/before-detector-fixed/assets \
  --output "$run_dir/before"
UV_CACHE_DIR=../tmp/uv-cache-generator uv run --locked python tools/audit_formula_layout.py preview \
  --report "$run_dir/report.json" --phase after --output "$run_dir/after"
UV_CACHE_DIR=../tmp/uv-cache-generator uv run --locked python tools/audit_formula_layout.py compare \
  --report "$run_dir/report.json" --before "$run_dir/before" \
  --after "$run_dir/after" --output "$run_dir/index.html"
popd >/dev/null
```

Serve only the retained validation folder:

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null
python -m http.server 8766 --bind 127.0.0.1 \
  --directory tmp/formula-presentation-20261030
popd >/dev/null
```

Open `http://127.0.0.1:8766/`. The previews also work as local HTML files.
They use bundled assets and no CDN. No persistent server is started by the audit.

## Appendix D — Verification coverage

Regression coverage includes named/numeric HTML entities, ignored code, mixed
code/prose, real markup splits and real unclosed delimiters, frozen Before
assets, escaped dollars, punctuation/connector/body preservation, multiline
paragraphs and slide opt-out. JavaScript checks exercise the bundled KaTeX,
variable/unit styles and separation of display and inline passes. Integration
checks exercise the real page template/asset loader in DE/FR/IT. The relevant
CSS references use `formula-layout-2`; unchanged JavaScript references retain
`formula-layout-1` to invalidate stale browser copies. Malformed legacy formulas retain their previous representation rather
than aborting rendering.
No complete website or PDF build is needed for these checks.

References: [display mode](https://katex.org/docs/options.html),
[font commands](https://katex.org/docs/supported.html#font),
[auto-render](https://katex.org/docs/autorender.html).


## Full-page correction: floated margin figures and clipped equations

The published `NE_spitze_effektiv_wert.html` exposed a layout defect that the
isolated examples did not cover. Desktop courses have a 59.3% text column and
floated right-margin figures. The new formula block occupied 100% of the course.
Its overflow container could not fit beside the float and moved below the
figure, leaving a large blank area. Centring also used the wrong available width.
An older descendant selector applied the 59.3% width again to nested KaTeX display
spans, causing equation ink to extend beyond its measured container and be clipped.
This was a CSS integration defect, not incorrect canonical mathematics.

The outer formula block now receives the same desktop column width as prose.
The old display selector is restricted to direct children of the course, and
nested displays explicitly use automatic width. Mobile blocks keep the full
available text width. Formula contents, fonts, equation grouping and canonical
sources are unchanged. Only the stylesheet cache key advances to
`formula-layout-2`; JavaScript remains at `formula-layout-1`.

On the complete German page at 1600 px viewport width, the first formula's gap
after the preceding paragraph decreases from about 806 px to 16 px. The block
width is 750.14 px, matching the text column. Visible KaTeX base segments are
inside the block, rather than merely having a correctly sized wrapper.

The optional `test/formula-page-layout.browser.cjs` checks complete release pages
for DE/FR/IT at 1600, 1024, 760 and 390 px. It loads the existing release assets
and substitutes only the candidate stylesheet. Checks cover column alignment,
float clearance, visible equation extents and KaTeX errors. All 12 cases pass
with the correction; the original release CSS fails all six desktop cases.
The 65 targeted Python tests and both JavaScript test files also pass.
These are local checks of the complete release files, not verification of a
new deployment. Release trees and canonical data are untouched by this test.

Run from the orchestrator (writes diagnostics only under ignored `tmp/`):

```bash
pushd 50ohm-generator >/dev/null
OHM_TEST_BROWSER="$HOME/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell" \
OHM_TEST_WORKDIR=../tmp/formula-column-check \
node --test test/formula-page-layout.browser.cjs
popd >/dev/null
```

Set `OHM_TEST_BROWSER` to an installed Chromium headless executable; the test
never downloads a browser. Without it the browser tests explicitly skip.
`OHM_TEST_WORKDIR` is required when a browser is supplied. Optional
`OHM_TEST_RELEASE_ROOT` selects another complete release tree;
`OHM_TEST_CSS` selects an alternative stylesheet for a negative control.
Measurements and browser logs remain in the chosen working directory.
The retained investigation is `tmp/formula-column-fix-20261030/`, including
before/after measurements and the successful `regression-v2/` run.
