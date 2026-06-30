# Apex Escalation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a decision realizes a severity beyond its declared autonomy scope, it escalates to a binding higher-authority (apex) `hol:DecisionHolon`, enforced by SHACL so a constitutional matter can never be resolved within local autonomy.

**Architecture:** A standalone vertical layer parallel to `reopen.py` (temporal lineage). New `hol:escalatedTo`/`hol:maxSeverity` terms in our `hol.ttl`; a SPARQL SHACL constraint comparing realized severity (`hol:constrainedBy` → `risk:Severity`) against the scope ceiling (`hol:withinScope` → `hol:Scope` → `hol:maxSeverity`) using `risk:order`; an `escalate()` function that builds the apex board decision; a worked example + leak; and the first `hol`↔HGA alignment module. `evaluate_m4` and the M4 pipeline are untouched.

**Tech Stack:** Python 3.12, rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), pytest. RDF Turtle for vocab/shapes/examples.

**Source-ownership boundary (CLAUDE.md § Source ownership — CI-enforced by `tests/test_source_ownership.py`):** we author only `etkl`/`hol`/`iladub`/`risk`. HGA terms (`holon:`/`hev:`/`hpol:`/`hmk:`/`hbayes:`) appear ONLY as objects, ONLY in `hol-hga-align.ttl` (Task 4). `hol.ttl` (Task 1) stays standalone — no `w3id.org/holon` string.

**Test command (this repo):** the venv interpreter is required so `baml_client` (repo root) and `iladub` (editable install) resolve. Always run:
```bash
.venv/bin/python -m pytest <path> -v
```

---

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `vocab/ontology/hol.ttl` (modify) | Declare `hol:escalatedTo` + `hol:maxSeverity` (ours; stays standalone) | 1 |
| `vocab/shapes/escalation-shapes.ttl` (create) | `hol:EscalationShape` — SPARQL: severity > scope ceiling ⇒ must escalate | 2 |
| `examples/transplant/transplant-escalation.ttl` (create) | Conformant: local decision escalates to board apex | 2 |
| `examples/transplant/transplant-escalation-leak.ttl` (create) | Negative: Critical-constrained local decision, no escalation ⇒ FAIL | 2 |
| `tests/test_escalation_shacl.py` (create) | SHACL pair: conformant passes, leak fails | 2 |
| `src/iladub/escalate.py` (create) | `requires_escalation`, `escalate()`, `EscalationOutcome` | 3 |
| `tests/test_escalate.py` (create) | Logic + structural + ordinal-mirror + merged-graph conformance | 3 |
| `vocab/ontology/hol-hga-align.ttl` (create) | First `hol`↔HGA module (points outward only) | 4 |
| `tests/test_hga_alignment.py` (modify) | Assert hol-align axioms present + hol.ttl standalone | 4 |

---

## Task 1: hol vocabulary — `hol:escalatedTo` + `hol:maxSeverity`

**Files:**
- Modify: `vocab/ontology/hol.ttl` (append a new section at end of file)
- Test: `tests/test_escalation_vocab.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_escalation_vocab.py`:

```python
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOL = Namespace("https://w3id.org/etkl/hol#")


def _hol():
    return Graph().parse(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), format="turtle")


def test_escalatedto_is_decision_to_decision_objectproperty():
    g = _hol()
    assert (HOL.escalatedTo, RDF.type, OWL.ObjectProperty) in g
    assert (HOL.escalatedTo, RDFS.domain, HOL.DecisionHolon) in g
    assert (HOL.escalatedTo, RDFS.range, HOL.DecisionHolon) in g


def test_maxseverity_is_objectproperty_on_scope():
    g = _hol()
    assert (HOL.maxSeverity, RDF.type, OWL.ObjectProperty) in g
    assert (HOL.maxSeverity, RDFS.domain, HOL.Scope) in g


def test_hol_stays_standalone_no_hga():
    text = open(os.path.join(ROOT, "vocab", "ontology", "hol.ttl"), encoding="utf-8").read()
    assert "w3id.org/holon" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_escalation_vocab.py -v`
Expected: FAIL — `test_escalatedto_*` and `test_maxseverity_*` fail (terms not yet declared); `test_hol_stays_standalone_no_hga` passes.

- [ ] **Step 3: Append the new terms to `hol.ttl`**

Append at the very end of `vocab/ontology/hol.ttl` (after the SP3a "Events & decision lineage" section):

```turtle
#################################################################
#  Apex escalation — vertical authority-holarchy lineage
#################################################################

hol:escalatedTo a owl:ObjectProperty ;
    rdfs:label "escalated to"@en ; rdfs:domain hol:DecisionHolon ; rdfs:range hol:DecisionHolon ;
    rdfs:comment "This decision escalated the matter to a higher-authority decision because it exceeded the decision's autonomy scope (authority-holarchy lineage; the vertical analog of hol:supersedes)."@en .

hol:maxSeverity a owl:ObjectProperty ;
    rdfs:label "max severity"@en ; rdfs:domain hol:Scope ;
    rdfs:comment "The highest severity the scope's holder may resolve within its own autonomy; a realized severity above it must be escalated. The filler is an ordinal severity resource (in practice a risk:Severity) — hol stays standalone, so the range is left open."@en .
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_escalation_vocab.py tests/test_source_ownership.py -v`
Expected: PASS (all). `test_source_ownership` confirms hol.ttl is still standalone.

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/hol.ttl tests/test_escalation_vocab.py
git commit -m "feat(hol): add hol:escalatedTo + hol:maxSeverity (apex escalation vocab)"
```

---

## Task 2: escalation SHACL shape + worked example + leak

**Files:**
- Create: `vocab/shapes/escalation-shapes.ttl`
- Create: `examples/transplant/transplant-escalation.ttl`
- Create: `examples/transplant/transplant-escalation-leak.ttl`
- Test: `tests/test_escalation_shacl.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_escalation_shacl.py`:

```python
import os
from rdflib import Graph
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")


def _knowledge():
    # hol.ttl gives the vocab; risk.ttl carries the risk:order ordinals the SPARQL compares.
    g = Graph()
    g.parse(os.path.join(ONT, "hol.ttl"), format="turtle")
    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    return g


def _data(example_filename):
    # risk.ttl is also merged into the data graph so risk:order is visible to the SPARQL
    # constraint regardless of pySHACL ont-graph query semantics (deterministic).
    g = Graph()
    g.parse(os.path.join(TXD, example_filename), format="turtle")
    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    return g


def test_escalation_conformant_passes():
    shapes = Graph()
    shapes.parse(os.path.join(SH, "hol-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
    res = validate(_data("transplant-escalation.ttl"), shapes, _knowledge())
    assert res.conforms, res.report_text


def test_escalation_leak_fails():
    shapes = Graph().parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
    res = validate(_data("transplant-escalation-leak.ttl"), shapes, _knowledge())
    assert not res.conforms
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_escalation_shacl.py -v`
Expected: FAIL — files `escalation-shapes.ttl` / `transplant-escalation*.ttl` do not exist (parse error).

- [ ] **Step 3a: Create the shape `vocab/shapes/escalation-shapes.ttl`**

```turtle
@prefix hol:  <https://w3id.org/etkl/hol#> .
@prefix risk: <https://w3id.org/etkl/risk#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

#  THE INVARIANT: a decision whose realized severity (hol:constrainedBy a risk:Severity)
#  exceeds its autonomy scope ceiling (hol:withinScope / hol:maxSeverity) MUST be escalated
#  (hol:escalatedTo a higher-authority decision). A constitutional matter cannot be resolved
#  within local autonomy. The apex decision, whose own ceiling covers the severity, is exempt
#  (the FILTER ?so > ?co does not fire on it). Severity ordering is read from risk:order.

hol:escPrefixes
    sh:declare [ sh:prefix "hol"  ; sh:namespace "https://w3id.org/etkl/hol#"^^xsd:anyURI ] ,
               [ sh:prefix "risk" ; sh:namespace "https://w3id.org/etkl/risk#"^^xsd:anyURI ] .

hol:EscalationShape a sh:NodeShape ;
    sh:targetClass hol:DecisionHolon ;
    sh:sparql [
        sh:message "A decision whose realized severity exceeds its autonomy scope ceiling must be escalated (hol:escalatedTo a higher-authority decision). A constitutional matter cannot be resolved within local autonomy." ;
        sh:prefixes hol:escPrefixes ;
        sh:select """
            SELECT $this WHERE {
                $this hol:constrainedBy ?sev .
                $this hol:withinScope ?scope .
                ?scope hol:maxSeverity ?ceil .
                ?sev  risk:order ?so .
                ?ceil risk:order ?co .
                FILTER (?so > ?co)
                FILTER NOT EXISTS { $this hol:escalatedTo ?apex }
            }
        """ ;
    ] .
```

- [ ] **Step 3b: Create the conformant example `examples/transplant/transplant-escalation.ttl`**

```turtle
@prefix tx:   <https://example.org/transplant#> .
@prefix hol:  <https://w3id.org/etkl/hol#> .
@prefix risk: <https://w3id.org/etkl/risk#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

#  Apex escalation on the transplant showcase. A donor with an absolute contraindication
#  realises a constitutional risk:Critical. The local (recipient-centre) decision's autonomy
#  ceiling is risk:Breach, so Critical (order 3) > Breach (order 2): it CANNOT be resolved
#  locally and escalates to the transplant board, which makes the binding call. Synthetic.

tx:donor-9 a tx:Donor ; tx:activeMalignancy true .

#  Autonomy scopes (decision-authority ceilings).
tx:scope-recipient a hol:Scope ; rdfs:label "Recipient-centre autonomy"@en ;
    hol:maxSeverity risk:Breach .
tx:scope-board a hol:Scope ; rdfs:label "Transplant-board autonomy (apex)"@en ;
    hol:maxSeverity risk:Critical .

#  LOCAL decision: realises Critical within a Breach-ceiling scope -> must escalate.
tx:m4-decision a hol:DecisionHolon ;
    hol:optionSpace tx:opt-accept , tx:opt-decline ;
    hol:chosen tx:opt-decline ;
    hol:decidedBy tx:surgeon-1 ;
    hol:rationale "absolute contraindication present (constitutional risk)" ;
    hol:constrainedBy risk:Critical ;
    hol:withinScope tx:scope-recipient ;
    hol:escalatedTo tx:board-decision .
tx:opt-accept a hol:Option ;
    hol:rejectedBecause "absolute contraindication present (constitutional risk)" .
tx:opt-decline a hol:Option .

#  APEX decision: the board makes the binding call. Its ceiling is Critical, so the
#  escalation shape does not fire on it (3 > 3 is false).
tx:board-decision a hol:DecisionHolon ;
    hol:optionSpace tx:opt-confirm-decline , tx:opt-override ;
    hol:chosen tx:opt-confirm-decline ;
    hol:decidedBy tx:role-board ;
    hol:rationale "constitutional matter (absoluteContraindication) escalated to the board apex" ;
    hol:constrainedBy risk:Critical ;
    hol:withinScope tx:scope-board ;
    hol:triggeredBy tx:constitutional-event .
tx:opt-confirm-decline a hol:Option .
tx:opt-override a hol:Option ;
    hol:rejectedBecause "override rejected: a constitutional contraindication is absolute" .

tx:constitutional-event a hol:Event ; hol:condition "absoluteContraindication" .
```

- [ ] **Step 3c: Create the leak example `examples/transplant/transplant-escalation-leak.ttl`**

```turtle
@prefix tx:   <https://example.org/transplant#> .
@prefix hol:  <https://w3id.org/etkl/hol#> .
@prefix risk: <https://w3id.org/etkl/risk#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

#  NEGATIVE: a constitutional matter resolved within local autonomy. The local decision
#  realises risk:Critical within a Breach-ceiling scope but has NO hol:escalatedTo. The
#  escalation shape MUST flag this (Critical 3 > Breach 2, not escalated). MUST FAIL.

tx:scope-recipient a hol:Scope ; rdfs:label "Recipient-centre autonomy"@en ;
    hol:maxSeverity risk:Breach .

tx:m4-decision a hol:DecisionHolon ;
    hol:optionSpace tx:opt-accept , tx:opt-decline ;
    hol:chosen tx:opt-decline ;
    hol:decidedBy tx:surgeon-1 ;
    hol:rationale "absolute contraindication present (constitutional risk)" ;
    hol:constrainedBy risk:Critical ;
    hol:withinScope tx:scope-recipient .
tx:opt-accept a hol:Option ;
    hol:rejectedBecause "absolute contraindication present (constitutional risk)" .
tx:opt-decline a hol:Option .
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_escalation_shacl.py -v`
Expected: PASS — `test_escalation_conformant_passes` and `test_escalation_leak_fails` both pass.

If `test_escalation_leak_fails` does NOT fail (i.e. the leak conforms), the SPARQL cannot see `risk:order`: confirm `risk.ttl` is parsed into the `_data` graph (it is, in Step 1) — this is the deterministic guarantee, so no further action should be needed.

- [ ] **Step 5: Commit**

```bash
git add vocab/shapes/escalation-shapes.ttl examples/transplant/transplant-escalation.ttl examples/transplant/transplant-escalation-leak.ttl tests/test_escalation_shacl.py
git commit -m "feat(shapes): hol:EscalationShape — severity beyond scope must escalate (+ example/leak)"
```

---

## Task 3: capability — `escalate.py`

**Files:**
- Create: `src/iladub/escalate.py`
- Test: `tests/test_escalate.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_escalate.py`:

```python
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from iladub.decision import M4Context, evaluate_m4, build_decision_holon
from iladub.escalate import requires_escalation, escalate, _SEVERITY_ORDER
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH = os.path.join(ROOT, "vocab", "shapes")

HOL = Namespace("https://w3id.org/etkl/hol#")
RISK = Namespace("https://w3id.org/etkl/risk#")
TX = Namespace("https://example.org/transplant#")


def test_requires_escalation_compares_ordinals():
    assert requires_escalation("critical", "breach") is True
    assert requires_escalation("breach", "breach") is False
    assert requires_escalation("breach", "critical") is False


def test_severity_order_mirrors_risk_ttl():
    g = Graph().parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    from_ttl = {}
    for sev, order in g.subject_objects(RISK.order):
        label = str(g.value(sev, Namespace("http://www.w3.org/2000/01/rdf-schema#").label))
        from_ttl[label] = int(order)
    assert from_ttl == _SEVERITY_ORDER


def test_escalate_emits_lineage_and_apex_decision():
    out = escalate(TX["m4-decision"], "critical",
                   new_subject=TX["board-decision"], scope=TX["scope-board"])
    g = out.graph
    assert (TX["m4-decision"], HOL.escalatedTo, TX["board-decision"]) in g
    assert (TX["board-decision"], RDF.type, HOL.DecisionHolon) in g
    assert (TX["board-decision"], HOL.constrainedBy, RISK.Critical) in g
    assert (TX["board-decision"], HOL.withinScope, TX["scope-board"]) in g
    assert (TX["board-decision"], HOL.triggeredBy, None) not in g or \
        len(list(g.objects(TX["board-decision"], HOL.triggeredBy))) == 1
    assert out.apex_subject == TX["board-decision"]
    assert len(list(g.objects(TX["board-decision"], HOL.optionSpace))) == 2
    assert len(list(g.objects(TX["board-decision"], HOL.chosen))) == 1


def test_escalate_override_flips_chosen():
    confirm = escalate(TX["d"], "critical", new_subject=TX["b1"], scope=TX["s"]).chosen
    override = escalate(TX["d"], "critical", new_subject=TX["b2"], scope=TX["s"],
                        override=True).chosen
    assert confirm != override


def test_escalated_graph_conforms():
    # Local decision (declines under a constitutional Critical) + a Breach-ceiling scope.
    local = build_decision_holon(evaluate_m4(M4Context("O", "O", 95, 240,
                                 absolute_contraindication=True)),
                                 subject=TX["m4-decision"])
    local.add((TX["m4-decision"], HOL.withinScope, TX["scope-recipient"]))
    local.add((TX["scope-recipient"], HOL.maxSeverity, RISK.Breach))
    out = escalate(TX["m4-decision"], "critical",
                   new_subject=TX["board-decision"], scope=TX["scope-board"])
    data = local + out.graph
    data.add((TX["scope-board"], HOL.maxSeverity, RISK.Critical))
    data.parse(os.path.join(ONT, "risk.ttl"), format="turtle")  # risk:order for the SPARQL

    shapes = Graph()
    shapes.parse(os.path.join(SH, "hol-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(SH, "escalation-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ONT, "hol.ttl"), format="turtle")
    res = validate(data, shapes, knowledge)
    assert res.conforms, res.report_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_escalate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'iladub.escalate'`.

- [ ] **Step 3: Implement `src/iladub/escalate.py`**

```python
"""Apex escalation: when a decision realizes a severity beyond its declared autonomy
scope, it cannot resolve the matter locally — it escalates to a binding higher-authority
(apex) decision. The vertical (authority-holarchy) analog of reopen.py's temporal lineage.
Standalone: evaluate_m4 and the M4 pipeline are untouched."""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

HOL = Namespace("https://w3id.org/etkl/hol#")
RISK = Namespace("https://w3id.org/etkl/risk#")
TX = Namespace("https://example.org/transplant#")

# Mirrors risk:order in risk.ttl (kept honest by test_severity_order_mirrors_risk_ttl).
_SEVERITY_ORDER = {"ok": 0, "watch": 1, "breach": 2, "critical": 3}
_SEVERITY_IRI = {"ok": RISK.Ok, "watch": RISK.Watch, "breach": RISK.Breach,
                 "critical": RISK.Critical}


def requires_escalation(realized: str, scope_ceiling: str) -> bool:
    """True when a realized severity exceeds the autonomy scope's ceiling."""
    return _SEVERITY_ORDER[realized] > _SEVERITY_ORDER[scope_ceiling]


@dataclass
class EscalationOutcome:
    apex_subject: URIRef
    chosen: URIRef
    graph: Graph


def escalate(local_subject: URIRef, realized_severity: str, *,
             new_subject: URIRef, scope: URIRef,
             agent: URIRef = TX["role-board"],
             event_subject: URIRef = TX["constitutional-event"],
             condition: str = "absoluteContraindication",
             override: bool = False) -> EscalationOutcome:
    """Build the binding apex hol:DecisionHolon and wire authority-holarchy lineage.

    The apex option space is {confirm-decline, override}; chosen = confirm-decline by default
    (override=True selects override, with the other rejectedBecause). The apex decision is
    constrainedBy the realized severity, triggeredBy a constitutional hol:Event, decidedBy the
    board agent, and withinScope `scope`; local_subject hol:escalatedTo new_subject.
    """
    g = Graph()
    confirm = URIRef(str(new_subject) + "-opt-confirm-decline")
    over = URIRef(str(new_subject) + "-opt-override")
    g.add((new_subject, RDF.type, HOL.DecisionHolon))
    g.add((confirm, RDF.type, HOL.Option))
    g.add((over, RDF.type, HOL.Option))
    g.add((new_subject, HOL.optionSpace, confirm))
    g.add((new_subject, HOL.optionSpace, over))

    chosen = over if override else confirm
    rejected = confirm if override else over
    rejected_reason = ("decline overridden by board judgment" if override
                       else "override rejected: a constitutional contraindication is absolute")
    g.add((new_subject, HOL.chosen, chosen))
    g.add((rejected, HOL.rejectedBecause, Literal(rejected_reason)))
    g.add((new_subject, HOL.decidedBy, agent))
    g.add((new_subject, HOL.rationale,
           Literal(f"constitutional matter ({condition}) escalated to the board apex")))
    g.add((new_subject, HOL.constrainedBy, _SEVERITY_IRI[realized_severity]))
    g.add((new_subject, HOL.withinScope, scope))

    g.add((event_subject, RDF.type, HOL.Event))
    g.add((event_subject, HOL.condition, Literal(condition)))
    g.add((new_subject, HOL.triggeredBy, event_subject))

    g.add((local_subject, HOL.escalatedTo, new_subject))
    return EscalationOutcome(apex_subject=new_subject, chosen=chosen, graph=g)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_escalate.py -v`
Expected: PASS (all 5 tests).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/escalate.py tests/test_escalate.py
git commit -m "feat(escalate): escalate() builds binding apex decision + authority-holarchy lineage"
```

---

## Task 4: hol↔HGA alignment module

**Files:**
- Create: `vocab/ontology/hol-hga-align.ttl`
- Modify: `tests/test_hga_alignment.py` (append two tests)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_hga_alignment.py` (the file already defines `_g`, `ONT`, `HOLON`, and imports `Graph, RDFS, URIRef`):

```python
HEV = "http://w3id.org/holon/event/"
HOL_NS = "https://w3id.org/etkl/hol#"


def test_hol_alignment_axioms_present():
    """The hol->HGA module anchors the authority holarchy and event envelope to HGA."""
    g = _g(os.path.join(ONT, "hol-hga-align.ttl"))
    assert (URIRef(HOL_NS + "partOf"), RDFS.subPropertyOf, URIRef(HOLON + "partOf")) in g
    assert (URIRef(HOL_NS + "Event"), RDFS.subClassOf, URIRef(HEV + "HolonEvent")) in g


def test_hol_module_standalone():
    """The core hol vocabulary must NOT hard-depend on the holon: namespace."""
    text = open(os.path.join(ONT, "hol.ttl")).read()
    assert "w3id.org/holon" not in text, "core hol module leaked an HGA dependency"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_hga_alignment.py::test_hol_alignment_axioms_present -v`
Expected: FAIL — `hol-hga-align.ttl` does not exist (parse error).

- [ ] **Step 3: Create `vocab/ontology/hol-hga-align.ttl`**

HGA term IRIs verified against `w3c-cg/holon` HEAD (namespace registry + events/policy/markov/bayesian passes): `holon:partOf`, `hev:HolonEvent` (`http://w3id.org/holon/event/`), `hmk:PropagationSignal` (`http://w3id.org/holon/markov/`), `hbayes:PolicySelection` (`http://w3id.org/holon/bayesian/`), `hpol:BoundaryPolicy` (`http://w3id.org/holon/policy/`). Every triple subject is a `hol:` term or this module's own ontology IRI; HGA terms appear only as objects (source-ownership boundary).

```turtle
@prefix hol:    <https://w3id.org/etkl/hol#> .
@prefix holon:  <http://w3id.org/holon/> .
@prefix hev:    <http://w3id.org/holon/event/> .
@prefix hmk:    <http://w3id.org/holon/markov/> .
@prefix hpol:   <http://w3id.org/holon/policy/> .
@prefix hbayes: <http://w3id.org/holon/bayesian/> .
@prefix owl:    <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms:<http://purl.org/dc/terms/> .

#################################################################
#  OPTIONAL alignment of the hol decision-context vocabulary to the
#  W3C Holon CG ontology (HGA). ALIGNMENT, NOT IMPORT: rdfs:subClassOf /
#  rdfs:subPropertyOf / rdfs:seeAlso only; no owl:imports. hol.ttl stays
#  standalone and reasoner-free. HGA terms appear ONLY as objects
#  (CLAUDE.md § Source ownership). Anchor: HGA holon:/hev:/hmk:/hpol:/hbayes:
#  (http://w3id.org/holon/... — http, not https). Escalation-scoped.
#################################################################

<https://w3id.org/etkl/hol/hga-alignment> a owl:Ontology ;
    dcterms:title "hol → HGA alignment (W3C Holon CG)"@en ;
    dcterms:description """Optional, separately loadable alignment of hol to HGA. The authority
holarchy is HGA containment; the hol event is an HGA event envelope; iladub's accountable
DecisionHolon, escalation edge, and autonomy scope are gap-fills HGA has no equivalent for
(recorded as rdfs:seeAlso, not subclass)."""@en ;
    dcterms:creator "François Rosselet" ;
    dcterms:created "2026-06-30"^^xsd:date ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    owl:versionInfo "0.1.0" ;
    rdfs:seeAlso <https://w3id.org/etkl/hol> , <https://github.com/w3c-cg/holon> .

#  The authority holarchy is HGA holon containment (same anchor risk:withinContext uses).
hol:partOf rdfs:subPropertyOf holon:partOf .

#  An hol:Event is an HGA event envelope — defer the event substrate to the CG.
hol:Event rdfs:subClassOf hev:HolonEvent .

#  iladub GAP-FILLERS over HGA — seeAlso, NOT subclass (HGA has no equivalent):
hol:escalatedTo rdfs:seeAlso hmk:PropagationSignal ;
    rdfs:comment "HGA propagates a hmk:PropagationSignal (Distress->Resolution) and routes it by hpol: policy, but does not require the resolution to be an accountable decision. hol:escalatedTo records that the propagation was resolved by an accountable apex hol:DecisionHolon — enforced by hol:EscalationShape."@en .

hol:DecisionHolon rdfs:seeAlso hbayes:PolicySelection ;
    rdfs:comment "HGA's hbayes:PolicySelection is a belief-driven choice, not an accountable, agent-attributed, re-evaluable deliberation. hol:DecisionHolon is iladub's gap-fill — stronger than HGA's confidence/belief gate."@en .

hol:Scope rdfs:seeAlso hpol:BoundaryPolicy ;
    rdfs:comment "HGA hpol:BoundaryPolicy governs access (who may read/write a holon), NOT decision autonomy. hol:Scope (with hol:maxSeverity) bounds the severity a decision-maker may resolve before escalating — a distinct concept."@en .
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_hga_alignment.py tests/test_source_ownership.py -v`
Expected: PASS — alignment axioms present; `test_source_ownership` confirms the new module points outward only (no HGA IRI as a subject) and core ontologies remain standalone.

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/hol-hga-align.ttl tests/test_hga_alignment.py
git commit -m "feat(align): hol-hga-align.ttl — anchor hol to HGA (escalation-scoped, points outward)"
```

---

## Final verification

- [ ] **Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: all pass (the prior 122 passed / 4 skipped, plus the new escalation + alignment tests).

- [ ] **Dispatch the final code review** (subagent-driven-development closes with a whole-implementation review), then use `superpowers:finishing-a-development-branch`.

---

## Self-review notes (author)

- **Spec coverage:** component 1 (vocab) → Task 1; component 2 (hol-hga-align) → Task 4; component 3 (escalation-shapes) → Task 2; component 4 (escalate.py) → Task 3; component 5 (examples) → Task 2; component 6 (tests) → Tasks 1–4. All covered.
- **Naming deviation from spec:** the spec wrote `esc:EscalationShape` as shorthand; the plan uses `hol:EscalationShape` in `escalation-shapes.ttl` (no new namespace — matches the established `hol-shapes.ttl` pattern of hol:-named shapes). Flagged for review.
- **Determinism:** the SPARQL reads `risk:order`; both SHACL tests merge `risk.ttl` into the *data* graph so the ordinals are visible regardless of pySHACL ont-graph query semantics.
- **Boundary:** Task 1 keeps `hol.ttl` standalone; only Task 4's `hol-hga-align.ttl` names HGA terms, as objects; all guarded by `tests/test_source_ownership.py`.
