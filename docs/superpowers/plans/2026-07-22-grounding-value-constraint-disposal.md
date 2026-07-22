# Grounding Value-Constraint Disposal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the knowledge-grounding oracle so a NEURAL proposal to a value-constrained (non-scheme) contract field is verified by the contract's SHACL value constraints and grounded when it conforms, instead of always quarantined.

**Architecture:** For a non-scheme, non-exact field, `_grounds_to` consults the contract's SHACL property shape: if the field declares a value constraint and the datatype-cast value conforms to a *focused* single-field shape (pySHACL), it grounds; otherwise it quarantines. Scheme + exact branches unchanged. Soundness is the contract author's declared constraint strength, recorded transparently in the `PromotionDecision` rationale.

**Tech Stack:** Python 3.12, rdflib, pySHACL (via `iladub.validate.validate`), pytest. No new dependency, no new contract vocabulary.

## Global Constraints

- **§8 gate:** NEURAL propose (shipped `GroundingProposer`) → **SHACL-membrane dispose** (closed-world constraint over the field's focused value shape — the §8 "constraint → SHACL" membrane) → promote (`iladub:PromotionDecision`, §3). No tuned constant; **legality (SHACL conformance) gates admission, confidence never does.**
- **Soundness relocated, not relaxed:** the oracle enforces exactly what the contract declares. A field with only cardinality (or no shape) declares nothing to verify → quarantine (preserved). Verification strength (scheme/enum/pattern vs datatype/range) is the contract author's explicit choice, recorded in the rationale.
- **Only emit what the source supports (§7):** non-conformant / out-of-range / unconstrained → quarantined `CandidateConcept`, never dropped, never faked.
- **Focused-shape validation (correctness):** validate against a fresh node shape targeting the offer that carries ONLY this field's `sh:property` — NEVER the full `OrganOfferShape` (its other `sh:minCount 1` properties would fail a scratch offer and wrongly quarantine).
- **Testing:** run ONLY via `./.venv/bin/python -m pytest` (bare `python3` uses the wrong rdflib).
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `iladub-grounding-value-constraints`.

---

### Task 1: Value-constraint shape + property-shape reader

**Files:**
- Modify: `examples/transplant/offer-shapes.ttl` (add EF datatype+range constraint)
- Modify: `src/iladub/ground.py` (add `SH` namespace, `_VALUE_CONSTRAINTS`, `_property_shape`, `_has_value_constraint`)
- Test: `tests/test_grounding_value_constraints.py`

**Interfaces:**
- Produces:
  - `_property_shape(shapes: Graph, property_iri: str) -> BNode | None` — the `sh:property` node whose `sh:path == property_iri`.
  - `_has_value_constraint(shapes: Graph, ps) -> bool` — True iff `ps` declares any value constraint (datatype/in/pattern/min/max/length), i.e. anything beyond cardinality/path.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_grounding_value_constraints.py
from rdflib import Graph, Namespace
from iladub.ground import _property_shape, _has_value_constraint

TX = Namespace("https://example.org/transplant#")


def _shapes():
    return Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")


def test_ef_property_shape_has_value_constraint():
    s = _shapes()
    ps = _property_shape(s, str(TX) + "ejectionFraction")
    assert ps is not None
    assert _has_value_constraint(s, ps) is True          # datatype + range declared


def test_unconstrained_field_has_no_property_shape():
    s = _shapes()
    # causeOfDeath has no property shape at all -> nothing to verify -> quarantine downstream
    assert _property_shape(s, str(TX) + "causeOfDeath") is None


def test_cardinality_only_is_not_a_value_constraint():
    # organ shape is cardinality-only (min/maxCount) -> not a value constraint
    s = _shapes()
    ps = _property_shape(s, str(TX) + "organ")
    assert ps is not None
    assert _has_value_constraint(s, ps) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -v`
Expected: FAIL — `ImportError: cannot import name '_property_shape'` (and EF has no constraint yet).

- [ ] **Step 3: Write minimal implementation**

Add the EF value constraint to `examples/transplant/offer-shapes.ttl` — add the `xsd` prefix at the top and replace the EF property line:

```turtle
@prefix tx:   <https://example.org/transplant#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
```

Replace `sh:property [ sh:path tx:ejectionFraction ; sh:maxCount 1 ] .` with:

```turtle
    sh:property [ sh:path tx:ejectionFraction ; sh:maxCount 1 ;
                  sh:datatype xsd:decimal ; sh:minInclusive 0 ; sh:maxInclusive 100 ] .
```

In `src/iladub/ground.py`, add the SHACL namespace + reader helpers. After the existing namespace block (`ETKL`, `ILADUB`, `DEC`), add:

```python
from rdflib.namespace import XSD

SH = Namespace("http://www.w3.org/ns/shacl#")

# Value constraints (as opposed to cardinality/path) — presence of any means the contract
# declares something the SHACL membrane can verify a proposed value against.
_VALUE_CONSTRAINTS = (SH.datatype, SH["in"], SH.pattern,
                      SH.minInclusive, SH.maxInclusive, SH.minExclusive, SH.maxExclusive,
                      SH.minLength, SH.maxLength)


def _property_shape(shapes, property_iri):
    """The sh:property node whose sh:path == property_iri, or None."""
    for ps in shapes.subjects(SH.path, URIRef(property_iri)):
        return ps
    return None


def _has_value_constraint(shapes, ps):
    """True iff the property shape declares any value constraint (not just cardinality/path)."""
    return any((ps, p, None) in shapes for p in _VALUE_CONSTRAINTS)
```

Ensure `XSD` is available (the import above adds it).

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add examples/transplant/offer-shapes.ttl src/iladub/ground.py tests/test_grounding_value_constraints.py
git commit -m "feat(iladub): EF value constraint + property-shape reader (_property_shape/_has_value_constraint) — grounding B slice"
```

---

### Task 2: `_value_conforms` — the focused-shape SHACL oracle

**Files:**
- Modify: `src/iladub/ground.py` (add `_value_conforms`)
- Test: `tests/test_grounding_value_constraints.py`

**Interfaces:**
- Consumes: `_property_shape` (Task 1); `iladub.validate.validate`.
- Produces: `_value_conforms(offer_uri, target_class: str, property_iri: str, value: str, shapes: Graph) -> bool` — True iff the datatype-cast value conforms to the field's focused value-constraint shape.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_grounding_value_constraints.py
from rdflib import URIRef
from iladub.ground import _value_conforms

TXO = "https://example.org/transplant#OrganOffer"
OFFER = URIRef("urn:test:offer1")


def test_in_range_decimal_conforms():
    assert _value_conforms(OFFER, TXO, str(TX) + "ejectionFraction", "55", _shapes()) is True


def test_out_of_range_does_not_conform():
    assert _value_conforms(OFFER, TXO, str(TX) + "ejectionFraction", "150", _shapes()) is False


def test_wrong_datatype_does_not_conform():
    assert _value_conforms(OFFER, TXO, str(TX) + "ejectionFraction", "high", _shapes()) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -k conform -v`
Expected: FAIL — `ImportError: cannot import name '_value_conforms'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/ground.py`:

```python
def _value_conforms(offer_uri, target_class, property_iri, value, shapes):
    """SHACL-membrane oracle (§8, closed-world): does `value` satisfy the field's declared value
    constraints? Validates against a FOCUSED node shape targeting the offer that carries ONLY this
    field's sh:property (never the full node shape, whose other required properties would fail a
    scratch offer). The value is cast to the shape's sh:datatype: an ill-typed lexical form (e.g.
    'high' as xsd:decimal) fails sh:datatype -> correctly non-conformant."""
    from .validate import validate

    ps = _property_shape(shapes, property_iri)
    if ps is None:
        return False
    dt = shapes.value(ps, SH.datatype)

    focused = Graph()
    shape = BNode()
    focused.add((shape, RDF.type, SH.NodeShape))
    focused.add((shape, SH.targetNode, offer_uri))
    focused.add((shape, SH.property, ps))
    focused += shapes.cbd(ps)                       # bring the property shape's own constraints

    data = Graph()
    data.add((offer_uri, RDF.type, URIRef(target_class)))
    val = Literal(value, datatype=dt) if dt is not None else Literal(value)
    data.add((offer_uri, URIRef(property_iri), val))

    return validate(data, focused, Graph()).conforms
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -v`
Expected: PASS (6 passed). If `test_in_range_decimal_conforms` fails because pySHACL reports a violation from an unrelated shape, confirm the focused shape carries ONLY `ps` (the CBD of the EF property bnode) and `sh:targetNode OFFER` — no `sh:targetClass`.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/ground.py tests/test_grounding_value_constraints.py
git commit -m "feat(iladub): _value_conforms — focused-shape SHACL oracle for a proposed field value (grounding B slice)"
```

---

### Task 3: Wire the oracle into grounding — `_grounds_to`, typed emission, rationale, end-to-end DoD

**Files:**
- Modify: `src/iladub/ground.py` (`_grounds_to` signature + value-constraint branch; `_emit_grounded` typed literal; `ground_concept` threading + rationale)
- Modify: `tests/test_grounding.py` (retarget the unconstrained-quarantine test to `causeOfDeath`; update `_build_offer` for EF now grounding)
- Test: `tests/test_grounding_value_constraints.py` (end-to-end grounding pins)

**Interfaces:**
- Consumes: `_property_shape`, `_has_value_constraint` (Task 1); `_value_conforms` (Task 2).
- Produces: `_grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class)`; `_emit_grounded(..., datatype=None)`; `ground_concept` unchanged public signature (`ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g)`).

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_grounding_value_constraints.py
from iladub.ground import SurfaceConcept, load_contract, ground_concept
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer
from rdflib import RDF, Literal
from rdflib.namespace import XSD

ILA = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
CONTRACT = "examples/transplant/offer-contract.ttl"


def _terms():
    return Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")


def _ef_proposer(value_field="ejectionFraction"):
    c = load_contract(CONTRACT)
    ef = next(f for f in c.fields if f.fills_property.endswith(value_field))
    return c, FakeGroundingProposer(GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9,
                                                      "cardiac EF", "urn:iladub:suggester/fake"))


def test_in_range_ef_grounds_with_typed_literal_and_mode_rationale():
    c, p = _ef_proposer(); g = Graph()
    out = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "grounded"
    gn = list(g.subjects(RDF.type, ILA.GroundedNode))
    assert gn and g.value(gn[0], ILA.groundsTo) == URIRef(str(TX) + "ejectionFraction")
    # typed literal emission (xsd:decimal), not a bare string
    assert Literal("55", datatype=XSD.decimal) in list(g.objects(OFFER, URIRef(str(TX) + "ejectionFraction")))
    # rationale records the weaker verification mode
    pd = list(g.subjects(RDF.type, ILA.PromotionDecision))[0]
    assert "value-constraint" in str(g.value(pd, DEC.rationale)).lower()


def test_out_of_range_ef_quarantines():
    c, p = _ef_proposer(); g = Graph()
    out = ground_concept(SurfaceConcept("EF", "150", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed" and not list(g.subjects(RDF.type, ILA.GroundedNode))


def test_wrong_type_ef_quarantines():
    c, p = _ef_proposer(); g = Graph()
    out = ground_concept(SurfaceConcept("EF", "high", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed" and not list(g.subjects(RDF.type, ILA.GroundedNode))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -k "ef_" -v`
Expected: FAIL — `test_in_range_ef_grounds...` returns `"proposed"` (the oracle is not wired into `_grounds_to` yet).

- [ ] **Step 3: Write minimal implementation**

In `src/iladub/ground.py`, extend `_grounds_to` (replace the current body):

```python
def _grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class):
    """The grounding TARGET for iladub:groundsTo, or None if REJECTED (→ quarantine).

    Scheme-bound field: the SKOS concept whose prefLabel == value (membership is the oracle).
    Non-scheme + exact label match: the property (exact match is the oracle). Non-scheme,
    non-exact: the field's contract SHACL value constraint is the oracle (§8 membrane) —
    grounds iff the shape declares a value constraint AND the value conforms; else None.
    An unconstrained field has nothing to verify → None (quarantine): confidence≠validity (§7)."""
    if field.scheme is not None:
        term = scheme_member(concept.value, field.scheme, terms)
        return URIRef(term) if term else None
    if is_exact:
        return URIRef(field.fills_property)
    ps = _property_shape(contract_shapes, field.fills_property)
    if (ps is not None and _has_value_constraint(contract_shapes, ps)
            and _value_conforms(offer_uri, target_class, field.fills_property, concept.value, contract_shapes)):
        return URIRef(field.fills_property)
    return None
```

Extend `_emit_grounded` to type the literal (add a `datatype=None` parameter, replace the value-emit line):

```python
def _emit_grounded(g, concept, offer_uri, target_class, field, grounds_to, cand, agent, confidence, rationale, datatype=None):
```

Replace its final value-emit line:

```python
    g.add((offer_uri, RDF.type, URIRef(target_class)))
    val = Literal(concept.value, datatype=datatype) if datatype is not None else Literal(concept.value)
    g.add((offer_uri, URIRef(field.fills_property), val))
    return gn
```

Update `ground_concept` (the tail, from `grounds_to = ...`):

```python
    grounds_to = _grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, contract.target_class)
    if grounds_to is None:                                  # unverifiable / rejected → quarantine
        return "proposed"
    ps = _property_shape(contract_shapes, field.fills_property)
    datatype = contract_shapes.value(ps, SH.datatype) if ps is not None else None
    if field.scheme is None and not is_exact:               # grounded via the value-constraint membrane
        rationale = ("%s [grounded via SHACL value-constraint admissibility, weaker than "
                     "scheme-identity]" % rationale)
    _emit_grounded(g, concept, offer_uri, contract.target_class, field, grounds_to,
                   cand, agent, confidence, rationale, datatype)
    return "grounded"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -v`
Expected: PASS (9 passed).

- [ ] **Step 5: Update the shipped grounding tests (retarget the boundary + fix the end-to-end)**

In `tests/test_grounding.py`:

(a) Retarget `test_neural_to_unconstrained_field_quarantined` from EF to `causeOfDeath` (EF now grounds; `causeOfDeath` is genuinely unconstrained — no property shape). Replace its body:

```python
def test_neural_to_unconstrained_field_quarantined():
    """A NEURAL proposal to causeOfDeath (no scheme, no value constraint in the shape) has no
    oracle → must quarantine, never ground (the preserved soundness boundary)."""
    c = load_contract(CONTRACT); g = Graph()
    cod = next(f for f in c.fields if f.fills_property.endswith("causeOfDeath"))
    p = FakeGroundingProposer(GroundingProposal(cod.iri, str(TX)+"Category", 0.99, "cause of death",
                                                "urn:iladub:suggester/fake"))
    out = ground_concept(SurfaceConcept("COD", "MVA", "r5"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))
```

(b) In `_build_offer` and `test_end_to_end_grounds_and_quarantines`, EF now GROUNDS (value "55" ∈ [0,100]). Update the expected `out` dict so `"ef": "grounded"` (was `"proposed"`), and adjust any downstream count of grounded vs proposed nodes accordingly. Run the test to see the exact expected dict and update it to match the now-correct behaviour (EF grounded; `wrong`/`novel` still proposed).

- [ ] **Step 6: Run the full grounding suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py tests/test_grounding_value_constraints.py -q`
Expected: all pass — scheme/exact/invariant behaviour unchanged; EF grounds; unconstrained `causeOfDeath` quarantines.

- [ ] **Step 7: Run the whole suite (broader no-regression)**

Run: `./.venv/bin/python -m pytest tests/ -q`
Expected: all pass (the change is additive to the non-scheme/non-exact grounding branch; scheme/exact untouched).

- [ ] **Step 8: Commit**

```bash
git add src/iladub/ground.py tests/test_grounding.py tests/test_grounding_value_constraints.py
git commit -m "feat(iladub): ground value-constrained fields via the SHACL membrane — typed emission + mode rationale; retarget boundary test (grounding B slice, DoD)"
```

---

## Self-Review

**Spec coverage:**
- Contract shapes carry value constraints (EF datatype+range) → Task 1. ✓
- Property-shape reader (`_property_shape`/`_has_value_constraint`) → Task 1. ✓
- Focused-shape SHACL oracle (`_value_conforms`, targetNode + CBD, not full node shape) → Task 2. ✓
- Typed-literal emission → Task 3 (`_emit_grounded` datatype). ✓
- Rationale records the weaker mode → Task 3 (ground_concept). ✓
- Oracle wired into `_grounds_to`, scheme/exact unchanged → Task 3. ✓
- Tests: positive in-range grounds (RED, T3), out-of-range quarantines (T2 unit + T3 e2e), wrong-type quarantines (T2 + T3), unconstrained preserved-quarantine (retargeted, T3 Step 5), typed literal (T3), rationale (T3), scheme/exact regression (T3 Step 6–7). ✓
- Soundness relocated to contract; unconstrained → quarantine preserved → Global Constraints + Task 3 Step 5. ✓

**Placeholder scan:** none — every step has full code + exact commands. Task 3 Step 5(b) asks the implementer to read the actual `_build_offer` expected dict and update it to the now-correct values (EF grounded); the CHANGE (EF: proposed→grounded) is stated exactly, only the surrounding dict literal is environment-read.

**Type consistency:** `_property_shape(shapes, property_iri)->BNode|None`, `_has_value_constraint(shapes, ps)->bool`, `_value_conforms(offer_uri, target_class, property_iri, value, shapes)->bool`, `_grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class)`, `_emit_grounded(..., datatype=None)`, `ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g)` (public signature unchanged) are used identically across tasks and match `validate(data, shapes, knowledge)->ValidationResult(.conforms)`. ✓
