# Deterministic HTML formula presentation

Status: approved approach, normal-generator integration; no site release rebuilt.
Recovery baseline: generator `c5900b0` (clean and published before this work).

## Problem and scope

A standalone equation used to remain inline merely because punctuation followed
it or a connector separated two expressions. On `NE_spitze_effektiv_wert`, this
produced three different presentations of the U_eff/Û relationship and the
325 V and 651 V calculations. Broad CSS overrides mixed arbitrary sans fonts
with KaTeX's own fonts, sizes and glyph metrics.

The change belongs only to the normal HTML generator. Canonical math bodies,
the meaning of indices, translations, PDF tools and published releases are not
rewritten. Slides retain their previous paragraph classification and font profile.
Classification is presentational, not mathematical validation or syntax repair.

## Deterministic classification

`renderer/formula_layout.py` scans supported math delimiters, escaped dollars
and balanced groups. Existing bare-formula block tokens retain block status.
Additional rules apply to complete rendered paragraphs, not arbitrary lines.

| Paragraph content | Treatment |
|---|---|
| One expression | Display block |
| One expression plus one terminal punctuation mark | Display block; punctuation remains outside the math body |
| Expressions separated only by configured connectors | Display group; connectors remain text |
| Existing consecutive explicit display expressions | Separate display rows |
| A sentence containing expressions | Inline |
| Question or answer field | Keep its own inline/explicit-display layout |
| Unrecognized separators, mixed markup or unbalanced delimiters | Preserve; record for inspection |

Connectors and terminal punctuation are configured in `config/formula-layout.json`
by language. No language or semantic inference is performed. Body order and
characters are preserved; no typographical decision about an index is made.

## Generator and CSS integration

- `renderer/fifty_ohm_html_renderer.py` emits `formula-block`/`formula-item`
  wrappers for confidently classified display paragraphs.
- `templates/html/page.html` opts the normal page into the contextual profile
  with `data-formula-presentation="contextual"` and loads `formula-inline.js`
  before `latex.js`. The script is copied by the normal asset build.
- `assets/latex.js` consumes native display expressions first; a second pass
  handles inline expressions and ignores previously generated `.katex` trees.
- `assets/formula-inline.js` selects supported native KaTeX sans fonts for Latin
  variable atoms and upright text/units, while preserving explicit specialised
  fonts, metadata, quantity arguments and unknown command arguments.
- `assets/style-course.css` sizes inline math relative to local text, leaves
  display math serif, and removes blanket font-family substitutions on glyphs.
  Blocks use the entire content width, with non-shrinking equation items and no
  internal breaks at relation signs. Genuinely oversized equations scroll
  horizontally instead of being cut. Separate display rows remain separate.
- Answer labels contain a nonbreaking space after A:/B:/C:/D:.

The bundled KaTeX is **0.13.11**, not the version shown by current online docs.
The inline-only `\mathsfit` compatibility macro uses supported `\textsf`/`\textit`
stacking. Variable atoms are grouped so unbraced accents and subscripts keep
correct arguments. Greek/special glyphs may retain native fallback fonts;
identical Inter rendering is not promised. Native mathematical metrics take
priority over forcing an arbitrary family on internal glyph spans.

## Inventory: HTML text nodes, not parser callbacks

`tools/audit_formula_layout.py scan` reads release HTML without modifying it.
It inventories complete paragraphs, question/answer fields and raw display
nodes, deduplicates samples and records all page/line references and source hashes.
HTML entity/data callbacks are coalesced into the browser's actual text node.
Script/style/noscript/pre/code/textarea/option contents are excluded from math
analysis. Visible code in a mixed paragraph is preserved in its preview but
excluded from classification. Real markup boundaries still separate text nodes;
genuine unclosed expressions remain flagged. Extraction policy and excluded
node counts are recorded in the manifest.

The initial 174 unbalanced-delimiter flags were detector false positives:
30 distinct script fragments and 144 entity-split fragments. None justified
inserting math delimiters into canonical. They are absent from the corrected
report. Parse failures of isolated diagnostic fragments must not be presented
as confirmed source errors.

## Current validation artifacts

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

## Commands

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

## Verification

Regression coverage includes named/numeric HTML entities, ignored code, mixed
code/prose, real markup splits and real unclosed delimiters, frozen Before
assets, escaped dollars, punctuation/connector/body preservation, multiline
paragraphs and slide opt-out. JavaScript checks exercise the bundled KaTeX,
variable/unit styles and separation of display and inline passes. Integration
checks must also exercise the real page template/asset loader in DE/FR/IT.
No complete website or PDF build is needed for these checks.

References: [display mode](https://katex.org/docs/options.html),
[font commands](https://katex.org/docs/supported.html#font),
[auto-render](https://katex.org/docs/autorender.html).
