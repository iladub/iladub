# Loop A2.1 — GenAI-Proposed Pivot Dimension Names — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When Loop A1 escalates a nameless-but-structurally-sound column pivot (e.g. `Q1 Q2 Q3 Q4` with no header), have GenAI (boxed by BAML) propose the missing dimension name, certify the reshape deterministically via A1's round-trip oracle, and admit the name as an accountable `iladub:PromotionDecision` — never as a fact.

**Architecture:** A2 is an *augmenting pass* (`certify_with_proposals`) layered over A1. It does its own **value-set-based** recovery for the nameless case (measure column = leaf label ∈ the pivot's value set — validated by probe), injects the proposed name into the *recipe and derived base only* (never the source graph, for provenance), reuses A1's `grid_values` + `round_trip` oracle unchanged, and — on round-trip success — emits the derived base plus the name's `CandidateConcept`/`PromotionDecision` provenance. The model is reached only through an injected `Proposer` protocol (`FakeProposer` offline, gated `BamlProposer` live).

**Tech Stack:** Python 3, rdflib, pytest. BAML (`baml_src/` + generated `baml_client`, pinned to baml-py **0.222.0**). No network in the default test suite.

## Global Constraints

- **A1's deterministic behaviour is unchanged.** `recover_recipe`/`recover_base`/`certify` keep byte-for-byte behaviour; A2 does NOT route the nameless case through them (it does value-set recovery). The one A1 edit permitted is a **behaviour-preserving extraction** of the base-fact-writing loop from `emit_normalized_base` into a shared `emit_base_projection(g, t, recipe, base)` that both A1 and A2 call — proven identical by the A1 suite staying green. (This supersedes the spec's literal "A1 functions unchanged" with "A1 behaviour unchanged", for DRY; flagged in handoff.)
- **Provenance: the proposed name never enters the source graph.** No `LabelCell`/header label is fabricated. The name lives only in the recipe (`UnpivotOp.dimension`), the derived `tab:BaseFact` coordinates, and its `iladub:CandidateConcept`. The source had no label there; inventing one would violate provenance-to-the-page.
- **The name is a PROPOSITION, never oracle-verified.** The oracle gates the *reshape structure*; the name rides as `iladub:CandidateConcept` admitted by `iladub:PromotionDecision`. `dec:rationale` states the split explicitly.
- **Assert-first.** The proposer is consulted ONLY for a `name=None` structural column pivot. A fully-named pivot must NOT invoke the proposer (tested with a spy that raises if called).
- **Offline-first.** All logic is tested with `FakeProposer` — no API key, no network. The live model call sits behind `BAML_LIVE=1` + importable `baml_client`, skipped in normal CI.
- **`baml_client` stays pinned to baml-py 0.222.0** (`baml_src/generators.baml` `version "0.222.0"`); a mismatch hard-errors on import.
- **Source ownership.** `tab.ttl` stays standalone (no `iladub:`/`holon:` references): the new `tab:namePromotedBy` is declared **rangeless**; it points at an `iladub:PromotionDecision` only at runtime in Python.
- **Showcase** leads with the rendered original PDF and re-runs to 0 errors offline (uses a recorded/deterministic proposer).

---

### Task 1: The proposer seam (`propose.py`)

**Files:**
- Create: `src/iladub/etkl/propose.py`
- Test: `tests/etkl/test_propose.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) Proposal(name: str, confidence: float, rationale: str)`
  - `class Proposer(Protocol): def propose_dimension_name(self, values: list[str], context: dict) -> Proposal | None`
  - `@dataclass(frozen=True) FakeProposer(proposal: Proposal | None)` implementing the protocol (returns `self.proposal`, ignoring args).
  - `def baml_proposer_available() -> bool` — `os.environ.get("BAML_LIVE") == "1"` AND `importlib.util.find_spec("baml_client") is not None`.
  - `class BamlProposer` — `propose_dimension_name` lazily imports `baml_client` and calls `ProposeDimensionName` (wired in Task 4). Constructing it does NOT import baml_client (lazy in the method).

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_propose.py
import os
from iladub.etkl.propose import (Proposal, FakeProposer, baml_proposer_available,
                                  BamlProposer)


def test_fake_proposer_returns_proposal():
    p = FakeProposer(Proposal("Quarter", 0.9, "Q1..Q4 are quarters"))
    got = p.propose_dimension_name(["Q1", "Q2", "Q3", "Q4"], {"stub": "Product"})
    assert got.name == "Quarter" and got.confidence == 0.9


def test_fake_proposer_can_decline():
    assert FakeProposer(None).propose_dimension_name(["x"], {}) is None


def test_baml_gate_off_by_default(monkeypatch):
    monkeypatch.delenv("BAML_LIVE", raising=False)
    assert baml_proposer_available() is False


def test_baml_proposer_construction_is_lazy():
    # constructing must NOT import baml_client (no network / no version guard at construct time)
    b = BamlProposer()
    assert b is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_propose.py -v`
Expected: FAIL (`No module named 'iladub.etkl.propose'`).

- [ ] **Step 3: Implement `src/iladub/etkl/propose.py`**

```python
"""propose — the injected proposer seam for GenAI-assisted reshape (Loop A2).

The proposer is how A2 reaches a model, boxed by BAML. It is INJECTED so all logic is
offline-testable (FakeProposer); the live path (BamlProposer) is lazy + env-gated.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Proposal:
    name: str
    confidence: float
    rationale: str


class Proposer(Protocol):
    def propose_dimension_name(self, values: list, context: dict) -> "Proposal | None": ...


@dataclass(frozen=True)
class FakeProposer:
    """Deterministic offline proposer for tests/showcase. Returns its fixed proposal."""
    proposal: "Proposal | None"

    def propose_dimension_name(self, values, context):
        return self.proposal


def baml_proposer_available() -> bool:
    """True only when explicitly enabled AND baml_client is importable."""
    return os.environ.get("BAML_LIVE") == "1" and importlib.util.find_spec("baml_client") is not None


class BamlProposer:
    """Live proposer — calls the BAML ProposeDimensionName function. Lazy: baml_client is
    imported only inside the method, so constructing this never triggers the version guard."""

    def propose_dimension_name(self, values, context):
        from baml_client import sync_client
        r = sync_client.b.ProposeDimensionName(values, context.get("stub"), context.get("title"))
        return Proposal(name=r.name, confidence=r.confidence, rationale=r.rationale)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_propose.py -v`
Expected: PASS (4 tests). `test_baml_proposer_construction_is_lazy` passes because the import is inside the method.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/propose.py tests/etkl/test_propose.py
git commit -m "feat(etkl): proposer seam — Proposal/Proposer/FakeProposer + gated lazy BamlProposer (Loop A2.1)"
```

---

### Task 2: `certify_with_proposals` — the augmenting pass (offline core)

**Files:**
- Modify: `src/iladub/etkl/reshape.py`
- Test: `tests/etkl/test_certify_proposals.py`

**Interfaces:**
- Consumes: `denormalization.recover_dimensions` (→ `PivotedDimension(axis, level, name, values)`), `recipe.col_leaf_label`/`row_label`/`grid_values`, `oracle.round_trip`, `denormalization._entry`/`_num`, `propose.Proposer`/`Proposal`.
- Produces:
  - `@dataclass(frozen=True) ProposalOutcome(normalized_base, promotions: tuple, oracle_ok: bool, residue: tuple)`
  - `def certify_with_proposals(g, t, proposer) -> ProposalOutcome`
  - `def emit_base_projection(g, t, recipe, base) -> URIRef` (extracted from `emit_normalized_base`; shared).
  - A2-local helper `def _named_pivot_recipe_and_base(g, t, dim, name) -> tuple[Recipe, list]` using value-set measure detection (probe-validated).

- [ ] **Step 1: Write the failing test** (offline; uses FakeProposer)

```python
# tests/etkl/test_certify_proposals.py
import pytest
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.propose import Proposal, FakeProposer
from iladub.etkl.reshape import certify_with_proposals
TAB = Namespace("https://w3id.org/iladub/tab#"); EX = Namespace("https://example.org/d#")


def _nameless_pivot(ragged=False):
    """Product stub + nameless Q1..Q4 pivot; 2 rows. ragged=True drops a cell so it can't invert."""
    g = Graph(); t = EX.tbl
    cols = [EX["c%d" % i] for i in range(5)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        if lbl is not None:
            lc = URIRef(str(u) + "l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hstub, 0, "Product", [cols[0]])
    hdr(EX.hspan, 0, None, cols[1:])                      # nameless spanning parent
    for c, nm in zip(cols[1:], ["Q1", "Q2", "Q3", "Q4"]):
        hdr(URIRef(str(c) + "h"), 1, nm, [c])
    rows = ["A", "B"]; ru = {r: EX["r" + r] for r in rows}
    vals = {"A": ["A", "1", "2", "3", "4"], "B": ["B", "5", "6", "7", "8"]}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
        for c, txt in zip(cols, vals[r]):
            if ragged and r == "B" and c == cols[2]:      # drop one measure cell → not invertible
                continue
            e = EX["e_%s_%s" % (r, str(c)[-1])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    return g, t


def test_happy_path_names_and_inverts():
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "quarters")))
    assert out.oracle_ok and out.normalized_base is not None
    facts = list(g.objects(out.normalized_base, TAB.hasBaseFact))
    assert len(facts) == 8
    coords = {(str(g.value(co, TAB.dimensionName)), str(g.value(co, TAB.value)))
              for f in facts for co in g.objects(f, TAB.atDimensionValue)}
    assert ("Quarter", "Q1") in coords and ("Product", "A") in coords


def test_declined_proposal_escalates():
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(None))
    assert out.normalized_base is None
    assert (None, RDF.type, TAB.NormalizedBase) not in g


def test_uninvertible_region_is_rejected_even_with_a_name():
    g, t = _nameless_pivot(ragged=True)
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "quarters")))
    assert not out.oracle_ok and out.normalized_base is None


def test_named_pivot_does_not_call_proposer(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables

    class _Spy:
        def propose_dimension_name(self, values, context):
            raise AssertionError("proposer must NOT be called when the pivot is already named")
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    out = certify_with_proposals(rep.graph, t, _Spy())   # Region is named → no proposal
    assert out.normalized_base is None                   # A2 pass finds no nameless pivot; A1 owns named ones
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_certify_proposals.py -v`
Expected: FAIL (`certify_with_proposals` undefined).

- [ ] **Step 3: Extract the shared emitter, then add the A2 pass to `src/iladub/etkl/reshape.py`**

First, refactor `emit_normalized_base` to delegate its fact-writing to a shared helper (behaviour-preserving). Replace the body from `nb = URIRef(...)` through the fact loop with a call to `emit_base_projection`, and add that helper:

```python
def emit_base_projection(g, t, recipe, base):
    """Emit the derived NormalizedBase projection + its base facts from a validated
    (recipe, base). Shared by A1 (emit_normalized_base) and A2 (certify_with_proposals)."""
    ru = _materialize_recipe(g, t, recipe)
    nb = URIRef("%s-normbase" % t)
    g.add((nb, RDF.type, TAB.NormalizedBase))
    g.add((nb, TAB.derivedByRecipe, ru))
    g.add((nb, PROV.wasDerivedFrom, t))
    for i, row in enumerate(base):
        bf = URIRef("%s-fact-%d" % (t, i))
        g.add((bf, RDF.type, TAB.BaseFact))
        g.add((nb, TAB.hasBaseFact, bf))
        g.add((bf, TAB.measureValue, Literal(round(row["__measure__"], 6), datatype=XSD.decimal)))
        for k, v in row.items():
            if k == "__measure__":
                continue
            co = BNode()
            g.add((bf, TAB.atDimensionValue, co))
            g.add((co, TAB.dimensionName, Literal(k)))
            g.add((co, TAB.value, Literal(v)))
    return nb


def emit_normalized_base(g, t):
    """A1: if the deterministic recipe round-trips, emit the derived projection; else None."""
    recipe, verdict, base = certify(g, t)
    if not verdict.ok or not base:
        return None
    return emit_base_projection(g, t, recipe, base)
```

Then add the A2 pass (append to the module). Add these imports at the top: `from .propose import Proposal  # noqa: F401` is not needed; only `from dataclasses import dataclass` (already used indirectly — import it) and reuse existing `row_label`, `grid_values`, `col_leaf_label`, `dn`, `round_trip`, `UnpivotOp`, `Recipe`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProposalOutcome:
    normalized_base: object     # URIRef | None
    promotions: tuple           # PromotionDecision uris (Task 3); () until then
    oracle_ok: bool
    residue: tuple


def _nameless_col_pivots(g, t):
    return [d for d in dn.recover_dimensions(g, t)
            if d.axis == "column" and d.name is None and len(d.values) > 1]


def _named_pivot_recipe_and_base(g, t, dim, name):
    """Build (recipe, base) for a nameless column pivot given a proposed name. Measure
    columns are identified by VALUE-SET membership (leaf label in dim.values) — the
    nameless analogue of A1's level-0-label detection. The name enters ONLY the recipe
    and the base coordinates (never the source graph)."""
    valset = set(dim.values)
    measure_cols = [c for c in g.objects(t, TAB.hasLeafColumn) if col_leaf_label(g, c) in valset]
    stubs = []
    for c in g.objects(t, TAB.hasLeafColumn):
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if levels and max(levels) == 0 and col_leaf_label(g, c) not in valset:
            stubs.append(col_leaf_label(g, c))
    stub = stubs[0] if stubs else None
    recipe = Recipe((UnpivotOp(dimension=name, stub=stub, axis="column"),))
    base = []
    for r in g.objects(t, TAB.hasLeafRow):
        rlab = row_label(g, t, r)
        for c in measure_cols:
            e = dn._entry(g, t, r, c)
            if e is None:
                continue
            v = dn._num(str(g.value(e, TAB.cellText)))
            if v is None:
                continue
            row = {"__measure__": v}
            if stub is not None:
                row[stub] = rlab
            row[name] = col_leaf_label(g, c)
            base.append(row)
    return recipe, base


def certify_with_proposals(g, t, proposer):
    """A2 augmenting pass: for a nameless column pivot, ask the proposer for the dimension
    name, build the named recipe+base (value-set detection), and run A1's round-trip oracle.
    On success emit the derived projection (+ promotion in Task 3); else escalate."""
    pivots = _nameless_col_pivots(g, t)
    if not pivots:
        return ProposalOutcome(None, (), True, ())     # nothing nameless → A1 owns it; proposer untouched
    dim = pivots[0]
    context = {"stub": _first_stub_name(g, t, set(dim.values)), "title": None}
    proposal = proposer.propose_dimension_name(list(dim.values), context)
    if proposal is None:
        return ProposalOutcome(None, (), True, ())     # declined → escalate, nothing asserted
    recipe, base = _named_pivot_recipe_and_base(g, t, dim, proposal.name)
    verdict = round_trip(grid_values(g, t), base, recipe)
    if not verdict.ok or not base:
        return ProposalOutcome(None, (), verdict.ok, verdict.residue)   # not invertible → escalate
    nb = emit_base_projection(g, t, recipe, base)
    return ProposalOutcome(nb, (), True, ())           # promotions wired in Task 3


def _first_stub_name(g, t, valset):
    for c in g.objects(t, TAB.hasLeafColumn):
        levels = [int(g.value(h, TAB.headerLevel)) for h in g.subjects(TAB.coversColumn, c)]
        if levels and max(levels) == 0 and col_leaf_label(g, c) not in valset:
            return col_leaf_label(g, c)
    return None
```

- [ ] **Step 4: Run tests to verify they pass, and confirm A1 is unbroken**

Run: `.venv/bin/pytest tests/etkl/test_certify_proposals.py -v`
Expected: PASS (4 tests).
Run: `.venv/bin/pytest tests/etkl/ -q`
Expected: PASS (all A1 tests still green — the `emit_normalized_base` extraction is behaviour-preserving).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/reshape.py tests/etkl/test_certify_proposals.py
git commit -m "feat(etkl): certify_with_proposals — name a nameless pivot, value-set recovery, oracle-gated (Loop A2.1)"
```

---

### Task 3: Promotion emission (`promote.py`) + thin vocab

**Files:**
- Create: `src/iladub/etkl/promote.py`
- Modify: `src/iladub/etkl/reshape.py` (wire promotion into `certify_with_proposals`)
- Modify: `vocab/ontology/tab.ttl` (add rangeless `tab:namePromotedBy`)
- Test: `tests/etkl/test_promote.py`

**Interfaces:**
- Produces: `def emit_promotion(g, t, normalized_base, dimension_name, values, proposal) -> URIRef` — writes the `iladub:CandidateConcept`, the `iladub:PromotionDecision`, the `iladub:Suggester` agent, links the recipe's `UnpivotOp` via `tab:namePromotedBy`, and returns the PromotionDecision uri.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_promote.py
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.propose import Proposal, FakeProposer
from iladub.etkl.reshape import certify_with_proposals
from tests.etkl.test_certify_proposals import _nameless_pivot
TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")


def test_promotion_records_the_name_as_a_proposition():
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "Q1..Q4 are quarters")))
    assert out.normalized_base is not None and len(out.promotions) == 1
    pd = out.promotions[0]
    assert (pd, RDF.type, ILADUB.PromotionDecision) in g
    cand = g.value(pd, ILADUB.reviews)
    assert cand is not None and str(g.value(cand, RDF.type)) == str(ILADUB.CandidateConcept)
    assert str(g.value(cand, __import__("rdflib").RDFS.label)) == "Quarter"
    assert float(g.value(cand, ILADUB.confidence)) == 0.9
    assert g.value(cand, ILADUB.suggestedBy) is not None
    assert g.value(pd, DEC.decidedBy) is not None
    assert g.value(pd, DEC.produced) == out.normalized_base
    assert "proposition" in str(g.value(pd, DEC.rationale)).lower()
    # the admitted name links to its promotion via the rangeless tab link
    assert (None, TAB.namePromotedBy, pd) in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/etkl/test_promote.py -v`
Expected: FAIL (`out.promotions` empty / `tab:namePromotedBy` absent).

- [ ] **Step 3: Add `tab:namePromotedBy` (rangeless) to `vocab/ontology/tab.ttl`**

Append after the reshape-recipe block (keeps `tab.ttl` standalone — NO `iladub:` reference; the range is applied only at runtime):

```turtle
# --- A2 promotion link (rangeless: points at an iladub:PromotionDecision at runtime) -----
tab:namePromotedBy a owl:ObjectProperty ; rdfs:label "name promoted by"@en ;
    rdfs:comment "Links a reshape operation whose dimension name was GenAI-proposed to the iladub:PromotionDecision that admitted the name. Rangeless to keep tab.ttl standalone."@en .
```

- [ ] **Step 4: Implement `src/iladub/etkl/promote.py`**

```python
"""promote — emit the accountable provenance for a GenAI-proposed dimension name (Loop A2).

The proposed name is a PROPOSITION: an iladub:CandidateConcept reviewed by an
iladub:PromotionDecision (a dec:DecisionHolon). The reshape structure is oracle-certified;
the NAME is not — dec:rationale records that split.
"""
from __future__ import annotations

from rdflib import RDF, RDFS, BNode, Literal, Namespace, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
MODEL_ID = "claude-opus-4-8"


def _suggester(g):
    agent = URIRef("urn:iladub:suggester/baml.ProposeDimensionName@%s" % MODEL_ID)
    g.add((agent, RDF.type, ILADUB.Suggester))
    return agent


def emit_promotion(g, t, normalized_base, dimension_name, values, proposal):
    """Write the CandidateConcept + PromotionDecision for a promoted name; link the recipe's
    UnpivotOp via tab:namePromotedBy. Returns the PromotionDecision uri."""
    agent = _suggester(g)
    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(dimension_name)))
    g.add((cand, ILADUB.surfaceText, Literal(" | ".join(values))))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.confidence, Literal(round(proposal.confidence, 6), datatype=XSD.decimal)))

    pd = URIRef("%s-promotion-%s" % (t, dimension_name))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, t))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, Literal(round(proposal.confidence, 6), datatype=XSD.decimal)))
    g.add((pd, DEC.rationale, Literal(
        "Reshape round-trips exactly with dimension=%s; the name is a model proposition, "
        "not oracle-verified. Rationale: %s" % (dimension_name, proposal.rationale))))
    g.add((pd, DEC.produced, normalized_base))

    # link the UnpivotOp carrying this dimension name to its promotion
    for op in g.subjects(RDF.type, TAB.UnpivotOp):
        if str(g.value(op, TAB.opDimension)) == dimension_name:
            g.add((op, TAB.namePromotedBy, pd))
    return pd
```

- [ ] **Step 5: Wire promotion into `certify_with_proposals`**

In `reshape.py`, change the success branch to emit the promotion and return it:

```python
    nb = emit_base_projection(g, t, recipe, base)
    from .promote import emit_promotion
    pd = emit_promotion(g, t, nb, proposal.name, list(dim.values), proposal)
    return ProposalOutcome(nb, (pd,), True, ())
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/etkl/test_promote.py tests/etkl/test_certify_proposals.py -v`
Expected: PASS. Also `.venv/bin/pytest tests/test_source_ownership.py -q` — Expected: PASS (`tab.ttl` still standalone; the `iladub:` link is runtime-only, not in the .ttl).

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/promote.py vocab/ontology/tab.ttl tests/etkl/test_promote.py src/iladub/etkl/reshape.py
git commit -m "feat(etkl): promotion emission — CandidateConcept + PromotionDecision for a proposed name (Loop A2.1)"
```

---

### Task 4: BAML function + gated live smoke

**Files:**
- Create: `baml_src/reshape_propose.baml`
- Regenerate: `baml_client/` (via `baml generate`)
- Test: `tests/test_baml_propose_smoke.py`

**Interfaces:**
- Consumes: the existing `client: Claude` from `baml_src/clients.baml`; `BamlProposer` from Task 1.
- Produces: BAML `function ProposeDimensionName(values: string[], stub: string?, table_title: string?) -> DimensionNameProposal` with `class DimensionNameProposal { name: string, confidence: float, rationale: string }`.

- [ ] **Step 1: Create `baml_src/reshape_propose.baml`**

```baml
class DimensionNameProposal {
    name string @description("the single attribute/dimension name these column labels are the values of")
    confidence float @description("0.0-1.0, calibrated confidence in the name")
    rationale string @description("one sentence on why")
}

function ProposeDimensionName(values: string[], stub: string?, table_title: string?) -> DimensionNameProposal {
    client Claude
    prompt #"
        These column labels are the VALUES of one pivoted dimension in a table: {{ values }}.
        The row-key (stub) column is: {{ stub }}. Table title: {{ table_title }}.
        Name the single dimension whose values these are (one word or short phrase, e.g. "Quarter" for Q1..Q4).
        {{ ctx.output_format }}
    "#
}
```

(Confirm the BAML prompt/interpolation syntax against the installed toolchain with `baml describe` if `baml check` reports a syntax error — the exact interpolation braces must match the version in `baml_src/generators.baml`. Match the style already used in the repo's other `baml_src/*.baml` files.)

- [ ] **Step 2: Compile-check and regenerate the client**

Run: `.venv/bin/baml check` (or the repo's generate path) then `.venv/bin/baml generate`
Expected: no errors; `baml_client/` updated. Confirm `baml_src/generators.baml` still pins `version "0.222.0"` and `.venv` has `baml-py==0.222.0` (they must match).

- [ ] **Step 3: Write the gated live smoke test**

```python
# tests/test_baml_propose_smoke.py
import os
import pytest


@pytest.mark.skipif(os.environ.get("BAML_LIVE") != "1", reason="live BAML gated behind BAML_LIVE=1")
def test_propose_dimension_name_live():
    pytest.importorskip("baml_client")
    from iladub.etkl.propose import BamlProposer
    got = BamlProposer().propose_dimension_name(["Q1", "Q2", "Q3", "Q4"], {"stub": "Product", "title": None})
    assert got is not None and got.name          # a plausible non-empty name
    assert 0.0 <= got.confidence <= 1.0
```

- [ ] **Step 4: Run the default (skipped) + confirm collection**

Run: `.venv/bin/pytest tests/test_baml_propose_smoke.py -v`
Expected: 1 skipped (BAML_LIVE unset). No collection error.

- [ ] **Step 5: Commit**

```bash
git add baml_src/reshape_propose.baml baml_client tests/test_baml_propose_smoke.py
git commit -m "feat(etkl): BAML ProposeDimensionName + gated live smoke (Loop A2.1)"
```

---

### Task 5: Showcase Part J (offline-reproducible)

**Files:**
- Modify: `demo/etkl_demo_data.py` (add a nameless-pivot PDF generator, if none fits)
- Modify: `demo/etkl_1a_showcase.ipynb` (Part J)

**Interfaces:**
- Consumes: `certify` (A1), `certify_with_proposals` (A2), `FakeProposer`/`Proposal`.

- [ ] **Step 1: Add a nameless-pivot demo fixture**

In `demo/etkl_demo_data.py`, add `nameless_pivot_report_pdf(path)` — a small report with a `Product` stub and four quarter columns `Q1 Q2 Q3 Q4` under a **blank** spanning header (no "Quarter" title), values filled. Follow the reportlab style of the existing generators in that file. Probe it first (`compile_tables` → a `HierarchicalTable` whose column pivot recovers `name=None`) before wiring the cell.

- [ ] **Step 2: Add Part J cells to the notebook**

A markdown intro + a render cell (lead with the rendered original PDF, per standing directive) + a readout cell:

```python
# Part J — a NAMELESS pivot: A1 escalates (can't name the dimension); A2 proposes the name
from iladub.etkl import compile_tables
from iladub.etkl.reshape import certify, certify_with_proposals
from iladub.etkl.propose import FakeProposer, Proposal
from iladub.etkl.holon import TAB
from rdflib import RDF, Namespace
ILADUB = Namespace("https://w3id.org/iladub#"); DEC = Namespace("https://w3id.org/iladub/dec#")

rep = compile_tables(np_pdf)
t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))

# A1 alone: the dimension has no name -> nothing to invert (escalated)
_, v1, base1 = certify(rep.graph, t)
print(f"A1 deterministic: base facts = {len(base1)}  (the pivot has no header name -> escalated)")

# A2: a recorded proposer supplies the name (live, this is a BAML model call)
proposer = FakeProposer(Proposal("Quarter", 0.9, "Q1..Q4 are calendar quarters"))
out = certify_with_proposals(rep.graph, t, proposer)
print(f"A2 with a proposed name: oracle round-trips = {out.oracle_ok}, base facts = {len(list(rep.graph.objects(out.normalized_base, TAB.hasBaseFact)))}")
pd = out.promotions[0]
cand = rep.graph.value(pd, ILADUB.reviews)
print(f"PROMOTION (accountable): name '{rep.graph.value(cand, __import__('rdflib').RDFS.label)}' "
      f"proposed by {rep.graph.value(pd, DEC.decidedBy)} @ confidence {rep.graph.value(cand, ILADUB.confidence)}")
print("  ->", rep.graph.value(pd, DEC.rationale))
print()
print("The NAME is a proposition (never oracle-verified); the RESHAPE is deterministically certified.")
print("Offline here via a recorded proposer; live it is a BAML ProposeDimensionName call.")
```

- [ ] **Step 3: Re-run the whole notebook to 0 errors**

Run: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace demo/etkl_1a_showcase.ipynb --ExecutePreprocessor.timeout=420`
Expected: exit 0, no cell errors. Verify Part J shows A1 base facts = 0 → A2 base facts = 8 + the promotion line.

- [ ] **Step 4: Commit**

```bash
git add demo/etkl_demo_data.py demo/etkl_1a_showcase.ipynb
git commit -m "docs(demo): showcase Part J — nameless pivot, A1 escalates, A2 names + promotes (Loop A2.1)"
```

---

## Self-Review

**1. Spec coverage:** proposer seam (T1), augmenting-pass + value-set recovery + oracle + three escalation guards incl. no-call (T2), promotion emission reusing iladub/dec vocab + thin rangeless `tab:namePromotedBy` (T3), BAML function + gated live smoke (T4), offline-reproducible showcase Part J (T5). Honest split (structure certified / name a proposition) is in `dec:rationale` (T3) and the showcase (T5). All spec §7 files covered. ✓

**2. Placeholder scan:** No TBD/TODO; every code step has complete code; the only "confirm against toolchain" note (T4 Step 1) is a real compile-check instruction, not a placeholder. ✓

**3. Type consistency:** `Proposal(name, confidence, rationale)` / `Proposer.propose_dimension_name(values, context)` / `FakeProposer(proposal)` consistent T1→T5. `ProposalOutcome(normalized_base, promotions, oracle_ok, residue)` consistent T2→T5. `emit_base_projection(g,t,recipe,base)` and `emit_promotion(g,t,normalized_base,dimension_name,values,proposal)` consistent. Value-set recovery matches the probe. ✓

**Accepted risk (per user "don't over-engineer, be attentive"):** the name is never oracle-verified (a confidently-wrong name round-trips and is admitted as a provenance-bearing proposition) — by design, §8 of the spec. The A1 `emit_normalized_base` extraction is the only A1 touch, behaviour-preserving, gated by the A1 suite staying green.
