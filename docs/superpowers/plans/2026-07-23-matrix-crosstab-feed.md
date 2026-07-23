# Matrix (cross-tab) Feed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Carry a cross-tab's **row-header path** (via `coversRow`) as the record identity, so cross-tab records mint meaningful subjects (`urn:iladub:record:North`) instead of opaque row ids — while flat/hierarchical output stays byte-identical.

**Architecture:** DRY the header-path walk into a shared `_header_path(graph, table, cover_pred)`; `_column_header_path` (existing) and a new `_row_header_path` delegate to it (over `coversColumn` / `coversRow`). `table_records` uses the row-header path as `row_id` when present; `ground_document` mints a URI-safe subject slug. `ground_concept` and the etkl compiler are unchanged.

**Tech Stack:** Python 3.12, rdflib, pytest.

## Global Constraints

- **§8 gate:** PROCEDURAL raw extraction — pure RDF reads (`hasHeaderNode`/`coversRow`/`coversColumn`/`hasLabel`/`headerLevel`/`parentHeader`); NO tuned constant, NO IRI-name parsing. NO new grounding decision — a row-header path is just a subject label.
- **Backward compatibility (load-bearing):** `RecordTable` and plain hierarchical tables have no `coversRow` → `_row_header_path` returns `{}` → the opaque row-URI fragment `row_id`, byte-identical. The DRY refactor of `_column_header_path` must produce identical output (pure extraction). Verified by the PR#56/#58 tests staying green. The subject slug must preserve existing opaque ids (`table0-r1` → unchanged) so shipped subject counts/URIs are unaffected.
- **§7:** out-of-range / unmapped cells quarantine as `CandidateConcept` propositions, never dropped.
- **No shared shape / contract changes;** the E2E mapping is test-local and illustrative.
- **Probe-validated (2026-07-23):** `crosstab_table_pdf` → 2 records `North`/`South`, 6 column-path concepts each; E2E with `{"Q1 > Unit" → ejectionFraction}` → subjects `urn:iladub:record:North`/`…:South`, 2 grounded / 10 proposed.
- **Testing:** run ONLY via `./.venv/bin/python -m pytest`.
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `iladub-matrix-feed`.

---

### Task 1: Row-header path as record identity

**Files:**
- Modify: `src/iladub/feed.py` (extract `_header_path`; add `_row_header_path`; row-identity in `table_records`; URI-safe subject in `ground_document`)
- Test: `tests/test_concept_feed.py`

**Interfaces:**
- Consumes: the compiled `tab:` graph (`coversRow`/`coversColumn`/`hasHeaderNode`/`hasLabel`/`headerLevel`/`parentHeader`/`EntryCell`/`atRow`/`atColumn`).
- Produces: `_header_path(graph, table, cover_pred) -> dict`; `_column_header_path`/`_row_header_path` delegating to it; `table_records` with row-header-path `row_id`; `ground_document` minting `urn:iladub:record:<slug>`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_concept_feed.py` (the file already imports `os`, `tempfile`, `compile_tables`, `F`, `Graph`, `Namespace`, `URIRef`, `RDF`, `table_records`, `ground_document`, `FeedResult`, `load_contract`, `MappingGroundingProposer`, `GroundingProposal`, `TX`, `ILA`, `CONTRACT`):

```python
# --- Matrix / cross-tab feed ---
from iladub.feed import _row_header_path


def _compiled_crosstab_graph():
    p = os.path.join(tempfile.mkdtemp(), "ct.pdf"); F.crosstab_table_pdf(p)
    return compile_tables(p).graph


def test_crosstab_records_identified_by_row_header_path():
    recs = table_records(_compiled_crosstab_graph())
    assert len(recs) == 2
    assert {r.row_id for r in recs} == {"North", "South"}          # row identity, not opaque ids
    # each record carries column-path concepts (Q1/Q2 > Rev/Cost/Unit)
    paths = {c.text for r in recs for c in r.concepts}
    assert any(" > " in p and p.startswith("Q1") for p in paths)


def test_row_header_path_present_for_crosstab_empty_otherwise():
    from rdflib import RDF as _RDF
    TABNS = Namespace("https://w3id.org/iladub/tab#")
    hg = _compiled_crosstab_graph()
    ht = next(hg.subjects(_RDF.type, TABNS.HierarchicalTable))
    assert set(_row_header_path(hg, ht).values()) == {"North", "South"}
    # a RecordTable and a plain hierarchical (pivoted) table have NO row tree -> {}
    og = _compiled_offer_graph()
    ot = next(og.subjects(_RDF.type, TABNS.RecordTable))
    assert _row_header_path(og, ot) == {}
    pg = _compiled_hier_graph()
    pt = next(pg.subjects(_RDF.type, TABNS.HierarchicalTable))
    assert _row_header_path(pg, pt) == {}


def test_recordtable_row_ids_unchanged_opaque():
    # backward compat: an offer RecordTable's row_id stays the opaque URI fragment, not a header label
    recs = table_records(_compiled_offer_graph())
    assert all("-r" in r.row_id for r in recs)                     # e.g. "table0-r1"


def test_crosstab_grounds_to_named_subjects_end_to_end():
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    proposer = MappingGroundingProposer({
        "Q1 > Unit": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9, "unit", "urn:iladub:suggester/fake"),
    })
    g = Graph()
    res = ground_document(_compiled_crosstab_graph(), c, proposer, terms, shapes, g)
    assert res.records == 2
    assert res.grounded > 0 and res.proposed > 0
    subjects = set(g.subjects(RDF.type, TX.OrganOffer))
    assert URIRef("urn:iladub:record:North") in subjects
    assert URIRef("urn:iladub:record:South") in subjects
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -k "crosstab or row_header_path or row_ids_unchanged" -v`
Expected: FAIL — `_row_header_path` does not exist (ImportError); `test_crosstab_records_identified_by_row_header_path` gets opaque `row_id`s (`{"mtable0-r0", "mtable0-r1"}` ≠ `{"North","South"}`); the named-subject E2E fails (subjects are `urn:iladub:record:mtable0-r0`). `test_recordtable_row_ids_unchanged_opaque` PASSES already (pins current behavior).

- [ ] **Step 3: Implement — DRY the path walk, add row path, row identity, URI-safe subject**

In `src/iladub/feed.py`:

(a) Add `import re` at the top (after `from __future__ import annotations`).

(b) Replace `_column_header_path` with the shared helper + two thin delegates:

```python
def _header_path(graph: Graph, table, cover_pred) -> dict:
    """Map each target (column or row) covered by `table`'s header tree to its HEADER PATH: the
    deepest HeaderNode covering the target (via `cover_pred` = TAB.coversColumn or TAB.coversRow),
    walked up parentHeader to the root, labels joined ' > '. For a flat axis (level-0, single target,
    no parent) this is the single label. Returns {} when no header node covers via `cover_pred`.
    RDF reads only; no tuned constant, no IRI-name parsing."""
    label: dict = {}
    parent: dict = {}
    best: dict = {}                                 # target -> (level, header_node)
    for h in graph.objects(table, TAB.hasHeaderNode):
        lc = graph.value(h, TAB.hasLabel)
        label[h] = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
        parent[h] = graph.value(h, TAB.parentHeader)
        lvl_lit = graph.value(h, TAB.headerLevel)
        lvl = int(lvl_lit) if lvl_lit is not None else 0
        for u in graph.objects(h, cover_pred):
            if u not in best or lvl > best[u][0]:
                best[u] = (lvl, h)
    paths: dict = {}
    for u, (_, h) in best.items():
        parts: list = []
        cur = h
        while cur is not None:
            parts.append(label.get(cur, ""))
            cur = parent.get(cur)
        paths[u] = " > ".join(reversed(parts))
    return paths


def _column_header_path(graph: Graph, table) -> dict:
    """Column paths (deepest coversColumn header walked to root). Single label per column for a flat
    RecordTable (backward compatible)."""
    return _header_path(graph, table, TAB.coversColumn)


def _row_header_path(graph: Graph, table) -> dict:
    """Row paths (deepest coversRow header walked to root) — a cross-tab's row identity. {} when the
    table has no row-header tree (RecordTable / plain hierarchical)."""
    return _header_path(graph, table, TAB.coversRow)
```

(c) In `table_records`, compute the row path once per table and use it as the record id. Change the per-table body so that, alongside `header = _column_header_path(graph, t)`, it also has `row_path = _row_header_path(graph, t)`, and the final append uses:

```python
        header = _column_header_path(graph, t)
        row_path = _row_header_path(graph, t)
        rows: dict = {}
        # ... (unchanged EntryCell loop) ...
        for row in sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r])):
            cells = [c for _, _, c in sorted(rows[row], key=lambda kc: kc[0])]
            rid = row_path.get(row, str(row).split("#")[-1])
            out.append(Record(rid, tuple(cells)))
```

(d) Add a URI-safe subject helper and use it in `ground_document` (replace the `subject = URIRef("urn:iladub:record:" + rec.row_id)` line):

```python
def _record_uri(row_id: str) -> URIRef:
    """Mint a URI-safe record subject from a row id. Preserves an already-safe opaque fragment
    (e.g. 'table0-r1'); slugs a header path ('Region > North' -> 'Region_North')."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", row_id).strip("_") or "record"
    return URIRef("urn:iladub:record:" + slug)
```

and in `ground_document`:

```python
        subject = _record_uri(rec.row_id)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `./.venv/bin/python -m pytest tests/test_concept_feed.py -v`
Expected: all pass (cross-tab row identity + named subjects GREEN; `_row_header_path` unit GREEN; backward-compat + all shipped concept-feed tests still GREEN — the DRY refactor produces identical `_column_header_path` output, and the slug preserves opaque ids).

- [ ] **Step 5: Run the full suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/ -q`
Expected: all pass. The change is confined to `feed.py`; `ground_concept`, the etkl compiler, and all shapes are untouched. (A benign rdflib "Failed to convert Literal lexical form" warning on an out-of-range grounding attempt is expected.)

- [ ] **Step 6: Commit**

```bash
git add src/iladub/feed.py tests/test_concept_feed.py
git commit -m "feat(iladub): matrix/cross-tab feed — row-header path as record identity (named subjects); DRY header-path walk"
```

---

## Self-Review

**Spec coverage:**
- `_row_header_path` via coversRow (+ DRY `_header_path`) → Task 1 Step 3. ✓
- Row-header path as `row_id` in `table_records` → Task 1 Step 3(c). ✓
- URI-safe subject minting in `ground_document` → Task 1 Step 3(d). ✓
- Cross-tab row-identity test (RED-checked) → `test_crosstab_records_identified_by_row_header_path`. ✓
- `_row_header_path` present-for-crosstab / empty-otherwise → `test_row_header_path_present_for_crosstab_empty_otherwise`. ✓
- Backward compat (RecordTable row_ids opaque, unchanged) → `test_recordtable_row_ids_unchanged_opaque` + existing suite green. ✓
- E2E named subjects (North/South), records=2, grounded>0, proposed>0 → `test_crosstab_grounds_to_named_subjects_end_to_end`. ✓
- §8 PROCEDURAL (RDF reads, no tuned constant); §7 residue quarantined → feed docstrings + E2E `proposed > 0`. ✓
- Row-header-as-concept + multi-word cells out of scope → Global Constraints (no such code). ✓

**Placeholder scan:** none — full code + exact commands, every assertion probe-validated (2 records North/South, subjects named, grounded 2 / proposed 10 observed; robust `>0` used).

**Type consistency:** `_header_path(graph, table, cover_pred) -> dict`, `_column_header_path(graph, table)`, `_row_header_path(graph, table)`, `_record_uri(row_id) -> URIRef`, `table_records(graph) -> list[Record]` (signature unchanged), `Record(row_id, concepts)`, `ground_document(graph, contract, proposer, terms, shapes, g) -> FeedResult`, `MappingGroundingProposer(mapping)`, `GroundingProposal(field_iri, anchor_iri, confidence, rationale, suggester_iri)` used identically and match shipped signatures. ✓
