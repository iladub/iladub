# Transplant DataBook — Slice 1 (M4 raw→clean) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile a raw organ-offer DataBook into a single self-contained CleanDocumentHolon DataBook (grounded graph + propositions + M4 decision + provenance stamp), with no loose intermediate `.ttl`.

**Architecture:** Option C — DataBooks are the authored/stored artifact; on load their fenced blocks are parsed into transient rdflib graphs, the existing SP1 funnel runs unchanged, and the output is re-serialized to a DataBook. The only new code is a thin Python DataBook I/O adapter; the existing grounding/decision engine is untouched.

**Tech Stack:** Python, rdflib, pyshacl, PyYAML (newly declared), BAML (monkeypatched in tests), pytest.

**Branch:** `transplant-databook` (the design spec is already committed here).

---

## File structure

- Create `src/iladub/databook.py` — DataBook reader/writer adapter (the only new component). One responsibility: markdown DataBook ⇄ (frontmatter dict, ordered typed blocks, prose). No triplestore, no CLI.
- Modify `src/iladub/m4.py` — extract a text-based funnel core (`_compile_text`), add `compile_offer_databook`.
- Modify `pyproject.toml` — declare `pyyaml`.
- Create `examples/transplant/offer.databook.md` — the raw RawDocumentHolon DataBook.
- Create `examples/transplant/offer.clean.databook.md` — curated conformant CleanDocumentHolon (the discipline's "conformant" artifact).
- Create `examples/transplant/offer.clean.leak.databook.md` — curated leak (asserted block missing `tx:organ`).
- Create `tests/test_databook.py` — adapter unit tests.
- Create `tests/test_m4_databook.py` — the M4 vertical + conformant/leak tests.

---

## Task 1: DataBook adapter — parse (frontmatter + blocks + prose)

**Files:**
- Modify: `pyproject.toml`
- Create: `src/iladub/databook.py`
- Test: `tests/test_databook.py`

- [ ] **Step 1: Declare the PyYAML dependency**

In `pyproject.toml`, change the `dependencies` list to:

```toml
dependencies = [
    "rdflib>=7.0",
    "pyshacl>=0.26",
    "pyyaml>=6.0",
]
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_databook.py`:

```python
import os
from iladub.databook import read_databook, write_databook, Block, validate_frontmatter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAMPLE = """---
id: https://example.org/db/sample
title: Sample
type: databook
version: 1.0.0
created: 2026-06-23
---

Some prose.

<!-- databook:id: asserted -->
<!-- databook:graph: https://example.org/db/sample#g -->
```turtle
@prefix ex: <https://example.org/> .
ex:a ex:b ex:c .
```
"""

def test_read_parses_frontmatter_prose_and_block(tmp_path):
    p = tmp_path / "sample.databook.md"
    p.write_text(SAMPLE, encoding="utf-8")
    db = read_databook(str(p))
    assert db.frontmatter["id"] == "https://example.org/db/sample"
    assert db.frontmatter["type"] == "databook"
    assert "Some prose." in db.prose
    assert len(db.blocks) == 1
    b = db.blocks[0]
    assert b.lang == "turtle"
    assert b.id == "asserted"
    assert b.graph_iri == "https://example.org/db/sample#g"
    assert "ex:a ex:b ex:c ." in b.content
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_databook.py::test_read_parses_frontmatter_prose_and_block -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.databook'`

- [ ] **Step 4: Write minimal implementation**

Create `src/iladub/databook.py`:

```python
"""Thin DataBook (W3C Holon CG) I/O adapter — read/write only.

A DataBook is how a holon is serialized: YAML frontmatter (context layer),
typed fenced blocks (interior), prose (projection). This module parses and
emits that markdown; it deliberately does NOT implement the DataBook CLI,
triplestore push/pull, or the format spec — those are the CG's responsibility.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

import yaml
from rdflib import Graph

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_META_RE = re.compile(r"<!--\s*databook:(\w+):\s*(.*?)\s*-->")
_FENCE_OPEN = re.compile(r"^```(\w*)\s*$")
_FENCE_CLOSE = re.compile(r"^```\s*$")

_RDF_LANGS = {"turtle", "turtle12", "trig", "shacl", "ntriples"}


@dataclass
class Block:
    lang: str
    content: str
    id: Optional[str] = None
    graph_iri: Optional[str] = None


@dataclass
class Databook:
    frontmatter: dict = field(default_factory=dict)
    prose: str = ""
    blocks: list = field(default_factory=list)

    def graph(self, *selectors) -> Graph:
        """Parse the requested RDF blocks (by block id or by lang) into one graph.
        With no selectors, merge every RDF block."""
        g = Graph()
        want = set(selectors)
        for b in self.blocks:
            if b.lang not in _RDF_LANGS:
                continue
            if want and b.id not in want and b.lang not in want:
                continue
            g.parse(data=b.content, format="turtle")
        return g


def read_databook(path: str) -> Databook:
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    m = _FM_RE.match(raw)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    frontmatter = yaml.safe_load(m.group(1)) or {}
    blocks: list = []
    prose_lines: list = []
    pending: dict = {}
    lines = m.group(2).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        meta = _META_RE.search(line)
        fence = _FENCE_OPEN.match(line)
        if meta and not fence:
            pending[meta.group(1)] = meta.group(2)
            i += 1
            continue
        if fence:
            lang = fence.group(1)
            body: list = []
            i += 1
            while i < len(lines) and not _FENCE_CLOSE.match(lines[i]):
                body.append(lines[i])
                i += 1
            i += 1  # consume closing fence
            blocks.append(Block(lang=lang, content="\n".join(body),
                                id=pending.get("id"), graph_iri=pending.get("graph")))
            pending = {}
            continue
        prose_lines.append(line)
        i += 1
    return Databook(frontmatter=frontmatter,
                    prose="\n".join(prose_lines).strip(),
                    blocks=blocks)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_databook.py::test_read_parses_frontmatter_prose_and_block -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/iladub/databook.py tests/test_databook.py
git commit -m "feat(databook): DataBook reader (frontmatter + typed blocks + prose)"
```

---

## Task 2: DataBook adapter — write + round-trip

**Files:**
- Modify: `src/iladub/databook.py`
- Test: `tests/test_databook.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_databook.py`:

```python
def test_write_then_read_roundtrip(tmp_path):
    fm = {"id": "https://example.org/db/x", "title": "X", "type": "databook",
          "version": "1.0.0", "created": "2026-06-23"}
    blocks = [Block(lang="turtle", id="asserted", graph_iri="https://example.org/db/x#g",
                    content="@prefix ex: <https://example.org/> .\nex:a ex:b ex:c .")]
    p = tmp_path / "x.databook.md"
    write_databook(fm, blocks, "Hello prose.", str(p))
    db = read_databook(str(p))
    assert db.frontmatter["id"] == "https://example.org/db/x"
    assert db.prose == "Hello prose."
    assert len(db.blocks) == 1
    assert db.blocks[0].id == "asserted"
    assert db.blocks[0].graph_iri == "https://example.org/db/x#g"
    assert "ex:a ex:b ex:c ." in db.blocks[0].content
    assert db.blocks[0].lang == "turtle"

def test_graph_selector_extracts_block(tmp_path):
    fm = {"id": "https://example.org/db/y", "title": "Y", "type": "databook",
          "version": "1.0.0", "created": "2026-06-23"}
    blocks = [Block(lang="turtle", id="asserted",
                    content="@prefix ex: <https://example.org/> .\nex:s ex:p ex:o .")]
    p = tmp_path / "y.databook.md"
    write_databook(fm, blocks, "", str(p))
    g = read_databook(str(p)).graph("asserted")
    assert len(g) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_databook.py::test_write_then_read_roundtrip -v`
Expected: FAIL with `ImportError: cannot import name 'write_databook'` (the import at the top of the test file now references it)

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/databook.py`:

```python
def write_databook(frontmatter: dict, blocks, prose: str, path: str) -> None:
    out = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", ""]
    if prose:
        out.append(prose)
        out.append("")
    for b in blocks:
        if b.id:
            out.append(f"<!-- databook:id: {b.id} -->")
        if b.graph_iri:
            out.append(f"<!-- databook:graph: {b.graph_iri} -->")
        out.append(f"```{b.lang}")
        out.append(b.content)
        out.append("```")
        out.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out).rstrip() + "\n")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_databook.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add src/iladub/databook.py tests/test_databook.py
git commit -m "feat(databook): writer + round-trip + graph() selector"
```

---

## Task 3: DataBook adapter — frontmatter validation

**Files:**
- Modify: `src/iladub/databook.py`
- Test: `tests/test_databook.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_databook.py`:

```python
def test_validate_frontmatter_required_keys():
    assert validate_frontmatter({"id": "x", "title": "t", "type": "databook",
                                 "version": "1.0.0", "created": "2026-06-23"}) == []
    errs = validate_frontmatter({"id": "x"})
    assert any("title" in e for e in errs)

def test_validate_frontmatter_requires_process_stamp():
    fm = {"id": "x", "title": "t", "type": "databook", "version": "1.0.0",
          "created": "2026-06-23"}
    errs = validate_frontmatter(fm, require_process=True)
    assert any("process" in e for e in errs)
    fm["process"] = {"transformer": "BAML", "transformer_type": "llm",
                     "inputs": [], "timestamp": "2026-06-23T00:00:00Z"}
    assert validate_frontmatter(fm, require_process=True) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_databook.py::test_validate_frontmatter_required_keys -v`
Expected: FAIL with `ImportError: cannot import name 'validate_frontmatter'`

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/databook.py`:

```python
_REQUIRED = ("id", "title", "type", "version", "created")
_PROCESS_REQUIRED = ("transformer", "transformer_type", "inputs", "timestamp")


def validate_frontmatter(fm: dict, require_process: bool = False) -> list:
    """Return a list of human-readable problems (empty == valid). Lightweight CG-key
    check; full databook.shacl.ttl / JSON-schema conformance is a later hardening step."""
    errs = [f"missing frontmatter key: {k}" for k in _REQUIRED if k not in fm]
    if require_process:
        proc = fm.get("process")
        if not isinstance(proc, dict):
            errs.append("missing process stamp")
        else:
            errs += [f"missing process.{k}" for k in _PROCESS_REQUIRED if k not in proc]
    return errs
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_databook.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/iladub/databook.py tests/test_databook.py
git commit -m "feat(databook): validate_frontmatter (required keys + process stamp)"
```

---

## Task 4: The raw offer DataBook (RawDocumentHolon)

**Files:**
- Create: `examples/transplant/offer.databook.md`
- Test: `tests/test_m4_databook.py`

- [ ] **Step 1: Create the raw DataBook**

Create `examples/transplant/offer.databook.md`:

```markdown
---
id: https://example.org/transplant/databooks/offer-2026-0091
title: "Donor organ offer ET-2026-0091 (raw)"
type: databook
version: 1.0.0
created: 2026-06-23
description: >
  RawDocumentHolon: the unstructured EUROTRANSPLANT donor organ offer, carried
  with its acquisition provenance. Synthetic, domain-illustrative.
source:
  system: EUROTRANSPLANT
  reference: ET-2026-0091
  retrieved: 2026-06-23
---

EUROTRANSPLANT — DONOR ORGAN OFFER (synthetic)
Offer ref: ET-2026-0091
Donor: 41 y, cause of death: anoxic brain injury.
Organ offered: HEART. Echocardiography: LVEF 60%.
Blood group: O (donor). HLA: A2, B7, DR15.
Serology: HIV negative, HBV negative, HCV negative.
Donor size: 78 kg, 180 cm.
Note: donor had transient takotsubo-pattern wall-motion abnormality on admission.
Logistics: recovery hospital Bern; recipient centre Zurich; estimated transport 95 minutes.
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_m4_databook.py`:

```python
import os
from rdflib import Namespace
from rdflib.namespace import RDF
from iladub.databook import read_databook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")

def test_raw_offer_databook_loads():
    db = read_databook(os.path.join(TXD, "offer.databook.md"))
    assert db.frontmatter["id"].endswith("offer-2026-0091")
    assert db.frontmatter["source"]["reference"] == "ET-2026-0091"
    assert "Organ offered: HEART" in db.prose
```

- [ ] **Step 3: Run test to verify it passes**

Run: `python -m pytest tests/test_m4_databook.py::test_raw_offer_databook_loads -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add examples/transplant/offer.databook.md tests/test_m4_databook.py
git commit -m "feat(transplant): raw offer DataBook (RawDocumentHolon)"
```

---

## Task 5: Extract a text-based funnel core in m4 (no behavior change)

**Files:**
- Modify: `src/iladub/m4.py` (the `compile_offer` function)
- Test: `tests/test_m4_pipeline.py` (existing — must still pass)

- [ ] **Step 1: Refactor `compile_offer` to delegate to `_compile_text`**

In `src/iladub/m4.py`, replace the entire `compile_offer` function body with a thin wrapper plus a new private core. The new code:

```python
def _compile_text(text: str,
                  terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                  shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                  ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                  recipient_abo: str = "O",
                  ischemia_limit_minutes: int = 240) -> M4Result:
    terms = Graph().parse(terms_path, format="turtle")
    extraction = extract_offer(text)
    eg = to_rdf(extraction, terms)

    shapes = Graph().parse(shapes_path, format="turtle")
    knowledge = Graph().parse(ontology_path, format="turtle")
    result = validate(eg.graph, shapes, knowledge)

    minutes = int(extraction.projected_transport_minutes.value) \
        if extraction.projected_transport_minutes else ischemia_limit_minutes + 1
    donor_abo = extraction.abo_group.value if extraction.abo_group else ""
    decision = evaluate_m4(M4Context(donor_abo=donor_abo, recipient_abo=recipient_abo,
                                     projected_ischemia_minutes=minutes,
                                     ischemia_limit_minutes=ischemia_limit_minutes))
    return M4Result(extraction_graph=eg, validation=result, decision=decision,
                    decision_graph=build_decision_holon(decision))


def compile_offer(doc_path: str,
                  terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                  shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                  ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                  recipient_abo: str = "O",
                  ischemia_limit_minutes: int = 240) -> M4Result:
    return _compile_text(read_document(doc_path), terms_path, shapes_path,
                         ontology_path, recipient_abo, ischemia_limit_minutes)
```

- [ ] **Step 2: Run the existing M4 pipeline test to verify no regression**

Run: `python -m pytest tests/test_m4_pipeline.py -v`
Expected: PASS (the refactor is behavior-preserving; `test_compile_offer_validates_and_recommends_accept` still passes)

- [ ] **Step 3: Commit**

```bash
git add src/iladub/m4.py
git commit -m "refactor(m4): extract _compile_text core from compile_offer"
```

---

## Task 6: `compile_offer_databook` — raw DataBook → clean DataBook

**Files:**
- Modify: `src/iladub/m4.py`
- Test: `tests/test_m4_databook.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_m4_databook.py`:

```python
import pytest
from baml_client import sync_client
from baml_client.types import DonorClinical, Immunology, Logistics, CodedConcept
from iladub.m4 import compile_offer_databook
from pyshacl import validate as shacl_validate
from rdflib import Graph

HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")
ILADUB = Namespace("https://w3id.org/etkl/iladub#")

def _patch(monkeypatch):
    cc = lambda v, q, c=0.9: CodedConcept(value=v, source_quote=q, confidence=c)
    monkeypatch.setattr(sync_client.b, "ExtractDonorClinical",
        lambda doc: DonorClinical(organ=cc("Heart", "Organ offered: HEART"),
                                  ejectionFraction=cc("60", "LVEF 60%"),
                                  causeOfDeath=cc("takotsubo-pattern abnormality",
                                                  "transient takotsubo-pattern wall-motion abnormality"),
                                  sizeMetric=cc("78 kg", "Donor size: 78 kg")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractImmunology",
        lambda doc: Immunology(aboGroup=cc("O", "Blood group: O"),
                               hlaTyping=cc("A2, B7, DR15", "HLA: A2, B7, DR15"),
                               serology=cc("HIV negative", "HIV negative")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractLogistics",
        lambda doc: Logistics(projectedTransportMinutes=cc("95", "estimated transport 95 minutes")),
        raising=True)

def test_compile_offer_databook_emits_clean_holon(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out = tmp_path / "offer.clean.databook.md"
    res = compile_offer_databook(os.path.join(TXD, "offer.databook.md"), str(out))
    assert res.decision.recommendation == "accept"

    db = read_databook(str(out))
    ids = {b.id for b in db.blocks}
    assert {"asserted", "propositions", "decision"} <= ids

    # asserted graph passes the offer SHACL shape
    asserted = db.graph("asserted")
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    know = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    conforms, _, _ = shacl_validate(asserted, shacl_graph=shapes, ont_graph=know,
                                    inference="rdfs", advanced=True)
    assert conforms

    # exactly one proposition (the takotsubo candidate)
    props = db.graph("propositions")
    assert len(list(props.subjects(RDF.type, ILADUB.CandidateConcept))) == 1

    # the decision block is the accepted M4 decision holon
    dec = db.graph("decision")
    assert (TX["m4-decision"], HOL.chosen, TX["opt-accept"]) in dec

    # provenance stamp present and names its inputs
    assert "process" in db.frontmatter
    assert db.frontmatter["process"]["inputs"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_m4_databook.py::test_compile_offer_databook_emits_clean_holon -v`
Expected: FAIL with `ImportError: cannot import name 'compile_offer_databook'`

- [ ] **Step 3: Write minimal implementation**

In `src/iladub/m4.py`, add this import near the top (with the other `from .` imports):

```python
from datetime import datetime, timezone
```

Then append the function at the end of `src/iladub/m4.py`:

```python
def compile_offer_databook(in_path: str, out_path: str,
                           terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                           shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                           ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                           recipient_abo: str = "O",
                           ischemia_limit_minutes: int = 240) -> M4Result:
    """Compile a raw-offer DataBook (RawDocumentHolon) into a CleanDocumentHolon DataBook:
    grounded graph + propositions + M4 decision holon + a process provenance stamp."""
    from .databook import read_databook, write_databook, Block

    raw = read_databook(in_path)
    res = _compile_text(raw.prose, terms_path, shapes_path, ontology_path,
                        recipient_abo, ischemia_limit_minutes)

    raw_iri = raw.frontmatter.get("id", "urn:offer")
    clean_iri = raw_iri + ".clean"
    base = "https://example.org/transplant/knowledge/"

    blocks = [
        Block(lang="turtle", id="asserted", graph_iri=clean_iri + "#asserted",
              content=res.extraction_graph.graph.serialize(format="turtle").strip()),
        Block(lang="turtle", id="propositions", graph_iri=clean_iri + "#propositions",
              content=res.extraction_graph.propositions.serialize(format="turtle").strip()),
        Block(lang="turtle", id="decision", graph_iri=clean_iri + "#decision",
              content=res.decision_graph.serialize(format="turtle").strip()),
    ]
    frontmatter = {
        "id": clean_iri,
        "title": "Donor organ offer ET-2026-0091 (compiled)",
        "type": "databook",
        "version": "1.0.0",
        "created": "2026-06-23",
        "process": {
            "transformer": "BAML + Claude",
            "transformer_type": "llm",
            "transformer_iri": "https://api.anthropic.com/v1/models/claude-opus-4-8",
            "inputs": [
                {"iri": raw_iri, "role": "primary"},
                {"iri": base + "offer-contract", "role": "contract"},
                {"iri": base + "transplant-terms", "role": "knowledge"},
                {"iri": base + "offer-shapes", "role": "constraint"},
            ],
            "agent": {"name": "iladub", "role": "orchestrator"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    prose = (
        "## M4 — Offer acceptance decision\n\n"
        f"Recommendation: **{res.decision.recommendation}**. {res.decision.reason}\n\n"
        "`#asserted` carries the grounded offer; `#propositions` holds what could not be "
        "grounded (quarantined, never asserted); `#decision` is the accountable M4 "
        "`hol:DecisionHolon`."
    )
    write_databook(frontmatter, blocks, prose, out_path)
    return res
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_m4_databook.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/iladub/m4.py tests/test_m4_databook.py
git commit -m "feat(m4): compile_offer_databook — raw DataBook -> clean CleanDocumentHolon"
```

---

## Task 7: Curated conformant + leak clean DataBooks (the discipline)

**Files:**
- Create: `examples/transplant/offer.clean.databook.md`
- Create: `examples/transplant/offer.clean.leak.databook.md`
- Test: `tests/test_m4_databook.py`

- [ ] **Step 1: Create the curated conformant clean DataBook**

Create `examples/transplant/offer.clean.databook.md`:

```markdown
---
id: https://example.org/transplant/databooks/offer-2026-0091.clean
title: "Donor organ offer ET-2026-0091 (compiled)"
type: databook
version: 1.0.0
created: 2026-06-23
process:
  transformer: "BAML + Claude"
  transformer_type: llm
  transformer_iri: https://api.anthropic.com/v1/models/claude-opus-4-8
  inputs:
    - iri: https://example.org/transplant/databooks/offer-2026-0091
      role: primary
    - iri: https://example.org/transplant/knowledge/offer-contract
      role: contract
    - iri: https://example.org/transplant/knowledge/transplant-terms
      role: knowledge
    - iri: https://example.org/transplant/knowledge/offer-shapes
      role: constraint
  agent:
    name: iladub
    role: orchestrator
  timestamp: 2026-06-23T00:00:00Z
---

## M4 — Offer acceptance decision

Recommendation: **accept**. ABO compatible and within cold-ischemia window.

<!-- databook:id: asserted -->
<!-- databook:graph: https://example.org/transplant/databooks/offer-2026-0091.clean#asserted -->
```turtle
@prefix tx: <https://example.org/transplant#> .
tx:offer a tx:OrganOffer ;
    tx:organ tx:organ-heart ;
    tx:aboGroup "O" ;
    tx:ejectionFraction "60" .
```

<!-- databook:id: propositions -->
<!-- databook:graph: https://example.org/transplant/databooks/offer-2026-0091.clean#propositions -->
```turtle
@prefix iladub: <https://w3id.org/etkl/iladub#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
iladub:candidate-1 a iladub:CandidateConcept ;
    iladub:confidence "0.9"^^xsd:decimal ;
    iladub:fromRegion [ a iladub:SourceRegion ;
        iladub:surfaceText "transient takotsubo-pattern wall-motion abnormality" ] .
```

<!-- databook:id: decision -->
<!-- databook:graph: https://example.org/transplant/databooks/offer-2026-0091.clean#decision -->
```turtle
@prefix tx: <https://example.org/transplant#> .
@prefix hol: <https://w3id.org/etkl/hol#> .
tx:m4-decision a hol:DecisionHolon ;
    hol:optionSpace tx:opt-accept , tx:opt-decline ;
    hol:chosen tx:opt-accept ;
    hol:decidedBy tx:surgeon-1 ;
    hol:rationale "ABO compatible and within cold-ischemia window." .
tx:opt-accept a hol:Option .
tx:opt-decline a hol:Option ;
    hol:rejectedBecause "ABO compatible and within cold-ischemia window." .
```
```

- [ ] **Step 2: Create the leak variant (asserted block missing `tx:organ`)**

Create `examples/transplant/offer.clean.leak.databook.md` — identical to the conformant file EXCEPT the `asserted` block omits the required `tx:organ` and the frontmatter `id`/title note the leak. Full file:

```markdown
---
id: https://example.org/transplant/databooks/offer-2026-0091.clean-leak
title: "Donor organ offer ET-2026-0091 (compiled, LEAK)"
type: databook
version: 1.0.0
created: 2026-06-23
process:
  transformer: "BAML + Claude"
  transformer_type: llm
  transformer_iri: https://api.anthropic.com/v1/models/claude-opus-4-8
  inputs:
    - iri: https://example.org/transplant/databooks/offer-2026-0091
      role: primary
  agent:
    name: iladub
    role: orchestrator
  timestamp: 2026-06-23T00:00:00Z
---

## M4 — LEAK case (asserted offer missing required organ)

<!-- databook:id: asserted -->
```turtle
@prefix tx: <https://example.org/transplant#> .
tx:offer a tx:OrganOffer ;
    tx:aboGroup "O" ;
    tx:ejectionFraction "60" .
```
```

- [ ] **Step 3: Write the failing tests**

Append to `tests/test_m4_databook.py`:

```python
def test_curated_clean_conformant_passes_shacl():
    db = read_databook(os.path.join(TXD, "offer.clean.databook.md"))
    asserted = db.graph("asserted")
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    know = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    conforms, _, _ = shacl_validate(asserted, shacl_graph=shapes, ont_graph=know,
                                    inference="rdfs", advanced=True)
    assert conforms
    from iladub.databook import validate_frontmatter
    assert validate_frontmatter(db.frontmatter, require_process=True) == []

def test_curated_clean_leak_fails_shacl():
    db = read_databook(os.path.join(TXD, "offer.clean.leak.databook.md"))
    asserted = db.graph("asserted")
    shapes = Graph().parse(os.path.join(TXD, "offer-shapes.ttl"), format="turtle")
    know = Graph().parse(os.path.join(TXD, "transplant-ontology.ttl"), format="turtle")
    conforms, _, _ = shacl_validate(asserted, shacl_graph=shapes, ont_graph=know,
                                    inference="rdfs", advanced=True)
    assert not conforms

def test_frontmatter_leak_detected():
    from iladub.databook import validate_frontmatter
    db = read_databook(os.path.join(TXD, "offer.clean.leak.databook.md"))
    # leak file deliberately keeps a process stamp; prove the check catches a missing one
    fm = dict(db.frontmatter)
    fm.pop("process")
    assert validate_frontmatter(fm, require_process=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_m4_databook.py -v`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Run the full suite to confirm no regressions**

Run: `python -m pytest -q`
Expected: all pass (existing 88 + the new databook/m4-databook tests), prior skips unchanged.

- [ ] **Step 6: Commit**

```bash
git add examples/transplant/offer.clean.databook.md examples/transplant/offer.clean.leak.databook.md tests/test_m4_databook.py
git commit -m "test(transplant): curated conformant + leak clean DataBooks"
```

---

## Done — slice 1 complete

At this point: a raw offer DataBook compiles to a single self-contained clean DataBook (grounded graph + propositions + M4 decision + provenance), the adapter round-trips and validates, the conformant/leak discipline holds, and the existing engine + suite are untouched/green. Fan-out slices (knowledge stack → DataBooks, timeline Process DataBook, reopen lineage, grounding-governance enrichment) follow per the design spec.
