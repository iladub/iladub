# Loop B1.1 — Merge Resolution (deterministic cosmetics axiom) — Design

**Date:** 2026-07-12
**Status:** Design approved; ready for implementation plan.
**Parent design:** `docs/superpowers/specs/2026-07-10-etkl-inverse-report-grammar-design.md` §5–§7
(Domain B, deterministic cosmetics, pipeline order B → A).

## 1. Goal

Close a **silent-wrong** class in merged-header resolution: a merged header centered over
*part* of the columns is currently extended over columns its ink does not cover — asserted
(score 1.0), SHACL-conforming, never escalated. Loop B1.1 makes merge resolution honor the
**centering convention** it already implicitly relies on, and escalates the residue it cannot
ground rather than guessing.

This is the first deterministic **Domain B** (cosmetics) axiom. It produces a cleaner logical
grid for Domain A (reshape) to consume.

## 2. The gap (confirmed by probe)

`repair_coverage` (`src/iladub/etkl/headers.py`) greedily absorbs each orphan leaf column into
any spatially-adjacent parent, **ignoring the parent label's center position**. `HeaderNode`
carries no geometry (`level, covers, text, parent`), so the center signal that
`_covers_for_cell` reads from ink is dropped before repair runs.

**Evidence.** A merged header `WIDE` centered over columns 1–3 (ink center x≈250) with a
standalone column 4 (its own leaf `D`, no parent):

| Layout (ink center of `WIDE`) | Correct span (by centering) | Actual |
| --- | --- | --- |
| x=300 (true midpoint of cols 1–4) | `[1,2,3,4]` | `[1,2,3,4]` ✅ |
| x=250 (midpoint of cols 1–3 only) | `[1,2,3]`, col 4 standalone | `[1,2,3,4]` ❌ silent-wrong |

Both center positions yield the same span — proving the code cannot distinguish a full-span
merge from a partial one. The discriminator (label center = midpoint of its true span) is
present in the geometry but unused.

**Real-world instance:** a `2023 Actuals` group spanning three columns beside a standalone
`YoY %` column — current code folds `YoY %` under `2023 Actuals`.

## 3. Axiom

> A merged (spanning) header cell's column span is bounded by the **centering convention**:
> its resolved leaf-column range must be centered on the label's ink center, within a
> half-gutter tolerance. A parent absorbs an adjacent orphan column only if the extension
> keeps its span's midpoint aligned with its ink center.

This sharpens the parent design's B1.1 axiom ("a merged cell whose span aligns with the grid
tiling resolves to its logical anchor") with the concrete, geometry-grounded discriminator the
current code omits. Centering (Merge & Center) is the documented reading convention already
assumed by `_covers_for_cell`'s symmetrization; B1.1 applies it **consistently** through the
extension step.

## 4. Oracle (re-tiling + centering)

A resolved header tree is accepted only if:

1. **Tiling (existing):** the resolved spans tile the leaf columns with no gap and no overlap —
   already certified by `tab:CoverageShape` / `tab:NoOverlapShape` / `tab:RefinementShape`.
2. **Centering (new, geometric):** every spanning cell's resolved span is center-consistent
   with its ink — the midpoint of its resolved leaf-column x-range equals the label's ink
   center within a half-gutter tolerance.

Orphan columns that no parent can center-consistently absorb become their own **parentless
leaves** (valid — the `Analyte` stub is precedent). If a residue is genuinely unresolvable
under both checks, the region **escalates `MERGE_AMBIGUOUS`** — asserting nothing rather than
guessing. Honest failure over a fabricated tiling.

The centering tolerance is an **oracle over the centering convention**, not a constant tuned to
a fixture: it is expressed in units of the local gutter width (half a gutter), so it scales
with the grid and does not overfit any single layout.

## 5. Implementation approach (chosen: fix-in-place + oracle safety net)

Merge resolution today is split across `_covers_for_cell` (initial span from ink, with
center-of-mass symmetrization) and `repair_coverage` (greedy orphan absorption). The chosen
approach bounds both by centering, threading the label's ink center to repair time:

- **Thread geometry:** carry the label's ink center (and x-extent) to where extension happens —
  either as a field on `HeaderNode` or via a parallel `{node_index: center_x}` map produced by
  `infer_header_tree`. (Plan picks the least-invasive form; `HeaderNode` gaining an optional
  geometry field is acceptable if it stays backward-compatible.)
- **Bound `repair_coverage`:** a multi-column parent extends into an adjacent orphan **only if**
  the extended span stays centered on the parent's ink (midpoint within a half-gutter of the
  ink center). Orphans failing this stay uncovered at that level.
- **Resolve leftovers honestly:** a leftover orphan that has its own leaf header is a parentless
  leaf (fine). A leftover orphan with no coverage at all → escalate `MERGE_AMBIGUOUS`.
- **Explicit centering oracle:** after resolution, verify each spanning cell is center-consistent;
  a violation escalates rather than asserts (the safety net that guarantees no new silent-wrong).

Rejected alternatives:
- **Explicit `resolve_merges(cells, grid)` refactor** (replace `_covers_for_cell`+`repair_coverage`
  with one geometry-aware step): cleaner separation of Domain B, but a larger refactor than B1.1
  needs now. Deferred — may fall out naturally in B1.2/B1.3.
- **Oracle-only (escalate, never resolve):** smallest change, but escalates Case D instead of
  resolving `[1,2,3]` — lower value; we can resolve it deterministically, so we should.

## 6. Scope boundaries

**In scope:** centering-bounded merge resolution for header-tree spanning cells on the
hierarchical (column-header) path; the new centering oracle; `MERGE_AMBIGUOUS` escalation;
regression + negative fixtures; full existing-suite preservation.

**Out of scope (explicit):**
- The **deferred nameless-pivot-from-PDF** case (blank spanning header, matrix classifier,
  corner-on-own-top-line cross-tab) — its own loop; see
  `docs/superpowers/specs/2026-07-12-nameless-pivot-from-pdf-deferred.md`. B1.1 must not touch
  `is_matrix_candidate` or `infer_column_tree_by_proximity`.
- **B1.2 (text un-wrap)** and **B1.3 (alignment/sizing normalization)** — later B1 slices.
- **Row-header** merge resolution — the mirror can follow, but B1.1 is column-axis only.

## 7. No-regression contract

The following shipped fixtures must remain byte-identical in their recovered header trees
(centered labels whose center = full-span midpoint, so centering-bounded extension preserves
their spans):

- `pivoted_report_pdf` — "Current Visit" / "Prior Visit" over 3 cols each.
- `denormalized_report_pdf` / `region_pivot_pdf` — "Region" over 4 wide cols.
- `crosstab_report_pdf` — via the matrix proximity path (untouched by B1.1).
- `row_grouped_report_pdf`, `multi_table_report_pdf`, transposed, flat record — unaffected.

The plan pins these before any change and re-runs the full suite as the gate.

## 8. Test plan (probe-first)

1. **Regression fixture FIRST** (per the deferred-loop lesson): a partial-merge layout —
   a parent centered over cols 1–3 beside a standalone col 4 — that currently mis-resolves to
   `[1,2,3,4]`. Assert it now resolves to parent `[1,2,3]` + parentless leaf col 4.
2. **Negative (must escalate):** a merge geometry that is genuinely center-ambiguous with an
   uncoverable residue → assert `MERGE_AMBIGUOUS`, nothing asserted.
3. **No-regression:** the §7 fixtures keep their exact recovered trees; full suite green.
4. **Oracle unit test:** the centering check accepts a centered full-span label and rejects an
   off-center over-extension (in gutter-relative units, not a tuned constant).

## 9. Source ownership / conventions

No RDF authored here beyond a possible `MERGE_AMBIGUOUS` escalation reason string reusing the
existing `iladub:CandidateConcept` escalation machinery (subjects owned; no HGA terms as
subjects). No new `tab:` vocabulary is required (recording merge resolution as a recovered-recipe
cosmetic *operation* is deferred to the explicit-`resolve_merges` refactor / later B1 work).
Multilingual literals unaffected. Every axiom ships a worked example that conforms **and** a
negative test that must fail (the `MERGE_AMBIGUOUS` case).
