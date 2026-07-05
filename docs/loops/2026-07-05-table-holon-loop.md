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
- [ ] Field of possibles (each a future increment, escalated today): multi-level/merged headers
      (pivot/hierarchical) · matrix/cross-tab · key-value · stacked · multi-word headers ·
      **multi-band tables (header banded away from body — needs band-grouping)** ·
      measured-vs-reconstructed ASCII diff view · domain grounding (value → LOINC/UCUM) ·
      retry/repair control · cross-run STATE ledger.
