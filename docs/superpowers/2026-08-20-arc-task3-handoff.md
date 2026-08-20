# Handoff — Tasks 1-3 shipped; Tasks 4-8 unstarted

**Topic:** process · **Date:** 2026-08-20 · **Branch:** `arc-denominator` @ `001014e` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASKS 1, 2, 3 COMPLETE AND SIGNED
OFF. TASKS 4-8 NOT STARTED.**

> Written at ~136k tokens, under the 150k executing floor, while still accurate. The controller seat
> is what needs the fresh session; implementer and reviewer seats are already fresh subagents.

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable denominator
and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

**As of `001014e` the strip reads `etkl 1/7  holon 4/6  substrate 0/3  dec ?  tab ?`.** Tasks 4 and 6
replace the two `?`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST.** Rulings 1-11, every deferred minor, the pre-flight scan. Git-ignored: `git clean -fdx` destroys it |
| `docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md` (committed `f436a8c`) | the plan, 8 tasks. **Two of its load-bearing claims are now known dead** — see § What was decided |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — the **binding authority**. Conflicts resolve against it, not against the plan |
| `.superpowers/sdd/.../task-N-report.md` | what each task actually built, its TDD evidence and its FALSIFICATION block |
| `docs/superpowers/2026-08-20-arc-task1-done-handoff.md` | the previous handoff. Still current on Rulings 1-8 and the suite trap; superseded on the suite *workaround* (see below) |

## What was decided, and where that decision is recorded

**In the ledger, and nowhere else — reversible.** Rulings 1-8 are described in the previous handoff.
New this session:

- **Ruling 9** — the plan's Task 2 was 7/8 already-done work: both register repairs had landed in
  slice 1 (`3b36609`) **2h24m before the plan was written**. No corrective action. Recorded because
  it is the second instance of one authoring failure — a load-bearing claim about a file asserted
  from an earlier reading rather than re-measured. Every remaining dispatch carries "your run wins".
- **Ruling 10** — the `prog:source` Important finding went to a **Task 3 fix round**, not a new task,
  and had to land before Task 4. Done: `001014e`. Re-review was in flight when this was written.
- **Ruling 11** — **the plan's criterion IRI form is dead on arrival.** The plan says
  `urn:iladub:arc:crit:<rung>:<nn>` (`plan:257`, `:283`); Task 1's shipped M9b
  (`tests/arc-shapes.ttl:129-136`) refuses it outright. The live scheme is
  **`prog:criterion:<rung>:<nn>`**, convention at `arc-manifest.ttl:28-32`. **Tasks 4, 6, 7 and 8 must
  each be told this**, or they author a manifest section the membrane refuses.

**Carried interfaces that exist only in the ledger:**

- **Task 8** — criterion IRIs now also appear in *object* position and in a comment. All 16 subject
  occurrences are line-anchored, so Task 8's rdflib-free reader **must anchor its regex at line
  start**. Also still unapplied: **Ruling 2** (update
  `test_the_strip_never_raises_when_its_sources_are_missing`'s monkeypatch list when `cockpit.ARC`
  becomes `ARC_MANIFEST`, or that test passes while patching nothing).
- **Task 5** — the fix round's own closing concern: `prog:source` is now *required* but still
  *unverified* — nothing checks the path exists or the line is in range, so Task 5's
  `corpus-manifest.ttl` inserts can silently stale `etkl:02-07`'s pointers. The implementer named
  M10 (an environment-leg check) as the candidate and declined it as new scope.
- **Task 5** — the pre-flight scan's row: T5 must **re-verify** T3's asserted `etkl` booleans equal
  the ones it computes from `corpus-manifest.ttl`.

## The suite: the trap, and the workaround that removes it

The unfiltered suite is **~35 minutes** and neither leg fits in a 600 s tool call (`-m "not corpus"`
18m10s, `-m corpus` 17m28s — measured on Task 1). **This session found the workaround:** run both legs
in a **detached git worktree** under the scratchpad, in the background, against the task's commit, so
the working copy stays free and the next implementer starts immediately.

**Two git-ignored directories must be symlinked into the worktree or six modules fail to collect and
the run is a FALSE RED:** `baml_client/` (generated) and `corpus/` (the 7 documents). With both, the
worktree collects **1266 tests**, the same as the working copy.

**Caveat:** the venv's editable install resolves `iladub` to the MAIN repo's `src/`, so a worktree run
does **not** isolate `src/` changes. For **Task 8** (which touches `scripts/cockpit.py`) confirm what
is actually being executed before trusting a worktree green.

## Unverified or assumed

- **No full-suite leg has run against `001014e`.** Both legs finished GREEN at `93234cb` — corpus
  43 passed (18m32s), non-corpus 1215 passed / 7 skipped / 1 xfailed / **10 warnings** (19m22s),
  figures identical to Task 1's — but neither covers the fix commit, whose diff touched
  `tests/arc-shapes.ttl` and 12 fixtures. **Re-run both in the worktree at the head you inherit.**
  Task 3's own focused run at `001014e` is 15 passed. The 10 warnings are unexplained: Task 1's
  report gave its figures without mentioning them, so whether they pre-date this branch is
  unestablished.
- **The `prog:source` clause is enforced but its VALUE is unverified** — nothing checks the path
  exists or the line range is real, unlike M5's filesystem check on `prog:oracleArtifact`. Both the
  implementer and the re-reviewer named this as candidate **M10**, out of scope for Task 3.
- **The pre-flight conflict scan is still not independent** — the plan's author scanned it. The task
  review loop remains the only compensating check, and it has now caught two dead plan claims
  (Ruling 9, Ruling 11), which is evidence the scan missed things rather than that it was clean.
- **Seven deferred Minors from Task 3 and five from Task 1** are in the ledger, untouched, pointed at
  the final whole-branch review. One of them — `arc-manifest.ttl:8` asserting unmeasured counts
  "`dec` (16, task 4) and `tab` (10, task 6)" — is a number Task 6 is required to re-derive by grep.
- **Nothing on this branch is pushed.** `main` is pushed at `f436a8c`.

## The next concrete action

In a **fresh session**: read the ledger, then **dispatch Task 4** (the `dec` rung, 16 criteria) — its
brief is already extracted at `.superpowers/sdd/.../task-4-brief.md`. Carry into the dispatch:
**Ruling 11's IRI scheme** (the brief still names the dead `urn:` form), the "your run wins" clause,
the `prog:source` field the membrane now requires on every criterion, and the brief's own step 4 —
**D3 says author no liveness criterion on this rung**; if the implementer thinks D3 is wrong it must
say so and stop, not settle it itself.
