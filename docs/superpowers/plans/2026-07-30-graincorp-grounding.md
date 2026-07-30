# GrainCorp Grounding Implementation Plan (Loop K)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Records gain their recovered group keys as groundable SurfaceConcepts (with page provenance), blank placeholders stop minting noise, and a committed illustrative shipping-stem contract lets the real document ground end-to-end through the shipped `ground_concept` — grounded nodes behind PromotionDecisions, the rest honestly quarantined.

**Architecture:** Two feed changes in `table_records` (blank-drop, group-key injection); a three-file contract under `examples/shipping/` following the transplant conventions exactly; zero changes to `ground.py`. Committed tests are fully offline (exact-match grounding + abstaining proposer).

**Tech Stack:** Python 3 + rdflib, pySHACL (via the shipped `_value_conforms`), pytest, Turtle. Spec: `docs/superpowers/specs/2026-07-30-graincorp-grounding-design.md`.

## Global Constraints

- **Zero changes to `src/iladub/ground.py`** — this loop adds a contract and feed enrichment, never grounding logic.
- Blank recognition reuses `iladub.etkl.celltype.is_blank` — never a second marker list. The literal string `'Blank'` is NOT a marker and must keep flowing through (it quarantines).
- Injection is driven by **column identity**, never by text matching; injected only where the record has no non-blank concept at that column; at most once per column.
- Contract patterns/`sh:in` sets are contract-author declarations (the PR #55 soundness relocation), not tuned constants — they live ONLY in `examples/shipping/stem-shapes.ttl`.
- Contract property local names: `port`, `commodity`, `status`, `total`, `month` — chosen so `exact_field`'s normalization matches the real header texts; committed tests need NO proposer proposals (abstaining proposer only).
- Shipped transplant/offer feed + grounding tests must stay byte-identical in outcome.
- Never commit the GrainCorp PDF; the capstone measurement is Task 3, controller-run, recorded in docs only.
- Canonical test command: `. .venv/bin/activate && python3 -m pytest -q <paths>` from repo root, FOREGROUND. Full suite ~180 s, timeout ≥ 400000 ms. Baseline: 677 passed / 5 skipped.

## File Structure

- Modify: `src/iladub/feed.py` (`table_records` only)
- Create: `examples/shipping/stem-contract.ttl`, `examples/shipping/stem-terms.ttl`, `examples/shipping/stem-shapes.ttl`
- Create: `tests/test_feed_group_keys.py` (feed units), `tests/test_stem_contract.py` (contract units + PDF E2E)

---

### Task 1: Feed — blank-drop + group-key injection

**Files:**
- Modify: `src/iladub/feed.py` (the cell loop and record minting inside `table_records`, ~lines 38-70)
- Test: `tests/test_feed_group_keys.py` (create)

**Interfaces:**
- Consumes: `celltype.is_blank(s) -> bool`; the loop I graph shape (`tab:DerivedRowGroup` nodes with `hasLabel` → an EntryCell carrying `atColumn`/`cellText`/`hasBBox`/`prov:wasDerivedFrom`, `coversRow` → row URIs); `_column_header_path`, `_bbox_xy`, `SurfaceConcept`.
- Produces: no signature change — `table_records(graph) -> list[Record]`, records enriched.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_feed_group_keys.py`:

```python
"""Loop K — the feed carries recovered group keys to the grounding portal, and blank
placeholder cells stop minting noise propositions.

Injection is column-identity-driven (never text): a record gains one SurfaceConcept per
covering DerivedRowGroup whose column it does not already populate, valued with the group
key and provenanced to the SOURCE cell the key came from (§5/§6). Blank cells
(celltype.is_blank — loop A's one owned convention) are dropped; the literal string
'Blank' is NOT a marker and flows through to honest quarantine.
See docs/superpowers/specs/2026-07-30-graincorp-grounding-design.md.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.feed import table_records

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
T = URIRef("urn:doc#h0")


def _table(g, headers, rows):
    """Minimal HierarchicalTable in the holon emission shape. headers: list of column
    label texts (index = column). rows: {row_index: {col_index: text}}."""
    g.add((T, RDF.type, TAB.HierarchicalTable))
    for c, htext in enumerate(headers):
        cu = URIRef(f"{T}-c{c}")
        h = URIRef(f"{T}-h{c}")
        lc = URIRef(f"{T}-hl{c}")
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((T, TAB.hasHeaderNode, h))
        g.add((h, TAB.coversColumn, cu))
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((lc, TAB.cellText, Literal(htext)))
        g.add((h, TAB.hasLabel, lc))
    for r, cols in rows.items():
        ru = URIRef(f"{T}-r{r}")
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((T, TAB.hasLeafRow, ru))
        for c, text in cols.items():
            e = URIRef(f"{T}-e{r}_{c}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((T, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru))
            g.add((e, TAB.atColumn, URIRef(f"{T}-c{c}")))
            g.add((e, TAB.cellText, Literal(text)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(50.0 * c, datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"urn:doc#p0-{50 * c}-{10 * r}")))


def _group(g, i, label_cell, member_rows):
    grp = URIRef(f"{T}-rg{i}")
    g.add((grp, RDF.type, TAB.HeaderNode))
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((T, TAB.hasHeaderNode, grp))
    g.add((grp, TAB.hasLabel, URIRef(f"{T}-{label_cell}")))
    g.add((grp, PROV.wasDerivedFrom, URIRef(f"{T}-r{i}")))
    for m in member_rows:
        g.add((grp, TAB.coversRow, URIRef(f"{T}-r{m}")))
    return grp


def _by_row(recs):
    return {r.row_id.split(">")[-1].strip(): {c.text: c.value for c in r.concepts}
            for r in recs}


def test_suppressed_key_is_injected_with_source_provenance():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {1: "Mackay", 2: "150"}})                       # Month suppressed on r1
    _group(g, 9, "e0_0", (0, 1))                               # month group keyed at r0c0
    recs = table_records(g)
    concepts = {r.row_id: r.concepts for r in recs}
    r1 = [r for r in recs if "r1" in r.row_id][0]
    month = [c for c in r1.concepts if c.text == "Month"]
    assert len(month) == 1 and month[0].value == "Jul"
    assert month[0].region == "p0-0-0"                         # the SOURCE cell's fragment
    r0 = [r for r in recs if r.row_id.endswith("r0") or "r0" in r.row_id][0]
    assert sum(1 for c in r0.concepts if c.text == "Month") == 1   # r0: own cell, no dupe


def test_occupied_column_is_never_duplicated():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {1: "Mackay", 2: "150"}})
    _group(g, 8, "e0_1", (0, 1))                               # PORT group; both rows have Port
    recs = table_records(g)
    for r in recs:
        assert sum(1 for c in r.concepts if c.text == "Port") == 1, r.concepts


def test_nested_groups_sharing_a_label_cell_inject_once():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"], {0: {1: "Mackay", 2: "100"}})
    _group(g, 7, "e0_1", (0,))
    _group(g, 8, "e0_1", (0,))                                 # same label cell, same column
    recs = table_records(g)
    # r0's own Port cell occupies the column: zero injections, still exactly one Port
    assert sum(1 for c in recs[0].concepts if c.text == "Port") == 1


def test_blank_cells_are_dropped_but_do_not_block_injection():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {0: "(blank)", 1: "Mackay", 2: "-"}})           # blank Month AND blank Qty
    _group(g, 9, "e0_0", (0, 1))
    recs = table_records(g)
    r1 = [r for r in recs if "r1" in r.row_id][0]
    texts = {c.text: c.value for c in r1.concepts}
    assert texts.get("Month") == "Jul"                         # injected THROUGH the blank
    assert "Qty" not in texts                                  # blank dropped, nothing injected
    assert all(c.value not in ("(blank)", "-") for c in r1.concepts)


def test_literal_Blank_string_is_not_a_marker():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"], {0: {0: "Jul", 1: "Blank", 2: "100"}})
    recs = table_records(g)
    assert {c.text: c.value for c in recs[0].concepts}["Port"] == "Blank"


def test_all_blank_row_mints_no_record():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {0: "(blank)", 1: "-", 2: ""}})
    assert len(table_records(g)) == 1


def test_injected_concept_sorts_by_its_column_position():
    g = Graph()
    _table(g, ["Month", "Port", "Qty"],
           {0: {0: "Jul", 1: "Mackay", 2: "100"},
            1: {1: "Mackay", 2: "150"}})
    _group(g, 9, "e0_0", (0, 1))
    r1 = [r for r in table_records(g) if "r1" in r.row_id][0]
    assert [c.text for c in r1.concepts] == ["Month", "Port", "Qty"]
```

- [ ] **Step 2: Run to verify failure**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_feed_group_keys.py -q`
Expected: FAIL (no injection, blanks present).

- [ ] **Step 3: Implement in `table_records`**

Inside the per-table loop of `src/iladub/feed.py::table_records`:

(a) **Blank-drop + occupancy tracking** — in the cell loop, after reading the cell text,
skip blanks and track occupied columns:

```python
        from .etkl.celltype import is_blank
        rows: dict = {}
        row_cols: dict = {}
        for e in graph.subjects(RDF.type, TAB.EntryCell):
            if (t, TAB.hasCell, e) not in graph:
                continue
            row = graph.value(e, TAB.atRow)
            if row is not None and (row, RDF.type, TAB.AggregationRow) in graph:
                continue          # a subtotal is not a record (§7): its cells mint no subject
            col = graph.value(e, TAB.atColumn)
            txt = str(graph.value(e, TAB.cellText))
            if is_blank(txt):
                continue          # loop K: a placeholder has no content to ground — dropping
                                  # it also leaves the column OPEN for group-key injection
            prov = graph.value(e, PROV.wasDerivedFrom)
            region = str(prov).split("#")[-1] if prov is not None else str(e).split("#")[-1]
            concept = SurfaceConcept(header.get(col, ""), txt, region)
            x0, y0 = _bbox_xy(graph, e)
            rows.setdefault(row, []).append((x0, y0, concept))
            row_cols.setdefault(row, set()).add(col)
```

(b) **Group-key injection** — immediately after the cell loop, before the ordering/minting
code:

```python
        # Loop K: recovered group keys become groundable concepts. A suppressed key (the
        # author writes Month once per group) never appears among the row's own cells; the
        # derived row group carries it with provenance to the SOURCE cell (§5/§6 — context
        # is carried, to the page). Column-identity-driven, injected only where the record
        # has no non-blank concept at that column, once per column (nested groups can share
        # one label cell). The y-sort key is the ROW's own extent, not the source cell's,
        # so record ordering is untouched.
        for h in graph.objects(t, TAB.hasHeaderNode):
            if (h, RDF.type, TAB.DerivedRowGroup) not in graph:
                continue
            label = graph.value(h, TAB.hasLabel)
            col = graph.value(label, TAB.atColumn) if label is not None else None
            if col is None:
                continue
            key = str(graph.value(label, TAB.cellText))
            prov = graph.value(label, PROV.wasDerivedFrom)
            region = str(prov).split("#")[-1] if prov is not None else str(label).split("#")[-1]
            x0, _ = _bbox_xy(graph, label)
            for row in graph.objects(h, TAB.coversRow):
                if row not in rows or col in row_cols.get(row, set()):
                    continue
                own_y = min(y for _, y, _ in rows[row])
                rows[row].append((x0, own_y, SurfaceConcept(header.get(col, ""), key, region)))
                row_cols.setdefault(row, set()).add(col)
```

The existing ordering/collision-guard/minting code below stays untouched.

- [ ] **Step 4: Run the new tests + the shipped feed tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_feed_group_keys.py tests/test_concept_feed.py tests/etkl/test_row_groups.py tests/etkl/test_aggregation_rows.py -q`
Expected: ALL PASS. If a shipped concept-feed test fails, the blank-drop or occupancy
change leaked into a fixture without blanks/groups — find out why before touching any test.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/feed.py tests/test_feed_group_keys.py
git commit -m "feat(feed): group-key injection + blank-drop — recovered keys reach the grounding portal (loop K)"
```

---

### Task 2: The shipping-stem contract + grounding tests

**Files:**
- Create: `examples/shipping/stem-contract.ttl`, `examples/shipping/stem-terms.ttl`, `examples/shipping/stem-shapes.ttl`
- Test: `tests/test_stem_contract.py` (create)

**Interfaces:**
- Consumes: `ground.load_contract(path)`, `ground.ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g)`, `SurfaceConcept`; `propose_ground.FakeGroundingProposer` (find the ABSTAIN form used by shipped tests: `grep -n "FakeGroundingProposer" tests/test_grounding.py` — mirror it); Task 1's enriched `table_records` + `ground_document`.
- Produces: the three example files; no code.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_stem_contract.py`:

```python
"""Loop K — the illustrative shipping-stem contract: the real document's vocabulary,
verified by the SHIPPED ground_concept (zero new grounding logic). Scheme membership
(commodity, port), sh:in (status), sh:pattern (total, month) ground; everything else —
vessels, 'TBA', the literal 'Blank' — quarantines honestly (§7). All offline: property
local names match the normalized header texts, so the exact-match path decides and the
proposer only ever abstains."""
import pytest

from rdflib import Graph, Namespace, RDF, URIRef

from iladub.ground import SurfaceConcept, ground_concept, load_contract

ILADUB = Namespace("https://w3id.org/iladub#")
C = "examples/shipping/stem-contract.ttl"
TERMS = "examples/shipping/stem-terms.ttl"
SHAPES = "examples/shipping/stem-shapes.ttl"


def _ground(field_text, value):
    contract = load_contract(C)
    terms = Graph().parse(TERMS, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    g = Graph()
    # mirror the abstaining-proposer construction the shipped grounding tests use
    from tests.test_grounding import ABSTAIN            # adjust: reuse the shipped helper
    verdict = ground_concept(SurfaceConcept(field_text, value, "p0-x-y"), contract,
                             URIRef("urn:slot#s1"), ABSTAIN, terms, shapes, g)
    return verdict, g


def test_contract_loads_five_fields_two_schemes():
    c = load_contract(C)
    assert len(c.fields) == 5
    assert sum(1 for f in c.fields if f.scheme) == 2           # commodity, port


@pytest.mark.parametrize("field,value", [
    ("Commodity", "Sorghum"), ("Port", "Mackay"),
    ("Status", "Accepted"), ("Total", "25,000"), ("Month", "Aug 26")])
def test_verifiable_values_ground(field, value):
    verdict, g = _ground(field, value)
    assert verdict == "grounded", (field, value, verdict)
    assert (None, RDF.type, ILADUB.PromotionDecision) in g     # accountable admission


@pytest.mark.parametrize("field,value", [
    ("Commodity", "Vibranium"), ("Status", "Perhaps"),
    ("Total", "TBA"), ("Total", "Blank"), ("Month", "sometime"),
    ("Name Of Ship", "STAR EXPRESS")])                          # no contract field at all
def test_unverifiable_values_quarantine(field, value):
    verdict, g = _ground(field, value)
    assert verdict != "grounded", (field, value, verdict)
    assert (None, RDF.type, ILADUB.CandidateConcept) in g      # never dropped, never faked


def test_e2e_fixture_records_ground_offline(tmp_path):
    import os
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.compile import compile_tables
    from iladub.feed import ground_document
    from tests.etkl import fixtures as F
    from tests.test_grounding import ABSTAIN                    # adjust as above
    p = os.path.join(str(tmp_path), "sub.pdf")
    F.subtotal_hier_table_pdf(p)
    rep = compile_tables(p)
    contract = load_contract(C)
    terms = Graph().parse(TERMS, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    g = Graph()
    res = ground_document(rep.graph, contract, ABSTAIN, terms, shapes, g)
    assert res.records == 3                                     # the subtotal mints none
    # the fixture's 'Port' column values are in the port scheme -> ground; the rest quarantine
    assert res.grounded >= 2 and res.proposed > 0
    assert (None, RDF.type, ILADUB.PromotionDecision) in g
```

IMPORTANT — two find-first items for the implementer:
1. The abstaining proposer: `grep -n "FakeGroundingProposer\|GroundingProposal(" tests/test_grounding.py src/iladub/propose_ground.py` and reuse the shipped abstain construction (import it if it is a module-level helper; otherwise build the same `GroundingProposal` inline and drop the `from tests.test_grounding import ABSTAIN` lines). Do NOT invent a new proposer class.
2. `ground_concept`'s verdict return values: check its docstring/returns ("grounded" vs "proposed" strings or similar) and pin the ACTUAL values.
3. The fixture E2E's `Port` values are 'Mackay'/'Gladstone' — both must be in the port scheme for the `grounded >= 2` bound; 'Qty' values ('100'/'150'/'300') do NOT match the grouped-total pattern `^[0-9]{1,3}(,[0-9]{3})*$`... they DO match (1-3 digits, zero comma groups). Verify against the real regex behavior and adjust the bound to the measured count, asserting an exact number once measured.

- [ ] **Step 2: Run to verify failure**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_stem_contract.py -q`
Expected: FAIL (files missing).

- [ ] **Step 3: Author the three example files**

`examples/shipping/stem-contract.ttl`:

```turtle
@prefix ship: <https://example.org/shipping#> .
@prefix etkl: <https://w3id.org/iladub/etkl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Illustrative semantic data contract for a public shipping-stem slot table (loop K).
# Declares ONLY what it can verify: two SKOS schemes, one sh:in, two sh:pattern fields.
# Vessels, exporters, dates and times carry no verifiable constraint by design — they
# quarantine as CandidateConcepts (§7: credibility over completeness).
ship:stem-contract a etkl:SemanticDataContract ;
    rdfs:label "Shipping stem slot"@en ;
    etkl:targetClass ship:ShippingSlot ;
    etkl:requiresKnowledge ship:scheme-commodity , ship:scheme-port ;
    etkl:hasField ship:f-commodity , ship:f-port , ship:f-status , ship:f-total , ship:f-month .

ship:f-commodity a etkl:Field ; etkl:fillsProperty ship:commodity ; etkl:admissibleScheme ship:scheme-commodity .
ship:f-port      a etkl:Field ; etkl:fillsProperty ship:port ;      etkl:admissibleScheme ship:scheme-port .
ship:f-status    a etkl:Field ; etkl:fillsProperty ship:status .
ship:f-total     a etkl:Field ; etkl:fillsProperty ship:total .
ship:f-month     a etkl:Field ; etkl:fillsProperty ship:month .
```

`examples/shipping/stem-terms.ttl`:

```turtle
@prefix ship: <https://example.org/shipping#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

ship:scheme-commodity a skos:ConceptScheme ; skos:prefLabel "Grain commodities"@en .
ship:c-wheat    a skos:Concept ; skos:inScheme ship:scheme-commodity ; skos:prefLabel "Wheat"@en .
ship:c-sorghum  a skos:Concept ; skos:inScheme ship:scheme-commodity ; skos:prefLabel "Sorghum"@en .
ship:c-chickpeas a skos:Concept ; skos:inScheme ship:scheme-commodity ; skos:prefLabel "Chickpeas"@en .
ship:c-barley   a skos:Concept ; skos:inScheme ship:scheme-commodity ; skos:prefLabel "Barley"@en .
ship:c-canola   a skos:Concept ; skos:inScheme ship:scheme-commodity ; skos:prefLabel "Canola"@en .

ship:scheme-port a skos:ConceptScheme ; skos:prefLabel "Export ports"@en .
ship:p-mackay     a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Mackay"@en .
ship:p-gladstone  a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Gladstone"@en .
ship:p-carrington a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Carrington"@en .
ship:p-geelong    a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Geelong"@en .
ship:p-fisherman  a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Fisherman Islands"@en .
ship:p-kembla     a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Port Kembla"@en .
ship:p-portland   a skos:Concept ; skos:inScheme ship:scheme-port ; skos:prefLabel "Portland"@en .
```

`examples/shipping/stem-shapes.ttl`:

```turtle
@prefix ship: <https://example.org/shipping#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

# Value membrane for the stem contract (closed world — what may cross into the clean
# holon). Patterns and the sh:in list are CONTRACT-AUTHOR DECLARATIONS (the PR #55
# soundness relocation): the contract owns per-field verification strength.
ship:ShippingSlotShape a sh:NodeShape ;
    sh:targetClass ship:ShippingSlot ;
    sh:property [ sh:path ship:status ;
        sh:in ( "Accepted" "Received" "Nominated" ) ] ;
    sh:property [ sh:path ship:total ;
        sh:pattern "^[0-9]{1,3}(,[0-9]{3})*$" ] ;
    sh:property [ sh:path ship:month ;
        sh:pattern "^[A-Z][a-z]{2} [0-9]{2}$" ] .
```

(If the GrainCorp Status column carries values outside this list, they quarantine — that
is the design, not a bug. Task 3 measures the real distribution.)

- [ ] **Step 4: Run the tests, fix the find-first items, measure the E2E counts**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_stem_contract.py tests/test_grounding.py -q`
Expected: PASS after resolving the abstain-proposer import and pinning measured E2E counts.
`tests/test_grounding.py` must be untouched and green.

- [ ] **Step 5: Commit**

```bash
git add examples/shipping tests/test_stem_contract.py
git commit -m "feat(examples): illustrative shipping-stem contract — schemes, sh:in, patterns; offline grounding tests (loop K)"
```

---

### Task 3: Capstone measurement + docs (controller-run; needs the local GrainCorp PDF)

**Files:**
- Modify: `docs/superpowers/specs/2026-07-30-graincorp-grounding-design.md` (status), `docs/superpowers/residues.md`

- [ ] **Step 1: Ground the real document**

Compile the stem (recorded row-role vector), run `ground_document` with the stem contract,
terms, shapes and the abstaining proposer. Measure and record:
- records; grounded; proposed (quarantined) counts;
- injected Month/Season concepts present and Month values grounding via the pattern;
- `#PromotionDecision == #GroundedNode` (every admission accountable);
- Status value distribution vs the sh:in list (adjust NOTHING — record the honest split);
- score/cells still 0.9496/509 (compile untouched).

- [ ] **Step 2: Full suite** — expect 677 + new tests, 5 skipped.

- [ ] **Step 3: Docs** — spec status → Shipped with the measured tallies; register: add the
  "unconstrained fields stay propositions" note with counts (a design property, recorded
  once, not per-loop); ledger updated.

- [ ] **Step 4: Commit docs.**

---

## Self-Review

- **Spec coverage:** §2.1 → Task 1; §2.2 → Task 2 Step 3; §1.3/§1.4 criteria → Task 2
  tests; §1.6 capstone → Task 3; §1.5 shipped-fixture guard → Task 1 Step 4 + Task 2
  Step 4 running the shipped suites.
- **Placeholder scan:** the three find-first items in Task 2 carry explicit grep/measure
  instructions instead of guessed values (abstain construction, verdict strings, E2E
  counts) — deliberate, per the fixture-probing lesson.
- **Type consistency:** `SurfaceConcept(text, value, region)` used identically in feed and
  tests; `table_records` signature unchanged; contract vocabulary matches
  `load_contract`'s reader (`targetClass`/`hasField`/`fillsProperty`/`admissibleScheme`).
