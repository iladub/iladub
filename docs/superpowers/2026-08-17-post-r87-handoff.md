# Handoff — after R87, and after the branch sweep

**Date:** 2026-08-17
**Branch:** `main`, HEAD `540e608`, in sync with `origin/main`, tree clean

**Why this exists:** the session that produced it ran to ~420K tokens, far past the 150K
executing floor and 8× the 50K originating floor. Two new tasks (integration, then the
branch sweep) were started above the floor when they should have been handed off. Nothing
below is known to be wrong — but it was written late in a long session, which is exactly
the condition the floors exist for, so verify rather than trust.

## Goal

R87 is closed and merged. What remains is small, unstarted, and independent: four stale
documents, six parked branches awaiting a keep/delete decision, and four new residues.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `540e608` (merge of PR #105) | The whole R87 loop on `main`, as six task commits `1d3ed83`..`c7c08ec`. Each commit message IS its task report — measurements, deviations, falsification tables. |
| https://github.com/iladub/iladub/pull/105 | The PR description: what shipped, the oracles, the test evidence table. |
| `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md` | The plan all six tasks executed. G1–G7 and §7 still bind on any follow-up. |
| `tests/etkl/test_vacuity_registry.py` | The guard, its 9-row registry, and — in the module docstring — the deviation from the plan's criterion 2 and the measurement that forced it. |
| `docs/superpowers/residues-open.md` | R97, R98, R99, R100, raised by this loop. R98 CORRECTS spec §3. |
| `scratchpad/branch-audit.md` (session scratchpad, NOT committed) | The branch classification. **Ephemeral — regenerate rather than cite.** |

## What was decided, and where each decision is recorded

1. **The derivation runs at document scope; the page leg is deliberately unfurnished.**
   Recorded in `358c1bb` and in `document.py`'s call-site comment.
2. **`escalation-shapes.ttl` is in the COMPILE membrane only**, not grounding. Recorded in
   `e3073e5` and in `compile.py:398-417`.
3. **Criterion 2 is TERM REACHABILITY, not the plan's "non-negated patterns bind ≥1 row".**
   The plan's wording, implemented literally, reports three HEALTHY shapes as vacuous.
   Recorded in `3c28458` and in the test module's docstring.
4. **The engine record was corrected**: `engine_name()` returns `rudof` here, so every
   figure in this loop is the rudof leg. Recorded in `e3073e5`. Earlier commits on the
   branch say the reverse and are superseded on that point.
5. **History was rewritten** 12 implementation commits → 6, content byte-identical.
   Original preserved at local ref `backup/loop-escalation-2026-08-17`. Recorded nowhere
   but here and in that ref.
6. **28 branches deleted** (7 local, 21 remote), each re-verified as an ancestor of
   `origin/main` at delete time. Recorded nowhere but here.

## Unverified or assumed

* **Six parked branches were kept without adjudication** — nobody decided they are worth
  keeping; they were kept because deleting them destroys work and that call is the
  maintainer's. Five are LOCAL-ONLY (no remote copy):
  `archive/unify-extraction-sp3d` (7 files nowhere else), `maritime-voyage-design`
  (commit subject says "planning, local-only"), `iladub-zero-etl-showcase` (tip is "final
  review"), `iladub-rule-column-refinement` (3 of 5 patches already upstream, 2 unique —
  the most recently active), `aggregation-evidence` (spec+plan only, no feat/test).
  `semantic-architecture` has a remote copy and 16 of 37 files still differing from main.
* **Four handoff documents in `docs/superpowers/` are STALE AND READ AS CURRENT.**
  `2026-08-15-r87-task3-handoff.md` says the batteries have not run; they have.
  `2026-08-16-r87-task4-handoff.md` and `2026-08-16-r87-task5-handoff.md` describe work
  that is now finished; the latter says the session stops at Task 5, and it did not. This
  repo already learned this failure mode — `residues.md` records that stale rows "were
  consumed as fact and cost real sessions".
* **The pySHACL leg was run once, green, at `d1e5ab1`'s tree.** It has never run against
  `540e608` (which differs only in docs).
* **The vacuity registry measures DOCUMENT graphs only** — R100. A shape idle on one
  membrane leg and live on the other is invisible to the guard.
* **Term reachability does not catch an impossible JOIN** whose terms are all present.
  Stated in the test module; R87's class is term-absence.
* **`backup/loop-escalation-2026-08-17` is the only copy of the pre-rewrite commits.**
  Their files are all on `main`; their commit objects are not. Safe to delete once you are
  satisfied with the rewritten history.

## The next concrete action

Mark the four stale handoffs superseded — a `**SUPERSEDED 2026-08-17 by <what>**` line at
the top of each, not deletion; they are honest records of what was known when written, and
this register's own convention is strike-and-keep. It is a single small commit on `main`
and it removes the one hazard this session created that is not recorded anywhere else.

Then, separately and only with the maintainer: the six parked branches.
