# NEURAL Loop B1.3 — Narrow-Flank Merge Resolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the `MERGE_AMBIGUOUS` escalations that loop B1.2 left quarantined, by having a BAML proposer pick a narrow-flank reading (absorb vs standalone), disposing it with the shipped `region_tiles` SHACL oracle, and admitting a legal reading only as an oracle-guarded `PromotionDecision` proposition — never as grounded truth.

**Architecture:** A new injected `SpanProposer` seam (mirroring the shipped A2 `Proposer`) proposes a reading for a narrow-flank tie B1.2 detected. A pure tree-rewrite builder produces the header tree under that reading; the existing `assert_hier_region` + `region_tiles` dispose it structurally; a new `emit_span_promotion` records the accountable proposition. `compile_tables` gains an optional `span_proposer=None` param — absent it, behaviour is byte-identical to today (escalate).

**Tech Stack:** Python 3.12, rdflib, pySHACL (via the shipped `tiling.region_tiles`), pytest. BAML is a live-only path (`BAML_LIVE=1`), never on the test path.

## Global Constraints

- **§8 gate (verbatim intent):** this slice is **NEURAL** — GenAI-via-BAML *proposing*, disposed by a *semantic oracle* (`region_tiles`, the loop-C tiling SHACL), promoted under the assert/propose/promote epistemics (§3). NEVER a Python geometry heuristic with a tuned tolerance. State the classification in the code.
- **Oracle, not confidence:** `region_tiles` rejects structurally-illegal proposals; **legality gates admission, confidence never does.** A legal-but-non-unique reading is admitted ONLY as an `iladub:CandidateConcept` reviewed by an `iladub:PromotionDecision` — a proposition, never asserted as grounded truth (§3).
- **No behaviour change by default:** `compile_tables(..., span_proposer=None)` → byte-identical to today. Live `BamlSpanProposer` stays `BAML_LIVE=1`-gated via the existing `baml_proposer_available()`.
- **Scope (YAGNI):** ONLY the single narrow-orphan tied flank (B1.2's `_narrow_flank_tie`). General merged-header span is loop B2. Genuine overlap collisions (offcenter) stay escalated — never enter the resolution branch.
- **Only emit what the source supports (§7):** the span reading carries full provenance (suggester, confidence, tie rationale); nothing is fabricated.
- **Testing:** run tests ONLY via `./.venv/bin/python -m pytest` (bare `python3` uses the wrong rdflib → spurious SPARQL failures).
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `etkl-neural-b1-3-merge-resolution`.

---

### Task 1: `SpanProposer` seam — `SpanProposal`, `SpanProposer` protocol, `FakeSpanProposer`, `BamlSpanProposer`

**Files:**
- Modify: `src/iladub/etkl/propose.py`
- Test: `tests/etkl/test_span_proposer.py`

**Interfaces:**
- Consumes: the existing `baml_proposer_available()` (env gate, unchanged).
- Produces:
  - `SpanProposal(choice: str, confidence: float, rationale: str, suggester_iri: str = "urn:iladub:suggester/recorded-span-proposer")` — frozen; `choice ∈ {"absorb","standalone"}`.
  - `SpanProposer` Protocol: `propose_header_span(self, context: dict) -> SpanProposal | None`.
  - `FakeSpanProposer(proposal: SpanProposal | None)` — frozen, returns its fixed proposal.
  - `BamlSpanProposer` — `propose_header_span` lazy-calls BAML `ProposeHeaderSpan`.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_span_proposer.py
import dataclasses
from iladub.etkl.propose import SpanProposal, SpanProposer, FakeSpanProposer


def test_spanproposal_is_frozen():
    p = SpanProposal("absorb", 0.9, "reads as one span")
    assert dataclasses.is_dataclass(p) and p.choice == "absorb"
    try:
        p.choice = "standalone"  # type: ignore[misc]
        assert False, "SpanProposal must be frozen"
    except dataclasses.FrozenInstanceError:
        pass


def test_fake_span_proposer_returns_fixed_proposal():
    p = SpanProposal("standalone", 0.7, "flank is its own column")
    fp = FakeSpanProposer(p)
    assert fp.propose_header_span({"span_label": "Current Visit"}) is p


def test_fake_span_proposer_can_abstain():
    assert FakeSpanProposer(None).propose_header_span({}) is None


def test_span_proposer_protocol_shape():
    assert hasattr(SpanProposer, "propose_header_span")
    FakeSpanProposer(None).propose_header_span({})  # structural smoke
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_span_proposer.py -v`
Expected: FAIL — `ImportError: cannot import name 'SpanProposal'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/etkl/propose.py`:

```python
@dataclass(frozen=True)
class SpanProposal:
    """A proposed reading for a narrow-flank merge tie (loop B1.3). `choice` is 'absorb'
    (the flank belongs under the span) or 'standalone' (the flank is its own top-level leaf).
    The reading is a PROPOSITION (§3): admitted only via a PromotionDecision after region_tiles
    confirms it is structurally legal — never asserted as grounded truth."""
    choice: str                 # "absorb" | "standalone"
    confidence: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/recorded-span-proposer"


class SpanProposer(Protocol):
    def propose_header_span(self, context: dict) -> "SpanProposal | None": ...


@dataclass(frozen=True)
class FakeSpanProposer:
    """Deterministic offline span proposer for tests/showcase. Returns its fixed proposal
    (or None to model abstention)."""
    proposal: "SpanProposal | None"

    def propose_header_span(self, context):
        return self.proposal


class BamlSpanProposer:
    """Live span proposer — calls the BAML ProposeHeaderSpan function. Lazy: baml_client is
    imported only inside the method, so constructing this never triggers the version guard.
    NEURAL propose seam; env-gated by baml_proposer_available()."""

    def propose_header_span(self, context):
        from baml_client import sync_client
        r = sync_client.b.ProposeHeaderSpan(
            context.get("span_label"),
            context.get("leaf_labels"),
            context.get("flank_label"),
            context.get("flank_side"),
        )
        return SpanProposal(
            choice=r.choice,
            confidence=r.confidence,
            rationale=r.rationale,
            suggester_iri="urn:iladub:suggester/baml.ProposeHeaderSpan",
        )
```

`propose.py` already imports `dataclass`, `Protocol`, `os`, `importlib.util` at the top — no new imports needed.

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_span_proposer.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/propose.py tests/etkl/test_span_proposer.py
git commit -m "feat(etkl): SpanProposer seam — SpanProposal, FakeSpanProposer, BamlSpanProposer (B1.3 propose)"
```

---

### Task 2: Tie carry-through — `HeaderNode.ambiguous_flank`

**Files:**
- Modify: `src/iladub/etkl/headers.py` (`HeaderNode` dataclass; `resolve_narrow_flanks`; `infer_header_tree` parent-link reconstruction)
- Test: `tests/etkl/test_ambiguous_flank.py`

**Interfaces:**
- Consumes: existing `resolve_narrow_flanks(nodes, grid, ink_cols_by_node)`, `_narrow_flank_tie`.
- Produces: `HeaderNode.ambiguous_flank: int | None = None` — the tied leaf column recorded when `_narrow_flank_tie` fires; carried through `infer_header_tree`'s final reconstruction.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_ambiguous_flank.py
from dataclasses import replace
from iladub.etkl.headers import HeaderNode, resolve_narrow_flanks
from iladub.etkl.grid import LeafGrid


def test_ambiguous_flank_records_the_tied_column():
    # boundaries [0,100,200,300,400,440]: col4 width 40 < 0.5*median_pitch(100)=50, ink-unreached
    grid = LeafGrid(boundaries=(0.0, 100.0, 200.0, 300.0, 400.0, 440.0), ncols=5,
                    pitch=100.0, confidence=1.0)
    node = HeaderNode(level=0, covers=(1, 2, 3, 4), text="Span", parent=None, center_x=250.0)
    ink = [(1, 2, 3)]                      # node's ink reaches cols 1..3 only; col4 is the flank
    out = resolve_narrow_flanks([node], grid, ink)
    assert out[0].ambiguous is True
    assert out[0].ambiguous_flank == 4


def test_ambiguous_flank_defaults_none_and_field_present():
    n = HeaderNode(0, (1,), "x", None)
    assert n.ambiguous_flank is None
    assert replace(n, ambiguous_flank=3).ambiguous_flank == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ambiguous_flank.py -v`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'ambiguous_flank'` (field absent) / `resolve_narrow_flanks` doesn't set it.

- [ ] **Step 3: Write minimal implementation**

In `src/iladub/etkl/headers.py`, add the field to `HeaderNode`:

```python
@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None
    center_x: float | None = None
    ambiguous: bool = False
    ambiguous_flank: int | None = None
```

In `resolve_narrow_flanks`, record the flank column (change the single mutation line):

```python
        flank = _narrow_flank_tie(n.covers, tuple(ink), b)
        if flank is None:
            continue
        out[i] = replace(n, ambiguous=True, ambiguous_flank=flank)
```

In `infer_header_tree`, carry the field through the final reconstruction (the `linked.append(...)` line):

```python
        linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx,
                                 n.center_x, n.ambiguous, n.ambiguous_flank))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ambiguous_flank.py tests/etkl/test_headers.py tests/etkl/test_span_gate.py -v`
Expected: PASS (new tests pass; all shipped `test_headers` / `test_span_gate` stay green — the field is additive with a default).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/test_ambiguous_flank.py
git commit -m "feat(etkl): HeaderNode.ambiguous_flank — carry the tied leaf column through infer_header_tree (B1.3 seam)"
```

---

### Task 3: Candidate-reading builder + proposer context — `span.build_reading`, `span.flank_context`

**Files:**
- Create: `src/iladub/etkl/span.py`
- Test: `tests/etkl/test_span_builder.py`

**Interfaces:**
- Consumes: `iladub.etkl.headers.HeaderNode`; `iladub.etkl.grid.LeafGrid`.
- Produces:
  - `build_reading(tree: tuple[HeaderNode, ...], node_idx: int, flank: int, choice: str) -> tuple[HeaderNode, ...]` — pure tree rewrite.
  - `flank_context(tree: tuple[HeaderNode, ...], node_idx: int, flank: int) -> dict` — the proposer's inputs.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_span_builder.py
from iladub.etkl.headers import HeaderNode
from iladub.etkl.span import build_reading, flank_context


def _tree():
    # parent "Current Visit" over cols 1..4 (col4 = tied flank, ambiguous), plus three
    # deeper sub-header leaves for cols 1,2,3 and a header-empty flank (no leaf for col4).
    parent = HeaderNode(0, (1, 2, 3, 4), "Current Visit", None, 250.0, True, 4)
    a = HeaderNode(1, (1,), "Analyte", 0, 150.0)
    r = HeaderNode(1, (2,), "Result", 0, 250.0)
    u = HeaderNode(1, (3,), "Unit", 0, 350.0)
    return (parent, a, r, u)


def test_absorb_keeps_flank_and_clears_ambiguous():
    out = build_reading(_tree(), 0, 4, "absorb")
    assert out[0].covers == (1, 2, 3, 4)
    assert out[0].ambiguous is False and out[0].ambiguous_flank is None


def test_standalone_drops_flank_and_adds_empty_leaf():
    out = build_reading(_tree(), 0, 4, "standalone")
    assert out[0].covers == (1, 2, 3)          # flank removed from the span
    assert out[0].ambiguous is False
    # a header-empty flank becomes a new top-level leaf covering exactly (4,)
    leaves = [n for n in out if n.covers == (4,) and n.parent is None]
    assert len(leaves) == 1 and leaves[0].level == 0 and leaves[0].text == ""


def test_standalone_reparents_existing_leaf_for_the_flank():
    # if a deeper leaf already covers the flank, re-root it instead of adding an empty one
    tree = _tree() + (HeaderNode(1, (4,), "Flag", 0, 450.0),)
    out = build_reading(tree, 0, 4, "standalone")
    roots4 = [n for n in out if n.covers == (4,) and n.parent is None]
    assert len(roots4) == 1 and roots4[0].text == "Flag" and roots4[0].level == 0
    assert not any(n.covers == (4,) and n.text == "" for n in out)   # no spurious empty leaf


def test_flank_context_carries_labels_and_side():
    ctx = flank_context(_tree(), 0, 4)
    assert ctx["span_label"] == "Current Visit"
    assert ctx["leaf_labels"] == ["Analyte", "Result", "Unit"]
    assert ctx["flank_label"] == ""            # header-empty flank
    assert ctx["flank_side"] == "right"        # flank == max(covers)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_span_builder.py -v`
Expected: FAIL — `ModuleNotFoundError: iladub.etkl.span`.

- [ ] **Step 3: Write minimal implementation**

Create `src/iladub/etkl/span.py`:

```python
"""span — loop B1.3 NEURAL narrow-flank merge resolution: propose -> tile-oracle -> promote.

§8 gate: this module hosts the NEURAL slice. The reading is NOT decided by geometry here — a
SpanProposer (BAML, injected) proposes it and region_tiles (SHACL) disposes it; a legal reading
is admitted only as a PromotionDecision proposition (§3). build_reading/flank_context are pure
structural rewrites (no geometry constant); the decision lives in the injected proposer + oracle.
"""
from __future__ import annotations

from dataclasses import replace

from .headers import HeaderNode


def build_reading(tree, node_idx, flank, choice):
    """Rewrite the resolved header tree under a proposed reading for the tied flank column.

    absorb     -> the ambiguous node keeps the flank in its covers (clear the ambiguity flags).
    standalone -> drop the flank from the node's covers; the flank becomes a top-level leaf.
                  If a deeper node already covers exactly (flank,) under this node, re-root it
                  (parent=None, level 0); otherwise (a header-empty flank) append a new empty
                  level-0 leaf covering (flank,). assert_hier_region's orphan-promotion then
                  emits it as a standalone leaf, satisfying the tiling shapes.

    Pure structural rewrite — no geometry, no tuned constant. Returns the new tree tuple."""
    out = list(tree)
    n = out[node_idx]
    if choice == "absorb":
        out[node_idx] = replace(n, ambiguous=False, ambiguous_flank=None)
        return tuple(out)
    # standalone
    new_covers = tuple(c for c in n.covers if c != flank)
    out[node_idx] = replace(n, covers=new_covers, ambiguous=False, ambiguous_flank=None)
    for i, m in enumerate(out):
        if m.covers == (flank,) and m.parent == node_idx:
            out[i] = replace(m, parent=None, level=0)
            return tuple(out)
    out.append(HeaderNode(0, (flank,), "", None))
    return tuple(out)


def flank_context(tree, node_idx, flank):
    """Build the SpanProposer inputs from the tree: the spanning label, the neighbouring leaf
    sub-labels (deeper nodes covering a single column under the span, in column order), the
    flank's own leaf label (empty for a header-empty flank), and the flank side."""
    n = tree[node_idx]
    span_cols = [c for c in n.covers if c != flank]
    leaf_labels = []
    for c in sorted(span_cols):
        for m in tree:
            if m.parent == node_idx and m.covers == (c,):
                leaf_labels.append(m.text)
                break
    flank_label = ""
    for m in tree:
        if m.covers == (flank,) and m.parent == node_idx:
            flank_label = m.text
            break
    side = "right" if flank == max(n.covers) else "left"
    return {"span_label": n.text, "leaf_labels": leaf_labels,
            "flank_label": flank_label, "flank_side": side}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_span_builder.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/span.py tests/etkl/test_span_builder.py
git commit -m "feat(etkl): span.build_reading + flank_context — pure reading rewrite + proposer context (B1.3)"
```

---

### Task 4: Span-promotion emitter — `promote.emit_span_promotion`

**Files:**
- Modify: `src/iladub/etkl/promote.py`
- Test: `tests/etkl/test_span_promotion.py`

**Interfaces:**
- Consumes: `iladub.etkl.propose.SpanProposal`; `rdflib`.
- Produces: `emit_span_promotion(g, region_uri, node_text, flank, choice, proposal) -> URIRef` — writes an `iladub:CandidateConcept` + `iladub:PromotionDecision` for the span reading; returns the PromotionDecision uri.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_span_promotion.py
from rdflib import Graph, RDF, RDFS, URIRef, Namespace
from iladub.etkl.promote import emit_span_promotion
from iladub.etkl.propose import SpanProposal

ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")


def test_emit_span_promotion_writes_candidate_and_decision():
    g = Graph()
    region = URIRef("urn:doc#htable0")
    proposal = SpanProposal("standalone", 0.82, "the flank reads as its own column")
    pd = emit_span_promotion(g, region, "Current Visit", 4, "standalone", proposal)

    # a proposition CandidateConcept exists, reviewed by the returned PromotionDecision
    cands = list(g.subjects(RDF.type, ILADUB.CandidateConcept))
    assert len(cands) == 1
    assert (pd, RDF.type, ILADUB.PromotionDecision) in g
    assert (pd, ILADUB.reviews, cands[0]) in g
    assert (cands[0], ILADUB.status, ILADUB.proposed) in g
    # rationale records the tie + choice (auditable proposition, not an assertion)
    rat = str(g.value(pd, DEC.rationale))
    assert "standalone" in rat and "tied" in rat.lower()
    # provenance links back to the region (§6 provenance-to-the-page chain)
    assert (pd, DEC.consideredEvidence, region) in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_span_promotion.py -v`
Expected: FAIL — `ImportError: cannot import name 'emit_span_promotion'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/etkl/promote.py` (module already imports `RDF, RDFS, BNode, Literal, Namespace, URIRef`, `Decimal`, and defines `ILADUB`, `DEC`, `GIST`, `_slug`):

```python
def emit_span_promotion(g, region_uri, node_text, flank, choice, proposal):
    """Write the CandidateConcept + PromotionDecision for a NEURAL narrow-flank merge reading
    (loop B1.3). The reading is a PROPOSITION: region_tiles has confirmed it is structurally
    LEGAL, but geometry could not decide it uniquely — so it is admitted accountably, never
    asserted as grounded truth (§3). Returns the PromotionDecision uri."""
    agent = URIRef(proposal.suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    confidence = Literal(Decimal(str(round(proposal.confidence, 6))))

    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal("%s span reading: %s (flank col %d)" % (node_text, choice, flank))))
    g.add((cand, ILADUB.surfaceText, Literal(node_text)))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.suggestedAnchor, GIST.Category))
    g.add((cand, ILADUB.fromRegion, region_uri))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    g.add((cand, ILADUB.confidence, confidence))

    pd = URIRef("%s-span-promotion-%s-c%d" % (region_uri, _slug(choice), flank))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, region_uri))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, confidence))
    g.add((pd, DEC.rationale, Literal(
        "Geometry tied at narrow flank col %d; model proposed '%s'; region_tiles confirms the "
        "reading is structurally legal but NOT oracle-verified as unique — admitted as a "
        "proposition. Rationale: %s" % (flank, choice, proposal.rationale))))
    g.add((pd, DEC.produced, region_uri))
    return pd
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_span_promotion.py -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/promote.py tests/etkl/test_span_promotion.py
git commit -m "feat(etkl): promote.emit_span_promotion — accountable proposition for a B1.3 span reading"
```

---

### Task 5: Resolution orchestrator + compile plumbing — `span.resolve_ambiguous_merge`, `compile_tables(span_proposer=...)`, end-to-end DoD

**Files:**
- Modify: `src/iladub/etkl/span.py` (add `resolve_ambiguous_merge`)
- Modify: `src/iladub/etkl/compile.py:78` (`compile_tables` signature) and `compile.py:224-230` (the `MERGE_AMBIGUOUS` branch)
- Test: `tests/etkl/test_b1_3_merge_resolution.py`

**Interfaces:**
- Consumes: `span.build_reading`, `span.flank_context` (Task 3); `promote.emit_span_promotion` (Task 4); `propose.SpanProposer` (Task 1); `tiling.region_tiles`; `holon.assert_hier_region`; `hierarchical.HierRegion`; `iladub.etkl.headers.merge_tiling_ok`.
- Produces:
  - `resolve_ambiguous_merge(graph, hreg, band, table_uri, doc_uri, page, proposer) -> tuple[int, tuple] | None` — on success returns `(asserted_token_count, (promotion_uri, ...))` and has committed the region + promotions into `graph`; returns `None` (graph untouched) when unresolved.
  - `compile_tables(pdf_path, page_number=0, validate_shapes=True, span_proposer=None)`.

**Why the resolution DoD is at the orchestrator level, not through `compile_tables`:** a narrow-flank tie needs (i) grid dilution — `infer_leaf_grid` needs ≥~48 data rows to separate the leaf columns whose gutter the spanning label's ink straddles — **and** (ii) the `header-body-split.rq` SPARQL step, which is super-linear and hangs past ~15 rows. These conflict, so **no single band drives a narrow-flank resolution through `compile_tables`** (the exact orthogonal limitation `test_span_gate.py`'s docstring documents — it is why B1.2 also tested at the tree level, not through `compile_tables`). The honest DoD therefore exercises the real `resolve_ambiguous_merge` orchestrator on a `HierRegion` assembled the same proven way (`grid` from a 60-row band, `tree`/`split`/`rows` from a 6-row band) — hitting every production path (grid inference, header tree, `build_reading`, `assert_hier_region`, `region_tiles`, `emit_span_promotion`). `compile_tables` is separately proven for the default, kw-smoke, and offcenter-escalation paths (offcenter is a 2-row band that `compile_tables` handles today). Empirically verified before writing this task: the assembled region asserts 30 tokens and **both** readings tile (`region_tiles=True`), an illegal DUP-leaf reading tiles `False`, and offcenter escalates `MERGE_AMBIGUOUS`.

- [ ] **Step 1a: Add the reusable assembled-region helper to `test_span_gate.py`**

`test_span_gate.py` builds its geometry via `_band` / `_region_node` but never assembles a `HierRegion` (it stops at tree inspection). Add a module-level helper and the two imports it needs (append to the existing `from iladub.etkl...` imports at the top of the file):

```python
from iladub.etkl.rows import logical_rows
from iladub.etkl.hierarchical import HierRegion


def _ambiguous_hier_region():
    """Assemble the narrow-orphan HierRegion the way _region_node does: grid from a 60-row band
    (dilution infer_leaf_grid needs) + tree/split/rows from a 6-row band (header-body-split.rq is
    super-linear -> must run on the small band). Returns (hreg, small_band). classify_hierarchical
    CANNOT be used here: it runs recover_leaf_grid on ONE band, which won't resolve 5 columns
    without the 48+-row dilution. Empirically: assert_hier_region asserts 30 tokens; both readings
    tile."""
    grid = infer_leaf_grid(_band(25, False, 60))
    assert grid.ncols == 5
    small = _band(25, False, 6)
    split = header_body_split(small, grid)
    tree = infer_header_tree(small, grid, split)
    rows = logical_rows(small, grid, small.lines[split].top)
    return HierRegion(grid, tree, rows, split), small
```

Run `./.venv/bin/python -m pytest tests/etkl/test_span_gate.py -v` — confirm the existing two tests still pass (pure addition).

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_b1_3_merge_resolution.py
import os
from dataclasses import replace
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from rdflib import Graph, RDF, URIRef, Namespace
from iladub.etkl import compile_tables
from iladub.etkl.propose import SpanProposal, FakeSpanProposer
from iladub.etkl.span import build_reading, resolve_ambiguous_merge
from iladub.etkl.headers import HeaderNode
from iladub.etkl.holon import assert_hier_region
from iladub.etkl.tiling import region_tiles
from tests.etkl.test_span_gate import _ambiguous_hier_region
from tests.etkl import fixtures as F

ILADUB = Namespace("https://w3id.org/iladub#")


def _reasons(rep):
    return [r.reason for r in rep.regions]


def test_narrow_orphan_resolves_to_asserted_with_promotion():
    # a proposer picks the standalone reading (a legal tiling) -> MERGE_AMBIGUOUS flips to asserted,
    # carrying a PromotionDecision proposition (§3). Both readings are legal for a genuine tie.
    hreg, band = _ambiguous_hier_region()
    assert any(n.ambiguous_flank is not None for n in hreg.tree), "fixture must produce a narrow-flank tie"
    g = Graph()
    fp = FakeSpanProposer(SpanProposal("standalone", 0.8, "flank reads standalone"))
    out = resolve_ambiguous_merge(g, hreg, band, URIRef("urn:doc#htable0"), URIRef("urn:doc"), 0, fp)
    assert out is not None, "a legal reading must resolve"
    n_asserted, promos = out
    assert n_asserted > 0 and len(promos) >= 1
    assert list(g.subjects(RDF.type, ILADUB.PromotionDecision)), "resolution must record a promotion"


def test_no_proposer_stays_escalated():
    # an abstaining proposer -> no resolution (graph untouched, caller escalates)
    hreg, band = _ambiguous_hier_region()
    out = resolve_ambiguous_merge(Graph(), hreg, band, URIRef("urn:doc#htable0"),
                                  URIRef("urn:doc"), 0, FakeSpanProposer(None))
    assert out is None, "an abstaining proposer must not resolve"


def test_illegal_reading_rejected_by_oracle():
    # the load-bearing guard: a reading whose scratch region violates tiling is refused by
    # region_tiles regardless of confidence -> legality gates admission, not confidence.
    hreg, band = _ambiguous_hier_region()
    amb = next(i for i, n in enumerate(hreg.tree) if n.ambiguous_flank is not None)
    flank = hreg.tree[amb].ambiguous_flank
    # deliberately-illegal: a second level-0 leaf over the flank -> two leaf headers for one column
    bad = list(build_reading(hreg.tree, amb, flank, "standalone"))
    bad.append(HeaderNode(0, (flank,), "DUP", None))
    bad_region = replace(hreg, tree=tuple(bad))
    scratch = Graph()
    assert_hier_region(scratch, bad_region, band, URIRef("urn:doc#bad"), URIRef("urn:doc"), 0)
    assert region_tiles(scratch) is False, "overlapping leaf access must fail the tiling oracle"


def test_offcenter_overlap_never_enters_resolution(tmp_path):
    # a genuine overlap collision (no ambiguous_flank) stays escalated even WITH a proposer present
    p = os.path.join(str(tmp_path), "offcenter.pdf"); F.offcenter_merge_report_pdf(p)
    rep = compile_tables(p, span_proposer=FakeSpanProposer(SpanProposal("absorb", 0.99, "x")))
    assert "MERGE_AMBIGUOUS" in _reasons(rep), _reasons(rep)


def test_compile_tables_accepts_span_proposer_kw(tmp_path):
    # signature smoke: the new optional kw exists and the default path is unchanged
    p = os.path.join(str(tmp_path), "simple.pdf"); F.simple_table_pdf(p)
    rep = compile_tables(p)                       # no kw -> today's behaviour
    assert "asserted" in [r.verdict for r in rep.regions]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_b1_3_merge_resolution.py -v`
Expected: FAIL — `ImportError: cannot import name 'resolve_ambiguous_merge'` (and `compile_tables()` has no `span_proposer` kw).

- [ ] **Step 3: Write minimal implementation**

Append `resolve_ambiguous_merge` to `src/iladub/etkl/span.py`:

```python
def resolve_ambiguous_merge(graph, hreg, band, table_uri, doc_uri, page, proposer):
    """NEURAL propose -> SHACL-oracle dispose -> promote for a narrow-flank merge tie (B1.3).

    For each header node B1.2 flagged with an `ambiguous_flank`, ask the proposer for a reading,
    build that reading, and tile-check it on a scratch graph (region_tiles). ALL flagged nodes
    must resolve legally, or the whole region stays escalated (return None, graph untouched).
    On success, commit the (last) legal reading's region + one promotion per resolved flank into
    `graph` and return (asserted_token_count, (promotion_uri, ...)).

    Legality gates admission — never confidence: a proposal whose scratch region fails region_tiles
    is refused regardless of proposal.confidence."""
    from dataclasses import replace
    from rdflib import Graph
    from .holon import assert_hier_region
    from .tiling import region_tiles
    from .promote import emit_span_promotion

    flagged = [i for i, n in enumerate(hreg.tree) if n.ambiguous_flank is not None]
    if not flagged:
        return None                                  # not a narrow-flank tie -> caller escalates

    tree = hreg.tree
    promos = []
    for idx in flagged:
        flank = tree[idx].ambiguous_flank
        proposal = proposer.propose_header_span(flank_context(tree, idx, flank))
        if proposal is None or proposal.choice not in ("absorb", "standalone"):
            return None                              # abstain / malformed -> escalate
        tree = build_reading(tree, idx, flank, proposal.choice)
        promos.append((idx, flank, proposal))

    reading = replace(hreg, tree=tree)
    scratch = Graph()
    n = assert_hier_region(scratch, reading, band, table_uri, doc_uri, page)
    if n <= 0 or not region_tiles(scratch):
        return None                                  # illegal reading -> oracle refuses -> escalate

    graph += scratch
    promo_uris = tuple(
        emit_span_promotion(graph, table_uri, hreg.tree[idx].text, flank, prop.choice, prop)
        for idx, flank, prop in promos
    )
    return n, promo_uris
```

Modify `compile_tables` signature in `src/iladub/etkl/compile.py` (line 78 region):

```python
def compile_tables(pdf_path: str, page_number: int = 0, validate_shapes: bool = True,
                   span_proposer=None) -> "CompilationReport":
```

Replace the `MERGE_AMBIGUOUS` branch (`compile.py:224-230`) with the resolution-then-escalate flow:

```python
                if hreg is not None and not merge_tiling_ok(hreg.tree, hreg.grid):
                    resolved = None
                    if span_proposer is not None:
                        from .span import resolve_ambiguous_merge
                        table_uri = URIRef(f"{_DOC}#htable{idx}")
                        resolved = resolve_ambiguous_merge(
                            graph, hreg, band, table_uri, _DOC, page_number, span_proposer)
                    if resolved is not None:
                        n, _promos = resolved
                        tokens = sum(len(ln.words) for ln in band.lines)
                        asserted_total += n
                        escalated_total += max(0, tokens - n)
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.HierarchicalTable), ascii_view))
                    else:
                        cand_uri = URIRef(f"{_DOC}#region{idx}")
                        escalate_region(graph, cand_uri, _DOC, ascii_view, "MERGE_AMBIGUOUS",
                                        TAB.HierarchicalTable, 0.4)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        reports.append(RegionReport(region.kind, "escalated", 0, "MERGE_AMBIGUOUS",
                                                    str(TAB.HierarchicalTable), ascii_view))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_b1_3_merge_resolution.py -v`
Expected: PASS (5 passed). Both `standalone` and `absorb` tile for this fixture (empirically verified while writing this plan), so the `standalone` proposal resolves. Do NOT tune any pipeline constant (§8) if anything is off — inspect `region_tiles(scratch)` on each reading directly and pin the test to a legal one; the two readings are the only degrees of freedom.

- [ ] **Step 5: RED-check the resolution is non-vacuous**

Temporarily make `resolve_ambiguous_merge` return `None` unconditionally (add `return None` as its first line), run `./.venv/bin/python -m pytest tests/etkl/test_b1_3_merge_resolution.py::test_narrow_orphan_resolves_to_asserted_with_promotion -v`, and confirm it now FAILS (`out is None` → the assert trips). Revert the temporary line and re-run to confirm PASS.

- [ ] **Step 6: Run the full etkl suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/etkl -q`
Expected: all pass — every shipped `test_headers` / `test_hierarchical` / `test_merge_resolution` / `test_span_gate` fixture stays green (default `span_proposer=None` path unchanged), plus the new B1.3 tests.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/span.py src/iladub/etkl/compile.py tests/etkl/test_b1_3_merge_resolution.py tests/etkl/test_span_gate.py
git commit -m "feat(etkl): B1.3 resolve_ambiguous_merge + compile span_proposer seam — NEURAL propose->tile-oracle->promote (DoD)"
```

---

## Self-Review

**Spec coverage:**
- `SpanProposer` seam (SpanProposal / Protocol / Fake / Baml) → Task 1. ✓
- Tie carry-through (`ambiguous_flank`) → Task 2. ✓
- Candidate-reading builder + proposer context → Task 3. ✓
- Span-promotion emitter (CandidateConcept + PromotionDecision, tie rationale) → Task 4. ✓
- Oracle reuse (`region_tiles`) + resolution orchestrator + compile plumbing (`span_proposer=None`) → Task 5. ✓
- Four behavioural pins: resolves (T5 test 1 + RED-check), abstains→escalates (T5 test 2 + no-kw smoke test 5), illegal→oracle-refuses (T5 test 3), overlap-collision-stays-escalated (T5 test 4). ✓
- Anti-overfit / zero tuned constant → Global Constraints + T5 Step 4 note + illegal-reading guard. ✓
- Scope boundary (only narrow-orphan; overlap out; B2 later) → Global Constraints + T5 test 4. ✓
- Live BAML env-gated, never on test path → Task 1 (`BamlSpanProposer`), all tests inject `FakeSpanProposer`. ✓

**Placeholder scan:** none — every step has full code + exact commands.

**Type consistency:** `SpanProposal(choice, confidence, rationale, suggester_iri)`, `SpanProposer.propose_header_span(context)->SpanProposal|None`, `build_reading(tree, node_idx, flank, choice)->tuple[HeaderNode,...]`, `flank_context(tree, node_idx, flank)->dict`, `emit_span_promotion(g, region_uri, node_text, flank, choice, proposal)->URIRef`, `resolve_ambiguous_merge(graph, hreg, band, table_uri, doc_uri, page, proposer)->tuple[int,tuple]|None`, and `HeaderNode(..., ambiguous, ambiguous_flank)` are used identically across tasks. `compile_tables(pdf_path, page_number, validate_shapes, span_proposer)` matches the shipped signature plus the new kw. ✓

**Note (carried, not blocking):** `header-body-split.rq` is super-linear in band row count (documented in the B1.2 spec §2.7). If the B1.3 pipeline test's band is large this could be slow; `_ambiguous_band()` already uses the small-band construction from `test_span_gate.py`, so this is avoided.
