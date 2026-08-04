# Loop P — Grid-Region Scoping + Header-Row Welding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ruled section bands read correctly when the author's box contains full-width strips (key heading, notices) above an interior-ruled grid whose header row wraps across several visual lines — closing R42 gap (a) on the CBH stem (spec `docs/superpowers/specs/2026-08-04-cbh-dimension-split-design.md` §3, diagnosis CORRECTION block).

**Architecture:** Two evidence-positive author-mark tests. (1) **Grid-region scoping (AXIOM):** a band line belongs to the ruled grid iff ≥1 *interior* vertical rule crosses it — derived by a SPARQL query over a per-band evidence graph (the loop-B2c `classifygraph` pattern); lines above the grid are peeled into `Band.captions` and CARRIED as `tab:RegionCaption` (loop C's class) on the asserted table. (2) **Header/wrapped-row welding (justified PROCEDURAL raw extraction, loop H's marks-are-delimiters mirrored):** consecutive re-extracted rows whose y-centers share one author-drawn full-width hrule box weld into ONE row, per-rule-column text joined top-to-bottom — the CBH 3-visual-line header becomes one 16-column header row (`Time Nom Accepted`). Both integrate at the existing seam `_build_ruled_band` (`src/iladub/etkl/compile.py:24`).

**Tech Stack:** Python 3 (`.venv`), rdflib SPARQL over transient evidence graphs, pdfplumber/reportlab fixtures, pytest.

**Doc impact:** increment — a loop-P entry in `docs/wiki/concepts/neurosymbolic-exemplars.md` (Task 4); no contradiction.

## Global Constraints

- **§8 gate:** the grid-membership decision is an AXIOM — `vocab/queries/grid-region.rq`, **zero numeric literals** (all geometry, including y-centers, emitted as facts by the PROCEDURAL emitter — the `header-covers.rq`/`tab:inkCenterX` precedent). The welding is **justified PROCEDURAL raw extraction** (chars → cells by author-drawn boxes, the `rule_aware_lines` class); its only merge licence is the *presence* of a drawn box containing both rows — no distance, no tuned constant. `COORD_EPS` (shipped) is the only epsilon permitted.
- **§5/§7 carry:** peeled lines are never dropped — every caption line lands as `tab:RegionCaption` (`tab:captionText`/`tab:captionRow`/`tab:hasCaption`, all existing terms) on the region's asserted table, or stays inside the band when the region escalates (escalation keeps the whole band's ascii view — unchanged behavior).
- **No overfitting:** CBH is the specimen, not the target. Every new behavior is pinned by a synthetic fixture; a counter-fixture (no strips above the grid) and the whole ruled fixture family must compile **byte-identically**; the GrainCorp stem must re-measure at exactly **0.9655 / 2152 cells / 133 records / 585 grounded / 1265 quarantined** (corpus battery `-k graincorp-stem`). Any deviation is a STOP-and-report, never an absorbed change.
- **Honest failure:** where the new evidence is absent (no interior rules, no full-width hrule boxes) behavior is byte-identical to main; the welding never splits rows, only merges within a drawn box.
- **Canonical test command:** `./.venv/bin/python -m pytest` (bare `python3` = wrong rdflib). System `git` is broken this session — use `/opt/homebrew/bin/git` (or `export PATH="/opt/homebrew/bin:$PATH"` first).
- Branch: `loop-p-grid-region` off `main`. Commit trailer: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Suite baseline before this loop: 825 passed / 5 skipped non-corpus (+1 machine-local scrubbed-env release-gate failure — environmental, ignore), 19 corpus tests of which `financial/apple…` is a deliberate red (R41 — unrelated; must STAY red).

## File Structure

| File | Responsibility |
|---|---|
| `tests/etkl/fixtures.py` (modify) | `sectioned_ruled_table_pdf(path)` — the CBH-shaped synthetic: heading + notice strips over an interior-ruled grid with a 2-hrule header box wrapping one column name across two visual lines. |
| `tests/etkl/test_grid_region.py` (create) | The loop's battery: red E2E pin, evidence/derivation units, welding units, counter-fixture no-regression pins. |
| `src/iladub/etkl/gridregion.py` (create) | PROCEDURAL layer of the AXIOM: emit the per-band line/rule evidence graph, run `grid-region.rq`, return grid line indices. No decision logic. |
| `vocab/queries/grid-region.rq` (create) | The grid-membership derivation (open world; the band is the closure boundary). |
| `vocab/ontology/tab.ttl` (modify) | New owned terms for the evidence facts (only those not already present); `owl:versionInfo` bump. |
| `src/iladub/etkl/geometry.py` (modify) | `weld_hrule_boxes(relines, hrules, rule_xs) -> list[Line]` — box-licensed row welding. |
| `src/iladub/etkl/bands.py` (modify) | `Band.captions: tuple[Line, ...] = ()` (additive, default empty). |
| `src/iladub/etkl/compile.py` (modify) | `_build_ruled_band` peels captions + welds; assert sites emit the carried captions. |

---

### Task 1: The sectioned-ruled fixture and the red pins

**Files:**
- Modify: `tests/etkl/fixtures.py`
- Test: `tests/etkl/test_grid_region.py`

**Interfaces:**
- Produces: `sectioned_ruled_table_pdf(path: str) -> dict` returning `{"cols": [x0,x1,x2,x3,x4], "header_names": ["ID", "Time Nom Accepted", "Client", "Volume"], "caption_texts": ["GERALDTON", "BERTH MAY BE UNAVAILABLE 2000HRS"]}`. Tasks 2–4 import it from `tests.etkl.fixtures`.

- [ ] **Step 1: Create the branch**

```bash
cd "/Volumes/WD Green/dev/git/iladub"
/opt/homebrew/bin/git checkout -b loop-p-grid-region main
```

- [ ] **Step 2: Write the fixture builder**

Append to `tests/etkl/fixtures.py` (imitate the existing builders' reportlab idiom — Courier, explicit coordinates; reportlab's y-axis is bottom-up, pdfplumber's top-down: keep every drawn object's *page-top* y in a local helper so the truth dict speaks pdfplumber coordinates):

```python
def sectioned_ruled_table_pdf(path):
    """The CBH shape (spec 2026-08-04 §3 CORRECTION): one author-drawn section box
    containing, top to bottom: a bare key heading, one notice line (both full-width
    strips no interior rule crosses), then an interior-ruled grid whose header row is
    ONE hrule-delimited box holding TWO visual text lines (col 1's name wraps:
    'Time Nom' / 'Accepted'; cols 0/2/3 are single-line, vertically centered), then
    three data rows. Interior vertical rules span ONLY the grid rows."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    H = letter[1]

    def y(top):                       # page-top -> reportlab bottom-up
        return H - top

    cols = [72, 172, 292, 392, 492]   # 4 columns: ID | Time Nom Accepted | Client | Volume
    sec_top, grid_top, hdr_bot, grid_bot = 60, 110, 140, 200
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Courier", 9)
    # the section OUTER border (spans heading + notice + grid, like CBH's)
    c.rect(cols[0], y(grid_bot), cols[-1] - cols[0], grid_bot - sec_top, stroke=1, fill=0)
    # full-width strips: heading + notice (NO interior rules up here)
    c.drawString(cols[0] + 4, y(sec_top + 14), "GERALDTON")
    c.drawString(cols[0] + 4, y(sec_top + 30), "BERTH MAY BE UNAVAILABLE 2000HRS")
    # interior vertical rules: GRID ROWS ONLY (grid_top..grid_bot)
    for x in cols[1:-1]:
        c.line(x, y(grid_bot), x, y(grid_top))
    # full-width hrules: grid top, header-box bottom, grid bottom
    for hy in (grid_top, hdr_bot, grid_bot):
        c.line(cols[0], y(hy), cols[-1], y(hy))
    # header box (grid_top..hdr_bot) with TWO visual lines: line A tops the wrapped
    # name, line B carries the centered single-line names + the wrap's second word
    c.drawString(cols[1] + 4, y(grid_top + 12), "Time Nom")
    c.drawString(cols[0] + 4, y(grid_top + 24), "ID")
    c.drawString(cols[1] + 4, y(grid_top + 24), "Accepted")
    c.drawString(cols[2] + 4, y(grid_top + 24), "Client")
    c.drawString(cols[3] + 4, y(grid_top + 24), "Volume")
    # three data rows
    rows = [("10097", "15:01", "Brahman", "30,000"),
            ("10076", "14:38", "CBH", "50,000"),
            ("10118", "11:28", "Cargill", "48,904")]
    for k, row in enumerate(rows):
        ry = hdr_bot + 16 + 18 * k
        for x, cell in zip(cols, row):
            c.drawString(x + 4, y(ry), cell)
    c.save()
    return {"cols": cols,
            "header_names": ["ID", "Time Nom Accepted", "Client", "Volume"],
            "caption_texts": ["GERALDTON", "BERTH MAY BE UNAVAILABLE 2000HRS"]}
```

- [ ] **Step 3: Write the red E2E pin**

Create `tests/etkl/test_grid_region.py`:

```python
"""Loop P (spec 2026-08-04 §3): grid-region scoping + hrule-box header welding."""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF

from iladub.etkl import compile_tables
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import sectioned_ruled_table_pdf


def _compiled_fixture(tmp_path):
    pdf = tmp_path / "section.pdf"
    truth = sectioned_ruled_table_pdf(str(pdf))
    return truth, compile_tables(str(pdf))


def test_sectioned_ruled_table_reads(tmp_path):
    """RED on main: the heading/notice strips enter the header tree as fabricated
    all-column levels and the wrapped header box reads as several rows -> the section
    escalates (or asserts a garbage reading). GREEN when: exactly one asserted table,
    the four column names correct incl. the welded 'Time Nom Accepted', 12 data cells."""
    truth, rep = _compiled_fixture(tmp_path)
    asserted = [r for r in rep.regions if r.verdict == "asserted"]
    assert len(asserted) == 1, [(r.kind.name, r.verdict, r.reason) for r in rep.regions]
    texts = {str(o) for o in rep.graph.objects(None, TAB.hasLabel)} | \
            {str(o) for s in rep.graph.subjects(RDF.type, TAB.HeaderNode)
             for o in rep.graph.objects(s, TAB.hasLabel)}
    # hasLabel points at label NODES on some paths; fall back to any literal text field.
    # The load-bearing assertion is on the WELDED name reaching the reading:
    flat = " ".join(str(t) for t in rep.graph.objects(None, None)
                    if hasattr(t, "value") or isinstance(t, str))
    for name in truth["header_names"]:
        assert name in flat, f"header name {name!r} missing from the reading"
    assert rep.score >= 0.9, rep.score


def test_sectioned_captions_carried(tmp_path):
    """§5/§7: the peeled strips are CARRIED as tab:RegionCaption, never dropped."""
    truth, rep = _compiled_fixture(tmp_path)
    caps = {str(t) for c in rep.graph.subjects(RDF.type, TAB.RegionCaption)
            for t in rep.graph.objects(c, TAB.captionText)}
    for text in truth["caption_texts"]:
        assert any(text in c for c in caps), (text, caps)
```

NOTE to implementer: the first test's `flat` scan is deliberately liberal at RED time;
once Task 3 lands, tighten it to read the leaf header labels the way
`tests/etkl/test_header_stack.py` reads them (imitate its accessor), and keep BOTH the
tightened form and the caption test. Record the tightening in the task report.

- [ ] **Step 4: Run to verify RED**

Run: `./.venv/bin/python -m pytest tests/etkl/test_grid_region.py -v`
Expected: both tests FAIL on main's behavior (escalation or missing welded name /
missing captions). Paste the actual region verdicts into the task report — this pins
main's misreading as evidence.

- [ ] **Step 5: Commit**

```bash
/opt/homebrew/bin/git add tests/etkl/fixtures.py tests/etkl/test_grid_region.py
/opt/homebrew/bin/git commit -m "test(loop-p): sectioned-ruled fixture + red pins (R42 gap a)"
```

---

### Task 2: Grid-region scoping — evidence graph, AXIOM query, caption peel + carry

**Files:**
- Create: `src/iladub/etkl/gridregion.py`
- Create: `vocab/queries/grid-region.rq`
- Modify: `vocab/ontology/tab.ttl` (new terms + versionInfo bump)
- Modify: `src/iladub/etkl/bands.py` (Band.captions field)
- Modify: `src/iladub/etkl/compile.py` (`_build_ruled_band` peel; assert-site caption emission)
- Test: `tests/etkl/test_grid_region.py` (unit additions)

**Interfaces:**
- Consumes: `Band`, `Rule` (geometry), the fixture from Task 1.
- Produces: `grid_lines(sub: Band, sub_rules: Sequence[Rule]) -> set[int]` (indices into `sub.lines` that are INSIDE the grid; empty set when the derivation abstains — <2 distinct rule x's, or no interior rule); `Band.captions: tuple[Line, ...]`; caption triples on asserted ruled tables. Task 3 welds only the grid lines; Task 4 measures.

- [ ] **Step 1: Write the failing unit tests** (append to `tests/etkl/test_grid_region.py`)

```python
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word


def _line(top, bottom, *texts):
    x = 80.0
    ws = []
    for t in texts:
        ws.append(Word(t, x, x + 8.0 * len(t), top, bottom))
        x += 8.0 * len(t) + 10
    return Line(tuple(ws), top, bottom)


def test_grid_lines_interior_rule_presence():
    """A line is grid iff an INTERIOR rule (x strictly between the band's outermost
    rule x's) crosses it. Outer-border segments never make a line grid."""
    from iladub.etkl.gridregion import grid_lines
    lines = (_line(60, 70, "HEADING"),          # above interior rules
             _line(75, 85, "NOTICE", "TEXT"),    # above interior rules
             _line(110, 120, "A", "B"),          # crossed by interior rules
             _line(130, 140, "1", "2"))          # crossed by interior rules
    band = Band(lines, 60.0, 140.0)
    rules = [Rule(72.0, 58.0, 145.0),            # outer left (full extent)
             Rule(300.0, 58.0, 145.0),           # outer right
             Rule(150.0, 105.0, 145.0),          # INTERIOR: grid rows only
             Rule(220.0, 105.0, 145.0)]
    assert grid_lines(band, rules) == {2, 3}


def test_grid_lines_abstains_without_interior_rules():
    """Only the two outer rules -> no interior evidence -> abstain (empty set):
    behavior falls back to main's, byte-identical."""
    from iladub.etkl.gridregion import grid_lines
    lines = (_line(60, 70, "A", "B"), _line(80, 90, "1", "2"))
    band = Band(lines, 60.0, 90.0)
    rules = [Rule(72.0, 55.0, 95.0), Rule(300.0, 55.0, 95.0)]
    assert grid_lines(band, rules) == set()


def test_grid_region_query_has_no_numeric_literal():
    """§8: the derivation reads facts only; every number is emitted by the
    PROCEDURAL layer (the header-covers.rq / tab:inkCenterX precedent)."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/grid-region.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)          # strip comments
    assert not re.search(r"\b\d+\.?\d*\b", body), "numeric literal in the AXIOM"
```

- [ ] **Step 2: Run to verify they fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_grid_region.py -v -k "grid_lines or numeric"`
Expected: ImportError / FileNotFoundError (`gridregion`, `grid-region.rq` absent).

- [ ] **Step 3: Add the owned terms**

In `vocab/ontology/tab.ttl` — FIRST grep the file for each name; add ONLY the missing
ones (loop-B2c lesson: grep the target ttl before adding vocab), next to the
`tab:ClassifyBand` block, same style; bump `owl:versionInfo` per the file's habit:

```turtle
tab:BandLine a owl:Class ; rdfs:label "Band line (evidence)"@en ;
    rdfs:comment "Transient evidence: one visual line of a ruled band, with its vertical ink extent and center emitted as facts (loop P)."@en .
tab:lineIndex a owl:DatatypeProperty ; rdfs:domain tab:BandLine ; rdfs:range xsd:integer .
tab:lineCenterY a owl:DatatypeProperty ; rdfs:domain tab:BandLine ; rdfs:range xsd:decimal .
tab:RuleSpan a owl:Class ; rdfs:label "Vertical rule span (evidence)"@en ;
    rdfs:comment "Transient evidence: one author-drawn vertical rule segment (x, y-extent) of a ruled band (loop P)."@en .
tab:ruleX a owl:DatatypeProperty ; rdfs:domain tab:RuleSpan ; rdfs:range xsd:decimal .
tab:ruleTop a owl:DatatypeProperty ; rdfs:domain tab:RuleSpan ; rdfs:range xsd:decimal .
tab:ruleBottom a owl:DatatypeProperty ; rdfs:domain tab:RuleSpan ; rdfs:range xsd:decimal .
```

- [ ] **Step 4: Write the AXIOM query**

Create `vocab/queries/grid-region.rq`:

```sparql
# grid-region.rq — which band lines are INSIDE the ruled grid (loop P AXIOM).
# Open-world derivation over the per-band evidence graph (the band is the closure
# boundary — the MIN/MAX aggregation closes within the one transient graph).
# A line is a grid line iff at least one INTERIOR vertical rule crosses its center:
# interior = a rule strictly between the band's outermost rule x-positions (the outer
# border of the author's section box never counts). Every number here is a FACT
# emitted by gridregion.py (raw geometry) — this query contains no numeric literal.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?idx WHERE {
  ?line a tab:BandLine ; tab:lineIndex ?idx ; tab:lineCenterY ?cy .
  FILTER EXISTS {
    ?r a tab:RuleSpan ; tab:ruleX ?x ; tab:ruleTop ?rt ; tab:ruleBottom ?rb .
    FILTER(?rt <= ?cy && ?rb >= ?cy)
    FILTER(?x > ?minx && ?x < ?maxx)
  }
  {
    SELECT (MIN(?rx) AS ?minx) (MAX(?rx) AS ?maxx) WHERE {
      ?rr a tab:RuleSpan ; tab:ruleX ?rx .
    }
  }
}
```

NOTE: rdflib evaluates the inner `SELECT` fine at this position, but if the
`FILTER EXISTS` cannot see `?minx/?maxx` bindings in your rdflib version, restructure
to bind `?minx/?maxx` in the outer group FIRST (sub-select before the `?line` triple
patterns) — equivalence is proven by the Step-1 unit tests, which are the contract.

- [ ] **Step 5: Write the PROCEDURAL layer**

Create `src/iladub/etkl/gridregion.py`:

```python
"""gridregion — the ruled-band grid-membership evidence graph + query runner (loop P).

Which visual lines of a ruled band are INSIDE the author's grid (vs. full-width
strips above it — key headings, notices) is a declarative DERIVATION over author-mark
facts (open world -> SPARQL; the band is the closure boundary). This module is the
PROCEDURAL layer only: emitting the transient evidence graph (raw geometry, including
the y-centers, so the query stays literal-free) and invoking rdflib. No decision
logic, no tuned constant — the decision lives in vocab/queries/grid-region.rq (AXIOM).
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from .bands import Band
from .geometry import Rule

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

GRID_REGION_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "grid-region.rq"


def grid_evidence(band: Band, rules: Sequence[Rule]) -> Graph:
    """Emit the transient line/rule evidence graph for one band."""
    g = Graph()
    for i, ln in enumerate(band.lines):
        u = _EV["line-%d" % i]
        g.add((u, RDF.type, TAB.BandLine))
        g.add((u, TAB.lineIndex, Literal(i, datatype=XSD.integer)))
        cy = (ln.top + ln.bottom) / 2.0
        g.add((u, TAB.lineCenterY, Literal(round(cy, 2), datatype=XSD.decimal)))
    for k, r in enumerate(rules):
        u = _EV["rule-%d" % k]
        g.add((u, RDF.type, TAB.RuleSpan))
        g.add((u, TAB.ruleX, Literal(round(r.x, 2), datatype=XSD.decimal)))
        g.add((u, TAB.ruleTop, Literal(round(r.top, 2), datatype=XSD.decimal)))
        g.add((u, TAB.ruleBottom, Literal(round(r.bottom, 2), datatype=XSD.decimal)))
    return g


def grid_lines(band: Band, rules: Sequence[Rule]) -> set[int]:
    """Grid-member line indices. Abstains (empty set) when the evidence cannot
    decide: fewer than 3 DISTINCT rule x-positions means no rule can be interior."""
    if len({round(r.x, 2) for r in rules}) < 3:
        return set()
    g = grid_evidence(band, rules)
    query = GRID_REGION_RQ.read_text()
    return {int(row.idx) for row in g.query(query)}
```

- [ ] **Step 6: Run the unit tests to verify they pass**

Run: `./.venv/bin/python -m pytest tests/etkl/test_grid_region.py -v -k "grid_lines or numeric"`
Expected: 3 PASS.

- [ ] **Step 7: Integrate the peel at the seam**

In `src/iladub/etkl/bands.py`, add to `Band` (after `column_xs`):

```python
    # Full-width strip lines peeled from ABOVE a ruled grid (key headings, notices —
    # loop P). Kept word-based (never rule-re-extracted) and CARRIED to the asserted
    # table as tab:RegionCaption; default empty so every existing constructor stands.
    captions: tuple[Line, ...] = ()
```

In `src/iladub/etkl/compile.py` `_build_ruled_band`, immediately after the
`xs = sorted({round(r.x, 2) for r in sub_rules})` line, insert the peel — the
remainder of the function then operates on the PEELED sub-band and its chars:

```python
    from .gridregion import grid_lines as _grid_lines
    gset = _grid_lines(sub, sub_rules)
    caption_lines: tuple = ()
    if gset and gset != set(range(len(sub.lines))):
        keep = sorted(gset)
        caption_lines = tuple(ln for i, ln in enumerate(sub.lines) if i not in gset)
        sub = _replace(sub,
                       lines=tuple(sub.lines[i] for i in keep),
                       top=min(sub.lines[i].top for i in keep))
```

and thread `caption_lines` onto every `return` of `_build_ruled_band` via
`_replace(<band>, captions=caption_lines)`. `band_chars` (already computed from
`sub.top`) then excludes the caption strips automatically — this is what stops the
`GERALDTO N` chop.

- [ ] **Step 8: Emit the carried captions at the assert sites**

Add to `compile.py` a small helper (place next to `escalate_region`'s definition or
import section):

```python
def _emit_band_captions(graph, table_uri, band):
    """Loop P §5/§7 carry: one tab:RegionCaption per peeled strip line. captionRow is
    the line's index within the ORIGINAL band (captions precede the grid, so their
    order is their index)."""
    from rdflib import Literal, RDF, URIRef
    from rdflib.namespace import XSD
    for k, ln in enumerate(getattr(band, "captions", ()) or ()):
        cap = URIRef("%s-bandcap%d" % (table_uri, k))
        graph.add((cap, RDF.type, TAB.RegionCaption))
        graph.add((cap, TAB.captionText, Literal(" ".join(w.text for w in ln.words))))
        graph.add((cap, TAB.captionRow, Literal(k, datatype=XSD.integer)))
        graph.add((table_uri, TAB.hasCaption, cap))
```

Call `_emit_band_captions(graph, table_uri, band)` at EVERY assert site in
`compile_tables` that has both a `table_uri` and the compiled `band` in scope (grep
`reports.append(RegionReport(region.kind, "asserted"` — the hierarchical/ruled,
record, matrix and row-hier paths). Sites where the band has no captions add zero
triples, so blanket wiring is safe.

- [ ] **Step 9: Run the loop battery + the ruled family**

Run: `./.venv/bin/python -m pytest tests/etkl/test_grid_region.py tests/etkl/test_grid.py tests/etkl/test_header_stack.py -v`
Expected: `test_sectioned_captions_carried` may still be RED only if the fixture's
section still escalates (welding lands in Task 3) — everything else green, and the
two counter-behavior pins (`test_grid_lines_abstains…`, existing ruled fixtures)
green. If any EXISTING ruled fixture changed behavior: STOP, report — the peel must
be a no-op wherever no full-width strip exists.

- [ ] **Step 10: Commit**

```bash
/opt/homebrew/bin/git add vocab/ontology/tab.ttl vocab/queries/grid-region.rq src/iladub/etkl/gridregion.py src/iladub/etkl/bands.py src/iladub/etkl/compile.py tests/etkl/test_grid_region.py
/opt/homebrew/bin/git commit -m "feat(loop-p): grid-region scoping AXIOM — interior-rule presence peels and carries section strips"
```

---

### Task 3: Header/wrapped-row welding by author hrule boxes

**Files:**
- Modify: `src/iladub/etkl/geometry.py` (new `weld_hrule_boxes`)
- Modify: `src/iladub/etkl/compile.py:_build_ruled_band` (weld after re-lining)
- Test: `tests/etkl/test_grid_region.py` (unit additions) — plus the Task-1 E2E goes green here

**Interfaces:**
- Consumes: `rule_aware_lines` output (`list[Line]`, one Word per rule column), `Band.hrules`, the band's rule x-extent.
- Produces: `weld_hrule_boxes(relines: list[Line], hrules: Sequence[HRule], rule_xs: Sequence[float]) -> list[Line]`.

- [ ] **Step 1: Write the failing unit tests** (append to `tests/etkl/test_grid_region.py`)

```python
from iladub.etkl.geometry import HRule


def test_weld_merges_rows_sharing_a_full_width_box():
    """Two re-extracted rows inside ONE author-drawn full-width hrule box weld into
    one row; per-column text joins top-to-bottom ('Time Nom' + 'Accepted')."""
    from iladub.etkl.geometry import weld_hrule_boxes
    r1 = _line(110, 118, "Time", "Nom")           # visual line A (col-1 words)
    r2 = _line(122, 130, "ID", "Accepted")        # visual line B
    # words must sit in rule columns for the column join; rebuild precisely:
    a = Line((Word("Time Nom", 160, 220, 110, 118),), 110, 118)
    b = Line((Word("ID", 80, 100, 122, 130), Word("Accepted", 160, 225, 122, 130)), 122, 130)
    hrules = [HRule(105.0, 72.0, 300.0), HRule(140.0, 72.0, 300.0)]
    out = weld_hrule_boxes([a, b], hrules, [72.0, 150.0, 300.0])
    assert len(out) == 1
    texts = sorted(w.text for w in out[0].words)
    assert texts == ["ID", "Time Nom Accepted"]


def test_weld_never_splits_and_ignores_partial_hrules():
    """One row per box -> unchanged; an hrule NOT spanning the rule x-extent (a cell
    border fragment) delimits nothing."""
    from iladub.etkl.geometry import weld_hrule_boxes
    a = Line((Word("A", 80, 90, 110, 118),), 110, 118)
    b = Line((Word("B", 80, 90, 150, 158),), 150, 158)
    full = [HRule(105.0, 72.0, 300.0), HRule(140.0, 72.0, 300.0), HRule(170.0, 72.0, 300.0)]
    partial = [HRule(130.0, 72.0, 120.0)]          # spans a fraction of the width
    assert weld_hrule_boxes([a, b], full, [72.0, 300.0]) == [a, b]
    assert weld_hrule_boxes([a, b], full + partial, [72.0, 300.0]) == [a, b]


def test_weld_without_hrules_is_identity():
    from iladub.etkl.geometry import weld_hrule_boxes
    a = Line((Word("A", 80, 90, 110, 118),), 110, 118)
    assert weld_hrule_boxes([a], [], [72.0, 300.0]) == [a]
```

- [ ] **Step 2: Run to verify they fail**

Run: `./.venv/bin/python -m pytest tests/etkl/test_grid_region.py -v -k weld`
Expected: ImportError (`weld_hrule_boxes` absent).

- [ ] **Step 3: Implement**

Append to `src/iladub/etkl/geometry.py` (after `rule_aware_lines`):

```python
def weld_hrule_boxes(relines: list[Line], hrules: Sequence[HRule],
                     rule_xs: Sequence[float]) -> list[Line]:
    """Merge re-extracted rows that share one author-drawn FULL-WIDTH hrule box
    (loop P; loop H's marks-are-the-row-delimiters, applied as a merge LICENCE: the
    drawn box containing both rows is positive evidence they are one row — the CBH
    header's wrapped names). Justified PROCEDURAL raw extraction: pure containment
    over author marks; the only epsilon is the shipped COORD_EPS; welding only ever
    MERGES rows inside a box — it never splits, and with no full-width hrules it is
    the identity.

    A full-width hrule spans the band's rule x-extent (both ends within COORD_EPS of
    [min(rule_xs), max(rule_xs)] or beyond). Boxes are consecutive full-width hrule
    pairs; a row belongs to a box iff its y-center lies inside. Within a merged row,
    each column's words join top-to-bottom with single spaces; the merged Word's bbox
    is the union of its parts."""
    if not relines or not hrules or len(rule_xs) < 2:
        return list(relines)
    lo, hi = min(rule_xs), max(rule_xs)
    full = sorted({round(h.y, 2) for h in hrules
                   if h.x0 <= lo + COORD_EPS and h.x1 >= hi - COORD_EPS})
    if len(full) < 2:
        return list(relines)
    out: list[Line] = []
    used = [False] * len(relines)
    boxes = list(zip(full, full[1:]))

    def box_of(ln: Line):
        cy = (ln.top + ln.bottom) / 2.0
        for bi, (a, b) in enumerate(boxes):
            if a <= cy <= b:
                return bi
        return None

    i = 0
    while i < len(relines):
        bi = box_of(relines[i])
        group = [relines[i]]
        j = i + 1
        while bi is not None and j < len(relines) and box_of(relines[j]) == bi:
            group.append(relines[j])
            j += 1
        if len(group) == 1:
            out.append(relines[i])
        else:
            cols: dict[int, list[Word]] = {}
            xs = sorted(rule_xs)
            for ln in group:
                for w in ln.words:
                    cx = (w.x0 + w.x1) / 2.0
                    col = next((k for k in range(len(xs) - 1)
                                if xs[k] <= cx < xs[k + 1]), len(xs) - 2)
                    cols.setdefault(col, []).append(w)
            words = []
            for col in sorted(cols):
                ws = sorted(cols[col], key=lambda w: (w.top, w.x0))
                words.append(Word(" ".join(w.text for w in ws),
                                  min(w.x0 for w in ws), max(w.x1 for w in ws),
                                  min(w.top for w in ws), max(w.bottom for w in ws)))
            out.append(Line(tuple(sorted(words, key=lambda w: w.x0)),
                            min(ln.top for ln in group),
                            max(ln.bottom for ln in group)))
        i = j if j > i + 1 else i + 1
    return out
```

- [ ] **Step 4: Integrate at the seam**

In `_build_ruled_band`, right after `relines = rule_aware_lines(band_chars, xs) if len(xs) >= 2 else []`:

```python
    if relines:
        from .geometry import weld_hrule_boxes
        relines = weld_hrule_boxes(relines, sub_hrules, xs)
```

- [ ] **Step 5: Run the whole loop battery — the Task-1 E2E must go green**

Run: `./.venv/bin/python -m pytest tests/etkl/test_grid_region.py -v`
Expected: ALL PASS, including `test_sectioned_ruled_table_reads` and
`test_sectioned_captions_carried`. Now TIGHTEN the Task-1 E2E's `flat` scan into the
proper leaf-label accessor (per the Task-1 note) and re-run: still green.

- [ ] **Step 6: Ruled-family no-regression**

Run: `./.venv/bin/python -m pytest tests/etkl/ -q`
Expected: everything green. A changed verdict/score on ANY existing fixture: STOP and
report with the diff of readings — welding must be conservative (merge-only, licensed
by drawn boxes).

- [ ] **Step 7: Commit**

```bash
/opt/homebrew/bin/git add src/iladub/etkl/geometry.py src/iladub/etkl/compile.py tests/etkl/test_grid_region.py
/opt/homebrew/bin/git commit -m "feat(loop-p): hrule-box row welding — author-drawn boxes licence the wrapped header weld"
```

---

### Task 4: CBH + stem measurement, register + docs close

**Files:**
- Modify: `docs/superpowers/residues.md` (R42 row: gap (a) close)
- Modify: `docs/superpowers/specs/2026-08-04-cbh-dimension-split-design.md` (§3 status note: measurements)
- Modify: `docs/wiki/concepts/neurosymbolic-exemplars.md` (+ its index line if the wiki index lists per-page updates)

**Interfaces:**
- Consumes: everything above; the corpus battery (`-m corpus`).

- [ ] **Step 1: Full non-corpus suite** — `./.venv/bin/python -m pytest -m "not corpus" -q` (expect 825-baseline + this loop's new tests, minus the 1 known machine-local release-gate env failure). Record the tally.
- [ ] **Step 2: CBH measurement** — `./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -v -s -k "cbh"` (Bash timeout 600000). Record VERBATIM: score (was 0.0698), per-region verdicts (were 4× MERGE_AMBIGUOUS), captions carried (expect GERALDTON/KWINANA/ALBANY/ESPERANCE + notices as `tab:RegionCaption`). The Unadjudicated gate is compile-without-crash; the measured reading is François's adjudication evidence. If sections STILL escalate: that is a measured result — report the reason verbatim, do not force.
- [ ] **Step 3: Stem no-regression** — `./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -v -s -k "graincorp-stem"` (timeout 600000). Expected EXACTLY: score 0.9655, records 133, grounded 585, quarantined 1265. ANY drift: STOP and report (Global Constraints).
- [ ] **Step 4: Register + spec + wiki** — rewrite R42's row: gap (a) CLOSED with the measured CBH numbers (keep gap (b) open, pointing at loop Q); append a dated status note to spec §3 with the same measurements; add the loop-P entry to `neurosymbolic-exemplars.md` (grid-region.rq = AXIOM exemplar; weld_hrule_boxes = justified-PROCEDURAL exemplar; cite file paths). Gate: `./.venv/bin/python -m pytest tests/test_doc_governance.py tests/test_docgov_extract.py -q` green (PATH export first — broken system git).
- [ ] **Step 5: Commit** — `docs(loop-p): close — R42 gap (a) measured, spec status note, exemplars entry` + trailer. Then the finishing flow (PR to main) runs from the controller, not this task.

---

## Self-review (done at plan time)

- **Spec coverage:** §3 CORRECTION mechanism (1) grid-region scoping → Task 2; mechanism (2) hrule welding → Task 3; §5/§7 caption carry → Tasks 2/3 tests; no-overfit counter-pins → Tasks 2 Step 9 / 3 Step 6; stem byte-identity → Task 4 Step 3; R31 doubled rules — `weld_hrule_boxes` deduplicates hrule y's via `round(…, 2)` set and the rule-x dedup in `_build_ruled_band` already rounds; if CBH's x=345.1/345.6 pair still splits a column, that is R31's OPEN residue measured again — report, don't absorb (Task 4 Step 2's honest-report clause covers it).
- **Known risks, stated:** (a) rdflib sub-select scoping in `grid-region.rq` — restructuring note included, unit tests are the contract; (b) `_build_ruled_band`'s downstream (`refine_rule_columns` → `recover_leaf_grid` → `header_body_split` → confirmed boundaries) now sees a shorter band — the loop-G lesson (`recover_leaf_grid` must carry every boundary-bearing field) applies to the `captions` field: thread it through EVERY `_replace` return; (c) the Task-1 red test's liberal `flat` scan is deliberately temporary with an explicit tightening instruction.
- **Type consistency:** `grid_lines(band, rules) -> set[int]` consistent across Tasks 2–3; `weld_hrule_boxes(relines, hrules, rule_xs)` consistent between unit tests and seam integration; `Band.captions` default `()` used by `_emit_band_captions` via `getattr`.

## Status note (loop close, 2026-08-04)

**Outcome: closed honestly, without the real-CBH close this plan's Task 4 originally
expected.** Tasks 1–3 shipped as designed — the sectioned-ruled synthetic fixture and red
pins (Task 1), the grid-region scoping AXIOM (`vocab/queries/grid-region.rq` +
`vocab/queries/line-enclosed.rq`, `src/iladub/etkl/gridregion.py`, `Band.captions` +
caption carry at all assert sites, Task 2), and `weld_hrule_boxes` header/wrapped-row
welding (`src/iladub/etkl/geometry.py`, Task 3) — all green, 490/490 in `tests/etkl/` at
branch head.

**Task 4 closed differently than planned.** Measuring the shipped machinery against the
real CBH specimen (Task 4 Step 2) found it inert: `grid_lines`'s interior-rule test does
not fire on CBH (border twins x=37.92/38.2 read as interior, defeating the min/max-x
test), so no peel happens and CBH's score stays 0.0698. A follow-on fix wave (3 commits —
ink-witness `b515283`, straddle `33f213f`, opening-box `6d7aa60`) tried three different
band-local peel licences at the `_build_ruled_band` seam. Each one fixed CBH while
breaking the GrainCorp stem, or vice versa, in a different way:

- ink-witness: CBH 0.9926 (4/4 sections assert) but stem 1.0000-WRONG (header stack
  swallowed, chains `[1,1,1]`, grounded 0);
- straddle: CBH 0.3636 (peel stalls on KWINANA's short heading) and stem
  `REGION_TILING_FAILED` (loop L clause-0 disengaged);
- opening-box: CBH 0.0724 (near-unchanged) and stem 0.9660 ≠ 0.9655 (loop M carriage
  dead, chains `[1,1,1]`, grounded 167).

The wave was **reverted** (`1271156`) rather than iterated further, once the pattern
showed a structural conflict, not a tuning problem: `_build_ruled_band` is one seam
shared by three laws (loop L's engagement, loop M's carriage, CBH's section peel) that
each need a different licence from the same peel decision, and no band-local licence
satisfies all three. Branch content is now byte-identical to `f06276f`
(controller-verified empty diff) — the stem battery is exactly intact at
0.9655/2152 cells/133 records/585 grounded/1265 quarantined, 10/10 stem tests, and real
CBH is unchanged at 0.0698.

**R42 gap (a) stays OPEN**, with the full measured map recorded in its residues.md row;
close re-homes at SECTION scope inside loop Q's design (recognition of a sectioned,
repeated-header chain first, then the re-reading licence for the strips above each
section's grid — never a single band deciding blind). The docs close (this task) records
the outcome in `docs/superpowers/residues.md` (R42), the spec's §3 status note
(`docs/superpowers/specs/2026-08-04-cbh-dimension-split-design.md`), and a new loop-P
entry plus negative lesson in `docs/wiki/concepts/neurosymbolic-exemplars.md`. No code,
manifest, or verdict changes — docs only, per François's 2026-08-04 adjudication.
