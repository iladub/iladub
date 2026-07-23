# Concept Feed — ET(K)L tables → grounding (closes raw-doc→grounded-graph)

**Date:** 2026-07-22
**Status:** Design — approved for spec (brainstorm 2026-07-22).
**Slice:** Wire the ET(K)L table-compilation output into the knowledge-grounding pipeline — the
follow-up **(a)** of the grounding design (`2026-07-19-knowledge-first-grounding-design.md`). Closes
the end-to-end loop: **raw document → `compile_tables` → tab: RDF → concept feed → `ground_concept` →
grounded graph + propositions.**

**Gate context (CLAUDE.md §8):** the bridge is **PROCEDURAL raw extraction** (RDF reads over the
compiled table graph — no tuned constant, no IRI-name parsing). It introduces **no** new grounding
decision: it reuses the shipped `ground_concept` oracle unchanged (NEURAL propose → SHACL/scheme
membrane dispose → promote), so grounding soundness — *legality gates admission, confidence never
does* — is inherited. This is the RawDocument→grounding-portal→CleanDocument traversal of the holonic
interaction model.

---

## 1. The decision (one sentence)

A new `feed` bridge reads asserted `tab:RecordTable`s from a `CompilationReport.graph` and emits one
`SurfaceConcept(text=column-header, value=cell-text, region=cell-provenance)` per data cell, grouped by
row into records; a `ground_document` driver mints one subject per row and grounds each cell's concept
against a contract via the existing `ground_concept`.

## 2. Why this is the sound close (feasibility probed, 2026-07-22)

An offer table (`Organ/LVEF/ABO/COD` × 2 donor rows) was compiled through the real `compile_tables`
before speccing: it classifies **`RECORD_TABLE`, score 1.0**, and the compiled RDF exposes every link
the bridge needs **as triples** (no IRI-name parsing): `table hasHeaderNode h`, `h coversColumn c`,
`h hasLabel lc`, `lc cellText <header>`; and `EntryCell atColumn c`, `atRow r`, `cellText <value>`. The
bridge reconstruction yielded exactly two records with clean `(header, value)` pairs. The slice is
therefore de-risked; the grounding half is the already-shipped, reviewed oracle.

## 3. Components (each single-purpose)

### 3.1 `src/iladub/feed.py` — the bridge

- `@dataclass(frozen=True) Record(row_id: str, concepts: tuple[SurfaceConcept, ...])`.
- `table_records(graph: Graph) -> list[Record]`: for each `tab:RecordTable` subject —
  1. build `column → header-text` by walking `hasHeaderNode → (coversColumn, hasLabel → cellText)`;
  2. for each `tab:EntryCell`, read `atColumn` / `atRow` / `cellText`, resolve the column's header, and
     build `SurfaceConcept(text=header, value=cellText, region=<entry-cell provenance id>)`;
  3. group concepts by `atRow` (stable order by row, then column) → one `Record` per row.
  Pure RDF reads. `region` = a provenance id derived from the entry-cell identity (traces to the cell's
  `onPage`/`hasBBox` in the source graph — §6 provenance-to-the-page).

### 3.2 `ground_document(...)` — the driver (in `feed.py`)

`ground_document(graph, contract, proposer, terms, shapes, g) -> FeedResult` where
`@dataclass(frozen=True) FeedResult(records: int, grounded: int, proposed: int)`. Iterates
`table_records(graph)`; for each `Record` mints `subject = URIRef("urn:iladub:record:" + row_id)`;
grounds each concept via the shipped `ground_concept(concept, contract, subject, proposer, terms,
shapes, g)`, tallying `"grounded"` / `"proposed"`. Populates `g` (grounded graph + propositions).
Subject minting is internal (no callback param — YAGNI).

### 3.3 `MappingGroundingProposer(mapping)` — offline per-header proposer (`propose_ground.py`)

Sibling of `FakeGroundingProposer`. `mapping: dict[str, GroundingProposal]` keyed by the concept's
header text; `propose_grounding(concept, fields)` returns `mapping[concept.text]` or a
`field_iri=None` proposal (→ quarantine) for an unmapped header. This is the honest offline stand-in
for the BAML proposer's per-concept field proposal — needed because a table's headers ("ABO", "LVEF")
don't exact-match property local-names and therefore route to the proposer. Live `BamlGroundingProposer`
is untouched.

### 3.4 Demo fixture `offer_table_pdf(path)` (`tests/etkl/fixtures.py`)

The probe-validated 4-column (`Organ`/`LVEF`/`ABO`/`COD`) × 2-row (`Heart 60 O MVA`, `Lung 55 A CVA`)
offer table, single-token cells, wide column gaps. Pure reportlab (matches the existing fixtures).

## 4. Data flow

```
offer_table_pdf → compile_tables → CompilationReport.graph (tab:RecordTable)
  → feed.table_records(graph) → [Record(row, (SurfaceConcept(header, value, region), ...))]
  → ground_document(..., contract=offer-contract, proposer=MappingGroundingProposer, terms, shapes, g):
       per row: subject = urn:iladub:record:<table>-<row>
       per cell: ground_concept(concept, contract, subject, proposer, terms, shapes, g) → grounded | proposed
  → g: GroundedNode + PromotionDecision (asserted, grounded cells) + CandidateConcept per cell
       (grounded cells' cands are the promoted propositions; ungrounded cells' cands stay quarantined)
```

Per-record oracle coverage (proves all three grounding paths through the table feed):
- **Organ** — header exact-matches `tx:organ` (`is_exact`), scheme-bound → `scheme_member("Heart", scheme-organ)` → grounds.
- **ABO** — header "ABO" not exact → proposer → `f-abo` (scheme-bound) → `scheme_member("O", scheme-abo)` → grounds.
- **LVEF** — header "LVEF" not exact → proposer → `f-ef` (value-constrained `xsd:decimal[0,100]`) → `_value_conforms("60")` → grounds **via the just-shipped value-constraint disposal**.
- **COD** — header "COD" not exact → proposer → `f-cod` (no scheme, no value constraint) → no oracle → **quarantine** (`CandidateConcept`).

## 5. Testing (offline; run `./.venv/bin/python -m pytest`)

New `tests/test_concept_feed.py`:

1. **Bridge — two records, correct cells:** on the compiled `offer_table_pdf` graph, `table_records`
   returns 2 `Record`s; each has 4 `SurfaceConcept`s with the right `(header, value)` — Heart row
   `(Organ,Heart)/(LVEF,60)/(ABO,O)/(COD,MVA)` and the Lung row — grouped by `atRow`.
2. **Bridge — provenance carried (§6):** every `SurfaceConcept.region` is non-empty and distinct per
   source cell.
3. **`MappingGroundingProposer`:** maps `"ABO"→f-abo`, `"LVEF"→f-ef`, `"COD"→f-cod`; an unmapped header
   yields a `field_iri=None` proposal.
4. **End-to-end DoD, RED-checked:** `offer_table_pdf → compile_tables → table_records →
   ground_document(offer-contract, MappingGroundingProposer, terms, shapes, g)` →
   `FeedResult(records=2, grounded=6, proposed=2)`; assert 2 typed `tx:OrganOffer` subjects and 6
   `GroundedNode`s (organ/abo/ef × 2 rows). The 2 COD cells produced **no** `GroundedNode` (their
   `causeOfDeath` value was quarantined) — assert no `GroundedNode` `groundsTo`/binds `tx:causeOfDeath`
   and that neither `OrganOffer` subject carries a `tx:causeOfDeath` value. (Note: every cell emits a
   `CandidateConcept` — grounded ones are the promoted propositions — so the discriminating signal is
   the `GroundedNode` count and the `FeedResult` tallies, NOT the raw `CandidateConcept` count.)
   **RED-check:** stubbing `table_records` to return `[]` yields zero `GroundedNode`s (proves the feed
   is load-bearing, not vacuous).

Full `tests/` suite stays green (the slice is additive — a new module + a new fixture + a new proposer
sibling; `ground_concept` and the etkl compiler are unchanged).

## 6. Anti-overfit

The bridge is **pure RDF reads** — no tuned constant, no IRI-name parsing (headers/values/rows resolved
via `coversColumn`/`hasLabel`/`atColumn`/`atRow`). The driver reuses the shipped `ground_concept`
oracle **unchanged**, so grounding soundness (legality gates admission, confidence never does) is
inherited, not re-implemented. The DoD's **quarantine assertion (COD)** is the load-bearing guard: it
proves the oracle still gates through the table path — feeding concepts does not rubber-stamp them.

## 7. Scope boundary (YAGNI)

- Only **asserted `tab:RecordTable`** regions are fed. Hierarchical / matrix / escalated / ignored
  regions are out of scope (different cell models) — a documented deferral, not a silent gap. **Note:
  transposed regions ARE fed** — `assert_transposed_region` axis-flip-normalizes into a `tab:RecordTable`
  with the same `hasHeaderNode`/`coversColumn`/`hasLabel` + `EntryCell atColumn/atRow` cell model, so the
  bridge reads them correctly and each cell grounds against its (post-flip) header. This path is not
  separately fixtured here (grounding is cell-independent), so it is untested-but-correct, not designed-out.
- Row = record, header = field, value = cell; single-token cells (multi-word / merged cells out of
  scope).
- No grounding-logic changes — `ground_concept` is reused as-is.
- No BAML on the test path; live `BamlGroundingProposer` unchanged.
- Domain-neutral: the demo uses the synthetic transplant offer table + the shipped `offer-contract` /
  `offer-shapes`; no real patient data.

## 8. Definition of done (the loop CLOSES)

- A raw offer-table PDF compiles and grounds end-to-end — two `OrganOffer` records with organ/abo/EF
  grounded and cause-of-death quarantined — through the real `compile_tables` + real `ground_concept`,
  RED-checked non-vacuous.
- The bridge is honestly classified PROCEDURAL raw extraction (RDF reads); no grounding decision is
  re-implemented.
- Residue (unconstrained / unresolvable cells, e.g. COD) is quarantined as `CandidateConcept`
  propositions, never dropped (§7).
- Full suite green.

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
