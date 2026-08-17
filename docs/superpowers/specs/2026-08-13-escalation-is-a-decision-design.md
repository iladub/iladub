# Escalation is a decision — closing R87

**Date:** 2026-08-13
**Author:** François Rosselet
**Residue closed:** R87 (`escalation-shapes.ttl` is in NO membrane)
**Baseline:** `main` at `06fe726` (PR #104, the one-engine membrane)

Doc impact: increment

---

## 1. R87's premise does not survive measurement

R87's row instructs: *"Parse `escalation-shapes.ttl` into `compile._validate`'s pinned leg."*
Following that instruction literally would produce a **vacuous** membrane — a shape wired in that
cannot fire, for reasons no measurement in the row's history had looked for.

The row conflates two unrelated senses of *escalate*:

- `escalation-shapes.ttl`'s `dec:EscalationShape` validates **apex severity escalation** — a decision
  whose `dec:constrainedBy` severity exceeds its `dec:withinScope` → `dec:maxSeverity` ceiling must
  carry `dec:escalatedTo` (`vocab/shapes/escalation-shapes.ttl:16-31`).
- What a *compile* escalates is a **region**, via `holon.escalate_region`
  (`src/iladub/etkl/holon.py:424`), which emits none of those predicates.

Three measurements, all run 2026-08-13 at `06fe726`:

**M1 — the pipeline emits none of the vocabulary the shape reads.**

```
$ grep -rn "constrainedBy\|withinScope\|escalatedTo" src/iladub/etkl/
(no output)
```

The entire document-compile pipeline never emits any of the three predicates
`dec:EscalationShape`'s SPARQL body needs. The body cannot match — by construction, not by luck.

**M2 — the only producer of that vocabulary is never called from `src/`.**
`iladub.escalate.escalate()` (`src/iladub/escalate.py:34`) is the sole emitter of
`dec:constrainedBy` + `dec:withinScope` + `dec:escalatedTo`. Its only callers are
`tests/test_escalate.py:34,48,49,61`. It belongs to the transplant/M4 showcase track.

**M3 — neither membrane loads `risk.ttl`.** `compile._build_membrane` parses `tab.ttl` + `dec.ttl` +
`iladub.ttl` (`src/iladub/etkl/compile.py:419-431`); `feed._GROUND_ONT_FILES` is `("iladub.ttl",
"dec.ttl")` (`src/iladub/feed.py:587`). The shape's `SELECT` compares `?sev risk:order ?so` against
`?ceil risk:order ?co`. With `risk.ttl` absent from the ontology graph, `?so`/`?co` bind nothing and
the `FILTER (?so > ?co)` never fires — so the shape would be vacuous **twice over**.

**Therefore R87's evidence was misread.** Its recorded "(conforms=True, 0 refusing focus nodes, 0
results) … TOTAL 0 / 0" across all seven corpus documents is not evidence that the shape is *safe to
wire in*. It is evidence that the shape is **inert on that graph, and stays inert under every
possible document**. Wiring it as the row instructs makes the enforcement claim formally true while
nothing can ever trigger it — the failure mode CLAUDE.md's "honest failure > fake success" rule
exists to forbid.

## 2. What the measurement found instead — the repair is small and vertical

**M4 — every escalation site already mints a proper escalation decision.** Beside each
`escalate_region` call sits a `BandRecorder` judgement:

```python
brec.record("verdict", ["asserted", "escalated", "ignored"], "escalated", REASON)
```

at **17 call sites** — `src/iladub/etkl/compile.py:514, 531, 574, 592, 606, 644, 657, 681, 694, 735,
748, 790, 816, 829, 857, 876, 898`. That produces a `dec:DecisionHolon` with a URIRef subject, an
option space of three, exactly one chosen option, an accountable agent and a rationale
(`src/iladub/etkl/decisionlog.py:50-68`).

Not all 17 choose `escalated` — `:531` chooses `"ignored"`, and several choose `"asserted"`. **The
derivation must key on the chosen option, never on the call site**, which is precisely why §4.1
matches on `rdfs:label` rather than enumerating emitters. M5's count of 32 is the number of
*decisions that chose escalation*, not the number of call sites.

This node is **distinct from the `iladub:CandidateConcept`**, which is load-bearing: R69 is the
shipped publication defect in which `dec:` properties on the candidate itself entailed (via
`dec:confidence`'s `rdfs:domain dec:DecisionHolon`) that every escalated region *was* a decision
holon, and then failed it against `dec:DecisionHolonShape` for having no option space, no chosen
option and no agent (`src/iladub/etkl/holon.py:433-441`). **Nothing in this spec puts a `dec:`
property on a candidate.** Furnishing happens on the verdict decision, which is already a decision
holon and already passes `dec:DecisionHolonShape`.

**M5 — the corpus census.** `scripts/measure_dec_membrane.py`'s helpers (`manifest_entries`,
`compiled_graph`, `_closed(…, "SHIPPED")`), all 7 corpus documents compiled and subclass-closed:

| document | `dec:DecisionHolon` | `chosen` = escalated | constrainedBy / withinScope / escalatedTo / maxSeverity |
| --- | --- | --- | --- |
| apple-fy2026q3-statements | 119 | **15** | 0 / 0 / 0 / 0 |
| bfs-population-bilan-2023 | 232 | **10** | 0 / 0 / 0 / 0 |
| cbh-stem-2026-08-03 | 65 | **4** | 0 / 0 / 0 / 0 |
| graincorp-capacity-2026-08-04 | 18 | 0 | 0 / 0 / 0 / 0 |
| graincorp-stem-2026-07-31 | 36 | 0 | 0 / 0 / 0 / 0 |
| ons-index-of-services-2026-02 | 218 | 0 | 0 / 0 / 0 / 0 |
| who-wfa-boys-zscore-0-5 | 81 | **3** | 0 / 0 / 0 / 0 |
| **total** | **769** | **32**, over 4 of 7 documents | **0 / 0 / 0 / 0** |

So the escalation decision exists 32 times over. What it lacks is exactly the three predicates the
shape reads. **The repair is to furnish a decision that already exists, then wire the shape into a
membrane where it now has something to say.**

Three documents carry **zero** escalations. Any oracle for this work must therefore select a
document that escalates; a test written against `graincorp-stem` or `ons` would pin nothing.

## 3. The vacuity finding that generalizes

**M6 — `dec:EscalationShape` is not focus-node-idle; it is BODY-idle.** Wired against the corpus it
would receive **769 focus nodes** (it targets `dec:DecisionHolon`, of which there are 769) and bind
**zero** rows. A guard that counted focus nodes alone would have pronounced it healthy.

**M7 — 10 shapes already wired into the compile membrane are idle corpus-wide** (0 focus nodes on
all 7 documents):

| shape | target | why (measured / to be adjudicated) |
| --- | --- | --- |
| `iladub:GroundedNodeShape` | `iladub:GroundedNode` | grounding-scope; live at `feed._validate_grounding`, correctly idle at compile |
| `iladub:PromotionDecisionShape` | `iladub:PromotionDecision` | same |
| `dec:EventShape` | `dec:Event` | transplant-track; **goes live under this spec** (see §4.4) |
| `dec:ExpansionRequestShape` | `dec:ExpansionRequest` | transplant-track; **goes live under this spec** |
| `dec:MilestoneShape` | `dec:Milestone` | transplant-track; stays idle |
| `tab:AggregationCellShape` | `tab:AggregationCell` | corpus does not exercise it |
| `tab:BaseFactShape` | `tab:BaseFact` | corpus does not exercise it |
| `tab:LicenceRefusalShape` | `tab:licenceRefused` | corpus does not exercise it |
| `tab:PivotedDimensionShape` | `tab:PivotedDimension` | corpus does not exercise it |
| `tab:SectionTotalShape` | `tab:SectionTotal` | corpus does not exercise it |

A blanket assertion "every wired shape must be non-idle" therefore **fails 10 times today** and
cannot ship as written. The guard must be a *registry*, not a universal (§4.5).

## 4. What ships

### 4.1 Furnish the escalation decision — AXIOM

A derivation query, `vocab/queries/escalation-furnish.rq`, `CONSTRUCT` form. Its contract:

**Matches** every `?d a dec:DecisionHolon` such that `?d dec:chosen ?o` and `?o rdfs:label
"escalated"`. The match is on the **option's label**, never on a URI suffix: `BandRecorder` mints
`rdfs:label` on every option (`src/iladub/etkl/decisionlog.py:61`), and the URI shape
`{d}-opt-{slug}` is an implementation detail no query may depend on.

**Derives**, for each match:

- `?d dec:constrainedBy risk:Breach`
- `?d dec:withinScope etkl:readerScope`
- `?d dec:escalatedTo ?req`, where `?req` is the expansion request for that decision
- `?req a dec:ExpansionRequest`
- `?req dec:regarding ?r`, where `?r` is the decision's own `dec:regarding` (the region)
- `?req dec:condition` — a literal naming the reading failure

**Invariants the implementer must preserve:**

1. **Open-world and evidence-positive.** The query derives only where an escalated choice is
   *present*. Nothing is inferred from the absence of a triple (CLAUDE.md §8, §7).
2. **Monotonic and idempotent.** Running it twice adds nothing the first run did not.
3. **Nothing is written onto an `iladub:CandidateConcept`.** R69 (§2).
4. **`?req`'s identity is derived from `?d`, not minted randomly**, so the derivation is a pure
   function of the graph. Whether `?req` is a URIRef built from `?d` or a blank node is the
   implementer's call — but note the membrane skolemizes (`membrane._payload_nt`, PR #104), so a
   blank node is no longer a hazard, and `dec:EscalationShape` carries `sh:sparql`.
5. **A decision with no `dec:regarding` must derive no request at all**, rather than a request with
   no subject matter. MEASURE whether every verdict decision carries `dec:regarding` before
   choosing between "skip it" and "it cannot happen"; `BandRecorder.record` writes it
   unconditionally at `decisionlog.py:52`, but the load-bearing claim is about the *graph*, not the
   writer.

**Gate classification (CLAUDE.md §8): AXIOM, derivation form.** A `CONSTRUCT` over an RDF evidence
graph, open world. It is not PROCEDURAL: no geometry, no arithmetic, no tolerance. It is not
NEURAL: nothing is underdetermined — the reading judgement was already made and recorded; this
states its consequence.

**Where it runs** is the implementer's seam to measure, not the spec's to assert. Name the
constraint: the derived triples must be in the graph *before* `compile._validate` runs, and must be
part of the document graph the membrane sees — not a region scratch graph (the R19 hazard recorded
at `decisionlog.py:12`). MEASURE which call site satisfies both before writing it.

### 4.2 Vocabulary — owned namespaces only

`etkl:readerScope`, an autonomy scope carrying `dec:maxSeverity risk:Watch`, declared in
`vocab/ontology/etkl.ttl`. One severity for every region escalation: *beyond local autonomy* is what
escalation means, so there is no per-case judgement, no mapping table, and no tuned constant. Per-
reason severity remains addable later as pure vocabulary data with no code change (§7).

`risk:Breach` and `risk:Watch` are `risk:Severity` instances with `risk:order` 2 and 1
(`vocab/ontology/risk.ttl:64,66`) — so `?so > ?co` holds and the shape fires.

Source ownership (CLAUDE.md § Source ownership): `etkl:` and `dec:` and `risk:` are ours; every new
triple's subject is a term we own. No HGA IRI appears.

### 4.3 Membrane wiring

- `risk.ttl` joins the ontology graph built by `compile._build_membrane`
  (`src/iladub/etkl/compile.py:418-432`). Without it the shape is vacuous by M3.
- `escalation-shapes.ttl` joins `_DEC_SHAPE_FILES` (`src/iladub/etkl/compile.py:399`).
- **Compile leg only.** Grounding decisions are `iladub:PromotionDecision`s whose chosen option is
  never "escalated", so the shape has nothing to say at `feed._validate_grounding`. Wiring it there
  would re-create exactly the vacuity this spec repairs.

Enlarging the ontology graph enlarges the closure **both** legs see. `compile.py:425-429` records
that this was measured once before (adding `dec.ttl` + `iladub.ttl` moved no tab verdict). That
measurement does not transfer to `risk.ttl`: **re-measure every corpus verdict, both legs, with and
without `risk.ttl` in `_FULL_ONT`**, and state the result. Do not assume.

### 4.4 A constraint this creates

`dec:ExpansionRequest rdfs:subClassOf dec:Event` (`vocab/ontology/dec.ttl:197-198`). Under subclass
closure every minted request is therefore also a `dec:Event`, and `dec:EventShape` requires
**exactly one** `dec:condition` (`vocab/shapes/dec-shapes.ttl:61-65`), while
`dec:ExpansionRequestShape` requires at least one `dec:regarding` (`:72-75`). Both are already wired
into the compile membrane and both are idle today (M7). The emission must satisfy them from the
first commit, or the membrane refuses every escalating document.

`dec:regarding`'s domain is already `owl:unionOf(dec:DecisionHolon, dec:ExpansionRequest)`
(`vocab/ontology/dec.ttl:204`) — the widening has **shipped on `main`**, so the comment at
`src/iladub/etkl/decisionlog.py:92-93` calling it "widened on this branch only" is stale. Correct it
in passing.

### 4.5 The vacuity registry — the generalized guard

A test that, for every shape wired into either membrane, measures two things on real corpus graphs:

1. **focus-node count** (targets resolved: `sh:targetClass`, `sh:targetSubjectsOf`,
   `sh:targetObjectsOf`), and
2. for every shape carrying `sh:sparql`, **whether the body's non-negated patterns bind ≥ 1 row**.
   M6 is why: 769 focus nodes and zero bindings is the R87 defect, and criterion 1 alone declares it
   healthy.

A shape that is idle by either criterion must appear in a **registry with a measured reason**. The
test fails when a shape is idle and **unregistered**, and equally when a shape is registered and has
become **live** — a stale registration is how a guard rots into a rubber stamp.

The registry is seeded with the 10 rows of M7 plus their reasons. **Each of the five
"corpus-does-not-exercise-it" rows raises a residue** — a shape validating a feature no corpus
document exercises is either a corpus gap or a dead shape, and this spec does not adjudicate which.

**Placement:** the default install must run it. `tests/etkl/test_membrane_equiv.py` is skipped
wholesale without `pyrudof`, which is not a core dependency; put this beside
`tests/etkl/test_membrane.py`. (Same trap as R92 and the parity oracle — the default install is the
failing side.)

**Cost:** the guard needs compiled corpus graphs. `-m corpus` is the right marker; the fast suite
must not grow a 5-minute dependency. State the measured runtime in the task report.

## 5. Falsifying oracles

Per CLAUDE.md plan-authoring rule 4, each is mandatory and each must be shown **failing** before it
is shown passing.

- **O1 — the shape is live.** On a document that escalates (apple, bfs, cbh-stem or who-wfa — never
  graincorp/ons, which have zero escalations by M5), remove `dec:escalatedTo` from one escalated
  decision. The compile membrane must **refuse** the page. Restore; the suite is green.
- **O2 — the guard catches R87 itself.** Remove the furnishing derivation while leaving
  `escalation-shapes.ttl` wired. `dec:EscalationShape`'s body-bindability drops to 0 and the vacuity
  registry test must **fail**. This is the oracle whose absence let R87 be filed as "0 violations,
  nothing to do."
- **O3 — no verdict moved.** Every corpus document's compile verdict, both legs, before and after
  `risk.ttl` enters `_FULL_ONT` (§4.3).
- **O4 — the batteries.** Corpus `-m corpus` 36 passed; fast suite 1152 passed / 7 skipped /
  1 xfailed; both also green under `ILADUB_MEMBRANE=rudof`. Baselines at `06fe726`.

O1 and O2 are complementary and neither substitutes for the other: O1 proves the shape refuses when
the graph is wrong; O2 proves the *guard* refuses when the shape is toothless. R87 existed because
only the first kind of oracle was ever written.

## 6. Why this is iladub's signature, not a chore

CLAUDE.md §4: *a promotion is a decision holon* — admitting a proposition is an accountable,
agent-attributed act. Its mirror is that **refusing** to read a region is also a decision, and one
that by definition exceeds the reader's autonomy: the compiler is saying *I cannot settle this*.
Until now that act was recorded as a bare verdict with no authority relation at all. After this
loop, a region the compiler could not read names, in RDF, the severity it realized, the autonomy
scope it exceeded, and the human-addressed request it escalated to — and a membrane refuses the
document if it does not.

The `dec:ExpansionRequest` is the right apex precisely because there is **no automated higher
authority** for a reading failure. dec.ttl already describes it as the evidence-positive third
outcome — *"say I don't know in a voice that can't be mistaken for no"* (`dec.ttl:189-200`).

## 7. What is deliberately NOT done

Read this section against every plan-supplied test before it ships (CLAUDE.md plan rule 5).

- **Grounding-portal refusals still mint no decision holon.** That is **R86** — 2040 quarantined
  concepts across the two contracted corpus documents, measured, unattributed. This spec touches the
  *compile*-side refusal only. **No test in this loop may assert that a quarantined concept, a
  refusing `ground_concept` call, or a proposed candidate carries a decision holon, an escalation,
  or an expansion request. It does not, by design.**
- **Per-reason severity is not adjudicated.** Every escalation realizes `risk:Breach`. No test may
  assert that MULTI_TABLE_AMBIGUOUS and ROUND_TRIP_FAIL differ in severity — they do not.
- **The 10 idle shapes are registered, not repaired.** No test may assert that
  `tab:SectionTotalShape` (or the other four corpus-not-exercised shapes) has focus nodes.
- **`dec:MilestoneShape` stays idle.** The transplant/M4 track keeps its ad-hoc validation; giving
  that track a real membrane was the alternative repair considered and not chosen.
- **`escalation-shapes.ttl` is not wired into the grounding membrane** (§4.3).
- **No change to what escalates.** This loop moves no region from asserted to escalated or back. If
  a corpus escalation count moves, that is a defect, not a feature — O3 covers it.

## 8. Residue accounting

Closes **R87**. Register stands at **86 rows, 17 closed** at loop start (`06fe726`).

Expected new rows: the five corpus-not-exercised shapes (§4.5), one row or five at the
implementer's discretion, each recording its measured focus count of 0.

Not closed and explicitly untouched: **R86**, **R89**, **R61**, **R95**, **R96**.
