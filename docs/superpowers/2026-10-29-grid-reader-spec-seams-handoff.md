# Handoff: the grid-reader spec, split confirmed and seams measured (spec still owed)

**Serves:** prog:criterion:tab:05 — loop A of two (the adopted-grid reader). `prog:met false` at `fcf27f1`.

**Topic:** tab · **Date:** 2026-10-29

**Doc impact: none** (a handoff; the spec it asks for will carry its own).

Session 4 of this subject. It stopped at 51,762 working tokens (plimslop's figure), just over the
originating floor, before writing any spec text. Measurement ran in the first half: a subagent
gathered the facts below, and this session read the feed, the scorer, the emitter and the disposal
lift. Part 5 was written first, over the floor, and each action is graded.

## 5. The next concrete action (written first)

1. **ASSERTED — write the spec** `docs/superpowers/specs/2026-10-30-an-adopted-grid-is-read-design.md`
   (or another slug) for **loop A only**. Its inputs:
   - the four rulings (`2026-10-29-publisher-truth-predictions-measured-handoff.md`, § "Rulings,
     confirmed directly");
   - that file's "Session 3" seams;
   - § 2 and § 3 of this file.

   Then give loop B its own spec after A merges.
2. **PROPOSED, over the floor — the design draft in § 3.** It is this session's reasoning and was
   reviewed by no one. The spec author re-derives it against the code, and does not copy it. The
   seams that would refute it are flagged **MEASURE** in place.

## 1. Goal

Unchanged. Loop A: apple p2's adopted grid reaches `feed.table_records`, and through shipped code it
scores 58 `CORRECT` with 0 unclaimed cells. Loop B: disposing of superseded-only firings by publisher
truth.

## 2. Where the primaries are, and what was measured this session (at `fcf27f1`)

- **PRs #375 and #376 are merged** (`823de95`, `fcf27f1`). Branch `spec-superseded-arm-truth` is
  spent.
- **Every adopted grid in the baselines is `asserted`.** All 17 match the addendum's 17: apple p2; bfs
  p5, p5-datagrid-2, p6; caltrain p0–p3; fed p2, p3, p5, p8, p10; ons p7, p8; who p2, p3. The tally
  is over `pages[].regions[]` whose `table` contains `datagrid`. So the reader can take every
  `tab:DataGrid` in the graph without asking for its verdict. **MEASURE** that this still holds when
  the spec is written.
- **Grid cells link to their row.** `emit_data_grid` adds `tab:atRow` to each `tab:EntryCell` and
  joins it to the grid by `tab:hasDataCell` (`src/iladub/etkl/datagrid.py`, the inner loop of
  `emit_data_grid`). Aggregate rows are typed `tab:AggregationRow` directly, for the feed's skip rule.
  Emission has one site, `src/iladub/etkl/compile.py:1921`. **MEASURE** whether adoption (`…/adopt`,
  `document.py:1832`) emits through `emit_data_grid` or through a second site that would need the
  ordinal too.
- **The ordinal's source is `enumerate(grid.rows)`, and nothing has shown that `grid.rows` is in top-to-bottom order.**
  `_lines` is sorted by `top` (`compile.py`, just above :1921). **MEASURE** that `grid.rows` is
  ascending on all 17 grids before asserting `r_i` as reading order. If it is not, the ordinal is the
  rank of the row's line.
- **Columns have no asserted order.** `tab:colIndex` is declared (`vocab/ontology/tab.ttl:558`:
  domain `tab:GridColumn`, range `xsd:integer`) but never emitted. Ruling 2 says "in column order", so
  the spec must name that order fact. § 3 proposes emitting `tab:colIndex`.
- **No grid-row class or shape exists.** `tab:hasGridRow` (`vocab/ontology/tab-datagrid.ttl:85-87`)
  has no range. `tab:LeafRow` (`tab.ttl:52`) is unrelated to grids by definition. No shape mentions
  `tab:hasGridRow`. The shape files are `vocab/shapes/tab-shapes.ttl` and
  `tab-physical-shapes.ttl`. `tab-datagrid.ttl` is not loaded by `compile._FULL_ONT`
  (`tests/test_probe_domain_range_agreement.py:6-7`, measured 2026-08-18).
- **No test checks that the `tab:` terms used in `src/` are declared.** The ttl and query checks are
  `tests/test_artifact_declarations.py:336` and `tests/test_query_declarations.py:101`. A new property
  needs its declaration and positive and negative shape tests written by hand.
- **The feed's minting is reusable as it stands.** `table_records` (`src/iladub/feed.py:502`) builds,
  per logical table, `(ordered, rows, rid_of, owner, row_keys)`. Passes 2 and 3 work only on that
  tuple. A grid branch that produces the same tuple inherits:
  - per-cell minting,
  - `SHARED_ROW_KEY` for repeated key text (apple's three `Other` rows),
  - the spanning-key split,
  - collision settlement.

  Record and hierarchical rows keep y0 order (`_read_table`, the final `sorted`).
- **The scorer needs one more path entry.** `_scored_rows` resolves a per-cell row key through
  `_paths_by_region` (`src/iladub/truth.py`), and that function reads only header nodes over
  `tab:coversRow`/`tab:coversColumn`. `truth.py` already imports feed privates (`_header_parts`,
  `_label_region`).
- **`SPURIOUS` counts unclaimed cells of matched rows only** (`truth.py:210`; spec 2026-10-22 § 3.3,
  line 105). The unclaimed count that loop A's oracle needs is new.
- **Truth layout, from the Fed precedent** (`tests/ground-truth/fed-h41-2025-01-02/`):
  - `table-1.csv` with columns `row_label,row_label_marked,row_occurrence,col_path,value`, where the
    `col_path` separator is ` › `;
  - `floor.json` (`{"table-1": {"CORRECT": 0}, "notes": []}`);
  - a hand-written `provenance.json` with `url`, `retrieved`, `table_ordinal`, `span_sha256`,
    `span_bytes`, `pages` and `source_note`. `pages` covers the **whole directory**
    (`truth.py` `load_truth`), not each table.

  Fed's pages are `[0]`, and no Fed grid is on p0, so Fed's truth block should not move. Predicted,
  not run.
- **The extractor is single-mode with hard-coded constants.** `scripts/ground_truth_extract.py`
  (149 lines) takes positional `<html> <out-dir>`, and `main` fixes ordinal 2 and the Fed sha
  (:136-137). Its tests are `tests/test_ground_truth_extract.py` (4), listed as oracleTests at
  `tests/arc-manifest.ttl:1554-1557`.
- **Loop B is not a few triples, so the split holds.**
  - `cor:DisposalShape` constraint (4) requires `cor:live > 0` (`tests/corpus-shapes.ttl:115` ff.).
  - `_count_firings` counts by reason for the **whole document** (`tests/corpus_firings.py:55`), so
    the lift has no page.
  - `lift_snapshots` reads only `firings`/`snapshotOf`/`durable` from the blob, not `truth`.
  - `test_escalation_reasons_are_adjudicated` parametrises over `live_pairs` only
    (`tests/test_corpus.py:225`).

  B needs page-scoped firings, a lifted truth block, a superseded arm in constraint (4) and an
  oracle arm.
- **Criterion text** (`tests/arc-manifest.ttl:1317-1325` for tab:05; tab:02 at :1261, tab:09 at
  :1406): arm (a) is "fires on the 7-document corpus and every firing document carries a dated
  cor:adjudication naming and disposing of it". It does not say *live*. The `FIRES n` comments above
  all three are stale (R237).
- **"Lane-C spec ruling 2" does not exist in the repo.** A subagent grepped docs, tests, src,
  scripts and git pickaxe on all branches, and found nothing. The pointer came from the memory note
  only. **Ask the maintainer what it names, or drop it.**

## 3. What was decided, and where it is recorded

- **The A/B split is confirmed** by the § 2 measurement. **Recorded only in this file.**
- **Design draft for loop A. PROPOSED, over the floor, not approved. Recorded only here.**
  1. **Vocabulary.**
     - Add a row-ordinal property, e.g. `tab:rowIndex`, with range `xsd:nonNegativeInteger`.
       Give it **no `rdfs:domain`**: R61 shows a domain typing things by inference.
     - Emit the declared `tab:colIndex` on each grid column. That is a proposal beyond ruling 4's
       letter, in its spirit.
     - Add a shape over `sh:targetObjectsOf tab:hasGridRow` that requires exactly one index, plus a
       holon-scoped SPARQL check that no two rows of one grid share one. Ship it with positive and
       negative tests.
     - Classification: PROCEDURAL emit glue. It records an order that extraction already fixed.
  2. **Feed.**
     - Add `_read_grid`, returning `_read_table`'s shape with order taken from `tab:rowIndex`.
     - Stub columns are the grid's columns that are not `tab:MeasureColumn`, ordered by
       `tab:colIndex`.
     - Skip aggregation rows, blank cells and unshown ink exactly as `_read_table` does.
     - The row key is the tuple of non-blank stub-cell texts. The per-cell key text is that tuple
       joined by a space, as hierarchical paths are joined.
     - A row with an empty tuple takes the per-row branch, and its id falls back to
       `_row_discriminator`.
     - A grid with 0 stub columns mints nothing, and a new residue records it (bfs p5-datagrid-2,
       ruling 3).
     - Grids are single-member logical tables. **MEASURE** that no grid is a subject or object of
       `tab:continuesTable`.
     - Classification: PROCEDURAL, on the same grounds as the per-cell branch's own comment (the
       product is not RDF, and no judgement is taken). This **refutes the earlier handoff's "AXIOM-shaped"
       label** for this code. The spec should state why.
  3. **Scorer.**
     - One derivation of a grid row's key, `(tuple, region)`, lives in `feed`. Both
       `table_records` and `truth._paths_by_region` call it, so the scorer never re-derives it.
     - The key region is the row node's IRI, which contains `#` and so stays out of the entry
       namespace.
     - Its path is the one-level `(key text,)`.
     - Add a new `UNCLAIMED` count: the compiled cells on the table's pages that no truth cell
       claims, matched rows or not. It is a superset of `SPURIOUS`.
  4. **Truth.**
     - Give the extractor a colspan-interval mode for the SEC markup, using the rules in the
       predictions handoff § 2:
       - header rows are those whose first cell is empty;
       - a `$`-only cell is a glyph;
       - `<br>` becomes a space;
       - the value is the displayed value, never the XBRL sign.
     - Its parameters (ordinal and sha) become arguments instead of constants.
     - Write `tests/ground-truth/apple-fy2026q3-statements/`, with `pages` `[2]`.
     - Classification: PROCEDURAL raw extraction.
  5. **Oracles.**
     - Apple's truth block gives 58 `CORRECT`, every other outcome 0, and `UNCLAIMED` 0.
     - Feed fixtures cover a single stub, a multi-stub tuple, a stubless grid refused, an aggregate
       skipped and a repeated label, plus **row order from `tab:rowIndex` where bbox order
       disagrees.** That last fixture is what falsifies an implementation still sorting by y0.
     - The apple contract pins move (`tests/test_corpus_apple_contract.py`, Session 3's list). The
       counts are re-measured, not predicted.
     - Then regenerate the baseline.

## 4. Unverified or assumed

- Every **MEASURE** in § 2 and § 3.
- That Fed's truth block does not move. Fed truth is on p0, and Fed has no grid on p0.
- Whether `UNCLAIMED` belongs in A. A consumes it as an oracle and B as a condition. Putting it in A
  saves a second 24-minute regenerate.
- That `tab:colIndex`'s declared range `xsd:integer` is acceptable beside a new
  `xsd:nonNegativeInteger` row index, or whether the two should agree.
- SEC-value licensing for committing the apple CSV is still unread. The values are filed facts in a
  public filing. Have the maintainer confirm.
- Session 3's unverified items still stand: p2 periods under the contract, and a multi-stub truth
  set that does not exist.
- What "Lane-C spec ruling 2" refers to (§ 2, last item).
