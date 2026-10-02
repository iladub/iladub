# Handoff: R261 loop (b) — design APPROVED in chat; write the spec (2026-10-02)

**Topic:** r261-totals-family · **Date:** 2026-10-02

**Serves:** prog:criterion:etkl:03 — loop (b) of the R261 totals family: the grand total `1,951,264`.

**Doc impact: none.**

This handoff was written at 63.9K working tokens, which is 1.3× the originating floor. The design
below was presented and approved under that floor's pressure, at about 45–60K. The spec was not
started. Part 5 was written first.

## 5. Next actions (written first)

- **Asserted:** a fresh session writes the loop (b) spec from part 3 below, with
  `superpowers:brainstorming` at **"Write design doc"**. That means steps 6–8: write the spec,
  self-review it, then the maintainer reviews it. Run `managing-context-budget` first. Do not
  re-present the design. Re-open a section only if a seam in part 4 measures against it.
- **Proposed, and it may fail:** the plan's Task 1 is unchanged from the previous handoff
  (`2026-10-02-r261-grand-total-spec-handoff.md` part 5). Ask the P4b question through BAML on the
  same 6 cases. It holds iff `1,951,264` gets `total_of_totals` ×3 and no control gets
  `total_of_totals`. If it fails, the wording is not re-tuned and the grand total goes back to the
  maintainer as a ruling.

## 1. Goal

Bind cbh p0's `1,951,264` as a `tab:PrintedTotal` aggregating the four bound port totals. It binds
when the exact Decimal sum holds AND the worker answers `total_of_totals` on the derived crop.

## 2. Where the primaries are

- **The previous handoff:** `docs/superpowers/2026-10-02-r261-grand-total-spec-handoff.md`. Its
  part 2 lists every primary: probe evidence, probe script, R261 spec, table-level code, cbh's hold,
  R284/R287. All of it still applies.
- **The seams this design touches.** They were read at `097691e` and not run:
  - `compile._bind_printed_totals`. Today it returns early unless the previous band asserted a table.
  - `totals.match_totals`. It is written but unwired.
  - `document._printed_total_bands` and the R7 block after it. They adopt only by `tab:totalOf`
    into `adopted_tables`.
  - `tab:PrintedTotalShape` (`vocab/shapes/tab-shapes.ttl`). `tab:totalOf` has `sh:maxCount 1`
    and no minCount, so a PrintedTotal with no `tab:totalOf` already passes.
  - The `tab:aggregates` comment in `vocab/ontology/tab.ttl`, which RESERVES the fourth usage.

## 3. Decided, and where recorded

The maintainer approved every item below in chat on 2026-10-02, replying *"looks right"* to the
sectioned design. **This file is the only record** until the spec carries them, so they are
reversible.

- **§ 0, the concerns stated FIRST.**
  1. [[R287]]. The worker called an in-table cell `table_total` on the derived crop. That binds
     nothing, since only `total_of_totals` binds. But the protection the worker adds beyond the
     arithmetic rests on n = 1 target and 4 nulls, and no corpus document offers the coincidence
     class: a lone number equal to the sum of the totals that is not a grand total.
  2. Once `1,951,264` is carved out, band 9's Note is expected to classify as ignored, not read.
     Lifting cbh's hold is the maintainer's call. The loop delivers the cell dump and this
     sentence; it does not adjudicate.
- **§ 1, the mechanism.**
  - A second level inside `_bind_printed_totals`, beside the table level, not gated by it.
  - **Operands:** every TABLE-LEVEL `tab:PrintedTotal` (those carrying `tab:totalOf`) bound in
    this page's graph so far. Always the whole set, and at least 2 of them (`totals.match_totals`).
  - **This refines the earlier ruling**, which said "every PrintedTotal bound on the page".
    Excluding totals-level totals means a bound grand total never sums into a later one. On cbh the
    result is identical. The maintainer approved the refinement.
  - **Candidate:** any lone-numeric line in any later band on the page. **No adjacency
    requirement**: the arithmetic and the worker decide, and adjacency would be a position
    heuristic. The maintainer approved this explicitly.
  - **Order:** the table level is tried first on each line. A line it binds is not asked at the
    totals level.
  - **On a bind:** the same carve, and the same `printed_total` judgement with options
    `total|not_total`. The rationale is built from the arithmetic only: "totals level: the N
    table-level PrintedTotals on this page sum exactly…". The remainder is reclassified.
- **§ 2, the worker.**
  - A sibling module (working name `totalrole.py`) and the BAML function `AskTotalRole`.
  - The answer is a closed `table_total|total_of_totals|other|cannot_tell` with no note field.
    It binds only on `total_of_totals`.
  - The wording is P4b's, with only the JSON line replaced by `ctx.output_format`.
  - The crop is the DERIVED one: the union of each operand total's table band through its own line,
    plus the candidate line. **Production draws the red box.** The 4 pt margin, 150 dpi, 2 px stroke
    and 2 pt pad are the measured instrument's parameters, carried as `crop_table`'s are.
  - The recorded-readings key is the question name + value + listing, with the candidate line last.
    It is never the PNG.
  - The module mirrors `printedtotal.py`'s reader stack rather than sharing it.
- **§ 3, vocabulary.**
  - No new class. A grand total is a `tab:PrintedTotal` with NO `tab:totalOf`, whose
    `tab:aggregates` point at PrintedTotals. The `tab:aggregates` comment goes from *reserved* to
    *used*.
  - Which level a total is follows from its links; nothing stores it as a label.
  - `tab:PrintedTotalShape` gains one constraint: without `tab:totalOf` it may aggregate only
    PrintedTotals, and with `tab:totalOf` it may aggregate none. Each half ships with a test that
    must fail.
- **§ 4, the R7 extension.**
  - `_printed_total_bands` adopts a pass-2 band whose PrintedTotal `tab:aggregates` a PrintedTotal
    that is `tab:totalOf` an adopted table. That is a graph link, not adjacency.
  - The existing refusal disjuncts apply unchanged.
- **§ 5, the oracles.**
  - Plan Task 1 is the BAML probe (part 5).
  - A CI fixture covers two tables with totals, a grand line and prose. The conjunction is pinned
    from both sides:
    - `total_of_totals` with the sum holding binds;
    - `total_of_totals` with the sum failing does not;
    - any other answer with the sum holding does not;
    - with only one table total bound, the worker is not asked.
    It also covers R7 adoption, and every task carries a FALSIFICATION block.
  - In the corpus sweep only cbh may move. Any other mover is a finding.
  - cbh: the cells are dumped and the hold is left to the maintainer.
- **§ 6, not done.** Labelled grand totals, partial-set subtotals, cross-page grand totals, reading
  the Note, and R287's column-scoped crop.

## 4. Unverified or assumed

- **The R7 extension adopts band 9 cleanly.** The prediction: band 9's pass-1 record is an
  escalation with no `table_uri`, so `_remove_escalation_record` withdraws it, and the Note's pass-2
  ignored node comes in through the `_ignored_subjects` copy. This was read, not run.
- **The derived crop is computable in production.** Each operand's table band is presumed to be
  `bands[idx-1]` of the band that bound it, since the table level binds only against the previous
  band. Whether those indices are still available at the totals-level bind (pass 2) is unmeasured.
- **[[R284]] exposure.** Band 9 is a second carve on the same page, and `donor_ev` comes from the
  uncarved bands. Whether `donors_for` names band 9 is unmeasured.
- **Band 9's carve.** Line 0 of a band that interleaves in y with band 10. The table-level carve
  removes a line by index and keeps the band bounds. That it handles this case unchanged is
  unmeasured.
- **The Note reads NON_TABLE → ignored in pass 2.** Predicted from box-split evidence § 5.4(3);
  never run with the grand total actually carved.
- **The BAML wording reproduces P4b.** Unrun (part 5).
- **The context figure** is from the hook: 63,888 working above a 63,454 baseline.
