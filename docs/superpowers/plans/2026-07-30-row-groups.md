# Row Groups from Confirmed Aggregations — Implementation Plan (Loop I)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Derive the Month > Port row-group tree from Loop H's confirmed aggregation rows so records carry their group identity (`Jul 26 > Mackay`), with a feed collision guard so same-group rows never merge.

**Architecture:** A SPARQL key/nesting derivation (AXIOM) over the emitted table graph, run from `assert_hier_region` inside the loop G scratch backstop; group nodes reuse the shipped `coversRow` row-header vocabulary with `hasLabel` pointing at the source EntryCell (provenance for free); a new subclass-targeted membrane shape plus a scoping fix to the two row-tiling triggers (derived groups are annotations, not a claimed partition).

**Tech Stack:** Python 3 + rdflib (SPARQL with `initBindings`), pySHACL membrane, pytest. Spec: `docs/superpowers/specs/2026-07-30-row-groups-design.md`.

## Global Constraints

- §8 gate: the group decision is an **AXIOM** (SPARQL derivation, open world); the only closed-world elements (key uniqueness, strict containment, no-intermediate) are query-local `NOT EXISTS` guards inside the one table holon. Python is engine glue only (bindings, triple merge, parent-walk) — the `interpret.run` pattern.
- **No numeric literal in any `.rq`** (the transform-gate rule). Column/row identities arrive as bindings; ordering uses data (`tab:y0`).
- **No language matching:** keys are read positionally from member cells; aggregation label text is never parsed (`'Jul 26 Total'` is never split).
- **§7:** no unique non-blank key → NO group (honest refusal). Conflicting keys refuse. Blank markers (`-`) are not special-cased in the query — a `-` key value simply conflicts or stands like any text; refusal is the safe direction.
- **Structural loop — FAILURE condition:** GrainCorp score/cells must be UNCHANGED at 0.9496/509. Any delta means the loop leaked into assertion accounting.
- **Row-shape scoping is load-bearing:** `RowCoverageShape` / `UnambiguousRowAccessShape` must keep firing for authored row trees (row-hier / matrix paths emit plain `tab:HeaderNode`s) and must NOT fire for tables whose only row headers are `tab:DerivedRowGroup`s (partial coverage is their honest shape).
- Canonical test command: `. .venv/bin/activate && python3 -m pytest -q` from repo root (bare python3 = wrong rdflib). Full suite ~170 s — run FOREGROUND with a long timeout. Baseline: 650 passed, 5 skipped.
- Never commit the GrainCorp PDF (third-party, lives outside the repo).
- Do not edit HGA namespaces; all new terms live in `tab:` (owned).

## File Structure

- Create: `vocab/queries/row-group-key.rq` — per-aggregation key derivation (SELECT).
- Create: `vocab/queries/row-group-nesting.rq` — containment nesting (SELECT pairs).
- Create: `src/iladub/etkl/rowgroups.py` — `derive_row_groups(g, table_uri, agg)` glue.
- Create: `tests/etkl/test_row_groups.py` — derivation + membrane + feed + E2E tests.
- Modify: `vocab/ontology/tab.ttl` — `tab:DerivedRowGroup ⊑ tab:HeaderNode`.
- Modify: `vocab/shapes/tab-shapes.ttl` — `tab:DerivedRowGroupShape` + trigger scoping in `RowCoverageShape` / `UnambiguousRowAccessShape`.
- Modify: `src/iladub/etkl/tiling.py` — eleventh shape IRI (+ docstring counts).
- Modify: `src/iladub/etkl/holon.py` — call `derive_row_groups` at the end of `assert_hier_region`.
- Modify: `src/iladub/feed.py` — collision guard in `table_records`.

---

### Task 1: Derivation queries + glue (`rowgroups.py`)

**Files:**
- Create: `vocab/queries/row-group-key.rq`
- Create: `vocab/queries/row-group-nesting.rq`
- Create: `src/iladub/etkl/rowgroups.py`
- Test: `tests/etkl/test_row_groups.py`

**Interfaces:**
- Consumes: the holon emission shape — `tab:EntryCell` with `tab:atRow`/`tab:atColumn`/`tab:cellText`/`tab:hasBBox → tab:y0`; aggregation rows `<table>-r{i}` with `tab:aggregates` edges; columns `<table>-c{j}`; `detect_aggregation_rows`' return `{row_index: (label_col, measure_col, members)}` (`src/iladub/etkl/rows.py`).
- Produces: `derive_row_groups(g: Graph, table_uri: URIRef, agg: dict) -> int` (number of groups constructed). Group nodes `<table>-rg{i}` typed `tab:HeaderNode` + `tab:DerivedRowGroup`, attached via `tab:hasHeaderNode`, with `tab:coversRow` per member, `tab:hasLabel` → the source EntryCell, `prov:wasDerivedFrom` → the aggregation row, `tab:parentHeader` by containment, `tab:headerLevel` = ancestor count.

- [ ] **Step 1: Write the failing tests**

Create `tests/etkl/test_row_groups.py`:

```python
"""Loop I — row groups derived from confirmed aggregations (AXIOM).

A confirmed aggregation row witnesses its group: its label column = the level, its
tab:aggregates edges = the members, and the group KEY = the unique distinct non-blank
cell value in the label column among the members. No unique value -> no group (§7).
Nesting = strict member-set containment. Keys are read positionally — label text of the
aggregation row itself is NEVER parsed (no language).
See docs/superpowers/specs/2026-07-30-row-groups-design.md.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl.rowgroups import derive_row_groups

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
T = URIRef("urn:doc#h0")


def _emit(g, rows, aggs):
    """Mirror the holon emission shape. rows: {row_index: {col_index: text}};
    aggs: {agg_row_index: member_row_indices}. y0 = 10*row (top-to-bottom order)."""
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
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
    for a, members in aggs.items():
        au = URIRef(f"{T}-r{a}")
        g.add((au, RDF.type, TAB.DetectedAggregationRow))
        for m in members:
            g.add((au, TAB.aggregates, URIRef(f"{T}-r{m}")))


def _grp(i):
    return URIRef(f"{T}-rg{i}")


def test_unique_key_builds_a_group_with_label_and_members():
    g = Graph()
    _emit(g, {0: {1: "Jul 26", 2: "Mackay", 3: "100"},
              1: {2: "Mackay", 3: "150"},
              2: {2: "Mackay Total", 3: "250"}}, {2: (0, 1)})
    n = derive_row_groups(g, T, {2: (2, 3, (0, 1))})
    assert n == 1
    grp = _grp(2)
    assert (grp, RDF.type, TAB.DerivedRowGroup) in g
    assert (grp, RDF.type, TAB.HeaderNode) in g
    assert (T, TAB.hasHeaderNode, grp) in g
    covers = set(g.objects(grp, TAB.coversRow))
    assert covers == {URIRef(f"{T}-r0"), URIRef(f"{T}-r1")}
    label = g.value(grp, TAB.hasLabel)
    assert str(g.value(label, TAB.cellText)) == "Mackay"
    assert label == URIRef(f"{T}-e0_2")          # the TOPMOST source cell (by tab:y0)
    assert g.value(grp, PROV.wasDerivedFrom) == URIRef(f"{T}-r2")


def test_conflicting_keys_refuse():
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Gladstone", 3: "150"},
              2: {2: "X Total", 3: "250"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (2, 3, (0, 1))}) == 0


def test_all_blank_keys_refuse():
    # Suppressed cells are ABSENT; an empty-text cell is also not a key.
    g = Graph()
    _emit(g, {0: {2: "", 3: "100"},
              1: {3: "150"},
              2: {0: "TOT", 3: "250"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (0, 3, (0, 1))}) == 0


def test_suppressed_key_month_shape():
    # The GrainCorp month shape: only the FIRST member carries the key in the label column.
    g = Graph()
    _emit(g, {0: {1: "Jul 26", 3: "100"},
              2: {3: "150"},
              4: {3: "200"},
              6: {1: "Jul 26 Total", 3: "450"}}, {6: (0, 2, 4)})
    n = derive_row_groups(g, T, {6: (1, 3, (0, 2, 4))})
    assert n == 1
    assert str(g.value(g.value(_grp(6), TAB.hasLabel), TAB.cellText)) == "Jul 26"


def test_nesting_by_containment_and_levels():
    # Two port groups inside one month group: parentHeader + headerLevel by ancestor count.
    g = Graph()
    _emit(g, {0: {1: "Jul", 2: "A", 3: "100"},
              1: {2: "A Total", 3: "100"},
              2: {2: "B", 3: "200"},
              3: {2: "B Total", 3: "200"},
              4: {1: "Jul Total", 3: "300"}},
          {1: (0,), 3: (2,), 4: (0, 2)})
    n = derive_row_groups(g, T, {1: (2, 3, (0,)), 3: (2, 3, (2,)), 4: (1, 3, (0, 2))})
    assert n == 3
    assert g.value(_grp(1), TAB.parentHeader) == _grp(4)
    assert g.value(_grp(3), TAB.parentHeader) == _grp(4)
    assert g.value(_grp(4), TAB.parentHeader) is None
    assert int(g.value(_grp(4), TAB.headerLevel)) == 0
    assert int(g.value(_grp(1), TAB.headerLevel)) == 1


def test_no_intermediate_skipping():
    # 3-level chain: the innermost group's parent is the MIDDLE group, never the outermost.
    g = Graph()
    _emit(g, {0: {0: "S", 1: "Jul", 2: "A", 3: "100"},
              1: {2: "A Total", 3: "100"},
              2: {1: "Jul Total", 3: "100"},
              3: {0: "S Total", 3: "100"}},
          {1: (0,), 2: (0,), 3: (0,)})
    n = derive_row_groups(g, T, {1: (2, 3, (0,)), 2: (1, 3, (0,)), 3: (0, 3, (0,))})
    assert n == 3
    # identical member sets are NOT strict containment -> no parent links at all here;
    # make the sets strictly nested instead:
    g2 = Graph()
    _emit(g2, {0: {0: "S", 1: "Jul", 2: "A", 3: "100"},
               1: {2: "A", 3: "50"},
               2: {2: "A Total", 3: "150"},
               3: {1: "Jul", 3: "10"},
               4: {1: "Jul Total", 3: "160"},
               5: {0: "S", 3: "5"},
               6: {0: "S Total", 3: "165"}},
           {2: (0, 1), 4: (0, 1, 3), 6: (0, 1, 3, 5)})
    assert derive_row_groups(
        g2, T, {2: (2, 3, (0, 1)), 4: (1, 3, (0, 1, 3)), 6: (0, 3, (0, 1, 3, 5))}) == 3
    assert g2.value(_grp(2), TAB.parentHeader) == _grp(4)     # not rg6
    assert g2.value(_grp(4), TAB.parentHeader) == _grp(6)
    assert int(g2.value(_grp(2), TAB.headerLevel)) == 2


def test_key_is_read_positionally_never_matched():
    # A key in another language derives identically — only position and uniqueness matter.
    g = Graph()
    _emit(g, {0: {2: "Zwischensumme-Gruppe", 3: "100"},
              1: {2: "Zwischensumme-Gruppe", 3: "150"},
              2: {2: "ZS", 3: "250"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (2, 3, (0, 1))}) == 1
    assert str(g.value(g.value(_grp(2), TAB.hasLabel), TAB.cellText)) == "Zwischensumme-Gruppe"


def test_no_confirmed_aggregations_derives_nothing():
    g = Graph()
    _emit(g, {0: {2: "A", 3: "100"}}, {})
    assert derive_row_groups(g, T, {}) == 0
    assert (None, RDF.type, TAB.DerivedRowGroup) not in g
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_groups.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.etkl.rowgroups'`

- [ ] **Step 3: Write the key query**

Create `vocab/queries/row-group-key.rq`:

```sparql
# row-group-key.rq (loop I, AXIOM) — the group KEY for one confirmed aggregation row.
# Bindings: ?agg = the tab:DetectedAggregationRow URI; ?lcol = the label-column URI.
# The key is the unique distinct non-blank cellText in the label column among the MEMBER
# rows (?agg tab:aggregates ?m). Uniqueness is a query-local NOT EXISTS — a holon-scoped
# closed-world guard inside an open derivation (§8): no different non-blank value may
# appear at that column among the members. No unique value -> zero rows -> NO group
# (honest refusal, §7). Blank markers ('-') are NOT special-cased: a '-' value conflicts
# or stands like any text, and refusal is the safe direction.
# ORDER BY ?y (the cell's tab:y0) LIMIT 1 picks the TOPMOST occurrence as the label cell —
# the author's first writing of the key; pure geometry, no numeric literal, deterministic.
# The aggregation row's own label text is never read (no language matching).
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?v ?cell WHERE {
  ?agg tab:aggregates ?m .
  ?cell a tab:EntryCell ; tab:atRow ?m ; tab:atColumn ?lcol ; tab:cellText ?v ;
        tab:hasBBox ?bb .
  ?bb tab:y0 ?y .
  FILTER(STR(?v) != "")
  FILTER NOT EXISTS {
    ?agg tab:aggregates ?m2 .
    ?c2 a tab:EntryCell ; tab:atRow ?m2 ; tab:atColumn ?lcol ; tab:cellText ?v2 .
    FILTER(STR(?v2) != "" && STR(?v2) != STR(?v))
  }
}
ORDER BY ?y
LIMIT 1
```

- [ ] **Step 4: Write the nesting query**

Create `vocab/queries/row-group-nesting.rq`:

```sparql
# row-group-nesting.rq (loop I, AXIOM) — parent links between derived row groups by STRICT
# member-set containment, with a no-intermediate guard. Binding: ?tbl = the table URI (the
# holon — all guards are scoped inside it). child < parent iff every member of child is a
# member of parent (NOT EXISTS a child member the parent lacks), parent has a member child
# lacks (strictness), and no third group sits strictly between them. Identical member sets
# are NOT containment (no link) — refusal over a guess. No numeric literal.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?child ?parent WHERE {
  ?child a tab:DerivedRowGroup . ?parent a tab:DerivedRowGroup .
  FILTER(?child != ?parent)
  ?tbl tab:hasHeaderNode ?child . ?tbl tab:hasHeaderNode ?parent .
  FILTER NOT EXISTS { ?child tab:coversRow ?m .
                      FILTER NOT EXISTS { ?parent tab:coversRow ?m } }
  FILTER EXISTS { ?parent tab:coversRow ?x .
                  FILTER NOT EXISTS { ?child tab:coversRow ?x } }
  FILTER NOT EXISTS {
    ?mid a tab:DerivedRowGroup .
    FILTER(?mid != ?child && ?mid != ?parent)
    ?tbl tab:hasHeaderNode ?mid .
    FILTER NOT EXISTS { ?child tab:coversRow ?a .
                        FILTER NOT EXISTS { ?mid tab:coversRow ?a } }
    FILTER EXISTS { ?mid tab:coversRow ?b .
                    FILTER NOT EXISTS { ?child tab:coversRow ?b } }
    FILTER NOT EXISTS { ?mid tab:coversRow ?c .
                        FILTER NOT EXISTS { ?parent tab:coversRow ?c } }
    FILTER EXISTS { ?parent tab:coversRow ?d .
                    FILTER NOT EXISTS { ?mid tab:coversRow ?d } }
  }
}
```

- [ ] **Step 5: Write the glue module**

Create `src/iladub/etkl/rowgroups.py`:

```python
"""rowgroups — loop I: row groups derived from confirmed aggregation rows (AXIOM).

A confirmed tab:DetectedAggregationRow witnesses its group: label column = level,
tab:aggregates = members, and the KEY = the unique distinct non-blank member value in the
label column (row-group-key.rq). Nesting = strict member-set containment
(row-group-nesting.rq). §8: both decisions are SPARQL derivations (open world; the
uniqueness/containment guards are query-local NOT EXISTS — the table holon is the closure
boundary). This module is ENGINE GLUE only (bindings, triple merge, a parentHeader depth
walk) — the interpret.run pattern; it decides nothing.

Group nodes reuse the shipped row-header vocabulary (tab:HeaderNode + hasHeaderNode +
coversRow + parentHeader + headerLevel) so feed._row_header_path reads them unchanged, and
are ALSO typed tab:DerivedRowGroup: the membrane shape targets the subclass, and the
row-tiling triggers exclude derived-only trees (derived groups are carried annotations —
§5 — not a claimed row partition; coverage is honestly PARTIAL: aggregation rows and rows
of unconfirmed groups stay uncovered). hasLabel points at the SOURCE EntryCell that carries
the key — provenance to the page (§6) with no text duplication."""
from __future__ import annotations

import os
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
_QDIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


def _query_text(name: str) -> str:
    return Path(os.path.join(_QDIR, name)).read_text(encoding="utf-8")


def derive_row_groups(g: Graph, table_uri: URIRef, agg: dict) -> int:
    """Derive one group node per confirmed aggregation row whose key is unique.

    `agg` is detect_aggregation_rows' return: {row_index: (label_col, measure_col,
    member_indices)}. Reads/writes `g` (the scratch graph inside the loop G backstop when
    the hierarchical path is gated). Returns the number of groups constructed."""
    key_q = _query_text("row-group-key.rq")
    made = 0
    for i in sorted(agg):
        label_col, _mcol, _members = agg[i]
        arow = URIRef(f"{table_uri}-r{i}")
        lcol_uri = URIRef(f"{table_uri}-c{label_col}")
        hit = list(g.query(key_q, initBindings={"agg": arow, "lcol": lcol_uri}))
        if not hit:
            continue                    # no unique non-blank key -> no group (§7)
        _v, cell = hit[0]
        grp = URIRef(f"{table_uri}-rg{i}")
        g.add((grp, RDF.type, TAB.HeaderNode))
        g.add((grp, RDF.type, TAB.DerivedRowGroup))
        g.add((table_uri, TAB.hasHeaderNode, grp))
        g.add((grp, TAB.hasLabel, cell))
        g.add((grp, PROV.wasDerivedFrom, arow))
        for m in g.objects(arow, TAB.aggregates):
            g.add((grp, TAB.coversRow, m))
        made += 1
    if made:
        parents = {}
        for child, parent in g.query(_query_text("row-group-nesting.rq"),
                                     initBindings={"tbl": table_uri}):
            g.add((child, TAB.parentHeader, parent))
            parents[child] = parent
        for grp in set(g.subjects(RDF.type, TAB.DerivedRowGroup)):
            if (table_uri, TAB.hasHeaderNode, grp) not in g:
                continue
            level, cur = 0, parents.get(grp)
            while cur is not None:
                level += 1
                cur = parents.get(cur)
            g.add((grp, TAB.headerLevel, Literal(level, datatype=XSD.integer)))
    return made
```

- [ ] **Step 6: Run the tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_groups.py -q`
Expected: PASS (8 tests). If the nesting test fails on the strict-chain case, debug the
query against the g2 graph directly (print `list(g2.query(...))`) before touching the glue.

- [ ] **Step 7: Commit**

```bash
git add vocab/queries/row-group-key.rq vocab/queries/row-group-nesting.rq src/iladub/etkl/rowgroups.py tests/etkl/test_row_groups.py
git commit -m "feat(etkl): row groups derived from confirmed aggregations — key + nesting AXIOM (loop I)"
```

---

### Task 2: Vocab + membrane (shape scoping is the hard part)

**Files:**
- Modify: `vocab/ontology/tab.ttl` (near the `tab:DetectedAggregationRow` declaration)
- Modify: `vocab/shapes/tab-shapes.ttl` (`RowCoverageShape` ~line 155, `UnambiguousRowAccessShape` ~line 205, new shape at end)
- Modify: `src/iladub/etkl/tiling.py:25-42` (`_TILING_SHAPE_IRIS` + the three "ten" docstring counts)
- Test: `tests/etkl/test_row_groups.py` (append)

**Interfaces:**
- Consumes: Task 1's emission shape (`tab:DerivedRowGroup` nodes with `hasLabel`/`coversRow`/`prov:wasDerivedFrom`).
- Produces: `region_tiles(g)` verdicts — `tab:DerivedRowGroupShape` refuses malformed groups; `RowCoverageShape`/`UnambiguousRowAccessShape` ignore derived-only trees but still fire for authored (plain `HeaderNode`) row trees.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_row_groups.py`:

```python
def _tiles(g):
    from iladub.etkl.tiling import region_tiles
    return region_tiles(g)


def test_membrane_refuses_a_labelless_group():
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.coversRow, URIRef("urn:doc#h0-r0")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    assert _tiles(g) is False


def test_membrane_refuses_a_memberless_group():
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.hasLabel, URIRef("urn:doc#h0-e0_2")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    assert _tiles(g) is False


def test_membrane_accepts_a_wellformed_group():
    g = Graph()
    grp = URIRef("urn:doc#h0-rg2")
    g.add((grp, RDF.type, TAB.DerivedRowGroup))
    g.add((grp, TAB.hasLabel, URIRef("urn:doc#h0-e0_2")))
    g.add((grp, TAB.coversRow, URIRef("urn:doc#h0-r0")))
    g.add((grp, PROV.wasDerivedFrom, URIRef("urn:doc#h0-r2")))
    assert _tiles(g) is True


def test_partial_derived_coverage_passes_the_row_tiling_shapes():
    """THE LANDMINE THIS TASK EXISTS FOR. RowCoverageShape / UnambiguousRowAccessShape fire
    as soon as ANY coversRow header exists, demanding every leaf row be covered. Derived
    groups are honestly PARTIAL (aggregation rows and unconfirmed groups' rows stay
    uncovered) — they are carried annotations, not a claimed partition. Without the trigger
    scoping, every real document with subtotals would escalate REGION_TILING_FAILED."""
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Mackay", 3: "150"},
              2: {2: "SUB", 3: "250"},
              3: {2: "Kembla", 3: "999"}}, {2: (0, 1)})
    assert derive_row_groups(g, T, {2: (2, 3, (0, 1))}) == 1
    # rows r2 (the aggregation) and r3 (no confirmed group) are UNCOVERED — must still pass
    assert _tiles(g) is True


def test_authored_row_trees_keep_the_strict_invariant():
    """The scoping must NOT weaken the row-hier/matrix membrane: a plain HeaderNode row tree
    with a coverage gap still fails."""
    g = Graph()
    t = URIRef("urn:doc#rh0")
    for r in (0, 1):
        g.add((URIRef(f"urn:doc#rh0-r{r}"), RDF.type, TAB.LeafRow))
        g.add((t, TAB.hasLeafRow, URIRef(f"urn:doc#rh0-r{r}")))
    h = URIRef("urn:doc#rh0-rh0")
    g.add((h, RDF.type, TAB.HeaderNode))          # authored, NOT DerivedRowGroup
    g.add((t, TAB.hasHeaderNode, h))
    g.add((h, TAB.coversRow, URIRef("urn:doc#rh0-r0")))   # r1 uncovered -> gap
    assert _tiles(g) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_groups.py -q`
Expected: the five new tests FAIL (`DerivedRowGroupShape` unknown; partial-coverage test
fails on RowCoverage/UnambiguousRowAccess).

- [ ] **Step 3: Add the vocab term**

In `vocab/ontology/tab.ttl`, next to the `tab:DetectedAggregationRow` declaration, add:

```turtle
tab:DerivedRowGroup a owl:Class ;
    rdfs:subClassOf tab:HeaderNode ;
    rdfs:label "derived row group"@en ;
    rdfs:comment "A row-group header node DERIVED from a confirmed aggregation row (loop I): its coversRow members come from the aggregation's operands, its label from the unique non-blank member value in the label column, its provenance from the witnessing aggregation row. Derived groups are carried annotations over the row axis — coverage may be PARTIAL (rows of unconfirmed groups stay uncovered), so the row-tiling shapes exclude derived-only trees; tab:DerivedRowGroupShape guards well-formedness instead."@en .
```

(No `owl:versionInfo` bump: additive, monotonic — 0.2.0 stands.)

- [ ] **Step 4: Add the shape and scope the two triggers**

In `vocab/shapes/tab-shapes.ttl`:

(a) Append the new shape:

```turtle
#################################################################
#  Derived row groups (loop I): a derived group must be
#  explained — one label (the source key cell), at least one
#  member, and its witnessing aggregation row. Targets the
#  SUBCLASS only: authored HeaderNodes are untouched.
#################################################################

tab:DerivedRowGroupShape a sh:NodeShape ;
    sh:targetClass tab:DerivedRowGroup ;
    sh:property [ sh:name "DerivedRowGroupShape" ; sh:path tab:hasLabel ;
        sh:minCount 1 ; sh:maxCount 1 ;
        sh:message "A derived row group needs exactly one label (its source key cell)." ] ;
    sh:property [ sh:name "DerivedRowGroupShape" ; sh:path tab:coversRow ; sh:minCount 1 ;
        sh:message "A derived row group needs at least one member row." ] ;
    sh:property [ sh:name "DerivedRowGroupShape" ; sh:path prov:wasDerivedFrom ;
        sh:minCount 1 ; sh:maxCount 1 ;
        sh:message "A derived row group needs exactly one witnessing aggregation row." ] .
```

Check the file's prefix block declares `prov:`; if not, add
`@prefix prov: <http://www.w3.org/ns/prov#> .` at the top AND `sh:declare` it on
`tab:prefixes` if any sh:sparql shape needs it (the property shapes above do not).

(b) In `RowCoverageShape`'s SPARQL (line ~163), replace the trigger line:

```
                FILTER EXISTS { ?tbl tab:hasHeaderNode ?any . ?any tab:coversRow ?anyrow }
```

with:

```
                FILTER EXISTS { ?tbl tab:hasHeaderNode ?any . ?any tab:coversRow ?anyrow .
                                FILTER NOT EXISTS { ?any a tab:DerivedRowGroup } }
```

and update the shape's `sh:message` to note the scope: `"Leaf row is not covered by any row-header of its table (row coverage gap; derived-only trees are exempt — they are partial annotations)."`

(c) In `UnambiguousRowAccessShape`'s SPARQL (line ~213), make the SAME trigger replacement,
AND exclude derived groups from the leaf-header count (inside the OPTIONAL):

```
                        OPTIONAL {
                            ?tbl tab:hasHeaderNode ?h .
                            ?h tab:coversRow $this .
                            FILTER NOT EXISTS { ?child tab:parentHeader ?h }
                            FILTER NOT EXISTS { ?h a tab:DerivedRowGroup }
                        }
```

- [ ] **Step 5: Register the shape in the tiling gate**

In `src/iladub/etkl/tiling.py`, extend `_TILING_SHAPE_IRIS` with `TAB.DerivedRowGroupShape`
(eleventh entry) and update the THREE docstring counts that say "ten" to "eleven" (grep
`ten` in the file; the loop H review verified all three stay in sync — keep them so).

- [ ] **Step 6: Run the tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_groups.py tests/etkl/test_tiling.py tests/etkl/test_aggregation_rows.py -q`
Expected: PASS. If `test_authored_row_trees_keep_the_strict_invariant` fails, the trigger
scoping went too far — re-check that the `NOT EXISTS { ?any a tab:DerivedRowGroup }` sits
INSIDE the `FILTER EXISTS`, not around it.

- [ ] **Step 7: Run the shipped-fixture guard**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_compile.py tests/etkl/test_matrix.py tests/etkl/test_rowheaders.py -q`
(Adjust to the actual test files covering matrix/row-hier compiles if named differently —
`ls tests/etkl/ | grep -iE "matrix|rowheader|compile"`.)
Expected: PASS — the authored-tree paths are untouched.

- [ ] **Step 8: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl src/iladub/etkl/tiling.py tests/etkl/test_row_groups.py
git commit -m "feat(etkl): DerivedRowGroup vocab + membrane; row-tiling triggers exempt derived-only trees (loop I)"
```

---

### Task 3: Emission + feed collision guard + E2E

**Files:**
- Modify: `src/iladub/etkl/holon.py` (`assert_hier_region`, after the body-entry-cell loop, before `return asserted` — around line 485)
- Modify: `src/iladub/feed.py` (`table_records` record-minting loop, lines 52-55)
- Test: `tests/etkl/test_row_groups.py` (append)

**Interfaces:**
- Consumes: Task 1's `derive_row_groups(g, table_uri, agg)`; the local `agg` dict already computed in `assert_hier_region` (line ~446); `feed._row_header_path` (unchanged); `feed._record_uri` (unchanged).
- Produces: compiled hierarchical tables carry group nodes; `table_records` mints collision-safe identities: rows sharing a path get their opaque fragment appended (`Mackay > htable0-r1`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_row_groups.py`:

```python
def test_feed_collision_guard_two_rows_one_group(tmp_path=None):
    """PR #59's recorded minor made real: two rows in the SAME group share a path — without
    the guard they mint the SAME record URI and silently merge. RED against today's feed."""
    from iladub.feed import table_records, _record_uri
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "Mackay", 3: "150"},
              2: {2: "SUB", 3: "250"}}, {2: (0, 1)})
    g.add((T, RDF.type, TAB.HierarchicalTable))
    g.add((URIRef(f"{T}-r2"), RDF.type, TAB.AggregationRow))   # feed skips it
    derive_row_groups(g, T, {2: (2, 3, (0, 1))})
    recs = table_records(g)
    assert len(recs) == 2
    ids = [r.row_id for r in recs]
    assert len(set(_record_uri(i) for i in ids)) == 2, ids     # DISTINCT subjects
    assert all(i.startswith("Mackay") for i in ids), ids       # both carry the group path


def test_feed_uncovered_rows_keep_opaque_identity():
    from iladub.feed import table_records
    g = Graph()
    _emit(g, {0: {2: "Mackay", 3: "100"},
              1: {2: "SUB", 3: "100"},
              3: {2: "Kembla", 3: "999"}}, {1: (0,)})
    g.add((T, RDF.type, TAB.HierarchicalTable))
    g.add((URIRef(f"{T}-r1"), RDF.type, TAB.AggregationRow))
    derive_row_groups(g, T, {1: (2, 3, (0,))})
    recs = table_records(g)
    by_id = {r.row_id: r for r in recs}
    assert "Mackay" in by_id            # single-member group: clean path, no suffix
    assert any(i.endswith("-r3") or i == "h0-r3" for i in by_id), by_id.keys()


def test_e2e_compiled_fixture_carries_the_group(tmp_path):
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.compile import compile_tables
    from iladub.feed import table_records
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "sub.pdf")
    F.subtotal_hier_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions), [r.reason for r in rep.regions]
    groups = list(rep.graph.subjects(RDF.type, TAB.DerivedRowGroup))
    assert len(groups) == 1, groups
    grp = groups[0]
    label = rep.graph.value(grp, TAB.hasLabel)
    assert str(rep.graph.value(label, TAB.cellText)) == "A"    # key from members r0/r1 col 1
    covers = {str(u).rsplit("-", 1)[-1] for u in rep.graph.objects(grp, TAB.coversRow)}
    assert covers == {"r0", "r1"}
    recs = table_records(rep.graph)
    assert len(recs) == 3
    pathed = [r.row_id for r in recs if r.row_id.startswith("A > ") or r.row_id == "A"]
    assert len(pathed) == 2 and len(set(pathed)) == 2, [r.row_id for r in recs]
```

NOTE for the implementer on the E2E key: the fixture's rows are
`("Jul","Mackay","V1","100","B1") / ("","Mackay","V2","150","B2") / ("","SUB","","250","")`
and Loop H detection returns `{2: (1, 3, (0, 1))}` — label column 1 is the PORT column
whose member values are 'Mackay'/'Mackay', so the expected key is **"Mackay"**, not "A".
Correct the two assertions accordingly (`== "Mackay"`, `startswith("Mackay")`) — then
verify against an actual compile BEFORE committing (`python3 -c` probe). If the compiled
grid maps columns differently, trust the measured value and pin THAT, updating this note.

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_groups.py -q`
Expected: the three new tests FAIL (no groups emitted by compile; collision guard absent —
the first test fails on `len(set(...)) == 2`).

- [ ] **Step 3: Wire the emission**

In `src/iladub/etkl/holon.py::assert_hier_region`, after the body-entry-cell loop and
immediately before `return asserted`, add:

```python
    # Row groups from the confirmed aggregations (loop I, AXIOM): runs AFTER the entry
    # cells exist (the key query reads member cells), still inside the caller's scratch
    # graph when the loop G backstop gates this path — a malformed group escalates in-band.
    if agg:
        from .rowgroups import derive_row_groups
        derive_row_groups(g, table_uri, agg)
```

- [ ] **Step 4: Add the feed collision guard**

In `src/iladub/feed.py::table_records`, replace the record-minting loop (lines 52-55):

```python
        for row in sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r])):
            cells = [c for _, _, c in sorted(rows[row], key=lambda kc: kc[0])]
            rid = row_path.get(row, str(row).split("#")[-1])
            out.append(Record(rid, tuple(cells)))
```

with:

```python
        ordered = sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r]))
        # Collision guard (loop I; closes the PR #59 recorded minor): two rows sharing a
        # header path (e.g. two bookings in one derived group) must never mint the same
        # record subject — each colliding row keeps its opaque fragment appended.
        rid_of = {row: row_path.get(row, str(row).split("#")[-1]) for row in ordered}
        multiplicity: dict = {}
        for rid in rid_of.values():
            multiplicity[rid] = multiplicity.get(rid, 0) + 1
        for row in ordered:
            cells = [c for _, _, c in sorted(rows[row], key=lambda kc: kc[0])]
            rid = rid_of[row]
            if multiplicity[rid] > 1:
                rid = f"{rid} > {str(row).split('#')[-1]}"
            out.append(Record(rid, tuple(cells)))
```

- [ ] **Step 5: Probe the E2E key value, then run the tests**

Probe FIRST (do not trust the plan's fixture reading):

```bash
. .venv/bin/activate && python3 - <<'PY'
import sys, tempfile, os
sys.path.insert(0, "tests")
from etkl import fixtures as F
from iladub.etkl.compile import compile_tables
from rdflib import Namespace, RDF
TAB = Namespace("https://w3id.org/iladub/tab#")
d = tempfile.mkdtemp(); p = os.path.join(d, "x.pdf")
F.subtotal_hier_table_pdf(p)
rep = compile_tables(p)
for grp in rep.graph.subjects(RDF.type, TAB.DerivedRowGroup):
    lb = rep.graph.value(grp, TAB.hasLabel)
    print("group:", grp, "label:", rep.graph.value(lb, TAB.cellText),
          "covers:", sorted(str(u) for u in rep.graph.objects(grp, TAB.coversRow)))
PY
```

Fix the E2E assertions to the measured key, then:
Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_row_groups.py tests/etkl/test_aggregation_rows.py tests/etkl/test_feed.py -q`
(Adjust the feed test filename if different: `ls tests | grep -i feed`.)
Expected: PASS, including the existing feed/matrix tests (cross-tab paths tile uniquely, so
the guard is inert there — if a matrix test fails, the guard is wrongly suffixing unique
paths; check the multiplicity count).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/holon.py src/iladub/feed.py tests/etkl/test_row_groups.py
git commit -m "feat(etkl): emit derived row groups on the hierarchical path; feed collision guard (loop I)"
```

---

### Task 4: Verification + docs (controller-run; needs the local GrainCorp PDF)

**Files:**
- Modify: `docs/superpowers/residues.md` (close the PR #59 minor mention if registered; add the ungrouped-groups residue)
- Modify: `docs/superpowers/specs/2026-07-30-row-groups-design.md` (status line with measured numbers)

- [ ] **Step 1: GrainCorp confirmation (the discriminating criteria)**

Run the recorded-proposer compile against the local stem PDF and check ALL of:

1. `tab:DerivedRowGroup` count == **16** (3 months + 13 ports; the grand total `2025/26
   Total` must REFUSE — its members carry conflicting month keys).
2. Every month group's ports are its children (`parentHeader`); months have no parent.
3. Spot-check identities: two same-port rows (the Aug 26 Mackay pair) mint DISTINCT record
   URIs, both carrying the `Aug 26 > Mackay` path.
4. Port Kembla data rows keep opaque identity.
5. **score == 0.9496 and cells == 509 — UNCHANGED (failure condition).**
6. `detected aggregation rows` still 17, `fused` still NONE.

- [ ] **Step 2: Full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q` (FOREGROUND, timeout ≥ 400000 ms)
Expected: 650 + new tests passed, 5 skipped, 0 failures.

- [ ] **Step 3: Update the register and spec status**

- `docs/superpowers/residues.md`: append the loop I row — *groups without a confirmed
  total* (Port Kembla stays ungrouped; would close via ditto-fill evidence cross-checked
  against H) — and note in the R4 row (or wherever the PR #59 minor lives) that the
  `_record_uri` collision guard shipped in loop I.
- Spec status → Shipped with the measured numbers from Step 1.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-30-row-groups-design.md
git commit -m "docs(loop-I): register + spec status with measured GrainCorp numbers"
```

---

## Self-Review

- **Spec coverage:** §2.1 queries → Task 1; §2.2 emission → Task 3; §2.3 membrane (+ the
  row-shape scoping the spec's §2.3 implies via "the matrix path's existing row headers are
  untouched" — surfaced explicitly here as the Task 2 landmine) → Task 2; §2.4 feed guard →
  Task 3; §1 success criteria → Task 4. The spec's `headerLevel` = containment count is
  implemented as the ancestor-depth walk over the derived `parentHeader` links —
  equivalent by construction on a forest (each group has ≤ 1 parent).
- **Placeholder scan:** none. The one deliberately-open value (the E2E key text) carries
  its own measure-first instruction rather than a guessed constant.
- **Type consistency:** `derive_row_groups(g, table_uri, agg) -> int` is used identically
  in Tasks 1 and 3; `agg` shape matches `detect_aggregation_rows`' return
  `{row: (label_col, measure_col, members)}` (rows.py); `_record_uri` unchanged.
