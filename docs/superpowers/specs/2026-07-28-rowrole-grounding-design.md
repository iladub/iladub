# Grounding the row-role proposal — band-local evidence for the NEURAL slice (Loop C.1)

- **Date:** 2026-07-28
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Follow-on increment to Loop C
  (`2026-07-26-header-row-roles-design.md`, PR #69, merged `1b7ba80`).
- **Origin:** A reader's objection to the shipped loop — *"a single parent with leaves can hardly be
  a hierarchy; why discriminate a parent alone?"* — prompted three measurements (§2). All three
  refuted the objection **as a rule** while confirming the reasoning **as evidence**. This loop
  encodes it as evidence.

---

## 1. Purpose and scope

Loop C decides each non-leaf header row's role (`furniture` | `continuation` | `level`) with a
NEURAL proposer disposed by two SHACL oracles. The proposer currently sees only **row texts, leaf
labels, and per-cell column indices** — it is asked to make a reading judgment nearly blind.

This loop gives it the band-local structural evidence a human reader actually uses, **without
moving the decision out of NEURAL** (§2 shows the decision cannot leave NEURAL) and **without
changing what disposes it**.

**In scope:**

- Three new keys on `rowrole.row_role_context`, all band-local and all exact:
  - `merge_candidates` — per non-leaf cell, the leaf label it would merge into and the resulting
    text under a `continuation` reading.
  - `row_cell_counts` — cells per non-leaf row.
  - `leaf_column_count` — the number of leaf columns.
- `ProposeHeaderRowRoles` takes the three new parameters; the prompt gains two sentences.
- `BamlRowRoleProposer` forwards them.

**Non-goals:**

- **Any change to disposal.** Both oracles, the promotion path, the no-search rule, and every
  refusal path are untouched. This loop changes only what the proposer *sees*.
- **Making the judgment decidable.** It is not (§2). Better-grounded ≠ verifiable.
- **Cross-band evidence** (title-block x-alignment). Deferred — see §6.1.
- **Layout-recurrence / split-table detection.** Deferred — no target in the measured document (§6.2).
- Anything about leaf-grid under-segmentation or row-grouping; those are their own loops.

**Success criteria:**

1. `row_role_context` on the shipped caption/wrap fixture reports `merge_candidates` pairing
   `"Unit"` with `"Ref"` → `"Unit Ref"`, `row_cell_counts` `[2, 1]`, `leaf_column_count` `4`.
2. A cell whose ink center lies outside every column (the shipped `-1` case) yields a **null**
   merge candidate, not a fabricated one.
3. **No behaviour change:** `build_row_reading`, both oracles, every refusal path, and the
   committed graph are byte-identical. The full suite (584 at Loop C close) stays green.
4. The BAML class/function signature and `BamlRowRoleProposer` agree in name, type and arity.
5. **Gate:** no tuned constant; no new numeric literal encoding a decision; the added evidence is
   *reported*, never *acted on* — no Python may branch on it to choose a role.

---

## 2. Measurement — why this is evidence and not a rule (2026-07-28)

The objection was that a level holding one node partitions nothing, so a solitary parent is a
title, not a hierarchy — **unless** the same layout recurs elsewhere, in which case the blocks are
one hierarchical table split at the parent level.

The reasoning is sound. Three measurements against the shipped fixtures show it cannot be applied
as a decision rule, and that no structural feature can.

**Finding 1 — solitary parents are common and genuine.** Level-0 node counts:

| fixture | level-0 nodes |
| --- | --- |
| `pivoted_table_pdf` | 2 — `Current Visit`, `Prior Visit` |
| `crosstab_table_pdf` | 2 — `Q1`, `Q2` |
| `region_pivot_pdf` | **1** — `Region` |
| `partial_merge_report_pdf` | **1** — `WIDE` |
| `unequal_width_merge_report_pdf` | **1** — `GROUP` |

"One node at a level ⇒ title" would demote `Region`, `WIDE` and `GROUP`, which are real merged
headers. Rejected as a rule.

**Finding 2 — coverage does not separate them either.** Each solitary parent covers a *proper
subset*, excluding the stub column, so each does partition (stub vs group):

```
region_pivot_pdf                ncols=5  'Region' covers [1,2,3,4]   covers_ALL=False
partial_merge_report_pdf        ncols=5  'WIDE'   covers [1,2,3]     covers_ALL=False
unequal_width_merge_report_pdf  ncols=4  'GROUP'  covers [1,2,3]     covers_ALL=False
```

GrainCorp's spurious `Date of Grain` level also covers a proper subset (1–12 of 0–13), so a
"covers everything ⇒ vacuous" test fires on neither the fixtures nor the real document.

**Finding 3 — ink span does not separate them, and this is the decisive one.**

```
region_pivot_pdf               'Region'        ink [282.0,318.0]  spans cols 2..3  -> 2 columns
partial_merge_report_pdf       'WIDE'          ink [238.0,262.0]  spans cols 2..2  -> 1 column
unequal_width_merge_report_pdf 'GROUP'         ink [210.0,240.0]  spans cols 2..2  -> 1 column
pivoted_table_pdf              'Current Visit' ink [208.5,286.5]  spans cols 1..3  -> 3 columns
GrainCorp                      'Date of Grain' ink [378.5,412.9]  spans cols 6..6  -> 1 column
```

`WIDE` is a genuine merged parent whose ink fits inside **one** column, sitting directly above a
leaf label in that same column. `Date of Grain` is a wrap fragment with exactly the same geometry.
They are physically indistinguishable. A short "Merge & Center" label and a wrap fragment are the
same shape — the underdetermination Loop B first documented.

**Conclusion.** Tiling (Loop C §2 Finding 5), coverage, and ink span are three independent
structural tests, and **all three fail**. The only discriminator is that *"Date of Grain"* reads as
the start of a longer name and *"WIDE"* does not. That is a language judgment, so the decision is
correctly NEURAL — this is now measured rather than asserted.

**But the proposer is never shown the evidence that would settle it.** It is not told what
`"Date of Grain"` would merge into, nor that a one-cell row sits over a fourteen-column table.
That is the gap this loop closes.

**Finding 4 — the caption's own signal is real but out of band.** The date line's x (398.3) matches
the page title `SHIPPING STEM` (399.0) in the band above, and no column. Strong evidence — and the
reason it reached the header region at all is that `detect_bands` cut one line too high. Using it
requires reading a neighbouring band, which widens `row_role_context` past the closure boundary.
Deferred to §6.1 as a deliberate architectural decision, not an oversight.

---

## 3. Components

### 3.1 `src/iladub/etkl/rowrole.py` — `row_role_context` (extend)

Three keys added. Nothing else in the module changes.

- **`merge_candidates: list[list[dict | None]]`** — parallel to `rows`. For each non-leaf cell,
  either `None` (its ink center lies in no column — the shipped `-1` case) or
  `{"column": int, "leaf_label": str, "merged": str}`, where `merged` is the text
  `build_row_reading` would produce for a `continuation` reading of that cell alone:
  `fragment + " " + leaf_label`.

  This is the signal that separates the indistinguishable pair: `"Date of Grain"` merged with its
  own column's leaf label reads as the start of a plausible column name (a *fragment* — see the
  composition note below for how it becomes the full `"Date of Grain Loading Commencement"`);
  `"WIDE" + "Unit"` → *"WIDE Unit"* is already a complete, plausible column name on its own.

  It reuses the shipped `_column_containing` for placement, so it can never disagree with what
  `build_row_reading` would actually do.

- **`row_cell_counts: list[int]`** — cells per non-leaf row.
- **`leaf_column_count: int`** — number of leaf-row cells.

  Together these carry the solitary-parent reasoning in raw form: *one cell over fourteen leaf
  columns* is a title far more often than a group label.

**Deliberately NOT reported: `_covers_for_cell`'s covers.** `_covers_for_cell` alone reports only
the ink column — for `Date of Grain` that is a single column. It is the DOWNSTREAM
`repair_coverage`/`_centered_run` symmetrized-run extension (`headers.py`), one stage later, that
turned that single ink column into `covers 1–12`. Reporting either would hand the proposer an
artefact that misleads. Cell counts and the leaf-column denominator are exact and underived; the
model can weigh them without being told a fabricated span.

**Multi-row composition note.** `merged` is computed per cell in isolation: for a single
non-leaf cell, it is `fragment + " " + leaf_label` — so GrainCorp's `"Date of Grain"` row, taken
alone, candidates as `"Date of Grain Commencement"`, not the full name. When SEVERAL continuation
rows land in the same column, `build_row_reading` composes them top-to-bottom
(`"Date of Grain" + "Loading" + "Commencement"`), so a single cell's `merged` is only a *fragment*
of that final label. The prompt now says this explicitly (a plain per-cell join could not by
itself explain the worked "Date of Grain" → "...Loading Commencement" example, so the composition
sentence is what makes that example true); the key is named `merge_candidates` (candidates, not
results) for the same reason.

### 3.2 `baml_src/header_rowrole.baml`

`ProposeHeaderRowRoles` gains `merge_candidates`, `row_cell_counts`, `leaf_column_count`. The
`HeaderRowRoleProposal` class is unchanged. Two sentences are added to the prompt:

1. Judge whether the merged text reads as a single column name — if joining the fragment to the
   label below produces a plausible column name, that is strong evidence for `continuation`; if it
   reads as two unrelated things, it is not.
2. A row with a single cell over a table of many columns is more likely a title than a group
   label — **unless** it plausibly groups a subset of the columns beneath it.

The second sentence carries the originating objection, hedged exactly as the measurement requires:
`Region`, `WIDE` and `GROUP` are solitary *and* genuine, so the model must be told the subset
exception, not a bare rule.

### 3.3 `src/iladub/etkl/propose.py` — `BamlRowRoleProposer`

Forwards the three new context keys positionally, matching the BAML signature. `RowRoleProposal`,
the Protocol, and `FakeRowRoleProposer` are unchanged — the seam's shape is untouched.

---

## 4. Testing

- **Context shape:** `row_role_context` on the shipped `caption_and_wrap_band` fixture reports
  `row_cell_counts` `[2, 1]`, `leaf_column_count` `4`, and

  ```python
  merge_candidates == [
      [{"column": 2, "leaf_label": "Qty",  "merged": "Monday Qty"},
       {"column": 3, "leaf_label": "Cost", "merged": "5 May Cost"}],
      [{"column": 1, "leaf_label": "Ref",  "merged": "Unit Ref"}],
  ]
  ```

  This is the fixture stating the loop's whole thesis: `"Unit Ref"` reads as a column name and
  `"Monday Qty"` / `"5 May Cost"` do not, and that contrast is available to the model only if it is
  reported.
- **Out-of-grid cell yields `None`,** not a fabricated merge — the regression guard for the Loop C
  clamp defect, re-asserted at the context layer. Uses the shipped out-of-grid band.
- **Agreement with `build_row_reading`:** for a cell whose `merge_candidates` entry is non-null,
  the reported `merged` is a substring of the label `build_row_reading` produces for that column
  under a `continuation` reading. Pins that the context can never disagree with the rewrite.
- **No behaviour change:** `build_row_reading`, `resolve_header_row_roles`, every refusal path, and
  the committed graph are unchanged. Existing Loop C tests carry this; the full suite stays green.
- **BAML/Python arity agreement:** the class fields and the proposer's read-back agree (the check
  Loop C added after finding `ProposeHeaderSpan` missing from `baml_src/`).

---

## 5. Neurosymbolic gate & discipline

- **Still NEURAL, and now measurably so.** §2 records three failed structural tests. This loop
  improves the proposal's *grounding*, not its *verifiability* — the oracles are untouched and still
  cannot rank two legal readings.
- **Evidence is reported, never acted on.** No Python branches on the new keys to select a role.
  `row_role_context` remains a pure structural read; `build_row_reading` still executes or refuses a
  given vector and never chooses one.
- **No tuned constant, no new numeric literal** encoding a decision. `row_cell_counts` and
  `leaf_column_count` are counts; `merged` is string concatenation.
- **No fabricated evidence.** The symmetrized cover set is deliberately withheld (§3.1) because it
  is derived under an assumption that is false for the very cells in question.
- **Band-local.** No cross-holon read; the band remains the closure boundary.
- **Legality still gates admission, never confidence.** Unchanged.

---

## 6. Open questions / later loops

1. **Cross-band furniture evidence.** The date line's x matches the page title's, not any column
   (§2 Finding 4). Reporting that would require `row_role_context` to read a neighbouring band —
   evidence-positive and therefore gate-legal, but a widening of the closure boundary that should be
   decided deliberately. The stronger version of this fix is upstream anyway: `detect_bands` cut one
   line too high, and excluding title-block furniture at segmentation would remove the problem before
   the header tree sees it. That is a segmentation loop, with a much larger blast radius.
2. **Layout recurrence / split tables.** If two blocks on a page (or across a page break) share a
   leaf layout and each carries a solitary parent, they are plausibly one hierarchical table split at
   the parent level, and that parent *does* discriminate — between blocks. A genuine capability and
   the sound half of the originating objection, but the measured document is a single page with no
   repeated block, so building it now would be speculation. Revisit when a document demands it.
3. **Leaf-grid under-segmentation** — the next loop; the reason GrainCorp scores 0.947 and not 1.0.
4. **Row-grouping with suppressed keys + interleaved subtotals** (`Mackay Total`, `Jul 26 Total`).
5. **Live-path exercise.** The BAML path has still never executed. It is not merely `BAML_LIVE`
   gated off — `BamlRowRoleProposer` is never constructed anywhere in `src/`
   (`compile.py` only accepts an injected `row_role_proposer`), and nothing on the row-role path
   calls `baml_proposer_available()`, so the live path is currently **unreachable from the
   library**, not just env-gated off. This loop adds parameters to a function no test invokes
   live. The arity check in §4 pins agreement between `baml_src/`'s declared signature,
   `propose.py`'s call-site text, and (when `baml_client/` is importable) the GENERATED client's
   actual signature — it catches a source/generated-client mismatch of the kind this branch
   shipped with, but it is still a static check: it cannot substitute for exercising the live
   call, which no test does.
