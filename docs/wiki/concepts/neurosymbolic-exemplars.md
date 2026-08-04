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
  - vocab/queries/section-repeat.rq
  - src/iladub/etkl/gridregion.py
  - src/iladub/etkl/geometry.py
  - src/iladub/etkl/sectiongraph.py
  - src/iladub/etkl/document.py
  - src/iladub/splitkey.py
  - tests/test_cbh_e2e.py
related: ["[[dimension-split]]"]
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
  Final review (F1, 2026-08-04): the licence is scoped to the grid's LEADING
  (header-)box only, per spec §3 — every later full-width box passes through unwelded.

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
measured map — every score, mechanism, and chain/grounded count per round — WAS recorded
in the R42 row of `docs/superpowers/residues.md`, but the loop Q close (`b89cf1b`) moved
it OUT of the row to keep the closed row legible; it now lives only at that row's
PRE-CLOSE revision (`git log --follow docs/superpowers/residues.md`, commit `b89cf1b`'s
parent, `a83db3f`) and in the loop-P plan's status note — not duplicated here either. The
architectural finding is that the repair belongs at SECTION scope (loop Q), where
recognition already knows it faces a sectioned, repeated-header chain before any peel
decision is made — not at one band deciding blind.

## Loop Q (2026-08-04) — section-scope repair, monotone adoption, and a NEURAL that only narrows

Loop P's negative lesson (above) resolved: the repair moved from band scope to SECTION
scope, closing R42's both gaps, measured end-to-end on the real CBH document
(`tests/test_cbh_e2e.py`; concept page: [[dimension-split]]).

- **`vocab/queries/section-repeat.rq`** (+ `src/iladub/etkl/sectiongraph.py`'s emitter) —
  an AXIOM, the fix for loop P's whipsaw: intra-page section RECOGNITION, over a fresh
  per-page evidence graph (the page is the closure boundary), derives which ruled bands
  are the SAME repeated author-drawn section — verbatim-identical `tab:headerBoxText`
  (the leading full-width hrule box's line texts) AND `tab:ruleXsSignature` (the band's
  distinct rounded interior rule x-positions). Zero numeric literals in the query; every
  compared value is a FACT the emitter reads off raw geometry/text. Recognition is
  **verdict-independent** — it runs over ALL ruled bands, escalated and already-asserting
  alike, so the decision "is this a repeated section?" never depends on whether a
  reading happened to succeed. Measured on CBH: recognizes bands `(1, 3, 5, 7)` as one
  group; band 9 (a differently-shaped table, not a repeated section) correctly abstains.
- **The monotone repair** (`src/iladub/etkl/document.py`'s driver step 3) — justified
  PROCEDURAL glue over AXIOM decisions: a recognized group's still-escalated members are
  re-read as pass-2 candidates (ink-witness peel + weld, salvaged from loop P's reverted
  wave, now licensed only WITHIN a recognized section group rather than at any lone
  band) and disposed by the EXISTING region membrane — a candidate is adopted **iff its
  re-reading asserts**; a still-escalating candidate leaves its pass-1 report
  byte-untouched. This is monotone **by construction**, not by convention: the driver
  can only turn an escalation into a membrane-passing assertion, never touch an already-
  asserting band, never worsen anything — pinned by a stem-shaped fixture that must
  traverse the whole driver with zero repair activity (`repaired_bands == ()`). Measured
  on CBH: `repaired_bands = ((0,1),(0,3),(0,5),(0,7))`, score 0.0698 → 0.9047, all four
  chained into one 4-member logical table via the existing `tab:continuesTable`
  machinery — no second stitching mechanism.
- **The naming cascade's pick-among-verified discipline** (`src/iladub/splitkey.py`,
  `resolve_split_key_name`) — the clearest shipped illustration yet of §8's rule that a
  NEURAL step may only ever **narrow** a set an AXIOM already verified, never invent
  membership. Arm 2 (AXIOM: whole-set SKOS scheme membership) computes the "ambiguity
  score" — the count of contract fields whose scheme admits every recovered marker —
  BEFORE any LLM call. Arm 3 (NEURAL, `ProposeSplitKeyName`, BAML) fires only when that
  score is 0 or ≥2, and even then the proposer's ranked candidates are matched against
  the VERIFIED admitting fields only; the highest-scoring MATCH asserts, and a top
  candidate naming no verified field is walked past rather than fabricated as a pick
  (`test_two_admitting_ignores_a_proposal_that_names_no_verified_field`). Confidence
  never promotes on its own: a 0.99-scored zero-admitting guess quarantines exactly like
  a 0.1-scored one (`test_confidence_never_promotes`). Measured on CBH: the four
  recovered port markers whole-set-admit exactly ONE contract field
  (`ambiguity_score == 1`) — arm 2 asserts `port` directly, and arm 3's proposer is
  never even called (a raising proposer proves the short-circuit in both the unit
  battery and the real-document E2E test).
- **A fix-round lesson for the gate itself:** loop Q's own review (F1) reproduced a §3
  violation that had shipped inside a gate-clean-LOOKING arm — `resolve_split_key_name`'s
  arm 1 (explicit `Key: Value` naming) minted a synthetic `groundsTo` IRI and asserted
  whenever the recovered key matched NO contract field, because the SHACL membrane
  (`GroundedNodeShape`) checks only `groundsTo`'s presence, never its resolution. Fixed
  at the caller (arm 1 now quarantines an unverified explicit name); the membrane-level
  gap itself is open as R53 in `docs/superpowers/residues.md` — a reminder that the §8
  gate classifies DECISIONS, not the membrane that is supposed to catch a decision gone
  wrong, and the two need independent verification.
