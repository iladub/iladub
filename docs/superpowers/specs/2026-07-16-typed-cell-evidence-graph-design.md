# Typed-Cell Evidence Graph — Type/Orientation Boundaries (Neurosymbolic Loop B2a) — Design

**Date:** 2026-07-16
**Status:** Design approved (scope + mechanism settled; header/body-split query feasibility-proven); ready for implementation plan.
**Governed by:** CLAUDE.md §8 (the neurosymbolic-first gate — AXIOM / NEURAL / **PROCEDURAL**, with the open/closed derivation-vs-constraint split) + `docs/superpowers/specs/2026-07-14-recovery-layer-neurosymbolic-audit.md` (items C1 header/body split, E1 stub/data split, F1 transpose orientation).
**Builds on (shipped):** loops one (transform substrate), B (role-derivation axioms), C (SHACL region gate). B2 introduces the **first pre-holon evidence graph** in the pipeline.

---

## 1. Goal

Four type/orientation decisions run mid-compile on Python geometry, *before* any table-holon RDF exists, and each keys on per-cell `is_numeric` typing over a grid of cells:

- **`headers.header_body_split(band, grid)`** (C1) — first line at/after which ≥1 leaf column is all-numeric to the band end.
- **`rowheaders.stub_data_split(band, grid)`** (E1) — count of leading text-stub columns (`k`), with columns `[k..]` all-numeric.
- **`orientation.looks_transposed(region)`** + **`transpose_is_coherent(region)`** (F1) — the type-orientation oracle (a typed numeric row but no typed numeric column; every value-row type-homogeneous).

B2a lifts all four from Python-over-geometry to declarative **SPARQL derivations** over a new **typed-cell evidence graph**, *faithfully* — preserving the existing numeric-homogeneity proxy exactly (a differential oracle). Scope is **these four** (the pure-typing decisions). **Deferred (B2c):** `regions.classify` (its `_word_in_column` alignment is geometric containment — PROCEDURAL — mixed with routing).

## 2. Gate compliance (CLAUDE.md §8 — open/closed split)

- **AXIOM — derivation (open world) → SPARQL.** Each decision *recovers* a boundary / count / orientation from typed-cell evidence — a derivation (the loop-B side of the gate), monotonic and evidence-positive. Expressed as SPARQL `SELECT`/`ASK` over the evidence graph. No SHACL (this is derivation, not conformance). No tuned constant.
- **PROCEDURAL (justified; Python in the reference implementation, language-agnostic class):** (1) `is_numeric` — raw datatype detection from text (irreducible raw extraction); (2) the typed-cell **evidence-graph emitter** — raw extraction of `(row, col, text, isNumeric)` facts; (3) the query **runner** — rdflib engine glue + parsing the scalar result back. No decision logic in Python; no tuned constant.
- **NEURAL:** none. The known *margins* — the numeric-homogeneity proxy's narrowness (acknowledged in `header_body_split`'s docstring), ambiguous typing — are **loop-two**; B2a lifts the existing AXIOM core faithfully and does not touch the proxy.

## 3. Architecture — the typed-cell evidence graph (the novel foundation, feasibility-proven)

The four decisions currently operate on Python `Band`/`LeafGrid`/`Cell` objects. B2a introduces a small, **transient, pre-holon** RDF graph built per band/region — the first evidence graph that is *not* a table-holon:

```
?cell a tab:GridCell ;
      tab:atGridRow    ?r ;      # 0-based line/row index
      tab:atGridColumn ?c ;      # 0-based leaf-column index
      tab:gridText     ?t ;      # the cell's surface text
      tab:isNumeric    true|false .   # is_numeric(?t), PROCEDURAL raw typing
```
Only **populated** cells are emitted (matching the Python, which skips empty cells). The graph is built, queried, and discarded per decision — never merged into a holon.

**Proven (2026-07-16):** `header_body_split` — the trickiest ("MIN row where some column is all-numeric to the end") — reproduces the Python exactly over a battery (split@1, a 2-line header split@2, all-text→None, 3-column), as a standard SPARQL aggregate `SELECT`:

```sparql
# header-body-split.rq  (proven). Returns the min body-start row, or empty -> None.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?s) AS ?split) WHERE {
  ?anycell tab:atGridRow ?s . FILTER(?s >= 1)
  FILTER EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?r1 . FILTER(?r1 >= ?s)
    FILTER NOT EXISTS { ?cx tab:atGridColumn ?col ; tab:atGridRow ?r2 ; tab:isNumeric false . FILTER(?r2 >= ?s) }
  }
}
```
(The other three are simpler variants over the same graph; each is TDD-validated per-`.rq` against the Python in the plan.)

## 4. The four decisions as SPARQL

Each keeps its **Python signature** (callers unchanged); the body becomes: emit the evidence graph → run the `.rq` → parse the scalar → return it (`None`/`False` when the result set is empty / the ASK is false).

- **`header-body-split.rq`** → `int|None` (§3, proven).
- **`stub-data-split.rq`** → `int|None`: the first column `k` all-numeric on body rows (rows `≥ split`), requiring `k ≥ 1` and every column `≥ k` all-numeric; else empty → `None`. (Consumes the split — either as a bound param or by composing with the header/body evidence.)
- **`looks-transposed.rq`** → `bool` (ASK): `EXISTS { a body row whose cells in columns ≥ 1 are all numeric }` **AND** `NOT EXISTS { a column whose body cells are all numeric }`.
- **`transpose-coherent.rq`** → `bool` (ASK): `NOT EXISTS { a row with, among its columns ≥ 1, both a numeric and a non-numeric cell }` (every value-row homogeneous).

## 5. Components

| Unit | Responsibility | Gate |
| --- | --- | --- |
| `src/iladub/etkl/celltype.py` (create) | the typed-cell evidence-graph emitter `grid_evidence(cells) -> Graph` + a scalar-query runner (`run_scalar(rq, graph, param?)`, `run_ask(rq, graph)`) | PROCEDURAL |
| `vocab/queries/{header-body-split,stub-data-split,looks-transposed,transpose-coherent}.rq` (create) | the four decisions as SPARQL derivations | AXIOM |
| `vocab/ontology/tab.ttl` (modify) | owned evidence terms `tab:GridCell`, `tab:atGridRow`, `tab:atGridColumn`, `tab:gridText`, `tab:isNumeric` (transient evidence, like `tab:namesLevel`) | owned vocab |
| `src/iladub/etkl/headers.py` (modify) | `header_body_split` body → build evidence + run `header-body-split.rq`; `is_numeric` unchanged | AXIOM exec + PROCEDURAL |
| `src/iladub/etkl/rowheaders.py` (modify) | `stub_data_split` body → run `stub-data-split.rq` | AXIOM exec + PROCEDURAL |
| `src/iladub/etkl/orientation.py` (modify) | `looks_transposed` / `transpose_is_coherent` bodies → run the two ASK `.rq` | AXIOM exec + PROCEDURAL |
| `tests/etkl/test_celltype.py` (create) | the differential oracle (battery vs the retired Python) + per-`.rq` unit tests | test |

`is_numeric` stays PROCEDURAL (raw typing) — the emitter calls it. The emitter is fed the **caller's existing cell extraction** (`_col_values` for the split pair; `region.cells` for orientation) so behaviour is preserved exactly; only the *decision* moves to SPARQL.

## 6. Data flow

```
band/region (Python geometry)
   │  is_numeric per cell  [PROCEDURAL raw typing]
   ▼  grid_evidence(cells) → typed-cell RDF (GridCell: row/col/text/isNumeric)   [PROCEDURAL raw extraction]
   │
   ▼  run the decision .rq over the evidence graph                                [AXIOM · derivation · open-world]
   scalar (split line | stub count | transposed? | coherent?)
   │
   ▼  parse → return via the UNCHANGED Python signature → existing callers (classify / infer_header_tree / compile transpose branch)
```

## 7. Testing

- **Differential oracle (anti-overfit):** `test_celltype.py` runs a *battery* of constructed grids — header/body at various split lines (incl. multi-line headers), clean/ragged/None stub splits, transposed / upright / all-text / mixed-row orientations — and asserts each `.rq`-backed function returns **exactly** what the retired Python returned. A frozen Python reference (ported, as in loop B's `_ref_*`) is the oracle so it survives the rewrite.
- **Behavioural spec = the shipped suites, unchanged:** `test_headers.py`, `test_rowheaders.py`, `test_orientation.py`, `test_regions.py`, and the end-to-end compile suites stay green with existing assertions.
- **Per-`.rq` unit tests** (both the SELECT scalars and the ASK booleans) over the evidence graph.
- **Gate test:** the four `.rq` + `celltype.py` carry no tuned constant (extend the existing `test_transform_gate` glob / add a `celltype.py` scan).

## 8. Source ownership / conventions

- The `.rq` reference only `tab:` (owned) + standard SPARQL. The evidence terms are owned `tab:` in the standalone `tab.ttl`. No HGA/FnO term as a subject.
- The evidence graph is **transient** (built and discarded per decision) — never asserted into a holon, mirroring `tab:namesLevel`/`tab:barredAsOperand`.

## 9. Honest gaps & scope boundaries

- **In scope:** `header_body_split`, `stub_data_split`, `looks_transposed`, `transpose_is_coherent` → SPARQL over the typed-cell evidence graph, faithful lift, callers unchanged.
- **Out of scope:** `regions.classify` (B2c — geometric `_word_in_column` containment is PROCEDURAL; only its "header words == ncols" routing is AXIOM — a mixed decision, its own slice). The **NEURAL margins** (numeric-homogeneity proxy narrowness, ambiguous typing, wrap-vs-column) are loop-two — B2a does **not** change the proxy or the behaviour, only the *form* (Python → SPARQL). `is_numeric` stays PROCEDURAL.
- **Faithfulness caveat (probed):** the header/body-split query's candidate split rows are the rows that carry cells; a blank mid-table line as the true boundary is a documented edge the battery checks — if the SPARQL diverges from the Python there, that specific case is a justified PROCEDURAL residue with a why note (the SPARQL-ceiling rule), not a behaviour change.
- **New evidence-graph architecture:** a per-band graph build is a real cost, justified by the gate (four AXIOM decisions currently hand-coded) and reused by B2c and future type-boundary lifts.

## 10. Settled design decisions (for the implementation plan)

- **Mechanism: SPARQL derivation over a transient typed-cell evidence graph**, via a `celltype.py` emitter + runner; the four decisions keep their Python signatures. *Not* SHACL (derivation, not conformance — open/closed split). *Faithful* lift (differential oracle; proxy unchanged).
- **All four pure-typing decisions in this slice** (a+b); `regions.classify` deferred (B2c).
- **Probe-validated** for `header_body_split` (2026-07-16); the other three TDD-validated per-`.rq` against the frozen Python reference.
- **Behavioural suites stay green unchanged;** signatures/returns of the four functions preserved.

**Resume pointer:** design committed on `main`. **Next action:** invoke `superpowers:writing-plans` on this spec → task-by-task plan (celltype.py emitter+runner + evidence vocab → promote the header/body-split probe → stub-data-split → the two transpose ASKs → rewire the four bodies + differential oracle → supersession/gate verification) → subagent-driven execution. **After B2a:** B2c (`regions.classify`) and loop two (NEURAL span-perception) remain queued.
