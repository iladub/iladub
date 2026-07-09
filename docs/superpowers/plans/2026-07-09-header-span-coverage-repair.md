# Header-Span Coverage Repair (Loop 8-pre) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix `infer_header_tree` so a short parent label over a wide column span covers its full span (a single `Region` parent recovers all of `North/South/East/West`), without changing any already-tiling tree.

**Architecture:** An additive `repair_coverage` step inside `infer_header_tree`, applied to the text-extent nodes **before** parent-linking: extend each coarse (non-leaf) node to absorb contiguous adjacent leaf columns that have no parent at that node's level, excluding the col-0 stub. Extends only; never removes/overlaps; no-op when the tree already tiles.

**Tech Stack:** Python 3, pytest.

## Global Constraints

- **No regression (the whole point):** every existing hierarchical / pivot / matrix / row-grouped fixture must compile with IDENTICAL header-node covers — the repair fires only on coverage gaps (probe-confirmed: the `Current Visit`/`Prior Visit` pivot is unchanged).
- **Additive & tiling-preserving:** the repair only *adds* an orphaned leaf to a *spatially adjacent* parent; the `tab:` SHACL (coverage / no-overlap / refinement / unambiguous) remains the certifier.
- **Stub convention:** column 0 is the stub — never absorbed; it stays its own orphan-promoted node.
- **Reuse** the existing `HeaderNode` dataclass; do not touch `_covers_for_cell` (text-extent, correct for multi-word/wrapped labels).

**Confirmed by probe (2026-07-09):** the repair turns `Region [1,2,3]` into `[1,2,3,4]` on the region-pivot and leaves the existing pivot's covers untouched.

---

### Task 1: `repair_coverage` + wire into `infer_header_tree` + tests

**Files:**
- Modify: `src/iladub/etkl/headers.py`
- Modify: `tests/etkl/fixtures.py` (append `region_pivot_pdf`)
- Test: `tests/etkl/test_headers.py`

**Interfaces:**
- Consumes: `HeaderNode` (headers.py), `grid.ncols`.
- Produces: `repair_coverage(nodes, ncols) -> list[HeaderNode]`; `infer_header_tree` calls it before parent-linking.

- [ ] **Step 1: Write the failing tests**

Append to `tests/etkl/test_headers.py` (import as needed):

```python
def test_repair_noop_on_tiling_tree():
    from dataclasses import replace
    from iladub.etkl.headers import repair_coverage, HeaderNode
    # a tree that already tiles: two level-0 parents over 6 leaves + a stub leaf at col 0
    nodes = [HeaderNode(0, (1, 2, 3), "A", None), HeaderNode(0, (4, 5, 6), "B", None),
             HeaderNode(1, (0,), "stub", None)] + [HeaderNode(1, (i,), str(i), None) for i in range(1, 7)]
    out = repair_coverage(list(nodes), 7)
    assert {(n.level, n.covers, n.text) for n in out} == {(n.level, n.covers, n.text) for n in nodes}


def test_repair_absorbs_adjacent_orphan_not_stub():
    from iladub.etkl.headers import repair_coverage, HeaderNode
    # 'Region' covers [1,2,3]; col 4 (West) orphaned at level 0; col 0 is the stub
    nodes = [HeaderNode(0, (1, 2, 3), "Region", None),
             HeaderNode(1, (0,), "Year", None)] + [HeaderNode(1, (i,), n, None)
             for i, n in zip(range(1, 5), ["North", "South", "East", "West"])]
    out = repair_coverage(list(nodes), 5)
    region = next(n for n in out if n.text == "Region")
    assert set(region.covers) == {1, 2, 3, 4}          # West absorbed
    assert 0 not in region.covers                      # stub NOT absorbed


def test_short_parent_covers_full_span_end_to_end(tmp_path):
    import pytest
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    # the 'Region' header node covers all four region leaf columns
    region = next(h for h in rep.graph.subjects(RDF.type, TAB.HeaderNode)
                  if str(rep.graph.value(rep.graph.value(h, TAB.hasLabel), TAB.cellText)) == "Region")
    assert len(list(rep.graph.objects(region, TAB.coversColumn))) == 4
```

- [ ] **Step 2: Add the fixture**

Append to `tests/etkl/fixtures.py` (probe-verified geometry — single spanning `Region` over four wide numeric leaf columns + a `Year` stub, staying one band):

```python
def region_pivot_pdf(path: str) -> dict:
    """A single spanning parent 'Region' over four WIDE numeric leaf columns
    (North/South/East/West) + a 'Year' stub. The short 'Region' label under-covers
    its span under text-extent recovery; repair_coverage must extend it to all four."""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((leaves[0] + leaves[3]) / 2.0, PAGE_H - 90.0, "Region")
    for x, n in zip(leaves, ["North", "South", "East", "West"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(60.0, PAGE_H - 104.0, "Year")
    c.setFont("Courier", 10)
    for i, (yr, vals) in enumerate([("2020", ["10", "20", "30", "40"]),
                                    ("2021", ["11", "21", "31", "41"])]):
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(60.0, y, yr)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"parent": "Region", "values": ["North", "South", "East", "West"], "stub": "Year"}
```

- [ ] **Step 3: Run to verify failure**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest tests/etkl/test_headers.py -q -k "repair or short_parent"`
Expected: FAIL (ImportError on `repair_coverage`; end-to-end shows `Region` covering 3, not 4).

- [ ] **Step 4: Implement `repair_coverage` + wire it**

In `src/iladub/etkl/headers.py`, add `from dataclasses import replace` to the imports if not present, and add:

```python
def repair_coverage(nodes: list[HeaderNode], ncols: int) -> list[HeaderNode]:
    """Extend each coarse (non-leaf) header node to absorb contiguous adjacent leaf
    columns that have no parent at that node's level, excluding column 0 (the stub).

    A short parent label over a wide span is under-covered by text-extent recovery
    (its ink does not reach the outer columns). This repair fills such coverage gaps
    by extending the spatially adjacent parent — additive only (never removes or
    overlaps), so the result still tiles. It is a no-op when the tree already tiles.
    """
    if not nodes:
        return nodes
    out = list(nodes)
    max_level = max(n.level for n in out)
    for lvl in range(max_level):                      # non-leaf levels only
        covered = set()
        for n in out:
            if n.level == lvl:
                covered.update(n.covers)
        orphans = [c for c in range(ncols) if c not in covered and c != 0]
        for c in orphans:
            for i, n in enumerate(out):
                if n.level == lvl and n.covers and (max(n.covers) == c - 1 or min(n.covers) == c + 1):
                    out[i] = replace(n, covers=tuple(sorted(set(n.covers) | {c})))
                    covered.add(c)
                    break
    return out
```

Then in `infer_header_tree`, insert the call between the `nodes` construction and the parent-linking loop:

```python
    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            covers = _covers_for_cell(cell, b)
            nodes.append(HeaderNode(lvl, covers, cell.text, None))

    nodes = repair_coverage(nodes, grid.ncols)        # <-- fill short-parent coverage gaps

    # Link each node to its nearest parent ...
    linked: list[HeaderNode] = []
    ...
```

(The parent-linking loop is unchanged — it now sees the extended covers, so `West`'s leaf node links `parentHeader Region`.)

- [ ] **Step 5: Run the targeted tests + FULL suite (the regression guard)**

Run: `PYTHONPATH="$PWD/src" python3 -m pytest -q`
Expected: PASS — the three new tests, and every existing test (pivot / crosstab / hierarchical / row-grouped fixtures compile identically, since the repair is a no-op on already-tiling trees). If any pre-existing hierarchical test changes, the repair over-reached — stop and fix (it must only absorb orphans).

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/headers.py tests/etkl/fixtures.py tests/etkl/test_headers.py
git commit -m "fix(etkl): repair_coverage — extend a short parent to its full span (no-op on tiling trees)"
```

---

### Task 2: canvas note

**Files:** Modify `docs/loops/2026-07-05-table-holon-loop.md`.

- [ ] **Step 1:** Add a one-line note under the increments (or the field-of-possibles) that Loop 2's header-span recovery was hardened (short parent over a wide span now covers its full span via `repair_coverage`, additive/tiling-preserving), enabling single-spanning-parent pivots to be read as named dimensions (Loop 8a). Commit:

```bash
git add docs/loops/2026-07-05-table-holon-loop.md
git commit -m "docs(loop): note header-span coverage-repair hardening"
```

---

## Self-Review (author checklist — completed)

- **Spec coverage:** §2 repair → Task 1 Step 4; §3 tests → Task 1 Steps 1-5.
- **No-regression is explicit:** Task 1 Step 5 runs the full suite and states the abort condition (any existing hierarchical test change = over-reach).
- **Placeholder scan:** none — complete code for `repair_coverage`, the wiring, the fixture, and all three tests.
- **Type consistency:** `repair_coverage(nodes, ncols) -> list[HeaderNode]`; `HeaderNode` frozen dataclass `(level, covers, text, parent)`; `replace` used for the extension.
