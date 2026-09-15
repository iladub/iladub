# Handoff — R234's lockout has a population of zero; it is not to be built, and not to be parked

**Serves:** prog:criterion:etkl:04 — ONS. The criterion is unmet and R234 is no longer its route.

**Date:** 2026-09-15. **Tree:** branch `r234-lockout-population`, cut from `main` at `024fd0d`.
**No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — nothing is to be built for R234, and it is NOT parked

Two maintainer rulings were taken this session, in this order, and both are recorded in the row:

1. **Park R234** — on the measurement that its lockout fires on **zero** natural bands.
2. **Re-resolved: leave R234 open and unparked** — because ruling 1 collided with CLAUDE.md's own
   parking precondition (§ 5c), and the maintainer chose not to break the rule to satisfy it.

So R234 is **open, unparked, unbuilt**, with `population zero` on its row. This is mechanical:
there is nothing to construct, and the next loop must not inherit R234 as a subject by default.

**The remedy is still unclassified, and that is now moot unless the population changes.** A
mechanism for one specimen — reachable only through the `(2,1)` cut that [[R232]]'s ruling refused —
is not justified by this measurement. If a later corpus document lands a second specimen, the § 8
classification question re-opens with a real denominator; the four options as framed are in this
loop's evidence § 6 and in the register row.

### 5b. PROPOSED — the substantive successor is probably [[R166]], and this loop did not verify it

**Rests on a judgement this loop did not test.** etkl:04's subject is **column identity**, and
[[R166]] *is* that class — the in-degree-10 hub of the register's largest component, with **five
donor-less bands** still asserting a data row as their column header after grid and span donation
repaired six. That makes it the obvious successor for the same criterion.

**Why it may be wrong:** whether R166 is *actionable* is unmeasured here. Its row records that
**no in-band signal can separate** a header row from a data row on those five bands (type contrast
0/12; the blank corner impossible by construction, twice over), and the two repairs that did land
both needed a **donor on the same page** — which those five do not have. So R166 may be blocked for
the same structural reason R234 turned out to be cheap to dismiss. **Measure that before planning
anything**, and pick the subject from the strip's `ready` set (8 rows) rather than from this
sentence.

### 5c. ASSERTED — the parking rule's two halves are enforced unequally (recorded, not raised)

Measured while applying ruling 1:

- `scripts/residue_graph.py --candidates` = open ∧ in no criterion's `prog:blockedBy` ∧ **no OPEN
  neighbour in either link direction** (`residue_graph.py:62-73`, *"Computed, never decided"*).
- R234 has three open neighbours ([[R166]], [[R226]], [[R232]]) → refused. 90 candidates,
  R234 absent. `parked 0` — **no row has ever been parked**, so there is no format precedent in
  the repo; the format lives only in CLAUDE.md prose.
- **Only M21 is CI-enforced** (`tests/test_arc_manifest.py:707`,
  `test_m21_a_blocking_edge_to_a_parked_residue_is_refused`): a criterion may not be
  `prog:blockedBy` a parked row. That half was **satisfied** for R234 (no criterion blocks on it).
  The open-neighbour half has **no test**.
- So parking R234 would have **passed CI while breaking CLAUDE.md's written "only"**. The
  maintainer resolved it by not parking.

**No row is raised for this, deliberately.** A lint for the open-neighbour half would fire on zero
on the day it shipped (`parked 0`), which is precisely what [[R188]] ruled against. It is recorded
here so the next maintainer triage knows the asymmetry exists before it parks anything.

### 5d. ASSERTED — what NOT to do

- **Do not build a multi-line boxhead reader, widen `merge_tiling_ok`, or touch
  `header_body_split`** for R234. Population zero; both rulings say no.
- **Do not loosen `group_wrapped`'s gap test.** Unchanged from the previous loop and now with a
  named live population: the three graincorp bands at `2.3e-05 pt` ARE what `<=` would re-admit.
- **Do not park any row without re-running `--candidates`** — and note that CI will not stop you.
- **Do not re-run this census expecting more.** Its limits are in evidence § 7.

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-15-r234-lockout-population-evidence.md` (§ 1 the proxy,
  § 2 the control, § 3 the tally, § 4 the three-way margin split, § 5 the validation).
- **The instrument** — `scripts/r234_lockout_census.py`. Carries its control inline; exits
  non-zero if the control fails. One command: `PYTHONPATH=. .venv/bin/python scripts/r234_lockout_census.py`.
- **R234's prior evidence** — `2026-09-15-r234-boxhead-measured-evidence.md` (the lockout chain).
- **The order this loop executed** — `2026-09-15-repair-plan-next-loop-handoff.md` § 5b.
- **The row** — [[R234]] open (unparked) in `residues-open.md`; index line in `residues.md`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The lockout fires on 0 natural bands at exact equality | evidence § 3, R234's row |
| § 5b's proxy was settled without the disputed quantity | evidence § 1 |
| The instrument agrees with R208's shipped probe | evidence § 5 |
| R208 spec § 7's table is incomplete; its § 4(a) conclusion stands | evidence § 5, not a new row |
| **Park R234** (maintainer, ruling 1) | this § 5a, R234's row |
| **Re-resolved: leave R234 open, unparked** (maintainer, ruling 2) | this § 5a + § 5c, R234's row |
| No lint for the open-neighbour half, per R188 | this § 5c |

## 3. Unverified or assumed

- **§ 5b entirely** — that [[R166]] is the successor, and that it is actionable at all.
- **"Zero at exact equality" is this corpus** — 7 documents, 191 bands. Absence here, not evidence
  of absence, the same limit [[R208]] § 4(a) states about its own null.
- **The three-way margin classification is prose**, not a computed verdict (evidence § 4). The
  margins are computed; calling `2.3e-05` sub-precision and `9.35e-01` a row is a reading.
- **`superseded` is still unexplained** — third loop carrying this. The band escalates on its own,
  yet document-scope reporting showed region 0 `superseded` with 0 cells. Never traced.
- **Whether R208 spec § 7's omission was a filter or an oversight** is not established; only that
  its own probe reports candidates the table lacks.

## 4. What this session did, and what it cost

Ran the ordered § 5b census after first settling its proxy; got **population zero**; validated the
instrument against R208's own probe; put the § 8 classification to the maintainer, who ruled *park*;
found that ruling refused by the register's own gate; put the conflict back, and the maintainer ruled
*leave open*. Built no remedy, edited no shipped file.

**The cost worth carrying: I was wrong twice about the same nine bands, in opposite directions, and
both times from a formatting choice rather than a logic error.** First I read `exact=[]` as "these
are plainly rows, correctly refused" — wrong. Then, seeing margins print `0.0`, the reverse. Both
came from **rounding the margin to 2 decimal places**, which collapses R208's `2.3e-05` residual and
a genuine `9.35e-01` row boundary into the same displayed value. Full precision separated three
distinct classes immediately. *A rounded number is an instrument, and 2dp was the wrong one.*

A second, smaller one: the first plimslop preflight was logged in the **wrong unit** — 95,000 as a
total-window figure against a floor CLAUDE.md measures on `working = tokens − baseline`, recording a
spurious OVERRIDE. Re-logged at 49,000 with a note naming the correction.
