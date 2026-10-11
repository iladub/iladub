# Handoff: R299, a row is not evidence for its own admission (2026-10-11)

**Serves:** maintenance — R299 was picked by the maintainer on 2026-10-11 from
`2026-10-10-r305-corpus-baseline-handoff.md` § 5.2.

**Topic:** table reading · **Date:** 2026-10-11

Part 5 was written at about 60K working tokens, over the 50K originating floor and under the 150K
executing floor. It is graded per action for that reason.

## 5. The next concrete action, typed

0. **ASSERTED, and it blocks this PR: CI is red, and the cause is the held `tab:ClockTime` commit,
   not the row rule.** Run 38115897575 failed four synthetic tests
   (`test_boxhead_absence_site.py::test_u14_…`, and three in `test_section_repair.py`), all on
   `rep.repaired_bands == ()`. They fail identically with `main`'s `datagrid.py` restored, and pass
   with `main`'s `celltype.py` restored. Measured on `multi_section_ruled_pdf`
   (`ID | Time Nom Accepted | Client | Volume`, times `15:01`): on `main` pass 1 escalates both
   bands `MATRIX_AMBIGUOUS` (0 asserted, 23 and 22 escalated) and section repair then reads two
   record tables, 18 tokens each, score 1.0. With `15:01` typed `ClockTime`, pass 1 ASSERTS both
   bands as `tab:HierarchicalTable` (19 asserted, 4 and 3 escalated, 14 cells), nothing escalates,
   so section repair never runs: score 0.8444. The held commit was never put through CI; "seven
   accepted documents byte-identical" was true and did not cover this fixture. **R299's closure in
   this branch is therefore premature**: its criterion requires `tab:ClockTime` to ship. Next step,
   PROPOSED: find why a second measure column disambiguates the matrix reading, and whether the
   14-cell hierarchical reading is wrong or the fixture's expectation is. Unmeasured. Until then
   this PR is a draft.
1. **PROPOSED, and awaiting a ruling: whether this remedy stands under the 2026-09-17 ruling** (one
   geometric attempt, then NEURAL). The shipped rule is the third variant tried on one role
   judgement (is this line a heading or a data row), after 2026-10-07's blank-as-wildcard. The case
   for letting it stand: it is typed, not geometric; it carries no count and no tolerance; and it
   removes a circularity in G1 instead of adding a criterion. The case against: three variants is
   the unbounded pattern the ruling names. The maintainer decides. If the ruling goes against it,
   the remedy is reverted and `tab:ClockTime` goes back on hold.
2. **PROPOSED: no subject is chosen.** Candidates on record: R295, R304, R83.
3. **ASSERTED: R295's row is stale as evidence.** It measures Caltrain scoring 1.0 with 3 of 4
   pages ignored. Caltrain now adopts all 4 pages at 0.9031 (`tests/corpus-baseline/`). Re-measure
   before planning against that row. Whether its subject (a score blind to a table classified
   NON_TABLE) survives on another document is unmeasured.

## 1. Goal

Refuse Caltrain's direction heading as a data row without losing a real row anywhere, and ship
`tab:ClockTime` with it (R299's closing criterion).

## 2. Where the primaries are

- The rule: `src/iladub/etkl/datagrid.py`, `derive_data_grid`, the `relaxing` set and
  `refusing_without`, with the measurement in the comment above them.
- The CI pins: `tests/etkl/test_clock_time.py`.
- The blast radius: `git diff main -- tests/corpus-baseline/` on this branch.
- The closure evidence: `docs/superpowers/residues-closed.md`, R299.
- `tab:ClockTime` and Caltrain's four recorded boxhead readings: cherry-picked from the held
  branch `caltrain-clock-time-held` (`c1f4dad`), unchanged.

## 2a. Results

- **Variant 1, leave-one-out alone (the row's proposal): refuted.** The `Train No.` row is refused
  by the every-measure universal and still nulls the heading's columns.
- **Variant 2, plus "a row the universal refuses relaxes nothing": refuted on cbh p0** (45 → 44
  rows). The lost row is a vessel line with `N/A` in col 0, the only row relaxing that column.
- **Variant 3, shipped:** only a row agreeing with the seed family in none of its non-blank measure
  cells is barred from relaxing a column for itself. Caltrain refuses the heading on all 4 pages
  (header block lines 0..4), graincorp-stem p1 keeps 77 rows, cbh p0 is identical.
- **Blast radius:** one `regenerate`, 07:07 to 07:31. Ten of eleven snapshots byte-identical.
  Caltrain 0.0 / 415 triples → 0.9031 / 35,665; all 4 pages adopt.
- **The graph was read, not only scored.** The heading is in the `datagrid-residue` surface text on
  every page; `Train No.` is label cell `lc0`; `Tamien` is `r0c0`; `6:51a` is `r0c1`.

## FALSIFICATION

Each run against `tests/etkl/test_clock_time.py`, then restored (21 passed):

- headers allowed to relax (drop `not contradicts_every_measure(h)` from `relaxing`): 4 fail;
- no row left out (`leave_out = False`): 4 fail, the former xfail among them;
- every row left out (`leave_out = True`): `test_a_lone_exception_that_agrees_elsewhere_is_kept`
  fails. Its first fixture did NOT fail here, because the heading's own word nulled the column;
  the exception cell was moved to the heading's nil-glyph column to make the test pin something.

## 3. What was decided, and where it is recorded

Nothing was ruled this session. § 5.1 is the open ruling.

## 4. Unverified, assumed, or found on the way

- **A refused row can still relax a column for other rows.** Found while writing the fixtures: the
  heading, refused for one column, nulls another column for a row below it. This is the behaviour
  before this loop too; it is not fixed and no row was raised for it.
- **A lone row that agrees nowhere is refused** and escalated. Pinned as a known cost. No corpus
  document has one today (ten snapshots byte-identical).
- The train numbers were not individually checked as column labels in the graph. `Train No.` lands
  as a label cell and the four recorded readings dispose, which is what the held branch measured.
- `tab-datagrid.ttl`'s prose for G1 was not updated to state the rule.
- cbh p0 types several columns `ClockTime` with the held commit. Its snapshot is byte-identical, so
  nothing downstream reads the difference today.
