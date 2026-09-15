# Handoff — R44 re-measured: the score rose 0.54 and repaired none of its three reasons

**Serves:** prog:criterion:etkl:05 — bfs. R44 gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-15. **Tree:** branch `r44-bfs-triage`, cut from `main` at `22a8264`.
**No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — R44's row is re-stated to what HEAD reads, and one of its figures was never right

Mechanical; the numbers are measured and in this loop's evidence § 5. At `22a8264`:

| reason | row (2026-08-04) | live | superseded | total |
| --- | --- | --- | --- | --- |
| ROUND_TRIP_FAIL | 5 | 1 | 4 | **5 — unmoved** |
| REGION_TILING_FAILED | 2 | 2 | 0 | **2 — unmoved** |
| KIND_NOT_SUPPORTED | 2 | 3 | 1 | **4** |
| DATAGRID_RESIDUE | 0 | 1 | 0 | **1 — new** |

Score `0.3438` → **`0.8850746268656716`**; `chains` 7 → 6; `RECORD_TABLE` asserting 8 → 7 (+2
superseded).

**The row's `KIND_NOT_SUPPORTED ×2` was wrong the day it was written.** The 2026-08-20 census and
bfs's own `cor:adjudication` both say **×3**, on the pages today's three live firings sit on. Two
independent sources contradicted the row for four weeks and nothing read them together.

### 5b. ASSERTED — do not read the score rise as progress on R44

The document went from `0.3438` to `0.8851` and **every one of R44's three reasons still stands.**
The rise is R225's D2 moving page 5's ink into an adopted grid; four ROUND_TRIP_FAIL firings went
from *escalated* to *superseded* — concealed, not repaired — and adoption added a DATAGRID_RESIDUE
of its own. A count of live firings alone reports this as a fix. It is not one.

This is the concrete vindication of the 2026-08-20 refusal to pin a `cor:scoreFloor` on bfs:
*"nothing in the vocabulary stops a floor being pinned at 0.3438 and this document being called met
without one glyph of it being read correctly."* Had a floor been pinned then, `etkl:05` would now
look 0.54 closer to met with the same three defects intact.

### 5c. PROPOSED — the next BUILD subject is probably p5's round-trip mechanism, and this loop did not test that

**Rests on a judgement this loop did not measure.** ROUND_TRIP_FAIL is the largest single component
(5 of 12 reason-bearing regions), it is confined to **one page** and **one mechanism**
(region-level, `holon.py:536`/`:545` — *not* the cell-level emitter at `:59`–`:95`, which the corpus
never reaches), which makes it the most bounded of the three surfaces.

**Why it may be wrong, stated before anyone builds it:** four of the five are superseded, so it is
unmeasured whether repairing the mechanism changes any *asserted* output at all — adoption may
already be carrying that ink correctly, in which case the repair moves a verdict and not a reading.
**Measure that first:** with p5's adoption suppressed, do the four superseded regions return as live
ROUND_TRIP_FAIL, and does the adopted grid's reading of those rows agree with what the round-trip
check rejects? If adoption already reads them correctly, R44's round-trip half is a *reporting*
defect, not a reading defect, and the remedy is a different class entirely.

### 5d. ASSERTED — what NOT to do

- **Do not pin a `cor:scoreFloor` for bfs.** The 2026-08-20 hold stands and this loop strengthens
  its reasoning.
- **Do not count live firings alone** on any document where adoption fires. bfs is the corpus's
  only document carrying live and withdrawn escalations at once (2026-09-14 decision census).
- **Do not trust any `file:line` in the `tab` rung's criteria statements** — all ten are stale
  ([[R236]]) — **nor their `FIRES n` counts**, all five of which are stale and two of which name
  the wrong document set ([[R237]]). In particular, do not plan `tab:07` around bfs: 4 of its 7
  live firings are on ons, which its comment does not mention.
- **Do not treat the three reasons as one problem.** They share no root cause; that is this loop's
  triage answer, and it is what R44's closure column asked for.

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-15-r44-bfs-triage-evidence.md` (§ 2 the control's own
  failure, § 3 the score ladder, § 4 the citation finding, § 5 the tally and the triage answer,
  § 6 what this loop got wrong first).
- **The instrument** — `scripts/bfs_reason_triage.py`. Carries its control inline; exits non-zero
  if the control fails. One command:
  `PYTHONPATH=src:. .venv/bin/python scripts/bfs_reason_triage.py`.
- **The only prior census** — `docs/superpowers/2026-08-20-escalation-reason-census.md`, the sole
  source for every figure on R44's row.
- **bfs's adjudication** — `tests/corpus-manifest.ttl:111-122` (HOLD, no floor); its reading ladder
  at `:244-272`.
- **The rows** — [[R44]] open in `residues-open.md`; [[R236]] raised by this loop.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| R44's three reasons share no root cause | evidence § 5, R44's row |
| ROUND_TRIP_FAIL is unmoved at 5 — 4 concealed by adoption | evidence § 5 |
| The row's `KIND_NOT_SUPPORTED ×2` was always wrong; it is 3 | evidence § 5, R44's row |
| The score rise repaired nothing | this § 5b, evidence § 5 |
| All ten `tab` criteria citations are stale | evidence § 4, [[R236]] |
| All five `tab` `FIRES n` counts are stale; two name the wrong documents | evidence § 7, [[R237]] |
| No lint proposed for citation correctness, per [[R188]] | evidence § 4 |
| **What to build for R44** | **UNDECIDED — a § 8 classification, the maintainer's** |

## 3. Unverified or assumed

- **§ 5c entirely** — that p5's round-trip mechanism is the next build, and that repairing it
  changes any asserted output.
- **Two row figures are unreconciled**: `RECORD_TABLE` 8 vs today's 7+2, and `chains` 7 vs 6. The
  chain fall is attributed to D2 by a 2026-09-14 measurement; the RECORD_TABLE count is explained
  by nothing measured here.
- ~~This is one document; whether the other six carry stale reason counts is unmeasured.~~
  **MEASURED after this bullet was written** — see evidence § 7 and [[R237]]. All five `FIRES n`
  counts on the `tab` rung are stale and two name the wrong document set. The measurement came from
  a whole-corpus snapshot this loop produced *by accident* and read before deleting; it was not
  planned work, and the bullet is struck rather than silently rewritten.
- **`superseded` is still unexplained** in the general case — fourth loop carrying this thread.
- **The citation census covers the `tab` rung only.** Other rungs' statements were not checked.

## 4. What this session did, and what it cost

Chose the subject from the arc's ready set on the maintainer's ruling, re-measured R44's premise,
found four of its five figures stale or wrong, produced the triage its closure column asked for,
and raised one new row. Built no remedy, edited no shipped file.

**The cost worth carrying: this loop's own instrument told it good news, and a second instrument
refuted it.** The first tally counted `verdict == "escalated"` alone and printed
`ROUND_TRIP_FAIL 5 → 1` — four failures apparently fixed. The shipped oracle's region dump showed
them alive as `superseded`. That is the previous loop's repair #4 — *a positive result is not
self-interpreting* — recurring in the very next loop, written by someone who had just read it.

**And the control caught the other one.** Its score leg was pinned to a literal `0.4033`, which was
two readings stale, so a correct measurement failed its own control. The repair — read the
manifest's `cor:reading` log instead — is the same lesson the register learned about rows: *a figure
carries its date, and a figure that does not is a defect waiting for a reader.*
