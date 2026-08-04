# CBH dimension-split-as-denormalization — loops P and Q — design

**Date:** 2026-08-04 · **Status:** loop Q closed 2026-08-04 (Task 7, §4.6) — CBH measured
end-to-end at score 0.9047; loop P's band-scoped fix-wave reverted (its shipped machinery
is what loop Q builds on) — see the R42 register row ·
**Discharges:** R42 (both gaps) · **Specimen:** `corpus/ag-trade/cbh-stem-2026-08-03.pdf`
(sha256-pinned in `tests/corpus-manifest.ttl`; battery id `cbh-stem-2026-08-03`)

**Doc impact:** none — design only; loops P and Q each carry their own `Doc impact:` at
their close (expected: increment — a dimension-split wiki entry once the machinery ships).

## 1. Problem (measured, not assumed)

The corpus battery (2026-08-04, PR #85) measured the CBH Daily Ship Roster at **0.0698**,
with **4 of 5 page-0 table regions escalating `MERGE_AMBIGUOUS` at 0 cells** and one
66-cell region asserting. Per-page probe (`compile_tables`, page 0): every port section is
already its own band (`detect_bands` splits at the inter-section gaps); each escalates on
its own header stack. The page has **`lines: 0`** — no vector rules at all (producer
`Microsoft® Excel® for Microsoft 365`) — so loop L's rule-anchored header-stack law never
engages; the failure sits in the borderless merged-header path (B1.x / loop C territory).

The page-0 render (measured):

```
GERALDTON                                 ← bare key heading
BERTH MAY BE UNAVAILABLE … (×4)           ← notice furniture
Time Nom | Date Nom | Date Loading | Time Loading      ← stack line 1
VNA # | Vessel Name | Time Nominated | … | Volume | …  ← stack line 2 (the wide row)
Accepted | Accepted | Completed | Completed            ← stack line 3
10 vessel rows                            ← values WITHOUT the port key
374,904                                   ← per-section total (arithmetic-confirmable)
KWINANA … [identical 3-line stack repeated] … 737,289
ALBANY …
```

## 2. The adjudicated reading (François, 2026-08-04 — folded into R42)

One **master table, dimension-split-as-denormalization** — the campaign spec's pagination
taxonomy **case 3** (2026-08-02 design §2b), here in **intra-page** form. The split
dimension's *value* was lifted out of the rows into a bare section heading; the dimension's
*name* appears **nowhere in the document**. Two stacked gaps, (b) blocked on (a):

- **(a)** the borderless Excel 3-line header stack does not read (`MERGE_AMBIGUOUS`);
- **(b)** once sections read, the rows are values-without-key: the key value must be
  attributed to its rows, and the denormalized column name recovered.

Decision (brainstorm): **two loops, (a) then (b)** — each closes vertically on the real
document. This spec fully designs (b) = **loop Q** (the mechanism needed design agreement)
and scopes (a) = **loop P** (diagnosis-first; its mechanism is chosen by measurement).

## 3. Loop P — the borderless header stack (entry loop; diagnosis-first)

**Invariant (the campaign's §2, unchanged):** a document a fluent human reads without
hesitation must compile or escalate *semantically*. The CBH stack is fluent-readable; four
`MERGE_AMBIGUOUS` escalations at 0 cells are a reading defect, not an honest escalation.

**What is pinned now (measured):** the stack is three lines; the wide row (line 2) carries
the leaf names; lines 1 and 3 are vertically split fragments of long column names
(`Time Nom` … `Accepted` reading as "Time Nom Accepted", `Date Loading` … `Completed` as
"Date Loading Completed"); the page is ruleless, so alignment evidence must come from the
words themselves. One region (66 cells) already asserts — the loop must not regress it.

**What is deliberately NOT pinned:** the mechanism. Loop P opens with systematic debugging
of ONE section's stack (which decision point raises `MERGE_AMBIGUOUS`, what evidence each
candidate reading has). Candidate homes, in gate order: (1) extend loop C's row-role NEURAL
(`rowrole.py` — `furniture | continuation | level` per row; the 3-line stack may be exactly
a `continuation`-sandwich) with its two shipped oracles (tiling + content conservation);
(2) a borderless clause for the header-stack law ONLY if a rule-free, constant-free
engagement condition exists (loop L's lesson: demand positive evidence per role; a law can
be gate-clean and wrong). **A Python geometry heuristic or tuned tolerance is a review
failure** (CLAUDE.md §8); abstention/escalation stays the honest floor.

**CORRECTION + diagnosis (measured 2026-08-04, systematic-debugging probes; supersedes the
two paragraphs above and §1's "no vector rules" claim):** the page IS ruled —
`page.lines` is 0 but Excel draws borders as RECTS, and `extract_rules` reads them (142
vertical rules, 95 hrules on page 0), so the failing path is the RULED one and loop L's
territory after all. Measured on the GERALDTON section: (i) every INTERIOR vertical rule
spans exactly the grid rows (y 105.5→199.6); only the OUTER border spans the whole section
(63.3→199.6), segmented by the author's row borders at 71.8 / 105.4 / **119.1**; (ii) the
heading and the four notice lines sit ABOVE the interior rules' extent — full-width merged
strips no interior vertical crosses — yet band construction feeds them to the header
builder, which fabricates 5 all-column spanning levels (`GERALDTON` > notices > …), and
the rule-aware re-extraction even chops the heading at column rules (`GERALDTO N`, the
R14/loop-G class); (iii) the "3-line stack" is ONE author-ruled header row (border segment
105.3→119.1 contains all three visual lines): per-column wrapped text (`Time Nom` +
`Accepted` = one cell's two lines, centered single-line names on the middle line);
(iv) `merge_tiling_ok` correctly refuses the fabricated tree on all four sections (no
ambiguous nodes — the centering/overlap arms), and no NEURAL proposer is wired in
production (R7), so the honest escalation is `MERGE_AMBIGUOUS` at 0 cells. **The
mechanism is therefore pinned as two evidence-positive presence-test AXIOMs, both
shipped patterns:** (1) **grid-region scoping** — a band line belongs to the ruled grid
iff ≥1 interior vertical rule crosses its y; lines above are peeled and CARRIED as
captions (`tab:RegionCaption`, loop C's class — which hands loop Q its section-key
evidence for free); (2) **header-row welding by author hrules** — visual lines between
consecutive author row-borders inside the grid's header region are ONE header row (loop
H's "author rules ARE the row delimiters", applied to the header side), cell text
recovered per rule column across the welded lines by the existing rule-aware char
machinery. No tuned constant; no NEURAL required on this evidence; the doubled rules
measured at x=345.1/345.6 are R31's known class and must collapse by the shipped
presence-test, not a distance. The loop P plan implements exactly this.

**Loop P outcome (François's adjudication, 2026-08-04 — supersedes this section's DoD
expectation of a closed gap (a)):** Tasks 1–3 shipped the two AXIOMs designed above —
`vocab/queries/grid-region.rq` + `vocab/queries/line-enclosed.rq` (`src/iladub/etkl/gridregion.py`)
and `weld_hrule_boxes` (`src/iladub/etkl/geometry.py`) — green on the synthetic fixture
(490/490 in `tests/etkl/`), but **inert on both real specimens**: the shipped
`grid_lines`/interior-rule test alone does not fire on CBH (border twins x=37.92/38.2
read as interior) and a subsequent fix wave (3 commits) attempting to make it fire was
**reverted** (`1271156`) after the breaker tripped. Three witness licences were tried at
the `_build_ruled_band` seam and each fixed one real specimen while breaking the other:
- **ink-witness** (interior rules must show header/body ink on both sides) — CBH 0.9926
  (4/4 sections assert, correct captions) but the stem regresses to 1.0000-WRONG: the same
  test that frees CBH's border twins also frees the stem's real header stack, which the
  peel then swallows (chains `[1,1,1]`, grounded 0).
- **straddle witness** (peel licensed only where the heading text straddles a rule) — CBH
  0.3636 (KWINANA's short heading doesn't straddle, peel stalls) and the stem's
  `'Friday, 31 July 2026'` line gets peeled, disengaging loop L's clause-0 engagement →
  `REGION_TILING_FAILED`.
- **opening-box witness** (peel licensed by the grid's own drawn opening header box) — CBH
  0.0724 (near-unchanged) and the stem drops to 0.9660 ≠ 0.9655: pages 1–2 flat-assert
  STANDALONE, loop M's carriage dead (chains `[1,1,1]`, grounded 167).

**The conflicting seam requirement, stated once:** `_build_ruled_band` is shared by three
laws that each need a DIFFERENT licence from the same peel decision — loop L's engagement
(stem p0's furniture row must stay), loop M's carriage (stem p1–2 must keep escalating
standalone when read alone), and CBH's sections (strips above the grid must peel). No
band-local licence satisfies all three; a repair scoped to one band cannot see enough
context to arbitrate between them.

**Loop Q's design is amended accordingly:** the peel/weld repair re-homes at SECTION
scope, disposed inside loop Q's design once recognition has already established it is
facing a sectioned chain with repeated headers (§4.1's recognition AXIOM) — i.e.
recognition first, then the re-reading licence for the strips above each section's grid,
rather than a single band deciding blind. Gap (a) of R42 stays OPEN; the full measured map
is recorded in the R42 row of `docs/superpowers/residues.md` (canonical; not duplicated
here). Section §3's "candidate homes" and "CORRECTION" text above stand as the diagnosis
that IS correct — the mechanism it names is real evidence, just insufficient at band
scope to arbitrate the three laws sharing the seam.

**DoD:** CBH page-0 sections compile (or escalate with a *semantic* reason François
adjudicates); the measured score replaces 0.0698 in the loop evidence; the 66-cell region
byte-identical; full suite + corpus battery re-run; R42 gap (a) closed in the register.

## 4. Loop Q — split-key attribution and naming

### 4.0 The section-scope repair (added 2026-08-04 from loop P's architectural finding)

Loop P proved no band-local licence can serve the peel/weld repair: the
`_build_ruled_band` seam is shared by loop L's engagement (stem p0 needs its furniture
row KEPT), loop M's carriage (stem p1–2 must keep escalating standalone), and CBH's
sections (strips must peel) — three consumers, contradictory demands, three measured
whipsaws (the R42 register row carries the map). The repair therefore runs at SECTION
scope inside the document driver, **strictly after** the readers it must not disturb:

1. **Band-level compile** runs exactly as today. *(CORRECTION, measured 2026-08-04 at
   loop Q Task 1: loop P's peel/weld IS wired in `_build_ruled_band` and fires wherever
   section edges are CLEAN — the loop-P synthetic asserts at band level, score 1.0.
   It is defeated — hence inert — precisely on doubled-edge documents like the real
   CBH, which escalate. Both outcomes are acceptable inputs to this step's ordering:
   a clean-edged section that asserts at band level needs no repair, only stitching;
   a doubled-edge section escalates and becomes a repair candidate. The stem is
   untouched either way — measured exact through loop P's close.)*
2. **Document carriage** (loop M recognition + loop O licence) runs next, unchanged —
   stem pages 1–2 are carried cross-page and never reach step 3.
3. **Section repair (NEW):** the page's **intra-page section repetition** is recognized
   over ruled bands REGARDLESS of their band-level verdict (the identity evidence is
   raw: header-box line texts repeating verbatim + agreeing interior-rule x-sets —
   author marks + raw text, no successful reading required). Within a recognized group,
   ONLY the still-escalated members are re-read as repair candidates; members that
   already assert (clean-edged sections read at band level) pass through untouched.
   Stitching (§4.1) then runs over ALL recognized members that assert, whichever route
   they took. Each
   recognized member is re-read as a **candidate**: peel leading non-grid strips (loop
   P's `grid_lines`/`enclosed` machinery, with the ink-witness interior definition —
   safe HERE because the scope guarantees a sectioned page, which the stem never
   presents to this step) + weld the leading header box; the candidate is **disposed by
   the existing region membrane** (tiling shapes + `merge_tiling_ok` + score): it
   ASSERTS only if the re-reading passes; otherwise the band stays escalated exactly as
   before. The repair is **monotone by construction** — it can only turn escalations
   into membrane-passing assertions, never touch an asserting band, never worsen an
   escalation — which is precisely the property the loop-P wave lacked and the reason
   it whipsawed.

§4.1's stitching then runs over the repaired sections; the peeled captions are the
key evidence §4.2 consumes. Loops' order of authority (band reading → carriage →
section repair) is load-bearing and must be pinned by a test on BOTH specimen shapes.

The repeated 3-line header block is loop M's **repeated-header signature**, intra-page: the
recognition AXIOM (leaf-header identity between blocks) generalizes from page pairs to
**band pairs within a page**, licensing `tab:continuesTable` between section tables — the
sections chain into ONE logical table exactly as pages did in loop M, and loop N's
document-level machinery (groups, arithmetic) rides the same chain. The **section boundary
oracle is arithmetic**: the per-section total (loop H `detect_aggregation_rows`, exact
Decimal) confirms where a section's rows end (`374,904`; `737,289`). A section whose total
does not confirm is refused stitching under the loop-O licence discipline — refusal
recorded as facts (`tab:licenceRefused` analog), never silently stitched.

### 4.2 Key-value attribution (AXIOM; loop I's pattern, new evidence source)

The candidate key is the heading line **between** a confirmed section end (total row or
page/section start) and the next repeated header block; berth-notice lines in that span are
carried as `tab:RegionCaption` (loop C's furniture carry — §5, never dropped). The key
becomes a derived group node (loop I's `tab:DerivedRowGroup` pattern) covering the
section's rows, `tab:hasLabel` → the source heading cell (**provenance to the page free**),
`prov:wasDerivedFrom` → the confirming total row. Record identities then carry the key
value positionally (`GERALDTON > r3`) exactly as loop I/N mint them — **attribution never
waits for naming**.

### 4.3 The naming cascade (the "score the ambiguity" mechanism, gate-shaped)

The denormalized column NAME is recovered by a three-step cascade; each step only fires
when the previous abstains:

1. **AXIOM — explicit naming in the source** (§0 recovery): a `Key: Value` marker form
   ("Port: GERALDTON") or shared literal label names the dimension from the document
   itself. CBH fails this (bare `GERALDTON`).
2. **AXIOM — unique admitting contract field**: ground the marker *values* against the
   destination contract's schemes (`ground.py`, shipped). A field **admits the set iff its
   scheme contains every marker** (whole-set membership — strict, decidable). The
   **ambiguity score is the count of admitting fields**: exactly one → the name is
   *derived from the contract*, asserted through a `iladub:PromotionDecision` recording
   the membership evidence. No LLM. Partial membership (a field admits a strict subset)
   never asserts here — it abstains to step 3, where the per-field membership counts are
   the proposal's evidence and any non-member marker quarantines as a value (§7).
3. **NEURAL — BAML scored proposal** (zero or ≥2 admitting fields): a BAML function
   `ProposeSplitKeyName(markers: string[], context: ContextSketch) → ScoredCandidate[]`
   — the context sketch itself LLM-inferred from document furniture (title "Daily Ship
   Roster", vessel/ETA/ETC vocabulary → maritime scope; markers are geographies). Disposal
   splits by what the oracle already established:
   - **≥2 admitting fields:** the LLM only *picks among already-verified* candidates — the
     winner asserts (membership was decided before the LLM spoke; the NEURAL narrows,
     soundly — the loop-C pattern).
   - **0 admitting fields:** the top proposal stays a quarantined `iladub:CandidateConcept`
     (suggested anchor, suggester, score) — `"port"` at 0.98 **never asserts on confidence
     alone** (§3; the B1.2 confidence≠validity lesson). Rows keep their positional key
     values regardless (§4.2).

Per-value membership is individual (the shipped grounding behavior): a marker outside the
scheme (a new or typo'd port) quarantines as a value while the name outcome is decided by
the members; §7 honest refusal throughout.

### 4.4 Demo contract (illustrative, public nomenclature)

Extend `examples/shipping/` with a CBH stem contract + terms: a `port` field whose scheme
carries the WA public port names (Geraldton, Kwinana, Albany, Esperance, …) alongside the
existing GrainCorp east-coast scheme — same illustrative posture as loop K's stem contract
(example.org, no identifying fields). The cascade's step 2 must resolve CBH **uniquely** to
`port` against this contract; a negative test presents a second admitting field to force
step 3's pick-among-verified path, and a no-contract test pins the quarantine path.

### 4.5 DoD (loop Q)

CBH compiles end-to-end through `compile_document`: one intra-page chain per page (and
across pages if the roster continues), records carrying port keys
(`GERALDTON > …`), the key name `port` asserted via the cascade with its
`PromotionDecision` trail, non-member markers quarantined; measured score and
records/grounded/quarantined tallies in the loop evidence; corpus battery re-run green on
the new expectation (François adjudicates the manifest verdict flip — the loop proposes,
never edits it); R42 deleted from the register.

### 4.6 Status (loop Q close, Task 7, 2026-08-04)

**§4.0-§4.4 SHIPPED and measured end-to-end on the real specimen** (`tests/test_cbh_e2e.py`,
one module-scoped `compile_document` over `corpus/ag-trade/cbh-stem-2026-08-03.pdf`):

- **§4.0 (section-scope repair):** score 0.0698 → **0.9047** (0.9046563192904656); all
  4 of the doubled-edge escalated bands recognized, ink-witness-repaired and adopted
  (`repaired_bands = ((0,1),(0,3),(0,5),(0,7))`) — monotone, byte-identical on the stem
  shape throughout Tasks 1-4.
- **§4.1 (stitching + arithmetic):** the four repaired sections chain into ONE 4-member
  logical table (`chains` = one 4-chain + one unrelated singleton, `[4, 1]`) via
  `tab:continuesTable`. The per-section printed-total confirmation half of §4.1 did
  **NOT** measure on the real document: `document._confirm_section_total` produced
  **zero** `tab:SectionTotal` facts on CBH (registered as R50/R47's residual, not
  silently dropped) — the section boundary the spec's arithmetic oracle describes is
  not yet what closes CBH's sections; the repeated-header signature (§4.0) is.
- **§4.2 (key-value attribution):** section captions injected as candidate concepts and
  used to prefix record identity — measured on the real document: 49 of 58 records
  section-prefixed, distinct across GERALDTON/KWINANA/ALBANY/ESPERANCE. Implemented as
  the FEED-level positional form only (`row_id` prefix + injected `SurfaceConcept`s);
  the spec's `tab:DerivedRowGroup`/`hasLabel`/`wasDerivedFrom` GRAPH-level form was not
  built — open as **R49**, not overclaimed by this close.
- **§4.3 (naming cascade):** the record-identity prefixes (`GERALDTON`/`KWINANA`/
  `ALBANY`/`ESPERANCE`) resolve to the CBH contract's `port` field via the
  **unique-admitting-field** AXIOM arm — `ambiguity_score=1`, one
  `iladub:PromotionDecision`, no LLM call needed on this specimen (arm 1, explicit
  naming, correctly abstains — CBH's markers are bare; a raising proposer confirmed
  arm 3 is never reached).
- **§4.4 (demo contract):** `examples/shipping/cbh-{contract,terms,shapes}.ttl` shipped
  (Task 6) and now referenced from `tests/corpus-manifest.ttl`'s CBH entry
  (`cor:contract`/`cor:terms`/`cor:shapes`, Task 7) — the membrane's all-or-none rule
  satisfied; **verdict adjudication (the `Unadjudicated` → flip) is François's, not
  changed by this loop**.
- **Grounding, full document:** records=58, grounded=134, still-quarantined=775; every
  `GroundedNode` behind exactly one `wasPromotedBy` (the §3 invariant, held over the
  whole repaired document, not a fixture).
- **R42 register outcome:** closed with both gaps measured (see the register row) —
  kept as `~~R42~~` with its closure narrative (repo convention: R1/R2/R35 are struck
  through and summarized, not deleted, so the resolution history stays legible).

## 5. Global constraints (hard; reviewers enforce)

- **§8 gate:** every decision classified AXIOM / NEURAL / PROCEDURAL before code; no tuned
  constant or Python span/read/group heuristic; NEURAL only oracle-disposed (tiling,
  conservation, scheme membership). Derivations open-world SPARQL; membranes closed-world
  SHACL; the holon/section is the closure boundary.
- **No overfitting (standing):** every mechanism is general — CBH is the *specimen*, never
  the target. The repeated-header generalization must keep loops M/N/O byte-identical on
  the GrainCorp stem; the cascade must behave on documents with explicit naming (step 1)
  and no contract (step 3, quarantine) — both fixture-pinned.
- **§7:** unconfirmed sections refuse stitching; refusals recorded as facts; nothing
  fabricated for coverage.
- Corpus battery + full suite re-run at each loop close; measurements (never mechanisms)
  go to the manifest notes only via François's adjudication.

## 6. Out of scope

- The other corpus defect loops (R41 apple crash, R43/R44 gov-stats, R45 WHO matrix).
- External-KB verification (UN/LOCODE) for step 3's zero-field case — considered and
  **deferred**: it imports an external source of truth into the membrane; revisit only if
  real documents show contract-silent splits that matter.
- R39 (nesting.rq perf) — loop Q rides the existing chain machinery and inherits its cost;
  the perf slice stays its own loop.
- Cross-document series reasoning (CBH edition-over-edition) — corpus `cor:series` exists;
  nothing here reads it.

## 7. Expected residues

To be measured, not presumed — likely: sections whose totals are blank (the R4-family
walk-back) refuse stitching; multi-level splits (port > berth) exceed the single-heading
derivation; the context-sketch LLM step needs its own provenance recording (R5's shape).
Each goes to the register at close with its measurement.
