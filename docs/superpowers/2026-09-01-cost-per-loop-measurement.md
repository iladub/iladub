# Measurement — cost per loop, the census's missing denominator

**Doc impact: none.**

`docs/superpowers/2026-09-01-progress-census-handoff.md` §5 blocks its whole menu on one figure that
was never measured: *how much of a session each loop consumed.* Its words, quoted, because the
reading of every other figure in that census turns on them:

> 20 cheap loops with one win is a healthy exploration rate, and 20 expensive ones is the problem the
> maintainer is describing. **Measure cost-per-loop before ranking any remedy below.** If the loops
> are cheap, candidate D is the answer and A–C are premature.

This file is that measurement, and nothing else. It ranks no remedy.

## The instrument

`plimslop` writes one `turn` record per turn to `~/.claude/plimslop/corpus.jsonl`, carrying the
figure the API reports (`input + cache_read + cache_creation`), the session's baseline, and whether
compaction dropped anything. **A loop is a session** (`CLAUDE.md` § Loop & context hygiene), so
per-session is per-loop.

Working tokens are computed exactly as the gate computes them — `peak tokens − session baseline`,
with `dropped` added back:

```python
working = max(r["tokens"] for r in session_turns) - session_turns[0]["baseline"] + max_dropped
```

Corpus at time of measurement: 607 `turn` records total, **554 of them for this project**, over 62
iladub sessions, 2026-08-15 → 2026-09-01. **No record exists before 2026-08-15**, which is when
`plimslop` began logging — the same limitation the score series has at 2026-08-04.

## The figures

| window | sessions | median working | mean | max | ≥ 50K (originating floor) | ≥ 150K (executing floor) |
| --- | --- | --- | --- | --- | --- | --- |
| census window 2026-08-26 → 09-01 | 19 | **122,419** | 138,662 | 270,265 | **18 / 19** | **8 / 19** |
| prior window 2026-08-15 → 08-25 | 43 | 138,579 | 152,744 | 400,006 | 43 / 43 | 18 / 43 |
| all recorded | 62 | 132,864 | 148,428 | 400,006 | 61 / 62 | 26 / 62 |

**Total spend in the 7-day census window: 2,634,594 working tokens across 19 sessions.**

The two windows are not materially different — median 122K against 139K. **Cost per loop did not
rise over the period the maintainer is concerned about; it was always this.** What changed is the
yield: the census's §3.2 puts cbh's +0.839 and ons's +0.530 before 2026-08-20 and finds exactly one
genuine capability gain (R45) in the twelve days to 2026-09-01.

## Attribution to production change — DIRECTIONAL, not exact

Sessions were mapped to commits by timestamp containment, and each session's commits classified by
whether they touched `src/`, `vocab/` or `scripts/` (merge-aware, `git diff-tree -m --first-parent`):

| | working tokens |
| --- | --- |
| sessions that landed production code | 802,507 |
| sessions that landed none | 1,832,087 |

**This split is soft and must not be quoted as exact.** Timestamp containment misattributes any
session that does its work one evening and merges the next morning, and at least two boundary cases
are visible in the raw table (`8de2b34f` ends 14:08Z; PR #145 merged 14:08:53Z). The robust claim is
the direction — the larger share of the window's tokens sat in sessions that landed no compiler
change — not the ratio.

## What this settles, and what it does not

**Candidate D is REFUTED on the census's own criterion.** D held that "nothing is wrong except the
accounting" and staked itself explicitly on the loops being cheap. The median loop costs 122,419
working tokens; **every session but one crossed the originating floor, and 8 of 19 crossed the
executing floor.** These are not cheap loops.

**It settles nothing about A, B or C**, which is the whole point of measuring before ranking. It does
supply one fact those candidates should be read against: the median loop performs its spec, plan and
design work at **2.4× the floor** this repo's own ruling
(`docs/superpowers/2026-08-26-context-regime-ruling.md`) says multi-step reasoning is compromised
past, and `plimslop reader override` reports the working-unit gate passed **27/59 = 46%** of the time.

## Unverified or assumed

- **The floors are asserted, not proven.** `CLAUDE.md` says so and `tiers.py` labels the 150K
  `NO SOURCE`. "2.4× the floor" inherits that weakness entirely — it is a ratio against an asserted
  number, not a measured harm.
- **Peak-minus-baseline is one choice of cost and not the only defensible one.** It is chosen because
  it is what the gate itself measures, so the figure and the floor are commensurable. Total tokens
  processed across a session would be a larger and differently-shaped number.
- **Session ≠ loop exactly.** `CLAUDE.md` rules that a loop is a session, but the raw table shows
  sessions that are plainly fragments (`a883793c`, 3 turns, 33,642) and sessions spanning a day
  (`9f3ce39f`, 27 turns, 2026-08-30 → 08-31). 19 sessions in a window the census called 20 PRs is a
  coincidence of counting, not a mapping.
- **The 11-of-59 caveat `plimslop reader override` prints** — records whose session was inferred and
  which logged no turn afterwards, the `/clear` signature — applies to the override rate quoted
  above, not to the working figures in the table.
- **Nothing here is pinned by a test.** The two scripts were written for this measurement and are not
  committed; the corpus is outside this repo and is not versioned with it. Re-deriving the table is a
  fresh session's cheap check, and the corpus will have grown by then.
