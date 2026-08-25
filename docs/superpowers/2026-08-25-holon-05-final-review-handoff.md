# Handoff — `holon:05`, the final fix wave then merge

**Topic:** the `holon:05` membrane-health loop — all seven tasks complete and the whole-branch review
done; one fix wave of seven prose edits stands between the branch and merge.

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Shape: mechanical** — pointers only.
It restates nothing from the primaries and settles nothing they settle.

**Why this exists:** written by the **fourth** controlling session and revised in place three times,
last at ~222k tokens, past the 150k executing floor with each override logged. **ALL SEVEN TASKS ARE
COMPLETE AND REVIEWED, AND THE FINAL WHOLE-BRANCH REVIEW IS DONE: `YES WITH FIXES`, zero Critical,
ZERO CODE FINDINGS.** What remains is ONE fix wave of seven one-line prose edits, one scoped
re-review, and the merge decision. This supersedes `2026-08-25-holon-05-task-7-handoff.md`, which is
spent.

## Goal

One line: **dispatch ONE fix wave for the seven prose findings below, run ONE scoped re-review, then
decide the merge** — under `superpowers:subagent-driven-development`. There is no second fix wave.

## Where the primaries are, and what to establish at each

| primary | what to establish there |
|---|---|
| `.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md` | **THE LEDGER — read this FIRST and in full.** The recovery map: the pre-flight scan, rulings R-PF1–R-PF4, every task's completion line, the **seventeen** deferred minors (re-count them; the ledger's own greps do not reproduce), and every `Ruling:` line. Tasks with a `Task N: complete` line are DONE — do not re-dispatch. |
| `docs/superpowers/2026-08-25-holon-05-loop-ledger.md` | **The COMMITTED copy of that ledger**, verbatim. The working copy above lives in a git-ignored workspace the SDD process DELETES at loop close — read this one if the workspace is gone. |
| the same directory's `task-7-report.md` | Task 7's nine falsifications, its four non-reproducing brief values, and the edge-deletion reasoning. |
| the same directory's `review-b314c23..ae5fefd.diff` | The package the Task-7 reviewer read. |
| the plan | § Global Constraints, § Measurements M1–M9, § Named seams. |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.9, §7, §8, §9, §11. |

## The seven blocking fixes — this is the whole remaining fix wave

Dispatch these as **ONE** subagent, not one per finding. Every one is a sentence the repo can measure
to be false; none is a code change. **Each fixer must RE-MEASURE before editing — do not transcribe
the numbers below.** That instruction is the point: every item here exists because someone did not.

1. **`tests/etkl/test_vacuity_registry.py:414-416` AND `docs/superpowers/residues-open.md:103`** —
   the claim that `test_no_registered_shape_has_gone_live` (`:337`) "consumes no population" is FALSE:
   `:343` calls `shapes_graph()` → `:143-147` → `wired_shape_files()` (`:133-140`). **Ship the correct
   wording**, which preserves the argument: the reverse arm needs no **enumerator**, because its
   **rows** are hand-typed. *(Originated in a controller ruling and was transcribed into source.)*
2. **`src/iladub/etkl/document.py:137-138`** — "nothing reads the file at import time, and `_seal`
   does not run it yet; that wiring is the next task's" is FALSE at HEAD: `:1324` is
   `graph += interpret.run(MEMBRANE_HEALTH_RQ, graph)`. A Task-2 comment Task 3 invalidated. It also
   leaks SDD process vocabulary ("the next task's") into production source — drop that too.
3. **`src/iladub/etkl/document.py:1747-1750`** — five citations ALL off by 50, under the words
   *"MEASURED, not assumed"*, and `recognized` has **two** writers where the comment names one.
   Measured: `section_facts` at `:1561, :1573, :1605, :1743`; `recognized` at `:1395, :1421`. The
   substantive claim survives (last write `:1743` < the `_seal` call at `:1751`).
4. **`src/iladub/etkl/document.py:1208`** — `:1486`/`:1690` are `:1536`/`:1740`.
5. **`tests/etkl/test_membrane_health.py:105-107`** — the pasted command returns **12**, not the
   stated 7; the honest repo-wide count is **8** (`:579` is a real interceptor the exclusion hides).
   M2's substantive claim (zero `type(e) is`) is untouched.
6. **`docs/superpowers/residues.md:260`** — R136's **index** line says the revert left "the suite fully
   green"; it was two modules, `31 passed`. Same defect the branch already fixed one row away in
   `5d01a4c`.
7. **`docs/superpowers/2026-08-25-holon-05-task-7-handoff.md` + its 3 topicless siblings** — add
   `**Topic:**` and **take the red with it**. Merging introduces no red (merge-base's newest doc is
   already topicless), but `d9eb6ae`'s handoff now sorts top under `max()` (`cockpit.py:283-292`), so
   the branch sustains it. Spec §8 item 9 wants a green suite. Four lines.

**Plus one Minor worth folding in — it is a SPEC GAP, so fix §4.6 first, then the file:**
`vocab/ontology/etkl-holons.ttl:79-80`, `etkl:Intact`'s comment was never amended with the model and
**no longer discriminates** — "Interior fully conforms to the membrane" is equally true of `Weakened`,
which also requires `?conforms = true`. The distinguishing fact (*nothing is held*) reached
`MembraneHealth`'s and `Weakened`'s comments but not `Intact`'s.

## What the review verified green — do not re-litigate these

- **Zero code findings.** The derivation is a genuine AXIOM; the oracles are real and independently
  falsifiable; the shape refuses for the right reasons.
- **The neurosymbolic gate is CLEAN** — no tuned constant or tolerance anywhere in the new code, no
  SHACL derives anything, no Python answers a span/read/group/role question.
- **Source ownership is CLEAN** — no HGA-prefixed term appears as a subject in any authored `.ttl`.
- **O9 falsified by hand**: each negative fixture trips exactly one arm.
- **`compile.py` has ZERO changes on this branch**, so R-PF4's premise holds by the diff alone.
- **The ruling audit: all ~20 rulings reach sound outcomes.** Exactly one reached the right conclusion
  from a false premise — the Task 6 Important-1 ruling, which is fix 1. *Fix the reason, keep the
  ruling.* The §11 / R131–R134 ruling was scrutinised hardest and is **sound**.

## What was decided in the fourth session, and where each decision is recorded

**All of it is in the ledger and nowhere else — therefore reversible.**

- **Task 6's owed re-review ran clean**, and its committed-file check came back **VERIFIED** by three
  independent routes (blob-hash identity, behavioural equivalence of `rq_terms`, the escape-sensitive
  scanner checked across all 46 `.rq` files). Task 6 has its completion line.
- **A ruling on spec §11's numbering:** §11 raises **eight** residues but allocates **three** numbers.
  Ruled: items 1–4 take R131–R134. Task 7 upheld this on independent reasoning and extended it —
  see below.
- **Task 7's edge deletion was UPHELD by the reviewer on stronger evidence than the report offered.**
- **R-PF1 is DISCHARGED** — `etkl:MembraneHealth` is `75-89`, re-measured at HEAD.

## Unverified or assumed

- **THE `1334 passed` FIGURE WAS NOT RE-RUN** (42 minutes; the reviewer was instructed not to).
  Both checkable projections hold at HEAD — collected = 1343, and `1334 + 1 + 7 + 1 = 1343`.
- **THE `1312` BASELINE IS NOT A CLEAN COMPARATOR, ON TWO INDEPENDENT GROUNDS.** It was measured in
  another session; Task 2's +3 triples broke a parity test (repaired in `b91e152`); and it predates
  `9adb4d0`, which introduced the surviving red.
- **ONE TEST IS RED, AND THE BRANCH SUSTAINS IT INDEPENDENTLY OF ITS CAUSE.**
  `test_the_live_newest_handoff_declares_a_topic`. The attribution to `main` (`9adb4d0`, an ancestor
  of merge-base `18226e7`) is **verified**. But `d9eb6ae` **on this branch** added a second topicless
  handoff, which is now the file `_newest_loop_doc()` selects. **This handoff carries a `**Topic:**`
  line to avoid becoming the third** — verify that it does, and consider whether the branch should
  repair the red rather than inherit it.
- **CORRECTED — the claim that `tests/test_corpus*.py` was never run on a pinned commit is FALSE**, and
  it was carried through three handoffs including this one. `pyproject.toml:96-101` declares the
  `corpus` marker but sets **no `addopts`**, so nothing is deselected by default; collection at HEAD is
  1343, the 49 corpus tests are inside it, and `1334 + 1 + 7 + 1 = 1343` closes exactly. **The corpus
  modules are covered.** Not a merge blocker.
- **THE R135/R117 CALL IS TAKEN** (by the final reviewer, at the controller's request): **plan ONE
  instrument; close both in the same act ONLY if the shipped instrument demonstrably covers
  `iladub-hga-align.ttl`; do NOT merge the rows now.** Same failure class — an owned-namespace IRI
  resolves whether or not any ontology declares it — but R117 carries a scoping question R135 does not:
  what *declared* means at the **alignment** seam. **Later loop's work, NOT a merge consideration.**
- **The deferred minors are TRIAGED — 17 of them, not the 15 or 16 earlier handoffs claimed** (the
  ledger's own counts did not reproduce; see below). Six are must-fix and are folded into the seven
  above; the rest are **later** or **drop**, itemised in the review's triage table. **One deferred
  minor is a genuine HOLE rather than prose and deserves its own residue row:** ledger `:190`, Task 3
  Minor 7 — O5 pins the *query*, not `_seal`'s *use* of it, so nothing in the suite distinguishes
  "derived by `membrane-health.rq`" from "a Python reimplementation that agrees". CLAUDE.md §8 is the
  only guard standing there.
- **THE LEDGER'S OWN COUNTS DO NOT REPRODUCE — the tenth instance of this branch's signature failure,
  in the artefact that catalogues the other nine.** `grep -c 'minor (deferred):'` returns 16 only
  because a dispatch line self-matches; there are 15 findings plus 2 in the Task-2 block = **17**. And
  `grep -c 'Ruling:'` returns **7**, not the 22 the controller reported (that figure came from a
  broader `Ruling\|RULING` query, stated as if it were the narrower one). **Re-count before citing.**
- **The register is now 127 rows / 25 closed / 102 open, next free number `R138`.** Ten pre-existing
  gaps (17, 21, 22, 41, 69, 70, 73, 75, 81, 82) are inherited, not introduced.

## The next concrete action

**In a fresh session: read the ledger FIRST and in full — it is the recovery map.**

Then, in order:

1. **Dispatch ONE fix subagent** with all seven findings above (plus the `etkl:Intact` spec gap if you
   take it). **Not one fixer per finding** — per-finding fixers each rebuild context and re-run suites,
   and a real session's fix wave cost more than all its tasks combined. Tell it to **re-measure every
   number before editing**; that is the whole lesson of this list.
2. **Run ONE scoped re-review** over the fix range (`scripts/review-package PLAN <FIX_BASE> HEAD`).
   **A base-commit trap has bitten three times on this branch:** controller handoff commits land
   between a task and its review, so use the head the last review actually saw and check what is in
   your range before dispatching. **There is no second fix wave** — adjudicate residuals with rulings.
3. **Verify the suite is green** after fix 7 lands — that is the one fix with a measurable effect
   beyond prose, and spec §8 item 9 depends on it. A focused run of
   `tests/test_doc_governance.py tests/test_arc_manifest.py tests/test_cockpit.py` is enough to see it.
4. **Collect every ledger line containing `Ruling:`** into the closing message — that list is the only
   place the decisions taken on the maintainer's behalf reach them. **Re-count rather than citing the
   figures in this file.**
5. **`superpowers:finishing-a-development-branch`** for the merge decision, which is the maintainer's.
   Then delete the plan's workspace — git history is the record.
