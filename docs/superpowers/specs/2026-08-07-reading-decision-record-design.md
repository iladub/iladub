# The reading decision record — what iladub understood, as evidence — design

**Date:** 2026-08-07 · **Status:** approved (François, 2026-08-07) ·
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
| `dec:consideredEvidence` | the observations consulted (the typed-cell and classify evidence already built per band) |
| `dec:optionSpace` | the candidates available, each a `dec:Option` |
| `dec:chosen` | the option taken |
| `dec:rejectedBecause` | on each discarded option — the observation that refuted it |
| `dec:rationale` | the human-readable statement (today's reason string, no longer the only record) |
| `dec:order` | position in the sequence for that band |
| `dec:partOf` | the parent decision — document → page → band → judgement |

`dec:order` and `dec:partOf` give the document→table decision hierarchy with no new terms.

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
