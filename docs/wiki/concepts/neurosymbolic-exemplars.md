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
related: []
confidence: high
updated: 2026-08-01
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
