# Handoff: which non-ag-trade document can carry a contract (2026-10-12)

**Serves:** maintenance — direction (b) of the 2026-10-06 ruling (contracts and grounding), picked
by the maintainer on 2026-10-12.

**Topic:** contracts and grounding · **Date:** 2026-10-12

Part 5 was written first, at about 56K working tokens, over the 50K originating floor. It is graded
per action for that reason. No contract was authored and no `src/` was changed.

## 5. The next concrete action, typed

1. **PROPOSED: the subject is the feed's record shape for a matrix, on apple, before any contract
   file is written.** apple is the only non-ag-trade candidate measured whose labels are the
   author's (§ 2a). What it lacks is a record shape a contract can name: `feed.table_records`
   gives one record per line item with one concept per period column, the concept's `text` is the
   whole column header path (`Three Months Ended > June 27, > 2026`), and the line item lives only
   in `Record.row_id`. `ground.exact_field` compares a concept's `text` to a field's property
   local name, so the only contract that grounds today has one property per printed period, which
   is a contract for one edition of one filing. The prediction to run first, in minutes: author
   that throwaway four-field contract in the scratchpad and call `ground_document` on apple under
   the abstaining proposer. If it grounds the income statement's amounts, the grounding machinery
   is fine and the gap is only the record shape. If it grounds nothing, there is a second gap and
   this item is wrong about where the work is.
2. **PROPOSED, depends on 1: a matrix cell is an observation.** One record per cell, carrying the
   row header path and the column header path as key concepts whose text is their value (the
   population `marker_field` already serves for section markers and split keys), and the amount as
   the measure. Whether that is a third population beside `is_section_marker` and `is_split_key`,
   and what scheme a period or a line item is admitted by, is the spec's question. It is
   originating work and belongs in a fresh session.
3. **ASSERTED: who-wfa is not the document to start on.** 37 of its 56 records carry no usable
   label (§ 2a), and the cause is an open row (R166). A contract authored there would ground a
   third of the document at best.
4. **PROPOSED, low confidence: bfs and ons are not better candidates.** Their asserted tables are
   `tab:DataGrid` (3 and 2), which `table_records` did not read on 2026-09-14
   (`2026-09-14-etkl-04-not-contractable-handoff.md`). Both have gained boxhead labels since. Not
   re-measured here.

## 1. Goal

Author a semantic contract for one accepted document that is not ag-trade, and measure what
grounds and what is proposed.

## 2. Where the primaries are

- **The ruling:** `docs/superpowers/2026-10-06-held-out-corpus-handoff.md` § 3 and § 5.2.
- **The feed:** `src/iladub/feed.py`, `table_records` and `_header_path`. Establish there which
  table types are read and where a column's label text comes from.
- **The match:** `src/iladub/ground.py`, `exact_field`, `marker_field`, `ground_concept`.
- **The precedent:** `examples/shipping/capacity-{contract,terms,shapes}.ttl`, and
  `tests/test_corpus.py::test_grounding_where_contracted`, which asserts non-vacuity.
- **The class who-wfa falls in:** `docs/superpowers/residues-open.md`, R166.

## 2a. What was measured

`compile_document` at `f976a82`, each document alone, then `feed.table_records(rep.graph)`.
Scores match the committed baseline (0.9963 and 0.9419).

| document | records | label set a record carries |
| --- | --- | --- |
| who-wfa | 19 | printed labels, with the spanner split across two parents: `Z-scores (weight in > Month` … `kg) > 3 SD` |
| who-wfa | 25 | a data row, in five `htable`s: `0: 7`, `7`, `0.1134`, `8.2970`, … |
| who-wfa | 12 | thirteen empty strings, in two `table4`s |
| apple | 59 | one of two sets: `Three Months Ended > June 27, > 2026` and its three siblings, or `June 27, > 2026`, `September 27, > 2025` |

who-wfa prints 61 months. 56 records plus the five rows read as labels is 61, so no row is
dropped; five are carried in the header role.

How the 59 split between the two label sets was not counted. apple's 59 `row_id`s are the printed line items (`Products`, `Total net sales (1)`,
`Gross margin`, …). One is not a line item: `respectively`, on p1.

## 3. What was decided, and where it is recorded

- **Maintainer, 2026-10-12, in conversation:** the next loop is contracts. Recorded only in this
  file.
- Nothing else was decided. Items 1, 2 and 4 of § 5 are proposals.

## 4. Unverified or assumed

- **No `ground_document` call was made on either document.** That `exact_field` cannot place a
  period path is read from the code, not run. § 5.1 is the run.
- **That who-wfa's 25 data-row labels are R166's mechanism is assumed** from the symptom. R166's
  row counts 12 asserted record-table readings corpus-wide; whether these five `htable`s are among
  them was not checked. The 12 empty-label records are not explained at all.
- **The who-wfa spanner split** (`Z-scores (weight in` over eight columns, `kg)` over three) is one
  printed label cut by the column tree. Not looked for in the register.
- **apple's p2 cash-flow grid (87 cells) contributes no record.** It is a `tab:DataGrid`. Consistent
  with § 5.4 and not examined further.
- **`respectively` as a row on apple p1** is prose read as a line item. Not looked for in the
  register and not raised.
- **Arc and register state:** R295's closing criterion (all four Caltrain pages reach a table
  region) is met in `tests/corpus-baseline/caltrain-weekend-timetable.json`; the row is still open
  and was not touched.
