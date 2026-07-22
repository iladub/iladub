# Concept Feed (ET(K)L tables → grounding) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the raw-doc→grounded-graph loop: a bridge reads asserted `tab:RecordTable`s from a `CompilationReport.graph` into per-cell `SurfaceConcept`s (row=record), and a driver grounds them against a contract via the shipped `ground_concept`.

**Architecture:** New `src/iladub/feed.py` (`table_records` bridge + `ground_document` driver + `Record`/`FeedResult`) sits between `iladub.etkl` (the compiled tab: graph) and `iladub.ground` (the grounding oracle). A new offline `MappingGroundingProposer` maps table headers to contract fields. `ground_concept` and the etkl compiler are unchanged.

**Tech Stack:** Python 3.12, rdflib, pytest, reportlab (fixture). No new dependency.

## Global Constraints

- **§8 gate:** the bridge is **PROCEDURAL raw extraction** — RDF reads over the compiled table graph, NO tuned constant, NO IRI-name parsing (headers/values/rows resolved via `coversColumn`/`hasLabel`/`atColumn`/`atRow`). It introduces NO new grounding decision: `ground_concept` is reused unchanged, so grounding soundness (legality gates admission, confidence never does) is inherited.
- **§7:** ungroundable cells (e.g. cause-of-death) are quarantined `CandidateConcept` propositions, never dropped, never faked.
- **Scope (YAGNI):** only asserted `tab:RecordTable` regions are fed (hierarchical/matrix/transposed/escalated/ignored out of scope); row=record, header=field, value=cell; single-token cells; no BAML on the test path.
- **Empirically validated (2026-07-22):** the offer table (Organ/LVEF/ABO/COD × Heart-row + Liver-row) compiles `RECORD_TABLE` and the full compile→feed→ground pipeline yields `FeedResult(records=2, grounded=6, proposed=2)`, 2 `OrganOffer` subjects, 6 `GroundedNode`s, 0 `causeOfDeath` triples. Row 2 MUST use `Liver` (in scheme-organ); `Lung` is NOT in the scheme.
- **Testing:** run ONLY via `./.venv/bin/python -m pytest` (bare python3 uses the wrong rdflib).
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `iladub-concept-feed`.

---

### Task 1: `MappingGroundingProposer` — offline per-header proposer

**Files:**
- Modify: `src/iladub/propose_ground.py`
- Test: `tests/test_concept_feed.py`

**Interfaces:**
- Consumes: `GroundingProposal` (existing).
- Produces: `MappingGroundingProposer(mapping: dict)` with `propose_grounding(concept, fields) -> GroundingProposal` — returns `mapping[concept.text]`, or a `field_iri=None` proposal for an unmapped header.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_concept_feed.py
from iladub.ground import SurfaceConcept
from iladub.propose_ground import GroundingProposal, MappingGroundingProposer


def _c(text, value="x"):
    return SurfaceConcept(text, value, "r0")


def test_mapping_proposer_maps_by_header_text():
    prop = GroundingProposal("urn:f-ef", "urn:anchor", 0.9, "ef", "urn:s")
    mp = MappingGroundingProposer({"LVEF": prop})
    assert mp.propose_grounding(_c("LVEF"), ()) is prop


def test_mapping_proposer_unmapped_header_yields_none_field():
    mp = MappingGroundingProposer({})
    out = mp.propose_grounding(_c("Whatever"), ())
    assert out.field_iri is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -v`
Expected: FAIL — `ImportError: cannot import name 'MappingGroundingProposer'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/propose_ground.py` (module already imports `dataclass`, `Protocol`, and defines `GroundingProposal`):

```python
@dataclass(frozen=True)
class MappingGroundingProposer:
    """Deterministic offline proposer for the concept feed: maps a concept's header TEXT to a
    fixed GroundingProposal (the honest stand-in for the BAML proposer's per-concept field
    proposal). An unmapped header returns a field_iri=None proposal -> the concept quarantines."""
    mapping: dict

    def propose_grounding(self, concept, fields):
        return self.mapping.get(
            concept.text,
            GroundingProposal(None, "https://w3id.org/semanticarts/ns/ontology/gist/Category",
                              0.0, "no mapping for %r" % concept.text,
                              "urn:iladub:suggester/mapping-proposer"),
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/propose_ground.py tests/test_concept_feed.py
git commit -m "feat(iladub): MappingGroundingProposer — offline per-header field proposer (concept feed)"
```

---

### Task 2: `feed.table_records` bridge + `offer_table_pdf` fixture

**Files:**
- Create: `src/iladub/feed.py`
- Modify: `tests/etkl/fixtures.py` (add `offer_table_pdf`)
- Test: `tests/test_concept_feed.py`

**Interfaces:**
- Consumes: `iladub.ground.SurfaceConcept`; the compiled `tab:` graph (`RecordTable`/`hasHeaderNode`/`coversColumn`/`hasLabel`/`cellText`/`EntryCell`/`atColumn`/`atRow`/`wasDerivedFrom`).
- Produces:
  - `@dataclass(frozen=True) Record(row_id: str, concepts: tuple[SurfaceConcept, ...])`.
  - `table_records(graph: Graph) -> list[Record]`.
  - `tests.etkl.fixtures.offer_table_pdf(path) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_concept_feed.py
import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl import compile_tables
from iladub.feed import table_records, Record
from tests.etkl import fixtures as F


def _compiled_offer_graph():
    p = os.path.join(tempfile.mkdtemp(), "offer.pdf"); F.offer_table_pdf(p)
    return compile_tables(p).graph


def test_table_records_two_records_correct_cells():
    recs = table_records(_compiled_offer_graph())
    assert len(recs) == 2
    by_header = [{c.text: c.value for c in r.concepts} for r in recs]
    # order is row-stable; row1 = Heart, row2 = Liver
    assert by_header[0] == {"Organ": "Heart", "LVEF": "60", "ABO": "O", "COD": "MVA"}
    assert by_header[1] == {"Organ": "Liver", "LVEF": "55", "ABO": "A", "COD": "CVA"}
    assert all(isinstance(r, Record) and len(r.concepts) == 4 for r in recs)


def test_table_records_carry_distinct_provenance():
    recs = table_records(_compiled_offer_graph())
    regions = [c.region for r in recs for c in r.concepts]
    assert all(regions) and len(set(regions)) == len(regions)   # non-empty and distinct per cell
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -k "table_records" -v`
Expected: FAIL — `ModuleNotFoundError: iladub.feed` (and `offer_table_pdf` missing).

- [ ] **Step 3: Write minimal implementation**

Create `src/iladub/feed.py`:

```python
"""feed — the ET(K)L → grounding bridge (closes raw-doc→grounded-graph).

PROCEDURAL raw extraction: reads asserted tab:RecordTable cells out of a compiled
CompilationReport.graph into per-cell SurfaceConcepts (row = record), then grounds them via the
shipped ground_concept oracle (unchanged — no new grounding decision here). RDF reads only; no
tuned constant, no IRI-name parsing. This is the RawDocument→grounding-portal traversal.
"""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from .ground import SurfaceConcept

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


@dataclass(frozen=True)
class Record:
    row_id: str
    concepts: tuple[SurfaceConcept, ...]


def table_records(graph: Graph) -> list[Record]:
    """Each asserted tab:RecordTable -> one Record per data row; each data cell -> a SurfaceConcept
    (text=its column header, value=cell text, region=cell provenance). RDF reads only."""
    out: list[Record] = []
    for t in graph.subjects(RDF.type, TAB.RecordTable):
        header: dict = {}
        for h in graph.objects(t, TAB.hasHeaderNode):
            lc = graph.value(h, TAB.hasLabel)
            label = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
            for col in graph.objects(h, TAB.coversColumn):
                header[col] = label
        rows: dict = {}
        for e in graph.subjects(RDF.type, TAB.EntryCell):
            if (t, TAB.hasCell, e) not in graph:
                continue
            col = graph.value(e, TAB.atColumn)
            row = graph.value(e, TAB.atRow)
            prov = graph.value(e, PROV.wasDerivedFrom)
            region = str(prov).split("#")[-1] if prov is not None else str(e).split("#")[-1]
            concept = SurfaceConcept(header.get(col, ""), str(graph.value(e, TAB.cellText)), region)
            rows.setdefault(row, []).append((col, concept))
        for row in sorted(rows, key=lambda r: str(r)):
            cells = [c for _, c in sorted(rows[row], key=lambda kc: str(kc[0]))]
            out.append(Record(str(row).split("#")[-1], tuple(cells)))
    return out
```

Add to `tests/etkl/fixtures.py` (uses the existing `canvas`, `letter`, `PAGE_H`):

```python
def offer_table_pdf(path):
    """A 4-column organ-offer record table (Organ/LVEF/ABO/COD) with two donor rows. Row 2 uses
    'Liver' (in scheme-organ); single-token cells, wide gaps -> compiles RECORD_TABLE. For the
    concept-feed end-to-end (raw-doc→grounded-graph)."""
    cols = [72.0, 200.0, 320.0, 440.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Organ", "LVEF", "ABO", "COD"),
            ("Heart", "60", "O", "MVA"),
            ("Liver", "55", "A", "CVA")]
    y0 = PAGE_H - 100.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -k "table_records or provenance" -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/feed.py tests/etkl/fixtures.py tests/test_concept_feed.py
git commit -m "feat(iladub): feed.table_records bridge (tab:RecordTable -> SurfaceConcepts, row=record) + offer-table fixture"
```

---

### Task 3: `ground_document` driver + end-to-end DoD

**Files:**
- Modify: `src/iladub/feed.py` (add `FeedResult`, `ground_document`)
- Test: `tests/test_concept_feed.py`

**Interfaces:**
- Consumes: `table_records` (Task 2); `iladub.ground.ground_concept`; `MappingGroundingProposer` (Task 1).
- Produces:
  - `@dataclass(frozen=True) FeedResult(records: int, grounded: int, proposed: int)`.
  - `ground_document(graph, contract, proposer, terms, shapes, g) -> FeedResult` — mints one subject per row and grounds each concept; populates `g`.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_concept_feed.py
from rdflib import Graph, Namespace, URIRef
from iladub.feed import ground_document, FeedResult, table_records
from iladub.ground import load_contract

TX = Namespace("https://example.org/transplant#")
ILA = Namespace("https://w3id.org/iladub#")
CONTRACT = "examples/transplant/offer-contract.ttl"


def _offer_deps():
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    cod = next(f for f in c.fields if f.fills_property.endswith("causeOfDeath"))
    mapping = {
        "ABO": GroundingProposal(abo.iri, str(TX) + "Category", 0.8, "abo", "urn:iladub:suggester/fake"),
        "LVEF": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9, "ef", "urn:iladub:suggester/fake"),
        "COD": GroundingProposal(cod.iri, str(TX) + "Category", 0.7, "cod", "urn:iladub:suggester/fake"),
    }
    return c, terms, shapes, MappingGroundingProposer(mapping)


def test_offer_table_grounds_end_to_end():
    graph = _compiled_offer_graph()
    c, terms, shapes, proposer = _offer_deps()
    g = Graph()
    res = ground_document(graph, c, proposer, terms, shapes, g)
    assert res == FeedResult(records=2, grounded=6, proposed=2)
    assert len(set(g.subjects(RDF.type, TX.OrganOffer))) == 2        # two record subjects
    assert len(list(g.subjects(RDF.type, ILA.GroundedNode))) == 6    # organ/abo/ef x 2 rows
    assert list(g.objects(None, TX.causeOfDeath)) == []              # COD quarantined, no property


def test_feed_is_load_bearing_red_check(monkeypatch):
    graph = _compiled_offer_graph()
    c, terms, shapes, proposer = _offer_deps()
    monkeypatch.setattr("iladub.feed.table_records", lambda _g: [])
    g = Graph()
    res = ground_document(graph, c, proposer, terms, shapes, g)
    assert res == FeedResult(0, 0, 0)
    assert list(g.subjects(RDF.type, ILA.GroundedNode)) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -k "end_to_end or red_check" -v`
Expected: FAIL — `ImportError: cannot import name 'ground_document'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/feed.py`:

```python
@dataclass(frozen=True)
class FeedResult:
    records: int
    grounded: int
    proposed: int


def ground_document(graph, contract, proposer, terms, shapes, g) -> FeedResult:
    """Ground a compiled document's record tables against a contract: one subject per row, each
    cell grounded via the shipped ground_concept oracle (unchanged). Populates `g` with grounded
    nodes + promotion decisions + propositions; returns the grounded/proposed tally."""
    from .ground import ground_concept

    records = table_records(graph)
    grounded = proposed = 0
    for rec in records:
        subject = URIRef("urn:iladub:record:" + rec.row_id)
        for concept in rec.concepts:
            status = ground_concept(concept, contract, subject, proposer, terms, shapes, g)
            if status == "grounded":
                grounded += 1
            else:
                proposed += 1
    return FeedResult(len(records), grounded, proposed)
```

Note: `test_feed_is_load_bearing_red_check` monkeypatches `iladub.feed.table_records`; `ground_document` must call the module-level `table_records` (a bare name lookup, as written) so the patch takes effect — do NOT bind it to a local alias.

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Run the full suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/ -q`
Expected: all pass (the slice is additive — new module + fixture + proposer sibling; `ground_concept` and the etkl compiler unchanged).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/feed.py tests/test_concept_feed.py
git commit -m "feat(iladub): ground_document driver — compile→feed→ground end-to-end (raw-doc→grounded-graph DoD)"
```

---

## Self-Review

**Spec coverage:**
- Bridge `feed.table_records` (tab:RecordTable → per-cell SurfaceConcepts, row=record) → Task 2. ✓
- `MappingGroundingProposer` (offline per-header) → Task 1. ✓
- `ground_document` driver (subject per row, reuse ground_concept) + `FeedResult` → Task 3. ✓
- `offer_table_pdf` fixture (Heart/Liver, RECORD_TABLE) → Task 2. ✓
- Provenance carried (§6) → Task 2 (region test). ✓
- End-to-end DoD, all three oracle paths + quarantine (COD), RED-checked → Task 3. ✓
- §8 PROCEDURAL bridge (RDF reads, no tuned constant/IRI-parsing); ground_concept unchanged → feed.py docstring + Global Constraints. ✓
- §7 residue quarantined (COD) → Task 3 assertion (`causeOfDeath == []`). ✓

**Placeholder scan:** none — every step has full code + exact commands, all empirically validated end-to-end before writing.

**Type consistency:** `Record(row_id, concepts)`, `table_records(graph)->list[Record]`, `FeedResult(records, grounded, proposed)`, `ground_document(graph, contract, proposer, terms, shapes, g)->FeedResult`, `MappingGroundingProposer(mapping).propose_grounding(concept, fields)->GroundingProposal`, `SurfaceConcept(text, value, region)`, `GroundingProposal(field_iri, anchor_iri, confidence, rationale, suggester_iri)`, `ground_concept(concept, contract, offer_uri, proposer, terms, shapes, g)` are used identically across tasks and match the shipped signatures. ✓
