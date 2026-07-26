# `f:modify` Write-Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce iladub's promotion invariant at the Fluree WRITE/commit gate — a grounded node without an accountable promotion is REJECTED at commit (reuse the full iladub SHACL membrane), and only the promotion's `dec:decidedBy` agent may write it (a static `f:modify` policy).

**Architecture:** A focused new module `src/iladub/etkl/writegate.py`: the STRUCTURAL gate reuses `vocab/shapes/iladub-shapes.ttl` wholesale (`gate_admits` = `validate` against it); the AUTHORIZATION axis is a static Fluree `f:modify` `AccessPolicy` template (`?$identity` must be the promotion's `dec:decidedBy`) certified structurally by `certify_modify_authorization`. No new vocab, no CONSTRUCT.

**Tech Stack:** Python 3.12, rdflib (incl. built-in JSON-LD parser), pySHACL (via `iladub.validate`), pytest. Fluree JSON-LD (`f:` = `https://ns.flur.ee/db#`).

## Global Constraints

- **Neurosymbolic gate (hard):** the commit gate is **CONSTRAINT → SHACL** (the closed-world membrane, reused at the data commit). `writegate.py` is **PROCEDURAL** glue (graph parse, `validate` delegation, substring presence check) — no domain decision, no tuned constant, no CONSTRUCT. No Python decides "may this write happen" — the SHACL membrane and the `f:modify` policy do.
- **Reuse, don't re-author:** the promotion invariant is `vocab/shapes/iladub-shapes.ttl` (`iladub:GroundedNodeShape` = `wasPromotedBy minCount 1` + `groundsTo` + `status asserted`; `PromotionDecisionShape` = `reviews` + `dec:decidedBy`; `NoLeakShape`; `CandidateConceptShape`). Do NOT duplicate any shape.
- **No new vocab, no CONSTRUCT.** Reuse `iladub:wasPromotedBy`, `dec:decidedBy`, `iladub:GroundedNode`.
- **Source ownership:** `f:` (Fluree's, `https://ns.flur.ee/db#`) appears ONLY in `src/iladub/fluree/f-modify-policy-template.jsonld` (a compile target — the `src/iladub/fluree/__init__.py` already exists from PR #65), OUTSIDE the `vocab/`/`examples/`/`tests/*.ttl` trees the source-ownership CI scans. No HGA term as a subject; `hfed:` unused.
- **Commands:** run tests with `. .venv/bin/activate && python3 -m pytest ...` (binary is `python3`).
- **Branch:** work continues on `iladub-fmodify-write-gate`.

**Key existing signatures (do not change):**
- `iladub.validate.validate(data: Graph, shapes: Graph, knowledge: Graph) -> ValidationResult(conforms: bool, report_text: str, report_graph: Graph)`.
- rdflib parses JSON-LD via `Graph().parse(path, format="json-ld")`; supports triple-pattern containment `(s, p, o) in graph` (any term may be a wildcard when using `.triples`, but here all terms are concrete).
- Namespaces: `ILADUB = https://w3id.org/iladub#`, `DEC = https://w3id.org/iladub/dec#`, `F = https://ns.flur.ee/db#`, `gist: = https://w3id.org/semanticarts/ns/ontology/gist/`.
- Status individuals: `iladub:proposed`, `iladub:asserted`. Classes: `iladub:Suggester`, `iladub:SourceRegion`.

---

### Task 1: The structural commit gate — `writegate.py` `commit_gate_shapes` + `gate_admits`

**Files:**
- Create: `src/iladub/etkl/writegate.py`
- Create: `tests/writegate-promoted.ttl` (admit fixture — fully membrane-conformant)
- Create: `tests/writegate-unpromoted.ttl` (reject fixture — bare grounded node)
- Test: `tests/test_writegate.py` (new)

**Interfaces:**
- Produces: `writegate.commit_gate_shapes() -> Graph`; `writegate.gate_admits(transaction: Graph, knowledge: Graph) -> ValidationResult`.

- [ ] **Step 1: Write the admit fixture `tests/writegate-promoted.ttl`**

```turtle
@prefix iladub: <https://w3id.org/iladub#> .
@prefix dec:    <https://w3id.org/iladub/dec#> .
@prefix gist:   <https://w3id.org/semanticarts/ns/ontology/gist/> .
@prefix prov:   <http://www.w3.org/ns/prov#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:     <https://example.org/demo#> .

#  A FULLY membrane-conformant commit: a complete proposition, promoted by an
#  accountable decision, producing a grounded node. gate_admits MUST admit this.
ex:cand a iladub:CandidateConcept ;
    iladub:surfaceText "Wirkstoffspiegel"@de ;
    iladub:suggestedAnchor gist:Magnitude ;
    iladub:suggestedBy ex:extractor-v0 ;
    iladub:confidence 0.62 ;
    iladub:fromRegion ex:region-p2 ;
    iladub:status iladub:proposed .

ex:extractor-v0 a iladub:Suggester ; rdfs:label "iladub extractor v0"@en .
ex:region-p2 a iladub:SourceRegion ; rdfs:label "page 2"@en .

ex:promo a iladub:PromotionDecision ;
    iladub:reviews ex:cand ;
    dec:decidedBy ex:curator-aliki .
ex:curator-aliki a prov:Agent ; rdfs:label "Dr. A. Curator"@en .

ex:gn a iladub:GroundedNode ;
    iladub:wasPromotedBy ex:promo ;
    iladub:groundsTo ex:DrugConcentration ;
    iladub:status iladub:asserted .
```

- [ ] **Step 2: Write the reject fixture `tests/writegate-unpromoted.ttl`**

```turtle
@prefix iladub: <https://w3id.org/iladub#> .
@prefix ex:     <https://example.org/demo#> .

#  AN UNACCOUNTABLE WRITE: a grounded node asserted with NO promotion decision.
#  gate_admits MUST reject this (iladub:GroundedNodeShape wasPromotedBy minCount 1).
ex:gn a iladub:GroundedNode ;
    iladub:groundsTo ex:DrugConcentration ;
    iladub:status iladub:asserted .
```

- [ ] **Step 3: Write the failing tests `tests/test_writegate.py`**

```python
"""The Fluree WRITE/commit gate: iladub's promotion invariant enforced at commit
(a grounded node without an accountable promotion is REJECTED), plus a static f:modify
policy authorizing writes only to the promotion's dec:decidedBy agent.
See docs/superpowers/specs/2026-07-25-fmodify-write-gate-design.md."""
import os
from rdflib import Graph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
TST = os.path.join(ROOT, "tests")


def _knowledge():
    g = Graph()
    for f in ("iladub.ttl", "dec.ttl"):
        g.parse(os.path.join(ONT, f), format="turtle")
    return g


def test_gate_admits_a_properly_promoted_write():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "writegate-promoted.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert result.conforms, result.report_text


def test_gate_rejects_a_grounded_node_without_promotion():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "writegate-unpromoted.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert not result.conforms
    assert "promotion" in result.report_text.lower()


def test_gate_rejects_a_leaked_candidate():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "leak-attempt.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert not result.conforms
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_writegate.py -q`
Expected: FAIL (`ModuleNotFoundError: No module named 'iladub.etkl.writegate'`).

- [ ] **Step 5: Create `src/iladub/etkl/writegate.py` (the structural gate)**

```python
"""writegate — enforce iladub's promotion invariant at the Fluree WRITE/commit gate.

STRUCTURAL: the commit gate reuses the full iladub epistemic membrane (iladub-shapes.ttl) —
a grounded node without an accountable promotion is REJECTED at commit. AUTHORIZATION (below):
a static f:modify AccessPolicy authorizes the write only to the promotion's dec:decidedBy agent.
This module is PROCEDURAL glue (graph parse, validate delegation, substring presence check) —
no domain decision, no tuned constant, no CONSTRUCT. f: is Fluree's vocabulary, consumed only
via the src/iladub/fluree/ template.
See docs/superpowers/specs/2026-07-25-fmodify-write-gate-design.md.
"""
from __future__ import annotations

import os

from rdflib import Graph

from ..validate import validate, ValidationResult

_SHAPES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "shapes", "iladub-shapes.ttl")


def commit_gate_shapes() -> Graph:
    """The commit-gate shape-set: the full iladub epistemic membrane (reused, not re-authored)."""
    return Graph().parse(_SHAPES, format="turtle")


def gate_admits(transaction: Graph, knowledge: Graph) -> ValidationResult:
    """Would this transaction be admitted at the commit? Validate it against the iladub
    membrane; .conforms False => REJECTED (e.g. a grounded node with no accountable promotion)."""
    return validate(transaction, commit_gate_shapes(), knowledge)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_writegate.py -q`
Expected: PASS (admit conforms; unpromoted rejected with "promotion" in the report; leaked candidate rejected). If the admit fixture unexpectedly fails, read `result.report_text` — every `CandidateConcept` property (surfaceText/suggestedAnchor/suggestedBy/confidence/fromRegion/status proposed), the promotion's `reviews`+`dec:decidedBy`, and the grounded node's `wasPromotedBy`+`groundsTo`+`status asserted` must be present.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/writegate.py tests/writegate-promoted.ttl tests/writegate-unpromoted.ttl tests/test_writegate.py
git commit -m "feat(etkl): writegate.gate_admits — promotion invariant as the commit gate (reuse the iladub membrane)"
```

---

### Task 2: The `f:modify` authorization policy + `certify_modify_authorization`

**Files:**
- Create: `src/iladub/fluree/f-modify-policy-template.jsonld`
- Modify: `src/iladub/etkl/writegate.py`
- Test: `tests/test_writegate.py` (append)

**Interfaces:**
- Consumes: `writegate` module from Task 1.
- Produces: `writegate.ModifyVerdict(ok, is_modify, wires_accountable)` (frozen); `writegate.certify_modify_authorization(f_modify_policy: Graph) -> ModifyVerdict`; the static template.

- [ ] **Step 1: Create `src/iladub/fluree/f-modify-policy-template.jsonld`**

A static, data-driven `f:modify` `AccessPolicy` — accountability travels in `wasPromotedBy`/`decidedBy`, so the policy is identical for any data. The `f:query` is Fluree's escaped-JSON `where` using full IRIs.

```json
{
  "@context": {
    "f": "https://ns.flur.ee/db#",
    "iladub": "https://w3id.org/iladub#"
  },
  "@graph": [
    {
      "@id": "iladub:accountableWritePolicy",
      "@type": ["f:AccessPolicy"],
      "f:required": true,
      "f:action": [{ "@id": "f:modify" }],
      "f:onClass": [{ "@id": "https://w3id.org/iladub#GroundedNode" }],
      "f:query": "{\"where\":[{\"@id\":\"?$this\",\"https://w3id.org/iladub#wasPromotedBy\":{\"@id\":\"?pd\"}},{\"@id\":\"?pd\",\"https://w3id.org/iladub/dec#decidedBy\":{\"@id\":\"?$identity\"}}]}"
    }
  ]
}
```

- [ ] **Step 2: Write the failing tests (append to `tests/test_writegate.py`)**

```python
from rdflib import Namespace, RDF, Literal, URIRef

F = Namespace("https://ns.flur.ee/db#")
FLUREE_DIR = os.path.join(ROOT, "src", "iladub", "fluree")


def _modify_template():
    return Graph().parse(os.path.join(FLUREE_DIR, "f-modify-policy-template.jsonld"), format="json-ld")


def test_modify_template_is_f_modify_and_binds_accountable():
    g = _modify_template()
    pol = next(g.subjects(RDF.type, F.AccessPolicy))
    assert (pol, F.action, F.modify) in g
    q = " ".join(str(o) for o in g.objects(None, F.query))
    for ref in ("?$identity",
                "https://w3id.org/iladub#wasPromotedBy",
                "https://w3id.org/iladub/dec#decidedBy"):
        assert ref in q, ref


def test_certify_modify_authorization_ok():
    from iladub.etkl import writegate
    v = writegate.certify_modify_authorization(_modify_template())
    assert v.ok and v.is_modify and v.wires_accountable, v


def test_certify_rejects_non_modify_policy():
    from iladub.etkl import writegate
    g = Graph()
    pol = URIRef("urn:bad:viewpol")
    g.add((pol, RDF.type, F.AccessPolicy))
    g.add((pol, F.action, F.view))   # f:view, not f:modify
    g.add((pol, F.query, Literal(
        '{"where":[{"@id":"?$this","https://w3id.org/iladub#wasPromotedBy":{"@id":"?pd"}},'
        '{"@id":"?pd","https://w3id.org/iladub/dec#decidedBy":{"@id":"?$identity"}}]}')))
    v = writegate.certify_modify_authorization(g)
    assert not v.is_modify and not v.ok


def test_certify_rejects_unaccountable_query():
    from iladub.etkl import writegate
    g = Graph()
    pol = URIRef("urn:bad:modpol")
    g.add((pol, RDF.type, F.AccessPolicy))
    g.add((pol, F.action, F.modify))
    # f:query omits decidedBy — anyone could write, not just the accountable decider
    g.add((pol, F.query, Literal(
        '{"where":[{"@id":"?$this","https://w3id.org/iladub#wasPromotedBy":{"@id":"?pd"}}]}')))
    v = writegate.certify_modify_authorization(g)
    assert not v.wires_accountable and not v.ok
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_writegate.py -k "modify or certify" -q`
Expected: FAIL (`AttributeError: module ... has no attribute 'certify_modify_authorization'`; the template test may fail on missing file until Step 1 exists — if Step 1 done, it passes independently).

- [ ] **Step 4: Add the authorization oracle to `src/iladub/etkl/writegate.py`**

Add the imports and code (append; the module already imports `os`, `Graph`):

```python
from dataclasses import dataclass

from rdflib import Namespace, RDF

F = Namespace("https://ns.flur.ee/db#")

# The full IRIs the f:modify f:query must reference to authorize a write ONLY to the
# promotion's accountable decider.
_MODIFY_REFS = (
    "?$identity",
    "https://w3id.org/iladub#wasPromotedBy",
    "https://w3id.org/iladub/dec#decidedBy",
)


@dataclass(frozen=True)
class ModifyVerdict:
    ok: bool
    is_modify: bool          # the policy is an f:AccessPolicy with f:action f:modify
    wires_accountable: bool  # its f:query resolves ?$identity through wasPromotedBy -> decidedBy


def certify_modify_authorization(f_modify_policy: Graph) -> ModifyVerdict:
    """Certify the f:modify policy authorizes a grounded-node write ONLY to the promotion's
    accountable dec:decidedBy agent: an f:AccessPolicy with f:action f:modify whose f:query
    wires ?$identity through wasPromotedBy -> decidedBy."""
    is_modify = any(
        (pol, F.action, F.modify) in f_modify_policy
        for pol in f_modify_policy.subjects(RDF.type, F.AccessPolicy)
    )
    query_texts = [str(q) for q in f_modify_policy.objects(None, F.query)]
    wires_accountable = any(all(ref in q for ref in _MODIFY_REFS) for q in query_texts)
    return ModifyVerdict(ok=is_modify and wires_accountable,
                         is_modify=is_modify, wires_accountable=wires_accountable)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_writegate.py -q`
Expected: PASS (all Task 1 + Task 2 tests: template is f:modify + binds accountable; certify ok; f:view → not is_modify; no-decidedBy → not wires_accountable).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/fluree/f-modify-policy-template.jsonld src/iladub/etkl/writegate.py tests/test_writegate.py
git commit -m "feat(etkl): f:modify policy + certify_modify_authorization — only the accountable decider may write"
```

---

### Task 3: Full-suite regression

**Files:**
- None (verification only).

- [ ] **Step 1: Run the full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass (prior 531 + the new write-gate tests), 5 skipped. The suite takes ~3 min; run it in the foreground and wait. If the runner times out, run `tests/test_writegate.py tests/test_source_ownership.py tests/test_grounding.py` explicitly and report that the full run should be verified separately.

- [ ] **Step 2: Commit (only if a fix was needed; otherwise skip)**

```bash
git add -A && git commit -m "fix(etkl): <describe regression fix>"
```

---

## Self-Review

**Spec coverage:**
- §3.1 static `f:modify` template → Task 2.
- §3.2 structural commit gate (reuse the full membrane) → Task 1 (`commit_gate_shapes`, `gate_admits`).
- §3.3 `gate_admits` + `ModifyVerdict` + `certify_modify_authorization` → Tasks 1 (gate) + 2 (certify).
- §4 no new vocab/CONSTRUCT; `f:` only in the `src/iladub/fluree/` template → Tasks 1/2; source-ownership unaffected (verified by the existing `test_source_ownership` in the full-suite run, Task 3).
- §5 demonstrator + negatives (unpromoted → rejected; leaked candidate → rejected; f:view → not is_modify; no-decidedBy → not wires_accountable; structural template test) → Tasks 1/2.
- §5 gate: SHACL CONSTRAINT reused (Task 1); `writegate.py` PROCEDURAL, no tuned constant, no CONSTRUCT → covered.

**Placeholder scan:** none — every step has full TTL/JSON-LD/Python/command content.

**Type consistency:** `commit_gate_shapes() -> Graph`, `gate_admits(transaction, knowledge) -> ValidationResult`, `ModifyVerdict(ok, is_modify, wires_accountable)`, `certify_modify_authorization(f_modify_policy) -> ModifyVerdict`, `F = https://ns.flur.ee/db#`, `_MODIFY_REFS` — consistent across Tasks 1–2. Fixtures `tests/writegate-promoted.ttl` / `tests/writegate-unpromoted.ttl` and the reused `tests/leak-attempt.ttl` referenced consistently.

**Note on `import` placement:** Task 2 Step 4 adds a second import block (`dataclass`, `Namespace`, `RDF`) below Task 1's imports. An implementer applying both tasks should consolidate imports at the top of `writegate.py` — functionally identical either way; not a defect, just tidier. (Flagged so a reviewer doesn't treat the split-import as an error.)

**Admit-fixture conformance:** `tests/writegate-promoted.ttl` is built to satisfy every shape in `iladub-shapes.ttl` — complete `CandidateConcept` (6 properties incl. `status proposed`, `confidence 0.62` as `xsd:decimal`), accountable `PromotionDecision` (`reviews` + `dec:decidedBy`), `GroundedNode` (`wasPromotedBy` + `groundsTo` + `status asserted`). `dec-shapes.ttl` decision-mechanics (optionSpace/chosen) are NOT part of the commit gate (spec scopes it to `iladub-shapes.ttl`), so the promotion needs only `reviews` + `decidedBy`.
