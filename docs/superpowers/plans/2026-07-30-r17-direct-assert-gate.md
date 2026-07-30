# R17 Direct-Assert Gate Implementation Plan (Loop J)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the record and transposed region paths the scratch → `region_tiles` → commit-or-escalate membrane backstop, closing the last direct-assert crash class (R17).

**Architecture:** Two inline gates in `src/iladub/etkl/compile.py`, byte-matching the loop G pattern 80 lines below them. No new vocab/shapes/constants; commit-path accounting byte-identical.

**Tech Stack:** Python 3 + rdflib, pySHACL via the existing `region_tiles`, pytest. Spec: `docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md`.

## Global Constraints

- **Commit-path behavior must be byte-identical:** for a healthy region, the same triples reach `graph`, the same `asserted_total`/`escalated_total` arithmetic runs, the same report is appended. Only the defective-region outcome changes (crash → in-band escalation).
- `REGION_TILING_FAILED` is the escalation reason; anchor `TAB.RecordTable` (both paths assert a RecordTable); confidence `0.4` (the shipped escalation convention).
- No new numeric constant, no vocab change, no shape change.
- Never weaken tests; the red tests must be shown to fail (raise) before the gate lands.
- Canonical test command: `. .venv/bin/activate && python3 -m pytest -q <paths>` from repo root, FOREGROUND (bare python3 = wrong rdflib). Full suite ~170 s, timeout ≥ 400000 ms. Baseline: 673 passed / 5 skipped.
- Never commit the GrainCorp PDF.

## File Structure

- Modify: `src/iladub/etkl/compile.py` (transposed branch ~line 196; record branch ~line 245; loop G NOTE comment ~line 325)
- Create: `tests/etkl/test_r17_gate.py`
- Modify: `docs/superpowers/residues.md` (delete the R17 row)

---

### Task 1: The gate on both paths (TDD, one task — the two sites are the same 6-line transformation)

**Files:**
- Modify: `src/iladub/etkl/compile.py`
- Test: `tests/etkl/test_r17_gate.py` (create)

**Interfaces:**
- Consumes: `assert_record_region(g, region, table_uri, doc, page) -> int` (imported at compile.py top, line 19); `assert_transposed_region(g, region, table_uri, doc, page) -> int` (imported inside the transposed branch); `region_tiles(g) -> bool` (`iladub.etkl.tiling`); `escalate_region(graph, cand_uri, doc, ascii_view, reason, anchor, confidence)`.
- Produces: no new interfaces — control-flow only.

- [ ] **Step 1: Write the failing tests**

Create `tests/etkl/test_r17_gate.py`:

```python
"""Loop J — R17: the record and transposed paths get the membrane backstop.

A defective region on these paths used to RAISE at compile_tables' final validation
(AssertionError, tab:CoverageShape — the loop G attempt-1 crash class, demonstrated in the
loop G final review by dropping one tab:coversColumn). With the gate, the region escalates
in-band as REGION_TILING_FAILED and the rest of the document survives (§7).
See docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md.
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")


def _corrupting(real):
    """Wrap an assert_* function: call it, then delete ONE coversColumn triple from the
    graph it wrote into — the exact R17 demonstration from the loop G final review."""
    def wrapped(g, *args, **kwargs):
        n = real(g, *args, **kwargs)
        t = next(iter(g.triples((None, TAB.coversColumn, None))))
        g.remove(t)
        return n
    return wrapped


def test_defective_record_region_escalates_instead_of_raising(tmp_path, monkeypatch):
    import iladub.etkl.compile as C
    from tests.etkl import fixtures as F
    monkeypatch.setattr(C, "assert_record_region", _corrupting(C.assert_record_region))
    p = os.path.join(str(tmp_path), "rec.pdf")
    F.simple_table_pdf(p)
    rep = C.compile_tables(p)                      # must NOT raise
    assert any(r.verdict == "escalated" and r.reason == "REGION_TILING_FAILED"
               for r in rep.regions), [(r.verdict, r.reason) for r in rep.regions]
    assert not any(r.verdict == "asserted" for r in rep.regions)


def test_defective_transposed_region_escalates_instead_of_raising(tmp_path, monkeypatch):
    import iladub.etkl.holon as H
    import iladub.etkl.compile as C
    from tests.etkl import fixtures as F
    monkeypatch.setattr(H, "assert_transposed_region",
                        _corrupting(H.assert_transposed_region))
    p = os.path.join(str(tmp_path), "tr.pdf")
    F.transposed_table_pdf(p)
    rep = C.compile_tables(p)                      # must NOT raise
    assert any(r.verdict == "escalated" and r.reason == "REGION_TILING_FAILED"
               for r in rep.regions), [(r.verdict, r.reason) for r in rep.regions]


def test_healthy_record_region_is_untouched(tmp_path):
    from iladub.etkl.compile import compile_tables
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "rec.pdf")
    F.simple_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions)
    assert not any(r.reason == "REGION_TILING_FAILED" for r in rep.regions)
    assert rep.score == 1.0


def test_healthy_transposed_region_is_untouched(tmp_path):
    from iladub.etkl.compile import compile_tables
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "tr.pdf")
    F.transposed_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions)
    assert not any(r.reason == "REGION_TILING_FAILED" for r in rep.regions)
```

NOTE for the implementer: if `_corrupting`'s `next(iter(...))` finds no coversColumn triple
on the transposed path (check what `assert_transposed_region` emits — it may use different
predicates), pick the equivalent load-bearing triple that `region_tiles` guards (e.g. a
`tab:hasLeafColumn` or the header-coverage triple) and note the substitution in your report.
The point is: corrupt ONE membrane-guarded triple. Verify on the UNGATED code that the
corruption raises (that is the red).

- [ ] **Step 2: Run the tests — the two defective-path tests must currently RAISE (red)**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_r17_gate.py -q`
Expected: the two `defective_*` tests FAIL with an `AssertionError` raised from inside
`compile_tables` (the final-validation crash — that is the R17 behavior being fixed). The
two `healthy_*` tests should already PASS. If a defective test fails with a clean
assertion-message about reports instead of an in-compile crash, STOP: the corruption did
not reach the membrane — re-check the wrapped function and predicate.

- [ ] **Step 3: Gate the transposed site**

In `src/iladub/etkl/compile.py`, the transposed branch currently reads:

```python
                    from .holon import assert_transposed_region
                    table_uri = URIRef(f"{_DOC}#ttable{idx}")
                    n = assert_transposed_region(graph, region, table_uri, _DOC, page_number)
                    b = region.grid.boundaries
                    value_cells = [c for c in region.cells if c.col >= 1]
                    asserted_total += sum(len(c.words) for c in value_cells if cell_round_trips(c, b))
                    escalated_total += sum(len(c.words) for c in value_cells if not cell_round_trips(c, b))
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.RecordTable), ascii_view))
```

Replace with:

```python
                    from .holon import assert_transposed_region
                    from .tiling import region_tiles
                    table_uri = URIRef(f"{_DOC}#ttable{idx}")
                    # R17 gate (loop J): scratch -> region_tiles -> commit-or-escalate, the
                    # same backstop as the hierarchical/matrix/row-hier paths. A defective
                    # region escalates in-band instead of crashing final validation.
                    scratch = Graph()
                    n = assert_transposed_region(scratch, region, table_uri, _DOC, page_number)
                    if n and not region_tiles(scratch):
                        cand_uri = URIRef(f"{_DOC}#region{idx}")
                        escalate_region(graph, cand_uri, _DOC, ascii_view,
                                        "REGION_TILING_FAILED", TAB.RecordTable, 0.4)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.RecordTable), ascii_view))
                    else:
                        graph += scratch
                        b = region.grid.boundaries
                        value_cells = [c for c in region.cells if c.col >= 1]
                        asserted_total += sum(len(c.words) for c in value_cells if cell_round_trips(c, b))
                        escalated_total += sum(len(c.words) for c in value_cells if not cell_round_trips(c, b))
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.RecordTable), ascii_view))
```

(`Graph` is already imported at the top of compile.py — verify, and add the import only if
missing.)

- [ ] **Step 4: Gate the record site**

The record branch currently reads:

```python
                table_uri = URIRef(f"{_DOC}#table{idx}")
                n = assert_record_region(graph, region, table_uri, _DOC, page_number)
                b = region.grid.boundaries
                data_cells = [c for c in region.cells if c.row > 0]
                asserted_total += sum(len(c.words) for c in data_cells if cell_round_trips(c, b))
                escalated_total += sum(len(c.words) for c in data_cells if not cell_round_trips(c, b))
                reports.append(RegionReport(region.kind, "asserted", n, None,
                                            str(TAB.RecordTable), ascii_view))
```

Replace with the same shape:

```python
                from .tiling import region_tiles
                table_uri = URIRef(f"{_DOC}#table{idx}")
                # R17 gate (loop J): see the transposed branch above.
                scratch = Graph()
                n = assert_record_region(scratch, region, table_uri, _DOC, page_number)
                if n and not region_tiles(scratch):
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view,
                                    "REGION_TILING_FAILED", TAB.RecordTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0,
                                                "REGION_TILING_FAILED",
                                                str(TAB.RecordTable), ascii_view))
                else:
                    graph += scratch
                    b = region.grid.boundaries
                    data_cells = [c for c in region.cells if c.row > 0]
                    asserted_total += sum(len(c.words) for c in data_cells if cell_round_trips(c, b))
                    escalated_total += sum(len(c.words) for c in data_cells if not cell_round_trips(c, b))
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.RecordTable), ascii_view))
```

IMPORTANT wiring note: the monkeypatch in the record red test patches
`iladub.etkl.compile.assert_record_region` (module-top import). Keep that import style —
do not move the import inside the branch, or the test's patch point changes.

- [ ] **Step 5: Update the loop G NOTE comment**

In the hierarchical backstop comment (~line 325), delete the sentence beginning "NOTE the
record and transposed paths (assert_record_region / assert_transposed_region above) are
STILL direct-assert" through "this gate covers this path only." and replace with:
`# Loop J closed R17: the record and transposed paths now carry the same gate.`

- [ ] **Step 6: Run the new tests + the record/transposed neighborhoods**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_r17_gate.py tests/etkl/test_compile_pipeline.py -q`
(If `test_compile_pipeline.py` is not the real name, find the compile-pipeline tests:
`ls tests/etkl | grep -iE "compile|pipeline|holon|transposed"` and run those.)
Expected: all PASS — the two red tests now see `REGION_TILING_FAILED` escalations.

- [ ] **Step 7: Full suite (foreground, ≥ 400 s timeout)**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: 673 + 4 new = 677 passed, 5 skipped. If any shipped record/transposed test fails,
the gate changed healthy-path behavior — a plan violation; diff the failing fixture's
compile before/after (the commit path must be byte-identical).

- [ ] **Step 8: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_r17_gate.py
git commit -m "feat(etkl): R17 gate — record and transposed paths escalate REGION_TILING_FAILED instead of crashing (loop J)"
```

---

### Task 2: Verification + docs (controller-run; needs the local GrainCorp PDF)

**Files:**
- Modify: `docs/superpowers/residues.md` (delete the R17 row)
- Modify: `docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md` (status line)

- [ ] **Step 1: Isomorphism probe (spec §3's cross-version check, recorded in ledger)**

Compile `simple_table_pdf` and `transposed_table_pdf` at HEAD and at the pre-change commit
(`git stash` the working tree or use the parent commit in a temp worktree); compare with
`rdflib.compare.isomorphic` — must be True for both. Record the result in
`.superpowers/sdd/progress.md`.

- [ ] **Step 2: GrainCorp confirmation**

Score 0.9496 / cells 509 / 15 groups / 17 detected / 33 records — ALL unchanged
(failure condition).

- [ ] **Step 3: Register + spec status**

Delete the R17 row from `docs/superpowers/residues.md` (also update the R13 row's
parenthetical "(the record/transposed paths remain direct-assert — see R17)" to note the
closure). Spec status → Shipped with measured numbers.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md
git commit -m "docs(loop-J): close R17 — register row deleted, spec status with measured numbers"
```

---

## Self-Review

- **Spec coverage:** §2.1 → Task 1 Step 3; §2.2 → Step 4; §2.3 → Step 5 + Task 2 Step 3;
  §3 red/healthy tests → Step 1; §3 isomorphism probe → Task 2 Step 1; §1 criteria → Task 2.
- **Placeholder scan:** the only deliberately-open items carry find-first instructions
  (the transposed corruption predicate; the compile-test filename) rather than guesses.
- **Type consistency:** gate blocks reuse the exact loop G names (`scratch`, `cand_uri`,
  `REGION_TILING_FAILED`, confidence 0.4); the record red test's patch point matches the
  module-top import kept by Step 4's wiring note.
