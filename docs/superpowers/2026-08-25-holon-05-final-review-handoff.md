# Handoff — `holon:05`, one open fix then the final whole-branch review

**Topic:** the `holon:05` membrane-health loop — Task 7's open Important finding, then the final
whole-branch review.

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Shape: mechanical** — pointers only.
It restates nothing from the primaries and settles nothing they settle.

**Why this exists:** written by the **fourth** controlling session at ~174k tokens, past the 150k
executing floor with the override logged. **All seven tasks are shipped. Tasks 1–6 are complete and
reviewed. Task 7 is reviewed and APPROVED but has ONE Important finding open** — the maintainer
directed that the fix loop not be started in this session. This supersedes
`2026-08-25-holon-05-task-7-handoff.md`, which is spent.

## Goal

One line: **fix Task 7's one open Important finding, then run the final whole-branch review** of
`docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md`, under
`superpowers:subagent-driven-development`.

## Where the primaries are, and what to establish at each

| primary | what to establish there |
|---|---|
| `.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md` | **THE LEDGER — read this FIRST and in full.** The recovery map: the pre-flight scan, rulings R-PF1–R-PF4, every task's completion line, the **fifteen** deferred minors, and every `Ruling:` line. Tasks with a `Task N: complete` line are DONE — do not re-dispatch. |
| the same directory's `task-7-report.md` | Task 7's nine falsifications, its four non-reproducing brief values, and the edge-deletion reasoning. |
| the same directory's `review-b314c23..ae5fefd.diff` | The package the Task-7 reviewer read. |
| the plan | § Global Constraints, § Measurements M1–M9, § Named seams. |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.9, §7, §8, §9, §11. |

## The one open finding — this is the first action

**`docs/superpowers/residues.md:261`** — R137's **index** line reads *"The only guard is M7, and it
covers only the **~15** rows a `prog:blockedBy` names."* Measured by the reviewer:

```
$ grep -oE 'prog:blockedBy +"[^"]+"' tests/arc-manifest.ttl | grep -oE 'R[0-9]+' | sort -u
R43 R44 R45 R71 R74 R79 R97            → 7 distinct residues
$ grep -cE 'prog:blockedBy' tests/arc-manifest.ttl        → 11 statements
```

Neither is `~15`; the figure overstates the guard's coverage by roughly 2×. **The fix is one token:
`~15` → `7`.** The **detail** row in `residues-open.md` is clean — it states the scope qualitatively
and carries no number, so it needs no edit.

This matters more than its size: it is the branch's own named failure mode — a count made from
reading — committed into an **index** line, which is exactly the artefact CLAUDE.md § Deferred
residues records being consumed as fact (the R87/R88 case).

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
- **`tests/test_corpus*.py` has never been run on a pinned commit of this branch.**
- **A CONTROLLER CALL IS OWED, and the reviewer named it as one:** whether **R135's remedy should also
  close R117**. They are the same defect class in two artifacts; R135 cross-references R117 and states
  the distinction. Two rows or one amended row is the maintainer's call, not a Task 7 defect.
- **Fifteen Minor findings are deferred** across Tasks 2–7, each on its own `minor (deferred):` ledger
  line. Three deserve the final review's attention: the false *"consumes no population either"* claim
  **shipped in source** at `tests/etkl/test_vacuity_registry.py:~410-412`; Task 3's Minor 4 (one
  argument derived in three places — the code-comment analogue of CLAUDE.md plan-rule 6); and
  `register_rows()` at `tests/test_arc_manifest.py:237` not matching a struck `~~Rn~~` index row, a
  latent instance of the very class R137 names.
- **The register is now 127 rows / 25 closed / 102 open, next free number `R138`.** Ten pre-existing
  gaps (17, 21, 22, 41, 69, 70, 73, 75, 81, 82) are inherited, not introduced.

## The next concrete action

**In a fresh session: read the ledger FIRST and in full — it is the recovery map.**

Then, in order:

1. **Fix the one open Important finding** above (`~15` → `7`), dispatched to an implementer, not fixed
   in the controller session. Then one scoped re-review
   (`scripts/review-package PLAN ae5fefd HEAD`), and Task 7's completion line.
2. **Run the final whole-branch review** on the most capable model, over
   `git merge-base main HEAD`..HEAD (merge-base is `18226e7`), using
   `superpowers:requesting-code-review`'s `code-reviewer.md`, pointed at the ledger's
   `minor (deferred):` and `Ruling:` lines so it can triage the fifteen.
3. **One fix wave only**, then one scoped re-review; adjudicate residuals with rulings.
4. **Collect every ledger line containing `Ruling:`** into the closing message — that list is the only
   place the decisions taken on the maintainer's behalf reach them.
