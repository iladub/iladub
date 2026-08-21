# Handoff — Task 6 complete and signed off; the strip has no `?` left; Tasks 7-8 unstarted

**Topic:** process · **Date:** 2026-08-21 · **Branch:** `arc-denominator` @ `0d50518` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASKS 1-6 COMPLETE AND SIGNED OFF.** Task 6
needed **no fix round** — Spec ✅, Approved, 0 Critical, 0 Important, 7 Minors deferred.
**TASKS 7-8 NOT STARTED.**

> Started at ~74k, handed off at ~120k against the 150k executing floor. Task 7 was NOT dispatched
> for that reason and no other: its dispatch plus its report plus its review would have landed past
> the floor, and this loop's own rule is that a seat hands off while still accurate.

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable denominator
and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

**As of `0d50518` the strip reads `etkl 1/7 · dec 11/17 · holon 4/6 · substrate 0/3 · tab 1/10`.**
**Task 6's deliverable was the last `?`, and it is gone.** Every rung now has a measured denominator.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST.** Rulings 1-18, every deferred minor, the pre-flight scan. Git-ignored: `git clean -fdx` destroys it |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — the **binding authority**. Two measured errors now: §7.1's `ons` score, and §7.4's `tab` count |
| `docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md` | the plan, 8 tasks. **Six load-bearing claims are now known dead** |
| `.superpowers/sdd/.../task-N-report.md` | what each task built, its TDD evidence, its FALSIFICATION block |
| `docs/superpowers/2026-08-21-arc-task5-handoff.md` | the previous handoff. Still current on Rulings 13-18 |
| `docs/superpowers/2026-08-20-arc-task3-handoff.md` | the worktree suite recipe, still correct |

## What this session did

**Task 6 shipped the `tab` rung at 1/10 and M10 with it, in one commit (`0d50518`, 7 files, +462/-15).**
No fix round was needed — the first task on this branch of which that is true.

**R105 is CLOSED.** M10 ships as an environment leg in `tests/test_arc_manifest.py`
(`_source_refusal`, `:240-262`): for **every** criterion, met or not, `prog:source`'s path must exist
and its line must be in range. All 43 pointers resolve. The row is struck (`~~R105~~`) and **moved**
to `residues-closed.md:84` with closure evidence in place — not deleted; the index at
`residues.md:185` reads `| R105 | closed |`. Ruling 18's three constraints were each verified
honoured by the reviewer: the `etkl` join survives **verbatim and unweakened**
(`test_arc_manifest.py:572-589`), the scope fence holds (path + line range only, never the line's
content), and the row was struck rather than deleted.

**The falsification arm that matters ran.** Arm B2 staled a *live* pointer (`dec:01` →
`CLAUDE.md:99252`) and turned the **tracked manifest's own** conformance test red. That is the arm
R105 asked for, and it proves the guard is on the real graph and not only on the new negative fixture
(`tests/arc-m10-stale-source-pointer-leak.ttl`).

**Both suite legs are GREEN at `170be91`** — the first full run covering Task 5's fix commit
`6f02058`, closing a gap two handoffs carried. Non-corpus **1219 passed / 7 skipped / 1 xfailed /
10 warnings** (19m48s); corpus **43 passed** (19m06s). Collection **1270**, reconciling exactly with
`4299cd8`'s 1267 plus Task 5's three new tests. Interpreter identity was verified against the
`python3` trap before the run was trusted: `sys.prefix` = the repo `.venv`, rdflib 7.6.0, `pyrudof`
importable. Worktree: `…/f436ba37-…/scratchpad/suite-170be91`.

## Rulings this session made

**None.** Every judgment call Task 6 raised was carried to the reviewer as a claim to judge, and all
five stood on independent measurement. That is the whole content of this session's decision-making:
it declined to adjudicate what a second seat could measure. The one thing that looks like a ruling —
that the reviewer's ⚠️ on the census firing counts is resolved — was resolved by the reviewer's own
substitute check, not by a controller's judgment (`git diff --stat 820ab24..HEAD -- src/ corpus/` is
empty, so the census HEAD is byte-identical for both its inputs).

## The plan's dead claims — now six, and two are in the spec

**Every remaining dispatch must carry "your run wins."** Tasks 2, 3, 4, 5 and 6 each found at least
one.

1. Task 2's register repairs were already done (Ruling 9).
2. The criterion IRI scheme `urn:iladub:arc:crit:…` is refused by the shipped membrane (M9b); the live
   form is **`prog:criterion:<rung>:<nn>`** (Ruling 11). **Tasks 7 and 8 must each be told this.**
3. The brief's *"all fifteen are `retrospective false`"* is dead (Task 4).
4. The brief's `git log -L 249,251:CLAUDE.md` evidence is wrong as stated (Task 4).
5. **Spec §7.1 (`:255`) says `ons` is at 0.4419; the census measures 0.9720** (Task 5, Ruling 16
   appended a dated errata).
6. **NEW, and the second in the spec: §7.4 says `tab` is 9 criteria over eight reasons. It is 10 over
   nine** — `TRANSPOSED` is misfiled there as a *kind*, and `RegionKind` (`regions.py:27-30`) has
   exactly three members, none of them `TRANSPOSED`. Also: **§7.4's blocker table gives `TRANSPOSED`
   no row, and two exist — R68 (a recorded reason, not an edge) and R71 (a real blocker).**

Brief step 2's *"all nine are `retrospective false`"* is dead the same way claim 3 is: M4
(`arc-shapes.ttl:123-128`) refuses `retrospective false` on any row where `metOn == declaredOn`, which
is every row this loop declares and meets. `tab:06` is `retrospective true`.

## The rule Task 6 had to state because the plan never did

**A `prog:blockedBy` edge names a register row whose closure would ADVANCE the criterion — not a row
that merely mentions the reason.** It is written into the manifest so the next seat does not re-derive
it. Under it: R15 and R68 are *recorded reasons*, not edges; R6 and R8 are neither. **This is the rule
that set `tab` to 1/10 rather than 2/10**, and it is the most reusable thing this task produced.

## Unverified or assumed

- **The suite has NOT run against Task 6's `0d50518`.** The green above covers `170be91`. A fresh leg
  is owed at the final head. Recipe in the Task 3 handoff: detached worktree, `baml_client` + `corpus`
  **symlinked in** or six modules fail to collect and the run is a FALSE RED. Standing caveat: the
  venv's editable install resolves `iladub` to the MAIN repo's `src/`, so a worktree run does **not**
  isolate `src/` changes — **decisive for Task 8**, which touches `scripts/cockpit.py`.
- **The 10 warnings are still unattributed.** Sampled this session as rdflib
  `ConjunctiveGraph is deprecated` from `plugins/parsers/jsonld.py:159` — i.e. a dependency
  deprecation, not this branch's — but the count has been reported without explanation since Task 1
  and still owes a proper attribution at the whole-branch review.
- **M11 / R106 is open and untouched**, as instructed. Task 6's ten rows were held to the non-vacuity
  rule **by hand**, and the reviewer confirmed the obligation is discharged *where it bites* — only
  `tab:06` is in the numerator, and it is falsified for real. It does not protect the next flip.
- **`tab 1/10` has one soft spot, and it is named:** `tab:06`'s `met true` excludes **R6** as an edge
  because R6 is unmeasured, where R71 (measured) is included. *Mechanically the same suppression story,
  minus the measurement.* Consistent and reasoned — but **a live run of the merge path over the corpus
  is what would settle whether 1/10 should be 0/10.**
- **Twenty-six deferred Minors** from Tasks 1, 3, 4, 5 and 6 are in the ledger, untouched, pointed at
  the final whole-branch review. Task 6's seven include two that harden M10 itself (a bare
  `prog:source` with no `:line` escapes the range check; two divergent pointer parsers now exist) and
  one **R105-family follow-up**: `prog:oracleArtifact` carries the same `<path>:<line>` grammar and M5
  *strips* the line rather than checking it.
- **The pre-flight conflict scan is still not independent** — the plan's author scanned it. It has now
  missed **six** dead claims.
- **The census's own per-page attributions have never been re-verified** (constraint (h) forbids the
  315 s re-run). Its inheritance premise IS verified: `src/` and `corpus/` are byte-identical to
  `820ab24`.
- **Nothing on this branch is pushed.** `main` is pushed at `f436a8c`.

## The next concrete action

In a **fresh session**: read the ledger, then **dispatch Task 7**. Extract its brief with
`scripts/task-brief docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md 7` — it is **not**
pre-extracted, unlike every previous task's. Carry into the dispatch: **"your run wins"** with the six
dead claims; the live IRI scheme **`prog:criterion:<rung>:<nn>`**; **dead claim 6** if Task 7 reads
§7.4; **the `prog:blockedBy` rule above**; **M10 now exists** — every `prog:source` a new task writes
is checked for path existence and line range, so a stale pointer turns the suite red rather than
passing silently (this is a *change in the environment* Task 7's brief predates); the non-vacuity rule
as a by-hand obligation with R106/M11 named and explicitly out of scope to close; and the suite
do-not-run with the worktree recipe as the reason.

**Task 8 touches `scripts/cockpit.py`** — the editable-install caveat above bites there, and its
worktree green must be confirmed against what is actually executing before it is trusted.
