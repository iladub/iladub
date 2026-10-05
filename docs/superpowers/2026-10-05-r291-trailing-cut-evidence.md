# Evidence + handoff: the trailing-notes cut reads every grid (R291 closed); a census shows main already carries 7 absent tokens (2026-10-05)

**Serves:** prog:criterion:etkl:03 — R265 is sequenced before R289, the named blocker on lifting cbh's hold.

**Topic:** r291-trailing-cut · **Date:** 2026-10-05

**Doc impact: none.**

Branch `r265-grouped-numbers` (draft PR #303) now carries R265, R290 and R291's fix. **R291's cause is
located and fixed**: it was not R265's typing reaching band formation directly. The trailing-notes cut
still read ONE grid per page. **The census the R290 handoff prescribed was run on `main` first, and
`main` already fails it**: 7 literals, all pre-existing, none of them R291's (§ 2.3). Part 5 was written
at about 105K working tokens, under the 150K executing floor; it is graded per action.

## 5. Next concrete action (written first)

1. **ASSERTED: finish the corpus sweep (§ 4), re-pin from its output, then take #303 out of draft.**
   The 496-cell pins (`tests/test_carriage.py:71`, `tests/etkl/test_run_merge_seam.py:466`) count
   ONE p5 grid and are expected to read 270. Re-pin them from the run, never by arithmetic. If
   `test_corpus.py` moves bfs off 0.9021428571, #303 stays held and that is the subject.
2. **PROPOSED: the next subject is R292, the ruled rebuild fusing words across a column gap.**
   Evidence: § 2.3; ons p7/p8 carry `aSources:` and `dataset01633` on `main`. What may be wrong:
   R292 is ONE instance of the class (the census sees two literals of it). Whether the remedy belongs
   in the joiner (`geometry`, R13's "a large gap with no space glyph does not split"), in
   `rebucket-fuses.rq`'s witness (blinded by full-width lines in the same band, § 2.2), or in not
   rebuilding a prose band at all is NOT decided. Separating a 64 pt gap from +0.30 kerning by
   magnitude needs a tolerance, which §8 forbids. So the first step is to design the evidence
   (pdfplumber's own word split? the line's other words?), not to code. That is originating work, so
   start it in a fresh session.

## 1. Goal

Locate and remove the `20208` token R265 put into bfs p5's band text (R291), so #303 can merge.

## 2. Findings

### 2.1 The cause (traced, both trees)

`compile.page_bands` → `trailing.cut_trailing_notes(segment(band), …)` → `_build_ruled_band`.
Instrumenting `_build_ruled_band` on bfs p5:

| tree | sub-band in | lines | rebuilt line 0 |
|---|---|---|---|
| `4379fbe` | `2020 8 606 033 …` | 4 | `2020 8 606 033 …` |
| R265 + R290 | `2020 8 606 033 …` | **8** (rows + `Sources:` + 3 footnotes) | **`20208 606 033 …`** |

`cut_trailing_notes` called the single-grid `derive_data_grid`. Under R265 the seed winner on p5 is
the canton table (R290), which admits none of the year rows. `trailing_refused` therefore finds no
admitted line above the notes, and does not cut. The fusion is a symptom of the uncut band.

### 2.2 Why the existing fusion guard did not refuse it

`_build_ruled_band` already asks `vocab/queries/rebucket-fuses.rq` whether a formed cell holds a
point that no word of ANY line of the band covers. The three footnote lines run the band's full
width and cover every gap, so the witness has nothing to find. Once the notes are cut, the band is
4 lines again and the rebuild does not fuse. The blind spot remains for any ruled band that keeps a
full-width line (§ 2.3, R292).

### 2.3 The census (the oracle R291's row names), run on `main` first

`scripts/carried_token_census.py`: every whitespace token of `tab:cellText`, `etkl:bandText` and
`iladub:surfaceText` must be a token of its page's `extract_words`, or a run of words on one
`text_lines` line whose glyphs abut (gap ≤ 0). The abutment clause was added after the first run
flagged 132 cells that ARE on the page: pdfplumber splits graincorp-stem `1`|`5,000` (gap −0.08)
and apple `2`|`2,067` (gap 0.0), which the glyph joiner reads as one token.

| graphs | findings | which |
|---|---|---|
| `4379fbe` | 7 | 5 `surfaceText` (bfs p4, p5 ×2, p6; ons p7) = **R262**; 2 `bandText` ons p7/p8 `aSources:`, `dataset01633` = **R292** |
| this branch, R291 fixed | 7 | identical to `main` |
| control: R265 + R290 before the fix (bfs replaced) | 8 | the 7, plus bfs p5 `#ignored5` `20208 20218 20228 20238` |

ons p7: `a` (x1 218.3) and `Sources:` (x0 282.0) are 64 pt apart on one line of a two-column prose
footnote block. The same `_build_ruled_band` trace shows the input line holds them apart and the
rebuilt line fuses them.

### 2.4 Whole-corpus graphs (canonical hash, blank nodes normalised)

Against `4379fbe`: apple, cbh, graincorp-capacity, graincorp-stem, ons, who are **IDENTICAL**. bfs
changes (16778 → 16940 triples): the p5 grid becomes `#p5-datagrid` + `#p5-datagrid-2` (R290), and
the delta is confined to `p5/adopt#…` subjects.

### 2.5 R265's close condition (re-measured)

bfs p5's year band, row 0 `2020 | 8 606 033 …`, through `rowzero.row_zero_differs`: **True** on
`4379fbe` (the false witness R265 names), **False** on this branch. The band is a 4-line
`RECORD_TABLE` again on both trees.

### 2.6 The test (falsified)

`tests/etkl/test_trailing_notes.py`: `test_the_notes_are_cut_under_the_grid_whose_row_they_trail_r291`
(offline, runs in CI) and `test_bfs_p5_year_rows_are_cut_from_their_notes_r291` (corpus). With
`trailing_refused_in_grids` reading `grids[:1]`, both fail (`0 == 2`; band text carries `20208`).
Restored: 10 of 10 pass.

## 3. Decided, and where

- R291 is closed: `residues-closed.md` and the `residues.md` index.
- R292 is raised: `residues-open.md` and the index.
- `donation.head_line_refusals` keeps the single-grid call. A donor's line 0 can carry a different
  refusal in each grid, and no evidence picks one (unlike the trailing cut, where the admitted row
  above does). Recorded only here; no measured case exists.
- R265 closes only with the sweep (part 5, item 1). Recorded here and in R265's row.

## 4. Unverified or assumed

- **The corpus sweep.** 47 corpus-referencing test files, run one per process from
  `tests` files matching corpus paths. Its outcome is appended below as an addendum when it ends.
  Files that reach the corpus only through a helper are not in that list.
- bfs's document score on this branch is read from `test_corpus.py` in the sweep, not from a snapshot.
- The census reads three predicates. `rdfs:label` and decision rationales were not checked.

## 2b. Where the primaries are

- Code: `src/iladub/etkl/trailing.py` (`trailing_refused_in_grids`, `cut_trailing_notes`).
- Instrument: `scripts/carried_token_census.py` (takes an N-Triples directory or compiles `corpus/`).
- Commit `f1f876f` (the fix and tests).
