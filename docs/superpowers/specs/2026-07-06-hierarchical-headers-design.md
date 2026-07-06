# Loop 2 · hierarchical headers + wrapped text — the geometry maker

**Status:** design (approved 2026-07-06)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** Loop 1 closing slice (`regions.py`, `roundtrip.py`, `holon.py`, `compile.py`, `tab:` physical layer)
**Reuses (verifier already exists):** `tab:` header-tree ontology (`HeaderNode`/`parentHeader`/`coversColumn`/`headerLevel`) + `CoverageShape`/`NoOverlapShape`/`RefinementShape` + `examples/tables/hierarchical-conformant.ttl`

## Why this exists — the problem no one solves verifiably

Hierarchical / merged column headers are the hardest case in table extraction. Line-based tools
(camelot, tabula, pdfplumber) have no header-tree concept and flatten. ML table-structure models
(Table Transformer/PubTables, Textract, Azure DI) detect *spanning cells* but emit a geometric grid,
not the **semantic access function** (which leaf a label governs), and are **probabilistic and
unverifiable**. LLM/VLMs hallucinate and cannot certify faithfulness. **There is no deterministic,
verifiable method** — which is exactly iladub's opening: our round-trip oracle + SHACL contract is the
certificate none of them have.

We already **own the destination and the structural verifier** (the `tab:` header tree + refinement
SHACL + a conformant hierarchical example). This loop is therefore the **maker** (geometry → header
tree) plus a new **vertical / 2-D round-trip oracle**.

## §1 — Scope & closing target

Compile a **column-hierarchical table with wrapped labels** end-to-end into a validated `tab:` holon.

- **Closing fixture:** `pivoted_report_pdf` — it already carries both traps: merged/centered
  "Current Visit" / "Prior Visit" parents **and** the wrapped "(SI)" sub-header line. **Done =** it
  stops escalating whole and produces a hierarchical holon whose header tree conforms to the existing
  refinement/coverage SHACL, with any unresolved residue escalated in-band.
- **In scope:** column header trees (arbitrary depth; tested at 2 levels) + wrapped cells (headers and
  body).
- **Out of scope** (see §8): row-header hierarchies, rich-format adapters, font/color/ruled-line signals.

## §2 — Architecture: the shared cell-evidence intermediate (the ingestion seam)

Introduce the **`SourceCell`** intermediate — the seam the compiler's front door normalizes *up* to,
not down to geometry:

```
SourceCell = { text, bbox, page,
               span_cols: int|None,     # merge across N leaf columns (abduced here)
               wrap_lines: tuple[bbox], # physical lines of one logical cell (abduced here)
               align: {h, v}|None,      # abduced from ink position
               header_hint: bool|None,  # abduced (spanning / above-boundary)
               provenance }
```

Thin **adapters** (one per media) fill `SourceCell`s at whatever fidelity the format allows; one
**agnostic brain** (§3–§4) consumes them, *using* structure when supplied and *abducing* it when
absent. **This loop builds the intermediate + the geometry adapter (which abduces span/wrap/align) +
the brain.** Rich adapters (`xlsx`/`docx`/`html`, which fill span/wrap/align *exactly* via
`openpyxl`/`python-docx`/DOM) are later thin increments feeding the same model — the verifier is
identical for all. HTML-with-`colspan`/`rowspan` is the legible view of this intermediate (the canvas's
"HTML hypothesis"); the `tab:` RDF is what the verifier checks.

New module: `src/iladub/etkl/cells.py` (the `SourceCell` model + the geometry adapter that produces
them from `Word`/`Line`/`Band`).

Wrapped-cell grouping is a **general primitive** applied in both the header and body regions before
levels or rows are assigned — the closing fixture's wrap is in the *header* (the "(SI)" line is a
wrapped continuation of the "Result" leaf label), while body wrap is exercised separately (§7.2).

0. **Wrapped-cell grouping** (`cells.py`). Two physical lines merge into **one** `SourceCell` iff they
   lie within the **same column-span**, are **vertically contiguous** (gap ≈ intra-cell leading, i.e.
   below the region's row-gap norm), and the lower line does **not** independently tile its level/row
   (a line that covers its level is a new level/row, not a wrap). This is what tells "Result"+"(SI)"
   apart from a third header level: "(SI)" sits under only two of the leaf columns and hugs "Result".
1. **Logical rows — the "row clock"** (`rows.py`, body region). The anchor is a column with **exactly
   one `SourceCell` per candidate row** (single-line, unwrapped); prefer the leftmost such (the
   row-stub). Its cell-tops set each logical row's top; a row's bottom is where its **tallest** cell
   ends. Assign every cell's lines to a band by **y-containment** (not top-alignment). **No such anchor
   column** → **escalate** the region.
2. **Header/body boundary** (`headers.py`). The body starts at the first row where **every leaf column
   is type-homogeneous** (numeric / date / a small repeated-value category) — the label→data
   transition — **corroborated by "spanning stops"** (merged/centered cells are header-only). Ambiguous
   (all-text, no spans) → **escalate**.
3. **Header-tree inference** (`headers.py`). The header region's physical lines, after wrapped-cell
   grouping, form the levels: at each level a `SourceCell` **centered over a contiguous run of leaf
   columns** is a parent `HeaderNode` (`coversColumn` = that run); the deepest level supplies the leaf
   labels; `parentHeader` links the levels. Generalizes to N levels.
4. **Access function.** Each body cell → (leaf-column path × leaf row). One `EntryCell` per (leaf
   column × leaf row) as in Loop 1, now under a multi-level header tree.

## §4 — The verifier (designed first)

Three oracles; a column-path is asserted only if all three pass for it.

- **2-D round-trip (faithfulness).** Re-render the inferred tree (parents centered over their span) +
  logical rows (wrapped cells placed in their band × column) to **row-band-aware spatial-ASCII**, and
  require every **measured word** to land back in exactly one logical cell at its measured position.
  This is the anti-silent-wrong gate. It proves *faithfulness* but not *uniqueness* — hence:
- **Type-homogeneity (boundary/depth disambiguator).** The geometric round-trip cannot pin the
  header/body boundary or tree depth (several interpretations reproduce the same ink); type-homogeneity
  of body columns pins it (§3.2). Also enforced as a body invariant.
- **SHACL (structure).** Reuse `CoverageShape` (every leaf column covered), `NoOverlapShape`,
  `RefinementShape` (child span ⊆ parent), and `UnambiguousAccessShape` — **already built, free**. Add
  **one** new physical invariant: `tab:WrappedCellShape` — a logical cell's wrapped lines are
  contiguous within its column-span and row-band (with a conforming example + a negative leak fixture,
  per project convention).

## §5 — Escalation granularity & score

**Per-column-path**, mirroring Loop 1's hybrid:

- A leaf column whose **header path resolves** *and* whose **body cells round-trip** → its cells
  **asserted** (with full header-path provenance + bbox + page).
- An **ambiguous header subtree** or a column failing round-trip → its cells **escalate** as
  `iladub:CandidateConcept`, reason `HEADER_UNRESOLVED` or `ROUND_TRIP_FAIL`, carrying the region's
  spatial-ASCII. A **wholly** unresolvable table escalates whole (today's behavior) — never faked.
- **Score** = asserted tokens / (asserted + escalated), the same word-token unit as Loop 1; header
  labels (LabelCells) remain structural and unscored.

## §6 — Spatial-ASCII upgrade (`roundtrip.py`)

`render_ascii` becomes **row-band-aware**: a logical row occupies K ASCII lines (K = max wrap depth in
the band), and each cell's text is placed within its band × column. This is the shared substrate for
the §4 round-trip renderer and also sharpens Loop 1's escalation evidence. Backward-compatible for
single-line tables (K = 1 reduces to today's output).

## §7 — Proof of closure (tests)

1. **`pivoted_report_pdf` → validated hierarchical holon**: the Current/Prior tree conforms to
   `RefinementShape`/`CoverageShape`; the wrapped "(SI)" is grouped into its Result cell; score reflects
   the asserted columns. (This is the region that escalates whole today.)
2. **Row-clock unit test**: a wrapped record table → logical rows correct, the wrapped cell's physical
   lines grouped into one cell by y-containment.
3. **Ambiguous-boundary escalation**: an all-text table with no spans → `HEADER_UNRESOLVED`, escalated,
   **not guessed**.
4. **Round-trip bites**: a deliberately mis-spanned header (parent span not matching the ink) → fails
   the 2-D round-trip → escalated.
5. **SHACL negative**: the `tab:WrappedCellShape` leak fixture fails; the conforming example passes.
6. **No regression**: Loop 1's record + closing-slice tests stay green (single-line path unchanged).

## §8 — Out of scope (recorded on the canvas, never silent)

- **Row-header hierarchies** — merged row-spanning stubs (the vertical analog of the column header
  tree). **This is a certain future loop:** pivot tables and aggregation-by-index produce row
  hierarchies for sure. It needs a new ontology term (`tab:coversRow`, the row analog of
  `coversColumn`) and a symmetric maker. **Deferred deliberately, not overlooked.**
- **Signal-tagging** — font weight/style, cell color, and **explicit ruled lines**. These are an
  **evidence fallback** to be engaged *only when the semantic geometry is insufficient* to resolve a
  case (reducing escalations), never the primary method. "Signals are evidence, never truth."
- **Rich-format adapters** (`xlsx`/`xls`/`docx`/`html`) — thin later increments that fill the same
  `SourceCell` intermediate exactly; the brain and verifier are unchanged.

## Module map (new / touched)

| File | Responsibility |
|------|----------------|
| `src/iladub/etkl/cells.py` (create) | `SourceCell` intermediate + geometry adapter (abduce span/wrap/align) |
| `src/iladub/etkl/rows.py` (create) | logical-row bands via the row-clock + wrapped-line assignment |
| `src/iladub/etkl/headers.py` (create) | header/body boundary (type-homogeneity+spanning) + header-tree inference |
| `src/iladub/etkl/roundtrip.py` (modify) | row-band-aware `render_ascii` + 2-D round-trip check |
| `src/iladub/etkl/holon.py` (modify) | emit multi-level header tree (`parentHeader`) + per-column-path escalation |
| `src/iladub/etkl/regions.py` (modify) | admit hierarchical regions (route past the single-word-header gate) |
| `src/iladub/etkl/compile.py` (modify) | per-column-path score/escalation for hierarchical regions |
| `vocab/shapes/tab-physical-shapes.ttl` (modify) | add `tab:WrappedCellShape` |
| `examples/tables/*`, `tests/tab-*-leak.ttl` | wrapped-cell conforming + leak fixtures |
| `tests/etkl/test_*` | the §7 proof suite |
