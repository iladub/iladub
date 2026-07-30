# Row de-fusion + arithmetic subtotal rows (Loop H — residue R4)

- **Date:** 2026-07-30
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Eighth loop of the GrainCorp real-document push
  (A = PR #67; B = PR #68; C = PR #69; C.1 = PR #70; D = PR #71; F = PR #72; G = PR #73).
- **Origin:** Residue **R4** — row-grouping with suppressed keys + interleaved subtotals
  (`Mackay Total`, `Jul 26 Total`). Today every subtotal compiles as an ordinary data record: the
  graph asserts a vessel named `Mackay Total` exists (a §7 violation), and any consumer summing the
  measure column double-counts. Worse, measured in Loop F and re-measured here: whole *data rows*
  are silently **fused** into the record above them.

---

## 1. Purpose and scope

Two halves, one vertical slice:

1. **De-fusion** — `group_wrapped` must never absorb a wrap-continuation **across an author-drawn
   horizontal rule**. The row-axis twin of Loops D/G: the author's rules outrank the derived
   heuristic.
2. **Arithmetic subtotal detection** — a **sparse** row whose numeric measure equals the sum of the
   non-aggregation rows above it (back to the previous confirmed aggregation row of same-or-outer
   level) is a `tab:AggregationRow`, not a data record. Language-independent by construction: a
   `" Total"` suffix test is **expressly forbidden** (English-specific — the tuned constant of
   natural language).

**Non-goals:**

- **The row-group hierarchy** (Month > Port `coversRow` tree from the suppressed-key pattern) —
  its own loop, once subtotals are first-class.
- **Unruled documents**: the hrule veto is inert without hrules; the fusion defect persists there
  exactly as the wrap heuristic allows (documented, not fixed — no measured unruled document
  exhibits the suppressed-key pattern).
- **R16/R3/R17** — untouched.

**Success criteria:**

1. **De-fusion (the red case):** GrainCorp row 4 currently fuses **three source lines** into one
   record (`'56817 56787'`, `'20,000 20,000 20,000'` as single cells). After: **zero fused cells**
   (measured in the spike), and the shipped genuine-wrap behavior is untouched (wrapped header rows
   and wrapped body cells sit in hrule-free gaps — measured: all 19 unseparated line pairs are
   genuine wraps).
2. **Detection:** every arithmetically-confirmable GrainCorp subtotal row is typed
   `tab:AggregationRow` with `tab:aggregates` edges to its member rows — including the two-level
   nesting (`Jul 26 Total` = 118,000 over four *port* groups' data) and blank-membered groups
   (`Fisherman Islands Total` 70,000 = 30,000 + 40,000 + blank).
3. **The honest limit:** `Port Kembla Total` (value `'-'`) is **not** confirmed — a blank total is
   arithmetically unverifiable, and vacuous `0 == 0` confirmation would mark any sparse row over
   blanks. It stays an ordinary row; named residue.
4. **No regression:** full suite green (629 at Loop G close); the borderless fixtures never carry
   hrules; the shipped `subtotals_row_group_pdf` / `totals_table_pdf` fixtures keep their current
   verdicts **unless** detection now types their subtotal rows — which is the desired change and
   must be asserted, not accidental.
5. **Gate:** the hrule veto is a presence test (no constant); detection is **decidable exact
   arithmetic** — the gate's explicitly-permitted PROCEDURAL class — stated and justified in code;
   the membrane keeps the closed-world check (`tab:AggregationRow` requires `tab:aggregates`, per
   the existing `AggregationCellShape` pattern). No language matching anywhere.

---

## 2. Measurement (2026-07-30)

**Finding 1 — the fusion mechanism is the suppressed-key pattern itself.** `group_wrapped` absorbs
line *j* as a wrap-continuation when its columns are a **proper subset** of the anchor's open
columns, it is a partial row, and the gap < `lead`. A suppressed-key data row (no Month/Port cells)
and a subtotal row (label + measure only) are **both** proper-subset partial rows — the
suppressed-key convention *is* the false-absorption trigger. Measured on GrainCorp: grouped row 4
contains **three** source lines (Mackay data + `Mackay Total` + Gladstone data), yielding cells
`'56817 56787'`, `'20,000 20,000 20,000'`.

**Finding 2 — the author draws every row boundary; hrules discriminate perfectly.** Of 54
consecutive line pairs in the band, **35 have an hrule between them** — every genuine row boundary,
including every data/subtotal boundary. The **19 pairs without an hrule are exactly the genuine
wraps**: the wrapped header rows (67.8 → 74.4 → 81.0) and wrapped body cells. The hrule is the
author's row delimiter; `gap < lead` is a heuristic that must not override it. (Double-drawn hrules
exist — 87.0/87.2 — harmless to a veto: any hrule in the gap vetoes.)

**Finding 3 — the veto works end-to-end (spiked).** With absorption vetoed across hrules: **zero
fused cells remain**; **44 clean numeric cells** appear in the measure column including `118,000`,
`140,000`, `147,500`, `158,000`; score/cells unchanged at 0.9496/509 (structural fix, not a score
fix — the pattern of Loops D/F/G).

**Finding 4 — the de-fused sequence, measured (band rows 3–29):**

```
 4  Jul 26  Mackay      …             20,000   17 cells (data)
 5          Mackay Total              20,000    2 cells  = row 4                    ✓
 6..11      Gladstone/Carrington/Geelong data + their totals: 20,000 / 23,000 / 55,000  ✓
12  Jul 26 Total (label in c1!)      118,000    2 cells  = 20+20+23+55k             ✓
13,14       Mackay ×2                 25,000 + 25,000
15          Mackay Total              50,000             = rows 13+14               ✓
16..18      Gladstone ×3              14,000 + 15,000 + 7,500
19          Gladstone Total           36,500                                        ✓
20..22      Fisherman ×3              30,000 + 40,000 + '-' (blank)
23          Fisherman Islands Total   70,000             = 30k + 40k + blank        ✓
26,27       Port Kembla data '-';  Port Kembla Total '-'   ← unverifiable, stays a row
```

**Finding 5 — the level is encoded by the label's column.** Port totals carry their label in the
Port column (c2); the month total in the Month column (c1). The confirmation rule that reconciles
every measured group, including the nesting:

> A sparse candidate with its label in column **L** and numeric value **v** is confirmed iff
> **v = Σ** of the **non-aggregation** rows above it, back to (exclusive) the previous **confirmed**
> aggregation row whose label column **≤ L**.

Verified: row 5 (L=2, back to start) = row 4 ✓; row 12 (L=1, back to start, summing only
non-aggregation rows — the port totals are excluded as already-confirmed aggregations) = 118,000 ✓;
row 15 (L=2, back to row 12 whose label column 1 ≤ 2) = rows 13+14 ✓. Blank measures contribute
nothing to a sum (`tab:Blank` semantics, Loop A).

**Finding 6 — candidates are structural, not linguistic.** Sparse rows have 2 cells; data rows have
15–17. "Sparse" is defined *relative to the row population*, not by a count constant — see §3.2.

---

## 3. Components

### 3.1 `cells.group_wrapped` — the hrule veto

The absorption loop gains one conjunct: never absorb line *j* when any `band.hrules` y lies in
`(tops[j-1], tops[j]]`. Presence test over author-drawn structure; no constant. Inert for bands
without hrules (the borderless fixtures and every unruled document). The docstring gains the
measured justification (Findings 1–2) and the honest limit: unruled suppressed-key documents keep
the fusion defect.

### 3.2 `rows.py` — arithmetic aggregation detection (PROCEDURAL, justified)

Operating on `logical_rows`' output (RowBands with column-tagged cells), per region:

- **Measure column:** the numeric column shared by sparse and dense rows (the existing celltype
  machinery already types cells; the detector considers each numeric column independently and a
  candidate confirms if its value reconciles in that column — GrainCorp has exactly one, the
  `Total` column).
- **Candidate:** a row with exactly two populated cells — one with a numeric token-sum (the
  measure), one without (the label) — and strictly fewer cells than the region's **widest** row.
  **Corrected during implementation:** the design originally said *modal* row shape, but the mode
  is broken on small groups — with two sparse rows against one full row, the mode IS the sparse
  count and the detector goes dead (caught by the Task 2 implementer's tests). The widest row
  defines the normal shape; no count constant either way, and the real gate is the arithmetic,
  not the sparsity prefilter.
- **Confirmation:** Finding 5's rule, applied top-to-bottom so inner groups confirm before outer
  ones consume them. Exact integer arithmetic on normalized numerics (Loop F's repairs feed this).
  Blank cells contribute nothing. A candidate with a non-numeric measure is **never** confirmed
  (the Port Kembla honesty).
- Output: per confirmed row, its member-row indices and the aggregated column.

**Why PROCEDURAL:** the gate's second procedural class is *decidable exact arithmetic*. Ordering +
integer sums over a finite row sequence is exactly that; a SPARQL formulation of nested
running-sum windows would be an obfuscation, not a lift. The **membrane** stays declarative: the
shipped `tab:` shapes pattern (§3.3).

### 3.3 Emission + membrane

`assert_hier_region` (and the row-hier path if reachable) types confirmed rows
`tab:AggregationRow` (already `⊑ tab:LeafRow` in shipped vocab, currently emitted only by
`denormalization.py`) and adds `tab:aggregates` → each member `tab:LeafRow`, plus
`tab:aggregationFunction "sum"`. A new closed-world shape mirrors `AggregationCellShape`:
a `tab:AggregationRow` requires ≥ 1 `tab:aggregates` and an `aggregationFunction` — the membrane
refuses a typed-but-unexplained aggregation.

Downstream honesty: whatever consumes `tab:LeafRow` as *records* must be checked; if the concept
feed reads hierarchical rows, aggregation rows must be excluded from record minting (measured
during planning; included if it is small, else named residue).

---

## 4. Testing

- **De-fusion red (committed, synthetic):** a ruled fixture with suppressed keys + an interleaved
  subtotal line and hrules between all body rows — currently fuses (assert the fused cell text as
  the red), then de-fuses. Genuine-wrap guard: a two-line wrapped body cell in an hrule-free gap
  still absorbs.
- **Detection units:** single-level group; two-level nesting (label-column levels); blank member
  contributes nothing; blank-total candidate NOT confirmed; a sparse row whose value does NOT
  reconcile is NOT confirmed (a lookup row is not a subtotal); no language matching (a subtotal
  labeled in another language confirms identically — the label text is never read).
- **Membrane:** an `AggregationRow` without operands fails the new shape.
- **End-to-end:** the de-fusion fixture compiles with its subtotal typed `tab:AggregationRow`,
  member edges present, and the subtotal row not minted as a data record (if the feed is in scope).
- **Shipped-fixture delta, asserted not accidental:** `subtotals_row_group_pdf` / `totals_table_pdf`
  — whatever changes must be pinned as the desired change.
- **Real-world (local, uncommitted):** GrainCorp — zero fused cells; every confirmable subtotal
  (per Finding 4) typed with correct members; `Port Kembla Total` remains an ordinary row;
  suite green.

---

## 5. Neurosymbolic gate & discipline

- **No language matching, ever.** `" Total"` is English; the detector never reads label text.
  Structure (sparsity, label column) + arithmetic only.
- **The hrule veto is a presence test** over author structure — the row-axis twin of Loops D/G.
- **Detection is PROCEDURAL by the gate's own carve-out** (decidable exact arithmetic), stated in
  code; the closed-world check is SHACL (the membrane), keeping the open/closed split.
- **Honest failure:** unverifiable candidates (blank totals) stay ordinary rows; unruled documents
  keep the fusion defect, named. Credibility over completeness.
- **No overfitting:** fixtures are authored from the measured *shapes* (suppressed keys, nesting,
  blank member, blank total), not GrainCorp bytes; GrainCorp is confirmation.

---

## 6. Residues

- **R4** — closed for ruled documents by this loop (de-fusion + first-class subtotals). Open
  narrower forms: **blank-total subtotals** (unverifiable, stay rows — Port Kembla); **unruled
  suppressed-key documents** (fusion persists without hrules).
- The row-group *hierarchy* (Month > Port `coversRow` tree) — future loop, now unblocked.
- The register at `docs/superpowers/residues.md` is canonical and is updated by this loop.
