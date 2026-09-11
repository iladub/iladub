# Handoff — the register serves the arc: the plan is written; execute it

**Topic:** register-serves-arc
**Serves:** maintenance — the loop moves no criterion; it changes how the next subject is chosen.
**Date:** 2026-09-11. **Loop shape:** originating (a plan, no code), written at ~32K working
tokens, under the 50K floor. **Doc impact: none** (the plan declares its own).

Part 5 written first.

## 5. The next concrete action

### 5a. ASSERTED — execute `docs/superpowers/plans/2026-09-11-the-register-serves-the-arc.md`, tasks 1–4, in a fresh session

The plan is a contract: signatures, invariants, tests verbatim, a `## FALSIFICATION` block per task,
and every load-bearing claim measured inline in its § Measured table. Task 1 first (the graph script
drops R131 and R141 today); tasks 2–4 in order. **Do not re-plan.** Tasks 5 and 6 are gated on the
maintainer being present and are not started by an agent.

Two things the executor will hit that the plan already names, so they are not surprises:
`test_the_work_line_degrades_on_a_detached_head` needs `serves` monkeypatched once `work()` grows a
segment (task 2 step 3), and the M21 fixture must name a row that exists live and is `prog:met false`
(task 4 step 1).

### 5b. PROPOSED — the candidate set is 80, and the maintainer parks fewer than half

Spec § 3.3 says 78; the plan measured 80 once the two qualified rows are readable. The task-4 test
pins 80 against an independent derivation. **Prediction, to be run at task 6:** the maintainer parks
under 40 of the 80. If they park most of them, PARKED is doing the work a `closed`-by-ruling state
would do and the spec's "never a closure" line should be re-argued.

### 5c. PROPOSED — spec § 3.2's prediction, carried forward unchanged

Once `serves a/m/–` renders (task 3), the criterion count in the window leaves zero within three
loops, or § 4's fork is the remedy. Baseline at this handoff: `serves 0/2/34` predicted for the
7-day window (this handoff and the spec's declare `maintenance`); re-measure, the window slides.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the plan | `docs/superpowers/plans/2026-09-11-the-register-serves-the-arc.md` | § Global Constraints; § Measured (every figure with its command); tasks 1–6 |
| the spec | `docs/superpowers/specs/2026-09-11-the-register-serves-the-arc-design.md` (PR #201) | § 3.1–3.3 the rules and oracles; § 4 the maintainer's fork; § 7 the task list the plan expands |
| the predecessor handoff | `docs/superpowers/2026-09-11-the-register-serves-the-arc-spec-handoff.md` | its 5b/5c propositions; its part 4 "unverified" list, two of which the plan now settles (below) |
| the readers the plan extends | `scripts/cockpit.py` (`topic()` `:306`, `work()` `:326`, `_CRITERION` `:188`), `scripts/residue_graph.py:43`, `tests/test_residue_register_integrity.py:40`, `tests/test_arc_manifest.py:294-336` | the seams each task names |

## 2. What was measured this session (branch `the-register-serves-the-arc-plan` off `f1129a9`)

All in the plan's § Measured table with commands. The ones that changed a decision:

- `residue_graph.py` reads **196** index rows, 133 open; the integrity regex reads **198 / 135**;
  the two dropped are R131 and R141. With them restored the structural parking candidates number
  **80**, not the spec's 78.
- `_criteria()` drops a criterion with no `prog:met` (`cockpit.py:225-226`), so `serves()`'s
  membership check reads `_CRITERION` matches directly.
- `residues()` is unpacked as a 3-tuple at **five** sites, so the parked count is a sibling
  `parked()`, not a fourth element — the one stated deviation from the spec's letter.
- The arc line may carry **no digit** with no manifest (`test_cockpit.py:132`), so `serves` renders
  `?` there, like `frontier`.
- M20 is reserved for R116 (`specs/2026-08-23-the-faithful-worktree-design.md:264`); **M21** is the
  parked-blocker refusal.
- PR #200 merged (`72a608a` on `main`); PR #201 (the spec) was `BLOCKED` with `test` in progress
  when this branch was cut, so this branch is stacked on it.
- `pytest tests/test_doc_governance.py tests/test_cockpit.py tests/test_residue_register_integrity.py`
  with the plan and this handoff on disk: see the PR description for the figure.

## 3. What was decided, and where that decision is recorded

- **`serves()` reads the first token after `**Serves:**`** — plan task 2, Invariant (a); reason: the
  one live line (`…-spec-handoff.md:4`) writes `maintenance — <why>`.
- **A refused `Serves:` value counts with the absent ones in `serves_window()`** — plan task 3,
  Invariant (a); reason: a fourth bucket is a verdict about prose.
- **`serves ?` with no manifest** — plan task 3; reason: the existing no-digit pin and `frontier`'s
  own refusal.
- **`parked()` beside `residues()`** — plan task 4 and § Self-review; reason: five unpack sites.
- **The refusal is M21** — plan § Measured; reason: M11 and M20 are reserved.
- **The candidate set is 80** — plan § Measured and task 4's test; supersedes the spec's 78, which
  is Evidence and stays.
- **Nothing in CLAUDE.md, the register, or the code was changed.** Task 5's proposed CLAUDE.md
  text is in the plan, and only there, until the maintainer asks for it.

## 4. Unverified or assumed

- **Every plan-supplied test is a proposition** (CLAUDE.md § Plan authoring rule 1): none has been
  run. The integrity fixture tests in task 4 are predicted to pass before any code changes; the plan
  says to record that rather than treat it as a defect.
- That the M21 fixture, a copy of the M7 one naming `R1`, is SHACL-clean and earns no M10: the M7
  fixture's `prog:source` pointer (`…-denominator-design.md:423-424`, file has 599 lines) resolves
  today; not re-run through the environment leg.
- That `work()`'s width tolerates a fourth segment (inherited from the spec handoff's part 4). Line 1
  already reads `register-serves-ar · the-register-serves-the-arc- · the-register-serves-the-` on
  this tree; `maintenance` adds 14 characters. Not measured against any renderer limit.
- The plan's line count (722, 3.3 per spec line) was not audited for restatement beyond the
  self-review; rule 6's grep check is the reviewer's.
