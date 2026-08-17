# Escalation is a decision — implementation plan (R87)

**Date:** 2026-08-15
**Branch:** `loop-escalation-is-a-decision`, HEAD `401e0d6`, tree clean
**Spec:** `docs/superpowers/specs/2026-08-13-escalation-is-a-decision-design.md`
**Ruling:** `docs/superpowers/2026-08-15-r87-ruling-handoff.md` §3 (option (d) accepted; §4.3 bullet 1 rejected)
**Residue closed:** R87
**Doc impact:** increment

Every `file:line` below was re-measured on this branch at `401e0d6`. The commands are inline
(plan rule 2). **Do not cite the handoffs as a source** — they were the deliberation, not the
evidence.

---

## Global Constraints

**G1 — §8 gate.** The furnishing derivation is **AXIOM, derivation form**: a SPARQL `CONSTRUCT`
over an RDF evidence graph, open world, monotonic, evidence-positive. It is not PROCEDURAL (no
geometry, no arithmetic, no tolerance) and not NEURAL (nothing is underdetermined — the reading
judgement was already made and recorded; this states its consequence). The only Python this loop
may add is **engine glue**: the call to `interpret.run` and a named constant naming the vocabulary
files. Any Python that *decides* something about escalation is a defect.

**G2 — `risk.ttl` does NOT join `_FULL_ONT`.** Spec §4.3's first bullet is **rejected**. The
ontology graph is read for exactly one thing, and `risk.ttl` has nothing to contribute to it:

```
$ nl -ba src/iladub/etkl/membrane.py | sed -n '448,456p'
   448	def subclass_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
   449	    """A NEW graph: the data plus its own rdfs:subClassOf type closure. Nothing else.
   450	
   451	    The ontology is READ for its `rdfs:subClassOf` axioms and never mixed in, so no ontology
   452	    node can become a focus node and the validated graph is data plus its type closure.

$ nl -ba src/iladub/etkl/membrane.py | sed -n '477,478p'
   477	    for a, _, b in ont_graph.triples((None, RDFS.subClassOf, None)):
   478	        supers.setdefault(a, set()).add(b)

$ grep -c "subClassOf\|subPropertyOf" vocab/ontology/risk.ttl
0
(exit status 1 — no matches)
```

`ont_graph` is consulted at `membrane.py:477` for `rdfs:subClassOf` only; the data graph is copied
through at `:490-493` and the closure added at `:494-498`, with no merge of the ontology. `risk.ttl`
carries zero `rdfs:subClassOf` axioms, so adding it to `_FULL_ONT` contributes **0 triples** to the
validated payload. The payload is byte-identical with and without it.

**Consequence for O3.** Spec §5's O3 is written against a change this plan does not make ("before
and after `risk.ttl` enters `_FULL_ONT`"). It is **restated** in Task 4: every corpus document's
compile verdict, both legs, before and after *the derivation plus the shape wiring*. O3 is not
dropped — it is re-pointed at the change that actually happens.

**G3 — the four conditions on option (d).** The derivation carries three vocabulary triples into
the document data graph. That is licensed only under all four:

1. Ordinals are **bound from `risk.ttl` as a query input, never written as literals**. This is the
   whole difference from the rejected option (b), so it must be a **testable property**, not a
   convention (Task 2, T2.3).
2. The `.rq` file carries an explicit note stating the licence and its boundary (Task 2, T2.5).
3. A test pins the carry is **bounded** — exactly the triples the shape reads, no more. "Merge
   `risk.ttl`" must fail it as surely as asserting nothing does (Task 2, T2.4).
4. **O3 re-run against the real change** (Task 4).

**G4 — spec §7, read before every test ships** (plan rule 5). No test in this loop may assert:

- that a quarantined concept, a refusing `ground_concept` call, or a proposed candidate carries a
  decision holon, an escalation or an expansion request (that is **R86**, untouched);
- that two escalation reasons differ in severity (every escalation realizes `risk:Breach`);
- that `tab:SectionTotalShape` or the other four corpus-not-exercised shapes have focus nodes;
- that `dec:MilestoneShape` is live;
- that `escalation-shapes.ttl` is wired into the **grounding** membrane;
- that any region moved between asserted and escalated. **If a corpus escalation count moves, that
  is a defect, not a feature.**

**G5 — nothing is written onto an `iladub:CandidateConcept`** (R69, spec §2). Furnishing happens on
the verdict decision holon, which already passes `dec:DecisionHolonShape`.

**G6 — source ownership.** `etkl:`, `dec:` and `risk:` are ours
(`etkl.ttl:1` `<https://w3id.org/iladub/etkl#>`, `risk.ttl:1` `<https://w3id.org/iladub/risk#>`).
Every new triple's subject is a term we own. No HGA IRI appears.

**G7 — no implementation source in this plan** (plan rule 1). Test **contracts** are given —
setup, assertion, and the measured proof the setup is constructible — but no verbatim test bodies
and no function bodies. Defect 5 and defect 6 in `CLAUDE.md:284-373` were both plan-supplied
artefacts; this plan declines the permission so that every test is falsified by the person who
wrote it. **Every task report carries a `## FALSIFICATION` block** (plan rule 4).

---

## The two decisions this plan does NOT make

Both are named as MEASURE seams (plan rule 3). The ruling deliberately left them open; answering
them from reading is the failure this rule exists to prevent.

**S1 — where the derivation runs.** Task 3. Three measured constraints, no answer.

**S2 — whether the `dec:escalatedTo` range widening ships this loop or as its own residue.**
Task 1. The ruling settled *what* the widening is, not *when* it ships.

---

## File Structure

| file | action | task |
| --- | --- | --- |
| `vocab/ontology/etkl.ttl` | edit — declare `etkl:readerScope` | 1 |
| `vocab/ontology/dec.ttl` | edit **or defer** — widen `dec:escalatedTo`'s range (S2) | 1 |
| `src/iladub/etkl/decisionlog.py` | edit — correct the stale comment at `:91-93` | 1 |
| `vocab/queries/escalation-furnish.rq` | **new** — the derivation | 2 |
| `tests/etkl/test_escalation_furnish.py` | **new** — derivation contract, offline | 2 |
| `src/iladub/etkl/compile.py` | edit — the vocabulary constant, the derivation call site (S1), `_DEC_SHAPE_FILES` | 2, 3, 4 |
| `src/iladub/etkl/document.py` | edit **or not** — depends on S1 | 3 |
| `tests/etkl/test_vacuity_registry.py` | **new** — the generalized guard | 5 |
| `docs/superpowers/residues-open.md` | edit — strike-and-move R87, raise the new rows | 6 |
| `docs/superpowers/residues-closed.md` | edit — receive R87 | 6 |
| `docs/superpowers/residues.md` | edit — `:32` census, `:136` R87 row | 6 |
| `docs/wiki/concepts/decision-holon.md` | edit — increment (`:7`, `:51` already name the shape) | 6 |

---

## Task 1: The vocabulary — `etkl:readerScope`, typed and ceilinged

### Goal

Declare the one autonomy scope every region escalation exceeds, so that `dec:EscalationShape`'s
`?scope dec:maxSeverity ?ceil` has something to bind.

### Measured

`etkl:readerScope` does not exist anywhere in the tree:

```
$ grep -n "readerScope" -r vocab/ src/ tests/
(no output; exit status 1 — no matches anywhere)

$ wc -l vocab/ontology/etkl.ttl
     161 vocab/ontology/etkl.ttl
```

**Two declarations force the type, not one.** The ruling named `dec:maxSeverity`'s domain; there is
a second constraint on the other side:

```
$ nl -ba vocab/ontology/dec.ttl | sed -n '113,114p'
   113	dec:withinScope a owl:ObjectProperty ;
   114	    rdfs:label "within scope"@en ; rdfs:domain dec:DecisionHolon ; rdfs:range dec:Scope ;

$ nl -ba vocab/ontology/dec.ttl | sed -n '216,218p'
   216	dec:maxSeverity a owl:ObjectProperty ;
   217	    rdfs:label "max severity"@en ; rdfs:domain dec:Scope ;
   218	    rdfs:comment "The highest severity the scope's holder may resolve within its own autonomy; a realized severity above it must be escalated. The filler is an ordinal severity resource (in practice a risk:Severity) — dec stays standalone, so the range is left open."@en .
```

`etkl:readerScope` is the **object** of `dec:withinScope` (range `dec:Scope`, `dec.ttl:114`) and the
**subject** of `dec:maxSeverity` (domain `dec:Scope`, `dec.ttl:217`). It must be typed
`a dec:Scope` or it sits outside two declared boundaries at once. `dec:maxSeverity` has **no**
`rdfs:range` — deliberately, per its own comment — so `risk:Watch` as filler asserts nothing out of
bounds.

The ceiling and the severity above it:

```
$ nl -ba vocab/ontology/risk.ttl | sed -n '64,67p'
    64	risk:Watch    a risk:Severity ; rdfs:label "watch"@en    ; risk:order 1 ;
    65	    rdfs:comment "Monitor; not yet actionable."@en .
    66	risk:Breach   a risk:Severity ; rdfs:label "breach"@en   ; risk:order 2 ;
    67	    rdfs:comment "A threshold/rule is breached in this context; actionable here."@en .
```

`2 > 1`, so `FILTER (?so > ?co)` fires once both ordinals are bound.

### What ships

`etkl:readerScope`, declared in `vocab/ontology/etkl.ttl`:

- `a dec:Scope`
- `dec:maxSeverity risk:Watch`
- `rdfs:label`, `rdfs:comment` in the house style of the file's existing terms

**One severity for every region escalation.** *Beyond local autonomy* is what escalation means, so
there is no per-case judgement, no mapping table and no tuned constant (spec §4.2, and G1 — a tuned
constant here would be prima facie evidence the decision belongs in AXIOM). Per-reason severity
stays addable later as pure vocabulary data with no code change.

`etkl.ttl` will need `dec:` and `risk:` prefixes; today it declares neither:

```
$ grep -n "prefix\|PREFIX" vocab/ontology/etkl.ttl | head -20
1:@prefix etkl:   <https://w3id.org/iladub/etkl#> .
2:@prefix owl:    <http://www.w3.org/2002/07/owl#> .
3:@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
4:@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
5:@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
6:@prefix dcterms:<http://purl.org/dc/terms/> .
7:@prefix prov:   <http://www.w3.org/ns/prov#> .
8:@prefix vann:   <http://purl.org/vocab/vann/> .
```

The reverse direction already exists — `risk.ttl:2` declares `@prefix etkl:` — so this is not a new
cross-file dependency, only the other half of one.

### Also in this task: the stale comment

```
$ nl -ba src/iladub/etkl/decisionlog.py | sed -n '91,93p'
    91	        # Page is a dec:Process, not a decision. NO dec:regarding here (final-review I5):
    92	        # dec:regarding's rdfs:domain is dec:DecisionHolon (widened on this branch only to
    93	        # unionOf(dec:DecisionHolon, dec:ExpansionRequest)), and a dec:Process is neither —
```

"widened on this branch only" is false — the widening shipped:

```
$ nl -ba vocab/ontology/dec.ttl | sed -n '202,206p'
   202	dec:regarding a owl:ObjectProperty ;
   203	    rdfs:label "regarding"@en ;
   204	    rdfs:domain [ a owl:Class ; owl:unionOf ( dec:DecisionHolon dec:ExpansionRequest ) ] ;
   205	    rdfs:range prov:Entity ;
```

Correct the comment. The substantive claim it makes (a `dec:Process` is neither, so no
`dec:regarding` on a container) is unaffected and stays.

### S2 — MEASURE seam: does the range widening ship this loop?

The ruling settled the *shape* of the widening:

```
$ nl -ba vocab/ontology/dec.ttl | sed -n '212,214p'
   212	dec:escalatedTo a owl:ObjectProperty ;
   213	    rdfs:label "escalated to"@en ; rdfs:domain dec:DecisionHolon ; rdfs:range dec:DecisionHolon ;
   214	    rdfs:comment "This decision escalated the matter to a higher-authority decision because the local decision's autonomy scope was insufficient to resolve it (authority-holarchy lineage; the vertical analog of dec:supersedes)."@en .
```

becomes `rdfs:range [ a owl:Class ; owl:unionOf ( dec:DecisionHolon dec:ExpansionRequest ) ]`, on
the precedent of `dec:regarding` at `:204`. It is needed because the derivation asserts
`?d dec:escalatedTo ?req` where `?req a dec:ExpansionRequest`, and:

```
$ nl -ba vocab/ontology/dec.ttl | sed -n '197,198p'
   197	dec:ExpansionRequest a owl:Class ;
   198	    rdfs:subClassOf dec:Event ;
```

— `dec:Event`, not `dec:DecisionHolon`.

**MEASURE before choosing, do not decide from reading.** Nothing appears to enforce the range today
(`subclass_closure`'s docstring at `membrane.py:458-465` says it deliberately does no domain/range
typing), but "appears" is the class of claim rule 2 exists to punish. Run:

```
grep -rn "escalatedTo" vocab/shapes/
grep -rn "sh:class\|sh:node\|rdfs:range" vocab/shapes/ | grep -i "escalat"
```

- **If no wired shape reads `dec:escalatedTo`'s range**, the widening moves no verdict. It is then a
  one-line vocabulary commit that can ship in this task at zero O3 cost — ship it here, and say in
  the task report that it was measured inert.
- **If any shape does read it**, the widening is verdict-moving. Do **not** ship it in this task:
  raise it as its own residue, stamped per Task 6's convention, and record the shape that reads it.

Either way the task report states which branch was taken and the command output that selected it.

### Tests (contracts, not bodies)

- **T1.1 — the scope is typed and ceilinged.** Parse `etkl.ttl` alone; assert
  `etkl:readerScope a dec:Scope` and `etkl:readerScope dec:maxSeverity risk:Watch` are both
  present. Falsify by deleting the `a dec:Scope` triple.
- **T1.2 — the ordinals are not restated.** Assert `etkl.ttl` contains **no** `risk:order` triple.
  This is condition 1's first line of defence at vocabulary level: the ordering is `risk.ttl`'s to
  own. Falsify by adding `risk:Watch risk:order 1` to `etkl.ttl`.
- **T1.3 — the ceiling is below `risk:Breach`.** Over `etkl.ttl ∪ risk.ttl`, assert the ordinal of
  `etkl:readerScope`'s `dec:maxSeverity` is strictly less than `risk:Breach`'s. This pins the
  *relation* the shape depends on, not the two numbers, so retuning `risk.ttl` cannot silently make
  the shape inert. Falsify by setting the ceiling to `risk:Critical`.

### `## FALSIFICATION`

Per test: remove or invert the thing it pins, show it **failing**, restore, show the suite green.

### Done when

`etkl:readerScope` is declared and typed; T1.1–T1.3 pass with falsification evidence;
`decisionlog.py:92` no longer claims the `dec:regarding` widening is branch-local; S2 is answered by
measurement and the answer is in the task report.

---

## Task 2: `escalation-furnish.rq` — the derivation, offline

### Goal

The `CONSTRUCT` that turns a recorded escalation verdict into the three predicates the shape reads,
plus the expansion request it escalates to. **Offline in this task** — a pure function from graph to
graph, tested against a real compiled corpus graph, wired into nothing.

### Measured — the input the derivation matches

Every escalation site already mints a decision holon with a labelled option space:

```
$ grep -c 'record("verdict"' src/iladub/etkl/compile.py
17

$ grep -n 'record("verdict"' src/iladub/etkl/compile.py
514:            brec.record("verdict", ["asserted", "escalated", "ignored"],
531:            brec.record("verdict", ["asserted", "escalated", "ignored"], "ignored", "")
574:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
592:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
606:                    brec.record("verdict", ["asserted", "escalated", "ignored"],
644:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
657:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
681:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
694:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
735:                    brec.record("verdict", ["asserted", "escalated", "ignored"],
748:                    brec.record("verdict", ["asserted", "escalated", "ignored"],
790:                    brec.record("verdict", ["asserted", "escalated", "ignored"],
816:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
829:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
857:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
876:                        brec.record("verdict", ["asserted", "escalated", "ignored"],
898:                    brec.record("verdict", ["asserted", "escalated", "ignored"],
```

Not all 17 choose `escalated` — `:531` chooses `"ignored"` unconditionally. **The derivation keys on
the chosen option's label, never on the call site.** What the recorder writes:

```
$ nl -ba src/iladub/etkl/decisionlog.py | sed -n '48,66p'
    48	        g = self._g
    49	        d = URIRef(f"{self._prefix}-d{self._n}")
    50	        g.add((d, RDF.type, DEC.DecisionHolon))
    51	        g.add((d, RDFS.label, Literal(judgement)))
    52	        g.add((d, DEC.regarding, self._regarding))
    53	        g.add((d, DEC.withinProcess, self._band))
    54	        g.add((d, DEC.decidedBy, self._agent))
    55	        g.add((d, DEC.order, Literal(self._n, datatype=XSD.integer)))
    56	        g.add((d, DEC.rationale, Literal(rationale)))
    57	        rejected = rejected or {}
    58	        for name in options:
    59	            o = URIRef(f"{d}-opt-{_slug(name)}")
    60	            g.add((o, RDF.type, DEC.Option))
    61	            g.add((o, RDFS.label, Literal(str(name))))
    62	            g.add((d, DEC.optionSpace, o))
    63	            if str(name) == str(chosen):
    64	                g.add((d, DEC.chosen, o))
```

`rdfs:label` on **every** option (`:61`), one `dec:regarding` (`:52`), one `dec:rationale` (`:56`).
The URI shape `{d}-opt-{slug}` at `:59` is an implementation detail **no query may depend on**.

### Measured — the second producer, and why invariant 5 is live rather than vacuous

Spec §4.1 invariant 5 asks: does every verdict decision carry `dec:regarding`, or must the
derivation skip those that do not? A second producer mints decision holons without going through
`ReadingRecorder.record`:

```
$ nl -ba src/iladub/etkl/datagrid.py | sed -n '695,697p'
   695	    g.add((dec_uri, RDF.type, DEC.DecisionHolon))
   696	    g.add((dec_uri, DEC.chosen, grid_uri))
   697	    g.add((dec_uri, DEC.optionSpace, grid_uri))

$ grep -n "DEC.regarding\|DEC.condition\|DEC.rationale" src/iladub/etkl/datagrid.py
(no output; exit status 1 — no matches)
```

**So a `dec:DecisionHolon` with no `dec:regarding` exists in real compiled graphs.** Invariant 5's
"skip it" branch is the live one; "it cannot happen" is refuted. Its chosen option also carries a
label, but a descriptive one:

```
$ nl -ba src/iladub/etkl/datagrid.py | sed -n '714,716p'
   714	    g.add((grid_uri, RDFS.label, Literal(
   715	        f"{grid.grid_type} on page {page}: {len(grid.rows)} rows x "
   716	        f"{len(grid.columns)} columns")))
```

— never `"escalated"`. **The derivation must be safe on the first ground, not the second.** Relying
on the label alone would make the query's safety depend on a formatted string in an unrelated
module.

### The contract

**File:** `vocab/queries/escalation-furnish.rq`, `CONSTRUCT` form, joining the 37 existing queries
in `vocab/queries/` (`why-escalated.rq` is its nearest neighbour and answers the *other* half of the
same question — why a region was escalated, as opposed to what that escalation obliges).

**Matches** every `?d` such that:

- `?d a dec:DecisionHolon`
- `?d dec:chosen ?o` and `?o rdfs:label "escalated"` — **the label, never a URI suffix**
- `?d dec:regarding ?r` — **a required pattern, not `OPTIONAL`**. This is how invariant 5 is
  satisfied: a decision with no `dec:regarding` matches nothing and therefore derives *nothing at
  all*, rather than a request with no subject matter. Do not implement it as a `FILTER`; the join
  is the guard.
- `?d dec:rationale ?why`
- `risk:Breach risk:order ?so` and `etkl:readerScope dec:maxSeverity ?ceil` and
  `?ceil risk:order ?co` — **bound from the vocabulary graph, condition 1.** These three patterns
  are what make the query a *derivation over evidence* rather than a restatement of `risk.ttl`.

**Derives**, per match:

| triple | source |
| --- | --- |
| `?d dec:constrainedBy risk:Breach` | the severity every region escalation realizes |
| `?d dec:withinScope etkl:readerScope` | Task 1 |
| `?d dec:escalatedTo ?req` | the apex |
| `?req a dec:ExpansionRequest` | |
| `?req dec:regarding ?r` | `?d`'s own `dec:regarding` |
| `?req dec:condition ?why` | `?d`'s own `dec:rationale` — see the maxCount seam below |
| `etkl:readerScope dec:maxSeverity ?ceil` | **carried vocabulary** (condition 3) |
| `risk:Breach risk:order ?so` | **carried vocabulary** (condition 3) |
| `?ceil risk:order ?co` | **carried vocabulary** (condition 3) |

**Exactly three carried vocabulary triples**, and they are the closure of what
`dec:EscalationShape`'s body reads from the terms the derivation itself names — no more:

```
$ nl -ba vocab/shapes/escalation-shapes.ttl | sed -n '16,32p'
    16	dec:EscalationShape a sh:NodeShape ;
    17	    sh:targetClass dec:DecisionHolon ;
    18	    sh:sparql [
    19	        sh:message "A decision whose realized severity exceeds its autonomy scope ceiling must be escalated (dec:escalatedTo a higher-authority decision). A constitutional matter cannot be resolved within local autonomy." ;
    20	        sh:prefixes dec:escPrefixes ;
    21	        sh:select """
    22	            SELECT $this WHERE {
    23	                $this dec:constrainedBy ?sev .
    24	                $this dec:withinScope ?scope .
    25	                ?scope dec:maxSeverity ?ceil .
    26	                ?sev  risk:order ?so .
    27	                ?ceil risk:order ?co .
    28	                FILTER (?so > ?co)
    29	                FILTER NOT EXISTS { $this dec:escalatedTo ?apex }
    30	            }
    31	        """ ;
    32	    ] .
```

`:23`/`:24` are supplied by the derivation; `:25`/`:26`/`:27` are the three carried triples.

**Because the vocabulary triples sit in the `CONSTRUCT` template, `CONSTRUCT` semantics give the
boundary for free**: no match ⇒ empty output ⇒ **zero** vocabulary triples. That is the property
that separates (d) from "merge `risk.ttl`", which asserts the whole file unconditionally on every
document.

### Invariants the implementer must preserve

1. **Open-world and evidence-positive.** Derives only where an escalated choice is *present*.
   Nothing inferred from absence (CLAUDE.md §8, §7).
2. **Monotonic and idempotent.** Running it twice adds nothing the first run did not.
3. **Nothing written onto an `iladub:CandidateConcept`** (G5).
4. **`?req`'s identity is a function of `?d`**, not minted randomly, so the derivation is a pure
   function of the graph. URIRef-from-`?d` or blank node is the implementer's call — the membrane
   skolemizes (`membrane._payload_nt`, `membrane.py:318`), so a blank node is no longer a hazard,
   but `dec:EscalationShape` carries `sh:sparql` and R88's pin history is about exactly this. If
   you choose a blank node, say in the task report which engine leg you measured it on.
5. **A decision with no `dec:regarding` derives nothing** — enforced by the join, per above.

### MEASURE seam: `dec:condition` cardinality

`?req dec:condition ?why` binds from `?d dec:rationale ?why`. The already-wired `dec:EventShape`
requires **exactly one**:

```
$ nl -ba vocab/shapes/dec-shapes.ttl | sed -n '60,63p'
    60	dec:EventShape a sh:NodeShape ;
    61	    sh:targetClass dec:Event ;
    62	    sh:property [ sh:path dec:condition ; sh:minCount 1 ; sh:maxCount 1 ;
    63	        sh:message "An event must declare exactly one condition." ] .
```

`decisionlog.py:56` writes one `dec:rationale` per decision, but **the load-bearing claim is about
the graph, not the writer**. MEASURE, on a real compiled escalating document, that no
`dec:DecisionHolon` carries more than one `dec:rationale`, before binding `dec:condition` from it.
A second rationale on one decision is a **document refusal**, not a warning. If the measurement
finds any, the query must reduce to one (`SAMPLE`/`MIN` over a sub-select, or a constant condition
literal) and the task report says which and why.

### Tests (contracts, not bodies) — `tests/etkl/test_escalation_furnish.py`

Marked `-m corpus` where a corpus graph is needed:

```
$ nl -ba pyproject.toml | sed -n '90,95p'
    90	[tool.pytest.ini_options]
    91	testpaths = ["tests"]
    92	pythonpath = ["."]
    93	markers = [
    94	    "corpus: real third-party documents (gitignored corpus/; run with -m corpus)",
    95	]
```

- **T2.1 — it furnishes what the shape reads.** On a synthetic graph carrying one recorder-shaped
  escalated verdict decision, assert all six derived data triples are present and `?req`'s type is
  `dec:ExpansionRequest`. Falsify by removing `dec:constrainedBy` from the template.
- **T2.2 — it is silent where there is no escalation.** On a graph whose only decision chose
  `"asserted"`, assert the output graph is **empty** — length zero, *including* the vocabulary
  triples. Falsify by hoisting the vocabulary triples out of the template into an unconditional
  assertion; the test must fail.
- **T2.3 — condition 1, the ordinals are bound, not written.** Run the derivation with a vocabulary
  graph in which `risk:Breach risk:order` has been changed from `2` to `7`, and assert the carried
  `risk:order` object is `7`. A query that wrote the literal `2` passes T2.1 and **fails this**.
  This is the testable property condition 1 demands. Falsify by replacing the bound `?so` with the
  literal `2`.
- **T2.4 — condition 3, the carry is bounded.** Assert the output contains **exactly three** triples
  whose subject is in the `risk:` or `etkl:` namespace, and name them. "Merge `risk.ttl`" must fail
  this as surely as asserting nothing does — state both directions in the report. Falsify in both
  directions: (a) union `risk.ttl` into the output; (b) delete one carried triple.
- **T2.5 — condition 2, the licence is written down.** Assert `escalation-furnish.rq` contains the
  note stating *a derivation may carry vocabulary into data when a shape reads it, bounded to the
  triples that shape's body reads from the terms this query names* — and its boundary. A test on a
  comment is unusual; it is here because condition 2 is the only condition that has no runtime
  consequence, and an unenforced condition is not a condition. Falsify by deleting the note.
- **T2.6 — idempotent.** Derive, union into the input, derive again; assert the second output adds
  no triple the first did not. Falsify by making `?req` a fresh random URIRef.
- **T2.7 — invariant 5, the datagrid admission holon.** Construct a graph containing a decision
  holon with `dec:chosen` but **no** `dec:regarding` (the `datagrid.py:695-697` shape, measured
  above — this setup is constructible by the code as it stands, plan rule 5). Assert the derivation
  emits nothing for it, **even if** its chosen option is labelled `"escalated"`. Falsify by making
  the `dec:regarding` pattern `OPTIONAL`.
- **T2.8 — the corpus census** (`-m corpus`). On the documents that escalate, assert the number of
  derived `dec:ExpansionRequest`s equals the number of decision holons whose chosen option is
  labelled `"escalated"` **and** which carry `dec:regarding`, and **report both counts and their
  difference**. Spec §5 M5 recorded 32 escalations over 4 of 7 documents (apple 15, bfs 10,
  cbh-stem 4, who-wfa 3); three documents carry zero. Re-measure — do not cite. A non-zero
  difference is the coverage hole invariant 5 creates, and this is the only test that can see it.
  **Select an escalating document**; a test written against `graincorp-stem` or `ons` pins nothing.
  Falsify by removing the `rdfs:label "escalated"` pattern (the count must jump to all 769-odd
  holons).

### `## FALSIFICATION`

As above, per test. T2.3 and T2.4 are the two that carry conditions 1 and 3 — their falsification
evidence is what makes option (d) distinguishable from option (b) and from a `risk.ttl` merge. If
either cannot be shown failing, the acceptance of (d) does not hold and the task report says so.

### Done when

The `.rq` exists, T2.1–T2.8 pass with falsification evidence, the `dec:condition` cardinality seam is
measured and its answer recorded, and **nothing in `src/` calls it yet**.

---

## Task 3: S1 — the seam. Where the derivation runs

### Goal

Wire the derivation into the pipeline at the site the **measurement** selects.

**This is the commit that can break every escalating document**, not Task 4. The moment
`dec:ExpansionRequest` instances enter a validated graph, two shapes that are already wired and
currently idle go live:

```
$ nl -ba src/iladub/etkl/compile.py | sed -n '399p'
   399	_DEC_SHAPE_FILES = ("dec-shapes.ttl", "iladub-shapes.ttl")

$ nl -ba vocab/shapes/dec-shapes.ttl | sed -n '71,74p'
    71	dec:ExpansionRequestShape a sh:NodeShape ;
    72	    sh:targetClass dec:ExpansionRequest ;
    73	    sh:property [ sh:path dec:regarding ; sh:minCount 1 ;
    74	        sh:message "An expansion request must name the off-the-map content it was raised about (dec:regarding)." ] .
```

`dec-shapes.ttl` carries both `dec:EventShape` (`:60-63`) and `dec:ExpansionRequestShape`
(`:71-74`), and is already in `_DEC_SHAPE_FILES`. Under subclass closure every minted request is
also a `dec:Event` (`dec.ttl:197-198`). **The emission must satisfy both from the first commit, or
the membrane refuses every escalating document.**

### The runner

The precedent is a flat union, measured:

```
$ nl -ba src/iladub/etkl/interpret.py | sed -n '18,29p'
    18	def run(query_path, *graphs):
    19	    """Execute the CONSTRUCT at `query_path` over the union of `graphs`; return the
    20	    constructed rdflib.Graph."""
    21	    union = Graph()
    22	    for g in graphs:
    23	        union += g
    24	    query = Path(query_path).read_text(encoding="utf-8")
    25	    result = union.query(query)
    26	    out = Graph()
    27	    for triple in result:
    28	        out.add(triple)
    29	    return out
```

No named vocab parameter, no `initBindings` — every graph is a positional member of one union. The
precedent is stronger than a two-graph call: `federate.py:97-100` passes **five** graphs including a
synthetic one-triple parameter graph, and `denormalization.py:96-97` chains one run's output into
the next's input:

```
$ nl -ba src/iladub/etkl/federate.py | sed -n '97,100p'
    97	    recipe = Graph()
    98	    recipe.add((RECIPE, ETKL.forViewer, URIRef(str(viewer))))
    99	    return interpret.run(os.path.join(_QUERIES, "federate-projection-governed.rq"),
   100	                         interior, terms, governance, policy, recipe)

$ nl -ba src/iladub/etkl/denormalization.py | sed -n '96,97p'
    96	    marks = interpret.run(os.path.join(_QUERIES, "name-levels.rq"), g)
    97	    dimgraph = interpret.run(os.path.join(_QUERIES, "recover-dimensions.rq"), g, marks)
```

So the call is `interpret.run(rq, document_graph, vocab_graph)` where `vocab_graph` is
`risk.ttl ∪ etkl.ttl`, and its output is unioned into the document graph.

**Name the vocabulary file set as a module constant**, on the precedent of `_GROUND_ONT_FILES`:

```
$ nl -ba src/iladub/feed.py | sed -n '586,587p'
   586	_GROUND_SHAPE_FILES = ("iladub-shapes.ttl", "dec-shapes.ttl")
   587	_GROUND_ONT_FILES = ("iladub.ttl", "dec.ttl")
```

Inline `os.path.join` paths at the call site would make the derivation's vocabulary invisible to
anyone reading the membrane. Parse it once, module-level, as `_build_membrane` does at
`compile.py:402-432` — not per page.

### The three measured constraints

**C1 — the first `_validate` call site is gated.**

```
$ nl -ba src/iladub/etkl/compile.py | sed -n '1079,1087p'
  1079	    if validate_shapes and (
  1080	        any(graph.subjects(RDF.type, TAB.RecordTable))
  1081	        or any(graph.subjects(RDF.type, TAB.HierarchicalTable))
  1082	    ):
  1083	        conforms, text = _validate(graph)
  1084	        if not conforms:
  1085	            raise AssertionError(f"asserted holon failed tab: SHACL:\n{text}")
  1086	
  1087	    return CompilationReport(score, tuple(reports), graph, asserted_total, escalated_total)
```

(`compile.py` ends at `:1087`.)

**C2 — the second, in `document.py`, differently gated, and it is the only one there.**

```
$ ls src/iladub/document.py 2>&1
ls: src/iladub/document.py: No such file or directory

$ grep -n "_validate(" src/iladub/etkl/document.py
1516:        conforms, text = _validate(graph)

$ nl -ba src/iladub/etkl/document.py | sed -n '1515,1518p'
  1515	    if validate_shapes and (recognized or section_facts):
  1516	        conforms, text = _validate(graph)
  1517	        if not conforms:
  1518	            raise AssertionError(f"document-level facts failed tab: SHACL:\n{text}")
```

**C3 — the `datagrid_adopt` trap. The name `graph` is rebound, and everything written before it is
dropped.**

```
$ nl -ba src/iladub/etkl/compile.py | sed -n '486,488p'
   486	    graph = Graph()
   487	    from .decisionlog import ReadingRecorder
   488	    recorder = ReadingRecorder(graph, doc, page_number)

$ nl -ba src/iladub/etkl/compile.py | sed -n '993p'
   993	    if datagrid_adopt and asserted_total == 0 and escalated_total > 0:

$ nl -ba src/iladub/etkl/compile.py | sed -n '1027,1029p'
  1027	            graph = Graph()                   # withdrawal: the page graph is rebuilt
  1028	            _grid_uri = _emit(graph, _grid, _lines, doc, page_number)
  1029	            _cells = len(list(graph.subjects(RDF.type, TAB.EntryCell)))
```

`ReadingRecorder` captures the graph object at `:488` and holds it; all 17 verdict sites
(`:514`–`:898`) write into that object. At `:1027` the **name** rebinds to a new `Graph`, and
`:1083` validates and `:1087` returns the new one. **Furnishing placed before `:1027` is discarded
on the adopting path.** This is the same shape as R73's defect 2, which plan rule 2 exists to catch.

There is also a comment at `compile.py:1011-1018` asserting *"The DOCUMENT path has no gap: it keeps
the original page graph."* **Do not use it.** It is written about `RegionReport` token accounting,
it is a claim from reading, and the whole point of rule 2 is that a comment is not a measurement.

### What to MEASURE before writing the call

Do not choose a site from the three constraints above. Measure the graphs themselves.

For each candidate insertion point — (i) inside `compile_tables` before `:1079`, (ii) inside
`compile_tables` after the `:1027` rebuild, (iii) in `document.py` before `:1515` — on a **real
escalating page**, both with and without `datagrid_adopt=True`, count in the graph object the site
actually holds:

```
# decision holons whose chosen option is labelled "escalated"
# decision holons that also carry dec:regarding
# tab:RecordTable + tab:HierarchicalTable  (does C1's gate even open?)
```

Then state, in the task report, the table of counts. **The site is the one where the escalations are
present, the gate opens, and nothing downstream rebinds the graph** — and if no single site
satisfies all three, that is a finding, not a defeat: report it and wire two sites, or say which
path is deliberately left unfurnished and raise it as a residue.

Two specific questions the counts must answer:

- **Does the adopting path retain any escalated decision at all?** If the rebuilt graph B has none,
  then furnishing after `:1027` correctly furnishes nothing, because the escalations were withdrawn
  — and the plan's answer is "the adopting path needs no furnishing", stated as a measurement, not
  as an inference from reading `:1027`.
- **Does `document.py:1516` see the page graph the recorder wrote, or the rebuilt one?** The answer
  determines whether document-scope validation is covered by the page-scope call or needs its own.

**The `datagrid_adopt` path has never been exercised by any test.** Whatever the measurement shows,
the report says how the path was exercised to produce the numbers.

### Tests (contracts, not bodies)

- **T3.1 — furnished before validation.** On an escalating page compiled with `validate_shapes=True`,
  assert the returned graph carries at least one `dec:ExpansionRequest` and that the compile did not
  raise. Falsify by moving the derivation call after `:1083`.
- **T3.2 — `dec:EventShape` is satisfied from the first commit.** Assert every derived `?req` carries
  exactly one `dec:condition`. Falsify by dropping `dec:condition` from the template — the compile
  must then **refuse the document**, which is the assertion.
- **T3.3 — `dec:ExpansionRequestShape` is satisfied.** Assert every derived `?req` carries at least
  one `dec:regarding`. Falsify by dropping it.
- **T3.4 — the R19 hazard is not re-created.** Assert the derivation runs on the document/page graph
  and never on a region scratch graph. The hazard is recorded at the source:

  ```
  $ nl -ba src/iladub/etkl/decisionlog.py | sed -n '12,14p'
      12	MEMBRANE HAZARD (spec §3.1): a recorder must be given the DOCUMENT graph, never a region's
      13	scratch graph. Decisions in a graph that region_tiles validates is the R19 hazard again — a
      14	shape firing on something that is not what it thinks it is.
  ```

  Falsify by calling the derivation inside the per-region path.
- **T3.5 — the adopting path behaves as measured.** Whatever the C3 measurement selects, pin it: on
  a page compiled with `datagrid_adopt=True`, assert the escalation-furnishing count the measurement
  recorded. **Write this test against the measured number, not the expected one.**

### `## FALSIFICATION`

Per test. T3.2's falsification is the one that proves §4.4's warning is real: with `dec:condition`
removed, an escalating document must be **refused**, not merely unvalidated.

### Done when

The derivation runs at the measured site; T3.1–T3.5 pass with falsification evidence; the counts
table is in the task report; the seam question is answered by measurement and the answer names the
commands that produced it.

---

## Task 4: Wire `escalation-shapes.ttl` into the compile membrane

### Goal

Give the shape a membrane in which it now has something to say. This closes R87's substance.

### Measured — it is wired into nothing today

```
$ grep -rn "escalation-shapes" . --include='*.py' --include='*.toml' --include='*.md' --include='*.ttl' | grep -v ".git/"
tests/test_escalation_shacl.py:31:    shapes.parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
tests/test_escalation_shacl.py:37:    shapes = Graph().parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
tests/test_escalate.py:69:    shapes.parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
```

(plus documentation references; no `src/` reference at all — R87's row holds.)

### What ships

`escalation-shapes.ttl` joins `_DEC_SHAPE_FILES` at `compile.py:399`. **Compile leg only** — the
grounding membrane is untouched (G4, spec §4.3): grounding decisions are `iladub:PromotionDecision`s
whose chosen option is never `"escalated"`, so wiring it there would re-create exactly the vacuity
this loop repairs.

**`risk.ttl` does not join `_FULL_ONT`** (G2). The three ordinal triples arrive via the derivation.

**The engine pin.** R87's row demanded a measurement — *does any escalation-carrying decision have a
blank-node subject?* — and the answer recorded there was **yes on the grounding graph** (167/167
blank for `dec:DecisionHolon`) and **no on the compile graph** (0/14). Since this loop wires the
shape into the **compile** leg only, the blank-node hazard does not arise from the shape's target.
It may arise from `?req` if the implementer chose a blank node (Task 2, invariant 4). **Re-measure
on this branch — do not cite the row** — and if `?req` is a blank node, state which engine leg the
verdict was taken on.

```
$ grep -n "pyrudof\|importorskip\|skip" tests/etkl/test_membrane.py | head
180:needs_rudof = pytest.mark.skipif(
181:    not __import__("importlib").util.find_spec("pyrudof"),
182:    reason="pyrudof not installed (optional dependency)")
```

### The tests that currently merge `risk.ttl` into the data graph

```
$ nl -ba tests/test_escalation_shacl.py | sed -n '19,25p'
    19	def _data(example_filename):
    20	    # risk.ttl is also merged into the data graph so risk:order is visible to the SPARQL
    21	    # constraint regardless of pySHACL ont-graph query semantics (deterministic).
    22	    g = Graph()
    23	    g.parse(os.path.join(TXD, example_filename), format="turtle")
    24	    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    25	    return g

$ nl -ba tests/test_escalate.py | sed -n '65p'
    65	    data.parse(os.path.join(ONT, "risk.ttl"), format="turtle")  # risk:order for the SPARQL
```

These belong to the transplant/M4 showcase track and are **not** changed by this loop. They are
listed here because they are the closest thing to a precedent for option (d), and because a
reviewer will find them: they merge the *whole* file unconditionally, which is precisely what
T2.4 forbids for the pipeline path. Do not extend them; do not delete them.

### O1 and O3

- **O1 — the shape is live.** On a document that escalates (apple, bfs, cbh-stem or who-wfa —
  never graincorp-capacity, graincorp-stem or ons, which carry zero escalations), remove
  `dec:escalatedTo` from the derivation's `CONSTRUCT` template. **The compile membrane must refuse
  the page.** Restore; the suite is green. This is the oracle that proves the shape refuses when the
  graph is wrong.
- **O3 — no verdict moved, restated per G2.** Every corpus document's compile verdict, **both
  legs**, before and after this loop's change (the derivation plus the shape wiring) — not before
  and after a `_FULL_ONT` edit, which is not happening. Report `(conforms, refusing focus nodes,
  results)` per document per leg. Enlarging the *data* graph is what needs watching here, and
  `compile.py:425-429`'s 2026-08-10 measurement is about enlarging the *ontology* graph, so it does
  not transfer.

  **G4 applies with force:** if any corpus escalation count moves, that is a defect, not a feature.
  Report the escalated-decision count per document alongside the verdict.

### `## FALSIFICATION`

O1 **is** this task's falsification, and it must be shown failing (the membrane refusing) before it
is shown passing.

### Done when

`escalation-shapes.ttl` is in `_DEC_SHAPE_FILES`; O1 shown failing then green; O3's table is in the
task report with both legs and all seven documents; the blank-node/engine question is re-measured on
this branch.

---

## Task 5: The vacuity registry — the generalized guard

### Goal

The guard whose absence let R87 be filed as *"0 violations, nothing to do."*

### Why a registry and not a universal

Ten shapes already wired into the compile membrane are idle corpus-wide (spec §3, M7), so a blanket
*"every wired shape must be non-idle"* **fails ten times on day one**. And the R87 defect is not
even visible to a focus-node count: `dec:EscalationShape` receives 769 focus nodes (it targets
`dec:DecisionHolon`, `escalation-shapes.ttl:17`) and binds zero rows. **Focus-node counting alone
pronounces it healthy.** Hence two criteria, not one.

### The contract

For every shape wired into either membrane, measured on real corpus graphs:

1. **Focus-node count** — targets resolved: `sh:targetClass`, `sh:targetSubjectsOf`,
   `sh:targetObjectsOf`.
2. For every shape carrying `sh:sparql`, **whether the body's non-negated patterns bind ≥ 1 row.**

A shape idle by **either** criterion must appear in a registry **with a measured reason**. The test
fails when a shape is idle and **unregistered**, and equally when a shape is registered and has
become **live** — a stale registration is how a guard rots into a rubber stamp.

**"Non-negated" is load-bearing.** `dec:EscalationShape`'s body ends in
`FILTER NOT EXISTS { $this dec:escalatedTo ?apex }` (`escalation-shapes.ttl:29`). Once the
derivation ships, that filter *correctly* eliminates every row, so a naive "does the body bind"
check reports zero on a healthy shape. Criterion 2 must strip the negated block and measure what
remains. **MEASURE this on the shipped state before writing the assertion** — if criterion 2 as
implemented reports `dec:EscalationShape` idle after Task 3, the criterion is wrong, not the shape.

### Seeding

Seed with the ten rows of M7 and their reasons. Spec §3's table gives the reasons; **re-measure the
focus counts, do not copy them.** The five rows whose reason is *"corpus does not exercise it"* each
raise a residue (Task 6) — a shape validating a feature no corpus document exercises is either a
corpus gap or a dead shape, and this loop does not adjudicate which.

Two of the ten (`dec:EventShape`, `dec:ExpansionRequestShape`) **go live under this loop** and must
therefore be **absent** from the seeded registry, or the "registered but live" arm fails
immediately. That is the intended behaviour and a good first falsification: register one of them,
show the test fail, unregister.

### Placement and cost

```
$ python3 -m pytest tests/etkl/test_membrane.py --collect-only -q 2>&1 | tail -3
tests/etkl/test_membrane.py::test_subclass_closure_drops_literal_subject_triples

28 tests collected in 0.30s

$ nl -ba tests/etkl/test_membrane_equiv.py | sed -n '19,21p'
    19	pytestmark = pytest.mark.skipif(
    20	    not __import__("importlib").util.find_spec("pyrudof"),
    21	    reason="pyrudof not installed (optional dependency)")
```

`test_membrane_equiv.py` skips **the whole module** without `pyrudof`, which is not a core
dependency; `test_membrane.py` collects 28 tests with no module-level skip (its `needs_rudof` at
`:180` is per-test). **The default install must run this guard** — put it beside
`test_membrane.py`, in `tests/etkl/test_vacuity_registry.py`. Same trap as R92 and the parity
oracle: the default install is the failing side.

The guard needs compiled corpus graphs, so it is `-m corpus` (`pyproject.toml:93-95`). **The fast
suite must not grow a five-minute dependency.** State the measured runtime in the task report.

### Tests (contracts, not bodies)

- **T5.1 — O2, the guard catches R87 itself.** Remove the furnishing derivation while leaving
  `escalation-shapes.ttl` wired. `dec:EscalationShape`'s body-bindability drops to zero and the
  registry test must **fail**. This is O2, and it is this task's reason for existing.
- **T5.2 — idle and unregistered fails.** Add a shape file with an unsatisfiable target; the test
  fails until it is registered.
- **T5.3 — registered and live fails.** Register a live shape; the test fails. Unregister.
- **T5.4 — criterion 2 sees past criterion 1.** Pin M6's shape directly: a shape with many focus
  nodes and zero non-negated bindings must be caught. **Criterion 1 alone must not catch it** —
  assert both, so that a future simplification collapsing the two criteria fails here.

O1 and O2 are complementary and neither substitutes for the other: **O1 proves the shape refuses
when the graph is wrong; O2 proves the guard refuses when the shape is toothless.** R87 existed
because only the first kind of oracle was ever written.

### `## FALSIFICATION`

T5.1 (= O2) is mandatory and is the task's headline falsification.

### Done when

The registry test exists beside `test_membrane.py`, runs on the default install under `-m corpus`,
T5.1–T5.4 pass with falsification evidence, the ten seeded rows carry re-measured focus counts, and
the runtime is stated.

---

## Task 6: The record

### Goal

Close R87, raise what this loop defers, run the batteries, increment the doc.

### O4 — the batteries

Run and report, on this branch:

- corpus battery: `python3 -m pytest -m corpus`
- fast suite: `python3 -m pytest -m "not corpus"`
- both again under `ILADUB_MEMBRANE=rudof`

Spec §5 O4 records baselines of 36 passed (corpus) and 1152 passed / 7 skipped / 1 xfailed (fast) —
**but those baselines are at `06fe726`, and this branch is at `401e0d6`.** Establish the branch's
own before-state first, on a clean checkout of `401e0d6`, and report before/after. A battery
compared against a baseline from a different commit measures the commits in between.

**The rudof leg has never been re-confirmed for this work** — every escalation verdict in the
deliberation forced `engine="pyshacl"`, while `engine_name()` reports `rudof` as this environment's
default. If the rudof leg diverges, that is a finding for the task report, not something to
suppress.

### Residue bookkeeping — the house-style plan's convention does NOT transfer

`docs/superpowers/plans/2026-08-13-membrane-parity.md`'s Task 4 strikes rows in place. This register
does not work that way:

```
$ grep -c "^| R" docs/superpowers/residues-open.md
69

$ grep -c "^| ~~R" docs/superpowers/residues-open.md
0
(exit status 1 — no matches)

$ grep -c "^| R" docs/superpowers/residues-closed.md
0

$ grep -c "^| ~~R" docs/superpowers/residues-closed.md
17
```

**Closed rows are struck and live in `residues-closed.md`.** 69 open + 17 closed = 86, which agrees
with the census:

```
$ nl -ba docs/superpowers/residues.md | sed -n '32,33p'
    32	**As of 2026-08-13: 86 rows, 17 closed.** (Ten numbers between R1 and R96 were never issued as
    33	rows; the denominator is rows that exist, not the highest number.)
```

**The stamp on a new row is a snapshot at the moment it is raised**, never updated afterwards:

```
$ nl -ba docs/superpowers/residues.md | sed -n '16,18p'
    16	rows record, in parentheses after its number, **the state of the register at the moment it was
    17	raised**: `| R97 (17/87 closed) |` means that when R97 went in, 17 of the 87 rows then present
    18	were closed.
```

**Order therefore matters.** Close R87 first (18 closed), then raise the new rows, re-running the
two counts between each so each stamp is true when written:

```
grep -c "^| R" docs/superpowers/residues-open.md
grep -c "^| ~~R" docs/superpowers/residues-closed.md
```

### What to close

**R87.** Strike its row, move it to `residues-closed.md`, and record **in the row it strikes** what
was measured and what now prevents recurrence — the closure evidence is the vacuity registry
(Task 5), not the wiring (Task 4). R87's original instruction ("parse it into the pinned leg") was
followed *and* found insufficient; say so.

R87 also has a row in the summary register:

```
$ grep -n "R87" docs/superpowers/residues.md
136:| R87 | open | `escalation-shapes.ttl` is in NO membrane |
```

Update `:136` and the `:32` census.

### What to raise

- **The five corpus-not-exercised shapes** (spec §4.5) — one row or five, implementer's discretion,
  each recording its **measured** focus count of 0.
- **Anything Task 3's measurement left unfurnished** (e.g. the adopting path), if the counts table
  showed a gap.
- **The `dec:escalatedTo` widening**, if S2's measurement sent it to its own residue rather than
  Task 1.

**Not closed and explicitly untouched:** R86, R89, R61, R95, R96.

### Doc impact — increment

```
$ grep -rn "escalation-shapes" docs/wiki/
docs/wiki/concepts/decision-holon.md:7:  - vocab/shapes/escalation-shapes.ttl
docs/wiki/concepts/decision-holon.md:51:(`dec:escalatedTo`, `dec:maxSeverity` on `dec:Scope`): `vocab/shapes/escalation-shapes.ttl`'s
```

`decision-holon.md` already names the shape and describes it as apex escalation for the
transplant/M4 track. Increment it to say that a *reading* refusal is now the same kind of act: a
region the compiler could not read names, in RDF, the severity it realized, the autonomy scope it
exceeded, and the human-addressed request it escalated to — and a membrane refuses the document if
it does not.

### `## FALSIFICATION`

Bookkeeping tasks have no test to invert. In its place, the task report states: the two counts
before and after each row change, and the diff of the three register files. If a stamp cannot be
reproduced from those counts, the bookkeeping is wrong.

### Done when

R87 struck and moved with closure evidence; new rows raised with true stamps; `residues.md:32` and
`:136` updated; O4's four battery runs reported with before/after; the wiki page incremented.

---

## Self-Review

**Spec coverage.** §4.1 (the derivation) → Tasks 2 and 3. §4.2 (vocabulary) → Task 1. §4.3
(membrane wiring) → Task 4, **first bullet rejected per G2**. §4.4 (the `dec:Event` constraint) →
Task 3, T3.2/T3.3, and the stale comment → Task 1. §4.5 (the vacuity registry) → Task 5. §5 oracles:
O1 → Task 4, O2 → Task 5 T5.1, O3 → Task 4 **restated per G2**, O4 → Task 6. §8 (residues) → Task 6.

**Deviation from the spec, stated rather than buried.** Spec §4.3's first bullet and the O3 that
depends on it are not implemented — the ruling rejected them on the measurement reproduced in G2.
O3 is re-pointed, not dropped.

**Plan rule 1.** No function body and no verbatim test appears above. Test contracts state setup,
assertion and falsification direction; the bodies are the implementer's. This is deliberate: the
plan-supplied tests in `CLAUDE.md:284-373`'s defects 5 and 6 are exactly what this loop cannot
afford, because the same author wrote the ruling and the plan.

**Plan rule 2.** Every `file:line` above was re-measured at `401e0d6` with the command shown. Two
claims are inherited rather than measured and are marked as such in Task 4 (R87's blank-node sweep)
and Task 5 (M7's ten rows) — both carry an instruction to re-measure rather than cite.

**Plan rule 3.** Two seams are named and not answered: S1 (Task 3, three constraints and a counts
table to produce) and S2 (Task 1, one grep to run). A third is named inside Task 2 (the
`dec:condition` cardinality) and a fourth inside Task 5 (whether criterion 2 must strip the negated
block). None is answered from reading.

**Plan rule 4.** Every task carries a `## FALSIFICATION` heading. Task 6's is the weakest — it is a
reproducibility check, not an inversion — and it says so.

**Plan rule 5.** G4 reproduces spec §7 in full as a hard constraint, and each test contract was
checked against it. T2.7 is the one whose *setup* needed measuring rather than assuming, and the
measurement is inline (`datagrid.py:695-697`, `grep` for `DEC.regarding` empty): the state that test
needs **is** constructible by the code as it stands.

**The one thing a reviewer should attack first.** G3 condition 2 — the licence note — is enforced by
a test that reads a comment (T2.5). That is a weak enforcement of the condition that matters most,
because it is the condition that stops option (d)'s precedent from being over-applied to the next
shape that wants a vocabulary triple. If a reviewer can propose a runtime enforcement of the
boundary, it should replace T2.5.
