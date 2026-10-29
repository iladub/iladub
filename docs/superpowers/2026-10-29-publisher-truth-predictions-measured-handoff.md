# Handoff: the three predictions are run; the scorer cannot read an adopted grid (spec owed)

**Serves:** prog:criterion:tab:05 — the spec for the superseded arm, settled by publisher truth.
`prog:met false` at `087c1ca`.

**Topic:** tab · **Date:** 2026-10-29

**Doc impact: none** (a handoff; the spec it asks for will carry its own).

This follows `2026-10-29-superseded-arm-by-publisher-truth-handoff.md`. Read that file's § 3 for the
two maintainer choices and the design shape; neither is re-opened here. This session ran that file's
§ 5 item 2 and stopped at ~72K working tokens, past the originating floor, on the maintainer's choice
(2026-10-29, in chat: "Evidence + handoff"). Part 5 is written first and was written under the floor's
overrun, so each action carries its own grade.

## 5. The next concrete action (written first)

1. **ASSERTED — before writing any spec section, the maintainer rules ONE scope question:** does the
   adopted-grid reader go into `feed.table_records` (the shared reader, so the grid also reaches
   contracts) or into the scorer only? The probe in § 2 shows the reading is the same either way. The
   difference is blast radius: in the feed it changes every document whose adopted grid the feed
   cannot see today ([[R341]]), and so a corpus baseline diff. Do not choose it on the maintainer's
   behalf.
2. **ASSERTED — then write the spec** `docs/superpowers/specs/2026-10-29-<topic>-design.md` from the
   previous handoff's § 3, this file's § 2, and the ruling in item 1. The three predictions are no
   longer propositions, and the spec may rely on them **for apple p2 only**.
3. **PROPOSED — the reading rule for a grid row** (§ 2, "the reader") is a derivation over asserted
   facts, so it is AXIOM-shaped (a SPARQL `SELECT` over `tab:hasDataCell`/`tab:MeasureColumn`/
   `tab:coversColumn`). That classification is a proposition. It fails if a grid ever has no non-measure
   column or more than one: the probe asserts exactly one and would raise. Whether a stub-less grid
   (pure matrix) or a two-text-column grid exists on the corpus is **not measured**. Find out in
   minutes by running the probe's `assert` over the six documents' adopted grids before the spec fixes
   the rule.

## 1. Goal

Unchanged: make tab:05 (and later tab:02 and tab:09) satisfiable by disposing of superseded-only
firings when publisher truth proves the adopted reading correct.

## 2. What was measured (2026-10-29, at `087c1ca`, branch `spec-superseded-arm-truth`)

**Prediction (b) holds: the 10-Q table can be read from markup alone.**
- Source: `https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm`,
  fetched with User-Agent `iladub-research contact@iladub.dev`. Table #17 (1-based, as
  `scripts/ground_truth_extract.py`'s `_span` counts): 49,055 bytes, sha256 starts `7999b55068408a58`,
  as the previous handoff recorded.
- The table is 12 grid columns wide. Header rows are those whose first cell is empty:
  `Nine Months Ended` spans columns [3,12), `June 27, 2026` [3,6) and `June 28, 2025` [9,12).
- **Rule:** a value cell's column path is every header whose interval contains the cell's interval,
  in header-row order. 58 truth cells result, each with a two-level path.
- Three markup facts the extractor must rule on:
  - a cell whose whole text is `$` is a unit glyph, not a value (4 rows carry one);
  - `<br>` inside the date headers must become a space: plain text reads `June 27,2026`;
  - `Other` occurs three times, so `row_occurrence` is 0, 1, 2.
- 7 section-label rows (e.g. `Operating activities:`) carry no value and yield no truth cell.

**Prediction (a) holds — but only through a reader that does not exist in the repo.**
- `iladub.truth.score_table` on the real compile, with a scratch truth CSV and `pages: [2]`, returns
  `REFUSED: 58`, every other outcome 0. The cause is that it finds **0 compiled rows** on p2.
- **The cause:** `feed.table_records` (`src/iladub/feed.py`, `table_records`) reads only subjects typed
  `tab:RecordTable` or `tab:HierarchicalTable`, joined by `tab:hasCell`. Apple's graph has 2
  `tab:HierarchicalTable`s (p0, p1) and 1 `tab:DataGrid` (`…/doc/p2/adopt#p2-datagrid`, also
  `tab:UniformGrid`, label "29 rows x 3 columns", 87 `tab:hasDataCell`). Measured on that graph:
  `table_records` yields rows on p0 and p1 (31/28, or 124/56 per-cell) and **none on p2**, in both modes.
- **The reader (throwaway probe, not committed):** for each `tab:hasGridRow` of the grid,
  - the row label is the text of its one cell whose `tab:atColumn` is **not** a `tab:MeasureColumn`
    (here `c0`, `tab:columnFamily tab:Text`);
  - each measure cell's column path is the labels of the grid's header nodes that `tab:coversColumn`
    its column, ordered by `tab:headerLevel` (`s0` "Nine Months Ended" at level 0, `h1`/`h2` the dates
    at level 1, both `tab:parentHeader s0`);
  - occurrence counts repeated labels in row order, with rows ordered by their `-rN` suffix. That
    suffix is an IRI-name read and is **not** acceptable in shipped code (feed reads no IRI names).
    The spec must name the asserted order fact instead (row bbox or another asserted ordinal).
- **Result:** truth 58, compiled 58, exact multiset intersection **58**, on (label, occurrence, path,
  value) after `iladub.truth.normalise`.

**Prediction (c) holds on p2:** compiled minus truth is empty, so no grid cell is unclaimed. The new
count's definition is still the spec's to write. The probe's version is "compiled cells of the page's
grid not in the truth multiset".

**How the result was obtained**, so it can be re-run: one full compile of
`corpus/financial/apple-fy2026q3-statements.pdf` takes **~19.5 minutes wall clock, ~100 s CPU**. Most of
the wall time is spent waiting. The graph was dumped to N-Triples once and every probe ran over the
dump. Do the same. Never compile twice to answer two questions.

## 3. What was decided, and where it is recorded

- The two choices and the design shape: the previous handoff § 3. Unchanged.
- Stopping here for the floor: the maintainer, 2026-10-29, in chat. **Recorded only in this file.**
- [[R341]] raised (below and in the register): the feed never reads an adopted data grid.

## 4. Unverified or assumed

- **Whether apple p2's 87 cells are absent from every contract output**, rather than only from
  `table_records`. That is likely, because `ground_document` reads `table_records`
  (`feed.py:1001,1003`), but no contract run was made.
- **Which other documents' adopted grids are invisible to the feed.** The baselines carry
  `DataGrid`-anchored regions in apple, bfs, ons, fed, caltrain and who
  (`grep -c DataGrid tests/corpus-baseline/*.json`). The count is **not** split by verdict, so how many
  are asserted is unmeasured. bfs p5 (496 cells, R238) and ons p7/p8 are the likely asserted ones, and
  they are the documents tab:09 and tab:02 need.
- That the row-order fact the spec needs exists in the graph without the IRI suffix.
- The previous handoff's § 4 items still stand: snapshot JSON carrying per-table pages and the new
  count, `lift_snapshots` lifting a truth block, R62 looking stale, R237, and SEC-value licensing.

## Addendum: § 5 item 3 run, and refuted (2026-10-29, same session)

**Ruling, reported, not yet confirmed directly:** the adopted-grid reader goes in `feed.table_records`,
not in the scorer only. The maintainer gave this "yes" to a subagent of this session. It reached the
controller only through that subagent's report, so **confirm it before the spec relies on it.**

**The one-stub-column rule is REFUTED: it holds on 13 of 17 adopted grids.** Each was compiled offline
(`BAML_LIVE` and `ILADUB_RECORD_READINGS` unset) from apple, bfs, ons, fed, caltrain and who-covid,
dumped to N-Triples, and the columns that are not `tab:MeasureColumn` were counted per grid:

| grid | non-measure columns | non-measure cells per row |
| --- | --- | --- |
| apple p2; bfs p5, p6; ons p7, p8; fed p3, p8, p10; caltrain p0–p3; who p2 | 1 | 1 on every row |
| bfs `p5-datagrid-2` (12 cols, 19 rows) | **0** | 0 |
| fed p2 (7 cols, 8 rows) | **3** | 3 ×7, 1 ×1 |
| fed p5 (6 cols, 23 rows) | **3** | 1 ×2, 2 ×5, 3 ×16 |
| who-covid p3 (5 cols, 45 rows) | **4** | 4 ×45 |

The probe's `assert` would crash the shared feed on 4 grids. **Because the reader goes in the feed, the
spec must rule on 0 and on several stub columns.** They are not corner cases. The criterion's own
documents (apple p2; bfs p5 primary; ons p7, p8) all have exactly one.

**Grid rows carry no order fact.** On all 17 grids, all 442 `tab:hasGridRow` nodes carry only
`rdf:type` and `prov:wasDerivedFrom`, whose target (e.g. `…p2-line16`) has no triples. The only
asserted order evidence is on cells: `tab:hasBBox`, `tab:firstGlyphEnd` and `tab:lastGlyphStart`. Row order,
and therefore `row_occurrence` for repeated labels, must come either from cell bboxes or from a new
row ordinal that adoption asserts, which is a vocabulary change. **The spec chooses.** The `-rN` IRI
suffix is not an option.

The dumps were in this session's scratchpad and do not outlive it. Recompile serially, about 15 minutes
for the five documents plus about 19.5 for apple, and dump once.

## Rulings, confirmed directly (maintainer, 2026-10-29, next session, in chat)

These four answers were given directly in chat (AskUserQuestion), not relayed by a subagent. They settle § 5 item 1 and both open
questions from the addendum.

1. **The adopted-grid reader goes in `feed.table_records`.** Contracts receive grid cells too, and [[R341]]
   closes everywhere. The PR carries the corpus-baseline diff.
2. **Several non-measure columns: the row key is the ordered tuple of the row's non-measure cells, in
   column order.** Each text column is a key dimension and none is dropped (fed p2, fed p5, who p3).
3. **No non-measure column: the feed refuses the grid, and the refusal is a recorded residue.** No label is
   invented (bfs `p5-datagrid-2`).
4. **Row order: adoption asserts an ordinal on each `tab:hasGridRow`.** This is a vocabulary change in
   `tab` plus its shape. Order is not derived from cell bboxes, and the `-rN` IRI suffix stays forbidden.

## Session 3 (2026-10-29): rulings taken, seams measured, spec still owed

Written at ~53K working tokens (plimslop's figure), just past the originating floor. The spec was not
started. The resume note had already put it in a fresh session.

### 5. The next concrete action (written first)

1. **ASSERTED — write the spec** `docs/superpowers/specs/2026-10-30-<topic>-design.md` from the
   previous handoff's § 3, § 2 and the addendum of this file, the four rulings above, and the seams
   below. No ruling it needs is open.
2. **PROPOSED — split the spec into two loops**, and let the spec author confirm or refuse:
   - (A) the grid reader: the row ordinal, the feed branch, the scorer seam, and the apple truth set.
     Its oracle: apple p2 scores 58 CORRECT, 0 unclaimed, through shipped code.
   - (B) the disposal arm: `cor:` shape and SPARQL over a lifted truth block.

   The reason is size. (B) depends on how `lift_snapshots` lifts a truth block, which is unmeasured
   (prior handoff § 4). The split is refuted if (B) turns out to be a few triples in
   `tests/corpus-shapes.ttl`. Opening `cor:DisposalShape` takes minutes and settles it.

### Seams measured this session, at `087c1ca` (all `file:line` read in this session)

- **Row order in the feed is geometry today** for record and hierarchical tables:
  `sorted(rows, key=min y0)` at `src/iladub/feed.py:312`. Ruling 4 makes the grid branch read the
  asserted ordinal instead. The other kinds keep y0, and the spec should say so rather than unify them.
- **The ordinal's source exists:** `emit_data_grid` (`src/iladub/etkl/datagrid.py:692`) loops
  `for r_i, line_idx in enumerate(grid.rows)` (:738). `r_i` is in scope where the row is minted
  (`tab:LeafRow` :741, `tab:hasGridRow` :759) and is not asserted.
  - There is no row-ordinal property in `tab`. `tab:colIndex` exists for `tab:GridColumn`
    (`vocab/ontology/tab.ttl:558`) but is not emitted by `emit_data_grid`.
  - No SHACL shape targets `tab:DataGrid` (declared in `vocab/ontology/tab-datagrid.ttl:68`).
- **Why grids are invisible (R341):** `_read_table` joins entries by `tab:hasCell`
  (`feed.py:261-263`), while grids join them by `tab:hasDataCell` (`datagrid.py:766`). Grids use
  `tab:hasCell` only for boxhead label cells (`boxhead.py:470`).
- **The scorer seam is the second one.** `truth._scored_rows` resolves a per-cell row key's path
  through `_paths_by_region`, which reads header nodes over `tab:coversRow`/`tab:coversColumn`
  (`src/iladub/truth.py:159-183`).
  - Grids emit no `tab:coversRow` anywhere, so a grid row key raises `TruthShapeError` unless the
    spec gives it a path. The ruled stub tuple is a natural row path.
  - The column side already works: `emit_boxhead` gives the grid `tab:hasHeaderNode` with
    `tab:coversColumn` (`boxhead.py:463-468`).
- **Grid cells carry no `prov:wasDerivedFrom`** (only the row does, `datagrid.py:760`). `region`
  therefore falls back to the IRI fragment (`feed.py:300-302`), e.g. `p2-datagrid-r3c1`, which
  `_on_pages` still matches (`truth.py:75`).
- **Contract blast: apple only.** Among the documents with grids (apple 1, bfs 3, ons 2, fed 5,
  caltrain 4, who-covid 2, by `grep -c datagrid tests/corpus-baseline/*.json`), only apple carries a
  `cor:contract` (`tests/corpus-manifest.ttl`).
  - On the apple graph (offline compile, dumped to N-Triples): `table_records` returns 180 per-cell
    and 59 per-row records today, and `p2-datagrid` has 29 rows with 58 non-blank measure cells.
  - So the per-cell count should rise to about 238 and the per-row count to about 88. Every pinned
    count in `tests/test_corpus_apple_contract.py` moves (lines 129, 130, 135, 136, 143, 156, 158, 165,
    171, 185). Those are predictions; re-measure them after implementation.
- **Baseline blast:** the ordinal triple changes `graph_sha256` (`scripts/corpus_verdict_snapshot.py`
  `_snapshot_of`) in every baseline with a grid: apple, bfs, ons, fed, caltrain and who-covid.
  Apple also gains a `truth` block once `tests/ground-truth/apple-fy2026q3-statements/` exists.
- **The truth extractor needs a second mode.** `scripts/ground_truth_extract.py` reads the Fed's
  `id`/`header` attributes (`_HEADER_ID`, `extract_table`, :93). The SEC table has none, so its header
  paths come from colspan intervals (§ 2 of this file). Classified PROCEDURAL (raw extraction from
  publisher markup, exact integer intervals); the spec states it.
- **Compile cost, re-measured:** an offline apple compile took **~2 minutes**, not 19.5. The
  19.5 minutes was likely the live/recording configuration. Unverified beyond this one run.

### Unverified or assumed (this session)

- Whether p2's periods ground under the apple contract. `test_p2_every_period_grounds` pins 6 periods;
  p2's "Nine Months Ended › June 27, 2026" path may add more or be refused.
- The multi-stub tuple (ruling 2) has no truth set to score against. Its tests are fixtures only.
- SEC-value licensing for committing the apple truth CSV (prior handoff § 4) is still unread.
