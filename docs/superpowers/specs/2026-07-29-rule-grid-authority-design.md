# Rules as leaf-grid authority (Loop D)

- **Date:** 2026-07-29
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Fourth loop of the GrainCorp real-document push
  (A = header/body split PR #67; B = header→column reconciliation PR #68; C = header-region row
  roles PR #69; C.1 = grounding the row-role proposal PR #70).
- **Origin:** The named residue from Loop C — GrainCorp's recovered grid has 14 columns where the
  source has 15, collapsing `Month`+`Port` into column 1 and
  `Date Loading Completed`+`Commodity`+`Total` into column 13.

---

## 1. Purpose and scope

Make the **author's own vertical rules** the authority for the leaf-column grid when they exist and
the words confirm them, instead of silently discarding them and inferring gutters. This recovers
the `Month`/`Port` column split from structure the author drew, and restores a border-awareness
capability that has been dead on arrival since it shipped.

**In scope:**

- `grid._rule_boundaries` — after the existing word-tiling acceptance, drop any boundary bounding
  an interval **no word occupies** (threshold-free; collapses double-drawn rules).
- `cells.recover_leaf_grid` — carry `band.rules` / `band.hrules` into every sub-band it constructs,
  and return immediately when a suffix yields rule boundaries (authority, no vote).
- A **residue register** at `docs/superpowers/residues.md` (§6) — the accumulated deferred items
  from Loops A–D in one tracked place, each with where it was measured and what would close it.

**Non-goals (deliberately, each a named residue in §6):**

- **Column 13.** The author drew no rule there and there is no gutter;
  `'CompletedCommodityTotal'` (x 716.3–818.4) is a single extracted blob, as is the body's
  `'(blank)Chickpeas   2 0,000'`. Not recoverable from rules or whitespace — it needs
  character-level evidence, the same class as the known split-number defect (`2 0,000` → `20,000`).
- **The nested-subset vote** in `recover_leaf_grid` (§2 Finding 3). Real, measured, and it will
  resurface for *ruleless* tables — but repairing it changes grid derivation for every table in the
  suite, which is a materially larger risk than this loop should carry.
- Anything about row-grouping or interleaved subtotals.

**Success criteria:**

1. GrainCorp's grid goes from 14 to **15** columns, and the recovered header labels contain
   `Month` and `Port` as **separate** labels (was the single label `Month Port`).
2. The four double-drawn hairline boundaries are collapsed: the rule path yields 15 columns, not 19.
3. **The score does NOT move.** It stays at **0.947** with **447** cells — splitting a column
   changes no token counts. This is a structural-correctness loop, not a score loop; a changed
   score would mean something unintended happened.
4. **No regression:** every ruled fixture keeps its column count through the rule path
   (`ruled_tight_table_pdf` 5, `ruled_merged_table_pdf` 5 — measured), every borderless fixture is
   untouched (`rules == 0` → the rule path is never entered), and the full suite (592 at Loop C.1
   close) stays green.
5. **Gate:** no tuned constant and no new numeric literal. The empty-interval collapse is a
   *presence* test, not a tolerance.
6. The residue register exists, and every deferred item named in Loops A–D appears in it.

---

## 2. Measurement (2026-07-29)

**Finding 1 — the author ruled the `Month|Port` split, and the code discards it.**
Band 2 carries 20 distinct rule x-positions. One of them, **92.7**, sits inside the recovered
column 1 (54.3–159.3) and genuinely separates the two: `Month` ink ends at 75.4, `Port` ink begins
at 93.8.

`infer_leaf_grid` *does* prefer rule boundaries (`grid.py:80`, `_rule_boundaries`). But
`recover_leaf_grid` (`cells.py:56`) rebuilds each candidate sub-band as

```python
Band(tuple(sub), min(l.top for l in sub), max(l.bottom for l in sub))
```

with **no `rules` argument**. Every sub-band it tests is ruleless, so `_rule_boundaries` returns
`None` and the rule path never executes for any multi-line band. The border-aware grid capability
is effectively dead wherever `recover_leaf_grid` is the entry point.

**Finding 2 — the rules are also vetoed by one word, and the veto is furniture.**
On the *full* band, `_rule_boundaries` rejects the rules because exactly **one word of 472**
straddles them: `'Friday, 24 J'` (x 398.3–427.0) — the caption line Loop C classifies as
`furniture`. This is self-healing once Finding 1 is fixed: `recover_leaf_grid` already iterates
row-suffixes to skip unstable top rows, and every suffix from line 1 onward accepts the rules.

**Finding 3 — the mode is independently wrong, and this is what actually produced the 14.**
Column counts across the 54 suffixes, with today's shipped (ruleless) code:

| ncols | suffixes | longest |
| --- | --- | --- |
| 2 | 1 | 2 rows |
| 3 | 1 | 3 rows |
| 4 | 1 | 4 rows |
| **14** | **35** | 49 rows |
| **15** | 16 | **55 rows** |

The correct 15-column grid — including the `Month|Port` split at 91.8 — **is already found by the
longest suffix, the whole band**. The mode discards it: as `start` increases the narrow gutter at
91.8 washes out, and 35 progressively-degraded views outvote the 16 strongest.

The suffixes are **nested subsets of one another**, not independent witnesses, so a mode over them
systematically over-weights the tail. `recover_leaf_grid`'s own docstring already recognises that
more rows means stronger gutter evidence — it applies that only as a tiebreaker *within* the
winning count, never to the vote itself.

*This corrects an earlier reading of this residue.* The dropped rules (Finding 1) and the vote
(Finding 3) are **independent** defects that each produce a wrong grid. This loop fixes Finding 1
and defers Finding 3 (§6), because the fix for Finding 3 touches every table in the suite.

**Finding 4 — the rule boundaries need collapsing, and it can be done without a tolerance.**
The 20 rule x-positions include double-drawn rules (14.64/15.60, 92.64/92.76,
829.92/830.16/830.88), which would yield 19 columns, four of them hairlines. A dedup *tolerance*
would be a new tuned constant — a §8 gate violation. It is unnecessary: measured per rule-to-rule
interval on the suffix that skips the caption,

```
[  14.64,   15.60]  width  0.96  words  0   <-- empty
[  15.60,   58.20]  width 42.60  words  4
[  58.20,   92.64]  width 34.44  words  7
[  92.64,   92.76]  width  0.12  words  0   <-- empty
[  92.76,  159.00]  width 66.24  words 47
        … 11 further intervals, 32–53 words each …
[ 715.20,  829.92]  width 114.72 words 53
[ 829.92,  830.16]  width  0.24  words  0   <-- empty
[ 830.16,  830.88]  width  0.72  words  0   <-- empty
```

Exactly the four hairlines are empty; every real column holds 4–53 words. There is no borderline
case, so **"an interval no word occupies is not a column"** is a presence test, not a threshold.
Collapsing on it yields **15 columns**.

**Finding 5 — blast radius, measured not assumed.** Old vs new column counts:

| fixture | rules | old | new |
| --- | --- | --- | --- |
| `ruled_tight_table_pdf` | 6 | 5 | 5 |
| `ruled_merged_table_pdf` | 6 | 5 | 5 |
| `borderless_tight_table_pdf` | 0 | 5 | 5 |
| `borderless_merged_table_pdf` | 0 | 5 | 5 |
| `simple_table_pdf` | 0 | 3 | 3 |
| `pivoted_table_pdf` | 0 | 7 | 7 |
| `crosstab_table_pdf` | 0 | 7 | 7 |

Ruled fixtures reach the same count through the rule path; borderless fixtures never enter it.

**Finding 6 — the outcome, spiked end-to-end.** With both changes, GrainCorp's recovered header
labels become 15, with `Month` and `Port` separate:

```
GC Fin Year | Month | Port | Unique Slot Reference Number | Exporter | Name Of Ship |
Date ETA of Ship | Date of Grain Loading Commencement | Date ETD of Ship |
Date Nomination Received | Time Nomination Received | Date Nomination Accepted |
Time Nomination Accepted | Status | Date Loading CompletedCommodityTotal
```

`score = 0.947`, `cells = 447` — **both unchanged**, as expected.

---

## 3. Components

### 3.1 `src/iladub/etkl/grid.py` — `_rule_boundaries` (extend)

After the existing word-tiling acceptance, collapse boundaries bounding an unoccupied interval:
a boundary `xs[i+1]` is kept only if some word's ink overlaps `[xs[i], xs[i+1])`. `xs[0]` is always
kept. Return `None` if fewer than two boundaries survive (fall through to the whitespace path).

Threshold-free and evidence-positive: a column exists only where ink occupies it. The docstring
must record *why* this is not a dedup tolerance — a future maintainer will be tempted to "simplify"
it into `abs(a - b) < eps`, which would reintroduce the gate violation this design avoids.

### 3.2 `src/iladub/etkl/cells.py` — `recover_leaf_grid` (fix + short-circuit)

- Construct each sub-band **with** the band's rules and hrules.
- Before the modal vote, if a sub-band yields rule boundaries, return that grid immediately with
  full confidence. The author's structure is authority; no vote is needed or wanted.
- The modal vote is otherwise **unchanged** — it remains the path for ruleless tables, carrying its
  known defect (§2 Finding 3), which is documented in place rather than silently inherited.

### 3.3 `docs/superpowers/residues.md` (new)

A single register of every deferred item from Loops A–D, each row carrying: what it is, where it
was measured, why it was deferred, and what would close it. Loops have been accumulating residues
across four specs and the SDD ledger; a register makes them one tracked list instead of archaeology.
Future loops append to it, and closing a residue means deleting its row in the loop that closes it.

---

## 4. Testing

- **Empty-interval collapse (unit):** a synthetic band whose rules include a double-drawn pair
  (two rules a fraction of a point apart) yields boundaries with that pair collapsed, and the
  surviving count equals the number of occupied intervals.
- **Rules become authority (unit):** a synthetic *ruled* band whose gutter inference would give a
  coarser grid than the rules returns the rule-derived grid, at full confidence.
- **The straddling-furniture veto self-heals (unit):** a ruled band whose *first* line carries a
  word straddling a rule still returns the rule-derived grid, because a later suffix accepts —
  the GrainCorp caption shape, synthetically.
- **Ruleless path untouched (regression):** a band with no rules returns exactly what it returns
  today (the modal-vote grid), asserted against the shipped fixtures' counts.
- **No fixture regression:** the counts in §2 Finding 5 hold; full suite green.
- **Real-world confirmation (local, uncommitted):** GrainCorp grid 14 → 15; `Month` and `Port`
  appear as separate labels; `score == 0.947` and `cells == 447` **unchanged**; column 13 still
  reads `Date Loading CompletedCommodityTotal`, recorded verbatim as the residue.

All fixtures synthetic and domain-neutral. **No third-party PDF committed.**

---

## 5. Neurosymbolic gate & discipline

- **PROCEDURAL, and justified as such.** Reading vertical rules out of a PDF and testing which
  intervals contain ink is raw extraction plus decidable containment — irreducibly procedural, and
  carrying no reading judgment. It decides *where the author drew lines*, not *what anything means*.
- **No tuned constant, no tolerance, no new numeric literal.** The collapse is a presence test
  (§2 Finding 4). The existing `COORD_EPS = 0.01` is a float-comparison epsilon and is deliberately
  **not** repurposed as a dedup width — the duplicates are 0.12–1.0 pt apart, so using it as a
  distance threshold would be exactly the tuned constant the gate forbids.
- **Recover the author's structure; do not re-derive it (§0).** Rules outrank inferred gutters
  because the author drew them. This loop restores that ordering rather than inventing a new one.
- **Honest failure preserved.** If the words do not tile the rules, `_rule_boundaries` still
  returns `None` and the whitespace path runs — the rules are never forced.
- **No overfitting.** Every fixture is synthetic and authored from the *shape* of the problem
  (double-drawn rule; straddling first-line word). GrainCorp is confirmation, not a target, and its
  unchanged 0.947 is reported as such rather than dressed up as an improvement.

---

## 6. Residues — the register this loop starts

`docs/superpowers/residues.md` is created with the following as its initial content. **The register
is canonical from then on** — this table is a snapshot for review, and later loops append to and
delete from the register, not from this spec.

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |
| R1 | **Column 13 blob** — `Date Loading Completed\|Commodity\|Total` merged | No rule drawn; no gutter; `'CompletedCommodityTotal'` x 716.3–818.4 is one cell | Not recoverable from rules or whitespace | Character-level re-segmentation; same mechanism as R2 |
| R2 | **Split-number cells** — `2 0,000` should be `20,000` | Loop B; visible in GrainCorp body rows | Data-side extraction, separate from structure | Intra-blob character spacing evidence |
| R3 | **Nested-subset vote** in `recover_leaf_grid` | §2 Finding 3: 35 degraded suffixes outvote 16 stronger | Changes grid derivation for every table | A statistic that respects nesting, plus a fixture battery |
| R4 | **Row-grouping + interleaved subtotals** — `Mackay Total`, `Jul 26 Total` | Loop B/C | Own loop | First-class row-group structure |
| R5 | **Proposal inputs not recorded** in `emit_row_role_promotion` | Loop C.1 final review | Not a regression; best done with a live run | Record the context the proposer saw |
| R6 | **Centre-only candidate** for wide parents | Loop C.1 final review | Pre-existing in shape; needs a live run to judge | Report all covered columns' candidates |
| R7 | **Live BAML path unreachable** — `BamlRowRoleProposer` never constructed in `src/` | Loop C.1 final review | No live run yet attempted | Wire it behind `baml_proposer_available()` |
| R8 | **`ProposeHeaderSpan` missing** from `baml_src/` | Loop C; B1.3's live path cannot run | Pre-existing, unrelated to the loops since | Author the function |
| R9 | **Conservation shape unreachable** through the row-role driver | Loop C final review | Sound as a backstop; covered by its own test | A reading that genuinely loses text, or accept as backstop |
| R10 | **`detect_bands` cuts one line too high** — the caption lands in the table band | Loop C.1 §2 Finding 4: date x 398.3 ≈ title x 399.0, matching no column | Segmentation has a large blast radius | Title-block exclusion at segmentation |
| R11 | **Mixed header rows** cannot be expressed per-row | Loop C §3.2 | No document exhibits one | Per-cell roles, when evidence demands |
| R12 | **Split-table recurrence** — solitary parent + repeated layout | Loop C.1 §6.2; stem.pdf is 1 page | No target document | Cross-block layout matching |

---

## 7. Open questions / later loops

1. **R3 is the one most likely to bite next.** It is dormant only because this loop routes ruled
   documents around it; the first ruleless document with a narrow gutter will hit it.
2. **R1 + R2 are one loop, not two** — both need character-level evidence inside an extracted blob.
3. Loop E (R4) is the next planned slice.
