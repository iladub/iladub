# Hierarchical Table Feed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the concept feed to `tab:HierarchicalTable` — a merged-header cell's field becomes the header PATH (root → leaf sub-header) — so hierarchical tables flow raw-doc→grounded-graph, while flat `RecordTable` output stays byte-identical.

**Architecture:** Generalize `feed.table_records` to read both `tab:RecordTable` and `tab:HierarchicalTable`, computing each column's field via a new `_column_header_path` helper (deepest covering `HeaderNode`, walked up `parentHeader` to root, joined `" > "`). This reduces to the single column label for flat tables. `ground_document`/`ground_concept` are unchanged.

**Tech Stack:** Python 3.12, rdflib, pytest.

## Global Constraints

- **§8 gate:** PROCEDURAL raw extraction — pure RDF reads over the header tree (`hasHeaderNode`/`coversColumn`/`hasLabel`/`headerLevel`/`parentHeader`); NO tuned constant, NO IRI-name parsing. NO new grounding decision — `ground_document`/`ground_concept` reused verbatim (a header path is just `SurfaceConcept.text`).
- **Backward compatibility (load-bearing):** the flat `RecordTable` feed output must stay byte-identical — guaranteed because `_column_header_path` yields the single label for flat tables (all headers level-0 / single-column / no parent). Verified by the existing `tests/test_concept_feed.py` staying green + an explicit label-not-path assertion.
- **§7:** out-of-range / unmapped cells quarantine as `CandidateConcept` propositions, never dropped.
- **No shared shape / contract changes;** the E2E mapping is test-local and illustrative (proves wiring, not a domain claim).
- **Probe-validated (2026-07-23):** the pivoted CBC table → 5 records with correct paths; through `ground_document` with `{"Current Visit > Result (SI)" → ejectionFraction}`, 4 grounded / 26 proposed (in-range Current Results ground via the value-constraint oracle; "252" and unmapped paths quarantine).
- **Testing:** run ONLY via `./.venv/bin/python -m pytest`.
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `iladub-hierarchical-feed`.

---

### Task 1: Header-path bridge — read HierarchicalTable, path-per-column

**Files:**
- Modify: `src/iladub/feed.py` (add `_column_header_path`; generalize `table_records`)
- Test: `tests/test_concept_feed.py`

**Interfaces:**
- Consumes: the compiled `tab:` graph (`RecordTable`/`HierarchicalTable`/`hasHeaderNode`/`coversColumn`/`hasLabel`/`headerLevel`/`parentHeader`/`EntryCell`/`atColumn`/`atRow`/`cellText`/`hasBBox`); `SurfaceConcept`.
- Produces: `_column_header_path(graph, table) -> dict[column, str]`; `table_records` handling both table types (unchanged signature/return).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_concept_feed.py`:

```python
# --- Hierarchical feed ---
from iladub.feed import _column_header_path


def _compiled_hier_graph():
    p = os.path.join(tempfile.mkdtemp(), "hier.pdf"); F.pivoted_table_pdf(p)
    return compile_tables(p).graph


def test_hierarchical_records_carry_header_paths():
    recs = table_records(_compiled_hier_graph())
    assert len(recs) == 5                                   # five analyte rows
    # every record has the stub + the 6 merged-header data cells
    by_path = {c.text: c.value for r in recs for c in r.concepts}
    assert by_path["Current Visit > Result (SI)"] in {"13.2", "39.5", "7.8", "252", "88.4"}
    assert by_path["Prior Visit > Unit"] in {"g/dL", "%", "x10^9/L", "fL"}
    assert "Analyte" in by_path                              # the stub column path is its single label
    # at least one full root>leaf path is present verbatim
    assert any(c.text == "Current Visit > Result (SI)" for r in recs for c in r.concepts)


def test_column_header_path_flat_is_single_label_hier_is_path():
    from rdflib import RDF as _RDF
    TAB = Namespace("https://w3id.org/iladub/tab#")
    # flat: offer RecordTable -> each column path is a single label
    fg = _compiled_offer_graph()
    ftab = next(fg.subjects(_RDF.type, TAB.RecordTable))
    assert "Organ" in set(_column_header_path(fg, ftab).values())
    assert all(" > " not in p for p in _column_header_path(fg, ftab).values())
    # hierarchical: at least one column path is a root>leaf path
    hg = _compiled_hier_graph()
    htab = next(hg.subjects(_RDF.type, TAB.HierarchicalTable))
    assert any(" > " in p for p in _column_header_path(hg, htab).values())


def test_recordtable_feed_unchanged_single_label_header():
    # backward compat: an offer record's concept header is a plain label, never a path
    recs = table_records(_compiled_offer_graph())
    headers = {c.text for r in recs for c in r.concepts}
    assert "Organ" in headers and all(" > " not in h for h in headers)


def test_hierarchical_grounds_end_to_end():
    # illustrative wiring: map the numeric "Result" path to the value-constrained EF field. In-range
    # Current-Visit results ground via the value-constraint oracle THROUGH the hierarchical feed;
    # out-of-range ("252") and unmapped paths quarantine. Proves path-concepts flow + the oracle gates.
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    proposer = MappingGroundingProposer({
        "Current Visit > Result (SI)": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9,
                                                         "result", "urn:iladub:suggester/fake"),
    })
    g = Graph()
    res = ground_document(_compiled_hier_graph(), c, proposer, terms, shapes, g)
    assert res.records == 5
    assert res.grounded > 0 and res.proposed > 0            # some in-range results ground; rest quarantine
    assert len(list(g.subjects(RDF.type, ILA.GroundedNode))) == res.grounded
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -k "hierarchical or column_header_path" -v`
Expected: FAIL — `_column_header_path` does not exist (ImportError), and `test_hierarchical_records_carry_header_paths` gets 0 records (the shipped `table_records` filters only `RecordTable`). `test_recordtable_feed_unchanged_single_label_header` PASSES already (current behavior) — that is expected (it pins backward compat).

- [ ] **Step 3: Implement `_column_header_path` + generalize `table_records`**

In `src/iladub/feed.py`, replace the `table_records` function with the generalized version and add the helper immediately after it:

```python
def table_records(graph: Graph) -> list[Record]:
    """Each asserted tab:RecordTable OR tab:HierarchicalTable -> one Record per data row; each data
    cell -> a SurfaceConcept (text=its column's HEADER PATH, value=cell text, region=cell provenance).
    For a flat RecordTable the path reduces to the single column label (backward compatible). RDF
    reads only; no tuned constant, no IRI-name parsing."""
    out: list[Record] = []
    tables = (set(graph.subjects(RDF.type, TAB.RecordTable))
              | set(graph.subjects(RDF.type, TAB.HierarchicalTable)))
    for t in sorted(tables, key=str):
        header = _column_header_path(graph, t)
        rows: dict = {}
        for e in graph.subjects(RDF.type, TAB.EntryCell):
            if (t, TAB.hasCell, e) not in graph:
                continue
            col = graph.value(e, TAB.atColumn)
            row = graph.value(e, TAB.atRow)
            prov = graph.value(e, PROV.wasDerivedFrom)
            region = str(prov).split("#")[-1] if prov is not None else str(e).split("#")[-1]
            concept = SurfaceConcept(header.get(col, ""), str(graph.value(e, TAB.cellText)), region)
            x0, y0 = _bbox_xy(graph, e)
            rows.setdefault(row, []).append((x0, y0, concept))
        for row in sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r])):
            cells = [c for _, _, c in sorted(rows[row], key=lambda kc: kc[0])]
            out.append(Record(str(row).split("#")[-1], tuple(cells)))
    return out


def _column_header_path(graph: Graph, table) -> dict:
    """Map each covered column of `table` to its HEADER PATH: the deepest HeaderNode covering the
    column, walked up parentHeader to the root, labels joined ' > '. For a flat RecordTable (headers
    all level-0, single-column, no parent) this is the single column label. RDF reads only."""
    label: dict = {}
    parent: dict = {}
    best: dict = {}                                 # column -> (level, header_node)
    for h in graph.objects(table, TAB.hasHeaderNode):
        lc = graph.value(h, TAB.hasLabel)
        label[h] = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
        parent[h] = graph.value(h, TAB.parentHeader)
        lvl_lit = graph.value(h, TAB.headerLevel)
        lvl = int(lvl_lit) if lvl_lit is not None else 0
        for col in graph.objects(h, TAB.coversColumn):
            if col not in best or lvl > best[col][0]:
                best[col] = (lvl, h)
    paths: dict = {}
    for col, (_, h) in best.items():
        parts: list = []
        cur = h
        while cur is not None:
            parts.append(label.get(cur, ""))
            cur = parent.get(cur)
        paths[col] = " > ".join(reversed(parts))
    return paths
```

(Delete the old inline `header` map that lived inside the previous `table_records`.)

- [ ] **Step 4: Run the tests to verify they pass**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -v`
Expected: all pass (hierarchical path tests GREEN; `_column_header_path` unit GREEN; the backward-compat + all shipped concept-feed tests still GREEN).

- [ ] **Step 5: Run the full suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/ -q`
Expected: all pass. The change is confined to `feed.table_records` + the new helper; `ground_document`, `ground_concept`, the etkl compiler, and all shapes are untouched. (A benign rdflib "Failed to convert Literal lexical form" warning on the out-of-range "252" grounding attempt is expected — it is the value-constraint oracle rejecting it.)

- [ ] **Step 6: Commit**

```bash
git add src/iladub/feed.py tests/test_concept_feed.py
git commit -m "feat(iladub): hierarchical table feed — header-path concepts (root>leaf); RecordTable output byte-identical"
```

---

## Self-Review

**Spec coverage:**
- Generalize `table_records` to RecordTable + HierarchicalTable → Task 1 Step 3. ✓
- `_column_header_path` (deepest header, walk parentHeader, join " > ") → Task 1 Step 3. ✓
- Bridge hierarchical-paths test (RED-checked) → `test_hierarchical_records_carry_header_paths`. ✓
- `_column_header_path` flat=label / hier=path unit → `test_column_header_path_flat_is_single_label_hier_is_path`. ✓
- Backward compat (RecordTable single-label, byte-identical) → `test_recordtable_feed_unchanged_single_label_header` + existing suite green. ✓
- E2E through unchanged `ground_document` (records=5, grounded>0, proposed>0) → `test_hierarchical_grounds_end_to_end`. ✓
- §8 PROCEDURAL (RDF reads, no tuned constant) → feed docstring + Global Constraints. ✓
- §7 residue quarantined (out-of-range/unmapped) → E2E `proposed > 0`. ✓
- Matrix out of scope; no shared shape/contract changes → Global Constraints. ✓

**Placeholder scan:** none — full code + exact commands, every assertion probe-validated (5 records, 4 grounded / 26 proposed observed; robust `>0` inequalities used).

**Type consistency:** `_column_header_path(graph, table) -> dict[column, str]`, `table_records(graph) -> list[Record]` (signature unchanged), `Record(row_id, concepts)`, `FeedResult(records, grounded, proposed)`, `ground_document(graph, contract, proposer, terms, shapes, g)`, `MappingGroundingProposer(mapping)`, `GroundingProposal(field_iri, anchor_iri, confidence, rationale, suggester_iri)`, `SurfaceConcept(text, value, region)` used identically and match shipped signatures. ✓
