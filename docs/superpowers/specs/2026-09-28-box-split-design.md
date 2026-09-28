# Spec — a band that holds two drawn tables is two tables: split at closed ruled boxes

**Serves:** prog:criterion:etkl:03 — cbh is not accepted while `#table9` fuses two side-by-side
tables; this loop also declares the carriage criterion `prog:criterion:tab:12` (§ 5) that can see it.

**Date:** 2026-09-28. **Branch:** `box-split`, cut from `main` at `6eb80ca`.

**Doc impact: none.** No published term changes; the split is compiler behaviour, and the new
criterion lives in `tests/arc-manifest.ttl` (internal).

**Provenance of the design.** § 1–4 below were presented section by section and approved by the
maintainer in chat on 2026-09-28, with one ruling each (§ 0). The defect is recorded in
`docs/superpowers/2026-09-28-cbh-one-is-not-a-compile.md` (PR #282); the design start point in
`docs/superpowers/2026-09-28-cbh-box-split-design-handoff.md` (PR #283). Every load-bearing
measurement is in § 7 with its command; probe scripts (gitignored, local only) are in
`internal/benchmarks/cbh-boxes-2026-09-28/` — `boxes.py`, `gaps.py`, `closed2.py`, `seam.py`.
**Written at 32,236 working tokens, under the originating floor.**

---

## 0. The rulings this spec obeys (2026-09-28, maintainer, in chat)

| # | Ruling |
|---|---|
| R-a | **Approach 1:** segment a band at the author's closed ruled boxes *before* `segment`/classification. Rejected: scoping `_rule_boundaries` by rule y-extent (one 9-column table, gutter absorbed); tuning the gutter splitter. |
| R-b | **The totals family is deferred** to its own loop (roster port totals `#ignored`; `1,951,264` is their sum). |
| R-c | **Touch is AXIOM:** two rules touch when their gap ≤ the thinner rule's stroke width. **Zero-width rules touch only exactly**, and are out of scope. |
| R-d | **Trigger:** a band is split only when it contains **≥ 2 closed boxes**. |
| R-e | **Declare `tab:12`**, a carriage criterion authored `met false`, with the corpus oracle under a strict xfail. |

## 1. The goal

cbh page 0, raw band 9 (y 683.5–761.5, 10 lines) compiles to what the author drew:

- **T1 — "Stock at Port (Main Storage Area) as at 29/07/2026":** a `RecordTable`, 7 columns,
  boxhead `PORT | WHEAT | MAIN WHEAT GRADES | BARLEY | CANOLA | OTHER | TOTAL`, 4 body rows
  `ALB, ESP, GER, KWI`.
- **T2 — "PORT MAINTENANCE SHUTDOWN DATES - 2026":** a `RecordTable`, 2 columns × 4 rows, **no
  boxhead** (the page draws none).
- Each title-bar text is carried as a `tab:RegionCaption` of its own table.
- The Note block is not a cell of either table.

## 2. Reading the boxes (design § 1)

**2.1 Rule reader — PROCEDURAL (raw extraction).** A new reader beside `geometry.extract_rules`,
used only by the split. A rule is one of: a **black-filled** rect that is not square, **each edge**
of a stroked rect, or a stroked line — each at its **painted** extent (stroke width included).
`extract_rules` is not used here because it takes every edge of every rect, fills included (§ 7.4).
A miss by this reader fails *safe*: no box forms and the band compiles exactly as today. The risk
is only commission (a box that is not there), which § 5's controls bound.

**2.2 Touch — AXIOM (R-c).** A horizontal and a vertical rule touch when both their x-gap and
y-gap are ≤ `min(thickness_h, thickness_v)`. A zero-thickness rule therefore touches only at gap
0. No constant enters: the bound is read off the two marks, and across the corpus the largest
positive-width near-miss gap is 0.01pt against a thinnest stroke of 0.385pt (§ 7.1), so any bound
in that interval gives the same boxes.

**2.3 Closed box — PROCEDURAL (exact interval arithmetic).** A box is a connected component of the
touch graph with ≥ 2 horizontals, ≥ 2 verticals, and a **closed outer frame**: each side of the
component's bounding box is covered by the union of its rules' painted extents — perpendicular
rules included, since a vertical's ink inks the corner — with no uncovered gap larger than the
component's thinnest stroke. Its cells are the gaps between its rules. Corpus: 10 closed (cbh 6,
graincorp 4), 3 open (bfs p5 ×2, p6 ×1) — the frame condition refuses exactly bfs's header-only
lattices (§ 7.2).

**2.4 Title bar.** A filled rect whose fill is **not black**, whose bottom touches the box's top
rule (§ 2.2), and whose x-extent lies between the box's outer verticals. The words inside it are
that box's title. Only cbh has title bars (§ 7.2 handoff census).

## 3. Where the split plugs in (design § 2)

**3.1 Site.** `compile.page_bands`, in the per-raw-band loop, **before**
`cut_trailing_notes(segment(band))`. Closed boxes are computed once per page.

**3.2 Decision — AXIOM.** "This band holds ≥ 2 tables" is a SPARQL `SELECT` over a per-band
evidence graph of its closed boxes (a box belongs to the band when every word inside it is a word
of the band), counting within the band — the holon-scoped close, as `band-run.rq` +
`merge_run_candidates` do. The Python around it only builds the graph and applies the result.

**3.3 Split — word-grained.** Every row line of band 9 carries words of both boxes (§ 7.3), so
lines are not the unit. For a band the query selects:

1. For each box: its words → `text_lines` → one box band; its title-bar words → that band's title.
2. Words in no box and no title bar → **one residue band**, sent through
   `cut_trailing_notes(segment(residue))` unchanged.
3. The resulting bands enter the list ordered by `(top, x0)`.

**3.4 Every input to a box band is box-scoped.** Each box band is built by the **unchanged**
`_build_ruled_band`. Measured on band 9, each input below, left page-scoped, breaks the read by
itself (§ 7.3):

| input | page-scoped failure | box-scoped input |
|---|---|---|
| `sub_rules` | `extract_rules` yields 12 xs for 8 drawn verticals (fill edges) → tiling refused | the box's own verticals from § 2.1, as `Rule(x=centre, top, bottom)` |
| rule filter | the loop's y-only filter hands each box the other's rules (22 / 20) | as above — no page-wide filter is consulted |
| `page_chars` | `band_chars` is filtered by y only → left-box glyphs enter the right box's first cell | glyphs clipped to the box's x-extent |
| `sub_hrules` | — | the box's own horizontals |

With all four scoped: **T1 7 columns × 5 lines, T2 2 columns × 4 lines** (§ 7.3).

**3.5 Captions are attached after the build.** `_build_ruled_band` replaces `captions` on every
return path with its own peel (`compile.py` — `word_band = _replace(… captions=caption_lines)` and
both later returns), so the call site sets `captions = title_lines + built.captions` on the result.

**3.6 Section repair.** A box band's `specs` entry is `None`: it is never rebuilt with
`section_repair=True`, whose rebuild would read page-scoped chars again (§ 3.4).

**3.7 Downstream, measured.** `merge_run_candidates` returns `()` for cbh p0 both today and with
the split in place (§ 7.3) — the run merge does not re-fuse the box bands.

## 4. What is not done (design § 4)

- The totals family (R-b). The roster port totals stay `#ignored`; where `1,951,264` lands is
  **measured and recorded** by O2, not asserted. This loop **raises the register row** widening
  R74 that the handoff notes was never written.
- A single closed box with ink outside it (the four cbh rosters) stays on loop P's caption peel.
- Boxes spanning several bands (graincorp-capacity, graincorp-stem p0–2) are untouched.
- Zero-width rules touch only exactly (R-c); bfs p5/p6 are unaffected.
- `extract_rules`'s over-read is not repaired for any other path.
- The Note block is not engineered: whether the residue reads as notes or `#ignored` is recorded.
- cbh is **not** accepted: `etkl:03` stays `met false`, no `cor:scoreFloor` is pinned. The ink
  score before/after is recorded as a fact, never as the oracle.
- No NEURAL worker.

**Named risks for the plan** (not settled here):

1. Downstream header derivation may read T2's first row (`ALB | 1 - 15 October`) as a boxhead.
   O2's "0 column labels on T2" is the check; if it fails, that is a finding, never a weakened
   assertion.
2. cbh band indices from 9 on shift by +2. Every test, fixture, reading or register row naming a
   cbh `#tableN` with N ≥ 9 must be **enumerated** (not grepped by guess) and re-keyed by content.

## 5. The oracle (design § 3) — never the ink score

**O1 — synthetic, runs in CI.** A reportlab fixture PDF modelled on band 9: two closed boxes side
by side in one band, each with a coloured title bar; one with a boxhead, one without; a note line
below. Positive: `page_bands` returns two box bands with the fixture's column counts, each
carrying its title words as captions, plus a residue band holding the note. Negatives, each in CI:

- **N1** — one closed box with a title bar and ink outside (roster-like): no split.
- **N2** — two open header-only lattices (bfs-like, no outer frame): no split.
- **N3** — two abutting rules with a sub-stroke gap (cbh's 2e-5): joined under § 2.2; the
  falsification sets the bound to 0 and shows the box refused.

**O2 — cbh carriage, local (`-m corpus`), pinned like `tab:11`.** On `compile_document`'s graph for
cbh, the region at y 681–761 has **exactly two** `RecordTable`s:

- T1: column labels exactly the 7 of § 1; row labels `ALB, ESP, GER, KWI`; pointwise cells
  including KWI × TOTAL = `284,895`.
- T2: 2 columns, **0** column labels, 4 rows with their date cells.
- Each title text as a `tab:RegionCaption` of its own table.
- No cell of either table contains `Note:` or the note prose.

**Controls — a total check beside the pointwise one.**

- **C1** — corpus-wide, the § 3.2 query selects **exactly one band**: cbh p0 band 9.
- **C2** — every other corpus document compiles to the same graph (canonical hash), before vs after.
- **C3** — cbh's four rosters keep identical cells, compared by content, not by `#tableN`.

**`tab:12`.** Declared in `tests/arc-manifest.ttl` authored `prog:met false`, `prog:oracleTest`
naming O2. O2 ships under `@pytest.mark.xfail(strict=True)`; the build XPASSes it, and the marker
and `prog:met` are flipped in one reviewed act — the `tab:11` forcing function
(`tests/test_carriage.py` docstring).

**Falsification (CLAUDE.md § Plan authoring, rule 4).** Every task removes or inverts its subject
and shows its test failing: delete the split call (O1, O2 fail); drop the frame condition (N2
fails); set the touch bound to 0 (N3 fails); page-scope `page_chars` (O2's T2 cells fail).

## 6. Classification (CLAUDE.md § 8)

| step | class | why |
|---|---|---|
| rule reader (§ 2.1) | PROCEDURAL | raw extraction: source vector marks → typed rule facts |
| touch, components, frame (§ 2.2–2.3) | PROCEDURAL | decidable exact interval arithmetic; the only bound is read off the marks (R-c) |
| title bar (§ 2.4) | PROCEDURAL | exact containment and touch over extracted fills |
| "band holds ≥ 2 tables" (§ 3.2) | AXIOM | SPARQL `SELECT`, open-world, closed only within the band |
| word partition + band construction (§ 3.3) | PROCEDURAL | applies the decision; decides nothing |

No tuned constant is introduced. Pre-existing constants met on the path (`segment._GUTTER_DOMINANCE`,
`detect_bands`' `gap_factor`) are untouched; the residue band still meets them as today.

## 7. Measurements (2026-09-28, `main` at `6eb80ca`; `src/` unchanged since `b2d2052`)

**7.1 Near-miss gaps** — `gaps.py`, every H/V rule pair with 0 < gap ≤ 1pt, corpus-wide:

```
lim>0:  50 pairs, max gap 0.01,  min lim 0.385, all joined True
lim==0: 77 pairs, gaps 0.00017 .. 0.57379, [('bfs', 5), ('bfs', 6)]
```

cbh p0: `TOUCH=exact` → right box `cols 1, rows 4, tiled 17/21`; `TOUCH=stroke` → `cols 2, rows 4,
tiled 21/21`, title bar found (`boxes.py corpus/ag-trade/cbh-stem-2026-08-03.pdf 0`).

**7.2 Closed frame** — `closed2.py` (a first version reported cbh open at top/bottom: its coverage
ignored the corner ink of the verticals — the horizontals start at 38.4, where the 0.48-wide left
vertical at 37.92 ends):

```
cbh p0            6 boxes  closed True  (4 rosters, 7-col box, 2-col box)
graincorp-capacity 1 box   closed True
graincorp-stem p0-2 3 boxes closed True
bfs p5            2 boxes  closed False (sides TBLR = T,T,F,F / T,T,T,F)
bfs p6            1 box    closed False (T,T,F,T)
```

**7.3 Seams on band 9** — `seam.py` (throwaway what-if, not the implementation):

```
raw band idx 9 y 683.5 761.5 lines 10
691.6 LLLLLLLLLRRRRR PORT WHEAT MAIN WHEAT GRADES ... TOTAL ALB 1 - 15 October
box [38, 449, 690, 731] rules by y: 22 by x&y: 15
box [543, 690, 690, 722] rules by y: 20 by x&y: 7
repo rule xs [37.92, 38.16, 75.74, 76.1, 154.22, 216.26, 259.22, 302.18, 345.14, 345.64, 448.85, 449.21]
own  rule xs [38.16, 75.98, 154.46, 216.5, 259.46, 302.42, 345.39, 449.09]
  (repo rules, box-scoped)            _rule_boundaries → None for both boxes
  (own rules, page chars)   ncols 7 ; ncols None, first cell 'PORTWHEATMAIN WHEAT GRADES…'
  (own rules, box chars)    ncols 7 rows 5 ; ncols 2 rows 4 ['ALB | 1 - 15 October', …]
runs today: ()   runs with split: ()
```

**7.4 `extract_rules` over-read** — handoff census (`cmp_repo.py`, not re-run this session):
427/460 non-rules on graincorp-capacity, 678/413 on apple p0.

---

## 8. Addendum — Task 3b: the resolution guard refuses only what it can witness (2026-09-28)

**Written at 66,455 working tokens, past the 50K originating floor, on the maintainer's explicit
override (logged in plimslop's pre-flight log).** Treat this section as a proposition a reviewer
must attack, not as settled design. Evidence: M1–M3 in
`docs/superpowers/2026-09-28-box-split-t3b-measurements.md`, M4 in
`docs/superpowers/2026-09-28-box-split-t3b-witness-census.md`.

### 8.0 The ruling it obeys

Maintainer, 2026-09-28, recorded in the SDD ledger: extend the loop with Task 3b. The plan's
constraint "`_build_ruled_band` is not modified" is lifted for the R225 arm-B guard only. The branch
does not merge until O2 XPASSes. `BASELINE_ASSERTED[("cbh-stem-2026-08-03",0)]` and
`EXPECTED_VERDICTS["cbh"]` are not re-pinned before T1 reads.

### 8.1 The defect

The guard (`compile._build_ruled_band`, `_under_resolved`) refuses a re-bucket when the rules give
fewer columns than `_word_column_count(sub)`. Its stated reason is that such a re-bucket "can only
FUSE". The count is a proxy for that property, and cbh T1 refutes the proxy. It reads 9 columns
against 7 rules because in the WHEAT and TOTAL cells the header word lies wholly right of the body
numbers (M1). Yet no line of T1 has two words that those two extra gutters separate, so nothing
would fuse. This is the one geometric attempt (§ 8 of CLAUDE.md, 2026-09-17), and it is refuted.
The remedy below adds no second heuristic: it tests the property the guard already claims, exactly.

### 8.2 The change

**A fusion witness** over a band's lines and a set of rule xs is two words `a`, `b` on one line,
both wholly inside the same consecutive rule interval, `a.x1 < b.x0`, such that some point of
`(a.x1, b.x0)` is covered by no word of any line of the band.

**Its query form, stated once.** No point-quantifier exists in SPARQL, so it is expressed through
word right edges: a witness exists iff some word right edge `e` has `a.x1 ≤ e < b.x0` and no word
`v` has `v.x0 ≤ e < v.x1`. This is equivalent. If an uncovered point `p` exists, the largest word
right edge `≤ p` satisfies the condition. If some `e` satisfies it, the points just right of `e`
are uncovered. The spans are closed, as in M4.

**The guard becomes a conjunction:** refuse iff the count refuses **and** a witness exists over
`(sub, xs)`. Where no witness exists, re-bucketing on `xs` joins no two words that the band's own
layout separates. So absence is a proof, and the refusal it lifts was never justified. Where a
witness exists, the refusal stands exactly as today.

- **Scope, measured (M4):** of 100 `_build_ruled_band` calls, exactly one changes, cbh T1, from
  refuse to accept. All 35 other refusals keep a witness. That includes the 8 bfs p6 bands with
  T1's shape and the 27 outer-box bands R225 was raised for. The 64 accepts cannot change, because
  the conjunction only relaxes.
- **The post-refinement site** (`len(col_xs) - 1 < _word_cols`) is **not changed.** It refused
  nothing in M4's census (fact 4), so changing it would ship an unexercised branch.
- **The witness runs only when the count refuses.** On the refused population it costs one query
  per band.

### 8.3 Classification (CLAUDE.md § 8)

| step | class | why |
|---|---|---|
| the witness (`vocab/queries/rebucket-fuses.rq`, an `ASK`) | AXIOM, derivation, open world | Evidence-positive: a refusal needs a witness *present*. Its one `NOT EXISTS` is closed within the band's own fresh graph, which is the closure boundary, as in `confirm-boundary.rq`. No numeric literal (`test_no_tuned_constant_in_rq_files`). |
| emit the band's word + interval evidence graph, run the query | PROCEDURAL | Engine glue, the `boundary.py` pattern. It decides nothing. |
| the count (`_word_column_count`) | unchanged | R225's shipped predicate, now a necessary condition only. Its gutter defaults are pre-existing and not re-opened here. |

**Why not NEURAL.** The witness makes no reading judgement. Whether two words belong to one cell
is exactly what it does *not* decide. It proves the one case where that question cannot matter,
because nothing the layout separates gets joined, and it abstains everywhere else, where today's
refusal stands. The judgement it leaves open is "is this gap a word space or a column gutter?".
M4 fact 1 shows that question in the 52 phrase-level witnesses. It is the NEURAL question for the
35 remaining refusals, and it is **not built here**. No oracle for it exists yet: no oracle, no
worker.

**New transient terms**, declared in `vocab/ontology/tab.ttl` beside `tab:HeaderGlyph` under a
"(transient, pre-holon)" heading: a word class carrying line identity and x0/x1, and a rule-interval
class carrying lo/hi. The names are the implementer's to choose. Never asserted into a holon.

### 8.4 Task 3b — the contract (not the code)

**Seam:** the `_under_resolved` assignment in `compile._build_ruled_band`. The count stays. The
witness is added as a conjunct, evaluated only when the count is True.

**Invariants.**
- I-3b-1: the guard's refusal set is a subset of today's.
- I-3b-2: `_build_ruled_band`'s behaviour is byte-identical on every band where the count does not
  refuse, and on every band where a witness exists.
- I-3b-3: the `.rq` carries no numeric literal, and the Python glue carries no tolerance.

**MEASURE before writing:**
- (i) Rebuild M4's census with the *query's* semantics. Containment is "wholly inside one
  interval"; M4 used word centres. Show the flip set is exactly `{cbh p0 T1}`. A different set is
  a finding: report it, never tune it away.
- (ii) Confirm on T1 that `refine_rule_columns` confirms no candidate at 101.38 or 377.88 once the
  band is accepted. `confirm-boundary.rq` needs header ink on both sides, and WHEAT/TOTAL sit on
  one side only. Measure it; do not assume it.

**Oracles.**
- **U1 (CI, synthetic):** a reportlab ruled grid with the T1 defect. In at least one ruled cell,
  the header word sits wholly right of every body word. It also has one multi-word header cell whose inter-word gaps are covered by a wider body word, as `MAIN WHEAT GRADES` is on T1, because the `NOT EXISTS` falsification below needs a pair to fire on. **MEASURE that the count refuses it on
  today's tree**, or the test pins nothing. After the change, `_build_ruled_band` returns a band
  whose header line re-buckets into one cell per rule interval.
- **U2 (CI, negative):** the same grid plus one body line carrying two words in one rule interval,
  across a gap no other line covers. Still refused.
- **U3 (CI, existing):** the R225 D1 tests M3 lists stay green.
- **O2 (corpus, local):** XPASS is the loop's oracle. **Proposed, and it may fail:** it was measured
  only that T1's header re-buckets to the 7 right cells (M3's control). The full path through
  classify, compile and the membrane has not been run. § 4 risk 1 (T2's first row read as a
  boxhead) is still live.
- **Local sweep:** the three cbh tests red since Task 3 (handoff § 2), plus
  `test_o3_no_page_loses_asserted_ink_to_a_merge`, plus `tests/test_cbh_e2e.py`. Re-pin cbh
  literals only from a measured value after O2 XPASSes. One test file per process, from a `.sh`
  under bash.

**FALSIFICATION (mandatory):**
- Drop the conjunct (count alone): U1 fails.
- Make the witness always-false (the guard off): U2 fails.
- Delete the `NOT EXISTS` from the query: U1 fails, because every inter-word gap becomes a witness.
- Restore, and show the suite green.

### 8.5 What 3b does not do

- It does not change the count, its gutter defaults, or the post-refinement site.
- It does not touch the 35 refusals that carry a witness, including bfs p6. Their "word space or
  gutter" judgement is recorded as the NEURAL candidate above, to be raised as a register row at
  Task 5, not built.
- No `section_repair=True` path is measured (M2's scope caveat). The census covers the default path
  only.
