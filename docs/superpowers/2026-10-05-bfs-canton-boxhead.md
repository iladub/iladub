# bfs canton grid: the boxhead is recorded, and R293 is ruled the last fix before acceptance (2026-10-05)

**Serves:** prog:criterion:etkl:05 — lifts one of the three bfs holds recorded in `2026-10-05-bfs-hold-reread.md` § 2.4, and records the maintainer's ruling on the other two.

**Topic:** bfs-hold · **Date:** 2026-10-05

**Doc impact: none.**

No `src/` change. One recorded reading (`readings/boxhead/eb6ba439….json`) and one manifest
reading. Part 5 was written at about 71K working tokens, past the 50K originating floor, so it is
graded per action.

## 5. Next concrete action (written first)

**Ruled by the maintainer, 2026-10-05: fix [[R293]], then accept bfs with [[R294]] recorded as a
defect.** R294's two figures are escalated, not lost and not fabricated. R293 is not ruled
acceptable as it stands, because it is a column-identity defect and not only a role defect: c7
and c8 both read `Rapport de`. ons, apple, and now p5's canton grid were all held to that standard.

1. **PROPOSED, check first, in minutes: find why p6 adopts no data grid.** p5's canton grid had
   the same detached-boxhead band cut that strands p6's boxhead
   (`2026-10-05-r289-seam-measured.md` § 2.2, last bullet: `p5#htable8`). On p5 the cut did not
   matter, because the page adopted a data grid and the boxhead reader labelled it (§ 2 below).
   A p6 boxhead recording already exists, and `readings/boxhead/README.txt` says it is "read but
   NOT carried — the page does not adopt". **Prediction:** if p6 adopted, the existing recording
   would label its columns and the band path's `table2` would be superseded. That would remove
   both R293 symptoms at once, with no new reader. **It may fail.** p6 holds nine record tables
   (`table2` … `table10`), one per region block, and adoption may refuse a page that splits that
   way for a reason that is correct. Run `derive_data_grids(pdf, 6)` and read the adoption
   verdict before designing anything.
2. **PROPOSED, only if 1 is refuted: the record path's one-line header cap**
   (`compile.py:463`, spec § 10.6, `holon.py:207`). The recorded `header_lines` answer for p6 is
   3, and the record path maps it to 1. That cap was designed, so lifting it is a spec decision
   for a fresh session, not a patch.
3. **ASSERTED, once R293 holds: the acceptance pass**, on the cbh pattern
   (`r289-reader-refuted` / PR #308): `cor:expectedVerdict`, the accepted-count pin in
   `tests/test_arc_manifest.py`, the M15 stale edges, `scripts/arc_depends.py` regeneration, and
   R294 recorded as a defect in the manifest rationale.

## 1. Goal

Find out whether the shipped boxhead reader can label p5's canton grid. That grid is the one bfs
hold that needs no new code. #303 split p5 into two grids, and only the 12-column year grid had
a recorded question.

## 2. Findings (measured on `main` `442930f`)

- **The canton grid was never asked.** Its header block is lines 25–32 of p5: the year table's
  source line and three footnotes, T2's title, and the three-line boxhead. That block exists, and
  the disposal said `no reading`, because no recording existed and no live reader ran.
- **Live, the reader labels all 10 columns and reads all three spanners.** The answers:
  `Cantons`, `État de la population au 1er janvier`, `Naissances vivantes`, `Décès`,
  `Accroissement naturel`, `international 1`, `intercantonal`,
  `État de la population au 31 décembre`, `en nombres absolus`, `en %`. The spanners are
  `Composantes de l'évolution de la population` (c2–c6), `Solde migratoire` (c5–c6) and
  `Variation 2` (c8–c9). The footnotes and the title went to `other_words`. `dispose_boxhead`
  admitted all of it with nothing dropped. The question was asked live twice (once in a probe,
  once in the recording compile), and both answers were identical address for address.
- **This is the header with two spanner levels** that the bfs re-read flagged as uncertain, citing
  the Jev spike's missed spanners. The shipped reader does not share that miss.
- **The score falls from 0.9021428571428571 to 0.8984485190409027, and that is honest
  accounting.** On p5, asserted goes from 936 to 947 and escalated from 76 to 83. The +11 is line
  L7, the only header line made entirely of leaf-label words, so the line-granular ledger carries
  it. The +7 comes from L5 and L6, which hold spanner words. `carried_lines` counts leaf labels
  only, so neither line is carried, and their ink moves into `#p5-datagrid-residue` from a
  `REGION_TILING_FAILED` region. Other pages did not move. The graph gains `p5-datagrid-lc0`…`lc9`.
- **A second question was recorded and is NOT committed.** A `header_lines` reading
  (`5ab4f29d….json`) for p5 `region5` answered 0. That is wrong for a band with a three-line
  boxhead, because the crop starts at a data row. It moves no score and adds one `no_boxhead`
  decision to a region that the adopted year grid supersedes. It is left out so the offline
  compile changes by the canton reading alone.

## 3. Decided, and where

- The canton reading is committed. The manifest gains reading `0.8984485190409027`
  (`tests/corpus-manifest.ttl`), and `readings/boxhead/README.txt` gains a row.
- bfs stays `cor:Unadjudicated`, with no floor.
- The ruling in § 5 is recorded here and in the manifest comment. The full R293 row in
  `residues-open.md` is unchanged. This note is its newest pointer.

## 4. Unverified or assumed

- That p6 would adopt cleanly, or that its existing recording would dispose against an adopted
  grid's columns (§ 5 item 1). Not run.
- Why the year grid's `region5` reaches the `header_lines` reader at all, when #307 measured
  that no bfs trigger reaches `classify_hierarchical`. Not traced. It is harmless here, because
  the region is superseded.
- A scratch-script trap, recorded because it cost a whole compile: a script run from the
  scratchpad does not have the repo root on `sys.path`. Then `baml_client` is not importable,
  `baml_boxhead_available()` is False, and `BAML_LIVE=1` silently does nothing. Put both `src`
  and `.` on the path.

## 2b. Where the primaries are

- `readings/boxhead/eb6ba43975c4193bc6180b98526bf15942a104d4d6f05053882aef3ac0a8437a.json`: the
  recorded proposal.
- `src/iladub/etkl/boxhead.py`: `header_block`, `read_grid_boxhead`, `carried_lines`.
- `2026-10-05-r289-seam-measured.md` § 2.2: R293's seam.
- `2026-10-05-bfs-hold-reread.md` § 2: the three holds this note starts from.
