# SP3c — Targeted Per-Milestone Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the extraction funnel contract-generic: a context contract declares (and a build-time generator emits) its own BAML extractor, and the closed loop runs the milestone's *targeted* extractor — demonstrated by M5 capturing only `recipientReady`.

**Architecture:** Additive to SP1's offer funnel. `bridge.generate_context_baml` emits a committed BAML class + function per context contract; `to_rdf.ground_typed` grounds a typed object driven by the contract (deriving `must_ground` from `etkl:admissibleScheme`); `m4.capture_for_milestone` reads a milestone's `iladub:extractor`, runs it, and grounds onto the shared `tx:offer` subject. The SP3b loop then captures exactly what the current milestone needs.

**Tech Stack:** Python ≥3.11, rdflib (existing); BAML (build-time generate + the extractor function); pytest. Offline-deterministic; live behind `BAML_LIVE=1`.

**Spec:** `docs/superpowers/specs/2026-06-19-targeted-extraction-sp3c-design.md`

---

## File structure & interfaces

| File | Responsibility |
|---|---|
| `vocab/ontology/iladub.ttl` (modify) | Add `iladub:extractor` (contract → BAML function name). |
| `src/iladub/bridge.py` (modify) | Add `generate_context_baml(graph, contract_node, fn_name, class_name)`. |
| `baml_src/generated_recipient.baml` (create, generated) | The committed M5 extractor (class + function). |
| `src/iladub/to_rdf.py` (modify) | Add `ground_typed(typed_obj, contract_graph, contract_node, terms, subject)`. |
| `src/iladub/m4.py` (modify) | Add `capture_for_milestone(milestone, timeline_graph, document_text, terms, subject, b=None)`. |
| `examples/transplant/heart-timeline.ttl` (modify) | `iladub:extractor` on `tx:ctx-m5`. |
| `examples/transplant/recipient-status.txt` (create) | Synthetic recipient-readiness document. |
| `tests/test_targeted_vocab.py`, `tests/test_targeted.py` (create); `tests/test_bridge.py`, `tests/test_to_rdf.py` (modify) | Tests. |
| `docs/use-case-transplant-m4.md` (modify) | SP3c section. |

**Key signatures (defined across the tasks):**
```python
# bridge.py
def generate_context_baml(graph: Graph, contract_node: URIRef, fn_name: str, class_name: str) -> str

# to_rdf.py
def ground_typed(typed_obj, contract_graph: Graph, contract_node: URIRef,
                 terms: Graph, subject: URIRef) -> ExtractionGraph

# m4.py
def capture_for_milestone(milestone, timeline_graph: Graph, document_text: str,
                          terms: Graph, subject, b=None) -> Graph
```

**Namespaces:** `TX = Namespace("https://example.org/transplant#")`, `HOL = "https://w3id.org/etkl/hol#"`, `ETKL = "https://w3id.org/etkl#"`, `ILADUB = "https://w3id.org/etkl/iladub#"`.

## Notes for the implementer
- Repo root `/Volumes/WD Green/dev/git/iladub`, branch `targeted-extraction-sp3c` (already created). Commit per task. Venv `/Volumes/WD Green/dev/git/iladub/.venv/bin/python`; run `python -m pytest`. `baml-cli` (v0.222) is installed; `baml_client/` is gitignored (regenerated from `baml_src/`).
- Deterministic everywhere except the BAML extractor call, which tests monkeypatch (`sync_client.b`) offline; live behind `BAML_LIVE=1`. CI never calls the API.
- `must_ground` is **derived**: a field with `etkl:admissibleScheme` must ground; without one it is a free literal. The existing offer `to_rdf` is untouched.

---

### Task 1: `iladub:extractor` vocabulary

**Files:**
- Modify: `vocab/ontology/iladub.ttl`
- Test: `tests/test_targeted_vocab.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_targeted_vocab.py`:
```python
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ILADUB = Namespace("https://w3id.org/etkl/iladub#")


def test_iladub_defines_extractor_property():
    g = Graph().parse(os.path.join(ROOT, "vocab", "ontology", "iladub.ttl"), format="turtle")
    assert (ILADUB.extractor, RDF.type, OWL.DatatypeProperty) in g
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_targeted_vocab.py -v`
Expected: FAIL (`iladub:extractor` not defined).

- [ ] **Step 3: Append to `vocab/ontology/iladub.ttl`** (prefixes already declared at top of that file):
```turtle
#################################################################
#  Contract-generic extraction binding (SP3c)
#################################################################

iladub:extractor a owl:DatatypeProperty ;
    rdfs:label "extractor"@en ;
    rdfs:domain etkl:SemanticDataContract ;
    rdfs:range rdfs:Literal ;
    rdfs:comment "Name of the build-time-generated BAML function that extracts this contract's fields."@en .
```
(If `etkl:` or `owl:`/`rdfs:` prefixes are not declared in iladub.ttl's header, add the missing `@prefix` lines near the others. Report if you had to.)

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_targeted_vocab.py tests/test_vocab_shapes.py -v && python -m pytest -q`
Expected: new test PASSES; existing vocab tests PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add vocab/ontology/iladub.ttl tests/test_targeted_vocab.py
git commit -m "feat(sp3c): iladub:extractor — contract declares its BAML extractor"
```

---

### Task 2: `generate_context_baml` + committed M5 extractor

**Files:**
- Modify: `src/iladub/bridge.py`
- Create: `baml_src/generated_recipient.baml`
- Test: `tests/test_bridge.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_bridge.py`:
```python
from rdflib import Namespace as _NS
TX = _NS("https://example.org/transplant#")
GENERATED_RECIPIENT = os.path.join(ROOT, "baml_src", "generated_recipient.baml")


def _heart_graph():
    return Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle")


def test_generate_context_baml_emits_class_and_function():
    from iladub.bridge import generate_context_baml
    out = generate_context_baml(_heart_graph(), TX["ctx-m5"],
                                "ExtractRecipientContext", "RecipientContext")
    assert "class RecipientContext {" in out
    assert "recipientReady CodedConcept?" in out
    assert "function ExtractRecipientContext(doc: string) -> RecipientContext {" in out


def test_generated_recipient_in_sync():
    from iladub.bridge import generate_context_baml
    with open(GENERATED_RECIPIENT, encoding="utf-8") as fh:
        committed = fh.read()
    assert committed == generate_context_baml(_heart_graph(), TX["ctx-m5"],
                                              "ExtractRecipientContext", "RecipientContext")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_bridge.py -k "context_baml or recipient_in_sync" -v`
Expected: FAIL with `ImportError: cannot import name 'generate_context_baml'`.

- [ ] **Step 3: Add `generate_context_baml` to `src/iladub/bridge.py`**

Append (the module already defines `ETKL`, `Graph`, `URIRef`):
```python
def generate_context_baml(graph: Graph, contract_node: URIRef,
                          fn_name: str, class_name: str) -> str:
    """Emit a BAML class + extraction function for ONE context contract's fields.
    Deterministic, build-time; references the shared CodedConcept (generated_types.baml)."""
    props = []
    for field in graph.objects(contract_node, ETKL.hasField):
        prop = graph.value(field, ETKL.fillsProperty)
        if prop is not None:
            props.append(str(prop).rsplit("#", 1)[-1])
    props = sorted(set(props))
    field_list = ", ".join(props)

    lines = [
        "// GENERATED by iladub.bridge.generate_context_baml — do not hand-edit.",
        f"// Context contract: {contract_node}",
        "",
        f"class {class_name} {{",
    ]
    for p in props:
        lines.append(f"  {p} CodedConcept?")
    lines += [
        "}",
        "",
        f"function {fn_name}(doc: string) -> {class_name} {{",
        "  client Claude",
        '  prompt #"',
        f"    From the document below, extract ONLY these fields: {field_list}.",
        "    For each, copy the exact source phrase into source_quote and give a 0..1 confidence.",
        "    If a field is absent, omit it. Do not invent values.",
        "",
        "    Document:",
        "    ---",
        "    {{ doc }}",
        "    ---",
        "    {{ ctx.output_format }}",
        '  "#',
        "}",
    ]
    return "\n".join(lines).rstrip() + "\n"
```

- [ ] **Step 4: Generate the committed file, run the structural + sync tests**

Run (from repo root):
```bash
python -c "from rdflib import Graph, Namespace; from iladub.bridge import generate_context_baml; \
TX=Namespace('https://example.org/transplant#'); \
g=Graph().parse('examples/transplant/heart-timeline.ttl'); \
open('baml_src/generated_recipient.baml','w').write(generate_context_baml(g, TX['ctx-m5'], 'ExtractRecipientContext', 'RecipientContext'))"
python -m pytest tests/test_bridge.py -v
```
Expected: the two new tests PASS (sync matches by construction) and the pre-existing bridge tests still PASS.

- [ ] **Step 5: Regenerate the BAML client and confirm the new symbols**

Run:
```bash
baml-cli generate --from baml_src
python -c "from baml_client.types import RecipientContext; from baml_client import b; assert hasattr(b,'ExtractRecipientContext'); print('ok')"
```
Expected: prints `ok`.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/bridge.py baml_src/generated_recipient.baml tests/test_bridge.py
git commit -m "feat(sp3c): generate_context_baml + committed M5 recipient extractor"
```

---

### Task 3: `ground_typed` (contract-driven grounding)

**Files:**
- Modify: `src/iladub/to_rdf.py`
- Test: `tests/test_to_rdf.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_to_rdf.py`:
```python
from types import SimpleNamespace
from iladub.to_rdf import ground_typed
from rdflib.namespace import RDF as _RDF

HEART = os.path.join(TXD, "heart-timeline.ttl")


def _heart():
    return Graph().parse(HEART, format="turtle")


def test_ground_typed_free_literal_field_is_asserted():
    # tx:recipientReady (M5) has no admissibleScheme -> asserted as a free literal
    typed = SimpleNamespace(recipientReady=CodedConcept("READY", "readiness: READY", 0.9))
    eg = ground_typed(typed, _heart(), TX["ctx-m5"], _terms(), TX["offer"])
    assert (TX["offer"], TX.recipientReady, Literal("READY")) in eg.graph


def test_ground_typed_unresolved_scheme_field_becomes_proposition():
    # ctx-m4: organ has admissibleScheme; "Zebra" does not resolve -> proposition; abo "O" resolves
    typed = SimpleNamespace(organ=CodedConcept("Zebra", "organ: Zebra", 0.3),
                            aboGroup=CodedConcept("O", "blood group O", 0.9))
    eg = ground_typed(typed, _heart(), TX["ctx-m4"], _terms(), TX["offer"])
    assert (TX["offer"], TX.aboGroup, Literal("O")) in eg.graph
    assert len(list(eg.propositions.subjects(_RDF.type, ILADUB.CandidateConcept))) == 1
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_to_rdf.py -k ground_typed -v`
Expected: FAIL with `ImportError: cannot import name 'ground_typed'`.

- [ ] **Step 3: Implement `ground_typed`**

In `src/iladub/to_rdf.py`, add `ETKL` to the namespace block (next to the existing `TX`/`ILADUB`/`XSD`):
```python
ETKL = Namespace("https://w3id.org/etkl#")
```
Then append the function:
```python
def ground_typed(typed_obj, contract_graph: Graph, contract_node: URIRef,
                 terms: Graph, subject: URIRef) -> ExtractionGraph:
    """Map a typed extraction object to RDF, driven by ONE contract (contract_node):
    each etkl:hasField's fillsProperty local-name is read off typed_obj; a field WITH an
    etkl:admissibleScheme must ground (unresolved -> CandidateConcept), a field WITHOUT one
    is asserted as a free literal on `subject`."""
    eg = ExtractionGraph()
    n = 0
    for field in contract_graph.objects(contract_node, ETKL.hasField):
        prop = contract_graph.value(field, ETKL.fillsProperty)
        if prop is None:
            continue
        cc = getattr(typed_obj, str(prop).rsplit("#", 1)[-1], None)
        if cc is None:
            continue
        must_ground = contract_graph.value(field, ETKL.admissibleScheme) is not None
        if (not must_ground) or _resolves(terms, cc.value):
            eg.graph.add((subject, prop, Literal(cc.value)))
        else:
            n += 1
            cand = ILADUB[f"candidate-{n}"]
            region = BNode()
            eg.propositions.add((cand, RDF.type, ILADUB.CandidateConcept))
            eg.propositions.add((cand, ILADUB.confidence, Literal(cc.confidence, datatype=XSD.decimal)))
            eg.propositions.add((cand, ILADUB.fromRegion, region))
            eg.propositions.add((region, RDF.type, ILADUB.SourceRegion))
            eg.propositions.add((region, ILADUB.surfaceText, Literal(cc.source_quote)))
    return eg
```

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_to_rdf.py -v && python -m pytest -q`
Expected: both new tests PASS; the existing offer `to_rdf` tests still PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/to_rdf.py tests/test_to_rdf.py
git commit -m "feat(sp3c): ground_typed — contract-driven grounding (must_ground derived)"
```

---

### Task 4: M5 instance + `capture_for_milestone`

**Files:**
- Modify: `examples/transplant/heart-timeline.ttl`, `src/iladub/m4.py`
- Create: `examples/transplant/recipient-status.txt`
- Test: `tests/test_targeted.py`

- [ ] **Step 1: Declare the extractor on `tx:ctx-m5` + add the recipient document**

In `examples/transplant/heart-timeline.ttl`: ensure the prefix line
`@prefix iladub: <https://w3id.org/etkl/iladub#> .` is present (add it next to the other
`@prefix` lines if missing), then change the `tx:ctx-m5` triple to add the extractor:
```turtle
tx:ctx-m5 a etkl:SemanticDataContract ; etkl:hasField tx:tf-recipient-ready ;
    iladub:extractor "ExtractRecipientContext" .
```

Create `examples/transplant/recipient-status.txt`:
```text
RECIPIENT STATUS REPORT (synthetic)
Recipient ref: ZRH-CAND-204
Recipient readiness: READY. Admitted; anaesthesia briefed.
Final crossmatch: negative.
```

- [ ] **Step 2: Write the failing `capture_for_milestone` test**

Create `tests/test_targeted.py`:
```python
import os
from rdflib import Graph, Namespace, Literal
from baml_client import sync_client
from baml_client.types import RecipientContext, CodedConcept
from iladub.timeline import Timeline
from iladub.m4 import capture_for_milestone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")


def _heart_graph():
    return Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle")


def _terms():
    return Graph().parse(os.path.join(TXD, "transplant-terms.ttl"), format="turtle")


def test_capture_for_milestone_grounds_recipient_ready(monkeypatch):
    monkeypatch.setattr(sync_client.b, "ExtractRecipientContext",
        lambda doc: RecipientContext(
            recipientReady=CodedConcept(value="READY", source_quote="readiness: READY", confidence=0.9)),
        raising=True)
    g = _heart_graph()
    tl = Timeline.from_graph(g)
    m5 = next(m for m in tl.ordered() if m.order == 5)
    captured = capture_for_milestone(m5, g, "ignored text", _terms(), TX["offer"])
    assert (TX["offer"], TX.recipientReady, Literal("READY")) in captured
```

- [ ] **Step 3: Run it to verify it fails**

Run: `python -m pytest tests/test_targeted.py -v`
Expected: FAIL with `ImportError: cannot import name 'capture_for_milestone' from 'iladub.m4'`.

- [ ] **Step 4: Add `capture_for_milestone` to `src/iladub/m4.py`**

Add near `capture_context` (it introduces two namespaces + a local import):
```python
from rdflib import Namespace as _Namespace

_HOL = _Namespace("https://w3id.org/etkl/hol#")
_ILADUB = _Namespace("https://w3id.org/etkl/iladub#")


def capture_for_milestone(milestone, timeline_graph: Graph, document_text: str,
                          terms: Graph, subject, b=None) -> Graph:
    """Run the milestone's declared (contract-targeted) extractor over a document and
    return the grounded graph on `subject`. The extractor is named by the milestone's
    requiresContext contract via iladub:extractor."""
    from baml_client import sync_client
    from .to_rdf import ground_typed
    b = b if b is not None else sync_client.b
    contract_node = timeline_graph.value(milestone.id, _HOL.requiresContext)
    fn_name = str(timeline_graph.value(contract_node, _ILADUB.extractor))
    typed = getattr(b, fn_name)(document_text)
    return ground_typed(typed, timeline_graph, contract_node, terms, subject).graph
```

- [ ] **Step 5: Run the test + full suite**

Run: `python -m pytest tests/test_targeted.py -v && python -m pytest -q`
Expected: PASS; full suite green (live tests still skipped).

- [ ] **Step 6: Commit**

```bash
git add examples/transplant/heart-timeline.ttl examples/transplant/recipient-status.txt src/iladub/m4.py tests/test_targeted.py
git commit -m "feat(sp3c): M5 extractor declaration + capture_for_milestone"
```

---

### Task 5: Targeted-capture loop scenario + live-gated smoke

**Files:**
- Modify: `tests/test_targeted.py`

- [ ] **Step 1: Add the failing targeted-loop test (proves only the M5 extractor runs)**

Append to `tests/test_targeted.py`:
```python
import pytest
from iladub.timeline import Cursor
from iladub.loop import advance_with_capture


def test_targeted_capture_advances_m5_to_m6(monkeypatch):
    # The non-targeted agents must NOT be called — make them explode if they are.
    def _boom(doc):
        raise AssertionError("a non-targeted extractor was called")
    for name in ("ExtractDonorClinical", "ExtractImmunology", "ExtractLogistics"):
        monkeypatch.setattr(sync_client.b, name, _boom, raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractRecipientContext",
        lambda doc: RecipientContext(
            recipientReady=CodedConcept(value="READY", source_quote="readiness: READY", confidence=0.9)),
        raising=True)

    g = _heart_graph()
    tl = Timeline.from_graph(g)
    ctx = Graph()
    ctx.add((TX["offer"], TX.organ, Literal("Heart")))      # M4 already satisfied
    ctx.add((TX["offer"], TX.aboGroup, Literal("O")))
    cursor = Cursor(tl)
    assert cursor.advance(ctx, TX["offer"]) is True          # M4 -> M5
    assert cursor.current.order == 5

    step = advance_with_capture(
        tl, cursor, ctx,
        lambda: capture_for_milestone(cursor.current, g, "recipient text", _terms(), TX["offer"]),
        TX["offer"])
    assert step.advanced is True
    assert cursor.current.order == 6
    assert (TX["offer"], TX.recipientReady, Literal("READY")) in ctx


@pytest.mark.skipif(os.environ.get("BAML_LIVE") != "1",
                    reason="set BAML_LIVE=1 to call the real API")
def test_targeted_capture_live():
    g = _heart_graph()
    tl = Timeline.from_graph(g)
    m5 = next(m for m in tl.ordered() if m.order == 5)
    doc = open(os.path.join(TXD, "recipient-status.txt"), encoding="utf-8").read()
    captured = capture_for_milestone(m5, g, doc, _terms(), TX["offer"])
    assert (TX["offer"], TX.recipientReady, None) in captured
```

- [ ] **Step 2: Run it offline (live skipped)**

Run: `python -m pytest tests/test_targeted.py -v`
Expected: `test_targeted_capture_advances_m5_to_m6` PASSES (the `_boom` agents are never called — proving targeting); `test_targeted_capture_live` SKIPPED.

- [ ] **Step 3: Run the full suite**

Run: `python -m pytest -q`
Expected: full suite green; live tests (`test_ping_live`, `test_compile_offer_live`, `test_closed_loop_live`, `test_targeted_capture_live`) skipped.

- [ ] **Step 4: Commit**

```bash
git add tests/test_targeted.py
git commit -m "test(sp3c): targeted-capture loop advances M5 (non-targeted agents never run)"
```

---

### Task 6: Documentation

**Files:**
- Modify: `docs/use-case-transplant-m4.md`

- [ ] **Step 1: Append the SP3c section**

Append to `docs/use-case-transplant-m4.md`:
```markdown

## Targeted capture (SP3c)

SP3b drove capture by running the whole offer funnel. SP3c makes the funnel **contract-generic**:
each milestone's required-context contract declares its own extractor (`iladub:extractor`), and
`iladub.bridge.generate_context_baml` emits — at build time — a BAML class + function for exactly
that contract's fields. `iladub.m4.capture_for_milestone` reads the declaration, runs the
milestone's extractor, and grounds it via `iladub.to_rdf.ground_typed` (a field with an
`etkl:admissibleScheme` must ground; otherwise it is a free literal).

Worked example: the cursor reaches M5, which needs `tx:recipientReady`. A recipient-status report
arrives; the loop runs **only** `ExtractRecipientContext` (not the organ/ABO agents), grounds
`tx:recipientReady`, and advances to M6. Extraction is now driven by what *this* milestone needs.

> Build-time-faithful: the per-milestone extractor is generated, committed, and sync-tested before
> any document is compiled. M4 still uses the SP1 offer funnel; generating extractors for every
> milestone (and retiring the fixed agents) is the natural next step.
```

- [ ] **Step 2: Verify markdown**

Run: `python -c "t=open('docs/use-case-transplant-m4.md').read(); assert 'SP3c' in t and 'generate_context_baml' in t; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 3: Commit**

```bash
git add docs/use-case-transplant-m4.md
git commit -m "docs(sp3c): targeted per-milestone capture section"
```

---

## Coverage map (plan ↔ spec)
- Spec §3 (`iladub:extractor`) → Task 1. §4 (`generate_context_baml`) → Task 2. §5 (`ground_typed`) → Task 3. §6 (`capture_for_milestone`) → Task 4. §7 (M5 instance + recipient doc) → Task 4. §8 (money-shot) → Task 5. §9 (testing) → Tasks 2–5. §10 (files) → all tasks.
- Spec §2 out-of-scope (migrating M4, refactoring offer `to_rdf`, enum fields, document routing) → not built.

## Note on the proposition counter
`ground_typed` numbers candidate IRIs (`candidate-1`, …) per call, like the offer `to_rdf`. Because
each call builds a fresh `ExtractionGraph`, the numbering is deterministic per invocation; the tests
assert on counts/membership, not specific candidate IRIs.
