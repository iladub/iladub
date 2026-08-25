# Handoff — continue the `holon:05` loop at Task 7

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Shape: mechanical** — pointers only.
It restates nothing from the primaries and settles nothing they settle.

**Why this exists:** written at 110k tokens by the third controlling session (executing floor 150k),
while still accurate, with two tasks and a whole-branch review left. **Tasks 1, 2, 3, 4 and 5 are
shipped and reviewed.** This supersedes `2026-08-25-holon-05-task-5-handoff.md`, which is spent.

## Goal

One line: **finish executing `docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md`,
Task 6 (if it did not land) and Task 7, then the final whole-branch review**, under
`superpowers:subagent-driven-development`.

## Where the primaries are, and what to establish at each

| open | to establish |
|---|---|
| `.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md` | **THE LEDGER — read this FIRST and in full.** The recovery map: the pre-flight scan, rulings R-PF1–R-PF4, the two rulings this session added, every task's completion line, and every deferred minor. Tasks with a `Task N: complete` line are DONE — do not re-dispatch. |
| the same directory's `task-N-brief.md` | **Briefs for all 7 tasks are pre-generated**, each with the plan's Global Constraints and the four pre-flight rulings appended. Dispatch from the brief; never make a subagent read the whole plan. |
| `.../task-6-report.md` | Whether Task 6 shipped the tripwire or took spec §4.9's fallback, and the measured count that decided it. **Read this before Task 7** — the branch determines whether a residue row already exists. |
| `.../task-5-report.md` | Task 5's M6/M7 measurements and its two-inversion `## FALSIFICATION` block. |
| the plan | § Global Constraints, § Measurements M1–M9, § Named seams. |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.9 (Task 6's tripwire + fallback), §7, §8 item 8, §9, §11. The plan cites rather than re-derives, so the citation is not optional reading. |
| `CLAUDE.md` § Plan authoring discipline rule 4 | **Per task:** no `## FALSIFICATION` block ⇒ the task review fails. |
| `CLAUDE.md` § Deferred residues | The register is an INDEX plus two row files; a new row carries its tally snapshot in parentheses; a closing change **strikes** a row, never deletes it. |

## What was decided in the third session, and where each decision is recorded

**Both rulings are in the ledger and nowhere else — therefore reversible.**

- **A pre-flight-scan MISS was found and ruled.** The scan's row "T5, T6, T7 pairwise disjoint files"
  assumed Task 6 SHIPS the tripwire. On Task 6's **fallback** branch it writes a residue row into
  `docs/superpowers/residues.md` + `residues-open.md` — the same two files Task 7's carry-forward R127
  row goes in, and Task 6 runs first.
- **Ruling: `R127` is a RESERVED LABEL, not the next free number.** A Task 6 fallback row takes
  **R128**. Why: "R127" is already cited in 10 committed places for a different residue — 10 docstring
  lines across four shipped tests (`tests/etkl/test_membrane_health.py:53,78,203,205,211,369,381,382,434,437`),
  `src/iladub/etkl/document.py:1309`, and three loop docs. Renumbering falsifies all of them.
- **Task 5 was approved with zero Critical and zero Important findings** — the first task on this
  branch whose plan-supplied tests were satisfiable **verbatim**, needing no substitution.

## Unverified or assumed

- **Task 7 has not been started.** No residue row, no manifest flip, no record change exists.
- **`R127` STILL HAS NO RESIDUE-REGISTER ROW, AND THIS IS THE MOST IMPORTANT LINE IN THIS FILE.**
  Re-verified this session: `grep -c R127 docs/superpowers/residues.md docs/superpowers/residues-open.md`
  → `0` and `0`; the register holds **116 rows, 24 closed, 92 open**, topping out at **R126**. "R127" is
  a label this loop's own spec and plan invented for a residue that was never registered — while Global
  Constraint 10 says it "must survive this loop intact" and **four shipped tests ride it**
  (`test_membrane_health.py:216, :388, :460, :578`). **Task 7 must CREATE the row**, not update one, and
  record 4 coupled tests by name. CLAUDE.md directs a maintainer to read `residues.md` in full; R127 is
  not in it, so closing R127 later turns four tests red for an invisible reason. This blocks the loop's
  definition of done. **Re-count the tally before writing the row** — Task 6's fallback may have added one.
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

**In a fresh session: read the ledger FIRST and let it tell you where Task 6 stands.**

If Task 6 has a `complete` line, execute **Task 7** — dispatch from `task-7-brief.md`. Task 7 carries
the R127 register row above, R-PF1's re-measurement, the full-suite run with its non-clean baseline,
and the ten deferred minors listed above. Then run the final whole-branch review on the most capable
model, over `git merge-base main HEAD`..HEAD, pointed at the ledger's deferred-minor lines.
