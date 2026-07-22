# Grounding — value-constraining-shape disposal (NEURAL, contract-membrane oracle)

**Date:** 2026-07-22
**Status:** Design — approved for spec (brainstorm 2026-07-22).
**Slice:** Extend the knowledge-grounding oracle (`2026-07-19-knowledge-first-grounding-design.md`) from
"SKOS-scheme membership or exact-match" to **the contract's SHACL value constraints**, so a NEURAL
grounding proposal to a value-constrained (non-scheme) field can be *verified and grounded* instead of
always quarantined. Follow-up **(b)** of the grounding design.

**Gate context (CLAUDE.md §8):** NEURAL propose (the shipped `GroundingProposer`) → **SHACL-membrane
dispose** (closed-world constraint over the contract's node shape — the §8 "constraint → SHACL"
membrane) → promote (an accountable `iladub:PromotionDecision`, §3). No tuned constant; legality
(SHACL conformance) gates admission, confidence never does.

---

## 1. The decision (one sentence)

For a **non-scheme** contract field whose proposal is **not** an exact label match, extend `_grounds_to`
from "reject (exact-only)" to: ground iff the field's property shape declares **≥1 value constraint**
(beyond cardinality) **and** the (datatype-cast) value **conforms** to that field's focused
value-constraint shape under pySHACL; otherwise quarantine. The scheme branch (SKOS membership) and the
exact branch are unchanged.

## 2. The soundness stance (the load-bearing decision — relocate, don't relax)

The shipped grounding slice set a **review-hardened boundary** (its Task-3 catch): *ground only what the
contract can verify — scheme members + exact matches; a bare datatype "can't tell a valid EF number from
pack-years", so a NEURAL guess to an unconstrained field is confidence≠validity and must stay a
`CandidateConcept` proposition.* Grounding on datatype/range appears to re-open that trap.

**It does not, because the soundness decision is relocated to the contract — where the membrane spec
belongs — not hidden in the oracle.** The oracle for a non-scheme field is **pySHACL conformance to the
contract's node shape**. Consequences:

- **The contract author declares the verification strength, per field.** A field constrained to
  `xsd:decimal [0,100]` gets range-strength verification *because the contract declared that admissible*.
  A field with `sh:in`/`sh:pattern` gets set/format-strength. This is an explicit, auditable,
  contract-level choice — not a blanket oracle policy asserting "range = correct".
- **"Unconstrained → quarantine" is preserved, not removed.** A property shape with only cardinality
  (`sh:maxCount`) — or a free-text field with no shape — declares **nothing to verify** → `None` →
  quarantine. The boundary moves from "scheme/exact only" to "did the contract declare a value
  constraint?"; it does not vanish.
- **Verification strength is transparent.** The `PromotionDecision` rationale records *which* constraint
  verified the grounding (e.g. "grounded via SHACL value-constraint admissibility [datatype+range
  0–100], weaker than scheme-identity"), so a downstream consumer sees a range-grounding is a
  plausibility-verified admissibility claim, not a scheme-identity claim.
- **Residual risk, named honestly.** A *mislabeled but in-range* value (pack-years 30 ∈ [0,100] proposed
  to EF) would ground — a **field-assignment error by the proposer** that a range cannot catch. This is
  the contract author's declared tolerance (they chose a range, not an enum); it is mitigated by the
  recorded proposer confidence/rationale, the accountable+reversible `PromotionDecision`, and
  provenance-to-region. A contract author wanting tighter verification declares `sh:in`/`sh:pattern`.

This keeps §8 intact (the membrane is SHACL, closed-world; it enforces exactly what the contract
declares — no more, no less) and keeps the strength honest rather than pretending range = scheme.

## 3. Components (each single-purpose)

### 3.1 Contract shapes carry the value constraints (`examples/transplant/offer-shapes.ttl`)

- Give a currently-quarantined field a value constraint to demonstrate newly-grounding:
  `tx:ejectionFraction` → `sh:datatype xsd:decimal ; sh:minInclusive 0 ; sh:maxInclusive 100`.
- Leave `tx:causeOfDeath` genuinely unconstrained (free text, no value shape) as the **preserved
  negative** — still quarantines.
- Standard SHACL only; **no new contract vocabulary**.

### 3.2 Oracle extension (`src/iladub/ground.py`, `_grounds_to`)

Signature gains `contract_shapes, offer_uri`. The scheme branch and the exact branch are byte-identical.
The new non-scheme/non-exact path:

```
if field has a value constraint in contract_shapes AND _value_conforms(offer_uri, prop, value, shapes):
    return URIRef(field.fills_property)
return None                                  # no constraint, or non-conformant → quarantine
```

A helper `_field_value_shape(shapes, property_iri)` locates the `sh:property` whose `sh:path ==
property_iri` and reports whether it declares any value constraint (`sh:in` / `sh:pattern` /
`sh:datatype` / `sh:minInclusive` / `sh:maxInclusive` / `sh:minExclusive` / `sh:maxExclusive` /
`sh:minLength` / `sh:maxLength`) — i.e. anything beyond `sh:minCount`/`sh:maxCount`/`sh:path`.

### 3.3 `_value_conforms(offer_uri, property_iri, value, shapes) -> bool` (new, `ground.py`)

The §8 SHACL membrane, closed-world:
1. Read the property shape's `sh:datatype` (if any); **cast** `value` to it (`Literal(value,
   datatype=dt)`); a cast that yields an ill-typed literal (e.g. "high" as `xsd:decimal`) makes the
   value fail `sh:datatype`/range → correctly non-conformant.
2. Build a **focused** shapes graph: a fresh `sh:NodeShape` targeting `offer_uri` (via
   `sh:targetNode offer_uri`) carrying **only this field's `sh:property`** constraint (the CBD of the
   matched property-shape bnode). This is the crux — validating against the *full* `OrganOfferShape`
   would fail on OTHER required properties (`organ`/`aboGroup` `sh:minCount 1`) that the scratch offer
   does not have, wrongly quarantining a conformant value. We isolate the one field, mirroring
   `tiling.py`'s CBD-subset approach.
3. Build a scratch data graph: `(offer_uri, RDF.type, targetClass)` + `(offer_uri, property_iri,
   typed_value)`.
4. Run pySHACL (reuse `iladub.validate.validate`) with the scratch data graph against the focused
   shapes graph.
5. Return conformance.

### 3.4 Typed-literal emission (`_emit_grounded`)

Emit the grounded value with its declared `sh:datatype` (e.g. `xsd:decimal`), not a bare
`Literal(concept.value)` string — required for range/datatype constraints to bind and more faithful to
the source. Scheme/exact fields with no declared datatype keep the string literal.

### 3.5 Rationale transparency

In the value-constraint branch, `ground_concept` sets the rationale to record the verification mode
(which constraints conformed), carried into the `PromotionDecision` `dec:rationale`.

## 4. Data flow

```
ground_concept
  exact_field? → is_exact, field                              (unchanged)
  else → proposer.propose_grounding → field
  emit_candidate; field is None → "proposed"
  grounds_to = _grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri):
      scheme field          → scheme_member(...)               (UNCHANGED — tight oracle)
      non-scheme + exact     → property IRI                    (UNCHANGED)
      non-scheme, not exact  → value-shape has a constraint
                               AND _value_conforms(typed value) → property IRI
                               else                             → None (quarantine)
  grounds_to None → "proposed";  else → emit_grounded (typed literal) → "grounded"
```

## 5. Testing (offline; `FakeGroundingProposer`; run `./.venv/bin/python -m pytest`)

Extend `tests/test_grounding.py`:

1. **Positive — range-constrained field grounds (new capability):** EF shape `xsd:decimal [0,100]`;
   NEURAL proposal EF value `"55"` → `"grounded"`, `GroundedNode` bound to `tx:ejectionFraction`.
   **RED** on current code (retargets the shipped quarantine test, #4).
2. **Negative — out-of-range quarantines (the discriminating guard):** EF `"150"` → `"proposed"`, no
   `GroundedNode`. Proves SHACL *rejects*; the load-bearing not-confidence-as-validity guard.
3. **Negative — wrong datatype quarantines:** EF `"high"` (not a decimal) → `"proposed"`. Pins the
   cast-failure path.
4. **Preserved boundary — unconstrained field still quarantines:** retarget the shipped
   `test_neural_to_unconstrained_field_quarantined` to `tx:causeOfDeath` (free text, no value shape) →
   `"proposed"`. Keeps "nothing to verify → quarantine" explicit.
5. **Typed-literal emission:** the grounded EF value is `Literal("55", datatype=xsd:decimal)`, not a
   bare string.
6. **Regression — scheme/exact unchanged:** `organ` (exact+scheme) + `Blood type→aboGroup` still ground;
   `"55%"→aboGroup` still scheme-rejected; `_build_offer` end-to-end updated for EF now grounding.
7. **Rationale records the weaker mode:** the EF `PromotionDecision` `dec:rationale` contains the
   value-constraint verification note.

## 6. Anti-overfit

The oracle is pySHACL over the contract's declared constraints — **no tuned constant**; discrimination is
exactly what the contract declares. The load-bearing guards are the **rejection** tests (#2, #3): an
out-of-range or wrong-type value must NOT ground regardless of proposer confidence. Legality (SHACL
conformance) gates admission; confidence never does — the B1.3 invariant, here on the grounding membrane.

## 7. Scope boundary (YAGNI)

- Extends **only** the non-scheme/non-exact branch; scheme + exact + no-field-quarantine paths unchanged.
- Any declared value constraint counts (`sh:in`/`sh:pattern`/`sh:datatype`/range); soundness is the
  contract author's declared strength, recorded in the rationale.
- Cardinality-only / free-text fields still quarantine.
- Concept feed (follow-up **a**) stays out of scope — hand-fed `SurfaceConcept`s.
- One `sh:pattern` field is nice-to-have, not required (datatype+range demonstrates the mechanism);
  include only if it falls out cheaply.

## 8. Definition of done (the loop CLOSES)

- A NEURAL proposal to a value-constrained field grounds through the real `ground_concept` when it
  conforms (in-range EF `"55"` → grounded, typed) and quarantines when it does not (out-of-range `"150"`,
  wrong-type `"high"`, unconstrained `causeOfDeath` → proposed) — RED-checked non-vacuous (#1).
- The grounded value is emitted with its declared datatype; the `PromotionDecision` records the
  verification mode.
- Every shipped grounding behaviour stays green (scheme/exact/invariant regression), full
  `tests/test_grounding.py` passes.
- Residue (unconstrained, non-conformant, out-of-range) quarantined as `CandidateConcept` propositions,
  never dropped, never faked.

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
