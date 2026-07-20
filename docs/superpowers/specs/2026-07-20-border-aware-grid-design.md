# Border-Aware Column Boundaries — recover the author's ruled column structure

**Date:** 2026-07-20
**Status:** Design — approved (brainstorm 2026-07-20).
**Scope:** the first real-PDF-robustness slice. When a table is **ruled**, extract the vertical
separator lines and use them as the leaf-column boundaries — recovering the author's explicit column
structure instead of guessing it from whitespace. Fixes real table-data mis-capture on tight/ruled
tables; purely additive (borderless tables unchanged).

## The problem (measured on a realistic fixture, 2026-07-20)

A report with a **ruled table and tight columns** (~2pt gutters) mis-captures its data. On the probe
`r_tight` (5 true columns, ruled): `infer_leaf_grid` (whitespace profile, tuned `gutter_pct=0.98`)
returns **ncols=4** with merged/wrong boundaries `[60, 157.5, 212.5, 267.5, 302]` — the tight gutters
never clear the `0.98` threshold. The header `Product Q1 Q2 Q3 Q4` (5 words) then mismatches the
4-column grid → misclassified, cells mis-assigned, table data not cleanly captured. Real human-made
reports routinely rule their columns and pack them tightly, so this is a genuine data-capture blocker
(not a cosmetic score issue).

## The key fact — the border encodes the truth exactly

pdfplumber already exposes the ruled lines the compiler ignores. On `r_tight`, `page.lines` yields
**vertical rules at x = [58, 120, 175, 230, 285, 342]** — precisely the 6 column separators (5 columns
between them). The author *explicitly drew* the column boundaries. §0 of this project: *recover the
author's structure* — the rules ARE the structure.

## The move (§8 classification)

For a **ruled** table, "where are the columns" stops being a NEURAL/tuned-`0.98` *perception* problem
(the audit's Family-C fragility, `infer_leaf_grid` A1) and becomes **PROCEDURAL raw extraction**: read
the vertical rules the author drew. Raw extraction of author-encoded structure is exactly PROCEDURAL
(like `extract_words`); mapping rule x-positions → boundaries is decidable geometry with **no tuned
constant**. This *removes* the `0.98` constant for ruled tables (a §8 win), and the rule-derived grid
is accepted only when the words **strictly tile** it (a threshold-free oracle), so a stray line can
never corrupt a good grid.

## The pipeline

1. **Extract vertical ruled lines** — new `geometry.extract_rules(pdf_path, page) -> list[Rule]`,
   a `Rule(x, top, bottom)` per near-vertical segment (`page.lines` + `page.edges`, `|x0-x1| <
   COORD_EPS`). PROCEDURAL, alongside `extract_words`. (Horizontal rules are extracted-but-unused
   this slice — a future header/row-split signal.)
2. **Attach rules to bands** — `Band` gains `rules: tuple[Rule, ...] = ()` (defaulted → every existing
   `Band(lines, top, bottom)` construction and fixture is unchanged). In `compile_tables`, after
   `detect_bands`, attach to each band the vertical rules whose y-extent overlaps the band's
   `[top, bottom]`.
3. **Rule-derived grid, word-tiling disposed** — in `infer_leaf_grid`: if `band.rules` is non-empty,
   build candidate boundaries from the sorted unique rule x-positions (bounded to the band's ink
   extent), and **accept** them iff every band word falls **strictly within** a rule-column
   (`_word_in_column` / strict containment — the threshold-free oracle). On accept, return that
   `LeafGrid` (confidence 1.0 — the boundaries are explicit, not sampled). On reject (words straddle
   the rules → they aren't clean column separators) or no rules, **fall back to the existing
   whitespace path, unchanged**.
4. **Everything unruled is untouched** — no rules attached → the current `infer_leaf_grid` runs
   verbatim. This is the regression guarantee.

## Why sound / anti-overfit

- **Purely additive.** Every shipped fixture is a borderless synthetic reportlab PDF → no rules → the
  whitespace path runs byte-identically → all existing tests stay green. This is the primary
  regression guard.
- **Removes a tuned constant** (`0.98`) for ruled tables rather than adding one.
- **Conservative oracle.** Rule boundaries are used only when the words strictly tile them; a stray
  vertical line (not a column separator) makes the words straddle → automatic fallback. No trust
  without confirmation.
- **First implementation step (anti-overfit):** before wiring into classify, verify empirically that
  (a) `extract_rules` + the tiling validation recover the **5 true columns** on `r_tight`, and
  (b) every shipped fixture's `infer_leaf_grid` output is **byte-identical** (no rules → unchanged).
  If any borderless fixture's grid changes, the rule path is leaking — fix that first.

## Definition of done (closes on the real blocker)

- A **ruled tight-column fixture** (the `r_tight` layout, drawn with reportlab `canvas.line`
  separators) compiles as a `RECORD_TABLE` with the **5 rule-derived columns**, its data captured
  (the table scores ~1.0) — where the whitespace path gave 4 columns and mis-captured it.
- A **direct check** that the rule-derived boundaries equal the true column x-positions, and that a
  borderless version of the same table still uses the whitespace path (rules absent).
- **Every existing test green** via `./.venv/bin/python -m pytest` (baseline 415 passed / 5 skipped);
  a targeted assertion that a representative borderless fixture's `infer_leaf_grid` is byte-identical
  before/after (the additive guarantee).
- **Gate (§8):** `extract_rules` and the rule→boundary mapping are PROCEDURAL (raw extraction + exact
  geometry, no tuned constant); the accept/reject is the threshold-free word-tiling oracle. The
  whitespace `infer_leaf_grid` (with its `0.98`, still the Family-C perception fallback for unruled
  tables) is unchanged and out of scope.

## File structure (for the plan)

- **Modify** `src/iladub/etkl/geometry.py` — add `Rule` dataclass + `extract_rules(pdf_path, page)`.
- **Modify** `src/iladub/etkl/bands.py` — `Band` gains `rules: tuple[Rule, ...] = ()`.
- **Modify** `src/iladub/etkl/grid.py` — `infer_leaf_grid`: rule-derived boundaries + word-tiling
  disposition, whitespace fallback (existing path untouched when no rules).
- **Modify** `src/iladub/etkl/compile.py` — extract page rules; attach band-overlapping rules to each
  band after `detect_bands`.
- **Create/extend** `tests/etkl/fixtures.py` — a `ruled_tight_table_pdf` reportlab fixture (tight
  columns + `canvas.line` vertical separators) and its borderless twin.
- **Create** `tests/etkl/test_border_grid.py` — rule extraction, rule-boundaries-recover-true-columns,
  word-tiling accept/reject, byte-identical borderless-fixture guard, end-to-end compile of the ruled
  fixture.

## Scope boundary (YAGNI)

- **Vertical rules → column boundaries only.** Horizontal rules (header/row separation), rectangles,
  and cell-level borders are out of scope (extracted-but-unused, noted for a follow-up).
- **No change to the whitespace `infer_leaf_grid`** for unruled tables — its `0.98`/Family-C
  perception problem is a separate (still-open) slice; this one sidesteps it for ruled tables only.
- **Partial / inconsistent rules** (only some columns ruled) → the word-tiling oracle rejects → whitespace
  fallback. A reconciliation (merge rules + whitespace) is a future refinement, not this slice.
- Scanned/image PDFs (no vector rules; would need OCR/line-detection) are out of scope.
