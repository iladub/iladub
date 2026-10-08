# Handoff: loop 2, Caltrain. The header was never the blocker: a clock time was not a datatype, and typing it exposes a heading leak (2026-10-07)

**Serves:** maintenance — loop 2 of the four the maintainer ordered on 2026-10-06
(`2026-10-06-r295-grid-scope-handoff.md` § 3): Caltrain's header, reusing the ons boxhead method.

**Topic:** compile · **Date:** 2026-10-07

**Doc impact: none.**

Part 5 was written first, at about 30K working tokens, before the whole-corpus snapshot came back. § 5.0
was added at about 100K, past the originating floor, after the snapshot refuted shipping. Parts 1 to 4 are
measurements and pointers.

**No `src/` change reaches `main` from this loop.** The code is held on the pushed branch
`caltrain-clock-time-held` (`c1f4dad`), because shipping it alone makes Caltrain assert a false row ([[R299]]).

## 5. Next concrete action

0. **PROPOSED, graded low because it was reached past the floor.** [[R299]] before loop 3, if the
   maintainer wants Caltrain to read. Leave-one-out re-typing is the candidate, and it is unmeasured.
   Run graincorp-stem p1 (77 rows) and the Caltrain grid FIRST, before writing anything else. Then
   rebase `caltrain-clock-time-held`: its four recorded readings answer exactly the question that a
   correct header block asks. Whether this takes precedence over loop 3 is the maintainer's call.
1. **ASSERTED.** Loop 3, as ordered: a membrane guard so an asserted table cannot merge columns the
   author separated with rules, then check fed-h41's asserted cells against it
   (`2026-10-06-r295-grid-scope-handoff.md` § 3).
2. **PROPOSED.** [[R297]] stays a separate loop. The R296 handoff (§ 5.2) asked: if loop 2 builds a
   line-role oracle, check it on bfs p6. Loop 2 built none. The shipped ons reader read Caltrain's
   legend correctly. R297 is a donation defect (a donor's line 0 handed to continuations), not a
   reader question, so nothing here bears on it. If R297's design turns out to need a line-role
   judgement, the boxhead reader is the instrument to try first.

## 1. Goal

Caltrain's header, read with the ons boxhead method (`baml_src/boxhead.baml`, `boxhead.py`).

## 2. Where the primaries are, and what was measured

- **Why no grid.** `datagrid.derive_data_grids(caltrain, p)` returns 0 grids on all 4 pages at `542116d`.
  The modal row signature is 17 runs, all `Text`, because `celltype._cell_datatype("6:51a")` is
  `tab:Text`. No column is a measure, so G1b (`if not measures: return None`) refuses.
- **The datatype** (branch `caltrain-clock-time-held`): `tab:ClockTime` in `vocab/ontology/tab.ttl`,
  and `celltype.is_clock_time`, a format grammar: 12-hour WITH a meridiem, or 24-hour zero-padded.
  Reach was grepped over every PDF in both registers (`pdftotext -layout`, one token per line).
  It matches caltrain (1552 tokens) and cbh (229, 24-hour `07:30`), and nothing else. graincorp-stem's
  `2:50:00` durations and who's `4:11` ages do not match by construction. On cbh p0 the grid keeps the
  same 45 rows and the same 40 refusals, and its five time columns retype Text → ClockTime.
- **Whole-corpus snapshot**, `corpus_verdict_snapshot.py` before (worktree at `542116d`) and after (the
  held branch without the blank change), then `corpus_snapshot_diff.py`: **0 of 7 documents changed**,
  every hash identical. Caltrain, by `snapshot()`: 0.0 (4 × escalated KIND_NOT_SUPPORTED) → 0.88 with
  pages 0 to 3 adopted. That 0.88 is hollow. Every page's grid admits line 2, the direction heading,
  as a data row, and refuses line 4 (`Train No.`), so the header block is the title ([[R299]]).
- **The boxhead reader on Caltrain**, with the R299 remedy applied (header block lines 0 to 4).
  Four live calls (`BAML_LIVE=1 ILADUB_RECORD_READINGS=1`) were recorded under `readings/boxhead/` on
  the held branch. All four dispose with nothing refused and nothing dropped. Column 0 is labelled
  `Train No.`, and every other column carries its own train number (p0 601…631, p1 633…665,
  p2 602…632, p3 634…668). The reader filed `6XX Local`, the title and the direction heading as other
  words, and `carried_lines` = (4,) on every page.
- **The refuted remedy.** Treating Blank as a wildcard in the every-measure universal fixed Caltrain, and
  `tests/etkl/test_datagrid.py::test_the_pipeline_escalates_the_page_the_grid_reads_completely` caught
  the cost: graincorp-stem p1 77 → 71 rows. The lost rows are 13, 15, 17, 19, 20 and 24, all
  `<port> | Maintenance | SHUTDOWN | … | N/A | N/A | N/A | N/A | Accepted | (blank) | SHUTDOWN | -`.
  These are real data rows. Recorded with `plimslop mark`.
- **Tests on the held branch:** `tests/etkl/test_clock_time.py`, 17 passing plus 1 strict xfail. FALSIFICATION:
  removing the `is_clock_time` branch from `_cell_datatype` fails 10 tests, including the synthetic
  timetable grid. Restored, all green. The blank-wildcard half failed 2 tests when reverted, before it
  was itself reverted.

## 3. What was decided, and where it is recorded

- **The ClockTime grammar is general, not tuned to spare cbh.** It reaches cbh, cbh's graph stays
  byte-identical, and the grid retypes correctly. Recorded here and in the `tab:ClockTime` comment
  on the held branch.
- **ClockTime does not ship alone.** A hollow 0.88 that asserts a heading as data is worse than an
  honest 0.0 escalation (CLAUDE.md § 7). Recorded here and in R299.
- **No new line-role oracle is needed for Caltrain.** The shipped reader filed the legend correctly.
  Recorded here only.

## 4. Unverified or assumed

- Leave-one-out re-typing is a guess. Nothing was run.
- The local sweep was NOT run on the held branch beyond `test_clock_time.py` and `test_datagrid.py`.
  `test_celltype*.py` and `test_nil_glyph.py` were not run (a zsh glob error ended the loop early).
- The rotated zone labels (`4 ENOZ`, refused `unplaceable`) are a stub-spanner reading that nothing
  carries. Not registered.
- Caltrain's score after R299 is unknown. The 0.88 includes the heading row.
