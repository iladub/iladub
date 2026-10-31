# Handoff 2026-10-31: the synthetic contract set plan is written; execute it

**Serves:** maintenance — project 1 of the contract:01 rescope; no criterion yet.

## 5. Next concrete action (written first; typed)

**Asserted** (mechanical): in a fresh session, run superpowers:subagent-driven-development on
`docs/superpowers/plans/2026-10-31-synthetic-contract-set.md`, Task 1 first, on branch
`contract-rung-spec` (PR #386 carries spec + plan + execution), worktree
`.claude/worktrees/contract-rung-spec`.

**Proposed** (may fail, found in minutes): Task 6 Step 1, the Word converter. The 2026-10-31 spike
timed out (AppleEvent -1712) saving a PDF to `/private/tmp`. If neither of the plan's two workarounds
runs without a per-run dialog, Task 6 stops and asks the owner; Tasks 1–5 and 7's non-Word parts do
not depend on it.

## 1. Goal

Build 39 fake filled-contract PDFs + 39 truth records from four local templates (spec § 4).

## 2. Where the primaries are

- Plan (above): its "Measured before writing" table pins the four URLs and sha256s; read it first.
- Spec: `docs/superpowers/specs/2026-10-31-synthetic-contract-set-design.md` (APPROVED).
- PR #386 (DRAFT).

## 3. What was decided, and where

- Execution method subagent-driven: owner, 2026-10-31, in chat; recorded in the plan header.
- No new dependency (pyproject.toml is a baseline input): the plan's Global Constraints.
- The plan's own calls (`syn:` repo-internal namespace, stdlib docx writer, the three mixed documents)
  are recorded only in the plan; the owner has not reviewed the plan's content yet.

## 4. Unverified

- Word may still have the spike's `t.docx` open, or a dialog up.
- The worktree has no `.venv`: use `../../../.venv/bin/python`, and symlink `baml_client/` only if a
  corpus run is needed (this plan needs none).
- The owner has not reviewed the four part maps; Task 2 writes them as `draft`.
