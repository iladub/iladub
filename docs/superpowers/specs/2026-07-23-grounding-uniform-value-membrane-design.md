# Grounding — uniform value membrane + sh:in/sh:pattern coverage

**Date:** 2026-07-23
**Status:** Design — approved for spec (brainstorm 2026-07-23).
**Slice:** Tighten the grounding oracle: (1) apply the contract's value-constraint membrane on the
**exact-match path** too, not just the propose path (close a soundness asymmetry surfaced by probe);
(2) demonstrate + test-cover the **tight** value oracles `sh:in` (enum) and `sh:pattern`, which the
shipped machinery already supports. Continuation of the value-constraint disposal
(`2026-07-22-grounding-value-constraint-disposal-design.md`).

**Gate context (CLAUDE.md §8):** no new decision kind — the oracle stays **SHACL-membrane dispose**
(closed-world) over the contract's declared constraints; no tuned constant. This slice makes the
membrane **uniform** (legality gates admission regardless of how the field was identified) and proves
the tight oracles already covered by design.

---

## 1. The decisions (two, one sentence each)

1. **Uniform value membrane:** for a non-scheme field that declares a value constraint, `_grounds_to`
   grounds **iff the value conforms** (`_value_conforms`) — whether the field was identified by exact
   label match or by a model proposal; an unconstrained field still grounds on exact match
   (field-identity) and quarantines on a bare proposal (no oracle).
2. **Tight-oracle coverage:** `sh:in` and `sh:pattern` — already enforced by the shipped
   `_value_conforms` (pySHACL) and already in `_VALUE_CONSTRAINTS` — are demonstrated and test-covered
   grounding-on-match/member and quarantining-on-miss through the real `ground_concept`.

## 2. Why (findings from probe, 2026-07-23)

- **The tight oracles already work.** A `sh:pattern "^(A|B|AB|O)$"` field grounds "O"/"AB" and rejects
  "Z"/"55%"; a `sh:in (Heart Liver Lung)` field grounds "Heart" and rejects "Kidney" — verified through
  both `_value_conforms` and the full `ground_concept`. No production-code extension is needed for
  coverage; the gap is demonstration + tests (the "worked example + negative test" discipline).
- **The exact path skips the membrane (the real fix).** Shipped `_grounds_to` returns the property IRI
  for an exact-matched non-scheme field **without** validating the value:
  ```python
  if is_exact: return URIRef(field.fills_property)   # ← no value check
  ```
  So an exact-matched `ejectionFraction`="999" grounds despite the `[0,100]` range, and an exact-matched
  enum field grounds a non-member. The value membrane applied only on the propose path — an asymmetry.
  Low-impact for the raw-doc pipeline (table headers rarely exact-match property local-names → they go
  via propose → constraints apply), but a genuine soundness inconsistency. Making the membrane uniform
  was probe-verified **non-breaking**: all 30 grounding/feed tests stay green.

## 3. The membrane change (`src/iladub/ground.py`, `_grounds_to`)

```python
def _grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class):
    """... Scheme-bound: SKOS membership. Non-scheme with a value constraint: the value must CONFORM
    (the SHACL membrane), regardless of exact-match vs proposal — legality gates admission uniformly.
    Non-scheme WITHOUT a value constraint: an exact label match grounds (field-identity is the oracle);
    a bare proposal has no oracle -> quarantine."""
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

Behavior delta: an exact-matched value-constrained field now quarantines a non-conforming value
(previously grounded it). Scheme, propose-with-constraint, and unconstrained paths are unchanged.

## 4. No shared-shape changes (the Task-4 lesson — load-bearing)

The transplant `examples/transplant/offer-shapes.ttl` is the **shared M4 conformance shape**; tightening
it broke 4 M4 tests last slice. This slice therefore **touches no shared shape**:

- The **asymmetry RED-check** reuses the *existing* EF `sh:datatype xsd:decimal ; [0,100]` constraint
  (already on offer-shapes, M4-safe: M4's EF="60" conforms): exact-EF "60" → grounds; exact-EF "999" →
  now quarantines.
- The **sh:in / sh:pattern coverage** uses **test-local shapes** (a pattern field + an enum field built
  in the test, targeting a synthetic offer node). The oracle is contract-agnostic — a real contract
  author declares `sh:in`/`sh:pattern` the same way; the test proves the machinery, not a particular
  contract.

## 5. Testing (offline; `./.venv/bin/python -m pytest`)

Extend `tests/test_grounding_value_constraints.py`:

1. **Uniform membrane — exact path now enforces the constraint (RED-checked):** with a proposer that is
   never consulted (exact match), an exact-matched `ejectionFraction`="60" grounds; "999" → `"proposed"`,
   no `GroundedNode`. **RED-check:** against the shipped `_grounds_to`, "999" grounds — this test fails
   pre-change and passes post-change (proves the fix is load-bearing).
2. **sh:pattern grounds on match / quarantines on non-match:** a test-local shape with
   `sh:pattern "^[0-9]+(kg|cm)$"` on a field; via the propose path, value "78kg" → `"grounded"` (bound to
   the property), "big" → `"proposed"`, no `GroundedNode`.
3. **sh:in grounds on member / quarantines on non-member:** a test-local shape with
   `sh:in ("positive" "negative")`; value "negative" → `"grounded"`, "unknown" → `"proposed"`.
4. **Scheme + unconstrained paths unchanged (regression):** the shipped scheme grounding, the
   `causeOfDeath` unconstrained-quarantine boundary, and the exact-organ scheme path still behave as
   before (covered by the existing suite staying green).

Full `tests/` suite stays green — the change is confined to `ground.py`'s non-scheme branch; M4 and the
concept feed are untouched (probe-verified: 30 grounding/feed tests green under the change).

## 6. Anti-overfit

The membrane is pySHACL over the contract's declared constraints — **no tuned constant**. The
load-bearing guards are the **rejection** tests: non-matching pattern (#2), non-member enum (#3), and the
out-of-range exact-EF (#1). Legality (SHACL conformance) gates admission; confidence never does. The
uniform membrane removes the one path where the value was previously trusted without verification.

## 7. Scope boundary (YAGNI)

- Only `_grounds_to`'s non-scheme branch changes; scheme and unconstrained paths unchanged.
- sh:in/sh:pattern coverage via test-local shapes; **no changes to any shared shape file** (M4-safe).
- **Deferred (documented edge):** an enum (`sh:in`) of *non-string typed* literals (e.g. `sh:in (1 2 3)`
  as integers) needs the input value cast to the literal datatype before the membership check; the
  natural case (string-label enums, like scheme prefLabels) works. Out of scope — no synthetic fixture.
- No concept-feed E2E extension (a later slice could add an enum/pattern column to the offer table).

## 8. Definition of done

- The value membrane is uniform: an exact-matched value-constrained field grounds a conforming value and
  quarantines a non-conforming one (RED-checked non-vacuous); scheme/unconstrained/propose paths
  unchanged.
- `sh:in` and `sh:pattern` are demonstrated grounding-on-match/member and quarantining-on-miss through
  the real `ground_concept`, with rejection tests as the load-bearing guards.
- No shared shape file changed; full suite green.
- Residue (non-conforming / unconstrained cells) quarantined as propositions, never dropped (§7).

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
