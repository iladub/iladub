# Loop 1 · the table-holon compiler

**Owns:** compile *any* table region — record, matrix, **pivot**, nested/hierarchical, key-value, stacked —
from a PDF/image into a **validated table-holon**. This is the case where every off-the-shelf parser
(LlamaParse, docling, unstructured) fails: merged cells + hierarchical headers. *A table is not an array.*

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ ② PROBLEM  compile any table (all kinds) → table-holon; parsers fail on pivots.    │
│            Human keeps: the topology ontology + review of escalated residue.        │
├────────────────────┬───────────────────────────────────────┬────────────────────────┤
│ ③ TRIGGER          │  ① GOAL / VERIFIER                     │ ⑦ CONTROL              │
│ a region typed     │  the table-holon (a) ROUND-TRIPS       │ continue · retry (new  │
│ "table" by 1a      │  (re-render → spatial-ASCII, diff the  │ kind / re-abduce) ·    │
│ arrives            │  measured geometry) AND (b) conforms   │ repair (one span/col) ·│
├────────────────────┤  to the TABULAR-TOPOLOGY ontology      │ ESCALATE (dec) · ship  │
│ ④ ACTIONS          │  (SHACL): every leaf cell resolves to  ├────────────────────────┤
│ measure→ascii→     │  exactly ONE col-path × row-path;      │ ⑤ STATE                │
│ signal-tag→abduce  │  header trees TILE; the profiled KIND  │ table-holon + learned  │
│ generator→propose  │  holds. Assert validated, propose the  │ generator→field-of-    │
│ HTML→map to holon  │  rest. Silent-wrong impossible.        │ possibles + kind ptns  │
├────────────────────┴───────────────────┬───────────────────┴────────────────────────┤
│ ⑥ LIMITS  per-region iteration cap ·    │ ⑨ MODEL  small VLM, residue only (ambiguous │
│           VLM-call budget · no-progress │  spans / wrapped-vs-parent / kind), constrained│
│           → escalate as .text/media     │  decoding to the ontology; chosen last          │
├─────────────────────────────────────────┴─────────────────────────────────────────────┤
│ ⑧ OBSERVABILITY  every cell cites page+bbox+header-path · dec log per region ·          │
│                  round-trip diff image · score (validated vs escalated) · kind+generator│
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## ① Goal / Verifier — the tabular-topology contract (this is sub-project **B**)
A table-holon is **done** when:
- **Round-trip:** re-render the inferred structure back to spatial-ASCII and **diff it against the measured
  geometry** — the geometry is the oracle, no semantic ground truth needed.
- **Ontology-conformant (SHACL):** every **leaf cell** resolves to **exactly one** column-header-path × one
  row-header-path (the *access function* is total and unambiguous); the **header trees tile** the leaf
  columns (coverage + refinement, no gap/overlap); the profiled **kind** (record / matrix / pivot / nested /
  key-value / stacked) satisfies its constraint pattern; declared **types/units** hold.
- **Honest:** validated cells → **assertions**; anything the geometry can't decide → **proposition** (`dec`)
  and escalation. **Score = validated% + escalated%; silent-wrong is impossible.**

The verifier is the ontology + round-trip — **not** a tuned threshold — so it **generalises to every
document**. *(The full tabular-topology ontology — layers below — is the next spec; this canvas fixes what
it must certify.)*

## ④ Actions — the maker pipeline (your spatial-ASCII → HTML insight)
1. **Measure** geometry in points (1a) — the oracle substrate; provenance-to-page.
2. **Spatial-ASCII** — render the faithful monospace geometry; cheap, human- and model-legible.
3. **Signal-tag** — wrap each text box with its non-text signals as markup (font weight/style, **cell
   color**, border/rule adjacency, alignment, indentation). *Signals are **evidence for roles**, never
   truth.*
4. **Abduce the generator** — from signals + organisation, infer the likely producing tool/domain → a
   **bounded field of possibles** (which layout conventions and kinds are even on the table). Turns
   open-ended interpretation into a **verified search in a bounded field**.
5. **Propose an HTML-table hypothesis** — `tr/td/th`, `colspan`/`rowspan` for **merged cells**,
   `scope`/`headers=` for header→cell association. **HTML because it solves merges + header association and
   is dual-audience** (renders for humans, parses for machines). Deterministic where the geometry decides
   (gutters/tiling); **small VLM only on the residue**.
6. **Map HTML → the formal table-holon** (RDF, the tabular-topology ontology) with type/grounding hooks.

> HTML is the **legible bridge, not the ontology** — the formal RDF/SHACL model sits behind it and is what
> the verifier checks. "Valid HTML" ≠ "understood the table."

## The tabular-topology ontology (Goal's contract) — layers to model in the next spec
- **Physical:** cells+bboxes, grid, spans/merges, alignment, indentation, wrapping, font/emphasis/color,
  rules/borders, whitespace.
- **Logical:** the **access function** — value ← (col-header-path × row-header-path); header **trees**; stub
  (row-keys); data region; derived cells (totals/subtotals). *Align to **RDF Data Cube `qb:`** + **CSVW**.*
- **Pragmatic:** caption/title (subject+scope), legend/key, footnotes (exceptions), notes, source; signals
  as evidence.
- **Type/grounding hooks (domain-neutral):** per leaf a type (quantity+unit, code, date, category, text);
  domain terminology (LOINC/UCUM/FHIR) plugs in **via contract**, outside the topology ontology.
- **Kinds (the field of possibles):** record · matrix/cross-tab · pivot · hierarchical/nested · key-value ·
  concatenated/stacked · transposed — each a constraint pattern over the layers.
- **Holon:** the table *is* a holon (interior=values · boundary=header structure · context=caption/footnotes
  · projection=grounded observations); each cell a micro-holon grounded by its header-paths.

## ⑤ State · ⑥ Limits · ⑦ Control · ⑧ Observability
- **State:** the table-holon-in-progress; durable **skills** = generator→field-of-possibles map, learned
  kind/layout patterns, ontology refinements (cross-document learning).
- **Limits:** per-region iteration cap; VLM budget; no-progress → **escalate the region** as spatial-text
  media with a `dec` verdict (never spin, never fabricate).
- **Control:** continue / retry (different kind or re-abduce generator) / repair (one failing header span or
  column) / escalate (emit validated cells, degrade the rest to `.text`/media) / ship.
- **Observability:** cell provenance (page+bbox+header-path), the `dec` log, the round-trip diff image, the
  score, and the inferred kind + generator.

## Rollout
- **L1 report** — *profile* the table's topology and render its HTML + `dec` verdicts; emit nothing to the
  graph. (Where 1a is today, plus the topology profile.)
- **L2 assisted** — emit the table-holon; a human reviews every escalation.
- **L3 unattended** — autonomous within Limits, once the verifier is trusted across diverse documents.

### Increments (status)
- [x] **1 — record-table closing slice** (2026-07-05): flat record table compiled end-to-end to a
      validated `tab:` holon with a score; every other region escalated in-band as an
      `iladub:CandidateConcept`. Closes the loop at L1 for the record kind. (Delivered by the
      table-holon-closing-slice PR: spec + plan under `docs/superpowers/`.)
- [x] **2 — hierarchical headers + wrapped text** (2026-07-06): a merged/`pivot` **column**-header
      table with wrapped labels (the `pivoted_report_pdf` case) compiled end-to-end to a validated
      multi-level `tab:HierarchicalTable` — leaf-grid recovery (excluding spanning rows), row-clock
      logical rows, type-homogeneity header/body split, centered-span tree inference, and a **2-D
      round-trip** oracle; residue escalated in-band. Certified by the reused refinement/coverage
      SHACL + a new `WrappedCellShape`. (Delivered by the hierarchical-headers-loop PR.)
- [x] **3 — detect & escalate transposed tables** (2026-07-07): a transposed table (fields down the
      first column, records along the others) previously compiled to a silently-*inverted*
      `tab:RecordTable` at score 1.0 — a silent-wrong neither the round-trip (geometry) nor the SHACL
      (structure) catches. A **type-orientation oracle** (`looks_transposed`: a numeric row but no
      numeric column — iladub's first *semantic* oracle) now escalates it as `TRANSPOSED`; normal
      tables unaffected. Detect-and-escalate only. (Delivered by the transposition-detect-escalate PR.)
- [x] **4 — compile transposed tables (axis-flip)** (2026-07-07): a detected transposed table now
      COMPILES into a correct, un-inverted `tab:RecordTable` (`tab:sourceOrientation "transposed"`)
      by axis-flip — a *logical relabel over unmoved physical cells*, so provenance-to-the-page
      survives (every value still traces to its original box). A **second oracle**
      (`transpose_is_coherent`: every field-row is type-homogeneous) gates the compile against the
      *reverse* silent-wrong — a false-positive detection escalates rather than asserting an inverted
      table. Certified cell-by-cell by the existing round-trip + `tab:` SHACL. Closes the
      detect→compile arc opened by increment 3. (Delivered by the compile-transposed-tables PR.)
- [x] **5 — compile row-header hierarchies** (2026-07-09): the vertical mirror of increment 2. Grouped
      labels running DOWN the stub columns (encoded blank-below / forward-fill) previously flattened to a
      `tab:RecordTable`, silently dropping the grouping and mis-profiling the kind. A row-header tree
      (**new `tab:coversRow`**, mirror of `coversColumn`) is now inferred from the stub columns
      (`looks_row_grouped` + `classify_row_hier`) and compiled into a `tab:HierarchicalTable`, certified by
      **four guarded row SHACL shapes** mirroring the column tiling invariants. Design A: stub columns are
      the row-header *axis*, only data columns are leaf columns; `North` encoded once as a row-header. A
      structural tiling backstop (`row_tree_tiles`) escalates `ROW_GROUP_AMBIGUOUS` on pathological
      geometry; blank-below = ditto-grouping is a documented *reading convention* (the mirror of Loop 2's
      centered-merge). Column and row hierarchies are now one machinery reflected across the diagonal.
      (Delivered by the row-header-hierarchies PR.)
- [x] **6 — compile matrix / cross-tab tables** (2026-07-09): the culmination of increments 2 and 5 — a
      table with **both** a hierarchical column header (over the data columns) **and** a stub row axis, each
      body cell addressed by the cross-product `(column-path × row-path)`. Previously a cross-tab classified
      UNSUPPORTED and lost its row axis (the stub became a phantom uncovered leaf column). Now `classify_matrix`
      **composes** Loop 2's column tree (`coversColumn`) and Loop 5's row tree (`coversRow`) and
      `assert_matrix_region` emits both — certified by the **union of the existing column + row SHACL, with NO
      new vocabulary or shapes** (the `atColumn × atRow` access function was built for this since increment 1).
      The one new algorithm is a **proximity (Voronoi) column-span builder**: short cross-tab labels (`Q1`, `Q2`)
      over wide numeric groups defeat text-extent span recovery, so each data column is assigned to its nearest
      parent-label center (a documented *centered-merge* convention). Detection (`UNSUPPORTED` +
      `header_body_split ≥ 2` + `stub_data_split not None`) cleanly separates it from the increment-2 pivot
      (covered stub) and increment-5 row-hierarchy (flat column header); a non-tiling matrix escalates
      `MATRIX_AMBIGUOUS`. (Delivered by the matrix-crosstab PR.)
- [x] **7 — multi-table page segmentation** (2026-07-09): closes the compiler's worst residual failure —
      `detect_bands` is 1-D (vertical gaps only), so it **fused** side-by-side and stacked-no-gap (repeated
      header) tables into one confident (wrong) assertion. A recursive `segment(band)` pass now runs **before**
      `classify`: it **proposes** cuts (widest full-height gutter; repeated-header row) and **certifies** each by
      re-running the existing classifiers — a horizontal cut is taken only when both sides classify `RECORD_TABLE`
      **and both have their own stub** (`has_own_stub`), which splits genuine side-by-side tables while keeping a
      ≥2-data-column row-hierarchy whole; a genuine-but-unclean second table escalates `MULTI_TABLE_AMBIGUOUS`
      (via the stub asymmetry, threshold-free). **The safety property is provable and tested: every single table
      segments to exactly one region** (the cross-tab, whose `Q1|Q2` gutter looks like a boundary, stays whole
      because its right half is data-only). No new vocabulary. Limits (documented): non-record side-by-side and
      different-header no-gap stacks. (Delivered by the multi-table-segmentation PR.)
- [x] **8-pre — header-span coverage repair** (2026-07-09, hardening): Loop 2's text-extent span recovery
      **under-covered a short parent label over a wide column span** (a `Region` header over four wide numeric
      columns recovered `[1,2,3]`, orphaning `West`). `headers.repair_coverage` now extends a coarse header
      node to absorb contiguous adjacent orphaned leaf columns (excluding the col-0 stub), before parent-linking
      — additive and tiling-preserving, so it is a **no-op on every already-tiling tree** (zero regression,
      full suite green) and leaves multi-word / wrapped labels untouched. Enables a single-spanning-parent pivot
      to be read as a **named dimension** end-to-end (the structural prerequisite for Loop 8a's denormalization
      recovery). (Delivered by the header-span-hardening PR.)
- [ ] Field of possibles (each a future increment, escalated today):
      key-value · stacked · multi-word single-level headers ·
      **multi-band tables (header banded away from body — needs band-grouping)** ·
      **signal-tagging (font/colour/ruled-lines — an evidence fallback only when the geometry is
      insufficient)** · rich-format adapters (xlsx/xls/docx/html feeding the same `SourceCell`
      intermediate) · measured-vs-reconstructed ASCII diff view · domain grounding (value → LOINC/UCUM) ·
      retry/repair control · cross-run STATE ledger.
