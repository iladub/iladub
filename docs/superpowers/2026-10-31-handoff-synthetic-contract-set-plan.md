# Handoff 2026-10-31: the synthetic contract set is designed and approved; the plan is next

**Serves:** maintenance — project 1 of the contract:01 rescope; no criterion yet.

## 5. Next concrete action (written first; typed)

**Asserted** (mechanical): in a fresh session, run superpowers:writing-plans on
`docs/superpowers/specs/2026-10-31-synthetic-contract-set-design.md` (APPROVED 2026-10-31). The
plan's first task re-fetches the four templates (GAFTA 48, 79B, 124 and the USDA charter party),
records their sha256, and measures the three facts the spec leaves unmeasured: AcroForm fields or
none (§ 4.3), blanks in No. 124 (§ 4.2), and the survey's table figures (§ 4.1).

What could change the plan, found in minutes: if No. 124 has no blanks, the count drops from 36 PDFs
to 27 and 124 appears only in mixed documents; this is already written into § 4.2.

## 1. Goal

Make fake filled contracts on real templates, in three flavours, with generator-written truth, for
the document router (project 2) and contract compiling (project 3).

## 2. Where the primaries are

- The spec above; its § 5 lists the ten owner decisions, and each other statement is marked (call).
- The brainstorm that led to it: `docs/superpowers/2026-10-31-handoff-document-router-brainstorm.md`.
- PR #386 (DRAFT) carries this branch, `contract-rung-spec`.

## 3. What was decided, and where

All recorded in the spec § 5: the set comes before the router; the contracts are fake (never
enforced, reproduced or shared), which settles licensing; the generator, fill specs and truth are
committed, and the templates and PDFs are not; the Word flavour uses the template's real text,
extracted at build time.

## 4. Unverified

- The machine has Microsoft Word but neither LibreOffice nor pandoc (measured 2026-10-31); the Word
  converter is the builder's choice, and Word automation on macOS is not portable.
- The worktree has no `.venv`; use the main checkout's or symlink it.
- After the spec, projects 2 (router) and 3 (contract:01) are each brainstormed, one at a time.
