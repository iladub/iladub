# Handoff — the census is measured; the plan is still the next act

**Topic:** process · **Date:** 2026-08-20 · **Branch:** none yet (start from `main` @ `820ab24`) ·
**Shape: originating** · **Status: SEAMS 1 AND 2 MEASURED. PLAN NOT WRITTEN.**

> Written at 99,149 tokens — 2× the originating floor. The corpus run is what spent it, and it is
> spent well: the expensive seam is now a tracked measurement the plan session can cite instead of
> re-run. Preflight logged (`stop`).

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable
denominator and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` (584 lines) | **the spec. Still the thing to read first and in full.** §7 carries the denominators, §9 what is NOT built, §11 the seven seams |
| `docs/superpowers/2026-08-20-escalation-reason-census.md` | **NEW, written this session.** Seams 1 and 2, measured. Three findings that change §7.4 — read § *What this does to the spec* |
| `docs/superpowers/2026-08-20-the-arc-has-a-denominator-handoff.md` | the previous handoff. Its § *Where the primaries are* table is still the right map; its § *Unverified* is now partly discharged (see below) |
| `tests/corpus-manifest.ttl` | the six `cor:Unadjudicated` documents the census exists to adjudicate; `:16-20` is the HOLD encoding |
| `tests/etkl/test_vacuity_registry.py:65-105` | `VACUITY_REGISTRY` — measured this session: **9 rows, 5 of them `tab:`**, of which `LicenceRefusalShape` carries a real adjudication in prose and **4 carry "not adjudicated here"**. §7.4's "the four rows" is correct |

## What was decided, and where that decision is recorded

**Nothing was decided this session.** Three *measurements* landed that the plan must act on, all
recorded in the census document with their commands and outputs inline:

1. **There are NINE escalation reasons, not eight.** `TRANSPOSED` is misfiled in spec §7.4 as a kind;
   `compile.py:688` passes it to `escalate_region`, and `RegionKind` (`regions.py:27-30`) has exactly
   three members, none of them `TRANSPOSED`. **`tab`'s denominator is 10, not 9.** The spec is wrong
   here and the plan corrects it — §7.4 itself instructed the plan to re-measure rather than copy,
   which is the instruction that caught it.
2. **Four of the nine reasons never fire on the corpus** — `MERGE_AMBIGUOUS`,
   `MULTI_TABLE_AMBIGUOUS`, `ROW_GROUP_AMBIGUOUS`, `TRANSPOSED`. Under §7.4's two-armed criterion
   (*does not fire, **or** every occurrence adjudicated*) those four read **met**, which would put
   4 of 10 `tab` criteria in the numerator for a reason that measures the corpus, not the reading.
   **This is the plan's hardest open question** and it is a §8-class gameability risk of the same
   family as the `etkl` floor defect `820ab24` just fixed. The census names a candidate form —
   the vacuity registry's *fires-and-adjudicated **or** registered-idle-with-a-reason* — but
   **choosing it is the plan's call, not this session's.**
3. **Graph-side 24 vs report-side 29**, reconciling exactly on apple p1's five withdrawn escalations.
   A SHACL membrane sees only the graph-side 24. The plan states which side the manifest counts.

## Discharged from the previous handoff's "unverified"

- **`tab`'s numerator is no longer unmeasured.** The full table is in the census document.
- **The ~5.5-minute corpus run is spent** — 315.3 s total, no crash, no `BUDGET_S` overrun (longest
  single document: graincorp-stem at 162 s). **A plan session does not need to re-run it**; if it
  wants to, the runner is `./.venv/bin/python` and the trap in the previous handoff still applies.
- **Register tally re-confirmed** for §10 repair 1: `grep -cE '^\| ~?~?R[0-9]+'` → 73 open + 21
  closed = 94 rows. `residues.md:40`'s "20 closed" is still wrong.

## Unverified or assumed

- **The six `etkl` adjudications are NOT written.** The census is the *evidence* they need, not the
  adjudications themselves. They are still the plan session's job, on the maintainer's 2026-08-20
  call, and the expected outcome is still five or six recorded HOLDs. **Do not pin a `cor:scoreFloor`
  at a measured score to move the fraction** — spec §7.1 and §8 refuse it.
- **Seams 3, 4, 5, 6 and 7 are unmeasured** — `prog:declaredOn` per criterion (git blame), every
  `prog:oracleTest` resolving under `--collect-only`, multi-line `statusLine`, the residue→residue
  backfill set, and whether liveness is a `dec` criterion. Seam 6 has a first cut only (73/21 row
  counts), not the backfill set itself.
- **`ROUND_TRIP_FAIL` is two mechanisms under one label** — region-level (`holon.py:493`, all 5
  corpus firings) and cell-level (`_emit_roundtrip_fail_cell`, `holon.py:55`, corpus-dead). Whether
  the manifest should distinguish them is unexamined.
- **graincorp-stem's manifest adjudication is stale** — its 2026-08-02 note describes page-1/2
  `REGION_TILING_FAILED` escalations that do not survive at HEAD (it escalates nothing now). Whether
  that is a repair this loop makes, or a residue, is undecided.
- **`docs/superpowers/2026-08-20-escalation-reason-census.md` is UNTRACKED** as of this handoff, as
  is this file. Nothing else in the working tree changed.

## The next concrete action

In a **fresh session**: write the plan from the spec, reading the census document alongside §7.4 —
and open by deciding finding 2 (what a corpus-dead reason's criterion says), because it sets the
`tab` denominator and every row under it.
