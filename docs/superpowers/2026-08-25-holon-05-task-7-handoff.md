# Handoff — continue the `holon:05` loop at Task 7

**Topic:** the `holon:05` membrane-health loop — Tasks 1-5 are shipped and reviewed and Task 6 is
mid-fix-round; the work is its scoped re-review, then Task 7.

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Shape: mechanical** — pointers only.
It restates nothing from the primaries and settles nothing they settle.

**Why this exists:** first written at 110k tokens by the third controlling session and **revised in
place at 148k**, when that session hit the 150k executing floor. **Tasks 1-5 are shipped and reviewed.
Task 6 is mid-fix-round: its fix is committed, its scoped re-review is NOT dispatched.** This
supersedes `2026-08-25-holon-05-task-5-handoff.md`, which is spent.

## Goal

One line: **close Task 6's fix round, execute Task 7, then run the final whole-branch review** of
`docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md`, under
`superpowers:subagent-driven-development`.

## Where the primaries are, and what to establish at each

| open | to establish |
|---|---|
| `.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md` | **THE LEDGER — read this FIRST and in full.** The recovery map: the pre-flight scan, rulings R-PF1–R-PF4, the two rulings this session added, every task's completion line, and every deferred minor. Tasks with a `Task N: complete` line are DONE — do not re-dispatch. |
| the same directory's `task-N-brief.md` | **Briefs for all 7 tasks are pre-generated**, each with the plan's Global Constraints and the four pre-flight rulings appended. Dispatch from the brief; never make a subagent read the whole plan. |
| `.../task-6-report.md` | Task 6's Step-1 measurement, its branch decision, its five falsifications, and the appended `# FIX REPORT — review round 1`. **Read its concern 1 before the re-review** (see Unverified, below). |
| `.../task-5-report.md` | Task 5's M6/M7 measurements and its two-inversion `## FALSIFICATION` block. |
| the plan | § Global Constraints, § Measurements M1–M9, § Named seams. |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.9 (Task 6's tripwire + fallback), §7, §8 item 8, §9, §11. The plan cites rather than re-derives, so the citation is not optional reading. |
| `CLAUDE.md` § Plan authoring discipline rule 4 | **Per task:** no `## FALSIFICATION` block ⇒ the task review fails. |
| `CLAUDE.md` § Deferred residues | The register is an INDEX plus two row files; a new row carries its tally snapshot in parentheses; a closing change **strikes** a row, never deletes it. |

## What was decided in the third session, and where each decision is recorded

**All of it is in the ledger and nowhere else — therefore reversible.**

- **A pre-flight-scan MISS was found and ruled.** The scan's row "T5, T6, T7 pairwise disjoint files"
  assumed Task 6 SHIPS the tripwire. On Task 6's **fallback** branch it writes a residue row into
  `docs/superpowers/residues.md` + `residues-open.md` — the same two files Task 7's carry-forward R127
  row goes in, and Task 6 runs first.
- **Ruling: `R127` is a RESERVED LABEL, not the next free number.** A Task 6 fallback row takes
  **R128**. Why: "R127" is already cited in 10 committed places for a different residue — 10 docstring
  lines across four shipped tests (`tests/etkl/test_membrane_health.py:53,78,203,205,211,369,381,382,434,437`),
  `src/iladub/etkl/document.py:1309`, and three loop docs. Renumbering falsifies all of them.
- **THAT RULING WAS THEN OVERTURNED, BY THE IMPLEMENTER, AND IT WAS RIGHT.** Spec §11:959-968
  allocates `R128` and `R129` verbatim to this loop and closes *"The next number after this loop is
  `R130`"*; `task-7-brief.md:38` Step 5 is "Raise R127, R128, R129". So R128/R129 are reserved exactly
  as R127 is. The controller's ruling had been made from **partial measurement** — it read the register
  but not spec §11, the very failure CLAUDE.md rule 2 forbids in a plan author. **Revised ruling: the
  fallback row is `R130`, as shipped.** The tally snapshot is `(24/116 closed)`, not the `(24/117)` the
  controller handed over — the implementer measured the register's own series (R126 = `24/115` with 116
  rows present) and showed the parenthetical **excludes** the row being added.
- **Task 5 was approved with zero Critical and zero Important findings** — the first task on this
  branch whose plan-supplied tests were satisfiable **verbatim**, needing no substitution.
- **Task 6 took spec §4.9's named FALLBACK, and the review UPHELD it** for the enumerator and the
  forward arm. Measured: 164 unreachable `(query, term)` pairs over 24 of 29 queries, of which **162
  would register a category error as vacuity** — the reviewer independently enumerated `interpret.run(`
  across `src/` and reproduced it (only `document.py:1229` and `:1324` pass the compile graph).
- **Two Important findings were ruled SUSTAINED and fixed in round 1** (`f4886e0`): the **reverse arm**
  was buildable after all — it consumes no population, only the registry's hand-typed keys, as
  `test_no_registered_shape_has_gone_live` (`:337-348`) already demonstrates — so it was built and R130
  narrowed to the forward arm; and R130's numbers cited no command, reproducing **R120**'s defect in the
  act of recording a different one, so R120's cheaper interim was taken (paste the commands, date the
  measurement) rather than committing a new census script.

## Unverified or assumed

- **TASK 6'S SCOPED RE-REVIEW IS NOT DISPATCHED. IT IS THE FIRST ACTION OF THE NEXT SESSION.**
  `FIX_BASE 6cae23e`, `HEAD f4886e0`. Use `re-review-prompt.md`, with the five findings, the brief, the
  report file, and a package from `scripts/review-package PLAN 6cae23e f4886e0`. Task 6 has **no
  completion line** until it verdicts.
- **AND THE RE-REVIEW HAS ONE THING TO CHECK THAT THE DIFF CANNOT SHOW IT.** Mid-round the implementer
  ran `git checkout tests/etkl/test_vacuity_registry.py` to undo falsification F4, and it reverted to
  HEAD, **destroying the 139 new lines**. It re-applied them from exact text and verified behaviourally
  and by reading back the escape-sensitive scanner lines, and F5 then ran against the re-applied file
  and failed correctly. But the re-application is **invisible in the final diff**, so *"the committed
  file is what was tested"* is a **claim, not a measurement**. Have the re-reviewer satisfy itself
  directly.
- **Task 7 has not been started.** No R127/R128/R129 rows, no manifest flip, no record change exists.
- **`R127` STILL HAS NO RESIDUE-REGISTER ROW, AND THIS IS THE MOST IMPORTANT LINE IN THIS FILE.**
  Re-verified this session: `grep -c R127 docs/superpowers/residues.md docs/superpowers/residues-open.md`
  → `0` and `0`; the register holds **116 rows, 24 closed, 92 open**, topping out at **R126**. "R127" is
  a label this loop's own spec and plan invented for a residue that was never registered — while Global
  Constraint 10 says it "must survive this loop intact" and **four shipped tests ride it**
  (`test_membrane_health.py:216, :388, :460, :578`). **Task 7 must CREATE the row**, not update one, and
  record 4 coupled tests by name. CLAUDE.md directs a maintainer to read `residues.md` in full; R127 is
  not in it, so closing R127 later turns four tests red for an invisible reason. This blocks the loop's
  definition of done. **Re-count the tally before writing the row** — Task 6 added `R130`, so the
  register now holds **117 rows** and R127's snapshot is `(24/117 closed)`, not the `(24/116)` R130
  carries. Task 7's Step 5 raises **R127, R128 and R129** (spec §11 gives all three verbatim); R130 is
  already shipped and out of scope, and **the spec's closing line "the next number after this loop is
  `R130`" is superseded to `R131`** — the shipped R130 row records that.
- **R-PF1 stands and Task 7 owes it:** re-measure `etkl:MembraneHealth`'s true line range in
  `vocab/ontology/etkl-holons.ttl` before writing the `arc-manifest.ttl:1337` citation. The controller
  measured `75-89` correct at post-Task-1 HEAD `2529983`, but Task 5 has since edited `vocab/`. **Never
  transcribe `75-89`.**
- **TASK 2 SHIPPED A REGRESSION ITS REVIEW MISSED.** `tests/etkl/test_document.py::test_single_page_document_matches_compile_tables`
  was red at `f33db9f` — verified directly by the second controller, not merely reported. Task 3's
  commit `b91e152` repaired it. **CONSEQUENCE: the plan's suite baseline `1312 passed, 7 skipped,
  1 xfailed` is NOT a clean comparator.** Task 7 Step 6 must treat any delta as a failure to
  ATTRIBUTE, not as noise, and must not assume a green branch.
- **The corpus files are indicatively green, not measured green.** `tests/test_corpus*.py` +
  `tests/test_cbh_*.py` gave **49 passed in 641.44 s**, but the run started at `b91e152` and a fix round
  mutated the tree mid-flight — including `vocab/queries/membrane-health.rq`, which `interpret.run`
  reads at RUNTIME. Re-run at a pinned commit if the answer has to be load-bearing. Also:
  `tests/etkl/test_cbh_e2e.py` does not exist; the file is `tests/test_cbh_e2e.py`.
- **O5 pins the QUERY, not `_seal`'s USE of it.** Nothing in the suite distinguishes "derived by
  `membrane-health.rq`" from "a Python reimplementation that agrees" — measured by the Task 3
  implementer. Deferred Minor 7; CLAUDE.md §8's gate is the only thing standing there.
- **Plan M2's census does not reproduce** — it claims 17 `AssertionError` interceptors; measured 7 with
  an exclusion that hides a genuine site, 8 truly, 12 without. The substantive claim (all
  isinstance-based, zero `type(e) is`) holds and is stronger. **Treat every other plan count as
  re-measurable, not as fact** — this is now the FOURTH plan claim on this branch that failed to
  reproduce.
- **Every plan-supplied test in Task 7 is a PROPOSITION** (Global Constraint 7). Three separate defects
  of this class have already been caught on this branch, all three by measuring rather than reading.

## Deferred minors awaiting the final whole-branch review

All are in the ledger with their reasons; the final reviewer must be pointed at them to triage.
**Two** from Task 2 (a report-prose line-number slip; `MembraneRefusal` not reconstructible from
`args`), **three** from Task 3 (Minors 4, 5, 7 — the thrice-derived re-entry comment, an entailed
set-cardinality assertion, and the O5 hole), **four** from Task 4 (an added assertion with no
inversion; the O7 census exclusion hiding a genuine site; a partial duplicate of a Task-2 assertion; a
Task-2 docstring whose census command returns 9 against its stated 7), and **one** from Task 5 (the
`parametrize` list has no `ids=`).

## The next concrete action

**In a fresh session: read the ledger FIRST and in full — it is the recovery map.**

Then, in order:
1. **Dispatch Task 6's scoped re-review** over `6cae23e..f4886e0`, carrying the concern-1 check above.
   Append the completion line when it verdicts clean.
2. **Execute Task 7** — dispatch from `task-7-brief.md`. It carries the R127/R128/R129 rows, R-PF1's
   re-measurement of `etkl:MembraneHealth`'s line range, the `arc-manifest.ttl:1337` citation flip, and
   the full-suite run against a baseline that is **not** clean.
3. **Run the final whole-branch review** on the most capable model, over `git merge-base main HEAD`..HEAD,
   pointed at the ledger's deferred-minor and `Ruling:` lines.
4. **Collect every ledger line containing `Ruling:`** into the closing message — that list is the only
   place the decisions taken on the maintainer's behalf reach them.
