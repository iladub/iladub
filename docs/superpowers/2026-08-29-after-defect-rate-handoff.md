# Handoff — after the defect-rate measurement (`06ca823`, `1ef1ccf`)

**Pointers. Nothing here is settled because it appears here** — open what it points at.
Written at ~149k working tokens, ~3× the originating floor, which is why it is a handoff and not a
loop.

## 1. Goal

Close register rows instead of raising them. The defect rate is flat; the **raise:close ratio of
3.93 : 1** is the thing that is actually degrading, and it was measured, not felt.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/2026-08-29-defect-rate-measurement.md` | The measurement itself: 32 defects / 51 tasks over 8 loops, the variance collapse, §3 the confound it cannot dissolve, §5 what it does not say, §7 the instrument defect and its repair |
| `docs/superpowers/residues.md` (index, ~2.8k — read in full) | 141 rows, 31 closed. **An index line is a pointer, not the residue** |
| `docs/superpowers/residues-open.md` row `R151` | The one open row with a live next action AND a falsifiable prediction attached |
| `CLAUDE.md` § "Deferred residues — the register" | The conventions: the `(n/m closed)` snapshot is never updated; a closing change **strikes** the row and records evidence in place, it does NOT delete it |
| plimslop `main` (PR #3 merged, `76cf696`) | The repaired gate. `plimslop reader override` now states its own contamination on every run |

## 3. What was decided, and where that decision is recorded

- **The defect rate is flat per task — rigour, not regression.** Recorded in the measurement doc §2
  and commit `06ca823`. The operation that dissolves the apparent escalation is normalising by
  task, which CLAUDE.md's narrative record has never done.
- **The candidate 8th plan rule is NOT adopted; the stronger-model-for-specs hypothesis is NOT
  tested.** Recorded in the measurement doc §6. **Both are reversible**: they were conditional on
  the rate rising, and it did not. If a later measurement shows it rising, they reopen unchanged.
- **The `/clear` session-inheritance defect is repaired** — plimslop PR #3. Recorded in
  `preflight._session`'s docstring, `reader._inherited`, the README, and measurement §7.
- **NOT decided anywhere, and carried forward from the previous handoff:** whether iladub should
  have a branch-protection rule requiring checks. `gh pr merge --auto` is a no-op here because
  there is none. Still nobody's decision.
- **The plimslop checkout IS the live installation** (`~/.local/bin/plimslop` symlinks into it;
  both hooks run with `PYTHONPATH=` it). Recorded in the auto-memory, nowhere in either repo.

## 4. Unverified or assumed

- **8 cases were excluded from the defect count as ambiguous.** The largest is L4's plan §0 — four
  measured corrections to a committed spec, found at plan-authoring time rather than in execution.
  Counting them takes L4 from 0.14 to 0.71 and removes it as an outlier. **That single judgement is
  the one most able to move the result**, and it was made by a subagent, not adjudicated.
- **L5 and L6 may undercount.** L5's task commits carry empty bodies; the per-task subagent reports
  live in untracked `.superpowers/sdd/`, which was not read.
- **A zero may measure looking, not quality.** The two lowest-rate loops are the two with the
  weakest evidence of adversarial attention. The data refuses "the rate is rising"; it does not
  establish the converse, and no one has tried to.
- **The register trend covers only the last 40% of the register** — 84 of 141 rows predate the
  snapshot convention (R95, 2026-08-12).
- **The `/clear` detector has a known false-positive mode**: a session whose last recorded turn is
  the one before the decision. Its live reading is 11 of 49; how many are false is not measured.
- **Whether closing rows is even the right remedy is NOT decided.** The alternative — cutting rows
  that no longer bite — was raised in the previous handoff about `R150` and never ruled. Cutting is
  not closing, and the register's own convention says a closure records evidence of repair.
- The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`. This session ran past it.

## 5. The next concrete action

**Open the register index, pick the rows whose closure would be a *repair*, and close them — in a
fresh session, starting with `R151`.** Its row carries a prediction that must be run **first**: the
ablation that refuted the `holon:02 → holon:01` edge on 2026-08-22 should now **fail to reproduce**,
because the membrane shipped since refuses what it used to pass. If it still reproduces, the row is
telling you something the plan did not.

**This is not a triage pass.** A row closed by tidying erases the proof of repair and silently
shrinks the denominator, which is the failure the register's own convention was written against.
