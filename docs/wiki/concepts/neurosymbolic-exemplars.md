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
  - vocab/queries/matrix-body-start.rq
  - src/iladub/etkl/matrix.py
  - vocab/queries/band-run.rq
related: ["[[dimension-split]]"]
confidence: high
updated: 2026-09-04
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

## The body starts at the stub (2026-09-02) — matrix body start (AXIOM) and the uncarried-ink guard (producer-side, not PROCEDURAL)

apple's `Three Months Ended … Nine Months Ended` double header was measured (this loop's spec,
`docs/superpowers/specs/2026-09-02-the-body-starts-at-the-stub-design.md` §1.1) to be a SPLIT
defect, not a tree defect: `header_body_split`'s type-transition query correctly finds a Numeric-
over-Currency boundary, but places it one line too early for a *matrix* — at the bare `2026 2025
2026 2025` years line, which carries no stub cell, rather than at the first line the author
actually headed in the stub. One AXIOM derivation and one producer-side guard close it, argued
fresh against this subject rather than inheriting either of two adjacent, non-transferable
rulings (R154's word-atomicity AXIOM; [[dimension-split]]'s Loop Q section-repair scope).

- **`vocab/queries/matrix-body-start.rq`** (+ `matrix_body_start` in
  `src/iladub/etkl/matrix.py`) — an AXIOM, open-world derivation: *which line is the first body
  line of a two-axis matrix*, answered by the **presence** of a stub cell, never by absence. The
  query runs over the same typed-cell evidence graph `header_body_split` already builds
  (`celltype.grid_evidence`), takes exactly **two bindings** it does not derive itself — `?split`
  (the type transition `header_body_split` already found) and `?k` (the stub width
  `stub_data_split` already found) — and returns `MIN(?row)` over cells with
  `tab:atGridRow >= ?split` and `tab:atGridColumn < ?k`: the first cell-bearing line at or after
  the type split that carries a cell in a STUB column, stub columns identified BY COLUMN INDEX,
  never by `tab:cellDatatype` (so a numeric stub label such as a bare year is still a stub
  label). The `MIN` is holon-scoped to one band; the query adds no vocabulary (`tab:GridCell`,
  `tab:atGridRow`, `tab:atGridColumn` are terms `header-body-split.rq` and `stub-data-split.rq`
  already read); no numeric literal is tuned — `?split`/`?k` arrive as bound integers, not
  authored constants. `header-body-split.rq` itself is deliberately **untouched**: the type
  transition stays the global header/body rule, and "stub" is a two-axis notion that only exists
  once a matrix's own stub|data split has already been derived, so this rule is matrix-scoped,
  living beside `matrix_body_start` in `matrix.py` rather than in `headers.py`. Measured on apple
  p1 band 2: type split 1, derived body start 2 — the years line becomes a header LEVEL, disposed
  by the existing column-tree and `region_tiles` machinery exactly as any other header level is,
  never asserted as a header by this rule itself. Both `classify_matrix` and `is_matrix_candidate`
  now count header levels at this DERIVED start rather than at the raw type split (controller
  ruling, spec §3.1, task 3b) — the plan that preceded that ruling had measured
  `is_matrix_candidate` as having "nothing to consume" from the new result and left it untouched;
  Task 5 then measured apple p1's TYPE split alone at 1, below EITHER gate's `>= 2` threshold, so
  the plan's own premise was a defect the controller corrected in the shipped code, not a design
  this exemplar should be read as endorsing.
- **The uncarried-ink guard** (`infer_column_tree_by_proximity`, same file) — **a closed-world
  completeness check, kept PRODUCER-SIDE under CLAUDE.md § "Producer-side guards vs the
  membrane," and explicitly NOT a third PROCEDURAL exemplar for this gate.** The constraint —
  *every header word whose centre lies over a DATA column is carried by exactly one column-tree
  node* — is closed-world over one holon (the band), which is SHACL's world in principle. But the
  membrane cannot enforce it in practice: a header word that wins no column is never emitted as a
  node at all, so the dropped ink never enters the graph for any shape to see or refuse — there is
  nothing there to validate. The guard reads only the band's own words and the nodes already
  built from them (no constant, no tolerance); it refuses (`classify_matrix` → `None`,
  `MATRIX_AMBIGUOUS`) when a data-column word's text is not among that level's node texts, and is
  explicitly exempted for a word centred in the STUB column (WHO's `Year: Month`, spec §1.5's O4
  leg), because the constraint is scoped to `data_cols` only. This is why it is not classed
  PROCEDURAL: it answers no "which columns/rows does X span" reading judgement and computes no
  arithmetic — it is a presence/membership check the membrane happens to be structurally unable to
  host, which CLAUDE.md's producer-side-guards ruling (R89/R102) treats as sufficient grounds to
  keep a guard at the producer rather than deleting it as a supposed membrane duplicate.
  Grouping unruled multi-word header spans into one label — the move that would let apple p2 band
  2 assert instead of refuse — is left undone: it is a *"which words form one label"* judgement,
  NEURAL by §8's own wording, and R155 already measured that class's geometric half
  impossible without a tuned constant. Raised as R162.

## The run is one band (2026-09-04) — the run derivation (AXIOM) and why the merge is a proposal

**Confidence: high** — measured on the shipped tree, not on the prototype every earlier
figure for this loop came from. Sources: `vocab/queries/band-run.rq`,
`sectiongraph.run_evidence` / `merge_run_candidates`, `compile.merged_run_admissible`,
`compile.merge_bands`, `tests/etkl/test_band_runs.py`,
`tests/etkl/test_run_merge_seam.py`, spec
`docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md`.

- **The adjacent-subsumption run derivation** (`vocab/queries/band-run.rq`, consumed by
  `sectiongraph.merge_run_candidates`) — **AXIOM / derivation / open world.** *Which
  contiguous ruled bands are CANDIDATES for one table?* Two adjacent bands extend the same
  run when one's set of distinct rounded rule x-positions is a subset of the other's, in
  either direction; runs are the maximal contiguous chains under that relation. It is a
  `SELECT` over a transient per-page evidence graph that `run_evidence` builds — one fresh
  `Graph` per call, the page as the closure boundary, exactly the `section-repeat.rq` /
  `classify-kind.rq` / `grid-region.rq` idiom — and it is evidence-positive: a band that
  carries no rules emits **no node at all** (`run_evidence`'s honest abstain) and so can
  never join. The two subsumption legs are holon-scoped `FILTER NOT EXISTS`, closing
  *within* the one page graph while the graph stays open, and adjacency is a **join on an
  emitted `tab:prevBandIndex` fact** rather than `?b = ?a + 1`, so the query keeps
  `section-repeat.rq`'s standing property that it contains **no numeric literal**.

- **Why this is not a NEURAL violation, and it is the whole argument.** §8 sends *"which
  columns/rows does X span / read / group"* to NEURAL. *"Are these bands one table?"* sounds
  like exactly that question — and it would be, if this derivation ANSWERED it. It does not.
  **D1 enumerates candidates and settles nothing; D2 disposes.** The judgement that decides
  whether a merged reading is admissible is `compile.merged_run_admissible`, which offers
  the merged band to the **existing, unchanged** closed-world chain
  `is_matrix_candidate → classify_matrix → assert_matrix_region → region_tiles` on a
  **scratch graph that is discarded on refusal** — the tiling membrane, reused rather than
  copied. So the shape is the §3 epistemics applied to geometry: the derivation PROPOSES,
  the oracle DISPOSES, and a refusal leaves the page's graph identical (pinned by
  `test_a_refused_run_leaves_the_page_byte_identical`, up to blank-node labelling — the
  page carries 3516 unlabelled bbox nodes, so `rdflib.compare.isomorphic` is the honest form
  of that claim and N-Triples line equality is not expressible).

- **Measured.** 14 candidate runs across all 27 corpus pages; the membrane accepts exactly
  **two**, apple p0 `2..7` and apple p1 `2..7`, and refuses 12. apple's document score moves
  0.1895 → 0.6289, **identical** under `validate_shapes=True`. The SPARQL form was
  cross-checked against `scripts/band_run_census.py`'s plain-Python relation on all 27
  pages: 0 mismatches. **No tuned constant anywhere**: the only number in the whole design is
  the 2dp rounding INHERITED from `sectiongraph._rule_xs_signature`, which this loop
  neither re-tuned nor justified — and which was measured to change the run set on **0 of
  27 pages**.

- **The exposure this exemplar must not hide.** The refusal is doing real work, and nothing
  specified it to. Forcing `merged_run_admissible` to accept unconditionally costs
  graincorp-capacity p0 390 asserted cells, bfs p6 216, apple p2 3 — so `is_matrix_candidate`
  is the sole guard on ink it was never designed to guard. That is **R170**, and it is made
  falsifiable (a corpus-wide per-page ink oracle) rather than guarded, because a guard tuned
  to today's evidence would be the §8 defect this entry is otherwise an example of avoiding.
