# Handoff: box-split Task 3b — reviewed; one spec defect, one maintainer ruling (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh is not accepted until `#table9` compiles as the two tables the author drew.

**Doc impact: none.** Authored at ~130K working tokens by the SDD controller: past the originating
floor, under the executing floor. Parts 1–4 are pointers, and part 5 is graded per action.

## 5. Next actions (written first)

- **Asserted:** in a fresh session, resume `superpowers:subagent-driven-development` on
  `docs/superpowers/plans/2026-09-28-box-split.md`, workspace `.superpowers/sdd/2026-09-28-box-split/`.
  Read `progress.md` first. Task 3b is **implemented and reviewed** (`db47fde`), but not complete.
- **Asserted (controller ruling, in the ledger):** Task 3b fix round 1 amends spec § 8.2. The
  witness is evaluated over the **cells the re-bucket actually forms** (`rule_aware_lines`), not over
  the author's rule intervals. The reviewer's two scratch counter-examples become CI negatives:
  interior-only rules fusing `AB|CD`, and R154's dropped divider under a straddling word.
  Re-run MEASURE (i). The flip set must stay `{cbh p0 T1}`.
- **Proposed, and it may fail:** that the cell-level witness keeps cbh T1 witness-free. T1's formed
  cells were measured as the 7 correct cells (M3 control, the Task 3b report), so it should.
  It has not been run.
- **Needs a MAINTAINER ruling before O2 can XPASS:** after 3b, T1 classifies `RECORD_TABLE` with 7
  cells, but `compile_tables` escalates it as `MULTI_TABLE_AMBIGUOUS`. `segment.is_multi_table_ambiguous`
  makes a widest-gutter cut at x≈140 and sees an own-stub on the right half. That code is outside
  § 8.0's lift. See the Task 3b report § "O2 diagnosis".

## 1. Goal

Make O2 (`tab:12`) XPASS, so that the box split ships compiling.

## 2. Where the primaries are

- Ledger `progress.md`: the Task 3b report and review lines, and both `Ruling:` lines.
- `task-3b-report.md`: MEASURE (i)/(ii), FALSIFICATION, the corpus sweep, the O2 diagnosis.
- `task-3b-review.md`: the Important finding with its two scratch cases, and 4 minors.
- Spec § 8: `docs/superpowers/specs/2026-09-28-box-split-design.md`. § 8.2's "absence is a proof"
  is the refuted claim.
- Code: `src/iladub/etkl/fusion.py`, `vocab/queries/rebucket-fuses.rq`, and the `_under_resolved`
  guard in `compile._build_ruled_band`.

## 3. What was decided, and where it is recorded

- The § 8.2 amendment (the witness reads formed cells) is a controller ruling, recorded in the
  ledger. It is not yet in the spec.
- The four minors are deferred in the ledger. One of them is the unbounded query cost: a large
  witness-free band takes ~65 s. It needs a register row at Task 5.

## 4. Unverified or assumed

- The cell-level witness has not been built or measured.
- The full suite has not been run after `db47fde`.
- Four cbh corpus test files are red and not re-pinned. `test_cbh_e2e`'s 3 failures predate 3b,
  per the implementer's baseline run.
- The workspace (`.superpowers/`) is gitignored: the report, the review and the ledger are not durable.
