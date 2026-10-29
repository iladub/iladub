# An adopted grid is read — Implementation Plan (loop A, 2026-10-29)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:tab:05 — loop A of two (spec § header). `prog:met` stays false after this loop; loop B meets it.

**Topic:** tab · **Date:** 2026-10-29

**Execution: subagent-driven** (maintainer, 2026-10-29, in chat). Start in a fresh session, on a branch off `main` after PR #381 merges.

**Doc impact: increment.** As the spec states it (spec header): one new property, one property newly emitted, one new shape. Nothing released changes meaning.

**Goal:** apple p2's adopted `tab:DataGrid` reaches `feed.table_records`, and `truth.score_table` scores it **57 `CORRECT`, every other outcome 0, `SPURIOUS` 0, `UNCLAIMED` 0** against a committed SEC truth set (spec § 1 as overridden by § 12.4 item 1).

**Architecture:** the emitter asserts a row ordinal and a column index on every grid (Task 1). The feed gains a grid reader with the same return shape as `_read_table`, so passes 2 and 3 run unchanged (Tasks 2–3). The scorer learns grid row keys and a new `UNCLAIMED` count (Task 4). The truth extractor gains an SEC colspan mode that produces apple's truth set (Task 5). Pins, register rows and the one baseline regenerate close the loop (Task 6).

**Tech Stack:** Python 3, rdflib, pySHACL + rudof (`iladub.etkl.membrane.validate`), pytest.

**Spec:** `docs/superpowers/specs/2026-10-29-an-adopted-grid-is-read-design.md`. **§ 12 overrides § 6 wherever they differ**, and this plan cites § 12 in those places. Read § 6 and § 12 before any task.

## Global Constraints

- **No implementation source in this plan** (CLAUDE.md § Plan authoring rule 1). Each task states signatures, invariants and oracles. The body is the implementer's.
- **`## FALSIFICATION` block in every task report** (rule 4): remove or invert the thing the test pins, show it failing, restore with `cp`, and show the suite green. No block means the task review fails.
- **No tuned constant anywhere** (spec § 5). A plan step or diff that introduces one fails review.
- **The feed reads no IRI names.** Row order comes from `tab:rowIndex`, and column order from `tab:colIndex`, never from the `-rN`/`-cK` suffix (ruling 4).
- **Record and hierarchical tables keep their y0 order** (`src/iladub/feed.py:312`). Do not unify the two orders (spec § 6.2 item 2, § 7).
- **No verdict filter on grids** (spec § 6.2, § 7). Every adopted grid is `asserted` (spec § 4).
- `tab:rowIndex` takes `xsd:nonNegativeInteger`, written explicitly at the emitter (§ 12.1 item 4). `tab:colIndex` keeps its declared range `xsd:integer` (ruling § 11.3).
- **The Fed extraction mode is unchanged.** `tests/test_ground_truth_extract.py` stays green with no edit (spec § 6.4).
- **Corpus baseline:** regenerate exactly once, after the last input edit and after `git add` of every new input file (CLAUDE.md § Corpus baseline). `tests/ground-truth/` is an input (`scripts/corpus_baseline.py:56`).
- **Branch and PR only.** Implementation runs on a fresh branch or worktree off `main` after PR #381 (spec + this plan) merges. The required check is `test`.
- Corpus compiles are serial, one at a time, never beside pytest ([[corpus-runs-are-serial]]).

## Review Focus

These are the inputs the spec implies but no oracle O1–O10 exercises. Each line names its owning task, where its test is added.

1. **A grid row and a record-table row that deliver the same rid.** `multiplicity` is document-wide (`feed.py:534`, `:625`, `:658`), so both rows take a discriminator, and an existing record's id changes. A reader expects distinct ids, no crash, and the record-table row's concepts unchanged. → Task 3, test (h).
2. **A grid with no `tab:hasHeaderNode`** (fed p5 has 0, § 12.2). In per-cell mode its cells carry no column key, so several cells of one row share a rid until pass 3. A reader expects one distinct record per value cell. → Task 3, test (i).
3. **A grid row whose stub cells are all blank, but which has value cells.** The key tuple is empty, so the row takes the opaque `_row_discriminator` path (spec § 6.2). A reader expects its value cells to be read, not dropped. → Task 3, test (j).
4. **A section-label row: stub text, no value cell** (apple has 7). In per-row mode it mints a one-concept record, exactly as a record table's label-only row does. In per-cell mode it mints nothing, but its text still enters the `SHARED_ROW_KEY` count. → Task 3, test (k).
5. **An SEC value cell no header interval contains.** Its column path would silently shorten. A reader expects the extractor to raise `TruthMarkupError`, never to write a short path. → Task 5, test (e).

---

### Task 1: Row ordinal, column index, and their shape

**Files:**
- Modify: `vocab/ontology/tab-datagrid.ttl` (declare `tab:rowIndex` beside `tab:hasGridRow`, which sits at :85)
- Modify: `src/iladub/etkl/datagrid.py` (`emit_data_grid`, :692; columns at :722-733, rows at :736-760)
- Modify: `vocab/shapes/tab-shapes.ttl` (append the new shapes)
- Test: `tests/etkl/test_datagrid.py` (emission) and a new `tests/etkl/test_grid_index_shape.py` (O8)

**Interfaces:**
- Produces: on every grid row `r_uri`, `(r_uri, tab:rowIndex, Literal(r_i, datatype=XSD.nonNegativeInteger))`, where `r_i` is its position in `grid.rows`. On every grid column `c_uri`, `(c_uri, tab:colIndex, Literal(k, datatype=XSD.integer))`, where `k` is its position in `grid.columns`. Tasks 2 and 3 read both.

**Decisions already settled:**
- **Home:** `tab-datagrid.ttl`. The membrane's ontology union is irrelevant here (§ 12.2, second bullet).
- **No `rdfs:domain`:** a choice, not R61 (§ 12.2). Say that in the term's comment.
- **`tab:colIndex`, not `tab:columnIndex`:** `tab:columnIndex` (`tab.ttl:326`) is celltype evidence with no domain. `tab:colIndex` (`tab.ttl:558`) is domained on `tab:GridColumn`, which is exactly the subject. Say that in the commit message (§ 12.2).
- **Value order:** `r_i` is top-to-bottom (spec § 4, third bullet). `k` is left-to-right (§ 12.2, first bullet). Both are measured, so nothing to re-measure.

**Shape contract** (§ 12.1 items 3–5 override spec § 6.1):
- **(S1)** `sh:targetObjectsOf tab:hasGridRow`: `tab:rowIndex` `sh:minCount 1`, `sh:maxCount 1`, `sh:datatype xsd:nonNegativeInteger`.
- **(S2)** `sh:targetObjectsOf tab:hasGridColumn`: `tab:colIndex` `sh:minCount 1`, `sh:maxCount 1`, `sh:datatype xsd:integer`.
- **(S3)** `sh:targetSubjectsOf tab:hasGridRow`: a SPARQL constraint that no two distinct rows of `$this` share a `tab:rowIndex` term.
- **(S4)** the same for `tab:hasGridColumn` / `tab:colIndex`.
- **No `sh:targetClass` and no `sh:class` on `tab:DataGrid`.** `tests/etkl/test_compile_membrane_shapes.py:266` fails otherwise ([[R103]]).
- Each shape carries a distinct `sh:message` substring, so a test reads its own verdict, as `tests/test_rule_separated_ink.py:58-64` does.

- [ ] **Step 1: Write the failing tests.**
  - `test_datagrid.py`: emit apple-shaped grids with `emit_data_grid` (reuse the module's existing fixtures, and MEASURE which ones exist first). Assert:
    - every row carries exactly one `tab:rowIndex`, typed `xsd:nonNegativeInteger`, and the values are exactly `0..n-1`;
    - each row's index equals its `grid.rows` position;
    - every column carries exactly one `tab:colIndex` equal to `k`.
  - `test_grid_index_shape.py` (O8): validate with `membrane.validate(g, shapes, ont, engine=…)` on both `ENGINES`, as `test_rule_separated_ink.py:67-70` parametrises. Use a minimal hand-built grid with 2 rows and 2 columns. Each of the following is refused by its own message:
    - a row missing its index;
    - a row with two indices;
    - two rows sharing an index;
    - a column missing its index;
    - two columns sharing an index;
    - a row index typed `xsd:integer`.
  - Control: the hand-built grid with correct indices raises none of the four messages. A second control: a grid emitted by `emit_data_grid` raises none of them.
- [ ] **Step 2:** run both files and see them fail for the stated reasons: the term is missing, and the shape is absent.
- [ ] **Step 3:** declare the term, emit both triples, and append S1–S4.
- [ ] **Step 4:** run both files, plus `tests/etkl/test_compile_membrane_shapes.py`, `tests/test_artifact_declarations.py` and `tests/test_vocab_shapes.py`, and see them green.
  - `test_artifact_declarations.py:298` pins `== 189` tracked artifact files. No new `.ttl` is added, so it must stay 189. If it moves, a file was added by mistake.
- [ ] **Step 5: FALSIFICATION.**
  - Drop the `datatype=` argument and S1's datatype case must fail.
  - Emit `r_i` reversed (`n-1-r_i`) and the position assertion must fail.
  - Delete S3 and the shared-index case must fail.
  - Restore after each one.
- [ ] **Step 6:** commit `feat(tab): assert a grid row ordinal and column index, and constrain them`.

### Task 2: One skip rule, and `_read_grid`

**Files:**
- Modify: `src/iladub/feed.py` (`_read_table`, :238-313)
- Test: a new `tests/test_feed_grid.py`

**Interfaces:**
- Produces: `_read_entry(graph, e, header: dict) -> _CellEntry | None`. This is the one site for the skip rules now inlined at `feed.py:258-305`: an aggregation row is skipped, an unshown cell with non-empty text raises `AssertionError`, an unshown cell is skipped, a blank cell is skipped (`is_blank`, which includes the declared nil spellings — [[R167]]). Otherwise it returns the `_CellEntry` `_read_table` builds today, with `.cell` set. `_read_table` calls it. **Move the R213 comment block with the code it explains; do not duplicate it.**
- Produces: `_read_grid(graph, grid, *, stubs_are_entries: bool) -> tuple[list, dict, dict, tuple]`, returning `(ordered, rows, row_cols, stubs)`:
  - `ordered`, `rows` and `row_cols` have exactly `_read_table`'s shape and meaning;
  - `stubs` is the grid's non-`tab:MeasureColumn` columns, ordered by `int(tab:colIndex)`.
  - Entries are the `tab:EntryCell`s joined by `tab:hasDataCell`, and each passes through `_read_entry`, with `header = _column_header_path(graph, grid)`.
  - When `stubs_are_entries` is false, a cell whose `tab:atColumn` is a stub is not an entry.
  - `ordered` is sorted by `int(tab:rowIndex)` of each row that has at least one entry.
- Consumes: Task 1's `tab:rowIndex` and `tab:colIndex`.

**Invariants:**
- `_read_table`'s output is unchanged for every table. The existing feed suites pin that: `test_concept_feed.py`, `test_feed_*.py` and `tests/etkl/test_unshown_ink.py`.
- No y0 is read on the grid path.

- [ ] **Step 1: Write the failing tests** in `test_feed_grid.py`. Use a hand-built grid fixture with the triples `emit_data_grid` writes (`datagrid.py:715-775`), plus Task 1's indices.
  - **(O2)** Make three rows' `tab:rowIndex` order disagree with their bbox `y0` order and with their IRI suffix order. Then `ordered` follows `tab:rowIndex`.
  - **(O6)** Within a grid: an `tab:AggregationRow`'s cells, a blank cell, an `—` cell and an unshown-empty cell are all absent from `rows`. An unshown cell with non-empty text raises `AssertionError`. The same four cases on a `tab:RecordTable` through `_read_table` behave identically. Drive both readers from one parametrised table of cases, so the shared site is what is pinned.
  - **(O3, reader half)** One stub column. With `stubs_are_entries=False` the stub cell is absent from `rows`; with `True` it is present. `stubs` is that one column.
  - **(O4, reader half)** Three stub columns whose `tab:colIndex` order differs from their IRI order and from their `colX0` order. `stubs` follows `tab:colIndex`.
- [ ] **Step 2:** run and see failures, because `_read_grid` and `_read_entry` do not exist yet.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** run `tests/test_feed_grid.py`, every `tests/test_feed_*.py`, `tests/test_concept_feed.py` and `tests/etkl/test_unshown_ink.py`. All green.
- [ ] **Step 5: FALSIFICATION.**
  - Sort `_read_grid` by `y0`: O2 must fail.
  - Inline a copy of the skip rules into `_read_grid` with the aggregation check removed: O6 must fail.
  - Restore after each one.
- [ ] **Step 6:** commit `feat(feed): read an adopted grid's cells through the record-table skip rules`.

### Task 3: The grid branch of `table_records`

**Files:**
- Modify: `src/iladub/feed.py` (`table_records`, :502-747; pass 1 at :534-626)
- Test: `tests/test_feed_grid.py`

**Interfaces:**
- Produces: `_grid_row_keys(graph, grid) -> dict[row, tuple[str, str]]`, mapping each grid row to `(text, region)`:
  - it covers **every** `tab:hasGridRow` of the grid, including aggregation rows and rows with no value cell. That is the population the existing count uses (comment at `feed.py:554-557`; § 12.2 SHARED_ROW_KEY bullet);
  - `text` is the row's non-blank stub-cell texts in `stubs` order, joined by one space;
  - `region` is `_label_region(graph, row)[1]`. **Neither the feed nor the scorer writes `str(row)`** (§ 12.2, row-region bullet);
  - a row whose text is empty is absent from the dict.
  - Task 4 consumes this.
- Consumes: Task 2's `_read_grid`; Task 1's indices.

**Behaviour:**
- **Input set.** `table_records` collects `graph.subjects(RDF.type, TAB.DataGrid)` beside the two table classes, at :526-527. Grids are not passed to `_logical_tables`: a grid is a single-member logical table (spec § 4, fourth bullet).
- **Order of `per_logical`.** Every record or hierarchical logical table comes first, in today's order, then the grids, ordered by `(tab:onPage, str(grid))`. This leaves every existing record's *position* unchanged. Its *id* can still change, through multiplicity (Review Focus 1).
- **Per grid in pass 1:**
  - **Ruling 3.** If `stubs` is empty, the grid adds nothing to `per_logical` and raises nothing (O5).
  - **No spanning-key path.** If `_spanning_keys(graph, grid)` is non-empty, raise `AssertionError` naming the grid: a childless multi-column spanner would take the key split and drop the stub key (§ 12.2, passes-2-and-3 bullet). It is 0 on all 17 corpus grids, so it fires nowhere today. It is a producer-side guard, so say *why* at the site (CLAUDE.md § Producer-side guards).
  - Call `_read_grid(..., stubs_are_entries=not per_cell)`.
  - `owner = {r: grid}`.
  - `rid_of[r]` is `_grid_row_keys(...)[r][0]` when present, else `_row_discriminator(graph, r)`. There is no section-key prefix: no grid caption is a `SectionCaption` (§ 12.2).
  - Add each `rid` to `multiplicity`.
- **`row_keys`, per-cell only:** `{r: (text, r, shared)}` for every row in `_grid_row_keys`. `shared` is `True` when another row **of the same grid** delivers the same text, counted over the whole `_grid_row_keys` population. With `node = r`, pass 2's `_key_region(node)` gives the same region that `_grid_row_keys` names.
- Passes 2 and 3 are byte-unchanged (§ 12.2).

- [ ] **Step 1: Write the failing tests** (`test_feed_grid.py`; fixtures as in Task 2):
  - **(a) O3:** one stub column.
    - Per-row: one record per row, and the stub text is a concept value.
    - Per-cell: no record's `ROLE_CELL_VALUE` concept carries a stub text, and each row's records carry one `ROLE_ROW_KEY` concept whose text is the stub text.
  - **(b) O4:** three stub columns, with `colIndex` ≠ IRI ≠ x order. The per-cell row-key text is the three texts in `colIndex` order, joined by one space.
  - **(c) O5:** a stubless grid gives `table_records(g) == []` and `table_records(g, per_cell=True) == []`, with no raise.
  - **(d) O7:** three rows whose stub reads `Other`, each with two value cells. Per-cell mode gives 6 records, all with role `SHARED_ROW_KEY`, under 6 distinct `row_id`s, and three distinct row-key regions.
  - **(e) O2, record half:** the per-row record order follows `tab:rowIndex`, with the fixture of Task 2's O2.
  - **(f)** a grid with a spanning key raises `AssertionError` naming the grid.
  - **(g) O6, record half:** an aggregation row mints no record in either mode.
  - **(h) Review Focus 1:** a `tab:RecordTable` row and a grid row deliver one rid. Assert no raise, two distinct `row_id`s, and the record-table record's concepts equal those of the grid-free graph's record.
  - **(i) Review Focus 2:** a grid with no header node, in per-cell mode, gives one distinct `row_id` per value cell.
  - **(j) Review Focus 3:** a row with blank stubs and two value cells gives its two value cells as records, with an rid that is `_row_discriminator`'s.
  - **(k) Review Focus 4:**
    - A label-only row gives one record of one concept in per-row mode, and none in per-cell mode.
    - A label-only row reading `Other` plus one valued `Other` row makes the valued row's key `SHARED_ROW_KEY`.
- [ ] **Step 2:** run and see the failures.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** run the whole feed set from Task 2 Step 4, plus `tests/test_corpus_apple_contract.py`.
  - That file's pins are **expected to move**, so record which fail and their new values. Do not edit them yet: Task 6 re-measures them on the regenerated baseline (spec § 8, third bullet).
- [ ] **Step 5: FALSIFICATION.**
  - Make `shared` always `False`: (d) must fail.
  - Order stubs by IRI: (b) must fail.
  - Drop the stubless refusal so the grid reads with an empty key: (c) must fail.
  - Restore after each one.
- [ ] **Step 6:** commit `feat(feed): a grid's rows reach table_records, keyed by its stub cells (R341)`.

### Task 4: The scorer reads grid rows, and counts `UNCLAIMED`

**Files:**
- Modify: `src/iladub/truth.py` (`score_table` :79-120; `_scored_rows` :123-156; `_paths_by_region` :159-174; `_score_row` :185-210)
- Test: `tests/test_ground_truth_score.py`

**Interfaces:**
- Consumes: `feed._grid_row_keys` (Task 3).
- `_paths_by_region(graph)` adds `region → (text,)` for every grid row in `_grid_row_keys` over `graph.subjects(RDF.type, TAB.DataGrid)`. Use the same `_AMBIGUOUS` rule if two paths share a region.
- `score_table` returns its current dict plus the key `"UNCLAIMED"`.
- Measured: no caller of `_scored_rows`, `_score_row` or `_paths_by_region` exists outside `truth.py` (`grep -rn` over `src tests scripts`, empty). Their signatures are free to change.

**`UNCLAIMED`, exactly as ruled (§ 12.4 item 2; the "≥ SPURIOUS" claim at spec § 6.3 is withdrawn):**
- It counts the scored rows' **value-cell** positions (pairs that came from a `ROLE_CELL_VALUE` concept) that no truth cell claims.
- Claims are the **union across all truth groups**: a position any group's `_score_row` claimed is claimed.
- The `(leaf, leaf)` label pair and role-less riders are not value cells.
- A one-record-per-row record contributes no value-cell position, by the ruling's "per-cell value records".
- `SPURIOUS` and the six outcomes are computed exactly as today.
- The implementer chooses how `_score_row` reports its claimed positions back. The invariant is that positions are counted in `norm[i]`'s indexing, with the matched label index `j` excluded.

- [ ] **Step 1: Write the failing tests:**
  - **(O9a)** A compiled per-cell row that no truth group matches contributes all of its value cells to `UNCLAIMED` and none of its label pair.
  - **(O9b)** A matched row with one spurious value cell gives `UNCLAIMED == SPURIOUS == 1`.
  - **(O9c)** Two truth groups match one compiled row, each claiming a different cell of its three. Then `SPURIOUS == 4`, as today's per-group count gives, and `UNCLAIMED == 1`. This is the case that shows `UNCLAIMED` is not `SPURIOUS` renamed.
  - **(c)** A grid fixture from Task 3 (a), scored per-cell against a hand-written truth list for it, is all `CORRECT` with `UNCLAIMED == 0`. That proves `_paths_by_region` resolves the grid row region.
  - **(d)** Every existing test in the file stays green, with the dict now carrying `UNCLAIMED`. Where an existing test compares the whole dict, add the key with its measured value, and say so in the report.
- [ ] **Step 2:** run and see the failures.
- [ ] **Step 3:** implement.
- [ ] **Step 4:** run `tests/test_ground_truth_score.py` and `tests/test_ground_truth_floor.py`. The floor test reads the committed baseline, so it stays green until Task 6.
- [ ] **Step 5: FALSIFICATION.**
  - Return `SPURIOUS` as `UNCLAIMED`: O9a and O9c must fail.
  - Use per-group claims instead of the union: O9c must fail.
  - Restore after each one.
- [ ] **Step 6:** commit `feat(truth): score grid rows; report UNCLAIMED against the union of claims`.

### Task 5: SEC colspan extraction and apple's truth set

**Files:**
- Modify: `scripts/ground_truth_extract.py` (`extract_table` :93 stays as is; `main` :134-146 hardcodes the Fed ordinal and sha)
- Create: `tests/fixtures/sec-colspan-table.html` (hand-written, SEC-shaped); MEASURE the repo's fixture directory convention first, and use it if it differs
- Create: `tests/ground-truth/apple-fy2026q3-statements/{table-1.csv,floor.json,provenance.json}`
- Test: `tests/test_ground_truth_extract.py` (add tests; **do not edit the 4 existing ones**)

**Interfaces:**
- Produces: `extract_sec_table(html: bytes, ordinal: int, expected_sha256: str) -> list[TruthRow]`. It is a new function, as § 12.2's extractor bullet allows. It reuses `_span` and the sha check.
- `main` takes `--mode {fed,sec} --ordinal N --sha256 HEX`. Fed's current values are the defaults, so `python scripts/ground_truth_extract.py <html> <out>` behaves exactly as it does today.

**Extraction rules** (spec § 6.4, plus § 12.4 item 1):
- the table's column grid comes from `colspan` (absent means 1) as exact integer intervals;
- header rows are those whose first cell's text is empty;
- a value cell's path is every header whose interval contains the cell's interval, in header-row order, joined by `SEP`;
- a cell whose whole text is `$` is a glyph, not a value;
- `<br>` becomes a space;
- the value is the displayed text, never the XBRL sign;
- **a displayed value that `iladub.etkl.celltype.is_blank` calls blank is no cell** (§ 12.4 item 1: this drops apple's `—`);
- a row with no value cell yields nothing;
- `row_occurrence` counts repeated labels in row order, as `extract_table` does.

**Irreducibility (§ 12.2, § 5 bullet), stated in the docstring:**
- PROCEDURAL raw extraction from publisher markup, by exact integer intervals, with no tolerance;
- "a header row's first cell is empty" is a reading convention, not a publisher-stated fact;
- the convention is defended by the span sha and by the measured intersection, not by markup.

- [ ] **Step 1: Write the failing tests** on the committed fixture (O10):
  - (a) colspan intervals give two-level paths;
  - (b) a `$`-only cell is dropped and its neighbour value is kept;
  - (c) `June 27,<br>2026` reads `June 27, 2026`;
  - (d) a `—` value yields no row, while a `(1,234)` value is kept verbatim;
  - (e) **Review Focus 5:** a value cell no header interval contains raises `TruthMarkupError`;
  - (f) a wrong sha raises `TableSpanMismatch`.
- [ ] **Step 2:** run and see the failures.
- [ ] **Step 3:** implement, then run the whole extractor file. The 4 Fed tests must pass unedited.
- [ ] **Step 4: Produce apple's truth set.**
  - Fetch the source into the scratchpad, never into the repo:
    `curl -A "iladub-research contact@iladub.dev" -o <scratch>/aapl.htm https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm`.
  - Run with `--mode sec --ordinal 17` and the full sha. Take the full sha from the span: only its prefix `7999b55068408a58` and its length of 49,055 bytes are on record. Check both.
  - **Expected: 57 rows.** If any other count comes out, stop and report: the prediction is measured (§ 12.4 item 1), and a different count is a defect in the extractor or in the source, not a new number.
  - Write `floor.json` as `{"table-1": {"CORRECT": 57}, "notes": []}`.
  - Write `provenance.json` by hand, in the Fed file's key order: url, `retrieved` (today), `table_ordinal 17`, the full `span_sha256`, `span_bytes 49055`, `pages [2]`, and a `source_note` stating SEC public filing and that licensing was cleared by the maintainer on 2026-10-29.
- [ ] **Step 5: FALSIFICATION.**
  - Remove the `is_blank` drop: (d) must fail, and the apple run must give 58.
  - Remove the interval-containment raise: (e) must fail.
  - Restore after each one.
- [ ] **Step 6:** `git add` the new files, then commit `feat(truth): SEC colspan extraction; apple p2 truth set (57 cells)`.

### Task 6: Regenerate, pin O1, re-measure contracts, register

**Files:**
- Regenerate: `tests/corpus-baseline/*.json` and `inputs.json`
- Modify: `tests/test_corpus_apple_contract.py` (only the pins that moved)
- Test: `tests/test_ground_truth_score.py` (the O1 exact test)
- Modify: `docs/superpowers/residues.md` and `residues-open.md` (and `residues-closed.md` for R341)

- [ ] **Step 1: Write the exact O1 test.** Read `tests/corpus-baseline/apple-fy2026q3-statements.json` → `truth["table-1"]` and assert:
  - `CORRECT == 57`;
  - `WRONG_VALUE`, `MISATTACHED`, `LOST`, `MISSING`, `REFUSED`, `SPURIOUS` and `UNCLAIMED` are each `0`.
  - The floor test enforces only `≥` (§ 12.2, extractor bullet), which is why this one is separate.
  - Record `MARKED_LABEL` as measured, with no prediction for it.
  - It fails now: the baseline has no apple truth block.
- [ ] **Step 2: Regenerate, once.** First confirm that every input file is tracked. Then run `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`: about 24 minutes, serial, unattended, with no input edits while it runs.
- [ ] **Step 3: Read the blast radius** with `git diff --stat -- tests/corpus-baseline/`. Check it against spec § 9 and § 12.2:
  - `graph_sha256` moves for apple, bfs, caltrain, fed, ons and who-covid;
  - apple gains a `truth` block;
  - Fed's truth block gains `UNCLAIMED`, its six outcomes unchanged;
  - nothing else moves. Any other movement is reported and explained before going on.
- [ ] **Step 4:** run the O1 test and `tests/test_ground_truth_floor.py`. Both must be green.
- [ ] **Step 5: Re-measure the apple contract pins.**
  - The simulation predicted per-row 59 → 88 and per-cell 180 → 237 (§ 12.2, § 12.4 item 1). Those are predictions; the run decides.
  - Update each moved pin to its measured value, with the measurement in the commit message.
  - `test_p2_every_period_grounds` may gain periods or refuse some (spec § 8, first bullet). Record what happens; do not predict it.
- [ ] **Step 6: Register.** Take the next free numbers at implementation time (R342 is free at `8cb246c`), and record the tally snapshot on each new row.
  - **The stubless-grid refusal** (ruling 3; spec § 6.2): bfs `p5-datagrid-2` yields no records.
  - **`tab.ttl:547-548` (measured: the comment is on :548) says `tab:GridColumn` is "never asserted into a holon"**, but `emit_data_grid` asserts it (§ 12.2, last bullet). The fix is contradiction-class, so it is not made here.
  - **Fed p5's grid has no header node,** so its records carry no column key (§ 12.2, column-paths bullet).
  - **Close ~~R341~~** with the closure evidence: the O1 test and the apple truth block.
- [ ] **Step 7: FALSIFICATION for O1** (spec § 3). Revert Task 3's input-set change in a scratch copy and re-score apple's compiled graph with `score_table` (one compile, not a regenerate). Expect `REFUSED: 57`, every other outcome 0. Restore, and the suite is green.
- [ ] **Step 8:** run the full suite (`pytest`, read `N passed`, not the exit code — [[macos-has-no-timeout-command]]). Then commit `test: apple p2 is scored 57/57 through shipped code; baseline regenerated (R341 closed)`, push, open the PR with `**Serves:** prog:criterion:tab:05`, and enable auto-merge.

## Self-review (done at authoring)

- **Spec coverage.**
  - § 6.1 → Task 1; § 6.2 → Tasks 2–3; § 6.3 → Task 4; § 6.4 → Task 5; § 9 → Task 6.
  - § 12.1 items 1–5 → Task 5 rules, Task 4, and the Task 1 shape contract.
  - § 12.2's unguarded spanner → Task 3 (f); its three register items → Task 6 Step 6.
  - § 7's "not done" was checked against every test above. No test asserts disposal, a row header node, a multi-stub truth set, or a verdict filter (rule 5).
- **Setup constructibility (rule 5).** Every fixture is a hand-built graph of triples `emit_data_grid` already writes (`datagrid.py:715-775`), plus Task 1's two. O9c's two-groups-on-one-row case is constructible because `_score_row` runs per group (`truth.py:111`).
- **Downward same-file citations (rule 7).** This plan cites code lines only in other files. Every `feed.py`/`truth.py` line it cites is measured at `8cb246c`, and those lines **will** shift as Tasks 2–4 edit them. Implementers re-locate by symbol, not by number.
