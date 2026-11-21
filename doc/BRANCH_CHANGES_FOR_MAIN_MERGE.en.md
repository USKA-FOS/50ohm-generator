# Generator changes: motivation and implementing commits

Snapshot: **21 November 2026**.

| Item | Reference |
| --- | --- |
| Repository | `USKA-FOS/50ohm-generator` |
| Branch | `design/object-centric-canonical` |
| Examined commit | `69bec73413877bc5f3e931db102f2c0457d1614b` |
| Comparison branch | `origin/main` |
| Main commit | `b5d5ea6e0b4f1b54b22bf74f9faa54a4f7b51938` |

This register describes the generator's functional and runtime changes relative
to main, the reasons for them, and their implementing commits. Where a feature
was corrected later, the follow-up commits are listed with the initial change.

## 1. Language resources and localized output

### External language resources and template overrides

**Change.** Load `labels.json` and templates from `generator_extra_content`.
Template lookup order is the selected language, default German resources, then
the generator's templates. Replace embedded German interface text with resource
lookups in pages, figures, tables, margin boxes, navigation, solutions and slides.
Externalize homepages and auxiliary pages.

**Motivation.** Generate German, French and Italian sites with one engine while
maintaining and translating interface text separately from generator code.

**Commits.** `359b5c7` introduces the multilingual loading infrastructure;
`2b3d868` completes externalization, removes German text fallbacks and propagates
labels to snippet and solution rendering.

**Implementation.** `src/config.py`, `src/build.py`,
`renderer/fifty_ohm_html_renderer.py`, HTML and slide templates.

**Integration requirement.** Build inputs must supply the expected language
resources. Technical template stubs cannot substitute for their content.
Language detection currently recognizes `de`, `fr` and `it`, defaulting to German.

### Localized titles for the three course editions

**Change.** Select German, French or Italian course titles for A, NE and NEA
when calling `build_unified_edition`.

**Motivation.** Display course titles in the publication language while retaining
the three Swiss editions and their existing structure.

**Commits.** `359b5c7`; `69bec73` preserves localized titles when integrating
the updated HB3/HB9 class-map interface from main.

**Implementation.** `build.py`.

### Localized legal-basis margin-box heading

**Change.** Obtain the heading of `<law>` boxes from `margin_law_label`.

**Motivation.** The German heading “Gesetzliche Grundlagen” remained visible on
French and Italian pages even when the box contents had been translated.

**Commit.** `563b902`.

**Implementation.** `templates/html/page.html`.

## 2. Question-data compatibility

### Recognition of explicitly removed questions

**Change.** Recognize a question listed in `pruned` even when it is absent from
both the current and comparison catalogs. Tolerate missing display metadata
for that case.

**Motivation.** Render references to removed questions with their rationale,
distinguishing them from references to questions that cannot be found.

**Commit.** `359b5c7`.

**Implementation.** `src/build.py`.

### Support for optional and list-valued rationale

**Change.** Accept absent, null, string or list values for `HB.rationale`.
Join nonempty list items with `; ` for presentation.

**Motivation.** Consume migrated question metadata without crashing on an absent
field or displaying a raw Python list.

**Commits.** `e366905`; `69bec73` retains this normalization when resolving the
rationale-handling change from main.

**Implementation.** `src/build.py`.

### Optional comparison catalog

**Change.** Accept both an omitted and an explicitly null `questions_upstream`
setting, using the existing optional configuration lookup.

**Motivation.** Build successfully when a separate comparison catalog is not
provided. The builder can use the regular catalog as its comparison baseline.

**Commit.** `69bec73`, completing integration of main's optional-catalog fix.

**Implementation.** `src/config.py`.

## 3. Build behavior and runtime

### Deterministic build-time answer shuffling

**Change.** Add `--seed`, seed configuration and a dedicated random generator
owned by the builder.

**Motivation.** Make review builds reproducible so answer-order changes do not
obscure actual content changes in comparisons.

**Commit.** `d19021d`.

**Implementation.** `build.py`, `src/config.py`, `src/build.py`.
The seed controls build-time shuffling, including slide answers.

### Explicit input configuration

**Change.** Require a configured input path instead of silently falling back to
an implicit `content` directory.

**Motivation.** Report incomplete configuration immediately rather than build
from an unintended location or fail later with a less useful error.

**Commit.** `0d029e0`.

**Implementation.** `src/config.py`.

### Python 3.14 environment

**Change.** Set Python 3.14 in `.python-version`, the project requirement and
Docker image, and update the dependency lockfile.

**Motivation.** Align reproducible local and container execution with the runtime
selected for the project.

**Commit.** `0f6787a`.

**Implementation.** `.python-version`, `pyproject.toml`, `uv.lock`,
`docker/Dockerfile`.

## 4. Release presentation and browser behavior

### Release identity, BETA indicator and feedback context

**Change.** Add the `release_id`, `beta` and `feedback_url` settings, boolean
validation, and conditional inclusion of release fragments in pages and slides.

**Motivation.** Identify the published release, distinguish beta versions and
associate feedback with the relevant release, language and page.

**Commits.** `1009f32`; presentation integration follows in `bcfe2ed`,
`913b3d7` and `2cfe32d`.

**Implementation.** Configuration, builder globals and page/slide inclusion points.
Release-specific elements are inactive without `release_id`.

### Language switching that preserves the current location

**Change.** Add DE/FR/IT header controls and preserve the deployment prefix,
page filename, query and anchor when switching language. Restore scroll position
in the same tab when browser storage is available.

**Motivation.** Let readers and reviewers compare languages without returning
to the homepage or searching again for their current passage.

**Commits.** `bcfe2ed`; presentation refinements in `913b3d7`.

**Implementation.** `assets/language-switch.js`, `templates/html/page.html`.
The same filename must exist in the language trees. Scroll restoration uses
pixels; without browser storage the language link still works.

### Header and footer layout for release controls

**Change.** Fit language controls and the BETA indicator into the existing
header, adjust responsive styling, position the release/feedback footer block
and refine generator-status panel visibility.

**Motivation.** Add release information without unnecessary header height,
overlapping controls or a broken mobile layout.

**Commits.** `bcfe2ed`, `913b3d7`, `2cfe32d`.

**Implementation.** `assets/style-fiftyohm.css`, `templates/html/page.html`,
`templates/html/generator_status.html`.

### Optional generator-status widget

**Change.** Add `generator_status` to control inclusion of the status widget
and its requests. Its default remains `true` unless configured otherwise.

**Motivation.** Allow static releases to operate independently of a live
build-status service.

**Commit.** `487465a`.

**Implementation.** `src/config.py`, `templates/html/page.html`.

### Explicit opt-in for legacy review controls

**Change.** Add `review_workflow`, disabled by default, to gate chapter/section
reservation widgets, GitHub editing, difference controls and `diff.html`.

**Motivation.** These controls appeared on learner-facing releases and linked
to the review workflow. Their inclusion must be an explicit publication choice.

**Commit.** `19af725`.

**Implementation.** Configuration, builder and chapter/section templates.
Ordinary feedback remains available.

### Configurable browser-side answer shuffling

**Change.** Add `shuffle_answers`, disabled by default for review. Write the
setting into the generated script without rewriting the source asset. Move
complete answer elements while preserving their behavior.

**Motivation.** Support stable-order review and shuffled training publications
without manually commenting JavaScript or maintaining separate engines.

**Commit.** `c5900b0`.

**Implementation.** `src/config.py`, `src/build.py`, `assets/script.js`.
This option is independent of the build-time seed.

## 5. Rendering corrections

### Additional unit macros

**Change.** Add KaTeX macros for `\minute` and `\farad`.

**Motivation.** Render valid unit expressions used by the question and course
inputs rather than showing unresolved commands.

**Commit.** `19af725`.

**Implementation.** `assets/latex.js`.

### Unicode nonbreaking spaces around ellipses

**Change.** Accept U+00A0 nonbreaking spaces and U+202F narrow nonbreaking spaces
around `...` in HTML and LaTeX rendering.

**Motivation.** Preserve translated punctuation spacing and prevent rendering
errors when those characters occur in the input.

**Commit.** `825686d`.

**Implementation.** `renderer/fifty_ohm_html_renderer.py` and
`renderer/fifty_ohm_latex_renderer.py`.

### Contextual presentation of inline and standalone formulas

**Change.** Classify complete paragraphs as inline expressions, standalone
formulas, punctuated formulas or groups joined by configured connectors.
Use mathematical sans-serif presentation inline and serif presentation for
standalone equations. Preserve variable shape distinctions, provide the intended
line width and prevent automatic breaking at relation signs. Add nonbreaking
spacing after answer prefixes A:/B:/C:/D:.

**Motivation.** Comparable equations on `NE_spitze_effektiv_wert.html` had
inconsistent layouts, while formulas within prose could introduce conspicuous
font and size changes. Correct presentation without rewriting formula content.

**Commit.** `3618738`.

**Implementation.** `renderer/formula_layout.py`, `config/formula-layout.json`,
HTML renderer, `assets/formula-inline.js`, `assets/latex.js`, page template
and course stylesheet.

**Integration requirement.** Retain the follow-up fix `fa6ca9f` below. Ambiguous
constructions are preserved; classification does not infer a subscript's meaning.
Slides retain their existing rendering profile.

### Formula layout beside floated figures

**Change.** Give formula blocks the text-column width and prevent CSS from
reapplying that width to nested KaTeX elements. Center equations in their column
and allow horizontal scrolling when necessary.

**Motivation.** The first formula correction could create large blank areas
beside floated illustrations and clip equations on complete course pages.

**Commit.** `fa6ca9f`, completing `3618738`.

**Implementation.** `assets/style-course.css`, stylesheet cache reference in
`templates/html/page.html`.

### TeX quotation-command boundaries

**Change.** Recognize `\glqq Text\grqq{}` and `\glqq{}Text\grqq{}` while
preserving incomplete or improperly delimited commands.

**Motivation.** AF305 exposed raw quotation commands. Recognition needed to
handle the agreed explicit source delimiters correctly.

**Commits.** `3cea91e` initially broadened recognition; `01c6ebc` withdrew
acceptance of an opening command without a delimiter. The latter is required
when retaining the former.

**Implementation.** `convert_latex.py`.

### Swiss publication quotation marks

**Change.** Render quotations from TeX commands and Markdown tokens as **«…»**.

**Motivation.** Follow the agreed Swiss quotation convention consistently across
the website's rendering paths.

**Commit.** `d9dcae2`, completing the preceding quotation changes.

**Implementation.** `convert_latex.py`,
`renderer/fifty_ohm_html_renderer.py`. Source wording and commands are retained.

## 6. Functional resolutions retained during main synchronization

The synchronization commits `e593970` and `69bec73` incorporated main's changes
while preserving the branch behavior described above. The 21 November merge
retains these specific integration decisions:

| Resolution | Motivation | Commit |
| --- | --- | --- |
| Combine localized edition titles with main's new class-map argument | Preserve translated course titles while accepting the updated builder interface | `69bec73` |
| Retain list/string rationale normalization | Preserve compatibility with migrated question metadata | `69bec73` |
| Keep disabled-chapter labels still used by the course index | Avoid losing the explanation attached to disabled chapters | `69bec73` |
| Accept an omitted or null comparison-catalog setting | Make the optional input work in both configuration forms | `69bec73` |
| Keep the generator homepage stub and apply incoming German homepage changes to its external template | Preserve the separation between runtime content and generator code | `69bec73` |

The corresponding homepage-resource update is recorded in
`50ohm-contents-ch` commit `f0d163bd2`.
