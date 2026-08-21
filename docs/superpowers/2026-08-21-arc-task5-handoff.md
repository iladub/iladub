# Handoff — Tasks 1-5 complete and signed off; Tasks 6-8 unstarted

**Topic:** process · **Date:** 2026-08-21 · **Branch:** `arc-denominator` @ `6f02058` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASKS 1-4 COMPLETE AND SIGNED OFF. TASK 5
COMPLETE AND SIGNED OFF** after one fix round (re-review clean: all five findings ADDRESSED, no
blocking issues). **TASKS 6-8 NOT STARTED.**

> Started at ~122k, finished at ~152k — **over** the 150k executing floor, which is why the
> re-review was delegated to a file rather than adjudicated here. The controller seat
> is what needs the fresh session; implementer and reviewer seats are already fresh subagents.

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable denominator
and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

**As of `6f02058` the strip reads `etkl 1/7  dec 11/17  holon 4/6  substrate 0/3  tab ?`.**
Task 6 replaces the last `?`. **`etkl` staying at 1/7 is Task 5 succeeding, not failing** — its
deliverable was six documents moving from "nobody has looked" to "measured, reasoned, held."

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST.** Rulings 1-17, every deferred minor, the pre-flight scan. Git-ignored: `git clean -fdx` destroys it |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — the **binding authority**. But see the dead claim below: §7.1 now has one measured error |
| `docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md` | the plan, 8 tasks. **Five load-bearing claims are now known dead** |
| `.superpowers/sdd/.../task-N-report.md` | what each task built, its TDD evidence, its FALSIFICATION block |
| `.superpowers/sdd/.../task-6-brief.md` | **already extracted (86 lines), waiting** |
| `docs/superpowers/2026-08-21-arc-task4-handoff.md` | the previous handoff. Still current on Rulings 1-12 |
| `docs/superpowers/2026-08-20-arc-task3-handoff.md` | the worktree suite recipe, still correct |

## What this session decided — Rulings 13-17

Full text and cost-if-wrong for each is in the ledger. In brief:

**Ruling 13 — Task 5 also edits `tests/arc-manifest.ttl`.** The brief's "Files" line was too narrow.
MEASURED: `etkl:01-07` cite `corpus-manifest.ttl:24,44,55,69,84,95,106`, each a document *subject*
line; inserting adjudications shifts every one from 44 down. The membrane requires `prog:source` to
be present and checks neither path nor line range, so nothing caught it. **Discharged, and the
implementer went further unprompted** — it wrote a test asserting each pointer lands on the named
document's subject line, and that test **fired unaimed during the falsification**.

**Ruling 14 — the step-5 test's home follows the artifact whose truth it pins.** Route (i) reads the
arc manifest → `tests/test_arc_manifest.py`. Independently confirmed doubly right: `test_corpus.py:22`
is `pytestmark = pytest.mark.corpus` at MODULE scope, so a cheap always-on pin there would be silently
skipped under `-m "not corpus"`.

**Ruling 15 — the six new adjudications must not claim François wrote them.** `cor:by` on the seven
nodes Task 5 added names the composing agent, with the human sign-off being the reviewed commit.
CLAUDE.md §3/§4: an adjudication is an *agent-attributed* accountable act, and several of these
rationales say in the same breath that nobody has read the compile against the PDF. **This is the
ruling most worth overturning if François disagrees** — he may consider the merge his sign-off, and
it reverts with one `sed` over seven literals.

**Ruling 16 — spec §7.1's stale ons score gets a dated errata line, appended, not rewritten.**

**Ruling 17 — C2 gets residue row R105 now, before Task 6** adds ten more unguarded `prog:source`
pointers.

## The plan's dead claims — now five, and one is in the SPEC

**Every remaining dispatch must carry "your run wins."** Tasks 2, 3, 4 and 5 each found at least one.

1. Task 2's register repairs were already done (Ruling 9).
2. The criterion IRI scheme `urn:iladub:arc:crit:…` is refused by the shipped membrane; the live form
   is **`prog:criterion:<rung>:<nn>`** (Ruling 11). **Tasks 6, 7 and 8 must each be told this.**
3. The brief's *"all fifteen are `retrospective false`"* is dead (Task 4).
4. The brief's `git log -L 249,251:CLAUDE.md` evidence is wrong as stated (Task 4).
5. **NEW, and the first one in the spec rather than the plan: spec §7.1 (`:255`) says `ons` is at
   0.4419; the census measures 0.9720 and 0.4419 appears nowhere in it.** Ruling 16 appends an
   errata. **Task 6 reads §7.1 next — carry this into its dispatch.**

Task 5 also found three dead claims in its own brief's step 6 (it names a file that validates nothing;
its literal command is the forbidden corpus run; `test_corpus.py` correctly ends up unmodified). All
three were independently confirmed by the reviewer.

## Unverified or assumed

- **Task 5's re-review is CLEAN and already adjudicated — do not redo it.** Fix round 1 at `6f02058`
  had all five findings verdicted ADDRESSED with no blocking issues, each re-derived independently
  rather than read off the report. Evidence, if you want it:
  `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/task-5-rereview-round1.md`. Two claims it
  checked that would otherwise have been load-bearing assumptions: **no `prog:source` pointer moved**
  (all seven joins re-verified), and **R105's tally snapshot is `21/95`**, where the denominator
  includes the new row — a convention the register's own prose states ambiguously and which was
  re-derived from the R95→R101 progression. Record that convention somewhere durable if a later loop
  raises another row.
- **The whole-branch review still owes a full run at the final head.** Worktree recipe in the Task 3
  handoff: detached worktree, `baml_client` + `corpus` **symlinked in** or six modules fail to collect
  and the run is a FALSE RED. Collection at `4299cd8` was 1267 and reconciles exactly with `6f11d13`'s
  green (1216 + 7 + 1 + 43). Standing caveat: the venv's editable install resolves `iladub` to the
  MAIN repo's `src/`, so a worktree run does **not** isolate `src/` changes — **decisive for Task 8**,
  which touches `scripts/cockpit.py`.
- **Two membrane holes, both the same shape — "requires the field, never checks the value" — and the
  whole-branch review owns both.** (a) **M10**: `prog:source`'s path/line is unverified; R105 records
  it, and only `etkl`'s seven are guarded. (b) **M11**: Task 4's non-vacuity rule is prose enforced by
  nothing — reverting criterion 10 to its vacuous citation still yields `shacl_ok=True`. Task 5's
  citations were checked by hand and all ten land, so the class did not recur — but by hand is not an
  oracle.
- **Residual gameability that is closed only in its cheap form (Task 5's C1).** Flipping
  `cor:expectedVerdict` to `cor:CompilesAbove` with a floor at today's score is spec §7.1 row 1 and
  **counts by design**. The rung's honesty there rests on a dated adjudication + sha256 + reviewed
  commit, not on the predicate. This is an honest boundary, not a gap — but it is the boundary.
- **The pre-flight conflict scan is still not independent** — the plan's author scanned it. It has now
  missed **five** dead claims.
- **Nineteen deferred Minors** from Tasks 1, 3, 4 and 5 are in the ledger, untouched, pointed at the
  final whole-branch review.
- **The census's own per-page attributions were not re-verified** (constraint (h) forbids the 315 s
  re-run). Task 5's rationales were confirmed to report the census faithfully; the census itself was
  Task 0's evidence.
- **Nothing on this branch is pushed.** `main` is pushed at `f436a8c`.

## The next concrete action

In a **fresh session**: read the ledger, **read
`.superpowers/sdd/.../task-5-rereview-round1.md` and adjudicate it**, close Task 5, then
**dispatch Task 6** (the `tab` rung, 10
criteria = 9 escalation reasons + 1 registry — it replaces the strip's last `?`). Its brief is already
extracted at `.superpowers/sdd/.../task-6-brief.md` (86 lines). Carry into the dispatch: **"your run
wins"**; the live IRI scheme **`prog:criterion:<rung>:<nn>`**; **dead claim 5 — §7.1's ons score, which
Task 6 reads**; **D1** (a corpus-dead escalation reason is NOT met by being dead) and **Ruling 12's
generalisation** (*a criterion is counted where its declaring prose lives; two rungs measuring one
artifact under two rules is the design, not double-counting* — Task 6 should apply it without
re-litigating); **Ruling 18 — M10 SHIPS IN TASK 6** (see below, decided by François 2026-08-21; it is no
longer optional and no longer the whole-branch review's); the non-vacuity rule as a by-hand obligation;
and the suite do-not-run with the worktree recipe as the reason.


## Ruling 18 — M10 ships in Task 6 (decided by François, 2026-08-21)

**This reverses two prior deferrals deliberately.** M10 was named and declined as "new scope" by
Task 3's implementer, then paid **by hand** by Ruling 13 (seven `prog:source` pointers re-pointed
manually, because nothing catches a stale one). Task 6 adds **ten more pointers**, so deferring again
means a third hand-payment plus ten new unguarded rows. Full text and cost-if-wrong in the ledger.

**What M10 is:** an **environment-leg check** — for every criterion's `prog:source "<path>:<line>"`,
does the path exist and is the line in range? **PROCEDURAL**, already covered by Global Constraint 2's
existing justification (filesystem facts no SHACL engine can see), sited beside the existing M5/M7
legs in `tests/test_arc_manifest.py`. No new gate argument needed.

**The constraint that stops Task 6 building the wrong thing — carry this verbatim.** M10 is **NOT the
`etkl` pointer test generalised.** That test resolves a pointer by *joining the criterion to the
document it names*, and **only `etkl` has a second graph to join against** — `dec`, `holon`,
`substrate` and `tab` cite prose files, so there is nothing to semantically join. R105's own row
records this as the R101 lesson. M10 is the weak-but-universal guard (path + line range, every
criterion); the `etkl` join stays the strong guard for the one rung that supports it. **Two
instruments, both kept.**

**Scope fence:** path existence and line range only. M10 does **not** check that the cited line says
anything in particular — different residue, must not be smuggled in.

**On landing:** strike R105 (`~~R105~~`) and record the closure evidence **in place**. Do not delete
the row — CLAUDE.md's 2026-08-12 reversal: a deleted row erases the proof of repair and silently
shrinks the denominator.

**If the implementer reports M10 blocked**, that is a finding about the register's oldest declined
item — not a Task 6 failure. Fall back to Ruling 13's hand-payment and record a third payment against
R105, which stays open.
