---
title: Table-holon compilation — the loop family
type: concept
sources:
  - docs/loops/2026-07-05-table-holon-loop.md
  - vocab/ontology/tab.ttl
  - vocab/shapes/tab-shapes.ttl
  - tests/test_corpus_stem.py
  - vocab/queries/continuation-of.rq
  - src/iladub/etkl/document.py
  - src/iladub/etkl/rows.py
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
tables that are not truly one; and R35 — subtotal confirmation is closed within one page, so
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
edges), missing-`GC Fin Year` keys go from 92 to 0, records drop from 154 to 133 (the 21
subtotal rows stop minting records), grounded concepts rise from 546 to 585, and record
identity collapses from three page-determined kinds to one uniform kind (a group path, at most
one disambiguation suffix) — with a single, correctly-refused exception, the document's own
`Grand Total` row (R4-family's zero-member walk-back honest refusal, R40). Two same-level
groups can now cover one row (R18's co-resident case, more frequent once the holon is
document-wide), so `feed._header_path`'s tie-break was made a deterministic total order
(lexicographic `(label, node)`) — not a semantic claim, just reproducibility across runs,
stores, and library versions. What remains open, named by ID rather than left implicit: R33's
false-stitch exposure now reaches this same machinery (a wrong continuation can destroy
page-confirmed facts, not just fail to gain them, and can fabricate or silently drop record
keys — measured only as a mechanism, not on a real false stitch); R37 (the wider-window
retraction reading is a modelling choice no oracle disposes); R38 (a headerLevel staleness
mode, closed for chains today but not proven unreachable in general); and R39
(`row-group-nesting.rq`, loop I's unchanged AXIOM, now the dominant compile cost at ~93–97 s
over the logical table's larger group count, queued for the derivation-scaling playbook).

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
