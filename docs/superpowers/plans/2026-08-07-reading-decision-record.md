# Reading Decision Record Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every judgement on the band-to-verdict path emits a `dec:DecisionHolon` into the document graph, so "why was this region escalated?" becomes a SPARQL query instead of a lost reason string — with no verdict changed.

**Doc impact:** none for this plan file — the loop's `Doc impact: increment` is declared in the design spec (`2026-08-07-reading-decision-record-design.md`).

**Architecture:** A new module `src/iladub/etkl/decisionlog.py` provides a recorder that mints `dec:DecisionHolon` nodes with `dec:optionSpace` / `dec:chosen` / `dec:rejectedBecause` / `dec:consideredEvidence` / `dec:order` / `dec:partOf`. It is threaded through `compile_tables`' band loop — the one place every judgement is *called* — so no judgement function is touched. Three committed SPARQL queries answer the spec's §4 questions, and the tests run those queries rather than counting triples.

**Tech Stack:** Python 3.11+/pytest, rdflib, the owned `dec:` vocabulary (no new terms).

**Spec:** `docs/superpowers/specs/2026-08-07-reading-decision-record-design.md` — read it first, especially §3.1 (the membrane hazard) and §4 (what the record must answer).

## Global Constraints

- **No verdict may change.** This slice records; it does not decide. Corpus scores must be byte-identical: stem **0.9655** / 2152 cells / chain [3], CBH **0.9047**, capacity **1.0000**, apple **0.0606860158**, WHO **0.5597**.
- **No new vocabulary.** `dec:` already carries every term needed (`DecisionHolon`, `Option`, `optionSpace`, `chosen`, `rejectedBecause`, `consideredEvidence`, `rationale`, `regarding`, `order`, `partOf`). Do not add terms to `dec.ttl` or any other ontology.
- **THE MEMBRANE HAZARD (spec §3.1):** decisions are emitted into the **document graph ONLY, never into a region's `scratch` graph before `region_tiles`**. A gate validating a graph containing decision holons is the R19 hazard again. Every `scratch = Graph()` in `compile_tables` stays decision-free.
- **No judgement function is modified.** `regions.classify`, `orientation.looks_transposed`, `orientation.transpose_is_coherent`, `rowheaders.looks_row_grouped`, `matrix.is_matrix_candidate`, `hierarchical.classify_hierarchical`, `tiling.region_tiles` are all untouched. The recorder observes results at the call site.
- **Gate:** the recorder is PROCEDURAL engine glue — it makes no domain decision, it records ones already made. No tuned constant.
- **Broken system git on this machine:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …`.
- **Run suites in the FOREGROUND** with generous timeouts; never background them and wait for a notification. Corpus runs and the full suite are the CONTROLLER's job.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-decision-record` — already created off `main`; the design spec is already committed there.

---

### Task 1: The recorder

**Files:**
- Create: `src/iladub/etkl/decisionlog.py`
- Create: `tests/etkl/test_decisionlog.py`

**Interfaces:**
- Consumes: `rdflib`, the `DEC` namespace (`https://w3id.org/iladub/dec#` — confirm against `src/iladub/etkl/holon.py`'s existing `DEC` binding and reuse it rather than re-declaring).
- Produces (Task 2 depends on these exact names): `decisionlog.ReadingRecorder(graph, doc_uri, page)` with `.band(idx) -> BandRecorder`; `BandRecorder.record(judgement, options, chosen, rationale, rejected=None, evidence=None) -> URIRef`.

- [ ] **Step 1: Write the failing test** — create `tests/etkl/test_decisionlog.py`:

```python
"""The reading decision record (spec 2026-08-07-reading-decision-record-design.md).

Every judgement on the band-to-verdict path becomes a dec:DecisionHolon, so the reading is
queryable rather than lost. Uses only the owned dec: vocabulary — the differential half
(optionSpace/chosen/rejectedBecause) which had no producer before this loop."""
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

DEC = Namespace("https://w3id.org/iladub/dec#")
DOC = URIRef("urn:test:doc")


def _rec(g):
    from iladub.etkl.decisionlog import ReadingRecorder
    return ReadingRecorder(g, DOC, 0)


def test_a_decision_records_its_option_space_and_choice():
    g = Graph()
    b = _rec(g).band(3)
    d = b.record("kind", options=["RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"],
                 chosen="UNSUPPORTED_TABLE",
                 rationale="header has 1 words but 5 columns")
    assert (d, RDF.type, DEC.DecisionHolon) in g
    opts = list(g.objects(d, DEC.optionSpace))
    assert len(opts) == 3, "every candidate considered must be recorded, not just the winner"
    labels = {str(l) for o in opts for l in g.objects(o, RDFS.label)}
    assert labels == {"RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"}
    chosen = list(g.objects(d, DEC.chosen))
    assert len(chosen) == 1
    assert str(next(g.objects(chosen[0], RDFS.label))) == "UNSUPPORTED_TABLE"
    assert str(next(g.objects(d, DEC.rationale))) == "header has 1 words but 5 columns"


def test_rejected_options_carry_their_refutation():
    """The differential's point: a discarded candidate names the observation that killed it."""
    g = Graph()
    b = _rec(g).band(3)
    d = b.record("kind", options=["RECORD_TABLE", "UNSUPPORTED_TABLE"],
                 chosen="UNSUPPORTED_TABLE",
                 rationale="header has 1 words but 5 columns",
                 rejected={"RECORD_TABLE": "header has 1 words but 5 columns"})
    rej = [o for o in g.objects(d, DEC.optionSpace)
           if (o, DEC.rejectedBecause, None) in g]
    assert len(rej) == 1
    assert str(next(g.objects(rej[0], RDFS.label))) == "RECORD_TABLE"
    assert "1 words" in str(next(g.objects(rej[0], DEC.rejectedBecause)))
    # the chosen option is never also rejected
    chosen = next(g.objects(d, DEC.chosen))
    assert (chosen, DEC.rejectedBecause, None) not in g


def test_order_increments_within_a_band_and_restarts_per_band():
    """dec:order is what makes 'which gate fired first' answerable — the R55 question."""
    g = Graph()
    r = _rec(g)
    b3 = r.band(3)
    d1 = b3.record("kind", ["A"], "A", "first")
    d2 = b3.record("transposed", ["A"], "A", "second")
    b5 = r.band(5)
    d3 = b5.record("kind", ["A"], "A", "other band")
    assert int(next(g.objects(d1, DEC.order))) == 0
    assert int(next(g.objects(d2, DEC.order))) == 1
    assert int(next(g.objects(d3, DEC.order))) == 0, "order is per band, not global"


def test_decisions_nest_band_under_page():
    """dec:partOf gives the document -> page -> band -> judgement hierarchy with no new terms."""
    g = Graph()
    r = _rec(g)
    d = r.band(3).record("kind", ["A"], "A", "why")
    band_node = next(g.objects(d, DEC.partOf))
    page_node = next(g.objects(band_node, DEC.partOf))
    assert (page_node, DEC.partOf, DOC) in g


def test_evidence_is_linked_when_supplied():
    g = Graph()
    ev = URIRef("urn:test:evidence")
    d = _rec(g).band(1).record("kind", ["A"], "A", "why", evidence=[ev])
    assert (d, DEC.consideredEvidence, ev) in g


def test_regarding_points_at_the_band_region():
    g = Graph()
    d = _rec(g).band(4).record("kind", ["A"], "A", "why")
    reg = next(g.objects(d, DEC.regarding))
    assert "region4" in str(reg), f"regarding should name the band's region, got {reg}"


def test_recorder_writes_only_to_the_graph_it_was_given():
    """The membrane hazard (spec §3.1): decisions must never leak into a region scratch graph."""
    g, other = Graph(), Graph()
    _rec(g).band(0).record("kind", ["A"], "A", "why")
    assert len(other) == 0
    assert len(g) > 0
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_decisionlog.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.etkl.decisionlog'`.

- [ ] **Step 3: Implement** — create `src/iladub/etkl/decisionlog.py`:

```python
"""decisionlog — the reading, recorded as evidence (spec 2026-08-07).

iladub records the LAST step of its reasoning (iladub:PromotionDecision) and discards the
rest: the reading that precedes it returns a kind and a reason string, the alternatives are
never named, and the moment a branch is taken the others cease to exist. This module gives
that reading a record, using only the OWNED dec: vocabulary — whose differential half
(dec:optionSpace / dec:chosen / dec:rejectedBecause) had no producer before this loop.

Gate classification (CLAUDE.md §8): PROCEDURAL engine glue. It makes no domain decision — it
records ones already made at the call site, and no judgement function is modified.

MEMBRANE HAZARD (spec §3.1): a recorder must be given the DOCUMENT graph, never a region's
scratch graph. Decisions in a graph that region_tiles validates is the R19 hazard again — a
shape firing on something that is not what it thinks it is.
"""
from __future__ import annotations

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

DEC = Namespace("https://w3id.org/iladub/dec#")


class BandRecorder:
    """Records the judgement sequence for one band. `dec:order` counts within the band."""

    def __init__(self, graph: Graph, band_node: URIRef, region_uri: URIRef, prefix: str):
        self._g = graph
        self._band = band_node
        self._regarding = region_uri
        self._prefix = prefix
        self._n = 0

    def record(self, judgement: str, options, chosen, rationale: str,
               rejected: dict | None = None, evidence=None) -> URIRef:
        """One judgement. `options` are candidate names; `chosen` is one of them (or None
        when the judgement admitted nothing); `rejected` maps a candidate name to the
        observation that refuted it."""
        g = self._g
        d = URIRef(f"{self._prefix}-d{self._n}")
        g.add((d, RDF.type, DEC.DecisionHolon))
        g.add((d, RDFS.label, Literal(judgement)))
        g.add((d, DEC.regarding, self._regarding))
        g.add((d, DEC.partOf, self._band))
        g.add((d, DEC.order, Literal(self._n, datatype=XSD.integer)))
        g.add((d, DEC.rationale, Literal(rationale)))
        rejected = rejected or {}
        for name in options:
            o = URIRef(f"{d}-opt-{_slug(name)}")
            g.add((o, RDF.type, DEC.Option))
            g.add((o, RDFS.label, Literal(str(name))))
            g.add((d, DEC.optionSpace, o))
            if str(name) == str(chosen):
                g.add((d, DEC.chosen, o))
            elif str(name) in rejected:
                g.add((o, DEC.rejectedBecause, Literal(rejected[str(name)])))
        for e in (evidence or ()):
            g.add((d, DEC.consideredEvidence, e))
        self._n += 1
        return d


class ReadingRecorder:
    """One per page compile. Mints the page decision under the document, and a band decision
    under the page, so dec:partOf carries document -> page -> band -> judgement."""

    def __init__(self, graph: Graph, doc_uri: URIRef, page: int):
        self._g = graph
        self._doc = doc_uri
        self._page = page
        self._page_node = URIRef(f"{doc_uri}#p{page}-reading")
        graph.add((self._page_node, RDF.type, DEC.DecisionHolon))
        graph.add((self._page_node, RDFS.label, Literal(f"reading page {page}")))
        graph.add((self._page_node, DEC.partOf, doc_uri))
        graph.add((self._page_node, DEC.regarding, doc_uri))

    def band(self, idx: int) -> BandRecorder:
        prefix = f"{self._doc}#region{idx}"
        band_node = URIRef(f"{prefix}-reading")
        self._g.add((band_node, RDF.type, DEC.DecisionHolon))
        self._g.add((band_node, RDFS.label, Literal(f"reading band {idx}")))
        self._g.add((band_node, DEC.partOf, self._page_node))
        self._g.add((band_node, DEC.regarding, URIRef(prefix)))
        return BandRecorder(self._g, band_node, URIRef(prefix), prefix)


def _slug(name) -> str:
    return "".join(c if c.isalnum() else "_" for c in str(name))
```

**Verify before running:** check `src/iladub/etkl/holon.py`'s existing `DEC` namespace binding and use the identical IRI string; if it differs from the one above, use holon.py's (it is the shipped one) and say so in your report.

- [ ] **Step 4: Run — verify green**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_decisionlog.py -q`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/decisionlog.py tests/etkl/test_decisionlog.py && git commit -m "feat(loop-decision-record): the recorder — dec:'s differential half gets its first producer

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Thread it through the band loop

**Files:**
- Modify: `src/iladub/etkl/compile.py` (`compile_tables`' band loop only)
- Modify: `tests/etkl/test_decisionlog.py` (append integration tests)

**Interfaces:**
- Consumes: Task 1's `ReadingRecorder` / `BandRecorder.record`.
- Produces: every band of every compiled page carries a decision chain in the document graph. Task 3 queries it.

- [ ] **Step 1: Write the failing integration tests** — append to `tests/etkl/test_decisionlog.py`:

```python
# ---------------------------------------------------------------- integration

import os
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")
needs_apple = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus doc not fetched")


@needs_apple
def test_every_band_carries_a_chain():
    """No region may end without a record of how it got there (spec §6)."""
    from iladub.etkl import compile_tables
    rep = compile_tables(APPLE, page_number=0)
    g = rep.graph
    bands = [b for b in g.subjects(RDF.type, DEC.DecisionHolon)
             if "reading band" in {str(l) for l in g.objects(b, RDFS.label)}
             or str(b).endswith("-reading")]
    assert bands, "no band decisions recorded at all"
    for b in bands:
        if str(b).endswith("-reading") and "region" in str(b):
            judgements = list(g.subjects(DEC.partOf, b))
            assert judgements, f"band {b} has no judgement decisions"


@needs_apple
def test_the_kind_rejection_is_recorded_for_band_3():
    """Spec §5's honest limit, made concrete: band 3 rejected RECORD_TABLE because the
    caption line was read as a header row — and nothing else was ever a candidate."""
    from iladub.etkl import compile_tables
    g = compile_tables(APPLE, page_number=0).graph
    rejections = [str(o) for _, _, o in g.triples((None, DEC.rejectedBecause, None))]
    assert any("1 words" in r for r in rejections), \
        f"band 3's kind rejection is not in the record; got {rejections[:5]}"


@needs_apple
def test_band_4_records_transposed_before_coherence():
    """THE R55 QUESTION. The register claimed coherence failed 'solely' because of
    parenthesized negatives; the truth is looks_transposed fired FIRST and the coherence
    oracle was only then consulted. dec:order must make that readable."""
    from iladub.etkl import compile_tables
    g = compile_tables(APPLE, page_number=0).graph
    orders = {}
    for d in g.subjects(RDF.type, DEC.DecisionHolon):
        if "region4-d" not in str(d):
            continue
        label = str(next(g.objects(d, RDFS.label)))
        orders[label] = int(next(g.objects(d, DEC.order)))
    assert "transposed" in orders, f"no transposed judgement recorded; got {sorted(orders)}"
    if "transpose_coherent" in orders:
        assert orders["transposed"] < orders["transpose_coherent"]


@needs_apple
def test_recording_does_not_change_the_verdicts():
    """This slice records; it does not decide."""
    from iladub.etkl import compile_tables
    rep = compile_tables(APPLE, page_number=0)
    verdicts = [(r.kind.name, r.verdict, r.reason, r.cells) for r in rep.regions]
    assert abs(rep.score - 0.1170) < 0.0001, f"score moved: {rep.score}"
    assert sum(1 for v in verdicts if v[1] == "asserted") == 1
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_decisionlog.py -k "chain or band_3 or band_4" -v`
Expected: FAIL — no decisions in the compiled graph yet.

- [ ] **Step 3: Wire the recorder into `compile_tables`.** In `src/iladub/etkl/compile.py`:

Immediately after `graph = Graph()` in `compile_tables`, add:

```python
    from .decisionlog import ReadingRecorder
    recorder = ReadingRecorder(graph, doc, page_number)
```

Then inside `for idx, band in enumerate(bands):`, immediately after `band_marks.append(...)`, add `brec = recorder.band(idx)`, and record each judgement **at its existing call site**, passing the value the code already computed. Record these, in the order the code evaluates them:

| judgement label | options | chosen | rationale |
| --- | --- | --- | --- |
| `multi_table` | `["single", "multi"]` | `"multi"` if `is_multi_table_ambiguous(band)` else `"single"` | `"MULTI_TABLE_AMBIGUOUS"` or `"single table"` |
| `kind` | `["RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"]` | `region.kind.name` | `region.reason or ""` |
| `transposed` | `["upright", "transposed"]` | per `looks_transposed(region)` | `"looks transposed"` / `"upright"` |
| `transpose_coherent` | `["coherent", "incoherent"]` | per `transpose_is_coherent(region)` | the same string |
| `row_grouped` | `["flat", "row_grouped"]` | per `looks_row_grouped(region)` | the same string |
| `matrix_candidate` | `["matrix", "not_matrix"]` | per `is_matrix_candidate(band)` | the same string |
| `hierarchical` | `["hierarchical", "not_hierarchical"]` | `"hierarchical"` if `hreg is not None` else the other | the same string |
| `region_tiles` | `["tiles", "does_not_tile"]` | per the gate's boolean | the same string |
| `verdict` | `["asserted", "escalated", "ignored"]` | the branch taken | the reason string passed to `escalate_region`, or `""` |

For `kind`, pass `rejected={name: region.reason for name in options if name != region.kind.name and region.reason}` so the rejection carries its refutation — this is what `test_the_kind_rejection_is_recorded_for_band_3` reads.

**Record only judgements the code actually evaluates on that band's path** — do not synthesise a judgement that was never made. A band that returns early (NON_TABLE) records `kind` and `verdict` and nothing else; that is the honest chain.

**HAZARD, restated:** every `record(...)` call passes through `recorder`/`brec`, which holds the **document** `graph`. Never pass a `scratch` graph. After wiring, grep the diff for `scratch` near any `record(` call — there must be none.

- [ ] **Step 4: Run — verify green plus the near suite**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_decisionlog.py tests/etkl/test_physical_gate.py tests/etkl/test_unit_marker.py tests/etkl/test_typing_equiv.py -q`
Expected: all PASS. If a verdict moved, the wiring changed behaviour — find and fix that; do not adjust the expectation.

- [ ] **Step 5: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/compile.py tests/etkl/test_decisionlog.py && git commit -m "feat(loop-decision-record): every band-to-verdict judgement recorded in the document graph

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: The three questions, answerable by SPARQL

**Files:**
- Create: `vocab/queries/why-escalated.rq`, `vocab/queries/what-was-considered.rq`, `vocab/queries/judgement-order.rq`
- Create: `tests/etkl/test_decision_queries.py`

**Interfaces:**
- Consumes: Task 2's recorded chains.
- Produces: the committed queries that make the record an audit surface rather than triples.

The point of this task: **the record's value is that a question can be answered from it by query alone.** Tests must run the queries, not re-implement them in Python.

- [ ] **Step 1: Write the queries.** `vocab/queries/why-escalated.rq` — given a region, its judgement chain in order with each rationale:

```sparql
# why-escalated.rq — the chain of judgements for one region, in the order they were made,
# each with its rationale and (where the candidate was refuted) the observation that killed
# it. Answers spec 2026-08-07 §4 question 1: "why was this region escalated?"
PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?order ?judgement ?chosen ?rationale WHERE {
  ?d a dec:DecisionHolon ; dec:regarding ?region ; dec:order ?order ;
     rdfs:label ?judgement ; dec:rationale ?rationale .
  OPTIONAL { ?d dec:chosen/rdfs:label ?chosen }
}
ORDER BY ?order
```

`vocab/queries/what-was-considered.rq` — the candidates for one region, and which were refuted:

```sparql
# what-was-considered.rq — every candidate the reader had for a region, with the refuting
# observation where one exists. Answers spec 2026-08-07 §4 question 2. A thin optionSpace is
# itself the finding (§5): it shows the reader had no differential to reason over.
PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?judgement ?option ?refutedBy WHERE {
  ?d a dec:DecisionHolon ; dec:regarding ?region ; rdfs:label ?judgement ;
     dec:optionSpace ?o .
  ?o rdfs:label ?option .
  OPTIONAL { ?o dec:rejectedBecause ?refutedBy }
}
```

`vocab/queries/judgement-order.rq` — which judgement fired first (the R55 question):

```sparql
# judgement-order.rq — the judgements for a region ordered by when they were made. This is
# the query that would have prevented R55's misattribution: it shows which gate fired FIRST,
# so a later gate's failure cannot be mistaken for the cause.
PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?judgement ?order WHERE {
  ?d a dec:DecisionHolon ; dec:regarding ?region ; dec:order ?order ; rdfs:label ?judgement .
}
ORDER BY ?order
```

- [ ] **Step 2: Write the tests** — create `tests/etkl/test_decision_queries.py`:

```python
"""The record is an audit surface only if a question can be answered from it BY QUERY.
These tests run the committed .rq files against a real compiled graph (spec §4/§6)."""
import os
import pytest
from rdflib import Namespace, URIRef

DEC = Namespace("https://w3id.org/iladub/dec#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")
pytestmark = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus doc not fetched")


def _graph():
    from iladub.etkl import compile_tables
    return compile_tables(APPLE, page_number=0).graph


def _run(name, g, region):
    q = open(os.path.join(QDIR, name), encoding="utf-8").read()
    return [tuple(r) for r in g.query(q, initBindings={"region": region})]


def _region(g, idx):
    from iladub.etkl.compile import _DOC
    return URIRef(f"{_DOC}#region{idx}")


def test_why_escalated_returns_an_ordered_chain():
    g = _graph()
    rows = _run("why-escalated.rq", g, _region(g, 3))
    assert rows, "no chain for band 3"
    orders = [int(r[0]) for r in rows]
    assert orders == sorted(orders), "chain is not ordered"
    assert any("1 words" in str(r[3]) for r in rows), \
        f"band 3's kind rationale missing from the chain: {rows}"


def test_what_was_considered_shows_the_thin_option_space():
    """Spec §5: the record must show, truthfully, that the reader had almost no differential.
    This test asserts the record is HONEST about that, not that the space is large."""
    g = _graph()
    rows = _run("what-was-considered.rq", g, _region(g, 3))
    kinds = {str(o) for j, o, _ in rows if str(j) == "kind"}
    assert kinds == {"RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"}, kinds
    refuted = [(o, r) for j, o, r in rows if r is not None]
    assert refuted, "no candidate carries its refutation"


def test_judgement_order_answers_the_r55_question():
    """Band 4: looks_transposed fired BEFORE the coherence oracle was consulted."""
    g = _graph()
    rows = _run("judgement-order.rq", g, _region(g, 4))
    order = {str(j): int(o) for j, o in rows}
    assert "transposed" in order, f"got {sorted(order)}"
    if "transpose_coherent" in order:
        assert order["transposed"] < order["transpose_coherent"]
```

- [ ] **Step 3: Run**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_decision_queries.py -v`
Expected: all PASS. If `_DOC` is not importable from `compile`, find the document URI the compile actually mints (print `list(g.subjects())[:3]`) and bind accordingly — report what you used.

- [ ] **Step 4: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/queries tests/etkl/test_decision_queries.py && git commit -m "feat(loop-decision-record): three committed queries make the record an audit surface

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Measure and close

**Files:**
- Modify: `docs/superpowers/specs/2026-08-07-reading-decision-record-design.md` (status + measured numbers)
- Modify: `docs/superpowers/residues.md` (register what this slice leaves)

**Note for the controller:** Steps 1–4 are measurements — the controller runs them; the implementer does Steps 5–6 with the numbers handed to it.

- [ ] **Step 1: The record on apple, printed as evidence**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
from iladub.etkl import compile_tables
from iladub.etkl.compile import _DOC
from rdflib import URIRef
import os
q = open("vocab/queries/why-escalated.rq", encoding="utf-8").read()
g = compile_tables("corpus/financial/apple-fy2026q3-statements.pdf", page_number=0).graph
for idx in (3, 4):
    print(f"\n--- region{idx} ---")
    for r in g.query(q, initBindings={"region": URIRef(f"{_DOC}#region{idx}")}):
        print(f"  {int(r[0])}. {r[1]:<20} chosen={r[2]}  — {r[3]}")
EOF
```
Record the output verbatim: it is the artifact this loop exists to produce.

- [ ] **Step 2: Byte-identity gate**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: 13 passed (stem 0.9655 / 2152 / chain [3], CBH 0.9047). Then:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -c "
from iladub.etkl.document import compile_document
for n,p,b in (('apple','corpus/financial/apple-fy2026q3-statements.pdf','0.0606860158'),
              ('capacity','corpus/ag-trade/graincorp-capacity-2026-08-04.pdf','1.0000'),
              ('who','corpus/health/who-wfa-boys-zscore-0-5.pdf','0.5597')):
    print(f'{n}: {compile_document(p).score:.10f}  [{b}]')"
```
Any movement is a regression — this slice records, it does not decide. STOP and report.

- [ ] **Step 3: The cost this slice adds**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl.document import compile_document
t0 = time.monotonic()
rep = compile_document("corpus/ag-trade/graincorp-stem-2026-07-31.pdf")
dt = time.monotonic() - t0
from rdflib import Namespace
from rdflib.namespace import RDF
DEC = Namespace("https://w3id.org/iladub/dec#")
merged = sum(len(p.graph) for p in rep.pages)
decisions = sum(len(list(p.graph.subjects(RDF.type, DEC.DecisionHolon))) for p in rep.pages)
print(f"stem: {dt:.0f}s  triples={merged}  decision holons={decisions}   [pre-loop ~151s / 29,377]")
EOF
```
Record both numbers; spec §6 requires the cost be measured, not assumed.

- [ ] **Step 4: Whole-graph SHACL + full suite**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -6
```
Expected: 0 failed except the known machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag`. The whole-graph SHACL runs inside the corpus tests — a conformance failure means decision holons tripped a shape, which is the §3.1 hazard and must be reported, not worked around.

- [ ] **Step 5: Spec status + register**

Set the spec's `**Status:**` to `closed 2026-08-07` with the measured numbers and the apple chain from Step 1. Then in `docs/superpowers/residues.md`, house format:

- **A residue for the thin option space** — the record now shows, on real documents, that the reader's entire candidate set for kind is three enum values, and that everything downstream is a Python branch rather than a candidate. Cite spec §5 and §7's slice B as what would close it. This row is the loop's own evidence for the next slice.
- **A residue for coverage** — judgements *inside* called functions (e.g. `classify`'s internal `classify-kind.rq` run, the header/body split's own AXIOM) are recorded only by their result, not their internal steps. Name what that means: the chain is complete at the compile-path granularity, not at the query granularity.

- [ ] **Step 6: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/specs/2026-08-07-reading-decision-record-design.md docs/superpowers/residues.md && git commit -m "docs(loop-decision-record): close — the reading is queryable; the thin option space is now measured evidence

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-07)

- **Spec coverage:** §1 problem → the whole loop; §2 unused vocabulary → Task 1 (first producer of `optionSpace`/`chosen`/`rejectedBecause`); §3 the eight properties → Task 1 Step 3 + Task 2's judgement table; §3.1 membrane hazard → Global Constraints + Task 2 Step 3's grep instruction + `test_recorder_writes_only_to_the_graph_it_was_given`; §4's three questions → Task 3's three queries and their tests; §5 honest limit → `test_what_was_considered_shows_the_thin_option_space` and Task 4's residue; §6 criteria → Task 4 Steps 1–4.
- **Placeholder scan:** none. The two "verify rather than assume" notes (the `DEC` IRI in Task 1, the document URI in Task 3) state the invariant and the fallback.
- **Type consistency:** `ReadingRecorder(graph, doc_uri, page)` → `.band(idx)` → `BandRecorder.record(judgement, options, chosen, rationale, rejected=None, evidence=None)` used identically in Tasks 1–2; the three query filenames match between Task 3's creation and its tests.
- **One risk I checked rather than assumed:** all nine `escalate_region` call sites already write into `graph` (the document graph), not a scratch graph — so recording alongside them cannot leak into a region scratch that `region_tiles` validates. That is what makes §3.1's hazard avoidable by construction rather than by discipline.
