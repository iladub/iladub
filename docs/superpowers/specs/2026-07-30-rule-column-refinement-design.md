# Refining coarse rules with interior gutters (Loop G — residue R13)

**LANDED — salvaged onto `main` 2026-08-17 from the parked `iladub-rule-column-refinement` branch.** Shipped as `9427137`, `1425d90`, `4ddfdc3`: `geometry.refine_rule_columns` (`geometry.py:194`), wired at `compile.py:155`. R13 is recorded closed in `residues-closed.md`. **`main` has since gone past this design** — an interior gutter is now only a *candidate*, confirmed by the `confirm-boundary.rq` AXIOM. Read as the design record, not as a description of current behaviour.

- **Date:** 2026-07-30
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Sixth loop of the GrainCorp real-document push
  (A = PR #67; B = PR #68; C = PR #69; C.1 = PR #70; D = PR #71; F = PR #72).
- **Origin:** Residue **R13**, opened by Loop D's own final review — *rules coarser than the columns
  are accepted and merge real columns*. Loop F then measured that **R1 ≡ R13**: GrainCorp's measure
  column holds `Date Loading Completed | Commodity | Total` with **no interior rule**, and this is
  what blocks residue R4.

---

## 1. Purpose and scope

Loop D made the author's vertical rules authoritative for the leaf grid. That was right, but it
treated them as **complete**. They are not: an author may rule some boundaries and leave others to
whitespace. Where that happens, three real columns are compiled as one, at confidence 1.0, with no
escalation.

This loop keeps rules authoritative and stops treating them as complete: inside each rule interval,
a persistent blank run **with ink on both sides** is an additional column boundary.

**In scope:**

- `geometry.refine_rule_columns(chars, rule_xs) -> list[float]` — the interior-gutter rule.
- `compile.py` — call it once per ruled band; feed the result to `rule_aware_lines` **and** store it
  on the band.
- `bands.Band` — a new derived field `column_xs`. `rules` remains **what the author drew**;
  `column_xs` is **what was derived** from rules + ink. Keeping them distinct is the point: Loop D's
  review rejected synthesising fake `Rule` objects for exactly this reason.
- `grid._rule_boundaries` — prefer `column_xs` when present.

**Non-goals:**

- **Residue R4 (subtotals).** This removes one of its two blockers by giving it a clean numeric
  `Total` column. It still needs the row de-fusion — `logical_rows` absorbs each subtotal line into
  the preceding data row (measured in Loop F).
- **The unruled path (R16)** and **the nested-subset vote (R3)** — untouched.

**Success criteria:**

1. GrainCorp's grid goes 15 → **17** columns; `Date Loading Completed`, `Commodity` and `Total`
   appear as **three separate labels** (was the single label `Date Loading CompletedCommodityTotal`).
   17 is the real header's column count.
2. **The score MOVES, upward, and by a measured amount:** `447 → 509` cells, `0.947 → 0.9496`.
   Unlike Loops D and F this loop *should* change the score, because the merged blob now yields three
   cells per row instead of one. A different number is a failure signal, in either direction.
3. **No over-splitting:** `ruled_tight_table_pdf` and `ruled_merged_table_pdf` each gain **zero**
   extra boundaries (measured, §2 Finding 3). Borderless fixtures never enter this path.
4. **No regression:** the full suite (609 at Loop F close) stays green.
5. `Band.rules` still contains only author-drawn rules; no synthesised `Rule` is ever constructed.

---

## 2. Measurement (2026-07-30)

**Finding 1 — the internal structure is invisible today.** `rule_aware_lines` emits **one `Word` per
rule column**, so everything downstream sees a single span:

```
line 4: [('(blank)Chickpeas 20,000', 720.9, 827.4)]
line 5: [('20,000', 811.6, 827.5)]
```

The 22–27 pt gaps inside that span reach neither the gutter profile nor `_rule_boundaries`. Only
**char-level** ink reveals them, which is why the refinement cannot live in `_rule_boundaries` alone
(it has no chars).

**Finding 2 — the gutters are unambiguous.** Char-level occupancy across the 54 inked rows of the
interval `[715.2, 829.92]`, at the shipped `gutter_pct = 0.98` / `min_gutter_bins = 3`:

```
x 744.2 .. 763.2   (19 bins blank)
x 789.2 .. 808.2   (19 bins blank)
```

Nineteen points wide — not marginal. Splitting at their centres (753.7, 798.7) gives three columns.

**Finding 3 — the naive rule over-splits badly; the interior condition is what saves it.**
Accepting *any* qualifying blank run adds a boundary to nearly every interval of the shipped
fixtures:

| fixture | naive rule | with the interior condition |
| --- | --- | --- |
| `ruled_tight_table_pdf` | **+5** (one per interval — 5 columns would become 10) | **0** |
| `ruled_merged_table_pdf` | **+2** | **0** |
| GrainCorp measure column | +2 | **+2** (753.7, 798.7 — the two wanted) |

The naive rule's "gutters" sit at each cell's *trailing* edge (e.g. interval `[58, 120]` → run at
107.5–120), where short left-aligned text leaves blank space with **no ink to its right**. That is
padding, not a separator. Requiring ink on **both** sides inside the interval rejects every one of
them and keeps both real ones — the same shape as Loop D's "an interval no word occupies is not a
column".

**Finding 4 — outcome, spiked end-to-end.** With the refinement, GrainCorp yields **17** header
labels, all correct:

```
GC Fin Year · Month · Port · Unique Slot Reference Number · Exporter · Name Of Ship ·
Date ETA of Ship · Date of Grain Loading Commencement · Date ETD of Ship ·
Date Nomination Received · Time Nomination Received · Date Nomination Accepted ·
Time Nomination Accepted · Status · Date Loading Completed · Commodity · Total
```

`cells = 509` (was 447), `score = 0.9496` (was 0.947).

---

## 3. Components

### 3.1 `geometry.refine_rule_columns(chars, rule_xs) -> list[float]` (new)

For each consecutive pair in `rule_xs`, take the **non-space** chars whose centre falls inside, build
the per-x-bin blank profile over the rows that have ink there, and emit the centre of every blank run
that is at least `min_gutter_bins` wide, at least `gutter_pct` blank, **and has ink on both sides
within the interval**. Returns the original boundaries plus the accepted centres, sorted.

The interior condition is the load-bearing half (§2 Finding 3) and is threshold-free.

### 3.2 `bands.Band` — new field `column_xs: tuple[float, ...] = ()`

Derived column boundaries. `rules` keeps its meaning — the marks the author actually drew — so
provenance stays honest and `column_xs` can be recomputed or discarded without pretending the
document said something it did not.

### 3.3 `compile.py` — one call, two consumers

In the ruled branch, replace the bare `xs` with `refine_rule_columns(band_chars, xs)`, pass the
refined list to `rule_aware_lines`, and set `column_xs` on the constructed `Band`. `sub_rules` is
passed through unchanged.

### 3.4 `grid._rule_boundaries` — prefer the derived boundaries

Where it currently reads `xs = sorted({round(r.x, 2) for r in band.rules})`, use `band.column_xs`
when non-empty, falling back to `band.rules` otherwise. Everything after — the word-tiling
acceptance, the unoccupied-interval collapse, and the interior-boundary requirement, all shipped by
Loop D — is unchanged and still applies.

---

## 4. Testing

Synthetic and domain-neutral, from the shapes measured in §2:

- **An interior gutter splits:** a ruled interval whose rows carry ink on both sides of a persistent
  blank run → the run's centre is added.
- **Trailing padding does NOT split** (the Finding 3 case): short left-aligned text leaving blank
  space at the interval's right edge → no boundary added. This is the test that would have caught
  the naive rule.
- **Leading padding does NOT split** — the mirror case.
- **A blank run present in only some rows does NOT split** — it must be persistent.
- **`Band.rules` is never synthesised:** after compiling a ruled fixture, every `Rule` on the band
  corresponds to an author-drawn x.
- **Regression:** `ruled_tight_table_pdf` and `ruled_merged_table_pdf` keep their column counts
  (measured: zero extra boundaries); borderless fixtures unaffected; full suite green.
- **Real-world (local, uncommitted):** 15 → 17 columns; the three labels separate; `cells == 509`,
  `score == 0.9496`. No PDF committed.

---

## 5. Neurosymbolic gate & discipline

- **PROCEDURAL, justified.** Reading ink occupancy and testing which x-ranges are blank is raw
  extraction plus decidable containment. It decides *where columns are*, not what anything means.
- **The new condition is threshold-free.** "Ink on both sides within the interval" is a presence
  test.
- **Inherited constants, stated rather than claimed away.** This path reuses `infer_leaf_grid`'s
  existing `gutter_pct = 0.98` and `min_gutter_bins = 3`. They are **pre-existing tuned constants**
  with documented tuning guidance; this loop inherits them rather than inventing new ones, and does
  **not** claim to be constant-free. If the gate is ever tightened against them, this call site is
  one of the places to revisit.
- **Rules stay the author's.** No synthesised `Rule` objects — the Loop D review rejected that, and
  the separate `column_xs` field exists to honour it.
- **Additive, never contradicting.** Refinement only *adds* boundaries inside an interval; it never
  removes or moves a rule the author drew.
- **No overfitting.** Fixtures are authored from the shape (interior gutter; trailing padding), not
  from GrainCorp bytes. GrainCorp is confirmation.

---

## 6. Residues

- **R13** — closed by this loop for the *ruled* path with interior evidence. It remains open in one
  narrower form: an interval whose sub-columns are separated by **neither** a rule **nor** a
  persistent gutter (e.g. a single-row table) is still merged. No measured document exhibits it.
- **R4** — one of its two blockers removed (a clean numeric `Total` column). Still blocked on the row
  de-fusion: `logical_rows` absorbs each subtotal line into the preceding data row.
- **R1** — closed with R13; it was the same defect.
- **R3, R16** — untouched.
