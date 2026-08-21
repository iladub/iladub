# Handoff — Task 7 built and under review, unadjudicated; Task 8 unstarted

**Topic:** process · **Date:** 2026-08-21 · **Branch:** `arc-denominator` @ `e36b79a` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASKS 1-6 COMPLETE AND SIGNED OFF. TASK 7 BUILT
AND COMMITTED; ITS REVIEW IS IN FLIGHT AND UNADJUDICATED.** **TASK 8 NOT STARTED.**

> This seat crossed the 150k executing floor when Task 7's report landed (151.6k). Task 7's review was
> therefore dispatched **to a file** rather than adjudicated here — the same move Task 5's seat made
> for the same reason. Adjudicating a review report is judgment work, and judgment is what degrades.

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable denominator
and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

**The manifest is finished** and reads `etkl 1/7 · dec 11/17 · holon 4/6 · substrate 0/3 · tab 1/10`
— **17 met of 43 criteria.** Task 7 wrote the four SPARQL derivations that read it; Task 8 wires them
into `scripts/cockpit.py` and is the last task.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST.** Rulings 1-19, every deferred minor, the pre-flight scan. Git-ignored: `git clean -fdx` destroys it |
| `.superpowers/sdd/.../task-7-review.md` | **the review this seat did not adjudicate. Written by the reviewer directly. Start here after the ledger** |
| `.superpowers/sdd/.../task-7-report.md` | what Task 7 built, its TDD/RED evidence, both falsification arms, the four live result sets |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — the **binding authority**. Three measured errors now (see below) |
| `docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md` | the plan, 8 tasks. **Seven load-bearing claims are now known dead** |
| `docs/superpowers/2026-08-21-arc-task6-handoff.md` | the previous handoff. Still current on Rulings 13-18, M10, and the `prog:blockedBy` rule |
| `docs/superpowers/2026-08-20-arc-task3-handoff.md` | the worktree suite recipe, still correct |

## What this session did

**Task 6 shipped and was signed off** — the `tab` rung at 1/10 plus **M10**, closing residue R105.
Details are in the Task 6 handoff; it needed no fix round, the first task on this branch of which that
is true.

**Both suite legs ran GREEN at `170be91`** — non-corpus 1219 passed / 7 skipped / 1 xfailed /
10 warnings, corpus 43 passed, collection 1270 reconciling exactly with the previous 1267 plus Task
5's three new tests. That closed a gap two handoffs carried.

**Task 7 was dispatched, built and committed** (`e36b79a`, 5 files, +586, all new: four `.rq` plus
`tests/test_arc_queries.py`). 35 passed; RED shown with the four `.rq` removed; both falsification
arms shown failing and restored.

## Rulings this session made

**Ruling 19 — the `arc-orphan` seam was stated AS a seam and deliberately NOT answered for the
implementer.** Recorded in the ledger with its full cost-if-wrong. Measured before dispatch:
`prog:blockedBy`'s values are **plain string literals** (`prog:blockedBy "R74"`,
`tests/arc-manifest.ttl:1055`) and the residue register is a **markdown file not in the graph at
all** — which is why M7 reads it in procedural code — so a residue that blocks nothing has **no node
in the manifest graph to select**, and the brief's `arc-orphan → (?residue)` shape looked
underivable. Rather than supply a substitute, the dispatch handed the implementer the measurement,
Global Constraint 9 verbatim, and an explicit refusal of the tempting wrong fix (*inventing triples
that mirror the register is deriving-by-absence*, which CLAUDE.md §8 forbids the graph half to do).

**It was confirmed.** The implementer measured the same thing independently and resolved it: the
caller supplies `?residue`, claimed to follow `adoption-candidate.rq`'s existing idiom, shape
unchanged, assertion claimed **strengthened not weakened**. **This is the third instance on this
branch of the CLAUDE.md rule-5 defect shape — a plan-supplied test whose SETUP cannot be
constructed.** Cost if the reviewer overturns it: the substitute is one query's calling convention,
and Task 8 is the only consumer.

**No other ruling was made.** Every other judgment call was carried to a reviewer as a claim to judge.

## The plan's dead claims — now seven, and three are in the spec

1. Task 2's register repairs were already done (Ruling 9).
2. The `urn:iladub:arc:crit:…` IRI scheme is refused by the membrane (M9b); the live form is
   **`prog:criterion:<rung>:<nn>`** (Ruling 11). **Task 8 must be told this.**
3. The brief's *"all fifteen are `retrospective false`"* (Task 4) — and its Task 6 twin, *"all nine
   are `retrospective false`"*: M4 refuses `retrospective false` on any row where
   `metOn == declaredOn`, which is every row this loop declares and meets.
4. The brief's `git log -L 249,251:CLAUDE.md` evidence is wrong as stated (Task 4).
5. **Spec §7.1 (`:255`): `ons` at 0.4419; the census measures 0.9720** (Task 5; errata appended).
6. **Spec §7.4: `tab` is 9 criteria over eight reasons. It is 10 over nine** (Task 6) — `TRANSPOSED`
   is misfiled there as a *kind*, and §7.4's blocker table gives it no row when **two** exist.
7. **NEW — spec §7.4 calls R101 "the first instance" of a residue that blocks no criterion. Task 7
   measures 59 of 74 open rows blocking nothing.** Unverified pending the review, and **it is the
   figure most likely to be quoted out of this loop**: if it holds, 80% of the open register serves no
   stated goal. Do not repeat it without opening the review's verdict on concern 4.

## Unverified or assumed

- **Task 7's review is IN FLIGHT and its verdict is unknown.** Read
  `.superpowers/sdd/.../task-7-review.md`. It carries five concerns to judge, none pre-judged: the
  `arc-orphan` resolution; the same seam in two further spec wordings (`arc-unblocked`'s *"every
  blocker now CLOSED"* and `arc-frontier`'s *"the OPEN residues"* are **register facts, not graph
  facts** — the graph's half was implemented and the two readings coincide only *today*); that
  **nothing in the membrane refuses a `prog:blockedBy` naming a CLOSED row** (M7 checks presence, not
  state — and R105 is now exactly such a row); the 59/74 figure; and a **controller error**.
- **A controller error is in the record, and it should stay there.** This seat's dispatch named
  `tests/test_source_ownership.py` as the policeman of `vocab/queries/`. The implementer measures that
  it never opens a `.rq`, and that `tests/test_transform_gate.py::test_no_tuned_constant_in_rq_files`
  is what actually polices them. It ran both. Pending the reviewer's confirmation — a controller error
  belongs in the record exactly as a plan defect does, and this is the first on this branch.
- **Task 8's dependency, stated by Task 7 and not yet verified by anyone:** `arc-orphan` must be
  called with **`initBindings`, once per register row** — it does not range over residues by itself.
  If Task 8 assumes a self-contained query it will get an empty result and no error.
- **The suite has NOT run against `e36b79a` or `0d50518`.** The last green is `170be91`. A fresh leg
  is owed at the final head. Recipe in the Task 3 handoff: detached worktree, `baml_client` + `corpus`
  **symlinked in** or six modules fail to collect and the run is a FALSE RED. **Standing caveat that
  is decisive for Task 8:** the venv's editable install resolves `iladub` to the MAIN repo's `src/`,
  so a worktree run does **not** isolate `src/` changes — and Task 8 touches `scripts/cockpit.py`.
  Confirm what is actually executing before trusting a worktree green there.
- **The 10 warnings are still unattributed.** Sampled this session as rdflib
  `ConjunctiveGraph is deprecated` from `plugins/parsers/jsonld.py:159` — a dependency deprecation,
  not this branch's — but the count has been reported without explanation since Task 1.
- **M11 / R106 is open and untouched.** Task 6's ten rows were held to the non-vacuity rule **by
  hand**, discharged only where it bites (one row in the numerator).
- **`tab 1/10` has one named soft spot:** `tab:06`'s `met true` excludes **R6** as an edge because R6
  is unmeasured, where R71 (measured) is included. A live run of the merge path over the corpus is
  what would settle whether 1/10 should be 0/10.
- **Twenty-six deferred Minors** from Tasks 1, 3, 4, 5 and 6 are in the ledger, untouched, pointed at
  the final whole-branch review — plus whatever Task 7's review adds.
- **The pre-flight conflict scan is still not independent** — the plan's author scanned it. It has now
  missed **seven** dead claims.
- **Nothing on this branch is pushed.** `main` is pushed at `f436a8c`.

## The next concrete action

In a **fresh session**: read the ledger, then **read `.superpowers/sdd/.../task-7-review.md` and
adjudicate it** — run any fix loop it warrants, write Task 7's completion line, and only then
**dispatch Task 8**. Task 8's brief is not pre-extracted; use
`scripts/task-brief docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md 8`.

Carry into Task 8's dispatch: **"your run wins"** with the seven dead claims; the live IRI scheme;
**`arc-orphan` needs `initBindings` per register row**; the four result shapes Task 7 fixed
(`arc-position → (?rungKey ?met ?declared)`, `arc-frontier → (?residue ?rungKey ?criterion)`,
`arc-unblocked → (?rungKey ?criterion ?statement)`, `arc-orphan → (?residue)`); **spec §9 forbids a
rung with no criteria rendering as `0`** — absent or null, never zero; the editable-install caveat as
the reason a worktree green cannot be trusted for `src/`-adjacent work; and the suite do-not-run.

After Task 8: the **whole-branch review** on the most capable model, pointed at the ledger's deferred
minors and parked lines, with a fresh suite leg at the final head.
