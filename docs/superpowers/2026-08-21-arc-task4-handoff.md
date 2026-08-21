# Handoff — Task 4 complete pending re-review; Tasks 5-8 unstarted

**Topic:** process · **Date:** 2026-08-21 · **Branch:** `arc-denominator` @ `fabfa0e` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASKS 1, 2, 3, 4 COMPLETE AND SIGNED
OFF** (Task 4 after two fix rounds). **TASKS 5-8 NOT STARTED.**

> Written at ~123k tokens, under the 150k executing floor, while still accurate. The controller seat is
> what needs the fresh session; implementer and reviewer seats are already fresh subagents.

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable denominator
and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

**As of `fabfa0e` the strip reads `etkl 1/7  dec 11/17  holon 4/6  substrate 0/3  tab ?`.** Task 6
replaces the last `?`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST.** Rulings 1-12, every deferred minor, the pre-flight scan. Git-ignored: `git clean -fdx` destroys it |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — the **binding authority**. Conflicts resolve against it, not against the plan |
| `docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md` | the plan, 8 tasks. **Four of its load-bearing claims are now known dead** — see below |
| `.superpowers/sdd/.../task-N-report.md` | what each task actually built, its TDD evidence and its FALSIFICATION block |
| `docs/superpowers/2026-08-20-arc-task3-handoff.md` | the previous handoff. Still current on Rulings 1-11 and the worktree suite recipe |

## What this session decided

**Ruling 12 — the sixteenth shape is counted; `dec` is 17 criteria, not 16.** The implementer measured
**16** node shapes where the spec said 15, and excluded `iladub:HgaGroundingGovernanceShape` because
that artifact already backs `prog:criterion:holon:03`/`:04`. Overturned: **the arc's rungs partition
declaring prose, not artifacts.** `holon:03`'s `prog:source` is `docs/holonic-interaction.md:151-153`,
a different rule in a different document asking whether the shape's *invariant* is built; a `dec`
pairing criterion asks whether that shape *ships a conforming example and a negative test*. CLAUDE.md:252
ranges over *"every vocabulary/shape"*, so exempting one is a curation rule the prose does not contain —
and **a curated denominator is the same defect as a fabricated numerator** (Global Constraint 6 from the
other side). Cost if wrong: one artifact underwrites criteria on two rungs, so overlapping evidence
could read as independent progress; mitigated by requiring the row to disclose the overlap, and
reversible by deleting one criterion.

**This ruling generalises, and Tasks 6-8 should apply it without re-litigating:** *a criterion is
counted where its declaring prose lives; two rungs measuring one artifact under two rules is the
design, not double-counting.*

## The plan's dead claims — now four

Tasks 2, 3 and 4 each found one. **Every remaining dispatch must carry "your run wins."**

1. Task 2's register repairs were already done (Ruling 9).
2. The criterion IRI scheme `urn:iladub:arc:crit:…` is refused by the shipped membrane; the live form
   is **`prog:criterion:<rung>:<nn>`** (Ruling 11). **Tasks 6, 7 and 8 must each be told this.**
3. The brief's *"all fifteen are `retrospective false`"* is dead — two `dec` criteria measure
   `metOn == declaredOn`, which M4 refuses at `false`. Transcribing the brief would have gone red.
4. The brief's `git log -L 249,251:CLAUDE.md` evidence is wrong as stated (4 commits, 2 of them
   adjacent-bullet context), though its conclusion holds.

## Unverified or assumed

- **Task 4 is closed clean at `6f11d13..fabfa0e`, after two fix rounds.** Round 1's re-review verified
  Ruling 12 (a)-(d) independently but found part (e) incomplete: **fix round 1's own diff falsified
  three counts in the manifest's prose** (`:518`, `:528`, `:549`), which were true at `5367dcf`. Round
  2 fixed them, prose-only — proved by `git diff … | grep '^[+-]' | grep -v '^[+-]#'` returning empty.
  **Ruling 12's premise was independently re-derived at that last gate**: the re-reviewer parsed
  `vocab/shapes/*.ttl` itself and counted **16** `sh:NodeShape` subjects across the four namespaces.
  The spec's 15 was wrong; three independent measurements now agree on 16.
- **No suite leg covers Task 4's commits** (`5367dcf`, `674d16f`, `fabfa0e`). Task 4 touched only
  `tests/arc-manifest.ttl`, and round 2 only comments within it — but re-run both legs at the head you
  inherit before the whole-branch review.
- **Both suite legs are GREEN at `6f11d13`** — non-corpus **1216 passed, 7 skipped, 1 xfailed, 10
  warnings (18m02s)**, exactly +1 on `93234cb`; corpus **43 passed (17m25s)**, matching Tasks 1 and 3
  exactly. This is the first full-suite coverage of the Task 3 fix commit `001014e`. **No leg covers
  `5367dcf` or `674d16f` (Task 4);** re-run both in the worktree at the head you inherit (recipe in the
  previous handoff; `baml_client` + `corpus` must be symlinked in or six modules fail to collect and
  the run is a FALSE RED).
- **The ten warnings are explained and are NOT this branch's** — eight are one rdflib JSON-LD
  `ConjunctiveGraph is deprecated` warning raised from `tests/test_fluree_policy.py` and
  `tests/test_writegate.py`, two from a docgov serialization. No `arc_*` test appears in the summary.
  Capture note: `tail -20` truncates the warnings block; use `tail -40`.
- **A bug class, and the rule that catches it has no oracle.** Task 4's criterion 10 shipped a
  **vacuous positive** at `5367dcf` — it cited a graph with zero focus nodes for the shape it claimed —
  and the implementer's own non-vacuity check missed it *by counting over a wider file set than the row
  cited*. The fix generalises the rule to "counts are taken over exactly the files each criterion
  cites", and the re-reviewer then ran that rule over **all ten** other met-true `dec` rows: every one
  is >= 1, so **the bug class is confined to that single row**. **But the rule is prose enforced by
  nothing** — reverting criterion 10 to the vacuous citation still yields `shacl_ok=True`, so the
  membrane admits a vacuous positive silently. This is the closest thing this loop has produced to a
  false `met true`, and it is unguarded. **Strong candidate for a new refusal (M11) or a residue row —
  whole-branch review owns it.** Tasks 5 and 6 author more rows: hold them to the rule by hand.
- **The `prog:source` VALUE is still unverified by anything** — the membrane requires the field but
  checks neither that the path exists nor that the line is in range. Candidate **M10**, declined twice
  as new scope. Task 5's `corpus-manifest.ttl` inserts can silently stale `etkl:02-07`'s pointers.
- **The pre-flight conflict scan is still not independent** — the plan's author scanned it. It has now
  missed four dead claims.
- **Fourteen deferred Minors from Tasks 1, 3 and 4** are in the ledger, untouched, pointed at the final
  whole-branch review.
- **Nothing on this branch is pushed.** `main` is pushed at `f436a8c`.

## The next concrete action

In a **fresh session**: read the ledger, confirm Task 4's re-review verdict, then **dispatch Task 5**
(the corpus adjudication pass — six documents, six recorded HOLDs). Its brief is not yet extracted; run
`scripts/task-brief <plan> 5`. Carry into the dispatch: the **"your run wins"** clause; the pre-flight
scan's row that **T5 must re-verify T3's asserted `etkl` booleans** equal the ones it computes from
`corpus-manifest.ttl`; the **`prog:source` staleness hazard** above; Global Constraint 7 (*never lower a
bar to meet it* — this is the task where a `cor:scoreFloor` could be pinned at a currently-measured
score, and the spec calls that out by name); and the suite do-not-run with the worktree recipe as the
reason.
