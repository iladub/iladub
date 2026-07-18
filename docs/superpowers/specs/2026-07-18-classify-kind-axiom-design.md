# Declarative Kind Classification — `regions.classify` as AXIOM (Neurosymbolic Loop B2c) — Design

**Date:** 2026-07-18
**Status:** Design approved — ready for `writing-plans`.
**Governed by:** CLAUDE.md §8 (the neurosymbolic-first gate + the open/closed derivation-vs-constraint split).
**Audit basis:** `docs/superpowers/specs/2026-07-14-recovery-layer-neurosymbolic-audit.md` — item **B1** (`classify` routing = AXIOM; multi-word-header escape = NEURAL) and reframe **#5** ("`regions.classify` → declarative classification").
**Builds on (shipped):** the B2a/B2b typed-cell evidence-graph pattern (a transient pre-holon RDF graph + a SPARQL derivation + a thin PROCEDURAL emitter/runner). B2c applies the *same* pattern one step **earlier** in the pipeline — to the band→kind decision that *produces* the cells B2a later types.

---

## 1. Goal

Lift the **entire kind decision** in `iladub.etkl.regions.classify` — today a Python cascade over grid geometry — into a **SPARQL derivation over a new pre-holon evidence graph**, keeping only irreducible geometry (grid inference + word/column containment) as justified PROCEDURAL. This is a **faithful lift**: `classify` feeds the whole compile pipeline, so its output (kind, cells, and reason) must be **byte-identical** to today's. The anti-overfit gate is therefore a **differential oracle** (a frozen `_ref_classify` vs the new SPARQL-backed `classify` over a band shape battery), *not* a capability change — mirroring B2a's cleanest-review strategy.

The multi-word-header escape (a merged/wrapped header that is geometrically ambiguous with two gutter-collapsed columns — audit B1.2) stays **out of scope**: it escalates to `UNSUPPORTED_TABLE`, the conservative floor, and is deferred to the NEURAL span-perception layer (loop two).

## 2. Gate compliance (CLAUDE.md §8)

The decision is **MIXED**, and the audit already settled every boundary:

| Unit | Class | Justification |
| --- | --- | --- |
| `grid.infer_leaf_grid` (unchanged) | **PROCEDURAL** | raw grid/boundary extraction (its tuned constants are a *separate*, deferred NEURAL concern — audit reframe #3; B2c does not touch it) |
| `_word_in_column`, `column_of` (unchanged) | **PROCEDURAL** | geometric containment with `COORD_EPS` — the audit's "Honest PROCEDURAL boundaries" names *"geometric containment checks (`_word_in_column`, the ±0.5pt cell-fit) … correctly procedural"* (a float-comparison epsilon, same character as `is_numeric`'s float parse — **not** a tuned decision tolerance) |
| new evidence-graph **emitter** + query **runner** | **PROCEDURAL** | engine glue — emits RDF facts and invokes rdflib; **no decision logic, no tuned constant** (identical role to `celltype.py`) |
| the **kind routing** (NON_TABLE / UNSUPPORTED / RECORD, *including* the `<2 lines` / `<2 cols` structural guards) | **AXIOM — derivation (open world) → SPARQL** | a single holon-scoped `SELECT` over the band's evidence graph. The **band is the closure boundary**: the count/completeness guards (`#words == ncols`, "every column covered") are query-local `COUNT`/`NOT EXISTS` closing *within the one band* while the graph stays open — the exact holon-scoped closed-world guard §8 permits. No SHACL: this **derives** a kind from present evidence, it does not validate a membrane crossing. |
| multi-word-header escape (wrap-vs-two-cells) | **NEURAL — deferred** | genuinely perceptual; `UNSUPPORTED_TABLE` is the floor until loop two |
| `assign_cells` (unchanged) | **PROCEDURAL** | raw geometric assignment of words to cells once RECORD is decided |

**Why AXIOM, not SHACL (the open/closed split):** `classify` *grows* the interpretation from evidence — it derives what a band **is** — so it is an open-world derivation (SPARQL), monotonic and evidence-positive. It is emphatically **not** a membrane validating what may cross into a clean holon (that is Loop C's `region_tiles` SHACL gate). Deriving a kind is open-world; the tiling membrane is closed-world; §8's rule holds.

## 3. Architecture — a new, earlier evidence graph (feasibility-proven 2026-07-18)

`classify` runs **before** B2a's typed-cell graph exists (it produces the `Cell`s B2a later types), and it needs a **strict-containment** fact — `_word_in_column` (word *fully inside* a column's span, ±`COORD_EPS`), which is **stricter** than B2a's centre-of-mass `column_of`. A word can have its centre in column *i* (so `column_of = i`) yet straddle the gutter (so `_word_in_column` is false) — and that straddle is exactly the "not a clean 1:1 tiling" signal. So B2c cannot reuse B2a's `tab:GridCell` graph; it emits a **new, minimal band-classification evidence graph**.

**Evidence graph (transient, per band):**
```turtle
_ev:band a tab:ClassifyBand ;
    tab:lineCount     N ;          # len(band.lines)
    tab:gridColumnCount K .        # grid.ncols  (from infer_leaf_grid)

# one node per word in the header line (band.lines[0]), sorted left-to-right by x0:
_ev:hw-0 a tab:HeaderWord ; tab:headerWordOrder 0 [ ; tab:strictlyInColumn j0 ] .
_ev:hw-1 a tab:HeaderWord ; tab:headerWordOrder 1 [ ; tab:strictlyInColumn j1 ] .
    …
```
`tab:strictlyInColumn j` is emitted **iff** `_word_in_column(w, j, boundaries)` holds for the (unique) column *j* the word is strictly inside; it is **omitted** when the word straddles a gutter (strictly inside no single column). Columns are disjoint half-open spans, so a strictly-contained word has exactly one such *j* — the fact is unambiguous.

**Faithful reformulation (proven equivalent to the Python loop):** the current code tests `_word_in_column(w_i, i, b)` for the word at sorted position *i* against **column *i***, returning `UNSUPPORTED` on the first failure. Emitting `strictlyInColumn = the column the word is actually strictly inside` (searching all columns) and comparing it to `headerWordOrder` is equivalent:
- word *i* strictly inside column *i* → `strictlyInColumn = order` → aligned;
- word *i* strictly inside column *j ≠ i* → `strictlyInColumn ≠ order` → misaligned (Python: fails `_word_in_column(w_i, i, b)`);
- word *i* strictly inside no column → `strictlyInColumn` absent → misaligned (Python: same).
The differential oracle (§7) pins this equivalence.

## 4. The derivation — `vocab/queries/classify-kind.rq` (feasibility-proven)

A single holon-scoped `SELECT` returning **kind + nhw + firstBad in one query** (proven verbatim below — copy exactly into `classify-kind.rq`). The **band is the holon**; every `COUNT`/`NOT EXISTS`/`MIN` closes within it.

```sparql
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?kind ?nhw ?firstBad WHERE {
  ?b a tab:ClassifyBand ; tab:lineCount ?nl ; tab:gridColumnCount ?nc .
  { SELECT (COUNT(?hw) AS ?nhw) WHERE { ?hw a tab:HeaderWord } }
  BIND(EXISTS {
      ?w a tab:HeaderWord ; tab:headerWordOrder ?o .
      FILTER NOT EXISTS { ?w tab:strictlyInColumn ?o }
  } AS ?mis)
  BIND(IF(?nl < 2 || ?nc < 2, tab:NonTable,
       IF(?nhw = ?nc && !?mis, tab:RecordTable, tab:UnsupportedTable)) AS ?kind)
  OPTIONAL {
    SELECT (MIN(?o2) AS ?firstBad) WHERE {
      ?w2 a tab:HeaderWord ; tab:headerWordOrder ?o2 .
      FILTER NOT EXISTS { ?w2 tab:strictlyInColumn ?o2 }
    }
  }
}
```
Priority matches the Python cascade exactly: structural guards first (NON_TABLE), then clean-tiling (RECORD), else UNSUPPORTED. **Proven** against the shape battery (1-line, 1-col, clean 3-col record, count-mismatch, straddle-misalign, wrong-column-misalign, two-bad) — kind, `nhw`, and `firstBad` all correct in one SELECT.

**Byte-identical reason (user decision 2026-07-18):** the oracle pins `reason` too, so the reader uses the two auxiliary scalars the query already returns to *rebuild* the exact legacy string — the **decision** stays in SPARQL, only string assembly is Python. `nhw` = header-word count; `firstBad` = the smallest `headerWordOrder` among misaligned words = the first index Python would return on (clean→None, count-mismatch→None, straddle-at-1→1, wrong-col-at-2→2, two-bad-first-0→0 — proven). The reader reconstructs:
| kind / branch | reason (byte-identical to legacy) |
| --- | --- |
| NON_TABLE, `nl<2` | `"fewer than 2 lines"` |
| NON_TABLE, `nc<2` | `"fewer than 2 columns"` |
| UNSUPPORTED, `nhw≠nc` | `f"header has {nhw} words but {nc} columns"` |
| UNSUPPORTED, misaligned | `w = sorted(header.words, key=x0)[firstBad]`; `f"header word {w.text!r} is not aligned 1:1 with column {firstBad}"` |
| RECORD | `"flat single-level header"` |

The query yields **kind + nhw + firstBad in one SELECT**; a `run_row` runner returns the row (the existing `run_scalar`/`run_ask` return only one value — a new thin multi-value runner is engine glue, no decision).

## 5. Components

| Unit | Responsibility | Gate |
| --- | --- | --- |
| `src/iladub/etkl/classifygraph.py` (new) | `classify_evidence(band, grid) -> Graph` (emit the band-classification graph) + `run_kind(rq_path, graph) -> (kind_iri, nhw, first_bad)` multi-value runner | PROCEDURAL |
| `vocab/queries/classify-kind.rq` (new) | the kind derivation (kind + nhw + firstBad) | AXIOM |
| `vocab/ontology/tab.ttl` (modify) | add `tab:ClassifyBand`, `tab:lineCount`, `tab:gridColumnCount`, `tab:HeaderWord`, `tab:headerWordOrder`, `tab:strictlyInColumn`, and the kind individuals `tab:RecordTable`/`tab:UnsupportedTable`/`tab:NonTable` (a `tab:RegionKind` class) | owned vocab |
| `src/iladub/etkl/regions.py` (modify) | `classify` rewired: procedural guards → emit evidence → SPARQL kind → reason rebuild → (RECORD) `assign_cells`. `_word_in_column`, `column_of`, `assign_cells`, `Cell`, `ClassifiedRegion`, `RegionKind` **unchanged** | PROCEDURAL glue + AXIOM call |
| `tests/etkl/test_classifygraph.py` (new) | emitter unit tests + the **differential oracle** (`_ref_classify` vs `classify`) over a band shape battery | test |

**Naming note:** the runner could live in `celltype.py` (already the query-runner home), but B2c's graph is a *different, earlier* evidence graph, so a sibling module `classifygraph.py` keeps the two pre-holon graphs cleanly separated and their emitters colocated with their own queries. The `run_kind` runner lives with the emitter (both PROCEDURAL glue).

## 6. Data flow

```
band ─► [PROCEDURAL] len(lines), infer_leaf_grid → grid.ncols, boundaries
      ─► [PROCEDURAL] for each header word (sorted x0): _word_in_column → strictlyInColumn?
      ─► [PROCEDURAL] classify_evidence(band, grid) → RDF graph
      ─► [AXIOM]      classify-kind.rq  → (kind, nhw, firstBad)
      ─► [PROCEDURAL] rebuild reason; if RECORD → assign_cells(band, grid)
      ─► ClassifiedRegion(kind, band, grid, cells, reason)   # identical shape to today
```
`ClassifiedRegion`'s public shape is **unchanged** — every downstream consumer (`compile.py`, `segment.py`, `holon.py`, `rowheaders.py`, …) is untouched.

## 7. Testing — the differential oracle (behaviour must NOT change)

**(1) Differential oracle (the hard gate).** Freeze the current `classify` logic as `_ref_classify` (a verbatim copy in the test module). For every band in a **shape battery**, assert `classify(band)` and `_ref_classify(band)` return **equal** `kind`, `reason`, and (for RECORD) `cells` (row/col/text). The battery covers every branch:
- `<2` lines → NON_TABLE; `<2` columns → NON_TABLE;
- clean flat record (2-col, 3-col, wider) → RECORD, cells identical;
- header count ≠ ncols (too few, too many words) → UNSUPPORTED, exact reason;
- a header word straddling a gutter (strictly in no column) → UNSUPPORTED, exact `"header word 'X' is not aligned 1:1 with column i"`;
- a header word strictly in the wrong column → UNSUPPORTED;
- multiple misaligned words → reason names the **first** (lowest-order) one (matches Python early-return);
- the real fixtures the docstring cites (`wide_cell_table_pdf`, the pivot's `Prior Visit` multi-word header) → same kind + reason as today.

**(2) Emitter unit tests.** `classify_evidence` emits the right triples: `lineCount`/`gridColumnCount`, one `HeaderWord` per header word with correct `headerWordOrder`, `strictlyInColumn` present exactly for strictly-contained words and absent for straddlers.

**(3) Behavioural suite stays green.** `test_regions`, `test_segment`, `test_holon`, `test_orientation`, `test_rowheaders`, `test_hier_escalation`, and the end-to-end compile tests must **all** pass unchanged — the whole point of a faithful lift is that nothing downstream shifts. Any diff here is a regression to investigate, never to accept.

## 8. Source ownership / conventions

- All new terms are owned `tab:` individuals/classes in the standalone `tab.ttl` (zero `w3id.org/holon` references — alignment-not-import). `classify-kind.rq` references only `tab:` + standard SPARQL (no FnO/HGA term as a subject). Every triple's subject is a `tab:` term we own.
- Turtle authoring, JSON-LD interchange conventions unchanged. The query is standard SPARQL 1.1 (the SPARQL-ceiling rule: no bespoke functions).

## 9. Honest gaps & scope boundaries

- **In scope:** the full band→kind derivation (all three kinds + structural guards) as one AXIOM; the byte-identical faithful lift; the differential-oracle gate.
- **Out of scope (deferred, floor preserved):**
  - **Multi-word / multi-level headers** (audit B1.2, the wrap-vs-two-cells perception) — stays `UNSUPPORTED_TABLE`, the conservative escalation, for the NEURAL layer (loop two). B2c changes *nothing* about which bands are admitted.
  - **`infer_leaf_grid`'s tuned constants** (`0.98`/`3`/`4`) — a separate NEURAL boundary-perception concern (audit reframe #3); B2c consumes the grid as raw extraction and does not touch it.
  - **The `compile.py` kind-routing cascade** (audit reframe #5's other half) — a distinct slice; B2c is scoped to `regions.classify` only.
- **Faithful by construction:** the lift is byte-identical (kind + cells + reason). It adds **no** new recall and removes **no** escalation — credibility over completeness. The value is architectural: the kind decision is now declarative, inspectable, and portable, and the evidence graph is the seam the NEURAL multi-word escape will later attach to.
- **`COORD_EPS` stays procedural** — a float-comparison epsilon on raw geometry, not a decision tolerance; the audit is explicit that `_word_in_column` is correctly procedural.

## 10. Settled design decisions (for the implementation plan)

- **Whole classification body → AXIOM** (user decision 2026-07-18): NON_TABLE / UNSUPPORTED / RECORD, incl. the `<2 lines`/`<2 cols` structural guards, all derive in `classify-kind.rq`. Python is emitter + runner + reason-rebuild + `assign_cells`.
- **Byte-identical reason** (user decision 2026-07-18): the query returns `nhw` + `firstBad` (MIN misaligned order); the reader rebuilds the exact legacy reason string. Oracle pins kind + cells + reason.
- **New sibling evidence graph** (`classifygraph.py`), not a reuse of B2a's `tab:GridCell` — B2c is earlier and needs strict containment, not centre-of-mass.
- **Anti-overfit = differential oracle** (frozen `_ref_classify` vs new `classify` over a shape battery) + green behavioural suite. Faithful lift, not a capability change.
- **`_word_in_column`/`column_of`/`assign_cells`/`infer_leaf_grid` unchanged**; `ClassifiedRegion` public shape unchanged.

**Resume pointer:** design committed on branch `etkl-classify-axiom`. **Next action:** `superpowers:writing-plans` → task-by-task plan (owned terms + emitter + emitter tests → `classify-kind.rq` + `run_kind` runner → rewire `classify` + reason rebuild → the differential-oracle battery + green-suite gate) → subagent-driven execution. **After B2c:** the knowledge-first + NEURAL propose→oracle→dispose disambiguation layers (B2a §9 roadmap; the multi-word-header escape lands here) and **loop two** (NEURAL span-perception).
