# Grounding Uniform Value Membrane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the contract's value-constraint membrane on the exact-match grounding path too (close a soundness asymmetry), and add coverage proving the tight value oracles `sh:in`/`sh:pattern` ground-on-match/member and quarantine-on-miss through the real `ground_concept`.

**Architecture:** One change to `_grounds_to` in `src/iladub/ground.py` (unify the non-scheme branch so a declared value constraint gates both exact and propose paths), plus tests in `tests/test_grounding_value_constraints.py` using test-local augmented shapes. No production code beyond `_grounds_to`; no shared shape file touched.

**Tech Stack:** Python 3.12, rdflib, pySHACL (via the shipped `_value_conforms`), pytest.

## Global Constraints

- **§8 gate:** the oracle stays SHACL-membrane dispose (closed-world) over the contract's declared constraints; NO tuned constant. The change makes the membrane UNIFORM — legality (SHACL conformance) gates admission regardless of how the field was identified; confidence never does.
- **No shared-shape changes (the Task-4 lesson, load-bearing):** `examples/transplant/offer-shapes.ttl` is the shared M4 conformance shape — do NOT modify it. The asymmetry test reuses the EXISTING EF `[0,100]` constraint (M4-safe); the sh:in/sh:pattern coverage uses TEST-LOCAL augmented shapes (built in the test, never written to disk).
- **§7:** non-conforming / unconstrained values quarantine as `CandidateConcept` propositions, never dropped.
- **Probe-verified:** the uniform-membrane change is non-breaking (30 grounding/feed tests green under it); sh:in/sh:pattern already ground/reject correctly via `_value_conforms`.
- **Testing:** run ONLY via `./.venv/bin/python -m pytest` (bare python3 uses the wrong rdflib).
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `iladub-uniform-value-membrane`.

---

### Task 1: Uniform value membrane + sh:in/sh:pattern coverage

**Files:**
- Modify: `src/iladub/ground.py` (`_grounds_to`)
- Test: `tests/test_grounding_value_constraints.py`

**Interfaces:**
- Consumes: `_property_shape`, `_has_value_constraint`, `_value_conforms`, `ground_concept`, `SH` (all existing in `ground.py`); `GroundingProposal`, `FakeGroundingProposer`; the existing test helpers `_shapes()`, `_terms()`, `TX`, `OFFER`, `CONTRACT`.
- Produces: `_grounds_to` with the value-constraint check applied on BOTH exact and propose paths for a constrained non-scheme field.

- [ ] **Step 1: Write the failing test (the asymmetry RED-check)**

Append to `tests/test_grounding_value_constraints.py`. First add the imports it needs near the top import block (after the existing `from rdflib...` line):

```python
from rdflib import BNode
from rdflib.collection import Collection
from iladub.ground import SH
```

Then append the tests:

```python
def _noop():
    return FakeGroundingProposer(GroundingProposal(None, str(TX) + "x", 0.0, "n/a", "urn:iladub:suggester/fake"))


def test_exact_path_enforces_value_constraint():
    # "ejectionFraction" EXACT-matches the EF field -> is_exact, proposer never consulted.
    # Uniform membrane: an in-range value grounds; an out-of-range value quarantines (was: grounded).
    c = load_contract(CONTRACT); terms = _terms(); shapes = _shapes()
    for value, expect in [("60", "grounded"), ("999", "proposed")]:
        g = Graph()
        out = ground_concept(SurfaceConcept("ejectionFraction", value, "r0"), c, OFFER, _noop(), terms, shapes, g)
        assert out == expect, (value, out)
    # the out-of-range exact value emitted NO grounded node
    g = Graph()
    ground_concept(SurfaceConcept("ejectionFraction", "999", "r0"), c, OFFER, _noop(), terms, shapes, g)
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))


def _augmented_shapes(property_iri, add_constraint):
    """offer-shapes.ttl + an extra property shape on `property_iri` (built in-memory; the committed
    file is NEVER modified). add_constraint(shapes, ps) attaches the value constraint to ps."""
    s = _shapes()
    node = next(s.subjects(SH.targetClass, TX.OrganOffer))
    ps = BNode()
    s.add((node, SH.property, ps))
    s.add((ps, SH.path, URIRef(property_iri)))
    add_constraint(s, ps)
    return s


def test_sh_pattern_grounds_on_match_quarantines_on_miss():
    # header "Size" -> propose f-size (not exact); sh:pattern gates the value.
    c = load_contract(CONTRACT); terms = _terms()
    size = next(f for f in c.fields if f.fills_property.endswith("sizeMetric"))
    shapes = _augmented_shapes(str(TX) + "sizeMetric",
                               lambda s, ps: s.add((ps, SH.pattern, Literal("^[0-9]+(kg|cm)$"))))
    p = FakeGroundingProposer(GroundingProposal(size.iri, str(TX) + "Magnitude", 0.9, "size", "urn:iladub:suggester/fake"))
    for value, expect in [("78kg", "grounded"), ("big", "proposed")]:
        g = Graph()
        out = ground_concept(SurfaceConcept("Size", value, "r0"), c, OFFER, p, terms, shapes, g)
        assert out == expect, (value, out)


def test_sh_in_grounds_on_member_quarantines_on_non_member():
    # header "Sero" -> propose f-serology (not exact); sh:in (enum) gates the value.
    c = load_contract(CONTRACT); terms = _terms()
    sero = next(f for f in c.fields if f.fills_property.endswith("serology"))
    def add_enum(s, ps):
        lst = BNode(); Collection(s, lst, [Literal("positive"), Literal("negative")])
        s.add((ps, SH["in"], lst))
    shapes = _augmented_shapes(str(TX) + "serology", add_enum)
    p = FakeGroundingProposer(GroundingProposal(sero.iri, str(TX) + "Category", 0.8, "sero", "urn:iladub:suggester/fake"))
    for value, expect in [("negative", "grounded"), ("unknown", "proposed")]:
        g = Graph()
        out = ground_concept(SurfaceConcept("Sero", value, "r0"), c, OFFER, p, terms, shapes, g)
        assert out == expect, (value, out)
```

- [ ] **Step 2: Run to verify the asymmetry test FAILS (and the coverage tests pass)**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -k "exact_path or sh_pattern or sh_in" -v`
Expected: `test_exact_path_enforces_value_constraint` FAILS — against the shipped `_grounds_to`, exact-matched "999" grounds (returns `"grounded"`, not `"proposed"`). `test_sh_pattern_...` and `test_sh_in_...` PASS already (the propose-path value-constraint membrane from the prior slice already enforces sh:pattern/sh:in) — that is expected; they are coverage for existing behavior.

- [ ] **Step 3: Make the membrane uniform**

In `src/iladub/ground.py`, replace the `_grounds_to` body (keep the signature). Change the docstring + the non-scheme branch:

```python
def _grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class):
    """The grounding TARGET for iladub:groundsTo, or None if REJECTED (→ quarantine).

    Scheme-bound field: the SKOS concept whose prefLabel == value (membership is the oracle).
    Non-scheme field that declares a value constraint: the SHACL value membrane is the oracle — the
    value MUST conform, whether the field was identified by exact label match OR by a model proposal
    (legality gates admission uniformly). Non-scheme field WITHOUT a value constraint: an exact label
    match grounds (field-identity is the oracle); a bare proposal has no oracle → None (quarantine)."""
    if field.scheme is not None:
        term = scheme_member(concept.value, field.scheme, terms)
        return URIRef(term) if term else None
    ps = _property_shape(contract_shapes, field.fills_property)
    if ps is not None and _has_value_constraint(contract_shapes, ps):
        return (URIRef(field.fills_property)
                if _value_conforms(offer_uri, target_class, field.fills_property, concept.value,
                                   contract_shapes)
                else None)
    return URIRef(field.fills_property) if is_exact else None
```

- [ ] **Step 4: Run to verify all pass**

Run: `./.venv/bin/python -m pytest tests/test_grounding_value_constraints.py -v`
Expected: all pass (the asymmetry test now GREEN; pattern/enum coverage GREEN; the shipped value-constraint tests unchanged).

- [ ] **Step 5: Run the full suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/ -q`
Expected: all pass. The change is confined to `_grounds_to`'s non-scheme branch; scheme + unconstrained paths are unchanged, `ground_concept`'s caller is unchanged, and M4 does not use `ground_concept`. (A benign rdflib "Failed to convert Literal lexical form" warning on the "high"/"999"-style ill-typed cases is expected.)

- [ ] **Step 6: Commit**

```bash
git add src/iladub/ground.py tests/test_grounding_value_constraints.py
git commit -m "feat(iladub): uniform value membrane — exact-match path now enforces the field's value constraint; sh:in/sh:pattern coverage"
```

---

## Self-Review

**Spec coverage:**
- Uniform value membrane (exact path enforces the constraint) → Task 1 Step 3. ✓
- Asymmetry RED-check (exact-EF "60" grounds, "999" quarantines) → Task 1 Step 1/2 (RED) + Step 4 (GREEN). ✓
- sh:pattern coverage (ground on match / quarantine on miss) → Task 1 (`test_sh_pattern_...`). ✓
- sh:in coverage (ground on member / quarantine on non-member) → Task 1 (`test_sh_in_...`). ✓
- No shared-shape changes; test-local augmented shapes; EF reused for the asymmetry test → Global Constraints + `_augmented_shapes` (in-memory) + the EF test using `_shapes()` unchanged. ✓
- Scheme / unconstrained / propose paths unchanged → the new `_grounds_to` preserves them; full-suite green (Step 5). ✓
- §7 residue quarantined → the rejection assertions (`"proposed"`, no `GroundedNode`). ✓

**Placeholder scan:** none — full code + exact commands, probe-validated (the membrane change was run against the grounding suites; sh:in/sh:pattern were run through `_value_conforms` and `ground_concept`).

**Type consistency:** `_grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class)` signature unchanged; `_augmented_shapes(property_iri, add_constraint)`, `ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g)`, `SurfaceConcept(text, value, region)`, `GroundingProposal(field_iri, anchor_iri, confidence, rationale, suggester_iri)` used identically and match the shipped signatures. ✓
