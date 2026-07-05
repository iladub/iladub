# Loop 1 · closing slice — record-table compiler with the round-trip oracle

**Status:** design (approved 2026-07-05)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md)
**Sub-projects reused:** #31 (etkl maker: geometry → bands → leaf-grid), #32 (`tab:` verifier: tiling + access-function SHACL)

## Why this exists — the doctrine it satisfies

Loop 1 shipped two **horizontal layers** — a maker (#31) with no verifier and a verifier
(#32) with no maker — that never ran against each other. No PDF ever produced a validated
table-holon, so **no loop closed**. Per the corrected definition of done
([loops README](../../loops/README.md)): *a loop increment ships only when it closes* — real
input → maker → the **whole** Verifier → a **score**, residue escalated **in-band**.

This slice is the **thinnest end-to-end path that closes**: compile the *simplest* kind — a
**flat record table** (one header row, N data rows) — fully, and **escalate every other region**
as an in-band proposition. It reuses #31 and #32 wholesale and adds the missing Verifier half
(the round-trip oracle), a region classifier, the RDF holon mapper, the escalation contract,
and the score artifact.

## Scope & success criterion

**Input:** a synthetic PDF containing a flat record table *and* at least one non-record region
(a title band and the `pivoted_report_pdf` hard-case fixture). Real input, not a hand-authored TTL.

**Done (the loop closes) when, run on that PDF:**
- a `score` is produced,
- **every** region is either **asserted** or **escalated** — nothing silently dropped,
- `tab:` SHACL conforms on the asserted holon,
- the pivot region **escalates** (not a crash, not a fake assertion),
- a deliberately mis-assigned cell is **caught** by the round-trip oracle (silent-wrong impossible).

## Architecture & data flow

```
compile_tables(pdf) ─▶ extract_words → detect_bands                     (reuses #31)
   per Band:
     regions.classify(band) ─▶ RECORD_TABLE | UNSUPPORTED_TABLE | NON_TABLE
       RECORD_TABLE:   assign words→columns (gutters) ; row0 = header
                       roundtrip.gate(cell) per cell ─▶ assert | escalate cell
       else:           escalate whole region → iladub:CandidateConcept
   holon.to_rdf(asserted cells) + candidates ─▶ rdflib Graph
   pyshacl(Graph, tab-shapes.ttl, inference="rdfs", advanced=True)       (reuses #32)
   ─▶ CompilationReport(score, regions, graph, ascii diffs)
```

### New modules (each small, single-purpose)

| Module | Responsibility | Depends on |
|---|---|---|
| `src/iladub/etkl/regions.py` | classify a `Band` → `RegionKind` via the gutter/header-alignment oracle; assign words → (column, row) | `bands`, `grid` |
| `src/iladub/etkl/roundtrip.py` | the oracle: per-cell gutter-containment gate + spatial-ASCII render/diff | `regions`, `grid` |
| `src/iladub/etkl/holon.py` | map validated region → `tab:` RDF; map escalated region → `iladub:CandidateConcept` | `rdflib`, `regions` |
| `src/iladub/etkl/compile.py` | `compile_tables(pdf) → CompilationReport`; orchestrate; run `tab:` SHACL; compute score | all of the above, `pyshacl` |

Public API (`__init__.py`) gains: `compile_tables`, `CompilationReport`, `RegionReport`, `RegionKind`.

## The round-trip oracle **is** the kind-classifier (one test, two jobs)

A line's words **tile the detected leaf columns** iff every word box ⊆ exactly one column span
and crosses **no detected gutter** (the gutters #31 already found as blank-on-≥98%-of-rows). That
single gutter-containment question does both jobs:

- **Every** line (header + data) tiles cleanly → **flat record table**; each data cell that tiles → **assert**.
- The **header** line's words cross gutters (a merged/centered parent spanning multiple columns —
  exactly the pivot fixture) → **not** a flat record → escalate whole, `suggestedAnchor = tab:HierarchicalTable`.
- A **data** word straddles a gutter → **that cell** escalates (`ROUND_TRIP_FAIL`).

**What a "cell" is:** a cell = the set of words of one data row that fall within one leaf-column
span. `cellText` = those words joined (in x-order). The gate passes for a cell iff **every** word
of the cell lies within that column's span and **none** crosses a gutter — i.e., the cell's ink does
not leak into an adjacent column. A single word straddling a gutter is the failure signal.

**The gutter is the oracle — no tuned epsilon.** The spatial-ASCII of measured-vs-reconstructed is
rendered as the human-legible **evidence** attached to each verdict (the canvas's "round-trip diff
image"), but the pass/fail gate is the numeric containment test.

```
GATE per cell:  measured_box ⊆ assigned_column_span  AND  crosses no gutter
OBSERVABLE:     measured          reconstructed
                Hb |13.2|g/dL     Hb |13.2|g/dL     ✓
                WBC|7.8 |x10^9    WBC|7.8 |x10^9    ✓
```

### Structural hypothesis for a record region

- **Leaf columns** = the gutter-separated column spans from `infer_leaf_grid` (#31).
- **Row 0** = header; its cells are `tab:LabelCell`s naming the columns; one `tab:HeaderNode` per
  column at `headerLevel 0` (a flat, single-level header tree — trivially tiles, satisfies #32's tiling shapes).
- **Rows 1..N** = `tab:LeafRow`s; each data word → the column whose span contains it → one
  `tab:EntryCell` with `atColumn`/`atRow`.

## Ontology additions — `tab:` Physical layer (completes its own design)

The loop canvas already scopes a **Physical layer** ("cells+bboxes, grid, spans") into the
tabular-topology ontology; v0.1 implemented only the Logical layer. This slice adds:

- `tab:cellText` — `Cell → rdfs:Literal` (**not** constrained to `xsd:string`; the multilingual rule).
- `tab:onPage` — `Cell → xsd:integer` (page index).
- `tab:hasBBox` — `Cell → [ tab:x0 ; tab:y0 ; tab:x1 ; tab:y1 ]` (a BBox node, four `xsd:decimal`).
- `tab:RecordTable ⊑ tab:Table` — the v1 kind (the only new class). The escalation `suggestedAnchor`
  reuses the **existing** `tab:HierarchicalTable` — no new pivot class needed.
- Provenance: `EntryCell prov:wasDerivedFrom <doc#page-region>` (the source region, page + bbox).
- **New shape (optional, kept):** `tab:EntryCellPhysicalShape` — an `EntryCell` must carry
  `cellText`, `onPage`, and `hasBBox`; ships with a conforming example **and** a negative leak fixture.

`tab:` core stays standalone (zero HGA imports); provenance rides `prov:` per project convention.

## Assert / propose in RDF

**Assert** (structure faithful — no domain grounding, so no `PromotionDecision`; grounding is a later loop):

```turtle
ex:e10 a tab:EntryCell ;
    tab:atColumn ex:c1 ; tab:atRow ex:r0 ;
    tab:cellText "13.2" ; tab:onPage 3 ;
    tab:hasBBox [ tab:x0 160.0 ; tab:y0 705.0 ; tab:x1 188.0 ; tab:y1 715.0 ] ;
    prov:wasDerivedFrom <doc#p3-160-705> .
```

**Propose** (undecidable region — in-band, never dropped):

```turtle
ex:regB a iladub:CandidateConcept ;
    iladub:surfaceText "<spatial-ascii of the region>" ;
    iladub:suggestedAnchor tab:HierarchicalTable ;
    iladub:suggestedBy <etkl-compiler> ;
    dec:confidence 0.4 ;
    dec:rationale "KIND_NOT_SUPPORTED: header line crosses gutters (merged parent header)" ;
    prov:wasDerivedFrom <doc#p4> .
```

**Reason codes** (Python `enum`, mirrored as the `dec:rationale` literal prefix):
`KIND_NOT_SUPPORTED` · `NOT_A_TABLE` · `ROUND_TRIP_FAIL` · `SHACL_FAIL`.

## The score (defined so it can't be gamed)

The **scoring unit is the data word-token** — robust because it needs no reliable grid for the
escalated regions (whose grid is precisely what we couldn't trust). Over **table-candidate** regions
only (RECORD_TABLE ∪ UNSUPPORTED_TABLE):

```
score = asserted_tokens / (asserted_tokens + escalated_tokens)
```

- `asserted_tokens` = data-row word-tokens in record regions whose **cell** passed the round-trip gate
  (a token inherits its cell's verdict).
- `escalated_tokens` = tokens whose cell failed + **every** data-row token in unsupported-table regions.
- **NON_TABLE** regions (title/prose) are **excluded** from the ratio and **listed separately**
  ("2 non-table regions escalated"), so prose can neither dilute nor inflate the table score.
- Header-row tokens are structural (`LabelCell`s), not facts, and are **not** scored.

`score == 1.0` ⇔ every table-body token round-tripped. `silent-wrong` is impossible: a token is
asserted only if its cell passes the oracle; otherwise it is part of a visible proposition.
`RegionReport.cells` still reports the structured `EntryCell` count for record regions.

## The closing artifact

```python
report = compile_tables("serial_cbc.pdf")
report.score                 # 0.71
report.regions[0]            # RegionReport(kind=RECORD_TABLE, verdict=asserted, cells=15)
report.regions[1]            # RegionReport(kind=UNSUPPORTED_TABLE, verdict=escalated,
                             #              reason=KIND_NOT_SUPPORTED, anchor=tab:HierarchicalTable)
report.regions[1].ascii_diff # the spatial-ASCII evidence (str)
report.graph                 # rdflib Graph: tab: holon + iladub: candidates
report.to_turtle()           # serialize holon + propositions
```

`CompilationReport` and `RegionReport` are frozen dataclasses. `compile_tables` is the single
entrypoint. This report **is** the loop's score — the canvas's **L1 "report" tier**.

## Proof of closure (tests that make it real)

1. **`test_record_table_closes`** — record fixture → `score == 1.0`, all cells asserted, `tab:` SHACL
   conforms, graph has the expected columns/rows/entries with `cellText`+bbox+prov.
2. **`test_pivot_escalates`** — `pivoted_report_pdf` → the pivot region is an `iladub:CandidateConcept`
   (`suggestedAnchor` pivot/hierarchical), **not** asserted; `score < 1.0`; no crash, no fake assertion.
3. **`test_roundtrip_catches_misassignment`** — a word straddling a gutter escalates that cell,
   `score < 1.0`. Proves the oracle **bites** (the anti-silent-wrong test).
4. **`test_nontable_band_escalates`** — a title/prose band → `NOT_A_TABLE`, excluded from the ratio.
5. **`test_report_serializes`** — `report.to_turtle()` re-parses and conforms to `tab:` SHACL.
6. **`test_entrycell_physical_shape_negative`** — the new physical-layer leak fixture fails SHACL.

Fixtures reuse `tests/etkl/fixtures.py` / `demo/etkl_demo_data.py` (`lab_report_pdf` for the record
case, `pivoted_report_pdf` for the escalation). `reportlab`-dependent tests keep the `importorskip` guard.

## Explicitly out of scope (on the canvas, never a silent gap)

Multi-level / merged headers · non-record kinds (matrix, cross-tab, key-value, stacked, transposed) ·
signal-tagging · VLM residue · **domain grounding** (cell value → LOINC/UCUM/FHIR, the
`PromotionDecision`-governed step) · retry/repair control loops · the cross-run `STATE.md` ledger ·
figure/image regions. Each is a future **field-of-possibles** increment, recorded on the loop canvas —
never discovered by the user asking.

## PR shape

This branch (`table-holon-closing-slice`) carries #31 + #32 as substrate and adds the closing work; it
becomes Loop 1's first **closed-loop** PR. On merge, the held drafts #31 and #32 are closed as folded-in.
