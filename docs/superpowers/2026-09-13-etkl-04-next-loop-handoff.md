# Handoff — etkl:04: the grid reading exists because the bands are broken

**Serves:** prog:criterion:etkl:04 — `gov-stats/ons-index-of-services-2026-02.pdf`
(`tests/arc-manifest.ttl:265`).

**Date:** 2026-09-13. **Branch this was written on:** `etkl-04-the-ons-document` (PR #217).

**Doc impact: none.** A handoff ships no term, no behaviour, no released assertion.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is graded.
This handoff was authored **under** the originating floor, but the grading is kept because the rule
is about the reader's needs, not the author's budget: a reader must be able to tell a mechanical
next step from a prediction that can fail.

---

## 5. The next concrete action

### 5a. ASSERTED: the loop opens with a maintainer's ruling on R225's fork. The option space is exact.

R225 measured a coupling that makes "fix the obvious defect" the wrong move, and the choice between
the two remedies is a values question about what a reading may claim — not something a further
measurement settles. Both arms are costed; neither needs more evidence first.

- **Arm A — widen the fallback gate.** Let a page carry BOTH a band reading and a grid reading, with
  one adjudicated against the other. Costs: a second reading per page needs a disposal rule, and
  `dec:supersedes` already models exactly this kind of judgement. Buys: band repair stops costing
  the grid, so R225 becomes fixable on its own terms.
- **Arm B — add a resolution test to the re-bucketing, then re-derive the gate.** `xs` must resolve
  more finely than the band's own word structure — `datagrid.py:346`'s ordinal comparison, applied
  at `compile.py:133`. Costs: the gate must be re-derived in the same change, or ONS silently loses
  552 cells (measured: 0.9720 → 0.5407). Buys: the narrower change, and it fixes the misreading at
  source rather than tolerating it.

**The oracle either arm must pass is the corpus pair**, and it is already measured on both sides:
ons must not lose its grid (571 cells today), and bfs p5 must not regress from its adopted 404.

**Why asserted:** the options are enumerated, each one's corpus effect is measured, and the decision
is about which claim the reader is allowed to make.

### 5b. ASSERTED: R224 is repairable WITHOUT that ruling, and is the mechanical half.

R224's two defects are bookkeeping inside the branch and do not touch band construction: capture
`emit_data_grid`'s returned URI at `compile.py:1359`, and take the branch's `band_marks` snapshot
before `:1362` adds its ink. The spec's § 4 invariants (I1, I2, I3) and § 5 falsifications stand
as written and were not disturbed by § 8. Doing this first is safe under either arm of 5a.

**Why asserted:** the defects are measured, the repair sites are exact, and no corpus score moves
because totals are preserved.

### 5c. PROPOSED, and it must be RUN before anything is built on it: does D1's repair restore stitching?

**The prediction:** capturing the grid URI makes ONS's two grids eligible for `tab:continuesTable`,
because `document.py:1554` stitches only regions whose `table_uri is not None`, and `continuesTable`
is currently 0 on a nine-page release whose two tables are consecutive halves of one series.

**Why it may fail:** stitching also requires the continuation AXIOM to RECOGNIZE the pair, and
nothing here has measured whether it does. `table_uri` may be necessary and not sufficient. The
check costs one compile, and it belongs before any claim that D1's repair "reconnects the series."

### 5d. What this hands over exposed

[[R224]] and [[R225]] are both **open** and untouched by code. [[R202]] is answered on its first
half and open on its second (the pair-by-identity helper). [[R43]] is amended and half dead.
[[R213]]'s ruling is recorded but **not implemented** — the three-way term (absent ink / nil marker
/ hidden ink) is still undesigned. etkl:04's route steps 1 and 2 (contract/terms/shapes, then the
grounding leg) are untouched and remain a loop of their own.

---

## 1. Where the primaries are

- **The spec** — `docs/superpowers/specs/2026-09-13-the-fallback-that-names-no-table-design.md`.
  Read § 8 first: it is appended after § 0-7 and it is where the causal story changed.
- **The rows** — [[R224]] and [[R225]] in `residues-open.md`. Read the full rows; R225's closure
  column carries the fork 5a asks a ruling on.
- **The instruments — NOT COMMITTED, and a loop acting on these figures must commit its own.**
  Every probe in this loop was a scratch script over `compile_tables` / `compile_document` /
  `page_bands` / `_build_ruled_band`. The spike was applied and reverted each time; `src/` is clean.
- **The suites that own the affected paths** — `test_border_grid.py`, `test_boundary_cuts_ink.py`,
  `test_rule_column_refinement.py`, `test_read_band_books_every_word.py` (31 passed under the spike,
  so they will NOT catch a regression of this class).

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| R224: two defects in the fallback branch, measured, no score moves | R224's row; spec § 2 |
| R225: border-only re-bucketing fuses rows; 41 of 41 bands lose columns | R225's row; spec § 8 |
| The obvious guard is REFUTED — the grid reading exists because the bands are broken | R225's row; spec § 8 |
| The remedy is document-dependent and needs a ruling, not a patch | R225's closure column; § 5a above |
| R213: option (c), an invisible glyph is a typed absence or proposition | R213's row (ruling only, not implemented) |
| R202's two unpaired regions are the fallback's appended region | R202's row, amended |
| R43's 0.4419 and its tiling failure are stale; its UNSUPPORTED/asserted oddity survives | R43's row, amended |

## 3. Unverified or assumed

- **5c, entirely** — see its grading.
- **bfs p5's adopted 404-cell reading is sampled, not verified.** 14 of 404 cells were inspected and
  read cleanly. Nobody has checked the whole table, its header, or whether the row addressing is
  right. "Clean when sampled" is the claim the row makes; "correct" is not.
- **A third arm to R225 may exist.** Two were costed. Nobody looked for a remedy that repairs band
  construction *and* keeps the grid without touching the gate.
- **R225's link to [[R44]] (bfs) is NOT causal.** 8 border-only bands sit on that document; no one
  has shown they cause any of R44's three escalation reasons.
- **An unbooked-ink figure of 75.9% was computed with `extract_words` as the denominator** and is
  NOT comparable to `unbooked_ink_census`'s band-ink measure. It appears in no row and must not be
  quoted forward.

## 4. What this loop did

Measured etkl:04's blocker to the line, raised [[R224]] and [[R225]], wrote the spec (+ § 8 after the
remedy was refuted), amended [[R43]], [[R202]] and [[R213]] (the maintainer's ruling), and re-pinned
`test_residue_graph`'s candidate count 92 → 91 with its measurement. **No production code** — the
remedy was spiked and refuted, and a refuted remedy is a row, not a commit. PR #217.

**A method note worth carrying, because it cost most of the loop.** Nine successive causes for
ONS's behaviour were proposed and retracted (unspaced glyphs → ink-based runs → two extractors →
pre-band fusion → …), and the bfs verdict flipped three times (win → collapse → undetermined → real
gain). Each retraction is recorded in the rows rather than overwritten. The specific trap: **page
scope (`compile_tables`) and document scope (`compile_document`) are different quantities** — bfs p5
LOSES at one and GAINS at the other, and comparing them produced two of the three flips.
