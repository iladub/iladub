# Loop 4 · compile transposed tables (axis-flip) — close the detect→compile arc

**Status:** design (approved 2026-07-07)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** Loop 3 (detect & escalate transposed — `orientation.looks_transposed`, `tab:TransposedTable`) +
Loop 1 (record maker: `holon.assert_record_region`, `roundtrip.cell_round_trips`)

## Why this exists — turn a safe residue into a validated holon

Loop 3 closed a silent-wrong: a **transposed** table (fields down the first column, records along the
others) now *escalates* as an `iladub:CandidateConcept` (`TRANSPOSED`) instead of silently asserting an
inverted `tab:RecordTable`. That escalation is honest but incomplete — the table is still residue a human
must resolve. This loop **compiles** it: axis-flip the physical grid and emit a correct, un-inverted
`tab:RecordTable`, with provenance-to-the-page intact. The detect→compile arc Loop 3 opened now closes
end-to-end.

Worked target — this fixture (`transposed_report_pdf`), which Loop 3 escalates at score 0.00:

```
Field  Alice  Bob        physical col 0 = field names   → logical HEADER
Age    30     25         physical cols 1..n = records   → logical ROWS
Sex    F      M
City   NYC    LA
```

compiles to the correct record table (score 1.00):

```
Field  Age  Sex  City    ← logical header (= physical column 0, read down)
Alice  30   F    NYC      ← record (= physical column 1, read down)
Bob    25   M    LA       ← record (= physical column 2, read down)
```

## §1 — Scope & closing target

- **Closing proof:** `transposed_report_pdf` (Loop 3: escalates, score 0.00) now **compiles** to a
  `tab:RecordTable` — header `[Field, Age, Sex, City]`, 2 leaf rows (`Alice`, `Bob`), 6 entry cells,
  `tab:sourceOrientation "transposed"`, score 1.00, conforming to the `tab:` SHACL — and every entry
  cell's `hasBBox`/`wasDerivedFrom` still points at its **original physical** page position.
- **In scope:** the coherence gate (`transpose_is_coherent`), the axis-flip maker
  (`assert_transposed_region`) with a shared entry-cell emitter, the `tab:sourceOrientation` property,
  and the compile/escalate gate in `compile.py`.
- **Out of scope:** transposed tables with **hierarchical** (multi-level) headers on either axis;
  transposed tables whose field-rows are individually type-mixed (a "Notes" field that is sometimes
  numeric) — these stay *detected-and-escalated* (§4); fully-numeric / all-text transposition (never
  detected — Loop 3 §8). Row-header hierarchies (`tab:coversRow`) remain a separate future loop.

## §2 — The compile gate is TWO oracles (the anti-silent-wrong crux)

Compiling is strictly harder than escalating. Escalating a false positive is safe — a human reviews the
`CandidateConcept`. **Compiling** a false positive is a *silent-wrong*: a genuinely-upright table, flipped,
still tiles and so passes the `tab:` SHACL — re-introducing the exact inversion Loop 3 closed, in the
opposite direction. So compilation requires a second oracle beyond detection:

- **`looks_transposed(region)` — DETECTS** (Loop 3, unchanged): a numeric row exists, no numeric column.
- **`transpose_is_coherent(region)` — DECIDES WHETHER TO COMPILE** (new): **every** body row's cells in
  columns `≥ 1` (excluding the col-0 field-label) are **type-homogeneous** — all `is_numeric` or all
  non-numeric. A genuine transposed table has type-coherent *field*-rows (Age all-numeric, Sex/City
  all-text); a coincidentally-flagged upright *record* table has rows that mix a text label, a number, a
  unit and a flag — so it **fails** coherence.

**Gate:**

| `looks_transposed` | `transpose_is_coherent` | action |
|---|---|---|
| False | — | normal record path (unchanged) |
| True | **True** | **compile** the axis-flip → `tab:RecordTable` |
| True | False | **escalate** `TRANSPOSED` (Loop 3 behaviour — detected, not confidently compilable) |

This preserves the doctrine: detect-and-escalate stays the floor; compilation fires only when the second,
independent oracle confirms the transposed reading is coherent. A false-positive flip fails coherence and
escalates — **never** asserts an inverted table. `transpose_is_coherent` is a generalization of
`looks_transposed`'s own logic (which already tests "a row whose cols ≥ 1 are all numeric"), lifted from
*one* numeric row to *all* field-rows being type-homogeneous — an oracle, not a tuned constant.

`transpose_is_coherent` lives in `orientation.py` beside `looks_transposed`; both keyed on
`headers.is_numeric`.

## §3 — The flip is a LOGICAL relabel, not a geometric transform (how provenance survives)

The crux of provenance-to-page: **we never synthesize a flipped coordinate.** Each physical `Cell` keeps
its measured `words` (real `x0/top/x1/bottom/page`). The flip only reassigns *logical roles*:

Given physical cells `O[r][c]` (row `r`, col `c`), the transpose is the logical assignment `T[i][j] =
O[j][i]`:

- **logical column `k`** ← physical **row** `k`; its **header label** ← the physical col-0 cell `O[k][0]`.
- **logical row `m`** (records) ← physical **column** `m` (for `m ≥ 1`).
- **EntryCell (row `m`, col `k`)** carries physical cell `O[k][m]`'s **own words** → its `hasBBox`,
  `onPage`, and `wasDerivedFrom` are the *true physical* measurement, not a flipped coordinate.

Because each emitted entry cell reuses the original `Cell`'s `words` (and therefore `cell.bbox`),
provenance-to-the-page is preserved by construction. This is the property a naive "transpose the grid"
implementation would silently break, and it is asserted by an explicit test (§6.4).

## §4 — Same faithfulness oracle, at the cell level

Certify each entry with the **existing** `roundtrip.cell_round_trips(cell, boundaries)` on the **original**
grid — does the word fit its physical column span? (No new geometric oracle; a transposed table is a valid
grid in its physical orientation, which is exactly why the round-trip passed on it before.)

- physical cell round-trips → assert its transposed `tab:EntryCell`.
- physical cell straddles a gutter → escalate that cell as `iladub:CandidateConcept` (`ROUND_TRIP_FAIL`),
  identical to `assert_record_region`. Never silently dropped.

The emitted `tab:RecordTable` is then certified by the **existing** `tab:` SHACL (`tab-shapes.ttl` +
`tab-physical-shapes.ttl`) via the unchanged `compile._validate` gate — coverage, no-overlap, unambiguous
access all hold for a clean flat record table.

## §5 — Maker & ontology

### `assert_transposed_region(g, region, table_uri, doc_uri, page) -> int` (`holon.py`)

Emits a `tab:RecordTable` from the axis-flip and returns the asserted entry-cell count. Structure:

- `table_uri a tab:RecordTable ; tab:sourceOrientation "transposed"`.
- one `tab:LeafColumn` + level-0 `tab:HeaderNode` per physical row `k`; the header's `tab:hasLabel` is a
  `tab:LabelCell` carrying `O[k][0]`'s text + bbox + page (context carried, per doctrine).
- one `tab:LeafRow` per physical column `m ≥ 1`.
- for each physical `O[k][m]` (`m ≥ 1`): if it round-trips, an `EntryCell` at (logical col `k`, logical row
  `m`) via the shared emitter; else a `ROUND_TRIP_FAIL` `CandidateConcept`.

### DRY — shared entry-cell emitter

Extract `_emit_entry_cell(g, table_uri, doc_uri, page, e_uri, col_uri, row_uri, cell)` from the existing
`assert_record_region` body (the `EntryCell`/`atColumn`/`atRow`/`cellText`/`onPage`/`hasBBox`/
`wasDerivedFrom` block, reusing `_bbox_node`). Both `assert_record_region` and `assert_transposed_region`
call it, single-sourcing the provenance triples. `assert_record_region`'s external behaviour is unchanged
(a pure refactor, guarded by its existing tests).

### Ontology (`vocab/ontology/tab.ttl`)

Add one annotation property and refine the `tab:TransposedTable` comment (which currently says "not yet
compiled"):

```turtle
tab:sourceOrientation a owl:DatatypeProperty ;
    rdfs:domain tab:Table ; rdfs:range xsd:string ;
    rdfs:label "source orientation"@en ;
    rdfs:comment "The physical orientation of the source region a table-holon was recovered from:
      \"upright\" (default, omitted) or \"transposed\" (records ran along physical columns; the holon
      was recovered by axis-flip). The holon's logical kind is unaffected."@en .
```

`tab.ttl` stays standalone (no external subjects). The compiled holon is a plain `tab:RecordTable` +
the annotation; `tab:TransposedTable` remains the escalation anchor for the detected-but-incoherent case.
A `tests/test_tab.py` term-presence check confirms `tab:sourceOrientation`.

## §6 — Gate placement (`compile.py`) & proof of closure

In the `RECORD_TABLE` branch, replace the Loop 3 unconditional escalation with the two-oracle gate:

```
if looks_transposed(region):
    if transpose_is_coherent(region):
        table_uri = URIRef(f"{_DOC}#ttable{idx}")
        n = assert_transposed_region(graph, region, table_uri, _DOC, page_number)
        # score exactly like the record path: asserted vs round-trip-failed entry tokens
        ...
        reports.append(RegionReport(region.kind, "asserted", n, None, str(TAB.RecordTable), ascii_view))
    else:
        # detected but not confidently compilable — escalate (Loop 3 behaviour)
        escalate_region(..., "TRANSPOSED", TAB.TransposedTable, 0.4)
else:
    # existing upright RECORD_TABLE assert logic, unchanged
```

Scoring mirrors `assert_record_region`: asserted entry tokens over asserted + round-trip-failed. The
`_validate` gate already fires whenever a `tab:RecordTable` is present, so the compiled transposed holon is
SHACL-checked with no change to that call.

**Tests (proof of closure):**

1. **`test_transposed_compiles`** — `transposed_report_pdf` → a `tab:RecordTable` with
   `tab:sourceOrientation "transposed"`, header `[Field, Age, Sex, City]`, leaf rows `{Alice, Bob}`, 6
   `EntryCell`s, **no** `iladub:CandidateConcept`; `report.score == 1.0`; SHACL conforms. The Loop 3
   escalation is upgraded to a compile.
2. **`test_transpose_is_coherent_oracle`** (unit) — the transposed region → True; a normal record region
   (mixed-type rows) → False; a region with one coincidental all-numeric row but other mixed rows → False
   (the false-positive guard).
3. **`test_false_positive_transpose_escalates`** — a synthetic region that trips `looks_transposed` but is
   genuinely upright (fails coherence) → escalates `TRANSPOSED`, **no** inverted `RecordTable` asserted.
   The compile-direction silent-wrong is closed.
4. **`test_transposed_provenance_to_page`** — the `EntryCell` for Alice's Age (`"30"`) has `onPage == 0`
   and a `hasBBox` equal to the physical `"30"` word's measured bbox (i.e. provenance points at the true
   physical position, not a flipped coordinate).
5. **`test_transposed_cell_straddle_escalates`** — a transposed fixture with one straddling body cell →
   that cell escalates `ROUND_TRIP_FAIL`; the rest of the table asserts. Cell-level honesty preserved.
6. **`test_normal_tables_still_compile`** (regression) — `record_report` / `simple_table` compile upright
   unchanged; `assert_record_region` refactor is behaviour-preserving.
7. **`test_tab_sourceorientation_term`** — `tab:sourceOrientation` is declared with domain `tab:Table`.
8. **No regression** — full etkl + tab suite stays green.

## §7 — Showcase (part of the loop)

Update `demo/etkl_1a_showcase.ipynb` **Part E**: it currently renders the transposed PDF and shows it
*escalate*. After this loop it renders the original PDF first (unchanged — "print the original, always"),
then shows it **compile**: `score = 1.00 | RecordTable asserted: True | sourceOrientation: transposed`,
prints the recovered header `[Field, Age, Sex, City]` and one record (`Alice → Age 30, Sex F, City NYC`),
and states the "so what": the same table Loop 3 could only flag, Loop 4 compiles correctly — and Alice's
`Age` cell still traces to the physical `"30"` on the page (provenance survived the flip). Re-run the
notebook to 0 errors as part of the loop.

## §8 — What's notable

The **coherence gate** is the reusable idea: a corrective transform (axis-flip) is asserted only when an
independent oracle confirms it *improves* type-coherence, and falls back to escalation otherwise. It is the
general pattern for any future "repair" increment (mis-split columns, mis-merged headers) — repair is
asserted only under a second oracle, never on the strength of the detector alone. And provenance-to-page
surviving a structural correction — because the correction is a logical relabel over unmoved physical
evidence — is the property that lets ET(K)L *fix* a table without lying about where its values came from.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/orientation.py` (modify) | add `transpose_is_coherent(region) -> bool` |
| `src/iladub/etkl/holon.py` (modify) | add `assert_transposed_region`; extract shared `_emit_entry_cell` (refactor `assert_record_region`) |
| `src/iladub/etkl/compile.py` (modify) | two-oracle gate in the `RECORD_TABLE` branch (compile / escalate / assert) |
| `src/iladub/etkl/__init__.py` (modify) | export `transpose_is_coherent`, `assert_transposed_region` |
| `vocab/ontology/tab.ttl` (modify) | add `tab:sourceOrientation`; refine `tab:TransposedTable` comment |
| `demo/etkl_demo_data.py` (maybe) | a straddle / false-positive fixture if not synthesizable in-test |
| `demo/etkl_1a_showcase.ipynb` (modify) | Part E: escalate → compile |
| `tests/etkl/test_orientation.py`, `tests/etkl/test_closing_slice.py`, `tests/test_tab.py` | the §6 proof suite |
