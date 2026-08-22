# Handoff — all eight tasks complete; what remains is not a task

**Topic:** process · **Date:** 2026-08-22 · **Branch:** `arc-denominator` @ `71e8d4b` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASKS 1-8 ALL COMPLETE AND SIGNED OFF.** Task 8
needed no fix round. **Four items remain, none of them a task.** Nothing is pushed.

> Written at 242k against a 150k executing floor, deliberately as a **pointer document assembled from
> the ledger** — not as new reasoning. Everything load-bearing was measured by a fresh seat and
> recorded at the time; this file only says where. Where it and the ledger disagree, **the ledger wins**.

## Goal

The strategy instrument, slice 1 — give each named rung of the arc a countable denominator and a
dependency edge to the register, so the cockpit stops printing `stage ?/5`.

**Done.** The strip now reads, measured by Task 8's reviewer rendering it:

```
arc  etkl ▰▱▱▱ 1/7  dec ▰▰▰▱ 11/17  holon ▰▰▰▱ 4/6  tab ▱▱▱▱ 1/10  substrate ▱▱▱▱ 0/3  frontier 15  ready 17
```

**17 met of 43 criteria**, with `cockpit.arc()` verified equal to `vocab/queries/arc-position.rq`'s
answer by an independent rdflib run, and `sum(declared) == 43`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST and treat it as authoritative.** Rulings 1-21, all ~37 deferred minors, every task's completion line. **Git-ignored: `git clean -fdx` destroys it** |
| `.superpowers/sdd/.../task-N-report.md`, `task-N-review.md`, `task-N-rereview-round1.md` | per-task evidence: TDD, FALSIFICATION blocks, and the reviewers' independent re-derivations |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — **binding authority, and now carrying three measured errors** (see the ledger's dead-claim list) |
| `docs/superpowers/2026-08-21-arc-task7-handoff.md` | the previous handoff. Current on Rulings 13-19 and on the suite recipe's rationale |
| `docs/superpowers/2026-08-20-arc-task3-handoff.md` | the detached-worktree suite recipe, still correct |

## The four remaining items, in order

1. **Raise the two residue rows.** Both exist **only in prose on this branch** and vanish with it if
   unraised — the exact condition **R106** was raised to prevent, so leaving them is the defect the
   loop just documented.
   - **The duplicate-key `prog:Rung` gap.** pySHACL returns `Conforms: True` on a graph with two rung
     nodes sharing one `rungKey`; `prog:RungShape` constrains the value per node and nothing counts
     nodes. **Attach Task 8's note:** `arc()`'s regex reader is immune for a *different* reason than
     `arc-position.rq` is, so the two readers would still agree on such a manifest — *"that is luck,
     not design."* Task 7's re-review confirmed the decline to fix it inside a fix round was **sound
     scoping**: `_refused_by_shacl` asserts an **exact set** of refusal numbers, so an eleventh
     refusal moves a contract owned by Tasks 2 and 6.
   - **The M7-state gap.** A `prog:blockedBy` naming a **closed** register row is admitted — M7 checks
     presence, not state. **R105 is now exactly such a row**, so this is live, not hypothetical.
2. **The whole-branch review**, on the most capable model, over `f436a8c..HEAD`
   (`scripts/review-package PLAN f436a8c HEAD`), pointed at the ledger's **~37 deferred minors** and
   the **one parked finding (I-1)** so it can triage what blocks merge. Two of those minors harden M10
   itself; one is the R105-family follow-up (`prog:oracleArtifact` carries the same `<path>:<line>`
   grammar and M5 *strips* the line rather than checking it).
3. **Both suite legs at the final head.** The last non-corpus green is `1235 passed / 7 skipped /
   1 xfailed / 10 warnings` at `71e8d4b`, run by Task 8's implementer **in the main working copy**
   (Ruling 20). **The corpus leg has not run since `170be91`** — Tasks 6-8 touch no `src/`, so it
   should be unaffected, but the review owes the run. Worktree recipe: detached worktree,
   `baml_client` + `corpus` **symlinked in** or six modules fail to collect and the run is a FALSE RED.
   **The 10 warnings are still unattributed** — sampled as rdflib `ConjunctiveGraph is deprecated`
   from the JSON-LD parser, i.e. a dependency deprecation, but the count has been reported without
   explanation since Task 1.
4. **`superpowers:finishing-a-development-branch`** — the merge/push decision, which is the
   maintainer's. **Nothing on this branch is pushed.**

## Decisions taken on the maintainer's behalf, and where each is recorded

**All 21 rulings are in the ledger with their cost-if-wrong.** The four worth knowing without opening it:

- **Ruling 18 (François's own decision, 2026-08-21)** — M10 shipped in Task 6 rather than deferring a
  third time. Landed; **R105 closed**.
- **Ruling 19** — the `arc-orphan` seam was stated *as a seam* and deliberately **not answered** for
  the implementer. Confirmed by measurement: the query was genuinely underivable as the plan wrote it.
- **Ruling 20** — Task 8 was permitted the full non-corpus leg **in the main working copy**, because
  the do-not-run rule guards a *worktree* artefact (the symlink FALSE RED) that does not apply there.
- **Ruling 21** — **I-1 parked, not fixed.** `.claude/settings.local.json` composes the context gauge
  with cockpit, so **the maintainer's live strip is THREE rows, not two, and nobody has seen it
  rendered.** No code change was dispatched: the file is gitignored and machine-local, outside this
  branch's diff, and the fallback is already recorded in the test docstring — compact single line,
  fractions behind `--verbose`, **never abbreviated rung names**. **This one is a taste call for the
  person who reads the strip daily.**

## Unverified or assumed

- **The corpus leg has not run since `170be91`.** Item 3 above.
- **The 10 warnings pre-date this branch but have never been attributed.** Item 3 above.
- **A controller measurement error is in the record** (Task 7's dispatch named the wrong test as the
  policeman of `vocab/queries/`, and the path it gave does not exist; the real one is
  `tests/etkl/test_transform_gate.py::test_no_tuned_constant_in_rq_files`). Kept deliberately, on the
  same footing as a plan defect.
- **Seven dead plan/spec claims** are listed in the ledger, three of them in the **spec**. The
  seventh — step 1's `<urn:iladub:arc:crit:` — would have produced an `arc()` reading zero criteria
  **that the honesty test would have passed**, and was caught in the brief before dispatch.
- **The most consequential measurement this loop produced is not about the arc**: **59 of 74 open
  residue rows block no criterion of any rung**, where spec §7.4 called R101 "the first instance."
  Confirmed twice, element for element. That is 80% of the open register serving no stated goal — not
  a criticism of the register, but the first time anything could count it.
- **The pre-flight conflict scan was never independent** — the plan's author scanned it, and it missed
  seven dead claims.
- **This session ran 74k → 242k**, crossing the 150k executing floor at Task 7's report; the override
  is logged. Past the floor it dispatched verbatim findings, ledgered outcomes, ran suite legs, and
  composed two dispatches. **It authored no spec, plan or design.** The two dispatch compositions are
  the only real judgment done past the floor and are the thing to re-check if Task 8 or the `tab` rung
  turns out wrong.

## The next concrete action

In a **fresh session**: read the ledger, then **raise the two residue rows** (item 1) — they are the
only thing on this branch that disappears if the next seat starts somewhere else.
