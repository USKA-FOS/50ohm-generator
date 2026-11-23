# Formula experiment withdrawal

Decision: 23 November 2026. Branch: `design/object-centric-canonical`.

The formula presentation experiment and its detector are removed from the
branch intended for integration with main. The complete original prototype
remains on **`fix/formula-presentation` at `fa6ca9f`**, locally and on origin.
The branch is not moved and history is not rewritten.

## Scope and recovery

The withdrawal reverses commits `9301006`, `3618738` and `fa6ca9f`:
contextual formula classification, connector grouping, punctuation promotion,
browser rendering, experimental CSS, configuration, inventory/preview tooling,
associated tests and the experimental specification. Answer-label spacing
introduced in that same patch also returns to main's behavior.

The subsequent affected-Markdown inventory is removed from the merge branch.
Its English version remains recoverable from `6de5569` and the pre-withdrawal
checkpoint `c9d2e9d`; it is not part of the original `fa6ca9f` prototype.
The local recovery tag `before-formula-withdrawal-2026-11-23` identifies the
complete pre-withdrawal merge-branch state.

## Resulting behavior

Formula parsing, the course stylesheet and browser integration return to main's
pre-experiment behavior, including its existing inline sans-serif CSS.
Standalone expressions retain the legacy display treatment; connectors and
punctuation no longer trigger the experimental contextual transformations.
This is a restoration, not a new typography policy or a claim that all earlier
rendering problems have been solved.

Unrelated language/resources, release controls, answer shuffling, quotation
conversion, unit macros, Python configuration and main synchronization remain.
Asset query strings change to `formula-withdrawal-20261123` so future generated
pages request the restored CSS and JavaScript. No canonical content is edited;
no site/PDF build or deployment is performed by this withdrawal.

## Future work

Keep these stages distinct:

1. Detect and report questionable source structures without changing rendering.
2. Review and approve source corrections, preserving the author's intended layout.
3. Agree on typography and rendering requirements before implementation.

The archived detector can be recovered later; it is not shipped in this merge
branch. Source correction and rendering changes require separate decisions.

## Verification

The complete Python suite reports **83 passed, 8 failed, 3 skipped**. All eight
failures are the unchanged caption-test failures listed in
[tools and tests](BRANCH_TOOLS_AND_TESTS.en.md). The five remaining JavaScript
checks pass. Unrelated protected files are compared with their pre-withdrawal
hashes. Local diagnostic evidence is under the orchestrator's ignored
`tmp/formula-withdrawal-20261123/` directory.
