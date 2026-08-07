# The reading decision record — what iladub understood, as evidence — design

**Date:** 2026-08-07 · **Status:** closed 2026-08-07 ·
**Slice:** A of the reading-as-differential-diagnosis architecture (§7 names B–E) ·
**Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf` page 0

**Doc impact:** increment — no new vocabulary (the `dec:` terms already exist and are
owned); a wiki note on the decision record queues for the next release. No site page
contradicted.

## 1. The problem

iladub records the *last* step of its reasoning and discards the rest. Every grounded node
traces to an accountable `iladub:PromotionDecision` with `prov:used` evidence — CLAUDE.md §4's
promise, kept. But the entire reading that *precedes* it — is this a table, how many columns,
is it transposed, is it a matrix, where does the header end — happens as a cascade of Python
calls returning a kind and a reason string. **The alternatives considered are never named, and
the moment a branch is taken the others cease to exist.**

Two measured consequences:

- **The reader cannot show its work.** `MATRIX_AMBIGUOUS` and `REGION_TILING_FAILED` are
  terminal states with no trail. A user cannot ask *why*, and neither can a reviewer.
- **Wrong attributions survive.** R55's register row claimed `transpose_is_coherent` failed
  "SOLELY because" of parenthesized negatives. Measured later, the truth was that a
  currency/numeric type split made `looks_transposed` fire *first*; the parens failed a
  *second* gate that would never have been reached. Nothing in the system could contradict the
  claim, because the chain was not recorded. That error stood in the canonical register for a
  day and was found only by hand-instrumenting the pipeline.

Every loop in the 2026-08-05/06 sequence reconstructed such a chain with ad-hoc probes. **That
reconstruction is the most valuable artifact of each loop, and the compiler throws it away.**

## 2. The vocabulary already exists, and its differential half has never been used

`vocab/ontology/dec.ttl` is, unintentionally, a differential-diagnosis vocabulary:
`dec:DecisionHolon`, `dec:Option`, `dec:optionSpace`, `dec:chosen`, `dec:rejectedBecause`,
`dec:consideredEvidence`, `dec:rationale`, `dec:regarding`, `dec:order`, `dec:partOf`,
`dec:revisitIf`, `dec:supersedes`.

Measured: the shipped `iladub:PromotionDecision` emission (`src/iladub/ground.py:126-137`)
uses `dec:decidedBy`, `dec:consideredEvidence`, `dec:confidence` and `dec:rationale` — and
**never** `dec:optionSpace`, `dec:chosen` or `dec:rejectedBecause`. The half of our own
vocabulary that expresses *a differential with refutations* has no producer.

This slice gives it one. It invents no vocabulary.

## 3. The design

**Every named judgement on the path from band to verdict emits a `dec:DecisionHolon` into the
document's compiled graph.** No verdict changes; the reading becomes queryable.

Per decision:

| property | carries |
| --- | --- |
| `dec:regarding` | the band/region node the decision concerns |
| `dec:consideredEvidence` | designed to carry the observations consulted (the typed-cell and classify evidence already built per band) — **no producer in this slice**: `BandRecorder.record` (`src/iladub/etkl/decisionlog.py:39-40`) accepts an `evidence=` parameter, but no `brec.record(...)` call site in `compile.py` ever passes one, so no `dec:consideredEvidence` triple is emitted by this loop's judgement chain |
| `dec:optionSpace` | the candidates available, each a `dec:Option` |
| `dec:chosen` | the option taken |
| `dec:rejectedBecause` | on each discarded option — the observation that refuted it |
| `dec:rationale` | the human-readable statement (today's reason string, no longer the only record) |
| `dec:order` | position in the sequence for that band |
| `dec:withinProcess` | the band process this judgement was made inside |

The containers are the other half of the hierarchy, and they are **processes, not decisions**: a
page and a band are `dec:Process` nodes, nested with `dcterms:isPartOf` (band → page →
document). So the hierarchy is `dcterms:isPartOf` between the containers and
`dec:withinProcess` from a judgement to its band — `dec:partOf` is decision→decision and a page
is not a decision, so it is *not* what carries this. With `dec:order` that gives the
document→table decision hierarchy with no new terms.

**Which judgements** — every one on the band-to-verdict path, so each band carries a *complete*
chain rather than a partial one: kind classification (`regions.classify`), header/body split,
the transposed test and its coherence oracle, row-grouping, matrix candidacy, hierarchical
classification, the tiling gate, and the escalation itself.

**Where the Python sits.** A recorder threaded through the compile path; the judgements
themselves are untouched. Per the gate this is engine glue: it makes no domain decision, it
observes ones already made. The *evidence* is the graph; the Python only carries it there.

### 3.1 The record ships inside the document graph (François, 2026-08-07)

The chain is part of what the document compiles to, not a side artifact — so it travels with
the graph, is queryable by the same SPARQL a consumer already uses, and cannot drift from the
reading it describes.

**Consequence that must be handled, not discovered later:** the record therefore passes
through the SHACL membrane. Decisions must be emitted into the **document graph only, never
into a region's scratch graph before `region_tiles`** — a gate that validates a graph
containing decision holons is the R19 hazard again (a shape firing on something that is not
what it thinks it is). The gate's shape set is unchanged by this loop; the emission point is
what keeps it true.

## 4. What the record must be able to answer

The test of this slice is not that triples exist — it is that a question can be answered from
them by query alone:

1. *Why was this region escalated?* → the chain of decisions for that band, ending in the
   escalation, each with its refuting observation.
2. *What else was considered?* → `dec:optionSpace` minus `dec:chosen`.
3. *In what order were the judgements made?* → `dec:order`, so a reader can see which gate
   fired first.

Question 3 is the one that would have prevented R55: apple band 4's chain must show
`looks_transposed` firing **before** the coherence oracle was consulted.

## 5. The honest limit, stated up front

With today's three-value `RegionKind` (`RECORD_TABLE`, `UNSUPPORTED_TABLE`, `NON_TABLE`), the
`optionSpace` is thin. Apple band 3 will record, truthfully, that the reader considered
`RECORD_TABLE`, rejected it because *"header has 1 words but 5 columns"*, and that **nothing
else was ever a candidate**.

That record is unflattering, and that is its value: it is the evidence for slice B, produced
by the system rather than argued in a spec. A reader of apple's graph will be able to see that
iladub's conclusion "unsupported" is a statement about iladub, not about the document.

## 6. Success criteria

- Compiling apple page 0 yields a complete chain per band, and the three §4 questions are
  answerable **by SPARQL over the compiled graph alone** — pinned by tests that run those
  queries, not by asserting triple counts.
- Band 4's chain shows `looks_transposed` before `transpose_is_coherent` (the R55 link).
- Every escalated region has a decision explaining it; no region ends without a chain.
- **Corpus scores byte-identical** — stem 0.9655 / 2152 cells / chain [3], CBH 0.9047,
  capacity 1.0000, apple 0.0606860158, WHO 0.5597. This slice records; it does not decide.
- Graph-size and compile-time cost measured and recorded (every band now carries a chain).
- Whole-graph SHACL still conforms with the decisions present.

## 6.1 Measured results — the close (2026-08-07)

**The artifact this loop exists to produce** — the committed `vocab/queries/why-escalated.rq`
run over apple page 0, regions 3 and 4, verbatim:

```
--- region3 ---
  0. multi_table          chosen=single             — single table
  1. kind                 chosen=UNSUPPORTED_TABLE  — header has 1 words but 5 columns
  2. matrix_candidate     chosen=not_matrix         — matrix-candidacy oracle found no two-axis matrix header structure
  3. hierarchical         chosen=hierarchical       — hierarchical oracle inferred a 1-node header tree
  4. region_tiles         chosen=does_not_tile      — region_tiles rejected the 15 body tokens asserted into scratch
  5. verdict              chosen=escalated          — REGION_TILING_FAILED
--- region4 ---
  0. multi_table          chosen=single             — single table
  1. kind                 chosen=RECORD_TABLE       — flat single-level header
  2. transposed           chosen=upright            — upright
  3. row_grouped          chosen=flat               — row-grouping oracle found no repeated row-label groups
  4. region_tiles         chosen=tiles              — region_tiles validated the 20 entries asserted into scratch
  5. verdict              chosen=asserted           —
```

**Verdict stability (the loop's binding constraint).** Byte-identical, verified three times
across the loop: `tests/test_corpus_stem.py` + `tests/test_cbh_e2e.py` — 13 passed (stem
0.9655 / 2152 cells / chain [3]; CBH 0.9047). Document scores: apple `0.0606860158`, capacity
`1.0000000000`, WHO `0.5597484277` — each matching its pre-loop baseline exactly.

**Cost of the record.** stem compile: 158s (pre-loop baseline ~151s). stem document-level
graph: 30,015 triples, of which the record is 638 triples across 142 nodes (2.1%). 30,015 −
638 = 29,377 — exactly the pre-loop triple count, so the record is purely additive and nothing
else in the graph moved. stem carries 36 `dec:DecisionHolon` judgements and 13 `dec:Process`
containers across 3 pages / 10 regions (≈3.6 judgements per region; 13 = 3 page-processes + 10
band-processes).

**§6 criteria, one by one:**

- *Compiling apple page 0 yields a complete chain per band, and the three §4 questions are
  answerable by SPARQL over the compiled graph alone.* **Met.** The chains above are that
  answer, produced by the committed query, pinned by tests that run the queries rather than
  asserting triple counts.
- *Band 4's chain shows `looks_transposed` before `transpose_is_coherent` (the R55 link).*
  **Not met.** See below — stated plainly, not softened.
- *Every escalated region has a decision explaining it; no region ends without a chain.*
  **Met.** Region 3's chain above ends in `verdict chosen=escalated — REGION_TILING_FAILED`,
  itself the product of the preceding four judgements; region 4 ends in an asserted verdict
  with the same completeness.
- *Corpus scores byte-identical.* **Met.** stem 0.9655 / 2152 cells / chain [3], CBH 0.9047,
  capacity 1.0000000000, apple 0.0606860158, WHO 0.5597484277 — all reproduced above.
- *Graph-size and compile-time cost measured and recorded.* **Met.** 158s / 30,015 triples /
  638 record triples (2.1%) / 36 decision holons / 13 process containers, above.
- *Whole-graph SHACL still conforms with the decisions present.* **Met for the membrane the
  compiler runs; not met against `dec-shapes.ttl`.** `compile._validate`
  (`src/iladub/etkl/compile.py:335-345`) loads only `tab-shapes.ttl` and
  `tab-physical-shapes.ttl` with `tab.ttl` as the ontology graph — it never loads
  `dec-shapes.ttl` or `dec.ttl`. The corpus suite passing at the counts above shows the record
  crosses that membrane without tripping a shape (the §3.1 hazard, and it held) — it says
  nothing about `dec-shapes.ttl` conformance. Validating a real compiled apple page 0 against
  `dec-shapes.ttl` with `dec.ttl` as ontology, `inference="rdfs"`, does **not** conform: five
  non-conforming focus nodes, all regions (`region2`, `region3`, `region5`, `region6`,
  `region7`), zero violations on any decision or process node this loop emits. Cause, traced
  and pre-existing: `escalate_region` (`src/iladub/etkl/holon.py:375`) emits `dec:confidence`
  on the region/candidate URI; `dec:confidence` has `rdfs:domain dec:DecisionHolon`
  (`vocab/ontology/dec.ttl:81`), so under RDFS inference the region node is entailed to be a
  `dec:DecisionHolon` and then fails `dec:DecisionHolonShape`'s `optionSpace`/`chosen`/
  `decidedBy` requirements plus a `dec:ConfidenceShape` datatype violation on the same value.
  The recorder never emits `dec:confidence`, and this loop's diff changes no `confidence`
  line — the defect predates this loop; this loop merely built the first gate that can see it
  (see R69). CBH was not scanned for this check, same caveat as the R55 table above.

**The R55 criterion, not met — the evidence.** I measured this across four documents by
compiling each and scanning every page's graph for judgements labelled `transposed` /
`transpose_coherent`:

| document | `transposed` judgements | `transpose_coherent` |
| --- | --- | --- |
| apple | `region4-d2`=upright, `region6-d2`=upright | none |
| capacity | `region3-d2`=upright | none |
| WHO | `region4-d2`=upright | none |
| stem | zero `transposed` judgements at all (path never reached) | none |

Every `transposed` judgement in the corpus chooses `upright`, so `transpose_is_coherent` is
never consulted and the ordering §6 asks for cannot be observed. `test_judgement_order_answers_the_r55_question`
guards that half behind `if "transpose_coherent" in order:`, so the assertion is inert — its
unconditional `assert "transposed" in order` still bites, and the test does not conceal the
situation, but the R55 link is unproven end-to-end. This is not an implementation defect: the
recorder records what the code evaluates, and the code never evaluates the coherence oracle on
this corpus. CBH was not scanned (different pipeline entry), so this table is not full
coverage even of the shipped corpus — it is what was measured.

## 7. Out of scope — the rest of the architecture

- **B — candidates as ontology classes:** replace the three-value enum with a carried set of
  topology candidates named in `tab.ttl`, narrowed by observation rather than by an early
  Python branch.
- **C — per-cell disposition:** ground what surviving candidates agree on; quarantine only the
  cells the ambiguity touches (§3's assert/propose at cell granularity, replacing
  region-level all-or-nothing escalation).
- **D — document-level strategy:** what kind of document this is and what regions it holds,
  with *that there is a table here* recorded as evidence rather than assumed.
- **E — the pivot/cube reading:** apple as a cube slice with two dimension hierarchies and
  aggregations on both axes, using `tab:BaseFact`, `tab:PivotedDimension` and the
  `tab-qb-align.ttl` anchor (`tab:BaseFact ⊑ qb:Observation`) that today is 8 lines loaded
  only by a test.

## 8. Global constraints (carried, per CLAUDE.md)

- **Ontologies are evidence for proof; Python validates heuristics** (François, 2026-08-07).
  The record is `dec:` terms in the graph; the recorder is glue and makes no judgement.
- Neurosymbolic gate: no decision moves into procedural code, no tuned constant. The
  judgements are untouched.
- §5 context is carried, not discarded — this slice exists because it currently is.
- Source ownership: `dec:` is owned; no new terms; `qb:`/HGA untouched.
