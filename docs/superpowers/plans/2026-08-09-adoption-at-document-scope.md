# Adoption at document scope (R73) — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make data-grid adoption the document's *last* reader — admitted only where carriage,
section repair and stitching have all failed — with a line-granular ledger so an adopted page
can never score 1.0000 for ink it did not read.

**Architecture:** A new focused module `src/iladub/etkl/adoption.py` owns two pure pieces: the
**line ledger** (which page lines the grid admitted, which escalated ink it left behind) and the
**candidate gate** (a holon-scoped `.rq` over the merged graph). `compile.py`'s existing
page-scope adoption branch is rewritten to use the ledger and to keep the band-index contract.
`compile_document` gains a final adoption pass that runs after the totals oracle and before
whole-graph validation.

**Tech Stack:** Python 3.11+, rdflib, pySHACL, pytest. RDF Turtle for vocabulary, SPARQL `.rq`
in `vocab/queries/`.

**Spec:** `docs/superpowers/specs/2026-08-09-adoption-at-document-scope-design.md`

## Global Constraints

- **Neurosymbolic-first gate (CLAUDE.md §8).** Every decision is AXIOM (SPARQL/SHACL), NEURAL
  (BAML propose + oracle dispose), or justified PROCEDURAL. **A tuned constant or tolerance is
  prima facie evidence of a defect.** The adoption gate is AXIOM (§5.2 of the spec); the ledger
  arithmetic is justified PROCEDURAL (exact counting over line-index sets, no tolerance) and
  must say so in the code.
- **Interval containment is permitted; coordinate tolerance is not.** The band↔line join uses
  `band.top <= line.top <= band.bottom` — the idiom `page_bands` itself already uses for hrules
  (`compile.py:309`). No epsilon, no rounding, no nearest-match.
- **Never lower a floor.** stem is `0.9654553611484971` with 1 chain of 3. If a change lowers
  it, report the measured number and stop — do not adjust the assertion.
- **No overfitting.** Nothing may key on "apple" or "page 1". Every rule is stated over lines,
  bands and verdicts.
- **Only emit what the source supports (§7).** The residue candidate carries the actual line
  text; no line count is invented.
- **Source ownership.** No `w3id.org/holon` IRI is written anywhere in this work.
- **Licences:** code Apache-2.0, vocabulary CC-BY-4.0.

---

### Task 1: The line ledger

A pure function: given the page's lines, the grid's admitted row indices, the bands and their
verdicts, decide which bands the grid *touched*, which lines are *residue*, and what each side
contributes to the token ledger. No graph, no I/O.

**Files:**
- Create: `src/iladub/etkl/adoption.py`
- Test: `tests/etkl/test_adoption_ledger.py`

**Interfaces:**
- Consumes: `iladub.etkl.geometry.Line` (`words: tuple[Word, ...]`, `top: float`,
  `bottom: float`); band objects exposing `.top` / `.bottom`;
  `iladub.etkl.compile.RegionReport` (`verdict: str`, `tokens_escalated: int`).
- Produces:
  ```python
  @dataclass(frozen=True)
  class LineLedger:
      admitted: tuple[int, ...]        # page line indices the grid read
      residue: tuple[int, ...]         # page line indices an escalated band covered, unread
      touched: frozenset[int]          # band indices the grid overlapped at all
      asserted_tokens: int
      escalated_tokens: int

  def build_ledger(lines, grid_rows, bands, reports) -> LineLedger
  ```

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_adoption_ledger.py
"""The line ledger (spec 2026-08-09-adoption-at-document-scope §5.3).

Every line is counted exactly once. The two failure directions this pins are the two the
spec measured: zeroing the escalation (page scores 1.0000 whatever the grid missed) and
band-granular withdrawal (the 0.594 double count)."""
from dataclasses import dataclass

from iladub.etkl.adoption import build_ledger


@dataclass(frozen=True)
class _W:
    text: str


@dataclass(frozen=True)
class _L:
    words: tuple
    top: float
    bottom: float


@dataclass(frozen=True)
class _B:
    top: float
    bottom: float


@dataclass(frozen=True)
class _R:
    verdict: str
    tokens_escalated: int = 0


def _line(n_words, top):
    return _L(tuple(_W(f"w{i}") for i in range(n_words)), top, top + 1.0)


def test_a_line_the_grid_read_is_asserted_and_never_residue():
    lines = [_line(3, 10.0), _line(2, 20.0)]
    bands = [_B(0.0, 30.0)]
    reports = [_R("escalated", 5)]
    led = build_ledger(lines, (0, 1), bands, reports)
    assert led.admitted == (0, 1)
    assert led.residue == ()
    assert led.asserted_tokens == 5
    assert led.escalated_tokens == 0
    assert led.touched == frozenset({0})


def test_an_unread_line_inside_an_escalated_band_stays_escalated():
    """The apple p1 shape: the grid reads the leaf rows and drops the section labels."""
    lines = [_line(2, 10.0), _line(3, 20.0), _line(4, 30.0)]
    bands = [_B(0.0, 40.0)]
    reports = [_R("escalated", 9)]
    led = build_ledger(lines, (1, 2), bands, reports)
    assert led.residue == (0,)
    assert led.asserted_tokens == 7
    assert led.escalated_tokens == 2
    assert led.touched == frozenset({0})


def test_a_band_the_grid_never_touched_keeps_its_own_token_count():
    lines = [_line(2, 10.0), _line(3, 90.0)]
    bands = [_B(0.0, 50.0), _B(80.0, 100.0)]
    reports = [_R("escalated", 2), _R("escalated", 7)]
    led = build_ledger(lines, (0,), bands, reports)
    assert led.touched == frozenset({0})
    assert led.residue == ()
    # band 1 is untouched: its OWN escalated token count carries, not the page-level one
    assert led.escalated_tokens == 7
    assert led.asserted_tokens == 2


def test_an_ignored_band_contributes_nothing_to_either_side():
    """A NON_TABLE band's ink was never in the denominator and does not enter it now."""
    lines = [_line(5, 10.0), _line(3, 60.0)]
    bands = [_B(0.0, 50.0), _B(55.0, 70.0)]
    reports = [_R("ignored", 0), _R("escalated", 3)]
    led = build_ledger(lines, (1,), bands, reports)
    assert led.residue == ()            # line 0 sits in an IGNORED band, not an escalated one
    assert led.escalated_tokens == 0
    assert led.asserted_tokens == 3


def test_no_line_is_on_both_sides_ever():
    lines = [_line(1, float(10 * i)) for i in range(10)]
    bands = [_B(0.0, 100.0)]
    reports = [_R("escalated", 10)]
    led = build_ledger(lines, (0, 2, 4, 6, 8), bands, reports)
    assert not set(led.admitted) & set(led.residue)
    assert led.asserted_tokens + led.escalated_tokens == 10
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/etkl/test_adoption_ledger.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'iladub.etkl.adoption'`

- [ ] **Step 3: Write the module**

```python
# src/iladub/etkl/adoption.py
"""adoption — the data grid as the DOCUMENT's last reader (spec 2026-08-09, residue R73).

A page's total reading failure is not final at page scope. Adoption is admitted only where
carriage (loop M), section repair (loop Q) and stitching have all had their turn and the page
still asserted nothing — and it withdraws the escalation of the ink it actually READ, line by
line, never the page's whole ledger.

GATE CLASSIFICATION (CLAUDE.md §8).
  * The candidate GATE is an AXIOM — `vocab/queries/adoption-candidate.rq`, holon-scoped to one
    page (the holon is the closure boundary, so its query-local NOT EXISTS is legitimate).
  * The LEDGER below is justified PROCEDURAL: exact counting over line-index sets. It is
    irreducible to AXIOM or NEURAL because it is arithmetic over indices the grid and the band
    inventory already decided — it decides nothing about the document, it only refuses to count
    a line twice. It carries no threshold, no tolerance and no tuned constant.

WHY LINE GRANULARITY IS FORCED (spec §M5). On the specimen page, NO escalated band is fully
covered by the grid. A band-granular ledger therefore withdraws nothing and scores the page
142/(142+97) = 0.594 — the double count that made the first wiring's 0.5941 meaningless, since
the grid's tokens include the very lines those bands escalate. Zeroing the escalation instead
scores it 1.0000 by construction, whatever the grid missed. Only the line is a unit both sides
agree on.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class LineLedger:
    """One adopted page's accounting. `admitted` and `residue` are DISJOINT by construction."""
    admitted: tuple[int, ...]
    residue: tuple[int, ...]
    touched: frozenset[int]
    asserted_tokens: int
    escalated_tokens: int


def build_ledger(lines, grid_rows, bands, reports) -> LineLedger:
    """Account for every line of an adopted page exactly once.

    `lines` is the page's own `text_lines(extract_words(...))` sequence, sorted by `top` — the
    SAME sequence `grid_rows` indexes into, which is what makes the join exact.

    A band is TOUCHED when the grid admitted at least one line inside it. Touched bands lose
    their escalation (part of their ink has been read, so their record no longer describes what
    happened) and contribute their UNREAD lines as residue. Untouched bands keep their own
    token count verbatim.

    The band↔line join is interval containment on the author's own band bounds — the idiom
    `page_bands` already uses for hrules — never a coordinate tolerance.
    """
    admitted = tuple(sorted(set(grid_rows)))
    admitted_set = set(admitted)
    escalated_bands = [i for i, r in enumerate(reports) if r.verdict == "escalated"]

    def _inside(band, line):
        return band.top <= line.top <= band.bottom

    touched = frozenset(
        i for i in range(len(bands))
        if any(_inside(bands[i], lines[j]) for j in admitted if j < len(lines))
    )

    residue = tuple(
        j for j, ln in enumerate(lines)
        if j not in admitted_set
        and any(i in touched and _inside(bands[i], ln) for i in escalated_bands)
    )

    asserted_tokens = sum(len(lines[j].words) for j in admitted if j < len(lines))
    escalated_tokens = (
        sum(len(lines[j].words) for j in residue)
        + sum(reports[i].tokens_escalated for i in escalated_bands if i not in touched)
    )
    return LineLedger(admitted, residue, touched, asserted_tokens, escalated_tokens)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/etkl/test_adoption_ledger.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/adoption.py tests/etkl/test_adoption_ledger.py
git commit -m "feat(adoption): the line ledger — every line counted exactly once"
```

---

### Task 2: The candidate gate as an AXIOM

"This page asserted nothing" becomes a holon-scoped SPARQL ASK over the merged graph, not a
Python condition on a token counter.

**Files:**
- Create: `vocab/queries/adoption-candidate.rq`
- Modify: `src/iladub/etkl/adoption.py` (append `is_adoption_candidate`)
- Test: `tests/etkl/test_adoption_gate.py`

**Interfaces:**
- Produces: `def is_adoption_candidate(graph, page: int, page_doc) -> bool`

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_adoption_gate.py
"""The adoption GATE is an AXIOM (spec §5.2): holon-scoped to one page, no numeric literal.

A page is a candidate iff its holon carries an escalation and NO entry cell. The closure is
query-local and page-scoped — the graph as a whole stays open."""
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

from iladub.etkl.adoption import is_adoption_candidate
from iladub.etkl.holon import TAB

ILADUB = Namespace("https://w3id.org/iladub#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DOC = URIRef("https://example.org/etkl/doc/p1")


def _escalation(g, doc=DOC):
    c = URIRef(f"{doc}#region2")
    g.add((c, RDF.type, ILADUB.CandidateConcept))
    g.add((c, PROV.wasDerivedFrom, doc))


def _cell(g, page):
    c = URIRef(f"{DOC}#cell0")
    g.add((c, RDF.type, TAB.EntryCell))
    g.add((c, TAB.onPage, Literal(page, datatype=XSD.integer)))


def test_an_escalation_with_no_cell_is_a_candidate():
    g = Graph()
    _escalation(g)
    assert is_adoption_candidate(g, 1, DOC) is True


def test_a_page_that_asserted_a_cell_is_not_a_candidate():
    g = Graph()
    _escalation(g)
    _cell(g, 1)
    assert is_adoption_candidate(g, 1, DOC) is False


def test_a_page_with_nothing_at_all_is_not_a_candidate():
    """No escalation means nothing to supersede — a page of prose is not a failure."""
    assert is_adoption_candidate(Graph(), 1, DOC) is False


def test_the_gate_is_page_scoped_not_document_scoped():
    """Another page's cell must not disqualify this one, and vice versa."""
    g = Graph()
    _escalation(g)
    _cell(g, 0)                      # page 0 read something; page 1 still failed
    assert is_adoption_candidate(g, 1, DOC) is True


def test_the_query_carries_no_numeric_literal():
    from pathlib import Path
    import re
    q = Path("vocab/queries/adoption-candidate.rq").read_text()
    body = re.sub(r"#.*", "", q)                       # comments may mention numbers
    assert not re.search(r"\b\d+(\.\d+)?\b", body), body
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m pytest tests/etkl/test_adoption_gate.py -v`
Expected: FAIL — `ImportError: cannot import name 'is_adoption_candidate'`

- [ ] **Step 3: Write the query and the runner**

```sparql
# vocab/queries/adoption-candidate.rq
#
# THE ADOPTION GATE (spec 2026-08-09-adoption-at-document-scope §5.2, residue R73).
#
# Is this page a total reading failure — an escalation on the page's own holon, and not one
# entry cell anywhere on it? Both variables (?page, ?doc) are supplied by the caller as data;
# the query text carries no literal.
#
# CLOSURE. The NOT EXISTS is query-local and HOLON-SCOPED: it closes the world over ONE page
# holon, which is the closure boundary (CLAUDE.md §8). The graph stays open — another page's
# silence says nothing here, and this query never DERIVES a fact, it only answers whether the
# document's last reader may be asked.
PREFIX tab:    <https://w3id.org/iladub/tab#>
PREFIX iladub: <https://w3id.org/iladub#>
PREFIX prov:   <http://www.w3.org/ns/prov#>

ASK {
  ?candidate a iladub:CandidateConcept ;
             prov:wasDerivedFrom ?doc .
  FILTER NOT EXISTS {
    ?cell a tab:EntryCell ;
          tab:onPage ?page .
  }
}
```

Append to `src/iladub/etkl/adoption.py`:

```python
from pathlib import Path

from rdflib import Literal, URIRef, XSD

_QUERIES = Path(__file__).resolve().parents[3] / "vocab" / "queries"
ADOPTION_CANDIDATE_RQ = _QUERIES / "adoption-candidate.rq"


def is_adoption_candidate(graph, page: int, page_doc) -> bool:
    """Run the gate AXIOM over ONE page holon of the merged graph.

    `page_doc` is the page's document URI — the subject every escalation on that page was
    derived from (`holon.escalate_region` stamps `prov:wasDerivedFrom`), which is how the page
    holon is addressed for candidates that carry no `tab:onPage` of their own.
    """
    q = ADOPTION_CANDIDATE_RQ.read_text()
    return bool(graph.query(q, initBindings={
        "page": Literal(int(page), datatype=XSD.integer),
        "doc": URIRef(str(page_doc)),
    }).askAnswer)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/etkl/test_adoption_gate.py -v`
Expected: 5 passed

If `_QUERIES` resolves wrongly, match the existing idiom in `src/iladub/etkl/document.py:118`
(`_QUERIES = …`) exactly rather than inventing a new one.

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/adoption-candidate.rq src/iladub/etkl/adoption.py tests/etkl/test_adoption_gate.py
git commit -m "feat(adoption): the candidate gate as a holon-scoped AXIOM"
```

---

### Task 3: Page-scope adoption uses the ledger and keeps the band-index contract

Rewrite the existing branch at `src/iladub/etkl/compile.py:884-897`. Today it replaces the whole
`reports` tuple with one region and zeroes `escalated_total`; both are defects (spec §1).

**Files:**
- Modify: `src/iladub/etkl/compile.py:869-897`
- Modify: `tests/etkl/test_datagrid.py:844-886` (the three shipped adoption tests)
- Test: `tests/etkl/test_datagrid.py` (same file, new assertions)

**Interfaces:**
- Consumes: `adoption.build_ledger` (Task 1).
- Produces: an adopted page's `regions` tuple = one report per band (touched bands rewritten
  to verdict `"superseded"` with `tokens_escalated=0`), then the grid region at index
  `len(bands)`, then — when `ledger.residue` is non-empty — the residue region at
  `len(bands) + 1`.

- [ ] **Step 1: Rewrite the three shipped tests to the new accounting**

Replace `tests/etkl/test_datagrid.py:844-886` with:

```python
# --- R73: adoption, and what it may and may not withdraw ---------------------------

@corpus_only
def test_adoption_is_off_by_default_at_page_scope():
    """Page scope is not where the decision belongs (spec 2026-08-09 §5.1).

    The register's original reason — 'compile_document compiles each page standalone before
    re-compiling continuation pages' — is MEASURED FALSE: the driver makes one pass and the
    carried reading is an INPUT to page p's compile. The real reason the page-scope flag stays
    off is the refusal branch: stem p1 standalone adopts at 811 FLAT cells and scores 1.0000,
    against 825 hierarchical chain-joined cells at 0.9706 under the driver."""
    from iladub.etkl.compile import compile_tables

    default = compile_tables(APPLE, 1, validate_shapes=False)
    explicit = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=False)
    assert default.score == explicit.score == 0.0
    assert default.escalated > 0


@corpus_only
def test_adoption_withdraws_only_the_escalation_of_ink_it_READ():
    """Line-granular, both directions pinned (spec §5.3).

    Not 1.0000: the section labels the grid never admitted keep escalating.
    Not 0.594: the lines the grid DID read are not counted on both sides."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=False)
    on = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=True)
    assert off.asserted == 0 and off.escalated > 0
    assert on.asserted > 0
    assert 0 < on.escalated < off.escalated, "residue must survive, and must shrink"
    assert on.score < 1.0, "an adopted page must never score 1.0000 by construction"
    assert on.score > off.score
    print(f"\napple p1 adopted: {on.asserted}/{on.escalated} score={on.score:.4f}")
    grid_cells = sum(r.cells for r in on.regions)
    assert grid_cells == 28 * 3, "28 entry rows x 3 columns"


@corpus_only
def test_adoption_keeps_the_band_index_contract():
    """Region report index IS band index (page_bands' pinned enumeration contract). The
    driver reads it at five sites; adoption used to collapse the tuple to length 1."""
    from iladub.etkl.compile import compile_tables, page_bands

    bands = page_bands(APPLE, 1)
    on = compile_tables(APPLE, 1, validate_shapes=False, datagrid_adopt=True)
    assert len(on.regions) >= len(bands) + 1
    assert on.regions[len(bands)].table_uri is not None, "the grid region carries its URI"
    assert on.asserted == sum(r.tokens_asserted for r in on.regions)
    assert on.escalated == sum(r.tokens_escalated for r in on.regions)


@corpus_only
def test_adoption_never_touches_a_page_that_read_something():
    """apple page 0 asserts 20 cells. A partial reading is not a total failure, and
    adoption is scoped to total failure only."""
    from iladub.etkl.compile import compile_tables

    off = compile_tables(APPLE, 0, validate_shapes=False, datagrid_adopt=False)
    on = compile_tables(APPLE, 0, validate_shapes=False, datagrid_adopt=True)
    assert off.asserted > 0
    assert on.score == off.score
    assert sum(r.cells for r in on.regions) == sum(r.cells for r in off.regions) == 20
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/etkl/test_datagrid.py -k adoption -v`
Expected: FAIL — `test_adoption_withdraws_only_the_escalation_of_ink_it_READ` fails on
`0 < on.escalated` (today it is 0), and `test_adoption_keeps_the_band_index_contract` fails on
the region count (today it is 1).

- [ ] **Step 3: Rewrite the branch**

Replace `src/iladub/etkl/compile.py:884-897` (keep the comment block at 869-883, but correct
its final paragraph — see Task 6) with:

```python
    if datagrid_adopt and asserted_total == 0 and escalated_total > 0:
        from .adoption import build_ledger
        from .datagrid import derive_data_grid as _dg, emit_data_grid as _emit
        _grid = _dg(pdf_path, page_number)
        if _grid is not None and _grid.rows:
            _lines = sorted([ln for ln in text_lines(extract_words(pdf_path, page_number))
                             if ln.words], key=lambda ln: ln.top)
            _led = build_ledger(_lines, _grid.rows, bands, reports)
            graph = Graph()                   # withdrawal: the page graph is rebuilt
            _grid_uri = _emit(graph, _grid, _lines, doc, page_number)
            _cells = len(list(graph.subjects(RDF.type, TAB.EntryCell)))
            # THE LEDGER IS LINE-GRANULAR (spec §5.3). Zeroing `escalated_total` would score
            # the page 1.0000 whatever the grid missed; withdrawing band-by-band would count
            # the read lines twice (0.594). Only the line is a unit both sides agree on.
            asserted_total = _led.asserted_tokens
            escalated_total = _led.escalated_tokens
            # Band index IS region index: touched bands are SUPERSEDED in place, untouched
            # bands keep their report verbatim, and the grid (plus any residue) is appended.
            reports = [
                _dc_replace_report(r, verdict="superseded", tokens_escalated=0)
                if i in _led.touched and r.verdict == "escalated" else r
                for i, r in enumerate(reports)
            ]
            reports.append(RegionReport(RegionKind.RECORD_TABLE, "asserted", _cells,
                                        None, str(TAB.DataGrid), "",
                                        table_uri=_grid_uri,
                                        tokens_asserted=_led.asserted_tokens))
            if _led.residue:
                _text = "\n".join(" ".join(w.text for w in _lines[j].words)
                                  for j in _led.residue)
                _res_uri = URIRef(f"{doc}#p{page_number}-datagrid-residue")
                escalate_region(graph, _res_uri, doc, _text,
                                "DATAGRID_RESIDUE", TAB.DataGrid, 0.0)
                reports.append(RegionReport(RegionKind.UNSUPPORTED_TABLE, "escalated", 0,
                                            "DATAGRID_RESIDUE", str(TAB.DataGrid), "",
                                            tokens_escalated=sum(len(_lines[j].words)
                                                                 for j in _led.residue)))
            _adopted_page = True              # the ledger above is authoritative for this page
```

Initialise `_adopted_page = False` next to `band_marks` at `compile.py:441`.

Mechanical points for the implementer (all four verified against the current file):

1. `_dc_replace_report` is `dataclasses.replace`; import it at the top of the branch as
   `from dataclasses import replace as _dc_replace_report` if `compile.py` does not already
   have a module-level alias (it imports `replace as _dc_replace` locally at line 916 — reuse
   that name if it is in scope, otherwise import it here).
2. The final `band_marks.append(...)` plus the differencing block at `compile.py:915-920`
   recompute every region's `tokens_*` from `band_marks`. Adoption now sets those fields
   itself, so both must be skipped when it fired: wrap lines 915-920 in
   `if not _adopted_page:`. Verify the invariant
   `sum(r.tokens_*) == asserted_total/escalated_total` still holds on the non-adopting paths —
   `test_adoption_keeps_the_band_index_contract` and the existing suite both check it.
3. `escalate_region`, `URIRef`, `text_lines` and `extract_words` are already imported in
   `compile.py` (lines 13, 15, 19). `TAB` and `RegionKind` are in scope. Nothing new is needed
   beyond `dataclasses.replace`.
4. `bands`, `reports` and `doc` are the existing locals of `compile_tables`
   (`compile.py:430-435`) — use those names, do not re-derive them.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/etkl/test_datagrid.py -k adoption -v`
Expected: 4 passed. Record the printed `apple p1 adopted: …` line — it is V3.

If the SHACL membrane rejects `dec:confidence 0.0` on the residue candidate, run
`python3 -m pytest tests/etkl/test_datagrid.py -k adoption -v` with `validate_shapes=True` on
one call to see the violation, use the smallest value the shape admits, and record the change
and the shape's name in the loop report. Do not silence the shape.

- [ ] **Step 5: Run the whole data-grid and compile suites**

Run: `python3 -m pytest tests/etkl/test_datagrid.py tests/etkl/test_tiling_gate.py -v`
Expected: all pass. Any failure here is a real regression — report it, do not adjust it away.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_datagrid.py
git commit -m "feat(adoption): line-granular ledger and the band-index contract at page scope"
```

---

### Task 4: The document-scope adoption pass

**Files:**
- Modify: `src/iladub/etkl/document.py` (insert the pass after the §4.0 totals loop, before
  `if validate_shapes and (recognized or section_facts):` at ~line 1357)
- Test: `tests/etkl/test_adoption_document.py`

**Interfaces:**
- Consumes: `adoption.is_adoption_candidate` (Task 2), the page-scope adoption branch (Task 3).
- Produces: `DocumentReport.pages[p]` replaced for adopted pages; `adopted: tuple[int, ...]`
  added to `DocumentReport` (page ordinals that adopted), placed after `repaired`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_adoption_document.py
"""Adoption at DOCUMENT scope (spec 2026-08-09, residue R73).

The decidability claim: a page's total reading failure is only final after carriage, section
repair and stitching have had their turn. The pass therefore runs LAST."""
import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APPLE = REPO / "corpus" / "financial" / "apple-fy2026q3-statements.pdf"

pytestmark = pytest.mark.corpus
corpus_only = pytest.mark.skipif(not APPLE.is_file(), reason="corpus not populated")


@pytest.fixture(scope="module")
def apple_doc():
    from iladub.etkl.document import compile_document
    return compile_document(str(APPLE))


@corpus_only
def test_the_document_adopts_the_page_the_pipeline_could_not_read(apple_doc):
    """apple p1: 0 asserted, 97 escalated, and the grid reads its 28 entry rows."""
    assert 1 in apple_doc.adopted, apple_doc.adopted
    p1 = apple_doc.pages[1]
    assert p1.asserted > 0
    print(f"\napple document: score={apple_doc.score!r} p1={p1.asserted}/{p1.escalated} "
          f"score={p1.score:.4f}")


@corpus_only
def test_an_adopted_page_never_scores_one_by_construction(apple_doc):
    """The zeroing tautology, refused: ink the grid did not read keeps escalating."""
    p1 = apple_doc.pages[1]
    assert p1.escalated > 0
    assert p1.score < 1.0


@corpus_only
def test_pages_that_read_something_are_not_adopted(apple_doc):
    assert 0 not in apple_doc.adopted and 2 not in apple_doc.adopted


@corpus_only
def test_the_document_score_rises(apple_doc):
    """Measured before this loop: 0.06068601583113457. The new value is RECORDED, not a floor
    to hit — but it must not be lower."""
    assert apple_doc.score > 0.06068601583113457


@corpus_only
def test_the_ledger_and_the_graph_agree_on_the_adopted_page(apple_doc):
    """Every escalated token on an adopted page has something in the graph escalating it."""
    from rdflib import RDF
    from iladub.etkl.holon import TAB
    ILADUB = __import__("rdflib").Namespace("https://w3id.org/iladub#")

    residue = [s for s in apple_doc.graph.subjects(RDF.type, ILADUB.CandidateConcept)
               if str(s).endswith("-datagrid-residue")]
    assert len(residue) == 1, residue
    assert apple_doc.pages[1].escalated > 0
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest tests/etkl/test_adoption_document.py -v`
Expected: FAIL — `AttributeError: 'DocumentReport' object has no attribute 'adopted'`

- [ ] **Step 3: Add the field and the pass**

In `src/iladub/etkl/document.py`, add to `DocumentReport` after `repaired`:

```python
    # Page ordinals where the DOCUMENT's last reader — the data grid — superseded a total
    # reading failure (spec 2026-08-09, R73). Empty for every document whose pages read.
    adopted: tuple[int, ...] = ()
```

Insert immediately before the `if validate_shapes and (recognized or section_facts):` gate:

```python
    # ---------------------------------------------------- ADOPTION (spec 2026-08-09, R73)
    # THE DOCUMENT'S LAST READER. Strictly after carriage, section repair, intra-page
    # stitching, chain assembly, chain arithmetic and the section-total oracle: a page's
    # total reading failure is only FINAL at document scope. Placing the pass here is what
    # makes the answer true rather than accidental — and it is why no band-index consumer
    # ever observes a rewritten page (every one of them has already run).
    #
    # The refusal branch is real and measured: compiled STANDALONE, stem p1 adopts at 811
    # FLAT cells and scores 1.0000, against the 825 hierarchical chain-joined cells it
    # asserts here at 0.9706. Page scope would prefer the worse reading. This pass never
    # consults a context-free compile — it reads the pages the driver actually produced.
    from .adoption import is_adoption_candidate
    adopted: list[int] = []
    for p in range(n_pages):
        if not is_adoption_candidate(graph, p, page_doc_uri(p)):
            continue
        # The adoption pass compiles under its OWN page-scoped doc URI, exactly as loop Q's
        # pass 2 does (`r2_doc`). Without it the two verdict judgements would mint the SAME
        # IRI and `dec:supersedes` would silently link a node to itself.
        adopt_doc = URIRef(f"{page_doc_uri(p)}/adopt")
        rep_a = compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes,
                               span_proposer=span_proposer,
                               row_role_proposer=row_role_proposer,
                               doc_uri=adopt_doc,
                               datagrid_adopt=True)
        if rep_a.asserted == 0:
            notes.append(f"page {p}: adoption refused — the grid read nothing")
            continue
        # Withdraw the escalation of every band the grid TOUCHED, then merge the adopted
        # page graph in. The residue candidate rides in with it, so the ledger and the graph
        # agree on what was left unread.
        for idx, r in enumerate(pages[p].regions):
            if idx < len(rep_a.regions) and rep_a.regions[idx].verdict == "superseded":
                _remove_escalation_record(graph, page_doc_uri(p), idx)
        graph += rep_a.graph
        # THE SUPERSESSION, made queryable — loop Q's precedent (dec:supersedes joins the two
        # VERDICT judgements, never the dec:Process containers).
        for idx, r in enumerate(pages[p].regions):
            if idx < len(rep_a.regions) and rep_a.regions[idx].verdict == "superseded":
                v1 = _verdict_decision(graph, page_doc_uri(p), idx)
                v2 = _verdict_decision(rep_a.graph, adopt_doc, idx)
                if v1 is not None and v2 is not None:
                    graph.add((v2, DEC.supersedes, v1))
        pages[p] = rep_a
        adopted.append(p)
        section_facts = True          # document-level facts changed: validation must run
```

and thread `tuple(adopted)` into the returned `DocumentReport` as the last argument.

If `graph += rep_a.graph` re-adds the page's own escalation records for UNTOUCHED bands
(they were never removed and are already in `graph`), that is a no-op — rdflib graphs are sets.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest tests/etkl/test_adoption_document.py -v -s`
Expected: 5 passed. Record the printed document score — it is V2.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/document.py tests/etkl/test_adoption_document.py
git commit -m "feat(adoption): the data grid as the document's last reader"
```

---

### Task 5: The regression floor and the refusal branch

The expensive verification. stem must be byte-identical; the refusal branch must be pinned on
real evidence.

**Files:**
- Modify: `tests/test_corpus_stem.py` (add two tests)
- Test: `tests/test_corpus_stem.py`

**Interfaces:**
- Consumes: the `stem_document` module fixture (one 180 s compile per session).

- [ ] **Step 1: Write the tests**

```python
@needs_stem
def test_stem_document_is_byte_identical_under_adoption(stem_document):
    """The adjudicated floor, to the last digit (spec §V1). Adoption must not fire here:
    carriage makes p1/p2 assert BEFORE the gate can ask. If this number moves, STOP and
    report it — never lower it."""
    assert stem_document.score == 0.9654553611484971, stem_document.score
    assert stem_document.adopted == (), stem_document.adopted
    assert len(stem_document.chains) == 1 and len(stem_document.chains[0]) == 3


@needs_stem
def test_page_scope_adoption_would_have_taken_the_page_the_driver_reads():
    """THE REFUSAL BRANCH, on real evidence (spec §M3).

    stem p1 compiled standalone is a total failure, and the grid reads it — flat, 811 cells,
    no chain, and scoring higher than the correct reading. Under the driver the same page
    asserts 825 hierarchical cells at 0.9706 as a member of the 3-page chain. This test is
    the reason adoption is the document's LAST reader and not the page's first."""
    from iladub.etkl.compile import compile_tables

    standalone = compile_tables(str(STEM), 1, validate_shapes=False, datagrid_adopt=True)
    assert standalone.asserted > 0, "the grid does read this page standalone"
    grid_cells = sum(r.cells for r in standalone.regions)
    assert grid_cells > 500, grid_cells
    print(f"\nstem p1 standalone adopted: {grid_cells} FLAT cells, "
          f"score={standalone.score:.4f}")
```

- [ ] **Step 2: Run them**

Run: `python3 -m pytest tests/test_corpus_stem.py -v -s -m corpus`
Expected: all pass. The stem compile costs ~180 s plus ~41 s validation; do not add a second
`compile_document` call to this module — reuse the fixture.

If `test_stem_document_is_byte_identical_under_adoption` fails, the loop has cost the only
adjudicated floor: stop, report the measured number and both `adopted` and `chains`, and do
not proceed to Task 6.

- [ ] **Step 3: Run the full corpus battery**

Run: `python3 -m pytest tests/test_corpus.py -v -m corpus`
Expected: every document still compiles; no floor lowered. Record each document's score.

- [ ] **Step 4: Commit**

```bash
git add tests/test_corpus_stem.py
git commit -m "test(adoption): the stem floor and the refusal branch, on real evidence"
```

---

### Task 6: Close R73, correct what it said, and record what is left

**Files:**
- Modify: `docs/superpowers/residues.md` (delete the R73 row, append two new rows)
- Modify: `docs/wiki/concepts/data-grid.md:134` (the adoption section)
- Modify: `src/iladub/etkl/compile.py:869-883` (the comment block's final paragraph)

- [ ] **Step 1: Correct the stale comment in `compile.py`**

The final paragraph of the adoption comment block still says adoption is off by default because
"the document driver compiles each page standalone before re-compiling continuation pages."
Replace that paragraph with:

```
    # OFF by default at PAGE scope, and the reason is not the one this comment used to give.
    # The driver makes ONE pass and the carried reading is an INPUT to page p's compile, so
    # forcing adoption on every page leaves the stem document byte-identical at
    # 0.9654553611484971. The real reason is the refusal branch: compiled standalone, stem p1
    # adopts at 811 FLAT cells and scores 1.0000, against the 825 hierarchical chain-joined
    # cells it asserts under the driver at 0.9706 — page scope would prefer the worse reading.
    # Adoption is therefore the DOCUMENT's last reader (document.compile_document), and this
    # flag stays the explicit page-scope API that measurement needs.
```

- [ ] **Step 2: Delete the R73 row and append the new rows**

Delete the `| R73 | …` row from `docs/superpowers/residues.md` entirely. Append:

```
| R79 | **An adopted page's unread structure is escalated as ONE page-level residue candidate**, not per line or per band — a consumer wanting to know which structural lines the grid dropped reads the candidate's `surfaceText` line list rather than a typed refusal per line | loop-adoption-scope, 2026-08-09, measured on apple p1: the residue is <RECORD THE MEASURED TOKEN COUNT> tokens over <N> lines | One candidate keeps the ledger and the graph in agreement at the cost of granularity; per-line refusal has no consumer yet | A consumer that needs to address a dropped line individually; then the residue becomes one candidate per line-run |
| R80 | **apple p1's hierarchy is read by nobody** — the pipeline escalates it as `HierarchicalTable` and the data grid drops it: `ASSETS:`, `Current assets:`, `Non-current assets:`, `Shareholders' equity:` are group labels over the 28 leaf rows the grid reads flat | loop-adoption-scope, 2026-08-09: 15 lines / 64 tokens unadmitted on the page, of which ~40 sit inside escalated bands; the adopted page scores <RECORD> rather than 1.0000 precisely because of them | The grid reads a rectangle; a balance sheet's indent hierarchy is a different reading, and no oracle for it exists on this page beyond the transcription's leaf rows | Transcribe apple p1's group structure, then decide whether the grid derives `tab:RowGroup` from indentation or refuses honestly |
```

Replace every `<RECORD…>` with the number Task 3 Step 4 and Task 4 Step 4 printed. **A plan
placeholder left in the register is a loop failure.**

- [ ] **Step 3: Increment the wiki page**

`docs/wiki/concepts/data-grid.md:134` currently says only "`datagrid_adopt`, off by default.
stem's document compile is unchanged at `0.9654553611484971`." Replace with a short section
stating: adoption is the document's last reader; the page-scope flag stays off and why (the
refusal branch, with the 811-vs-825 numbers); the ledger is line-granular so an adopted page
never scores 1.0000; the measured apple document movement. Update the page's `sources:` to cite
the new spec and keep its confidence tag honest.

- [ ] **Step 4: Run the documentation-governance lint**

Run: `python3 -m pytest tests/test_doc_governance.py -v`
Expected: pass. The spec carries `Doc impact: increment`; the wiki page must cite its sources
and stay out of the nav.

- [ ] **Step 5: Run the whole suite once**

Run: `python3 -m pytest -q`
Expected: green. Report anything that is not, with its output.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/residues.md docs/wiki/concepts/data-grid.md src/iladub/etkl/compile.py
git commit -m "docs(R73): close the residue, correct its mechanism, record what adoption leaves unread"
```

---

## Self-review against the spec

| Spec section | Task |
| --- | --- |
| §5.1 adoption is the document's last reader | Task 4 |
| §5.2 the gate is an AXIOM | Task 2 |
| §5.3 line-granular ledger | Task 1 (pure), Task 3 (page scope), Task 4 (document scope) |
| §5.4 one reading per line in the graph | Task 3 (residue candidate), Task 4 (withdrawal + `dec:supersedes`) |
| §5.5 reports keep the band-index contract | Task 3 |
| §6 V1 stem floor | Task 5 |
| §6 V2 apple document score | Task 4 |
| §6 V3 apple p1 page score | Task 3 |
| §6 V4 ledger disjointness | Task 1 |
| §6 V5 the refusal branch | Task 5 |
| §6 V6 report shape | Task 3 |
| §6 V7 graph/ledger agreement | Task 4 |
| §6 V8 corpus battery | Task 5 |
| §6 the three shipped tests rewritten | Task 3 |
| §8 R73 deleted, two residues recorded | Task 6 |
