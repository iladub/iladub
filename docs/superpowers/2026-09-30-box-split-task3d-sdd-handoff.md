# Handoff: box-split Task 3d, SDD mid-flight (2026-09-30)

**Topic:** box-split · **Date:** 2026-09-30

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none** (this handoff).

Written at ~111K working tokens (plimslop hook), as an umbrella under the 150K executing floor —
before it was needed. The SDD ledger is the live record; this file only points at it.

## 5. Next action (written first)

- **Asserted.** Resume `superpowers:subagent-driven-development` on
  `docs/superpowers/plans/2026-09-28-box-split.md`, Task 3d, from the ledger's **"Session 10"**
  block in `.superpowers/sdd/2026-09-28-box-split/progress.md` (gitignored). Its last lines say
  which sub-task is complete, which is mid-review, and which fix round is queued. Briefs are built by
  `bash .superpowers/sdd/2026-09-28-box-split/mkbrief.sh 3d.N` (the 3d.2, 3d.6 and 3d.7 briefs carry
  appended controller rulings — regenerate only 3d.3–3d.5 if the plan changes, or re-append).
- **Proposed, and it may fail:** 3d.7's T2 answers `0`. A `1` is O2's finding (plan 3d.7 Step 1),
  and it also leaves four shapes idle in `test_vacuity_registry` (plan amendments, 3d.1).

## 1. Goal

Task 3d executed and reviewed, 3d.0 → 3d.7, then Task 4 Steps 4–5, 5, 6.

## 2. Where the primaries are

- **Plan:** Task 3d plus "Task 3d — amendments after review (2026-09-30)" (`f41ff6d`).
- **Spec:** `docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.5, § 10.7.
- **Ledger:** `.superpowers/sdd/2026-09-28-box-split/progress.md`, "Session 10" block — pre-flight
  scan table, rulings, per-sub-task status. Reports and reviews sit beside it
  (`task-3d.N-{brief,report,review}.md`).
- **Evidence:** `docs/superpowers/2026-09-28-box-split-evidence.md` § 3 (3d.0's baseline, `84827f5`).

## 3. What was decided, and where it is recorded

- **A6 split in time** (controller ruling): 3d.2 measures merge-in with a band's pre-existing
  decisions; the statement-carrying U14 merge-in case is 3d.6's. Ledger + the 3d.2/3d.6 briefs.
- **`BoxheadAbsenceDecidedShape` also requires the `header_lines` judgement** (controller ruling,
  from 3d.1's review M1). Ledger only — reversible.
- Everything else is in the plan's amendments block.

## 4. Unverified or assumed

- Whether band decisions reach the document graph on `/r2` / `/adopt` merge-in (A6) — 3d.2's
  measure, pending when this was written.
- The 89 `tests/etkl` files outside 3d.1's measured set have not been run since `bf7057f`.
- Pre-existing red at `84827f5`, claimed by 3d.1's implementer, not re-run by the controller:
  `test_o3_no_page_loses_asserted_ink_to_a_merge` (cbh 43 < 54), `test_typing_equiv[cbh]`.
- Traps: implementers stall when they background pytest; corpus runs serial; `uv.lock` appears
  under `uv run`; two concurrent writers must never share this checkout.
