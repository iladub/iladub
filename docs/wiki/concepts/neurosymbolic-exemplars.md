---
title: Neurosymbolic exemplars — the loop-by-loop catalog
type: concept
sources:
  - tests/etkl/test_transform_gate.py
  - vocab/queries/classify-kind.rq
  - vocab/queries/header-body-split.rq
  - vocab/queries/stub-data-split.rq
  - vocab/queries/looks-transposed.rq
  - vocab/queries/transpose-coherent.rq
  - vocab/queries/grid-region.rq
  - vocab/queries/line-enclosed.rq
  - src/iladub/etkl/gridregion.py
  - src/iladub/etkl/geometry.py
related: []
confidence: high
updated: 2026-08-04
promoted_to: docs/neurosymbolic-first.md
---

# Neurosymbolic gate — exemplars already shipped

The AXIOM/NEURAL/PROCEDURAL gate itself is defined in `CLAUDE.md` § Core design
principles, principle 8. This file is the growing catalog of shipped exemplars —
what compliant code looks like, loop by loop.

Exemplars already shipped: the **declarative transform substrate** —
the reshape recipe executed as fixed SPARQL `CONSTRUCT`s (`vocab/queries/*.rq`, run by
`iladub.etkl.interpret.run`) reading their params from the RDF recipe, with the flat base a
derived `hproj:Projection` and a forward-`CONSTRUCT` round-trip oracle; the *flagship AXIOM*
case, gate-enforced by `tests/etkl/test_transform_gate.py` (neurosymbolic loop one, shipped
2026-07-15) — plus **role recovery** (`recover_dimensions`: the UNPIVOT dim-name + operand-role
rules as a two-pass SPARQL `CONSTRUCT` derivation over the `tab:` header graph — the first
*derivation axiom* under the open/closed split, loop B, shipped 2026-07-15),
`reshape.certify_with_proposals` (A2.1, NEURAL propose → oracle → promote), and
**region tiling** (`iladub.etkl.tiling.region_tiles`: the tiling backstops as a SHACL oracle
over each candidate region's RDF — the closed-world *constraint* mirror of loop B's open-world
derivation, loop C, shipped 2026-07-16), the **typed-cell evidence graph** (`iladub.etkl.celltype`
+ `vocab/queries/{header-body-split,stub-data-split,looks-transposed,transpose-coherent}.rq`:
header/body split, stub/data split, and transpose orientation as SPARQL derivations over a
transient pre-holon typed-cell graph — the first evidence graph in the pipeline, loop B2a, shipped
2026-07-17; extended in B2b (2026-07-18) with an open `tab:cellDatatype` lattice — Date/Currency
body-signals + "homogeneous non-Text" queries — for date/currency recall), the **declarative kind
classification** (`iladub.etkl.regions.classify` + `iladub.etkl.classifygraph` +
`vocab/queries/classify-kind.rq`: the whole NON_TABLE/UNSUPPORTED/RECORD kind decision as ONE
holon-scoped SPARQL `SELECT` over a fresh per-band evidence graph — the band *is* the closure
boundary; a byte-identical *faithful lift* gated by a frozen `_ref_classify` differential oracle,
with `infer_leaf_grid`/`_word_in_column` staying justified PROCEDURAL geometry, loop B2c, shipped
2026-07-18), and `segment.find_table_gutter` (propose → oracle → dispose).

## Loop P (2026-08-04) — grid-region scoping (AXIOM) and hrule-box welding (justified PROCEDURAL)

Two more exemplars shipped, both green on their synthetic fixture (490/490 in
`tests/etkl/`), plus a negative lesson the gate itself does not catch.

- **`vocab/queries/grid-region.rq`** (+ `vocab/queries/line-enclosed.rq`) — an AXIOM:
  which visual lines of a ruled band sit INSIDE the author's interior-ruled grid, as an
  open-world SPARQL `SELECT` over a transient per-band evidence graph of line y-centers
  and rule spans (`src/iladub/etkl/gridregion.py` is the PROCEDURAL emitter only — no
  decision logic, every literal a fact, zero numeric literals in the query itself, per
  the §8 gate). Lines outside the grid peel and carry forward as `tab:RegionCaption`
  (loop C's carry class), never dropped.
- **`weld_hrule_boxes`** (`src/iladub/etkl/geometry.py`) — justified PROCEDURAL raw
  extraction: merges re-extracted visual rows that share one author-drawn full-width
  hrule box (a wrapped header name split across two printed lines) into one row, per
  rule-column text joined top-to-bottom. Merge-only, licensed purely by containment
  inside a drawn box — no distance, no tuned tolerance beyond the shipped `COORD_EPS`.

**The negative lesson (measured, not merely argued):** a gate-clean licence — evidence-
positive, presence-tested, zero tuned constants, exactly the shape §8 asks for — can
still be the WRONG LAW if it is disposed at the wrong SCOPE. Three witness licences were
tried at the `_build_ruled_band` seam against the two real specimens (`corpus/ag-trade/
cbh-stem-2026-08-03.pdf`, `corpus/ag-trade/graincorp-stem-2026-07-31.pdf`): an
ink-witness, a rule-straddle witness, and an opening-box witness. Each one individually
passed the §8 gate and fixed the specimen it targeted, and each one broke the other
specimen — this re-measures loop L's lesson (R30/R31: a band-scoped law is blind to
context a wider scope would see) at band scope for a peel/weld decision instead of a
header-row law. All three were reverted (`1271156`) rather than shipped broken. The full
measured map — every score, mechanism, and chain/grounded count per round — is recorded
in the R42 row of `docs/superpowers/residues.md` (canonical; not duplicated here); the
architectural finding is that the repair belongs at SECTION scope (loop Q), where
recognition already knows it faces a sectioned, repeated-header chain before any peel
decision is made — not at one band deciding blind.
