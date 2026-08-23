# Handoff — Tasks 1-4 complete and reviewed clean; Task 5 committed UNREVIEWED; Task 6 remains

**Topic:** the arc / M19 · **Date:** 2026-08-23 · **Branch:** `the-worktree-that-resolves`
**Runner:** `./.venv/bin/python`, never `python3`.
**Shape: executing, stopped at 146.6k** — at the 150k executing floor.
The ledger, not this file, is the resumption state.

## §1 Goal

Finish executing `docs/superpowers/plans/2026-08-23-the-worktree-that-resolves.md` under
`superpowers:subagent-driven-development`. Tasks 1-4 are complete with clean reviews. **Task 5 is committed but UNREVIEWED** — its review
package is already written. **Next action: dispatch the Task 5 task reviewer** (§7).

## §2 Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-23-the-worktree-that-resolves/progress.md` | **the ledger — read this first.** Pre-flight table, rulings PF-1…PF-4 plus the brief-re-extraction ruling, every task's completion line and deferred minors. Trust it and `git log` over any recollection |
| `docs/superpowers/plans/…-the-worktree-that-resolves.md` | the plan (amended: PF-4 correction is in Task 3 Step 5, PF-1 is Task 3 Step 3 invariant 5) |
| `docs/superpowers/specs/…-the-worktree-that-resolves-design.md` | the spec — the binding authority. §7 oracle 2 carries a struck-through correction |
| `…/task-{1..6}-brief.md`, `task-{1..4}-report.md` | briefs 3 and 6 were RE-EXTRACTED after the plan amendment; 4 and 5 were already current |
| `tests/test_arc_ablation.py` | M19. **Every line number in every brief is stale** — Tasks 1-3 shifted them. Locate by content |

## §3 Commits so far

| task | commits | verdict |
| --- | --- | --- |
| 1 — probe module + explicit `PYTHONPATH` on `_run_module` | `256955b..7e4f84c` | review clean |
| 2 — `_MATERIALISED`/`_declared_inputs`/`_materialise` + disjointness collision guard | `6f977b6..2d08f06` | review clean |
| 3 — `_run_control`, the un-ablated control run | `2d08f06..95bfb9a` | review clean |
| 4 — collection ERROR must name the removed artifact (R118) | `5816384..5f2cad9` | review clean |
| 5 — limitation-4 rewrite + register rows | `5f2cad9..d6b393c` | **UNREVIEWED** |
| 6 — the live run | not started | — |

`5816384` is a handoff commit I made mid-flight; see ruling 4.

## §4 Rulings made in this session (the maintainer's to undo)

1. **Re-extract each brief before dispatching it.** The six briefs were extracted at 08:03,
   *before* the PF-4 plan amendment. The on-disk Task 3 brief still carried the unsatisfiable
   falsification #1 and only five Step 3 invariants; dispatching it would have re-introduced the
   defect PF-4 had just removed. Re-extracted 3 and 6; 4 and 5 were byte-identical.
   **Cost if wrong: none** — the plan is the source of truth and the extraction is mechanical.
2. **Task 4 goes to opus, not sonnet.** The plan's own Unverified §2 named it the likeliest place
   a plan-supplied test turns out unwritable, and it needed three measured probe constants, a
   regex decision and a path-form judgment. It found two plan defects. **Cost if wrong: one
   expensive dispatch.**
3. **Removed a pre-existing leaked git worktree** (`…/T/arcci/wt`, detached `2a19171`, created
   07:04, `arcci` prefix — not from this branch's code, which uses `arc-m19-*`). **Cost if wrong:
   a throwaway detached worktree any M19 run recreates.**
4. **CONTROLLER ERROR — I committed the handoff (`5816384`) while the Task 4 implementer was
   live**, moving HEAD under a running agent. Verified no damage (`git show --stat 5816384` carries
   only that one docs file; tree clean immediately after). Consequence: Task 4's review BASE is
   `5816384`, not `95bfb9a`, so a docs file stays out of its diff. **The rule this implies: the
   controller does not commit while an implementer is live.**
5. **Task 4's one ⚠️ is routed to Task 6, not into a fix loop.** The unverifiable claim is "the
   live manifest produces 0 collection ERRORs" — it supports only the observation that the plan's
   Task 4 Step 5 rationale was wrong, not any shipped behaviour, and the reviewer separately judged
   the true positive adequately pinned by the test's first half plus falsification direction B.
   Task 6 measures it by construction. **Cost if wrong: a plan-defect note rests on one
   unconfirmed number for one more task.**
6. **Resumed the Task 5 agent after an environment failure** rather than dispatching fresh or
   handing off a dirty tree. The machine slept mid-response, leaving four files modified, nothing
   committed and no report. Its context was intact and it was mid-measurement; a fresh implementer
   would have had to reconstruct half-applied edits from a diff it did not write. **Cost if wrong:
   the resumed agent mis-remembers its own partial state** — mitigated by telling it to re-read
   `git diff` first. It resumed correctly and self-caught a register mistake.

## §5 Unverified or assumed — not empty

1. **Task 5 is UNREVIEWED.** Its review package is already written to
   `…/review-5f2cad9..d6b393c.diff` (98 KB — the register diff is large). This is the same shape
   the previous session left Task 1 in.
2. **Whether §4.1 flips any live pair is STILL UNKNOWN.** `ablation_refusals` has not been run to
   completion against the live manifest since Tasks 2-4 landed. Spec §9 predicts zero new edges;
   that is a prediction. **Global Constraint 9: a newly grounding pair is a FINDING to record, and
   suppressing it or re-tuning the instrument until `[]` comes back is the one forbidden
   response.** Task 6 settles this and it is the reason Task 6 matters most.
3. **The plan is 1168 lines against a 338-line spec** — a worse ratio than the 919-line plan
   CLAUDE.md holds up as its counter-example. It contains no function bodies (verified: zero
   non-test `def`s) and the bulk is measurement transcripts plus verbatim tests, so it is not the
   rule-1 violation the ratio suggests. **Flagged to the maintainer, not ruled on.**
4. **No adversarial review has run on the spec.** PF-4 and Task 4's two findings all came from
   that class of reading, so it is live.

## §5a What Tasks 4 and 5 measured that the plan had wrong

These are the loop's own corrections and they belong in the loop record, not only in a ledger:

- **Seam S2 is CLOSED: `--tb=line`.** The module docstring's long-standing claim (`ERROR
  tests/x.py - FileNotFoundError: …`) is confirmed in *shape* but **refuted where it matters** —
  the short-summary tail clips to terminal width (at `COLUMNS=80` the removed path is `...`), and
  on the import-error shape carries no exception at all; `--tb=no` emits no `ERRORS` section, so
  the text simply did not exist. `_PROGRESS`'s input is unchanged, measured at both widths.
- **The plan's Task 4 Step 5 rationale is REFUTED.** The live manifest produces **0** collection
  ERRORs, so `test_m19_the_live_manifest_carries_no_refuted_edge` cannot notice a never-matching
  rule, as the plan claimed it would. (Confirm in Task 6 — ruling 5.)
- **The brief's `_UNRELATED_REMOVAL` fallback is SELF-CONTRADICTORY.** It asked for "a file the
  module does not touch while forcing the same break"; since `_ablate`'s only lever is deletion, a
  removal that breaks a module's collection is by construction a removal of something it touches.
  The substituted probe (`tests/docgov_extract.py` — a removal that *does* break collection but
  whose `ModuleNotFoundError` names the dotted module, never the path) tests the real boundary and
  is harder. Verified it cannot spuriously pass: slashed is not a substring of dotted.
- **Task 2's own materialisation destroyed the brief's probe.** Materialising `baml_client`
  removed the last always-broken import — so the pair Task 4's brief assumed no longer exists.
- **Limitation 4's literal `src/`-artifact scenario is also closed by §4.1** — measured by Task 5
  beyond what its brief asked.

## §6 Deferred minors, for the final whole-branch review

- ~~Task 1: module docstring limitation 4 is stale~~ — **closed by Task 5** (`d6b393c`).
- Task 2: the `ablation_refusals` collision guard sits after the pre-existing `dangling`/`testless`
  assertions rather than literally first. Both are filesystem-free, so "before any worktree" holds;
  wording gap only.
- **Task 4, still open — the doubled stale reference.** The Task 4 test docstring cites
  `_scores:219-226`, now `:412-418`, kept verbatim per plan-authoring rule 1 and flagged. Task 3's
  docstring around `:801` carries the **same** stale reference. Task 5's brief did not cover this
  and it reported the gap. **Fix both together** — the reviewer explicitly flagged that fixing one
  and leaving the other is worse than leaving both.
- **Task 4, still open — a residue candidate never written.** Under Task 4's rule, a declared
  artifact that is a **Python module** would be genuine consumption the instrument refuses to score
  (it raises — the safe direction). Zero of the 29 declared artifacts are `.py` today. Task 5's
  brief did not cover this; it belongs in the register.
- Task 4: the report's Direction-A falsification prose describes inverting a variable that was
  inlined during self-review. Transcripts are consistent with the real code; report-only cosmetic.

## §7 The next concrete action

**Dispatch the Task 5 task reviewer** against the already-written package
`.superpowers/sdd/2026-08-23-the-worktree-that-resolves/review-5f2cad9..d6b393c.diff`, with
`task-5-brief.md` and `task-5-report.md`. Tell it: (a) Task 5 is documentation-and-register work,
so Global Constraint 8's falsification requirement applies only if a test changed — the report
should say so explicitly rather than fabricate an inversion; (b) the register convention is
**strike the full row's number, never the 3-column index** (the implementer self-caught exactly
this and reverted — verify the revert is complete, because an index strike breaks the register's
own `awk` self-verification); (c) every rewritten docstring claim must be true of the code as it
now stands, and a confidently-stated obsolete fact is the exact defect this task existed to remove.

Then **Task 6** — re-extract its brief first (it was re-extracted once already, but re-extract
again rather than trust that). Task 6 runs `ablation_refusals` live. Two things it must carry:
Global Constraint 9 (**a newly grounding pair is a finding to record, never a result to suppress
or tune away**) and ruling 5's routed measurement (**confirm the 0-collection-ERRORs count against
the live manifest**). The two §6 items Task 5 could not reach — the doubled stale reference and the
Python-module residue row — should be assigned explicitly to Task 6 or to the final fix wave;
otherwise they die here.

Finish with the whole-branch review on the **most capable model**, package built from
`git merge-base main HEAD`, pointed at §6.
