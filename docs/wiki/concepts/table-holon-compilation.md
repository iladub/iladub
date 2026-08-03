---
title: Table-holon compilation — the loop family
type: concept
sources:
  - docs/loops/2026-07-05-table-holon-loop.md
  - vocab/ontology/tab.ttl
  - vocab/shapes/tab-shapes.ttl
  - tests/test_corpus_stem.py
  - vocab/queries/continuation-of.rq
  - vocab/queries/continuation-licence.rq
  - src/iladub/etkl/document.py
  - src/iladub/etkl/rows.py
  - tests/etkl/test_continuation_licence.py
related: ["[[assert-propose-promote]]", "[[grounding-membrane]]"]
confidence: high
updated: 2026-08-03
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

Pages 1-2 still escalate `REGION_TILING_FAILED` — a repeated-header (Excel print-titles) continuation
whose block-rule evidence is page-0-only — routed to Loop M as a pagination
problem, not a header-role one (residues R29-R32). The `render:` namespace and Producer-gated generator modules the campaign spec sketches (§2b) remain deliberately unbuilt — the universal rule-evidence law sufficed on this specimen, the transient reading evidence lives in `tab:` as pre-holon table facts, and a generator module is only earned by a corpus document the universal law cannot read.

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

**Loop M (2026-08-03) — pagination as a second accommodation operator, whole-document.**
Where loop L closed the fluent-reader invariant within one page, loop M applies the same
accommodation thesis across the page break itself: a human reader does not re-derive a
table's meaning at every page cut, so the compiler must not either. `continuation-of.rq`
(`vocab/queries/continuation-of.rq`) recognizes a continuation purely by REPEATED
author-drawn evidence — an identical header block and column grid across a page boundary —
never by reading label text, keeping the recognition inside the AXIOM/open-world discipline.
Once recognized, the confirmed header reading and its row roles are CARRIED onto the
continuation page (`tab:RepeatedHeader` facts, never data), and `document.compile_document`
(`src/iladub/etkl/document.py`) walks a chain of pages as one logical table for both
compilation and grounding. On the live 3-page GrainCorp stem this compiles ONE chain at
0.9655 over 2152 cells and grounds the full document at 154 records — 567 concepts promoted
(each behind exactly one `iladub:PromotionDecision`) / 1194 still quarantined. The thesis
has two measured open edges, both registered rather than hidden: R33 — the same
repeated-header evidence cannot distinguish a genuine page-cut (taxonomy case 2) from two
independent tables sharing a template (case 3), so the AXIOM can license a stitch between
tables that are not truly one (closed for MARKED documents by loop O's continuation licence,
below); and R35 — subtotal confirmation is closed within one page, so
a row group cut by the page break never confirms on the continuation page, leaving that
page's records without their injected keys and its subtotal rows unmarked in the feed.

**Loop N (2026-08-03) — the closure-holon principle: the arithmetic is unchanged, its holon
was lifted.** R35 measured that loop H's subtotal arithmetic (`rows.detect_aggregation_rows`,
untouched — not one line edited) is only ever run over one page's rows, so a group cut by a
page break confirms nothing on the continuation page. Loop N does not touch the arithmetic; it
runs the same decidable-exact-Decimal confirmation over a bigger holon — the logical table's
row sequence across every page a continuation chain licensed — then re-derives loop I's row
groups and injects group keys from the document-level result. On the live stem this closes R35
measurably: page 2's confirmed subtotals go from 0 to 21 (57 cross-page `tab:aggregates`
edges); missing-`GC Fin Year` keys go from 112 (pre-loop: 50 p1 + 62 p2) to 0; records drop from 154 to 133 (21 p2 subtotal rows stopped minting records); grounded concepts go from 567 (pre-loop) to 546 (once those records left the denominator) to 585 (chain-wide keys); quarantined concepts go from 1194 to 1265; and record identity collapses from three page-determined kinds to one uniform kind (a group path, at most one disambiguation suffix) — with a single, correctly-refused exception, the document's own
`Grand Total` row (R4-family's zero-member walk-back honest refusal, R40). Two same-level
groups can now cover one row (R18's co-resident case, more frequent once the holon is
document-wide), so `feed._header_path`'s tie-break was made a deterministic total order
(lexicographic `(label, node)`) — not a semantic claim, just reproducibility across runs,
stores, and library versions. What remains open, named by ID rather than left implicit: R33's
false-stitch exposure now reaches this same machinery (a wrong continuation can destroy
page-confirmed facts, not just fail to gain them, and can fabricate or silently drop record
keys — measured at this point only as a mechanism; loop O, below, measured it on real
false-stitch compiles and then gated it); R37 (the wider-window
retraction reading is a modelling choice no oracle disposes); R38 (a headerLevel staleness
mode, closed for chains today but not proven unreachable in general); and R39
(`row-group-nesting.rq`, loop I's unchanged AXIOM, now the dominant compile cost at ~93–97 s
over the logical table's larger group count, queued for the derivation-scaling playbook).

**Loop O (2026-08-03) — recognition is not permission: the continuation LICENCE.** Loops M and N
built the whole document-level machinery on ONE question ("does page N redraw page N−1's header
block on the same grid?"), and R33 measured that this question cannot separate a paginated table
(taxonomy case 2) from two independent tables printed from one template (case 3). Loop O splits
the question in two: recognition still answers *did the renderer repeat the header*, and a
**second AXIOM** — `vocab/queries/continuation-licence.rq`, open-world, with **no numeric
literal**: no digit is ever read as data, the ordinal cancellation happening entirely at
emission — answers *may that pair actually be stitched*, by asking whether the
non-table blocks the renderer drew AROUND the table are page-invariant furniture or new content.
The law (V4): page N's ABOVE-table blocks must be text-identical to blocks page N−1 also drew
(strict); blocks BELOW either page's table must answer each other modulo whole tokens equal to
that block's own printed page ordinal (cancelled at emission, so the query never learns what a
numeral is); blocks above page N−1's table are unconstrained, because a document's opening
furniture is legitimately drawn once — the asymmetry of the cut, and a symmetric law was measured
to refuse the stem's genuine stitch. `compile_document` gates carriage, `tab:continuesTable`, the
chain, the document-level arithmetic window and the document-level row groups behind that licence,
and a refusal is **recorded, not discarded** (`DocumentReport.refused_licences`, the graph fact
`tab:licenceRefused`, and `tab:LicenceRefusalShape` making the two verdicts exclusive over one
pair). What the loop measured, in the order it matters: **first the damage, on real compiles** —
a purpose-built two-page case-3 fixture with a page-local subtotal showed the false stitch
FABRICATING (a document-level row group keyed `Alpha` silently absorbing the other page's
unrelated row) and LOSING (the page's own legitimately-earned group superseded, then not
re-derived because the two pages' key values conflict); **then the fix** — the marked pair now
refuses, its page-local subtotal confirmation survives untouched, and the two pages compile as two
independent documents; **and the wall** — the genuine 3-page stem licenses both pairs and is
byte-identical on every tally (0.9655 over 2152 cells, one chain of 3, 133 records / 585 grounded
/ 1265 quarantined, ledger 41/62/0/21). R33 therefore closes **for marked documents only**, and
the boundary is stated rather than hidden: two markless byte-identical template pages still
stitch, which is invariant-*consistent* — no page-invariance evidence distinguishes them, and a
fluent reader reads them as one table — plus one narrow permissive class of the tail clause (two
tails differing only by a standalone token that happens to equal each page's own ordinal, e.g.
`TOTAL 1`/`TOTAL 2`; measured to bite only at that coincidence — the same tails at ordinals 5/6
refuse). R37 narrows in consequence: the wider-window retraction reading is now only ever
exercised inside a licensed continuation.

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
