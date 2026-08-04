---
title: Dimension-split-as-denormalization — section repair, attribution, naming
type: concept
sources:
  - docs/superpowers/specs/2026-08-04-cbh-dimension-split-design.md
  - src/iladub/splitkey.py
  - src/iladub/etkl/sectiongraph.py
  - src/iladub/etkl/document.py
  - examples/shipping/cbh-contract.ttl
  - examples/shipping/cbh-terms.ttl
  - examples/shipping/cbh-shapes.ttl
  - tests/test_cbh_e2e.py
related: ["[[neurosymbolic-exemplars]]", "[[table-holon-compilation]]", "[[assert-propose-promote]]", "[[grounding-membrane]]"]
confidence: high
updated: 2026-08-04
---

# Dimension-split-as-denormalization

**The taxonomy case.** A denormalized spreadsheet author sometimes splits ONE logical
column into repeated SECTIONS of a page rather than adding a column: instead of a
`Port` column with a value on every row, the document prints one heading
(`GERALDTON`), a block of rows that all implicitly belong to it, then the identical
header stack repeats and the next heading (`KWINANA`) starts the next block. The value
that would fill a `Port` cell is never written on the row — it is carried by POSITION,
in the section it falls under. This is spec §2b's taxonomy case 3, in its *intra-page*
form: not a table split across pages by pagination (loop M's problem), but a table
split across REPEATED BLOCKS of the same page by the author's own layout convention.
The real specimen (`corpus/ag-trade/cbh-stem-2026-08-03.pdf`, an Excel-exported daily
shipping stem) presents exactly this shape four times on one page: `GERALDTON`,
`KWINANA`, `ALBANY`, `ESPERANCE`, each a repeated 3-line header stack over its own rows,
with berth-notice furniture lines interleaved.

**Why this is hard, structurally, not just visually.** Excel's borderless export style
draws the header stack WITHOUT a ruled box (`Time Nom`/`Date Nom` wrap ambiguously into
`Time Nominated`/`Date Nominated`; a doubled `Accepted Accepted Completed Completed`
row), and CBH's grid uses a DOUBLED outer border (a twin rule ~0.3pt beside the true
edge) that defeats simple min/max-x interior tests. Two matters are therefore stacked:
(a) can the section's own table be READ at all (an escalation-recovery problem), and
(b) once read, whose rows are they — a KEY that is nowhere written on the rows
themselves, and whose NAME (`port`) is nowhere written in the document at all. Loop P
attempted (a) at BAND scope and was reverted after three witness rounds each broke one
of two real specimens (see `docs/superpowers/residues.md`'s `~~R42~~` row for the full
measured map) — the finding that reopened the design: **the repair needs to know it is
facing a sectioned, repeated-header chain BEFORE deciding how to peel a band**, which a
single band cannot know about itself.

## The section-repair ordering (spec §4.0)

Loop Q re-homes the repair at SECTION scope, and the ORDER in the driver
(`src/iladub/etkl/document.py`) is load-bearing — it is what keeps the fix from
whipsawing loop L's/M's existing readers the way loop P's band-local attempt did:

1. **Band-level compile runs first, unchanged.** A clean-edged section (no doubled
   border) asserts here already — loop P's peel/weld machinery is still wired into
   `_build_ruled_band` and fires wherever the edges are clean; CBH's doubled edges
   defeat it, so CBH's sections escalate `MERGE_AMBIGUOUS` and become repair
   candidates. The GrainCorp stem never presents a sectioned page at all, so it never
   reaches step 3 — measured byte-identical throughout.
2. **Document carriage runs next, unchanged.** Loop M's cross-page recognition + loop
   O's continuation licence still get first claim on any page pair that looks like a
   continuation.
3. **Section repair (new, loop Q).** `vocab/queries/section-repeat.rq` (run by
   `sectiongraph.section_candidates`) recognizes intra-page repetition over ALL ruled
   bands of the page, **regardless of band-level verdict** — the recognition evidence
   is raw author marks (verbatim header-box text + agreeing interior rule-x sets), not
   a successful reading, so it can see a repeated section even where every member is
   still escalated. Within a recognized group, ONLY the still-escalated members are
   re-read as candidates (ink-witness peel + weld, salvaged from loop P's reverted
   wave — safe HERE because the section scope guarantees a sectioned page, which the
   stem never presents to this step); already-asserting members pass through
   untouched. Each candidate is disposed by the SAME region membrane every band-level
   reading uses (tiling shapes + `merge_tiling_ok` + score) — it asserts only if the
   re-reading actually passes.

This makes the repair **monotone by construction**: it can only turn an escalation into
a membrane-passing assertion, never touch an already-asserting band, never worsen
anything. `DocumentReport.repaired_bands` is the honest, append-only record of what was
actually adopted — a candidate whose pass-2 re-read still escalates leaves NO entry
there, only a `notes` line. A stem-shaped synthetic fixture is pinned to traverse the
whole driver with `repaired_bands == ()` — zero repair activity — as the structural
guarantee that this new machinery cannot regress a document it was never meant to touch.

Measured on the real CBH document (`tests/test_cbh_e2e.py`, 2026-08-04): score
**0.0698 → 0.9047**; `repaired_bands = ((0,1),(0,3),(0,5),(0,7))` — all four escalated
sections recognized, repaired, and adopted; the four chain into one 4-member logical
table via the existing `tab:continuesTable` machinery (no second stitching mechanism —
loop M's chain assembly runs unmodified over the section-repair's output exactly as it
runs over cross-page continuations).

## Attribution never waits for naming (spec §4.2)

Once a section's table reads, its rows still carry no `Port` value — only the heading
above them does. Loop Q's key insight (following loop I's "value without a name" idiom)
is that a record can be given a stable, DISTINCT identity from its section's positional
key *before anything decides what that key is called*. `feed._inject_section_captions`
injects every one of a repaired table's peeled captions (`tab:RegionCaption`) as
candidate `SurfaceConcept`s on every one of that table's records — undiscriminated: a
genuine key (`GERALDTON`) and a berth-availability notice
(`BERTH MAY BE UNAVAILABLE 2000HRS...`) arrive on the record identically, both marked
`is_section_marker=True`. Separately, `feed.table_records` prefixes each record's base
row identity with the table's FIRST caption, positionally
(`"GERALDTON > p0 table0-r1"`), so two sections' "row 0" can never collide — this
prefix is the record's REAL identity, computed and used well before any cascade decides
a name.

Discrimination — which of a table's captions is the key and which is stray notice text
— is deliberately NOT decided at this layer; §4.3's cascade decides it later, by scheme
membership (a notice grounds nowhere; `GERALDTON` grounds in the port scheme). This is
implemented today only as the FEED-level positional form; the spec's fuller GRAPH-level
form (`tab:DerivedRowGroup` covering a section's rows, `tab:hasLabel` → the heading
cell, `prov:wasDerivedFrom` → a confirming total row) was never built — open as **R49**
in the residue register, not overclaimed by loop Q's close. Measured end-to-end: 49 of
CBH's 58 records are section-prefixed and distinct across all four ports.

## The three-arm cascade, and the §3 disposal split (spec §4.3)

The denormalized column's NAME is nowhere in the document — `resolve_split_key_name`
(`src/iladub/splitkey.py`) recovers it through a three-arm cascade, gate-shaped (each
arm fires only when the previous abstains), disposed strictly along assert-only-what-
you-can-ground lines (§3):

1. **AXIOM — explicit naming.** If every marker shares one `Key: Value` form
   (`"Port: GERALDTON"`), the key IS the name — real §0 evidence from the source
   itself, no LLM. But evidence recovered is not automatically evidence GROUNDED: if
   the recovered key names no contract field (`"Berth: 12A"` against a contract with no
   `berth` field), it must NOT assert — minting a synthetic `groundsTo` IRI on presence
   alone would fabricate a target the membrane cannot verify (this exact leak shipped
   and was caught and fixed in loop Q's own review — see below). CBH's markers are
   bare (`GERALDTON`, not `Port: GERALDTON`), so this arm correctly abstains on the
   real specimen.
2. **AXIOM — unique admitting contract field.** Ground the marker VALUES (not names)
   against the destination contract's SKOS schemes: a field ADMITS the marker set iff
   its scheme contains a matching label for EVERY marker (whole-set membership —
   strict, decidable, no LLM). The **ambiguity score is the count of admitting
   fields**. Exactly one → the name is derived FROM THE CONTRACT and asserted via an
   `iladub:PromotionDecision` recording the membership evidence. Measured on CBH: the
   four section-key markers (`GERALDTON`/`KWINANA`/`ALBANY`/`ESPERANCE`) whole-set-admit
   exactly the contract's `port` field (`ambiguity_score == 1`) — asserts here, no LLM
   call at all.
3. **NEURAL — BAML scored proposal**, firing only when arm 2's score is 0 or ≥2. This
   is the cleanest illustration in the codebase of §8's rule that a NEURAL step may only
   ever NARROW a set an AXIOM already verified, never invent membership on its own:
   soundness (which fields admit) was decided in arm 2 before the proposer ever speaks.
   With ≥2 admitting fields, the proposer's ranked candidates are matched against the
   VERIFIED admitting set only — the highest-scoring MATCH asserts, and a top-ranked
   candidate that names no verified field is walked past rather than fabricated as a
   pick. With 0 admitting fields (or no candidate matching a verified field with ≥2),
   the top proposal stays a quarantined `iladub:CandidateConcept` — confidence NEVER
   promotes on its own, however high the score (a 0.99-scored zero-admitting guess
   quarantines exactly like a 0.1-scored one).

Non-member markers (the notice strips) quarantine as VALUES regardless of how the name
resolves (§7) — they are injected as candidates by the attribution layer but never
become part of the marker set the cascade resolves the NAME against (that set is the
identity-prefix values only, one per section). Measured on CBH: 8 distinct notice-only
`is_section_marker` texts sit on the very same records as the four port markers, and
are shown disjoint from the set fed to the naming cascade.

**The membrane gap the cascade's own review surfaced.** Fix round 1 reproduced a real
§3 violation: arm 1's original implementation asserted an unverified explicit key
because `iladub:GroundedNodeShape` checks only `groundsTo`'s PRESENCE
(`sh:minCount 1`), never whether the IRI actually resolves to a real term. Fixed at the
call site (arm 1 now quarantines instead); the underlying SHACL gap — nothing stops a
DIFFERENT future caller from reintroducing the same class of bug — stays open as
**R53**. This is the concrete, measured version of the abstract "assert only what you
can ground" rule: a membrane that only checks a property is PRESENT, not that it
RESOLVES, is a membrane that can be fooled by any caller confident enough to skip its
own local check.

## Where this sits in the loop family

`dimension-split` closes `docs/superpowers/residues.md`'s R42 (both gaps, per the
measured citations in that row) and is the concrete worked example for spec §2b's
taxonomy case 3. See [[neurosymbolic-exemplars]] for the loop-Q AXIOM/NEURAL/PROCEDURAL
catalog entries, and [[table-holon-compilation]] for the table-compilation loop family
this repair extends.
