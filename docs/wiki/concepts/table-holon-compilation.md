---
title: Table-holon compilation — the loop family
type: concept
sources:
  - docs/loops/2026-07-05-table-holon-loop.md
  - vocab/ontology/tab.ttl
  - vocab/shapes/tab-shapes.ttl
  - tests/test_corpus_stem.py
related: ["[[assert-propose-promote]]", "[[grounding-membrane]]"]
confidence: high
updated: 2026-08-02
---

# Table-holon compilation — the loop family

`docs/loops/2026-07-05-table-holon-loop.md` frames table compilation as a
**loop-engineering** problem, not a parsing one: "a table is not an array,"
and off-the-shelf parsers fail exactly where merged cells and hierarchical
headers appear. The loop's canvas fixes a **verifier-first** goal before any
code: a `tab:Table` is done only when it (a) **round-trips** — re-rendered
structure diffed against the *measured* geometry, no semantic ground truth
needed — and (b) conforms to the tabular-topology **SHACL** membrane. Validated
cells become assertions; anything the geometry can't decide becomes a
proposition and an escalation. The design goal stated directly: **"score =
validated% + escalated%; silent-wrong is impossible."**

**How it works.** The loop doc's own increment log is the arc: increment 1
closes a flat record table end-to-end; increment 2 adds hierarchical/wrapped
column headers; **increment 3 — detect transposed tables — is explicitly
named "iladub's first semantic oracle"** (`looks_transposed`: a numeric row
but no numeric column), escalating rather than silently inverting a table
that round-trips and validates yet reads backwards; increment 4 closes the
detect→compile arc with axis-flip compilation, certified by a second oracle
(`transpose_is_coherent`) against the reverse silent-wrong. Increments 5–7
generalize the same header-tree machinery to row hierarchies, matrix/
cross-tab tables (the union of column and row SHACL, no new vocabulary), and
multi-table page segmentation. `vocab/ontology/tab.ttl` and
`vocab/shapes/tab-shapes.ttl` show the family continuing past this dated
loop record under lettered increments their own comments name in place —
loop C's committed row-role/caption evidence (`tab:RegionCaption`,
`tab:HeaderContentConservedShape`, GrainCorp push), loop G's header-boundary
confirmation evidence, loop H's arithmetic-verified `tab:DetectedAggregationRow`,
and loop I's `tab:DerivedRowGroup` row hierarchies inferred from confirmed
aggregations. [[assert-propose-promote]] documents where this arc lands: the
loop-K GrainCorp grounding capstone that measures the compiled table-holons'
concepts against a contract (137 grounded / 323 quarantined) — a later loop
this page's own three sources do not independently cover, so it is cited
there rather than asserted here.

**Loop L (2026-08-02) — the accommodation thesis, applied to a live document.**
Where prior loops fixed the compiler against synthetic and single-page fixtures,
loop L's premise is that a *fluent human reader* never hesitates on a well-formed
page, so a page a human reads without hesitation must compile, not escalate —
divergence is the compiler's problem, not the document's. Applied to the real
GrainCorp shipping stem, that surfaced a new law: under ruled evidence, the
header stack is read off the author's own rule marks (leaf = the deepest 1:1
rule-aligned line; furniture above the rule; continuation between rule and leaf),
engaging only on a narrow clause-0 precondition — exactly one header-block rule
with rows above *and* below it — that two adversarial review rounds tightened
from an initial looser trigger. On the live stem's page 0 this compiles 586
cells at score 0.9560 (`tests/test_corpus_stem.py::test_stem_page0_compiles`),
and grounds against the stem contract at 167 grounded / 385 still-quarantined
of a 552 candidate pool, with non-grain cargo (Woodchip, Cement) correctly
refused (`test_stem_page0_grounds_against_contract`). Pages 1-2 still escalate
`REGION_TILING_FAILED` — a repeated-header (Excel print-titles) continuation
whose block-rule evidence is page-0-only — routed to Loop M as a pagination
problem, not a header-role one (residues R29-R32).

Every SHACL shape in `tab-shapes.ttl` enforces the round-trip/tiling
contract literally: `CoverageShape` and `UnambiguousAccessShape` require
every leaf column to resolve to exactly one leaf header path;
`RefinementShape` requires a child header's covered columns to be a subset
of its parent's; the row-axis shapes mirror this but are *guarded* to fire
only on tables that declare a row axis, so flat tables still pass.
`HeaderContentConservedShape` is the loop C oracle for content loss: every
header-region source cell must appear in an asserted label or a carried
`tab:RegionCaption` — an all-furniture reading is legal by design (nothing
lost), but a word in neither is refused.

**Settled vs open.** The verifier-first paradigm, the round-trip oracle, and
the tiling/coverage SHACL are shipped and enforced across the sources here.
Where residues cluster: **R3** — `recover_leaf_grid`'s nested-subset vote can
be outvoted by shorter suffixes that are nested subsets of the correct grid,
not independent witnesses; open, and only latent today because ruled
documents route around it. **R4** — closed for the *ruled hierarchical*
path (loop H, 2026-07-30: hrule-veto de-fusion + exact-arithmetic subtotal
confirmation, measured on GrainCorp at 17 correctly-nested
`DetectedAggregationRow`s, zero regression) but its register row still
carries several narrower open forms: blank-total subtotals that are
arithmetically unverifiable and correctly left unconfirmed; unruled
suppressed-key documents, where the fusion defect persists because the
hrule veto has nothing to veto; the row-hierarchy and record compile paths,
both still unwired to the detector; and an acknowledged false-positive
direction (a coincidentally-summing reference number) inherent to
arithmetic-only detection.
