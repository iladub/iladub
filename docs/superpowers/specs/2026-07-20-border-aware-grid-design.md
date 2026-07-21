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

## Extension (2026-07-21): rule-aware CELL extraction — the actual fix

**Empirical finding that redirected the slice.** Rule-derived *boundaries* (steps 1–3 above) turned
out **insufficient** for tight/ruled tables, and the failure mode is instructive: when a gutter is
`< ~3pt` (exactly the tight case ruling exists to disambiguate), **pdfplumber merges the adjacent cell
texts into one word** during `extract_words` — *before* any grid logic runs (`"ProductRevenueExpense…"`,
or a wide value fusing with the next column: `"adj5.5"`). That merged blob then straddles the rule
boundaries → the step-3 word-tiling oracle **rejects** → whitespace fallback. So the very merging that
breaks whitespace also defeats the boundary oracle: **boundaries alone cannot recover data the word
extractor already fused.**

**The actual fix — re-extract cells by the rules.** For a ruled band, do not trust pdfplumber's
proximity word-grouping; instead **assign the page *characters* to rule columns** and reconstruct each
cell's text. Verified working: grouping `page.chars` by row and by rule-column (char center within
`[rule_i, rule_{i+1}]`) correctly splits the tight table into its true cells
(`['Product','Revenue','Expense','Margin','Growth']`, `['Alpha','123456','98765','24691','12.3%']`)
where `extract_words` produced one merged blob. This is still **PROCEDURAL raw extraction** — chars and
their positions are author-encoded; assignment-by-containment is decidable geometry, no tuned constant.

**Pipeline addition:**
5. **`geometry.extract_chars(pdf_path, page) -> list[Char]`** — raw per-character bboxes (PROCEDURAL,
   like `extract_words`).
6. **`geometry.rule_aware_lines(chars_in_band, rules) -> tuple[Line, ...]`** — group the band's chars
   into rows (top proximity, as `text_lines` does) and, within each row, into cells by rule-column;
   each cell becomes one `Word` at its char-span bbox. Deterministic containment assignment.
7. **`compile_tables`:** for a band with rules, **rebuild its lines** via `rule_aware_lines` (from the
   page chars in the band's y-extent) before classify. The rule-split words now tile the rules, so the
   step-3 rule grid is accepted and `classify` sees the true columns.

Steps 1–3 remain the foundation (rules extracted, attached, and the exact boundaries); step 7 is what
makes the words *match* those boundaries. Borderless bands (no rules) skip re-extraction entirely →
`extract_words` output unchanged → the additive guarantee holds.

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

- A **ruled tight-column fixture where pdfplumber merges the cell texts** (columns tight enough that
  `extract_words` fuses adjacent cells into one blob) compiles as a `RECORD_TABLE` with the **5 true
  columns and correctly-split cell text** — via rule-aware char re-extraction (step 7). Without it,
  the merged blob mis-captures the table. This is the genuine data-capture win.
- A **direct check** on that fixture: `extract_words` yields a merged blob spanning multiple columns
  (the failure), while `rule_aware_lines` yields the correct per-cell words (the fix); and the
  rule-derived boundaries equal the true column x-positions.
- A **borderless twin** (same words, no rules) is unchanged — `extract_rules == []`, no re-extraction,
  `extract_words`/`infer_leaf_grid` byte-identical to today.
- **Every existing test green** via `./.venv/bin/python -m pytest` (baseline 422 passed / 5 skipped
  after Tasks 1–3); the borderless-fixtures-no-rules guard (Task 4) proves the additive guarantee at
  scale.
- **Gate (§8):** `extract_rules`, `extract_chars`, `rule_aware_lines`, and the rule→boundary mapping
  are PROCEDURAL (raw extraction + decidable containment geometry, no tuned constant); the boundary
  accept/reject is the threshold-free word-tiling oracle. The whitespace `infer_leaf_grid` (with its
  `0.98`, still the Family-C perception fallback for unruled tables) is unchanged and out of scope.

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
