# Handoff — the two-ended peel is refuted in its leading half, and its trailing half has a population of one

**Topic:** The subject the previous handoff named — *"a two-ended furniture peel for RULES-FREE bands,
disposed by the alignment universe"* — was attacked before it was built. Its **leading** half is
refuted: the cut the alignment universe proposes is, by construction, a cut at the first admitted
data row, and the column header sits above it. Its **trailing** half survives but changes the reading
of exactly **one band corpus-wide**.

**Serves:** prog:criterion:etkl:04 — ONS. The criterion's subject is column identity; p4 is the only
ONS page that prints column labels at all.

**Date:** 2026-09-15. **Tree:** branch `r230-two-ended-furniture-peel`, cut from `main` at `8d6d20d`.
**No code was written and no shipped file was edited this session.**

**Doc impact: none.** No released term, vocabulary, shape, contract or instrument touched.

**Part 5 is graded per action, because this handoff was authored OVER the originating floor**
(CLAUDE.md § Loop & context hygiene). `plimslop preflight --shape originating --tokens 150800
--decision defer` was logged; the spec was deferred, not written late. Parts 1–4 are pointers and
records and do not degrade.

---

## 5. The next concrete action

### 5a. ASSERTED — the leading cut removes the boxhead, so the named subject cannot be built as named

`derive_data_grid` admits *data* rows. Its first admitted row is therefore the first row **below** the
column header, and a leading peel bounded by it cuts the header off the band. Sampled across the
corpus, **6 of 6** bands with a proposed `L > 0` had their column-header row(s) inside the cut:

```
cbh p0 band1        L=8  cuts  "VNA # Vessel Name Time Nominated Date Nominated Client ETA…"
cbh p0 band7        L=5  cuts  the same header trio
who p0 band2        L=2  cuts  "Year: Month Month L M S -3 SD -2 SD -1 SD Median 1 SD 2 SD 3 SD"
ons p8 band4        L=2  cuts  "S222 S243 KI77 KI7G KI7O"   (the series-id row)
graincorp-stem p1 band1  L=3  cuts  all three header lines
apple p2 band2      L=3  cuts  the whole date header
```

That is **6 of 6 sampled, not 28 of 28** — the other 22 real cuts were not read. The claim is
therefore strong on the sample and not established on the population; a spec must re-sample before
resting on it.

Every sampled **trailing** cut removed genuine furniture (`Sources: OFS - BEVNAT, STATPOP`, footnotes,
CBH's disclaimer). So `T` looks safe and `L` does not, and the asymmetry is structural rather than
incidental: furniture below a table is not addressed by the grid, while the header above it is the
thing the reader most needs.

**This does not refute ONS p4.** There, `L=6` works — page 4 goes `score 0.5278 → 0.8863`, region 0
ignored → asserted with 168 cells — because the hierarchical path recovers a header the leading cut
removed. It refutes the *generalisation*: the same rule that repairs p4 decapitates five other bands.

### 5b. ASSERTED — the trailing half's reading-changing population is ONE

Across 191 bands / 106 rules-free, a two-ended peel changes the reading of **2**:

| | apple p2 b2 | ONS p4 b0 |
|---|---|---|
| as-is → max ncols | 2 → 3 | 1 → 6 |
| best (L,T) | (1, 0) — leading only | (2, 1) — **trailing required** |
| current verdict | **escalated** (an existing reading) | **ignored** |
| after the peel | still `UNSUPPORTED_TABLE` | asserted, 168 cells |

So the trailing cut buys exactly one band, and it is ONS p4 b0. The other changing band is *moved and
not repaired* — its reason merely shifts from "header has 3 words but 2 columns" to "header has 4
words but 3 columns" — and it is currently escalated, so a peel there changes an existing reading
without fixing it. Under CLAUDE.md's zero-tolerance generalisation rule, **a population of one is the
finding**, not a detail.

### 5c. ASSERTED — an ncols-based safety gate is blind, and this is the trap to carry forward

Of the 16 rules-free bands that are **not** ignored, a `T=1` cut leaves `ncols` **unchanged on 12**:
WHO's 7 asserted bands (last line a real z-score row) and BFS p5 bands 9–12 (last line a real canton
row, e.g. `Thurgovie 289 650 …`). A trailing peel gated on *"did the grid get better"* would silently
delete a real data row on twelve live bands with no grid signal at all.

The corpus contains **no** rules-free band where a trailing cut both helps and is visible to the grid,
other than ONS p4 b0. Any trailing peel must be gated on **what the line is** — a furniture predicate
— never on whether `ncols` improves.

The same trap already fired inside the measurement: selecting the cut by max-`ncols` picks `(2, 1)` on
ONS p4, and `s=2` **escalates** (`ROUND_TRIP_FAIL`); `s=5` also reaches 6 columns and escalates
(`REGION_TILING_FAILED`). Only `s=6` asserts. `ncols == 6` is necessary and nowhere near sufficient,
and `classify` alone returns **0 cells even for the peel that works** — so neither can be a spec's
oracle. The page-scope figures (`0.5278 → 0.8863`, 168 cells) are the ones to cite.

### 5d. PROPOSED — the surviving candidate, and it must be RUN before anything is built on it

**Rests on a prediction that may fail.** The half that survives 5a is a **trailing-only** furniture
peel whose proposer is the datagrid's refusal set rather than its admission set — i.e. cut a trailing
line when the grid explicitly refuses it as `unplaceable`, and never bound the leading end at all.
That inverts the mechanism from "keep what was admitted" to "drop what was refused, from the bottom
only", which leaves the header untouched by construction.

Whether it is worth a loop is **a maintainer's call, not a loop's**, because 5b prices it: one band.
The honest alternatives are (i) build the trailing-only peel and accept a population of one, (ii) fix
ONS p4 by a different mechanism entirely, or (iii) rule that p4 is not the route to etkl:04 and park
it. **This handoff does not choose.**

If it is built, the first obligation is the pair named in `peel_leading_captions`' docstring —
`tests/etkl/test_continuation_licence.py` and `tests/etkl/test_logical_arithmetic.py` (test **modules**,
not functions; nothing of those names exists as a function). Their risk is now **measured and low**:
`case3_with_subtotals_pdf` — the fixture whose subtotal rows the earlier peel swallowed — **draws
rules** (`tests/etkl/fixtures.py:1629-1632`, and it returns `rule_xs`), as do
`cut_group_two_page_pdf`, `page_local_group_two_page_pdf`, `two_page_unrelated_pdf` and
`bare_identical_two_page_pdf`. A rules-free peel cannot reach them. `simple_table_pdf`
(`test_logical_arithmetic.py:299`) **is** rules-free and is the one fixture in that set a rules-free
peel could touch.

### 5e. ASSERTED — what this session must NOT be read as having done

No code, no spec, no plan, no contract, no instrument, no residue row. The peel is **unbuilt** and now
**partly refuted**. [[R231]] is untouched. [[R226]] (no leaf header block on any ONS page) is untouched
and still stands between a repaired p4 and a contract — recovering six *columns* is not recovering six
column *labels*. ons carries **no `cor:scoreFloor`** and stays `cor:Unadjudicated`, so etkl:04 could
not have been met by this loop under any outcome.

---

## 1. Where the primaries are

- **The row** — [[R230]] in `residues-open.md`, already amended once by the previous loop. Its
  amendment names the two-ended peel as the route; **this handoff refutes the leading half of that
  route** and nothing in the register records that yet. See § 3.
- **The previous handoff** — `docs/superpowers/2026-09-14-ons-p4-furniture-handoff.md`. Its § 5a names
  the subject this session attacked. Its § 3 flagged two assumptions as unverified; both were
  measured, and **one was refuted** (see § 2).
- **The site** — `infer_leaf_grid` and `_column_blank_profile` (`src/iladub/etkl/grid.py`; find by
  `grep -n "def infer_leaf_grid"`). The classification that ignores the band is `regions.py`'s
  `"fewer than 2 columns"` (`_reason`, `regions.py:91`).
- **The peel that refuses to help** — `peel_leading_captions` in `src/iladub/etkl/gridregion.py`. Its
  two call sites are `compile.py:147` (inside `_build_ruled_band`) and `sectiongraph.py:70`
  (read-only; "nothing is peeled off the band"). **A rules-free band reaches neither**:
  `page_bands:437` appends it directly when `sub_rules` is empty.
- **The proposer** — `derive_data_grid` in `src/iladub/etkl/datagrid.py:319`. Three call sites in
  `src/`: `compile.py:1407` (the fallback), `donation.py:127`, and its definition.
- **The translation precedent, and it is the one to reuse** — `_ink_key` +
  `head_line_refusals` (`src/iladub/etkl/donation.py:86,110-143`). It re-identifies a band's line 0
  against the page-line list **by ink**, requires `len(hits) == 1`, and its docstring records that raw
  word-tuple equality re-identified **0 of 12** bands. Do not invent a second translation.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The leading cut removes the boxhead (6/6 sampled) — the named subject cannot be built as named | **this file § 5a only.** Nothing else records it |
| The trailing half changes exactly one band's reading corpus-wide | this file § 5b only |
| An `ncols`-based gate on a trailing peel is blind (12 of 16 live bands) | this file § 5c only |
| The two index spaces are NOT the same space (32 vs 37) | this file § 3; refutes the previous handoff's § 3 assumption |
| Translation must go by ink key, not by offset arithmetic or `top` | this file § 1, § 3 |
| The spec was deferred at the context floor rather than written late | `plimslop` pre-flight log, this session |
| Whether to build the trailing-only peel at a population of one | **undecided — § 5d puts it to the maintainer** |

**Everything in the first three rows lives only in this file.** No residue row was raised, which is a
deliberate omission and a cost: if this file is not read, the next loop will rebuild the refuted
design. Raising [[R232]] (leading cut removes the boxhead) is the cheapest way to make it survivable.

## 3. Unverified or assumed

- **§ 5a is 6 of 6 SAMPLED, not 28 of 28.** The other 22 real cuts were never read. A spec must
  re-sample.
- **§ 5d entirely**, per its grading. The refusal-set proposer is a design proposition; nobody has run
  it, and it may abstain on ONS p4 itself.
- **The previous handoff's index-space assumption is REFUTED.** `DataGrid.rows` indexes the *page's*
  text lines (`datagrid.py:111,321-322`); band 0 holds 32 lines against the page's 37. The numeric
  agreement of `lines[6:-1]` with admitted `6…30` holds **only because band 0 starts at page line 0**.
  Band offsets on that page are 0 / 32 / 33 / 36.
- **Offset arithmetic is a latent break, on 2 measured bands.** `ons p7 band15` (page indices 60, 61,
  **66, 67**) and `ons p8 band8` (61, 62, **67, 68**) are not contiguous slices of the page-line list —
  two-column footnote blocks whose lines interleave with another band's by `top`. Both have an empty
  grid overlap today, so nothing is mis-cut; an `offset + j` translation would break there and an
  ink-key/top-identity one survives.
- **The proposer is absent on 11 of 27 pages**, which carry **78 of the corpus's 191 bands** (all in
  bfs and ons). On those the mechanism must abstain outright.
- **The contiguity guard abstains exactly where a table wants a peel most.** 60 of 64 overlapping
  bands are contiguous; the 4 gaps are all *explicit grid refusals* — apple's `Cost of sales:`,
  `Operating expenses:`, `Earnings per share:` section labels, and bfs p5's total row refused
  `RowAddressability/no-key`. So the mechanism is silent on apple's income statement and balance sheet.
- **Three proposed cuts remove more than half a band** (`cbh p0 band9` T=9 of 10, `bfs p6 band10` T=3
  of 4, `apple p2 band2` L=3 of 4). `cbh p0 band9` looks wrong — it keeps one line and cuts a 5-row
  port/grade table. Unexplained; not investigated.
- **`derive_data_grid`'s cost figure is INHERITED, not re-measured** — "4.6 s over all 27 corpus pages
  against 35.8 s of band-building" is quoted from `donation.py:112-115`. A peel-time proposer would
  call it on **every** page rather than only where a band could benefit, which is the lazy pattern that
  docstring establishes. Nobody measured the new shape.
- **`derive_data_grid`'s admission is PROCEDURAL Python, not SHACL.** `place()` carries `± 0.5`
  literals (`datagrid.py:364,378`) and a `len(hit) >= 2`. The `conforms` tuple names shapes but the
  admission is not one. A spec must not claim "proposer and disposer are both AXIOM".
- **`Band.captions` books ZERO tokens.** `_emit_band_captions` (`compile.py:254-274`) emits
  `tab:RegionCaption`/`tab:SectionCaption` and adds no ink to either score operand. Peeled furniture
  leaving an *ignored* band is harmless (an ignored band books nothing by design), but peeling from an
  *asserted* band would move ink out of the denominator. Unmeasured for the trailing-only shape.
- **No test pins ONS p4's current wrong reading**, and ons has no `cor:scoreFloor`, so a repair breaks
  no pin. It would oblige a new dated `cor:reading` in `tests/corpus-manifest.ttl` — the 2026-09-14 D1
  entry at `:226` is the precedent to copy.

## 4. What this session did

Read the register and the previous handoff, took its § 5a subject, and **measured its premises before
building it.** Three of them moved:

1. Its index-space assumption was **refuted** (32 ≠ 37).
2. Its conclusion **held** but its evidence did not — `infer_leaf_grid().ncols` does not reach it,
   and `classify` alone would have refuted it by returning 0 cells for the peel that works.
3. Its subject's **leading half was refuted outright** by a corpus census it had not run.

**Worth carrying, because it is the technique and not the result.** The previous handoff was written
by the session that measured ONS p4 most closely, and it was right about that page and wrong about the
rule. A leading peel bounded by the first admitted data row repairs p4 and decapitates five other
bands — and the thing that separated those two facts was a census over 191 bands, not more work on
page 4. **A repair measured on one page is a hypothesis about a corpus; the population is the only
thing that can tell you which.**

Two of this session's own instruments also failed, in opposite directions, on the same question —
whether a fixture draws rules. A fixed 60-line window said `case3_with_subtotals_pdf` draws none (it
draws four, below the window); a function-boundary parser then said `sectioned_ruled_table_pdf` draws
none (it delegates to `_draw_section`). Grepping for draw calls cannot answer it; only running
`page_bands` and reading `band.rules` can. That is the run-vs-grep distinction in
`enumerating-before-claiming`'s own last table row, hit twice in three turns.

---

## 6. RULING — 2026-09-15, by the maintainer: build arm (a), the TRAILING-ONLY peel

§ 5d put three options and declined to choose. **The maintainer chose arm (a): a trailing-only peel
whose proposer is the datagrid's REFUSAL set** — drop lines the grid explicitly refuses, from the
bottom only, never bounding the leading end. § 5d's sentence *"This handoff does not choose"* stands
as written: the handoff did not choose, and this section records that someone else did.

**What the ruling accepts, stated so the next session does not rediscover it as an objection:** the
arm changes exactly **one** band's reading corpus-wide (ONS p4 band 0, § 5b). That price was on the
table when the choice was made. Do not re-litigate it; if it must be reopened, reopen it as a
maintainer question, not as a loop's own finding.

**What the ruling does NOT license.** Arm (a) was typed **PROPOSED** in § 5d and that grade survives
the ruling — choosing an arm does not run its prediction. The mechanism has never been executed, and
it may fail on its own terms.

### The next session's order of work, and the first step is a measurement

1. **RUN THE PREDICTION FIRST, before writing any spec.** Two questions, both cheap:
   - Does the refusal-set proposer actually propose `T=1` on ONS p4 band 0 — i.e. is the trailing
     `Source: Index of Services estimate from the Office for National Statistics` line carried in
     `DataGrid.refusals`, and is it the *only* trailing refusal there?
   - Does it refuse to cut the **12** live bands of § 5c? Those rows (WHO's z-scores, BFS p5's
     cantons) are *admitted* by the grid, so the mechanism should never propose cutting them. **That
     is the claim that makes arm (a) safe, and it is unverified.** If any of the 12 is proposed for a
     cut, arm (a) is refuted and the ruling needs revisiting rather than implementing.
2. **Only then write the spec.** If step 1 fails, write the refutation and hand back — do not weaken
   the mechanism to make it pass, per CLAUDE.md § Plan authoring discipline (a plan-supplied test that
   cannot be satisfied is a plan defect, not a personal failure).
3. **Re-sample before resting on § 5a.** The leading-cut refutation is 6 of 6 *sampled* out of 28 real
   cuts. Arm (a) does not depend on it — it abandons the leading cut entirely — so this is not
   blocking, but any prose repeating "the leading cut removes the header" as a population claim must
   re-sample first.

### Constraints the implementation inherits (all measured, see § 3 and § 5c)

- **Gate on what the line IS, never on whether `ncols` improves.** On 12 of 16 live rules-free bands
  `T=1` leaves `ncols` unchanged while deleting a real data row.
- **Translate by ink key, not offset arithmetic.** Reuse `donation._ink_key` + its `len(hits) == 1`
  uniqueness guard; `offset + j` breaks on `ons p7 band15` / `p8 band8` ([[R233]]).
- **The proposer is absent on 11 of 27 pages** (78 of 191 bands). Abstain there; do not invent a
  fallback.
- **Follow the lazy precedent** (`donation.py:112-115`): do not call `derive_data_grid` on a page where
  no band could benefit. The cited cost is 4.6 s across 27 pages against 35.8 s of band-building, and
  that figure is inherited, not re-measured.
- **`Band.captions` books ZERO tokens** (`compile.py:254-274`). Peeling furniture off an *ignored*
  band is harmless; peeling off an *asserted* band moves ink out of the denominator. ONS p4 band 0 is
  ignored today, so the repair is upside — but the trailing-only mechanism will also fire on asserted
  bands, and that case is **unmeasured**.
- **The regression pair is `tests/etkl/test_continuation_licence.py` and
  `tests/etkl/test_logical_arithmetic.py`** (modules, not functions). Their fixtures are ruled except
  `simple_table_pdf`, so a rules-free peel can reach only that one.

---

## 7. Corrections to earlier sections of THIS file

Appended rather than edited in place, so the original wording stays readable and the correction is
visible as a correction. Three statements above were true when written and are false now.

1. **§ 5e's "no residue row" is FALSE.** It was written before the rows existed and was not revised
   when they were added minutes later, in the SAME commit (`077ccfc`). **[[R232]] and [[R233]] were
   raised by this loop.** Everything else in § 5e stands: no code, no spec, no plan, no contract, no
   instrument.
2. **§ 2's row "undecided — § 5d puts it to the maintainer" is SUPERSEDED by § 6.** The maintainer
   ruled on 2026-09-15: build arm (a), the trailing-only peel. The decision is recorded in § 6 and on
   [[R232]]'s row, so it is no longer a decision living in one file only.
3. **§ 1's "nothing else records it yet", said of the leading-half refutation, is SUPERSEDED.**
   [[R232]] records it, with its measurement and its 6-of-6-sampled caveat intact. § 2's first three
   rows are likewise no longer "this file only".

**What is NOT corrected, deliberately.** § 5a's finding is still **6 of 6 sampled out of 28 real
cuts**, and § 5d's arm (a) is still typed **PROPOSED** — the ruling chose it without running it. Those
are limits of the evidence, not stale wording, and they must survive into the next loop.

---

## 8. THE PREDICTION WAS RUN — arm (a) is REFUTED, and the loop was re-ruled

§ 6 ordered the prediction run before any spec, and said that a refuted arm means **revisiting the
ruling rather than implementing**. It was run the same day. Both of § 6's questions came back
**confirmed** — and the arm is dead anyway, for a reason neither question asked.

### 8a. Both § 6 questions: CONFIRMED

**Question 1 — does the refusal-set proposer propose `T=1` on ONS p4 band 0?** Yes, exactly:

```
ons p4 b0  lines=32  rules=0  T=1
    cut line 31 (page idx 31) [unplaceable]  'Source: Index of Services estimate from the Office for National Statis…'
```

The walk stopped at 1, so it is the **only** trailing refusal there, as predicted.

**Question 2 — does it refuse to cut the 12 live bands?** Yes, all 12:

```
who p0 b3,b4,b5 / p1 b3,b4,b5 / p2 b2   asserted   T=0  safe   ('1: 0 12 0.0644 9.6479 …' z-score rows)
bfs p5 b9,b10,b11,b12                   escalated  T=0  safe   ('Thurgovie 289 650 2 750 …' canton rows)
apple p2 b2                             escalated  T=0  safe
```

Only 2 live bands would be cut at all (`bfs p6 b1`, `ons p4 b2`), and both are `T == nlines`
annihilations that the ≥2-keep guard (below) refuses. **Arm (a) is provably safe.**

### 8b. And it is a NO-OP. That is the refutation

```
full band (today)                  lines=32  ncols=1  NON_TABLE          'fewer than 2 columns'
TRAILING-ONLY  T=1   <- arm (a)    lines=31  ncols=1  NON_TABLE          'fewer than 2 columns'
leading-only   L=6                 lines=26  ncols=3  UNSUPPORTED_TABLE
BOTH  L=6, T=1                     lines=25  ncols=6  UNSUPPORTED_TABLE
```

A trailing-only cut changes **nothing** — same `ncols`, same kind, same reason, band still ignored.
The leading furniture is what closes the gutters.

**The error, named so it is not repeated:** census #1 reported p4's best cut as `(2,1)` and marked it
*"trailing REQUIRED"*. § 5d and the ruling both read *required* as *sufficient*. **Required ≠
sufficient.** The trailing cut is necessary and useless alone.

### 8c. What survives, measured: the BOTH-ENDS refusal walk

Cut the contiguous run of grid-REFUSED lines from **both** ends of a **rules-free** band, keeping
**≥ 2 lines**. Corpus-wide:

```
BOTH-ENDS refusal walk, RULES-FREE only, >=2 lines kept
ons p4 b0  lines=32  L=6 T=1   ncols 1->6   kind NON_TABLE->UNSUPPORTED_TABLE
      FIRST KEPT LINE: 'Jan 2024 -0.1 -0.3 0.2 0.1 -0.2'
rules-free bands cut by the BOTH-ENDS walk: 1
```

Exactly **one** band corpus-wide, deriving precisely the cut that works, with **no tuned constant**.
Page-scope effect is already measured (§ 5a): `0.5278 → 0.8863`, region 0 ignored → asserted, 168
cells.

### 8d. Two corrections this run forces on earlier sections

1. **§ 5a's "6 of 6 sampled" header-eating is NOT a property of the rule.** "Refused from the top"
   and "first admitted row" are the **same bound** — every page line is either admitted or refused —
   so the two are not alternatives at all. All six header-eating bands were **RULED** bands, outside
   the design's rules-free scope. Within that scope the walk fires once and cuts no header anywhere.
   § 5a's *measurement* stands; its implication for this design does not.
2. **The ≥2-keep guard is load-bearing, not cosmetic.** Without it the walk annihilates **25 of 26**
   rules-free bands it touches (whole-band deletions: `Apple Inc.`, `GRAINCORP SHIPPING STEM`,
   `Notes`, `Page 5 of 7`). With it, 25 become abstentions and `apple p2 b2` (4 lines, `L=3`) is
   saved from decapitation. **It is not a tuned constant** — `classify` already returns
   NON_TABLE `"fewer than 2 lines"`, so a band below 2 has no grid by the pipeline's own definition.

**Option B is refuted too, as unconstructible.** Bounding `L` by the derived boxhead is circular:
`header_body_split(band, grid)` returns **`None`** at `ncols=1`, and `ncols=1` is the condition that
makes the band need cutting. You need the grid to find the header and the header cut to get the grid.

### 8e. RE-RULED 2026-09-15 — build the both-ends refusal walk

The maintainer re-ruled after seeing 8a–8d: **build the both-ends refusal walk** (rules-free scope,
≥2-keep guard). The population-of-one price was already accepted in § 6 and is unchanged; what
changed is that the mechanism now demonstrably works.

**NOT BUILT. No spec, no plan, no code** — this session is at ~3x the originating floor and a spec
written here is a draft the next session re-derives. The build wants a cleared context.

**What the next session inherits, and it is more than § 6 gave:** the mechanism is no longer a
prediction. It is measured end to end — proposer, guard, scope, population, and page-scope effect.
What remains genuinely unbuilt is the *wiring*: where in `page_bands` the walk runs (the rules-free
branch at `compile.py:437-438` — the `if not sub_rules:` guard and the `bands.append(...)`
it protects, re-measured AFTER this sentence was written rather than before — which today
bypasses every peel), how the cut lines are carried
(`Band.captions` books **zero** tokens, and p4 b0 is currently ignored so its ink is unbooked either
way — but that must be re-checked, not inherited), and the regression pair
(`tests/etkl/test_continuation_licence.py`, `tests/etkl/test_logical_arithmetic.py`), whose fixtures
are ruled except `simple_table_pdf`.

**Reproduce 8b in four lines** — no fixture needed:

```python
import dataclasses
from iladub.etkl.compile import page_bands
from iladub.etkl.grid import infer_leaf_grid
P = "corpus/gov-stats/ons-index-of-services-2026-02.pdf"
b0 = page_bands(P, 4)[0]; L = list(b0.lines)
for nm, ls in [("full", L), ("T=1", L[:-1]), ("L=6", L[6:]), ("both", L[6:-1])]:
    print(nm, infer_leaf_grid(dataclasses.replace(b0, lines=tuple(ls))).ncols)
```
