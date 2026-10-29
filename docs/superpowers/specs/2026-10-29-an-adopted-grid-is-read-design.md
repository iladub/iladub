# An adopted grid is read — the row ordinal, the feed's grid branch, and apple's truth (design, 2026-10-29)

**Serves:** prog:criterion:tab:05 — loop A of two. Loop A makes an adopted `tab:DataGrid` readable
by the feed and scorable against publisher truth. Loop B (its own spec, after A merges) disposes of
superseded-only firings by that truth, which is what meets tab:05, and later tab:02 and tab:09.
`prog:met false` at `e84c705` (`tests/arc-manifest.ttl`, tab:05).

**Topic:** tab · **Date:** 2026-10-29

**Doc impact: increment.** `vocab/ontology/` gains one property (`tab:rowIndex`) and starts using a
declared one (`tab:colIndex`); `vocab/shapes/` gains one shape. Contracts start receiving grid cells
([[R341]] closes). The released vocabulary's meaning grows; nothing it already says changes.

**Status: DRAFT for the maintainer.** § 11 lists what this spec does not decide. § 4 was filled at
~56K working tokens (over the originating floor, override logged); the design in § 6 was written
under it. **An adversarial review of § 6 against § 4 is owed before any plan** (fresh session).

## 1. Goal

Apple p2's adopted grid reaches `feed.table_records`, and through shipped code (no probe, no IRI-name
read) `truth.score_table` scores it **58 `CORRECT`, every other outcome 0, `UNCLAIMED` 0** against a
committed truth set extracted from the SEC filing.

Every other adopted grid on the corpus reaches the feed by the same branch, under the four rulings
below; a grid with no stub column is refused and recorded.

## 2. Inputs, and what each settles

- **The four rulings** (maintainer, 2026-10-29, directly in chat; recorded in
  `docs/superpowers/2026-10-29-publisher-truth-predictions-measured-handoff.md` § "Rulings, confirmed
  directly"):
  1. the adopted-grid reader goes in `feed.table_records`, so contracts receive grid cells too;
  2. with several non-measure columns, the row key is the ordered tuple of the row's non-measure
     cells, in column order — none is dropped;
  3. with no non-measure column, the feed refuses the grid and a residue records it; no label is
     invented;
  4. row order is an ordinal adoption asserts on each `tab:hasGridRow`; not cell bboxes, never the
     `-rN` IRI suffix.
- **The three predictions, run on apple p2 only** (same file, § 2): the SEC table is readable from
  markup (58 truth cells, two-level column paths); a probe reader over the graph intersects it
  exactly (58 of 58); compiled minus truth is empty.
- **The stub census** (same file, addendum): 13 of 17 adopted grids have exactly one non-measure
  column; bfs `p5-datagrid-2` has 0; fed p2, fed p5 and who-covid p3 have 3, 3 and 4.
- **The seams** (same file, § "Session 3"; and `2026-10-29-grid-reader-spec-seams-handoff.md` § 2).
  Re-measured for this spec in § 4.
- **The disposal design loop B will build** (`2026-10-29-superseded-arm-by-publisher-truth-handoff.md`
  § 3). Loop A supplies it two things: a truth block that can cover a grid page, and the `UNCLAIMED`
  count its "no asserted cell left unclaimed" condition needs.

### 2.1 Ruled 2026-10-28 item 2 is superseded

`specs/2026-10-28-tiling-matrix-roundtrip-design.md` § "Ruled 2026-10-28", item 2, counted a reason
whose every corpus output adoption replaces as **"fires nowhere"**. The maintainer's 2026-10-29
choice (the superseded-arm handoff § 3) replaces it: **a superseded firing is disposed only when
publisher truth proves the adopted reading correct, never by counting it as absent.** Loop B
implements that; this spec records the supersession so no plan builds on item 2. That spec is
Evidence and is not edited.

## 3. Oracles first

| # | oracle | what it falsifies |
| --- | --- | --- |
| O1 | `score_table` on apple's compiled graph against `tests/ground-truth/apple-fy2026q3-statements/table-1.csv`, `pages [2]`: **58 CORRECT, WRONG_VALUE = MISATTACHED = LOST = MISSING = REFUSED = SPURIOUS = 0, UNCLAIMED = 0** | the whole loop, end to end, on real input |
| O2 | feed fixture: a grid whose `tab:rowIndex` order **disagrees with bbox y order** reads rows in `tab:rowIndex` order (record order and `row_occurrence` of a repeated label) | an implementation still sorting grids by y0 |
| O3 | feed fixture: one stub column → one row key per row, the stub cell is the key and not a value | the stub cell leaking in as a valued cell (it would score `UNCLAIMED` on O1, but O3 names it) |
| O4 | feed fixture: three stub columns, colIndex order ≠ IRI order ≠ x order → the key is the stub texts in `tab:colIndex` order | ruling 2's "column order" read from anything but the asserted fact |
| O5 | feed fixture: a stubless grid mints **0** records and does not raise | ruling 3 |
| O6 | feed fixture: an `tab:AggregationRow`, a blank cell and an unshown cell in a grid are skipped exactly as `_read_table` skips them (the unshown + non-empty case raises, as there) | the grid branch forking the record-table skip rules |
| O7 | feed fixture: a repeated stub text (apple's three `Other`) → `SHARED_ROW_KEY` in per-cell mode, three distinct records | the shared-key rule not reaching grids |
| O8 | shape: a grid row with no `tab:rowIndex`, with two, and two rows of one grid sharing one index — each is a violation; the emitted apple/fixture grid conforms | the membrane half of ruling 4 |
| O9 | `UNCLAIMED` unit test: a compiled row no truth group matches contributes all its cells; a matched row contributes exactly its `SPURIOUS` cells | the new count being `SPURIOUS` renamed |
| O10 | extractor test on a committed SEC-shaped HTML fixture: colspan intervals → two-level paths, `$` dropped, `<br>` → space, displayed value kept | the second extraction mode |

**Falsification is owed per task** (CLAUDE.md § Plan authoring rule 4). O1 is falsified by reverting
the grid branch (expect `REFUSED: 58`, the measured pre-state). O2 by sorting the grid branch by y0.
None of these was run by this spec.

## 4. Measured facts (at `e84c705`)

Measured by a read-only subagent for this spec. The only compute was one `derive_data_grids` call on
apple p2.

- **Every adopted grid is `asserted` (HOLDS).** I scanned `pages[].regions[]` in
  `tests/corpus-baseline/*.json` for a `table` containing `datagrid`. There are 17, all `asserted`:
  apple p2; bfs p5, p5-datagrid-2, p6; caltrain p0–p3; fed p2, p3, p5, p8, p10; ons p7, p8; who p2,
  p3. Each URI is `…/pN/adopt#pN-datagrid[-2]`, so none comes from the `datagrid_fallback` path.
- **One emitter (HOLDS).** `emit_data_grid` (`src/iladub/etkl/datagrid.py:692`) is the only writer
  of grid rows and cells:
  - `hasGridRow` at :759, `hasDataCell` at :766, `atRow` at :767;
  - row nodes at :736-737, typed `tab:LeafRow` at :740.

  It has two callers: `compile.py:1921` (fallback) and `compile.py:2122` (the `datagrid_adopt`
  branch, imported as `_emit` at :2038). Document adoption (`document.py` ~1825-1990) does not emit.
  It merges `rep_a.graph`. So asserting the index in `emit_data_grid` covers both paths.
- **`grid.rows` is top-to-bottom by construction (HOLDS).**
  - `derive_data_grid` sorts `lines` by `top` (`datagrid.py:326-327`) and calls `rows.sort()` at
    :633, after the aggregate-witness pass appends out of order at :623.
  - Both callers build `_lines` filtered for words and sorted by `top`: `compile.py:1915-1917` and
    `:2041-2042`.
  - Re-derived on apple p2, the 29 rows are strictly monotone.
  - Equal `top` ties are possible in principle, so the order is non-decreasing. `enumerate` still
    gives distinct indices.

  **The § 10 premise on ordinal order is therefore measured, not assumed:** `tab:rowIndex = r_i`.
- **No grid is in a continuation chain (HOLDS).** The two writers of `tab:continuesTable`
  (`document.py:1609` and `:1759`) index band regions and run before adoption. Grids are appended at
  an index ≥ `len(bands)` (:1854). Adoption refuses or withdraws any superseded table that is chained
  (:1880-1898).
- **`tab:colIndex` is emitted, but not on data-grid columns (REFUTES the seams handoff's "never
  emitted").**
  - It is written at `spangraph.py:96` and `headergraph.py:36`, onto transient evidence-graph
    `tab:GridColumn` nodes. `emit_data_grid` does not write it.
  - Grid columns are minted at `datagrid.py:722-733` as `{grid}-c{k}`. Their only order facts are
    the IRI suffix and `tab:colX0`/`tab:colX1`.
  - `tab:MeasureColumn` is added at :725 when `col.is_measure` (decided at :99-105: the family is set
    and is not `Text`).

  **MEASURE in the plan:**
  - whether the evidence-graph nodes ever reach the document graph, since the uniqueness constraint
    in § 6.1 would then see them;
  - that `k` follows `colX0` order, which makes `tab:colIndex = k` left-to-right.
- **No row-ordinal property exists.** Grepping `vocab/ontology/*.ttl` for `rowIndex`, `ordinal` and
  `position` finds none. The integer properties that do exist are scoped to other subjects:
  - `tab:atGridRow` (domain `tab:GridCell`);
  - `tab:lineIndex`, `tab:headerRowOrder`, `tab:captionRow`, `tab:pageOrdinal`.

  `tab:atGridRow` is the nearest, and it is a cell's grid coordinate from the cell-typing evidence.
  Reusing it on a row node would give it a second meaning, so a new property is the right call.
- **Feed and scorer line ranges:**
  - `_read_table` is at `feed.py:238-313`, with the y0 sort at :312 and the `hasCell` join at :261.
  - `table_records` is at :502-747: pass 1 at :534-626, pass 2 at :654.
  - In `truth.py`, `_scored_rows` is at :123-156 and `_paths_by_region` at :159-174. `SPURIOUS`
    appears only at :93 and :210.
- **Lane overlap:**
  - The R74/tab:01 spec edits `tab-datagrid.ttl` and `tab-shapes.ttl`. Those are textual
    neighbours only, with no shared `src/` file.
  - The tab:08 spec edits `tab.ttl`, `tab-shapes.ttl` and the `compile.py` adoption site, and adds
    grid `coversRow` header nodes. Its own § 6 flags that `feed._row_header_path` may then change
    grid record ids. **That changes this loop's row key**: once a grid carries a row-header tree, the
    feed must choose between it and the stub tuple. **Run loop A and tab:08 serially, not in
    parallel.** R74 can run beside A if it rebases onto it.

## 5. Classification gate (CLAUDE.md § 8)

| decision | class | why |
| --- | --- | --- |
| assert `tab:rowIndex` from `enumerate(grid.rows)` and `tab:colIndex` on each grid column | PROCEDURAL emit glue | it records an order extraction has already fixed; no judgement is taken, nothing is inferred. It is the same class as the emitter's existing `tab:atRow`/`tab:atColumn` |
| one index per grid row, unique within its grid | AXIOM, constraint → SHACL | closed-world over one holon (the grid): `sh:minCount`/`sh:maxCount 1` plus a holon-scoped SPARQL constraint |
| which grid columns are stubs | **not decided here** | `tab:MeasureColumn` is already asserted at compile; the feed reads its absence *within one grid's asserted columns*. That is a holon-scoped closed read of a finished holon, not a derivation into the graph (§ 8's "closed-world guard … holon-scoped") |
| the grid branch of `table_records` | PROCEDURAL | the same grounds the per-cell branch states at `feed.py:667-673`: its product is an in-memory `Record`, not RDF, so there is no CONSTRUCT to write or shape to validate; and no judgement is taken. **This refutes the earlier handoff's "AXIOM-shaped" label** (`2026-10-29-publisher-truth-predictions-measured-handoff.md` § 5 item 3): that label held for a probe that returned rows; the shipped reader returns `Record`s |
| `UNCLAIMED` | PROCEDURAL, decidable exact arithmetic | a count over the scorer's own claim set |
| the SEC extraction mode | PROCEDURAL, raw extraction | source markup → typed truth rows by exact integer colspan intervals; no tolerance |

**No tuned constant appears anywhere in this loop.** A plan that introduces one fails review.

## 6. Design

### 6.1 Vocabulary (ruling 4)

- **`tab:rowIndex`**, `owl:DatatypeProperty`, range `xsd:nonNegativeInteger`, **no `rdfs:domain`**:
  a domain would type every subject by RDFS inference ([[R61]]). Declared in the file that declares
  `tab:hasGridRow` (`vocab/ontology/tab-datagrid.ttl`) or in `tab.ttl` beside `tab:colIndex` — the
  plan picks one after **MEASURING** which file the compile's ontology union loads (§ 4).
- **`tab:colIndex`** (already declared, `tab.ttl`, range `xsd:integer`) is emitted on every grid
  column. Its range is left as declared (§ 11 item 3).
- **Shape** `tab:GridRowIndexShape`, `sh:targetObjectsOf tab:hasGridRow`: exactly one
  `tab:rowIndex`; plus a SPARQL constraint on `tab:DataGrid` (or `sh:targetSubjectsOf
  tab:hasGridRow`) that no two of its rows share one, and the same for `tab:colIndex` over its
  columns. Positive and negative tests by hand (§ 4: no test catches an undeclared term).
- **Value:** the row ordinal is the position in `grid.rows`, which is top-to-bottom by construction
  (§ 4); the column index is the column's `k`, left-to-right subject to the § 4 MEASURE.

### 6.2 The feed's grid branch (rulings 1–3)

**Input set.** `table_records` takes every `tab:DataGrid` beside the record and hierarchical tables.
No verdict is consulted: every adopted grid in the baselines is `asserted` (§ 4). A grid is a
single-member logical table (§ 4 measures that no grid is in a `tab:continuesTable` chain).

**A reader of the same shape as `_read_table`.** `_read_grid(graph, grid)` returns
`(ordered, rows, row_cols)` exactly as `_read_table` does, so passes 2 and 3 run unchanged and the
grid inherits per-cell minting, `SHARED_ROW_KEY`, collision settlement and the identity invariant.
It differs in three places only:

1. **Join.** Entries are `tab:EntryCell`s joined by `tab:hasDataCell`, not `tab:hasCell`.
2. **Order.** `ordered` is by `tab:rowIndex`, not by min y0. Record and hierarchical tables keep y0
   (`feed.py:312`); the two kinds are not unified, and the plan must not unify them.
3. **Stub cells are the key, not entries.** A stub column is a grid column not typed
   `tab:MeasureColumn`; stubs are ordered by `tab:colIndex`. A row's **key tuple** is its non-blank
   stub-cell texts in that order.
   - In per-row mode the stub cells stay in the record as concepts, exactly as a record table's
     label column does (the per-row scorer finds the label among the concepts).
   - In per-cell mode the stub cells mint **no** cell record; they form the row key.

Skip rules (aggregation row, unshown ink and its raise, blank text) are shared with `_read_table`,
not copied: the plan factors them so both readers call one site (O6 pins it).

**Row identity.** One function in `feed` derives a grid row's key: `(text, region)`, where `text` is
the key tuple joined by one space (as hierarchical paths are joined) and `region` is the row node's
IRI. `table_records` feeds it into `rid_of` (as `row_path` does) and into `row_keys` (as
`_header_parts` does for hierarchical rows); the scorer calls the same function (§ 6.3).

- The region is the **row's** IRI, not a stub cell's: apple's three `Other` rows must stay three
  regrouped rows in `_scored_rows`, and a label-cell region would merge them. The IRI contains `#`, so
  it stays out of the entry-region space by `_label_region`'s own argument.
- A row whose key tuple is empty takes the opaque path: `_row_discriminator`.
- `SHARED_ROW_KEY` is decided by the existing count over delivered text (`feed.py:580-589`), now
  also over grid rows.

**Ruling 3.** A grid with 0 stub columns contributes nothing to `per_logical` and raises nothing. A
new register row (next free number at implementation) records the refusal and names bfs
`p5-datagrid-2`. The feed writes no graph, so the residue is the register's, not a
`CandidateConcept`.

### 6.3 The scorer

- `_paths_by_region` adds, for every grid row with a non-empty key, `str(row) → (text,)` from the
  feed's derivation. One level: the truth file prints the row label, and `_scored_rows` reads
  `[-1]`.
- Column paths need nothing: the grid's boxhead already gives `tab:hasHeaderNode` with
  `tab:coversColumn` (`boxhead.py:463-468`), which `_header_parts` reads.
- **`UNCLAIMED`** (new, reported beside `SPURIOUS`): every compiled cell on the scored pages that no
  truth cell claims — the unclaimed cells of matched rows (`SPURIOUS`) plus every cell of a compiled
  row no truth group matched. `UNCLAIMED ≥ SPURIOUS` always. It belongs in loop A: A's oracle O1
  needs it, and B's disposal condition consumes it; adding it in B would cost a second 24-minute
  regenerate.

### 6.4 Truth for apple

- `scripts/ground_truth_extract.py` gains a colspan-interval mode for SEC markup, with the four
  rules measured in the predictions handoff § 2: header rows are those whose first cell is empty; a
  cell whose text is only `$` is a glyph; `<br>` becomes a space; the value is the displayed value,
  never the XBRL sign. A value cell's column path is every header whose interval contains its
  interval, in header-row order.
- Its ordinal and expected sha become arguments; the Fed mode keeps its current behaviour and its 4
  tests stay green unchanged.
- `tests/ground-truth/apple-fy2026q3-statements/` holds `table-1.csv`, `floor.json`
  (`{"table-1": {"CORRECT": 58}, …}` — the plan fixes the floor at the measured value), and a
  hand-written `provenance.json`: url, retrieved, `table_ordinal 17`, `span_sha256` (prefix
  `7999b55068408a58`), `span_bytes 49055`, `pages [2]`, source note. SEC licensing cleared by the
  maintainer (2026-10-29, in chat).

## 7. What is NOT done

- **No disposal.** No `cor:` shape, no lifted truth block, no page-scoped firings: loop B.
- **No change to record or hierarchical table reading**, including their y0 order.
- **No grid row gets a header node or `tab:coversRow`.** The row key is the feed's reading of
  asserted stub cells; turning it into header nodes is tab:08's row-group design
  (`specs/2026-10-28-datagrid-residue-design.md`), not this loop's.
- **No truth set for a multi-stub grid.** Ruling 2 is pinned by fixtures only (O4).
- **No verdict filter** on grids (§ 6.2).
- No change to how adoption chooses a grid, or to any escalation reason.
- **No precedence rule between a stub key and a future grid row-header tree.** tab:08 would add
  one (§ 4, lane overlap); when it lands, *its* spec rules which key a grid row carries. Hence
  loop A and tab:08 are serial.

## 8. Unverified

- That p2's periods ground under the apple contract: `test_p2_every_period_grounds` pins 6 periods;
  the "Nine Months Ended › June 27, 2026" path may add more or be refused. Found out at the
  contract-pin step, re-measured, not predicted.
- That Fed's truth block's outcome counts do not move (its pages are `[0]`, no Fed grid is on p0).
  Its dict gains the `UNCLAIMED` key regardless.
- The apple contract counts after the change: Session 3 predicted ~238 per-cell and ~88 per-row
  records. Every pin in `tests/test_corpus_apple_contract.py` that moves is re-measured.

## 9. Predicted blast radius

- **Baselines:** `graph_sha256` moves for every document with a grid — apple, bfs, ons, fed,
  caltrain, who-covid — because of the two index triples. Apple gains a `truth` block. Fed's truth
  block gains `UNCLAIMED`. One regenerate, after the last input edit.
- **Contracts:** apple only carries a `cor:contract`; its pins move.
- **Tests:** the extractor's (4, unchanged), new feed fixtures, the shape's positive/negative, the
  scorer's new count.

## 10. Adversarial pass on this spec's premises

- *"Every adopted grid is asserted, so no verdict filter."* If a grid ever lands non-asserted, the
  feed would read a reading the compiler refused. § 4 re-measures it; if a single grid is not
  asserted, the plan reads the verdict, and this premise is struck.
- *"The row ordinal is reading order."* Measured by construction (§ 4: two sorts by `top`, apple p2
  strictly monotone). Equal-`top` ties keep distinct indices in emission order; no fixture covers a
  tie, and none is needed for O1.
- *"Stub = not `tab:MeasureColumn`."* A grid whose text column is mis-typed as measure would lose its
  key; the census found the counts above, and the 13 single-stub grids are the criterion's own
  documents. A mis-typing is a measure-typing defect upstream, not the feed's to repair.
- *"The row's IRI is a safe region."* `_on_pages` never sees it (candidates are filtered by their
  cells' regions), and `_paths_by_region` keys it whole.

## 11. Decisions for the maintainer

1. **The `UNCLAIMED` name and placement in loop A** (§ 6.3). Recommended as written.
2. **Emitting `tab:colIndex`** goes past ruling 4's letter (which names rows) in its spirit: ruling 2
   says "column order" and no column order is asserted today. Recommended.
3. **`tab:colIndex`'s range stays `xsd:integer`** beside `tab:rowIndex`'s `xsd:nonNegativeInteger`.
   Changing a released term's range is a contradiction-class doc impact; leaving them unequal is not.
   Recommended: leave it.
