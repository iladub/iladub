# The decision membrane — validating what iladub decides (R69, R81, R82) — design

**Date:** 2026-08-10 · **Status:** design, implemented (2026-08-11, branch `loop-decision-membrane`) · **Residues closed:** R69, R81, R82
(+ one unregistered defect this spec names in §3.3) · **Specimen:** the whole corpus — all 7
documents in `corpus/`, compiled through `compile_document`, plus the two contracted documents
grounded through `ground_document` · **Builds on:** `2026-08-06-subclass-only-closure-design.md`
(the closure the membrane ships), `2026-08-07`'s decision log (`BandRecorder`, the one
well-formed producer), `2026-08-09-adoption-at-document-scope-design.md` (which put the data
grid's admission holon on the verdict query surface and registered R81/R82)

**Doc impact:** contradiction. `docs/wiki/concepts/promotion-decision.md:48-49` asserts
"iladub's SHACL membrane hard-fails any grounded node lacking `wasPromotedBy`";
`docs/wiki/concepts/decision-holon.md:26` asserts "the core deliberation shape is enforced, not
just declared." §3 measures both false for every compiled and grounded document — the shapes are
applied only in unit tests against fixtures. The contradiction is **resolved by this loop**: the
membrane is turned on and the producers are fixed, after which both sentences become true. Both
pages (and `assert-propose-promote.md`) take an increment recording *where* enforcement happens.

**Doc impact — RESOLVED 2026-08-11, in this loop.** Both sentences are now true, and all three
wiki pages carry the increment naming the call sites: `compile._validate`
(`src/iladub/etkl/compile.py`) and `ground_document(..., validate_shapes=True)`
(`src/iladub/feed.py`). `promotion-decision.md` also carries the lesson the contradiction
taught — *a claim about enforcement that does not name its call site is how this one survived*
— and `assert-propose-promote.md` records the measured before-state (all 24 emitted
`iladub:CandidateConcept` nodes refused by their own shape). No contradiction remains, so the
release gate (`scripts/release_gate.py`) is unblocked by this spec.

---

## 0. The claim, in one line

iladub's differentiator is that **every grounded node is the product of an accountable
`iladub:PromotionDecision`** — stronger than HGA's bare confidence gate. Measured on real
documents, that claim is today **weaker** than HGA's: iladub records a confidence and an agent
and **no deliberation at all**, and nothing anywhere checks it. This loop makes the claim true
by making it *enforced* — the shapes that state it are applied to compiled and grounded graphs,
and the three producers that violate them are fixed.

## 1. The blindness has three layers, not one

R82 registered one: `dec-shapes.ttl` is never parsed against a compiled graph. Measurement
(§3) finds two more underneath it:

1. **The gate is absent.** `compile._validate` (`compile.py:389-399`) parses only
   `tab-shapes.ttl` + `tab-physical-shapes.ttl`. `grep -c 'dec:'` returns **0** on both.
   `iladub-shapes.ttl` — which holds `GroundedNodeShape`, the shape that *is* the differentiator
   — is absent too, from `_validate` and from every other production path.
2. **The closure hides one class of violation even if the gate were on.** Since spec
   2026-08-06 the membrane expands with `subclass_closure`, not `rdfs_closure`
   (`membrane.py:60-70`, both engines): domain/range typing is gone **by design** (it was the
   R19 mechanism). R69's violation depends on `dec:confidence`'s `rdfs:domain` and therefore
   **does not fire in-house** — but it fires for any consumer that applies our published
   axioms (Fluree, an external reasoner). R69 is a **publication** defect, not an in-house one.
3. **The producers are malformed independently of both.** Three emitters write `dec:` and
   `iladub:` triples that no shape has ever seen. Two are registered (R69, R81). The third —
   the promotion emitters themselves — is **unregistered and 27× larger than the other two
   combined**.

## 2. What proposes, what disposes, and are they independent

| | proposes | disposes | independent? |
| --- | --- | --- | --- |
| a candidate concept | `escalate_region` / `ground._emit_candidate` | `iladub:CandidateConceptShape` | **yes** — the shape was authored in the vocabulary loop, by a different act than the emitters, and has never been shown the emitters' output |
| a decision holon | `BandRecorder`, `emit_data_grid`, `ground._emit_grounded`, `promote.*` | `dec:DecisionHolonShape` | **yes**, with one caveat: `BandRecorder` *also* guards `len(options) >= 2` and `chosen in options` in Python (`decisionlog.py:44-47`). That guard is a producer-side fail-fast, not the oracle; it is why `BandRecorder`'s output passes, and it is precisely the guard the other three emitters lack |
| the loop as a whole | this design | the corpus: 7 documents compiled + 2 grounded, before and after | **yes** — the shapes are pre-existing artifacts the corpus has never been validated against |

The disposing oracle is **not authored by this loop**. `dec-shapes.ttl` and `iladub-shapes.ttl`
are shipped, tested vocabulary artifacts. This loop changes *where they are applied*, not what
they say. That is what makes the measurement in §3 a genuine falsification rather than a
self-graded exam — and it is why the numbers below could not have been predicted from the code.

## 3. What is measured

All figures 2026-08-10, this machine, `./.venv/bin/python`, pySHACL with `inference="none"`,
`advanced=True`, over `membrane.subclass_closure` (SHIPPED — what `_validate` would do) and
`membrane.rdfs_closure` (RDFS — what a consumer applying our published axioms sees). Ontology
graph = `dec.ttl` + `iladub.ttl` + `etkl.ttl` + `tab.ttl`. Scripts and full logs are evidence of
this loop; the commands are reproduced in §6.

### 3.1 Compile scope — `dec-shapes.ttl`, all 7 corpus documents

| document | triples | `dec:DecisionHolon` | SHIPPED | RDFS |
| --- | --- | --- | --- | --- |
| cbh-stem-2026-08-03 | 12 140 | 65 | conforms | conforms |
| graincorp-capacity-2026-08-04 | 5 705 | 18 | conforms | conforms |
| graincorp-stem-2026-07-31 | 29 999 | 36 | conforms | conforms |
| apple-fy2026q3-statements | 3 633 | 119 | conforms | **44** (11 foci × 4) |
| bfs-population-bilan-2023 | 8 118 | 232 | conforms | **40** (10 × 4) |
| ons-index-of-services-2026-02 | 11 062 | 218 | **2** | **2** |
| who-wfa-boys-zscore-0-5 | 8 058 | 81 | conforms | **12** (3 × 4) |

The two SHIPPED refusals are `<doc>/p7#p7-datagrid-admission` and `<doc>/p8#p8-datagrid-admission`,
both `dec:decidedBy` minCount — **R81(a′), observed live on the corpus**, on the
`datagrid_fallback=True` default path (not the adoption path R81 measured). R81(c)
(`optionSpace minCount 2`) stays **unobserved**: both ons grids refused rows, so both clear it,
exactly as the register recorded.

### 3.2 Compile scope — `iladub-shapes.ttl`, same 7 documents

24 focus nodes refuse under the **SHIPPED** closure — no inference trick needed — every one of
them a candidate minted by `escalate_region`, each failing **all four** required properties:

```
apple-fy2026q3   11 candidates  ┐  suggestedBy :: A candidate must record who/what suggested it.
bfs-population   10 candidates  │  confidence  :: A candidate must carry a confidence in [0,1].
who-wfa-boys      3 candidates  │  fromRegion  :: A candidate must record its source region.
                                ┘  status      :: A candidate's status must be 'proposed'.
cbh-stem / graincorp-capacity / graincorp-stem / ons: 0 candidates → conform vacuously
```

Cause, measured at `holon.py:370-376`: `escalate_region` emits `iladub:surfaceText`,
`iladub:suggestedAnchor`, `dec:confidence`, `dec:rationale`, `prov:wasDerivedFrom` — the
**decision** vocabulary on a **proposition**, and none of the four things §3 of CLAUDE.md says a
proposition must carry. This is R69's root cause and the §3.2 violation in one line of code:
fixing the first fixes the second.

### 3.3 Grounding scope — the unregistered defect

`ground_document` over the two contracted corpus documents, against the same two shape files:

| document | records | `GroundedNode` | `PromotionDecision` | `iladub-shapes` | `dec-shapes` |
| --- | --- | --- | --- | --- | --- |
| graincorp-stem | 133 | 585 | 585 | conforms | **585 foci × 2** |
| cbh-stem | 58 | 134 | 134 | conforms | **134 foci × 2** |

```
[585 foci] optionSpace :: A real decision deliberates at least two options (the no-change option counts).
[585 foci] chosen      :: A decision must record exactly one chosen option.
```

**Every `iladub:PromotionDecision` iladub has ever produced on a real document fails
`dec:DecisionHolonShape`** — 719 of them, under the SHIPPED closure. Cause at
`ground.py:126-143` (`_emit_grounded`): it emits `reviews`, `decidedBy`, `consideredEvidence`,
`confidence`, `rationale`, `produced`, and neither `dec:optionSpace` nor `dec:chosen`.
`promote.py`'s three emitters (`:33`, `:70`, `:100`) have the identical shape.

`iladub-shapes.ttl` conforms **because `PromotionDecisionShape` requires only `iladub:reviews`
+ `dec:decidedBy` and delegates the decision mechanics to `dec-shapes.ttl`** — which is never
run. The two shape files are complementary halves; the missing half is the accountability half.

### 3.4 The one producer that is already right

`BandRecorder` (`decisionlog.py:44-47`) refuses `<2` options and a chosen-outside-options before
it writes. That is why all 769 recorder-minted decision holons across the corpus pass both
shape files under both closures. It is the existing proof that the fix is affordable, and the
design in §5 follows its discipline.

### 3.5 Premise types (R76)

**Evidence** (real documents, real compiles): §3.1, §3.2, §3.3 in full. **Fixture**:
`promote.py`'s three emitters are reached only under a BAML/Fake proposer and appear **zero**
times in the corpus measurement (`promotions=0` on all 7 compiled graphs). Their defect is read
off the code and their fix is disposed by unit tests, not by the corpus. This spec does not
claim corpus evidence for them.

## 4. The falsifiers

**O1 — the loop's oracle (corpus, end-to-end).** With both shape files in the compile membrane
and the grounding membrane, all 7 corpus documents compile and both contracted documents ground,
**conforming**. Falsified by any refusal. The before-state is §3: 26 refusing focus nodes at
compile scope, 719 at grounding scope. This oracle cannot be satisfied by editing a shape —
§5.6 forbids weakening the shapes, and the diff makes any such edit visible.

**O2 — per-fix falsification (CLAUDE.md plan rule 4).** Each of the three producer fixes ships a
test that fails when its subject is removed or inverted, with the failing output pasted in the
task report. No falsification evidence ⇒ the task review fails.

**O3 — the anti-decoration oracle.** An option space that always says the same thing is
decoration, not deliberation. For the grounding fix, the test asserts the **rejected** option
carries a `dec:rejectedBecause` that names the *actual* refusal path taken by
`_grounds_to` (no scheme member / value refused by the SHACL value membrane / bare proposal with
no oracle), and that inverting the branch inverts which option is `dec:chosen`. A fix that
hard-codes one option string fails O3 while passing O1.

**O4 — the closure differential is preserved.** After the change, `dec-shapes.ttl` under
`rdfs_closure` must ALSO conform on all 7 documents (§3.1 shows 96 RDFS-only refusals today, all
R69). This is the falsifier for "R69 is closed for consumers, not just for us" — a fix that only
satisfies the shipped closure passes O1 and fails O4.

## 5. The design

### 5.0 Gate classification (CLAUDE.md §8), stated before any code

- The three producer changes are **PROCEDURAL** — recording, in RDF, decisions the surrounding
  code has *already made*, introducing no new decision. This is the classification
  `decisionlog.py` carries verbatim ("PROCEDURAL engine glue. It makes no domain decision — it
  records ones already made at the call site"), and this spec inherits it on the same grounds.
  **The irreducibility argument is the option space's honesty condition** (§5.6): every option
  emitted must be read off an existing branch in the control flow. An option that is not a
  branch the code actually took or could have taken is invented, and inventing one would be a
  domain decision — which would make the change NEURAL or AXIOM and out of scope here.
- The two gate changes are **AXIOM / constraint → SHACL, closed world**: the contract membrane
  validating what crosses into the clean holon. This is the canonical §8 constraint form; the
  holon remains the closure boundary.
- **No tuned constant, tolerance, or geometric threshold appears anywhere in this loop.** If one
  appears in the implementation, that task is a review failure.

### 5.1 `escalate_region` emits a proposition, not a decision (R69 + §3.2)

`escalate_region(g, cand_uri, doc_uri, ascii_text, reason, anchor, confidence)` currently writes
`dec:confidence` and `dec:rationale` onto the candidate. **No `dec:` property may appear on an
`iladub:CandidateConcept`.** After the change the candidate carries, per
`iladub:CandidateConceptShape`:

- `iladub:confidence` — `xsd:decimal` in [0,1] (the same value, on the property whose domain is
  `iladub:CandidateConcept`; `iladub.ttl:96-97`).
- `iladub:suggestedBy` — a rule IRI typed `iladub:Suggester`, **one per escalation reason**
  (`ROUND_TRIP_FAIL`, `MULTI_TABLE_AMBIGUOUS`, `TRANSPOSED`, …), following the shipped precedent
  `_EXACT_RULE = "urn:iladub:suggester/exact-match-rule"` (`ground.py:22`). *This is where the
  reason goes.* A per-reason suggester IRI is strictly more queryable than the current
  `dec:rationale` string — "which rule proposed this" is now a join, not a `FILTER regex` — and
  it costs **no new vocabulary**. The human-readable reason stays on the candidate as
  `rdfs:label`, as `ground._emit_candidate` already does (`ground.py:91`).
  **Rejected alternative:** minting `iladub:rationale`. It would add a vocabulary term to carry
  a string the suggester identity already carries better, and §"Source ownership" discipline says
  we grow our namespaces for gaps, not for convenience.
- `iladub:fromRegion` — an `iladub:SourceRegion` node, following `ground.py:99-101`.
- `iladub:status iladub:proposed`.

**SEAM THE IMPLEMENTER MUST MEASURE, not assume.** `cand_uri` is `<doc>#region{idx}` at all 11
call sites (`compile.py:459,481,519,551,602,626,693,774,802,841` + `holon.py:399`) — the
candidate URI *is* the region-identified node, so `iladub:fromRegion` would be self-referential
if pointed at itself. **Measure** what identifies the source region at each call site, and mint
the `SourceRegion` as a node distinct from the candidate. Do **not** change `cand_uri` itself:
`_emit_unit_markers` and the escalation queries name it, and a URI change is a consumer break
this loop has no mandate for.

**SECOND SEAM.** §6 of CLAUDE.md is provenance to the page. **Measure whether `page` is in scope
at each call site before deciding what the `SourceRegion` carries.** A `SourceRegion` typed and
otherwise empty is a shape-satisfying stub — the exact failure mode §5.6 forbids. If `page` is
available, it is carried; if it is not at some call site, that call site is named in the task
report and the gap goes to the register rather than being papered over.

**MEASURED IMPACT ON EXISTING TESTS** (these read `DEC.rationale`/`DEC.confidence` on candidates
and will fail until updated — they are part of the change, not collateral):
`tests/etkl/test_holon.py:63,64,126,212`, `tests/etkl/test_closing_slice.py:109,155,236`,
`tests/etkl/test_merge_resolution.py:88`. Each becomes an assertion on `iladub:confidence` /
`iladub:suggestedBy` / `rdfs:label`. **A test that is merely deleted is a rule-4 failure.**

### 5.2 `emit_data_grid`'s admission holon becomes a real decision (R81 a′, b, c)

At `datagrid.py:684-698` the holon gains:

- **`dec:decidedBy`** naming `decisionlog._READER_AGENT` — the same automated reader that
  decided every verdict this admission supersedes. This is the identical fix the DOCUMENT driver
  already applies (`document.py`, R81's closed half); it moves to `emit_data_grid` so *every*
  admission holon carries it, whichever path minted it. **This is the only one of the three faces
  that the corpus currently refuses** (§3.1, ons p7/p8).
- **`rdfs:label` on the grid** — so `effective-chain.rq`'s `OPTIONAL { ?d dec:chosen/rdfs:label
  ?chosen }` binds and a consumer can read *what* replaced the superseded band, not merely that
  something did. The label must state what the grid *is* (its shape and page), not a constant
  string — a constant label binds `?chosen` while telling the consumer nothing, which is §5.6.
- **A no-change option, emitted unconditionally** — the option "refuse the page", carrying
  `dec:rejectedBecause` that names how much ink the grid actually read. This closes R81(c) for
  the refusal-free case *and* is the honest record in every case: refusing the page was always
  available, so the option belongs in the space whether or not any row was refused. Emitting it
  only when `grid.refusals` is empty would make the option space a function of the outcome,
  which is backwards.

`dec:chosen` remains the grid, which stays in the option space — `dec:DecisionHolonShape`'s
`sh:sparql` constraint (chosen ∈ optionSpace) must still hold.

### 5.3 The promotion emitters deliberate (§3.3 — the unregistered defect)

`ground._emit_grounded` and `promote.py`'s three emitters each gain a **two-option space read
off the branch the code already takes**:

- `dec:optionSpace` → the *ground-to-field* option and the *quarantine-as-proposition* option.
- `dec:chosen` → the branch actually taken.
- `dec:rejectedBecause` on the other, naming why: for `_emit_grounded` the refusal path in
  `_grounds_to` (`ground.py:106-123`) — no scheme member, value refused by the SHACL value
  membrane, or bare proposal with no oracle; for `promote.py`'s three, the reason its own
  `dec:rationale` already states in prose (the reshape round-trips / the tiling is legal but not
  unique / the reading is legal and lossless but not unique).

This is not invention: `ground_concept` (`ground.py:147-171`) *literally branches* on
`field is None` and then on `grounds_to is None`, and the two outcomes are `"grounded"` and
`"proposed"`. The option space names the branch that exists. Nothing about *how* grounding
decides changes — this loop adds no judgement and removes none.

**SEAM.** The options must be nodes (`dec:optionSpace`'s range is `dec:Option`), and `pd` is a
`BNode` in `_emit_grounded` and a `URIRef` in `promote.py`. **Measure both** before choosing the
option node's identity; a URIRef option hung off a BNode decision is not addressable.

### 5.4 The gates

**Compile scope.** `compile._validate` parses `dec-shapes.ttl` and `iladub-shapes.ttl` in
addition to the two tab shape files, and `_FULL_ONT` gains `dec.ttl` and `iladub.ttl` — the
subclass closure needs `iladub:PromotionDecision rdfs:subClassOf dec:DecisionHolon`
(`iladub.ttl:60-61`) or the promotion shapes never target anything.

**SEAM THE IMPLEMENTER MUST MEASURE.** Adding ontologies to `_FULL_ONT` enlarges the subclass
closure for the **tab** shapes too, which are validated in the same call. **Measure the tab-shape
verdict on all 7 documents before and after the ontology change, independently of the new shape
files.** If any tab verdict moves, that is a finding to report, not a thing to absorb.

**Grounding scope.** `ground_document` gains `validate_shapes: bool = True`, mirroring
`compile_tables`, and validates the graph it populated through the same `membrane.validate`
seam — the one place SHACL runs (`membrane.py` docstring). Grounding is where `GroundedNode` and
`PromotionDecision` exist at all (`grounded=0, promotions=0` on every compiled graph, §3.3), so
without this gate the differentiator's own shape stays vacuous no matter what §5.4's first half
does.

**The Python duplicate goes.** `tests/test_corpus.py:168-169` asserts
`len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1` in a Python loop — a hand-rolled
re-implementation of `iladub:GroundedNodeShape`. Under §8 the shape is the decision and the
Python that re-states it is the defect. It is replaced by the membrane verdict.

**Order of work is not negotiable** (this is the "hard gate after the corpus is clean" decision):
producers first, corpus measured green, gates last. Wiring the gate first would turn every
pre-existing violation into a compile crash and conflate "the code is wrong" with "the shape
overreaches on compiled evidence" — the distinction R82 asks the loop to make.

### 5.5 What the gate does on refusal

`_validate`'s existing contract is unchanged: non-conformance raises `AssertionError`
(`compile.py:1035-1037`). A malformed decision holon becomes a **failed compile**, not a warning.
That is the point: after this loop, an under-furnished decision cannot reach a consumer.

### 5.6 The constraint that governs every fix: no stub-to-satisfy

Every triple this loop adds must carry information a consumer can act on. A `SourceRegion` with
nothing but a type, a constant `rdfs:label`, an option space whose second member is always the
same string — each of these turns a red shape green while leaving the graph exactly as
uninformative as before, which is the failure this loop exists to correct, re-committed one
level down. **If the honest answer is "we cannot say", the shape is wrong or the data is
missing** — say so in the task report and register it. Do not invent a value to pass a shape.

## 6. Verification

The reproduction commands, to be re-run after each producer fix and once at the end:

```
# compile scope, all 7 documents, both shape files, both closures
./.venv/bin/python scripts/measure_dec_membrane.py --scope compile
# grounding scope, the two contracted documents
./.venv/bin/python scripts/measure_dec_membrane.py --scope grounding
# the shipped batteries
./.venv/bin/python -m pytest -q
./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -s
```

The measurement harness this spec used is loop evidence written to the scratchpad; the
implementer promotes it to `scripts/measure_dec_membrane.py` so O1 and O4 are reproducible by
anyone, not just by this session. It reports per-document, per-shape-file, per-closure counts —
the §3 tables regenerated.

Expected end state, stated as numbers so it can be falsified: **compile scope 0 refusals on 7/7
documents under BOTH closures; grounding scope 0 refusals on 2/2 documents under BOTH closures.**

Today, counted two ways (focus nodes / validation results, both shape files summed):

| scope | closure | refusing focus nodes | validation results |
| --- | --- | --- | --- |
| compile (7 docs) | SHIPPED | 26 | 98 |
| compile (7 docs) | RDFS | 26 | 194 |
| grounding (2 docs) | SHIPPED | 719 | 1438 |
| grounding (2 docs) | RDFS | 719 | 1438 |

The focus-node count is identical across closures at compile scope by coincidence of arithmetic,
not by mechanism: the SHIPPED 26 are 24 candidates (`iladub-shapes`) + 2 admission holons
(`dec-shapes`), while the RDFS 26 are the same 24 candidates refusing under BOTH shape files
plus the same 2 admission holons. The results column is where the closure difference shows.

## 7. What is NOT done here

- **The 1265 + 775 quarantined concepts get no decision holon.** A refusal to promote is
  arguably an accountable act too (§4), but "a proposition enters the grounded graph only as the
  product of a promotion decision" does not require a decision for *non*-entry, and minting
  ~2000 more holons is a separate slice with its own cost measurement. Registered as a residue.
- **R66 (thin option spaces) is not closed.** This loop makes every option space *exist* and be
  *honest*; it does not make any of them richer than the branch the code takes. A two-option
  space that names a real branch is not thin — it is exact. Where the code genuinely deliberates
  more (a proposer that ranked several contract fields), the alternatives are not currently
  returned by `propose_ground`, which is R66's plumbing and stays R66's.
- **`dec:confidence`'s `rdfs:domain` is not narrowed.** §5.1 removes the property from
  candidates instead. The vocabulary is not weakened to accommodate a code defect.
- **`promote.py`'s three emitters have no corpus evidence** (§3.5). Their fix is disposed by unit
  tests. The task report says so explicitly rather than implying corpus coverage.
- **`escalation-shapes.ttl` is not added to the membrane.** Measured clean on apple p0 under both
  closures, but unmeasured on the other six; adding it is a one-line follow-on once measured.

## 8. What this loop records

- **R69 → closed** by §5.1, with O4 as the evidence that it is closed for consumers and not only
  for the shipped closure.
- **R81 → closed** by §5.2, all three remaining faces.
- **R82 → closed** by §5.4, with §3 as the "record what it refuses" the register asked for.
- **New rows** for: the quarantine-decision gap (§7), any call site where `page` is not in scope
  for the `SourceRegion` (§5.1), and `escalation-shapes.ttl`'s unmeasured six documents (§7).
- **The wiki contradiction** (`promotion-decision.md`, `decision-holon.md`) is resolved in the
  same change that makes the assertion true, and both pages gain the *where* — a claim about
  enforcement that does not name the call site is how this one survived.

## 9. Plan discipline for the implementation

This spec is a contract. The plan derived from it carries **no function bodies** (CLAUDE.md
§ "Plan authoring discipline" rule 1); every load-bearing claim about existing code in that plan
is measured inline with `file:line`, the command, and its output (rule 2); the three seams §5.1,
§5.3 and §5.4 name *what must be measured*, never the answer (rule 3); and every task report
carries a `## FALSIFICATION` block (rule 4). The five defects of the R73 plan are the worked
counter-example — in particular defect 2 (an ordering assumed from reading, not measured), which
§5.4's `_FULL_ONT` seam is the direct analogue of.
