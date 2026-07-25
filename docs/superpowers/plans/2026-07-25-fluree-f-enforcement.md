# Fluree `f:` Enforcement Compile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile the governed ODRL sensitivity-tag policy into a data-driven Fluree `f:AccessPolicy` and certify the `f:` grants equal the ODRL grants — closing *governed-projection-permitted == odrl-grants == f:-permitted* from one policy, entirely in CI, no Fluree server.

**Architecture:** A static Fluree-native `f:AccessPolicy` template (its `f:query` joins `?$identity → role → granted tag → resource tag`) + an AXIOM CONSTRUCT that reshapes ODRL read-permissions into flat `etkl:grantsTag` triples the policy's query reads + a faithfulness oracle (`certify_f_faithful`) that checks grant-set equivalence and that the template preserves AI-inherits-user. `f:` is consumed as a compile *target* (Fluree's JSON-LD), never authored as iladub ontology.

**Tech Stack:** Python 3.12, rdflib (incl. its built-in JSON-LD parser), pytest. SPARQL CONSTRUCT, RDF Turtle vocab, Fluree JSON-LD.

## Global Constraints

- **Neurosymbolic gate (hard):** grant derivation is **AXIOM** — a fixed SPARQL CONSTRUCT, open-world, evidence-positive (emit a grant only where a read-permission is present). `compile_f_policy` + `certify_f_faithful` are **PROCEDURAL** glue (graph union, set comparison, substring presence check) — no domain decision, no tuned constant. No Python decides who-may-read-what.
- **Source ownership:** `etkl:grantsTag` authored only in `etkl:`; `etkl.ttl` stays standalone. **`f:` is Fluree's vocabulary** (`https://ns.flur.ee/db#`) — it appears ONLY in the generated interchange artifact `src/iladub/fluree/f-policy-template.jsonld` (a compile target), which lives OUTSIDE the `vocab/`/`examples/`/`tests/*.ttl` trees the source-ownership CI scans. No HGA term as a subject anywhere; `hfed:` unused.
- **TDD / repo convention:** a worked case that certifies faithful + negatives that must fail.
- **Commands:** run tests with `. .venv/bin/activate && python3 -m pytest ...` (binary is `python3`).
- **Branch:** work continues on `iladub-fluree-f-enforcement`.

**Verified facts (do not re-derive):**
- Fluree `f:` namespace IRI = `https://ns.flur.ee/db#` (confirmed against the local ReBAC benchmark `internal/benchmarks/fluree-rebac/policy.jsonld`).
- Real Fluree `f:AccessPolicy` shape: `@type [f:AccessPolicy]`, `f:required true`, `f:action [{@id f:view}]`, and `f:query` is an **escaped-JSON string** whose `where` is a list of `{@id, <fullIRI>: {@id ...}}` patterns using **full IRIs** and `?$identity`/`?$this` variables.

**Key existing signatures (do not change):**
- `iladub.etkl.interpret.run(query_path, *graphs) -> rdflib.Graph` (unions its graphs).
- `src/iladub/etkl/federate.py` already imports `os`, `dataclass`, and from rdflib `Graph, Namespace, RDF, URIRef`; defines module constants `ETKL = Namespace("https://w3id.org/iladub/etkl#")`, `ODRL = Namespace("http://www.w3.org/ns/odrl/2/")`, `_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")`. Its grant helper `_permitted_for_role` iterates `policy.subjects(ODRL.action, ODRL.read)` → assignees ∩ roles → targets (mirror this).
- The transplant demo policy `examples/transplant/transplant-governance.ttl` grants (post PR #64): `role-opo {clinical, phi}`, `role-donor-region {clinical, phi}`, `role-recipient-ctr {clinical}`, `role-board {clinical, phi}`; tags `tx:clinical`, `tx:phi`.

---

### Task 1: `etkl:grantsTag` vocabulary

**Files:**
- Modify: `vocab/ontology/etkl.ttl`
- Test: `tests/test_fluree_policy.py` (new)

**Interfaces:**
- Produces: `etkl:grantsTag` (`owl:ObjectProperty`).

- [ ] **Step 1: Write the failing test**

Create `tests/test_fluree_policy.py`:

```python
"""Fluree f: enforcement compile: the governed ODRL tag-policy compiled to a data-driven
Fluree f:AccessPolicy, and certified faithful (f: grants == ODRL grants), no server.
See docs/superpowers/specs/2026-07-25-fluree-f-enforcement-design.md."""
import os
from rdflib import Graph, Namespace, RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")


def test_grantstag_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.grantsTag, RDF.type, OWL.ObjectProperty) in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py -q`
Expected: FAIL (triple not present).

- [ ] **Step 3: Add the property to `vocab/ontology/etkl.ttl`**

Add near the governance properties added in the prior increment (standalone — no `f:`/`holon:`):

```turtle
etkl:grantsTag a owl:ObjectProperty ;
    rdfs:label "grants tag"@en ;
    rdfs:comment "The sensitivity tag a role is granted read access on — the flat grant relation compiled from the ODRL tag-policy, read by a Fluree f:AccessPolicy's f:query to enforce the same governance at the data layer."@en .
```

- [ ] **Step 4: Run tests + source-ownership guard**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py tests/test_source_ownership.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/etkl.ttl tests/test_fluree_policy.py
git commit -m "feat(etkl): etkl:grantsTag — the flat role→tag grant relation for f: enforcement"
```

---

### Task 2: `compile-f-grants.rq` — reshape ODRL grants (AXIOM)

**Files:**
- Create: `vocab/queries/compile-f-grants.rq`
- Create: `tests/fluree-odrl-policy.ttl` (a minimal ODRL tag-policy fixture)
- Test: `tests/test_fluree_policy.py` (append)

**Interfaces:**
- Produces: a query consumed by `interpret.run(query_path, odrl_policy)` that emits `?role etkl:grantsTag ?tag` for every `odrl:permission[odrl:action odrl:read; odrl:assignee ?role; odrl:target ?tag]`.

- [ ] **Step 1: Write the fixture `tests/fluree-odrl-policy.ttl`**

```turtle
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .
@prefix tx:   <https://example.org/transplant#> .

#  A minimal ODRL tag-policy: OPO reads both tags, recipient reads clinical only.
tx:policy a odrl:Policy ;
    odrl:permission
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:clinical ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:phi ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-recipient-ctr ; odrl:target tx:clinical ] .
```

- [ ] **Step 2: Write the failing test (append)**

```python
from iladub.etkl import interpret

TX = Namespace("https://example.org/transplant#")
QUERIES = os.path.join(ROOT, "vocab", "queries")
ODRL_FIXTURE = os.path.join(ROOT, "tests", "fluree-odrl-policy.ttl")


def test_compile_f_grants_reshapes_odrl():
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    grants = interpret.run(os.path.join(QUERIES, "compile-f-grants.rq"), policy)
    pairs = {(str(r), str(t)) for r, t in grants.subject_objects(ETKL.grantsTag)}
    assert pairs == {
        (str(TX["role-opo"]), str(TX.clinical)),
        (str(TX["role-opo"]), str(TX.phi)),
        (str(TX["role-recipient-ctr"]), str(TX.clinical)),
    }
```

- [ ] **Step 3: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py::test_compile_f_grants_reshapes_odrl -q`
Expected: FAIL ("No such file" — the `.rq` is missing).

- [ ] **Step 4: Create `vocab/queries/compile-f-grants.rq`**

```sparql
PREFIX etkl: <https://w3id.org/iladub/etkl#>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>

#  AXIOM (open-world, evidence-positive): flatten each ODRL read-grant into the role→tag
#  relation a Fluree f:query reads. Mirrors federate-projection-governed.rq's grant pattern
#  exactly (odrl:action odrl:read ; odrl:assignee ?role ; odrl:target ?tag), so the f: policy
#  gates on the SAME grants the governed projection does.
CONSTRUCT {
  ?role etkl:grantsTag ?tag .
}
WHERE {
  ?perm odrl:action odrl:read ;
        odrl:assignee ?role ;
        odrl:target ?tag .
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py::test_compile_f_grants_reshapes_odrl -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/compile-f-grants.rq tests/fluree-odrl-policy.ttl tests/test_fluree_policy.py
git commit -m "feat(etkl): compile-f-grants.rq — reshape ODRL read-grants to etkl:grantsTag (AXIOM)"
```

---

### Task 3: The static Fluree `f:AccessPolicy` template

**Files:**
- Create: `src/iladub/fluree/__init__.py`
- Create: `src/iladub/fluree/f-policy-template.jsonld`
- Test: `tests/test_fluree_policy.py` (append)

**Interfaces:**
- Produces: a Fluree-native `f:AccessPolicy` (JSON-LD) whose `f:query` `where` binds `?$identity`, resolves the role via `prov:actedOnBehalfOf` then `etkl:hasRole`, and joins `etkl:grantsTag` + `etkl:sensitivity`. Loadable by rdflib (`format="json-ld"`).

- [ ] **Step 1: Create the package marker `src/iladub/fluree/__init__.py`**

```python
"""Fluree interchange artifacts (compile targets). f: is Fluree's vocabulary
(https://ns.flur.ee/db#), consumed here as an enforcement-policy target — never
authored as iladub ontology."""
```

- [ ] **Step 2: Create `src/iladub/fluree/f-policy-template.jsonld`**

A data-driven `f:AccessPolicy`: the grants travel as `etkl:grantsTag` data (compiled from the ODRL policy); this policy is identical for any tag-policy. The `f:query` is Fluree's escaped-JSON `where` using full IRIs.

```json
{
  "@context": {
    "f": "https://ns.flur.ee/db#",
    "etkl": "https://w3id.org/iladub/etkl#"
  },
  "@graph": [
    {
      "@id": "etkl:sensitivityViewPolicy",
      "@type": ["f:AccessPolicy"],
      "f:required": true,
      "f:action": [{ "@id": "f:view" }],
      "f:query": "{\"where\":[{\"@id\":\"?$identity\",\"http://www.w3.org/ns/prov#actedOnBehalfOf\":{\"@id\":\"?principal\"}},{\"@id\":\"?principal\",\"https://w3id.org/iladub/etkl#hasRole\":{\"@id\":\"?role\"}},{\"@id\":\"?role\",\"https://w3id.org/iladub/etkl#grantsTag\":{\"@id\":\"?tag\"}},{\"@id\":\"?$this\",\"https://w3id.org/iladub/etkl#sensitivity\":{\"@id\":\"?tag\"}}]}"
    }
  ]
}
```

Note: an AI agent authenticates carrying/ delegated-from the user's identity; the `?$identity → prov:actedOnBehalfOf → principal → etkl:hasRole → role` chain is what makes the agent inherit exactly the user's grants at the data layer. Exact Fluree `where` execution semantics (e.g. optional-path handling for a direct-role human) are validated by the deferred live-Fluree harness (spec §8); this increment certifies the compile, not Fluree's execution.

- [ ] **Step 3: Write the failing structural test (append)**

```python
FLUREE_DIR = os.path.join(ROOT, "src", "iladub", "fluree")
F = Namespace("https://ns.flur.ee/db#")


def _template_graph():
    return Graph().parse(os.path.join(FLUREE_DIR, "f-policy-template.jsonld"), format="json-ld")


def test_template_is_a_view_access_policy():
    g = _template_graph()
    pol = next(g.subjects(RDF.type, F.AccessPolicy))
    assert (pol, F.action, F.view) in g
    assert (pol, F.required, None) in g


def test_template_query_binds_identity_and_joins():
    g = _template_graph()
    q = " ".join(str(o) for o in g.objects(None, F.query))
    for ref in ("?$identity",
                "http://www.w3.org/ns/prov#actedOnBehalfOf",
                "https://w3id.org/iladub/etkl#hasRole",
                "https://w3id.org/iladub/etkl#grantsTag",
                "https://w3id.org/iladub/etkl#sensitivity"):
        assert ref in q, ref
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py -k template -q`
Expected: PASS (both structural tests). If rdflib cannot parse JSON-LD, ensure rdflib ≥ 6 is installed (its JSON-LD parser is built in); do not add a new dependency.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/fluree/__init__.py src/iladub/fluree/f-policy-template.jsonld tests/test_fluree_policy.py
git commit -m "feat(fluree): static data-driven f:AccessPolicy template (compile target)"
```

---

### Task 4: `compile_f_policy` + `certify_f_faithful`

**Files:**
- Modify: `src/iladub/etkl/federate.py`
- Test: `tests/test_fluree_policy.py` (append)

**Interfaces:**
- Consumes: `interpret.run`, `compile-f-grants.rq`, the template.
- Produces:
  - `federate.compile_f_policy(odrl_policy: Graph) -> Graph`
  - `federate.FlureeVerdict(ok, missing, extra, identity_ok)` (frozen)
  - `federate.certify_f_faithful(odrl_policy, f_policy, roles=None) -> FlureeVerdict`

- [ ] **Step 1: Write the failing tests (append)**

```python
from iladub.etkl import federate
from rdflib import URIRef, Literal


def test_compile_f_policy_is_faithful():
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    f_policy = federate.compile_f_policy(policy)
    # grants restated as etkl:grantsTag
    pairs = {(str(r), str(t)) for r, t in f_policy.subject_objects(ETKL.grantsTag)}
    assert (str(TX["role-opo"]), str(TX.phi)) in pairs
    # and the template's policy triple is present
    assert (None, RDF.type, F.AccessPolicy) in f_policy
    v = federate.certify_f_faithful(policy, f_policy)
    assert v.ok, v


def test_certify_flags_dropped_grant():
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    f_policy = federate.compile_f_policy(policy)
    f_policy.remove((TX["role-opo"], ETKL.grantsTag, TX.phi))   # drop a grant
    v = federate.certify_f_faithful(policy, f_policy)
    assert not v.ok and (str(TX["role-opo"]), str(TX.phi)) in v.missing


def test_certify_flags_extra_grant():
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    f_policy = federate.compile_f_policy(policy)
    f_policy.add((TX["role-recipient-ctr"], ETKL.grantsTag, TX.phi))   # phi not granted to recipient by ODRL
    v = federate.certify_f_faithful(policy, f_policy)
    assert not v.ok and (str(TX["role-recipient-ctr"]), str(TX.phi)) in v.extra


def test_certify_flags_broken_ai_inherits_user():
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    grants = interpret.run(os.path.join(QUERIES, "compile-f-grants.rq"), policy)
    # a template variant whose f:query resolves role WITHOUT the actedOnBehalfOf leg
    bad = Graph()
    pol = URIRef("urn:bad:policy")
    bad.add((pol, RDF.type, F.AccessPolicy))
    bad.add((pol, F.query, Literal(
        '{"where":[{"@id":"?$identity","https://w3id.org/iladub/etkl#hasRole":{"@id":"?role"}},'
        '{"@id":"?role","https://w3id.org/iladub/etkl#grantsTag":{"@id":"?tag"}},'
        '{"@id":"?$this","https://w3id.org/iladub/etkl#sensitivity":{"@id":"?tag"}}]}')))
    v = federate.certify_f_faithful(policy, grants + bad)
    assert not v.identity_ok and not v.ok
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py -k "compile_f_policy or certify_" -q`
Expected: FAIL (`AttributeError: module ... has no attribute 'compile_f_policy'`).

- [ ] **Step 3: Add to `src/iladub/etkl/federate.py`**

Add the Fluree namespace constant near the others (with `ETKL`/`ODRL`), then the functions:

```python
F = Namespace("https://ns.flur.ee/db#")
_FLUREE_TEMPLATE = os.path.join(os.path.dirname(__file__), "..", "fluree", "f-policy-template.jsonld")

# The full IRIs a faithful f:query must reference to preserve AI-inherits-user + the tag join.
_F_QUERY_REFS = (
    "?$identity",
    "http://www.w3.org/ns/prov#actedOnBehalfOf",
    "https://w3id.org/iladub/etkl#hasRole",
    "https://w3id.org/iladub/etkl#grantsTag",
    "https://w3id.org/iladub/etkl#sensitivity",
)


def compile_f_policy(odrl_policy: Graph) -> Graph:
    """Compile the ODRL tag-policy to a Fluree f: policy graph: derive the flat
    etkl:grantsTag grants (AXIOM CONSTRUCT) and union them with the static, data-driven
    f:AccessPolicy template. PROCEDURAL glue — no domain decision, no tuned constant."""
    grants = interpret.run(os.path.join(_QUERIES, "compile-f-grants.rq"), odrl_policy)
    template = Graph().parse(_FLUREE_TEMPLATE, format="json-ld")
    return grants + template


@dataclass(frozen=True)
class FlureeVerdict:
    ok: bool
    missing: tuple       # (role, tag) grants the ODRL policy has but the f: policy dropped
    extra: tuple         # (role, tag) grants the f: policy has but the ODRL policy lacks
    identity_ok: bool    # the template f:query preserves AI-inherits-user + the tag join


def _odrl_grants(policy: Graph) -> set:
    """{ (role, tag) } read-granted by the ODRL policy — mirrors the governed grant pattern
    (policy.subjects(odrl:action odrl:read) -> assignee x target)."""
    out = set()
    for perm in policy.subjects(ODRL.action, ODRL.read):
        roles = {str(r) for r in policy.objects(perm, ODRL.assignee)}
        tags = {str(t) for t in policy.objects(perm, ODRL.target)}
        for r in roles:
            for t in tags:
                out.add((r, t))
    return out


def certify_f_faithful(odrl_policy: Graph, f_policy: Graph, roles=None) -> FlureeVerdict:
    """Faithful iff the f: policy grants exactly what the ODRL policy grants (grant-set
    equivalence) AND its f:query preserves AI-inherits-user + the tag join."""
    odrl = _odrl_grants(odrl_policy)
    fgr = {(str(r), str(t)) for r, t in f_policy.subject_objects(ETKL.grantsTag)}
    if roles is not None:
        rs = {str(r) for r in roles}
        odrl = {(r, t) for (r, t) in odrl if r in rs}
        fgr = {(r, t) for (r, t) in fgr if r in rs}
    missing = tuple(sorted(odrl - fgr))
    extra = tuple(sorted(fgr - odrl))
    query_texts = [str(q) for q in f_policy.objects(None, F.query)]
    identity_ok = any(all(ref in q for ref in _F_QUERY_REFS) for q in query_texts)
    ok = (not missing) and (not extra) and identity_ok
    return FlureeVerdict(ok=ok, missing=missing, extra=extra, identity_ok=identity_ok)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py -q`
Expected: PASS (faithful ok; dropped → missing; extra → extra; no-actedOnBehalfOf template → identity_ok False).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/federate.py tests/test_fluree_policy.py
git commit -m "feat(etkl): compile_f_policy + certify_f_faithful (grant-set equivalence + AI-inherits-user)"
```

---

### Task 5: Transplant demonstrator + full-suite regression

**Files:**
- Test: `tests/test_fluree_policy.py` (append)

**Interfaces:**
- Consumes: `compile_f_policy`, `certify_f_faithful`, the real `examples/transplant/transplant-governance.ttl` ODRL policy.

- [ ] **Step 1: Write the failing demonstrator test (append)**

```python
def test_transplant_policy_compiles_faithfully():
    """The real transplant tag-policy (clinical/phi over OPO/recipient/donor-region/board)
    compiles to an f: policy that certifies faithful — the governed-bot claim at the data layer."""
    gov = Graph().parse(os.path.join(ROOT, "examples", "transplant", "transplant-governance.ttl"),
                        format="turtle")
    f_policy = federate.compile_f_policy(gov)
    v = federate.certify_f_faithful(gov, f_policy)
    assert v.ok, v
    # spot-check: recipient centre is granted clinical, NOT phi, at the data layer
    pairs = {(str(r), str(t)) for r, t in f_policy.subject_objects(ETKL.grantsTag)}
    assert (str(TX["role-recipient-ctr"]), str(TX.clinical)) in pairs
    assert (str(TX["role-recipient-ctr"]), str(TX.phi)) not in pairs
    # and the apex board sees phi
    assert (str(TX["role-board"]), str(TX.phi)) in pairs
```

- [ ] **Step 2: Run the demonstrator test**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_fluree_policy.py::test_transplant_policy_compiles_faithfully -q`
Expected: PASS. If it fails on the recipient/board grants, check the transplant policy grants (post PR #64: recipient `{clinical}`, board `{clinical, phi}`) — do NOT edit the example; the test must reflect the shipped policy.

- [ ] **Step 3: Run the FULL suite (nothing regressed)**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass (prior 522 + the new fluree-policy tests), 5 skipped. The suite takes ~3 min; if a runner times out, run `tests/test_fluree_policy.py` plus `tests/test_source_ownership.py` and `tests/test_governance.py` explicitly and note the full run separately.

- [ ] **Step 4: Commit**

```bash
git add tests/test_fluree_policy.py
git commit -m "test(etkl): transplant tag-policy compiles to a faithful f: policy (governed-bot at the data layer)"
```

---

## Self-Review

**Spec coverage:**
- §3.1 static template → Task 3.
- §3.2 `compile-f-grants.rq` (AXIOM) → Task 2.
- §3.3 `compile_f_policy` + `FlureeVerdict` + `certify_f_faithful` (grant-set equivalence + identity_ok) → Task 4.
- §3.4 `etkl:grantsTag` vocab → Task 1.
- §4 source-ownership (`f:` only under `src/iladub/fluree/`, outside scanned trees) → Tasks 1/3; `test_source_ownership` run in Task 1.
- §5 gate: CONSTRUCT AXIOM (Task 2), compile/oracle PROCEDURAL no-tuned-constant (Task 4) → covered.
- §6 demonstrator + negatives (dropped/extra grant, broken AI-inherits-user) + structural template test → Tasks 3/4/5.

**Deliberate spec simplification (flagged so review knows it is intentional):** the spec's `certify_f_faithful(odrl_policy, f_policy, roles)` signature keeps `roles` as an OPTIONAL param (`roles=None`); grant-set equivalence over `(role, tag)` pairs covers every role without a role list, and `roles`, when given, scopes the check to those roles. This is the spec's per-role intent, expressed as a pair-set difference — not a missing requirement.

**Placeholder scan:** none — every step has full TTL/SPARQL/JSON-LD/Python/command content.

**Type consistency:** `compile_f_policy(odrl_policy) -> Graph`, `certify_f_faithful(odrl_policy, f_policy, roles=None) -> FlureeVerdict(ok, missing, extra, identity_ok)`, `_odrl_grants`, module constants `F`/`_FLUREE_TEMPLATE`/`_F_QUERY_REFS`, `etkl:grantsTag`, Fluree IRI `https://ns.flur.ee/db#` — used consistently across Tasks 1–5. Namespaces `ETKL`/`ODRL`/`F`/`TX` consistent in tests.

**Note on `f:query` vs derived grants (non-collision):** the derived `etkl:grantsTag` triples use real role/tag IRIs; the template's `f:query` is a single string literal that merely *mentions* `grantsTag` as a substring — it produces no `etkl:grantsTag` triple, so `f_grants` (which reads `subject_objects(ETKL.grantsTag)`) counts only the real derived grants. Verified in the design; the tests exercise both.
