# Richer Cell Typing — Date/Currency Body-Signals (Loop B2b) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add **Date** and **Currency** as format-decidable body-signal types on the B2a typed-cell evidence graph, and generalize the four decision queries from "all-Numeric" to **"homogeneous ∧ non-Text"** — gaining real recall on date/currency tables with **zero numeric regression** and a conservative escalate-floor for ambiguous columns.

**Architecture:** `celltype` classifies each cell into `Numeric | Date | Currency | Text` (Numeric = `is_numeric`, unchanged; Date/Currency detectors apply only to non-numeric cells). The four `.rq` replace `?d != tab:Numeric` ("all-Numeric") with "no Text cell ∧ type-homogeneous". Staged: **typing enrichment lands first and is behaviour-neutral** (Date/Currency are "not Numeric" exactly as Text was), then recall is added query-by-query. Detectors + all four generalized queries are **feasibility-proven** (2026-07-17) against a Python "homogeneous non-Text" reference.

**Tech Stack:** Python 3, rdflib (SPARQL SELECT/ASK). Runner is `.venv/bin/python`. No new dependency.

## Global Constraints

From CLAUDE.md §8 + the spec (`docs/superpowers/specs/2026-07-17-richer-cell-typing-design.md`). Every task's requirements implicitly include this. **Reviewers enforce it.**

- **AXIOM — derivation (open world) → SPARQL.** The generalized queries are standard SPARQL SELECT/ASK. **No SHACL. No tuned constant** in any `.rq` or `celltype.py` — a date/currency **regex is a format grammar, not a tuned tolerance** (same character as `is_numeric`'s float-parse); month/day range integers (1–12, 1–31) are calendar structure, not tuning.
- **PROCEDURAL (justified; Python = reference language):** `is_numeric` (unchanged), the new `is_date`/`is_currency` (raw datatype detection), the emitter + runner. No decision logic.
- **Zero numeric regression:** Numeric = `is_numeric` byte-identical; detectors apply only to cells `is_numeric` calls non-numeric. **The B2a numeric differential oracle stays green** — it is the no-regression gate.
- **Not a differential-vs-old-Python oracle** (behaviour intentionally changes). Three batteries pin correctness: (1) no-numeric-regression [= B2a oracle], (2) desired-behaviour [date/currency recall], (3) precision [ambiguous/free-text/mixed still escalate].
- **`tab:Text` is the sole non-signal marker** — the queries never enumerate the type set, so future types (Boolean/Code) need no query change.
- **Behavioural suites green** — a genuinely-numeric fixture must not change. A fixture that *newly asserts* a date/currency table (new recall) is a deliberate, reviewed change (investigate each flip: intended recall vs over-split), NOT a silent regression.
- **Source ownership:** `tab:Date`/`tab:Currency` owned `tab:` in the standalone `tab.ttl`; `.rq` reference only `tab:` + standard SPARQL. No HGA/FnO subject.
- **Scope:** Date + Currency only. **Out of scope:** Boolean, Code/Id, `regions.classify` (B2c), the knowledge/NEURAL disambiguation layers (still escalate free-text/categorical); `is_numeric` unchanged.

---

## File Structure

**Modify:**
- `src/iladub/etkl/celltype.py` — add `is_date`/`is_currency` + the `Numeric→Date→Currency→Text` classifier.
- `vocab/ontology/tab.ttl` — add `tab:Date`, `tab:Currency` individuals of `tab:CellDatatype`.
- `vocab/queries/header-body-split.rq`, `stub-data-split.rq`, `looks-transposed.rq`, `transpose-coherent.rq` — generalize "all-Numeric" → "homogeneous non-Text".
- `tests/etkl/test_celltype.py` — detector precision tests + the three decision batteries.

---

## Task 1: Date/Currency detectors + lattice (typing enrichment — behaviour-neutral)

Add the detectors + classifier + vocab. The queries still key on `!= tab:Numeric`, so Date/Currency cells behave exactly as Text did — **the full suite must stay green with no behavioural change** (this is the safety of staging typing before the query generalization).

**Files:**
- Modify: `src/iladub/etkl/celltype.py`, `vocab/ontology/tab.ttl`
- Modify: `tests/etkl/test_celltype.py`

**Interfaces:**
- Produces: `celltype.is_date(s) -> bool`, `celltype.is_currency(s) -> bool`; `grid_evidence` now emits `tab:cellDatatype ∈ {Numeric, Date, Currency, Text}`. Consumed by Tasks 2–3.

- [ ] **Step 1: Write the failing detector-precision tests**

Add to `tests/etkl/test_celltype.py`:

```python
def test_cell_datatype_detectors():
    from iladub.etkl.celltype import is_date, is_currency
    from iladub.etkl.headers import is_numeric
    # dates: 4-digit year + valid ranges
    for s in ["2024-01-15", "2024/1/5", "31/12/2024", "1-2-2024", "15 Jan 2024", "15 January 2024"]:
        assert is_date(s), s
    # NOT dates (precision): too few digits / no 4-digit year / out-of-range
    for s in ["1-2", "3-4", "99-99-9999", "2024-13-01", "2024-01-32", "hello", "10", ""]:
        assert not is_date(s), s
    # currency: symbol adjacent to a numeric body
    for s in ["$1,000", "€20.50", "£5", "10 £", "-$3.00"]:
        assert is_currency(s), s
    for s in ["$", "USD", "10", "hello"]:
        assert not is_currency(s), s
    # Numeric is UNCHANGED (% and commas still Numeric; $ and dates are NOT numeric)
    assert is_numeric("10") and is_numeric("10%") and is_numeric("1,000")
    assert not is_numeric("$10") and not is_numeric("2024-01-15")


def test_grid_evidence_types_date_and_currency():
    from iladub.etkl import celltype
    from rdflib import RDF
    TAB = __import__("rdflib").Namespace("https://w3id.org/iladub/tab#")
    g = celltype.grid_evidence([(0, 0, "When"), (1, 0, "2024-01-15"), (2, 0, "$5")], 1)
    types = {str(g.value(c, TAB.gridText)): str(g.value(c, TAB.cellDatatype)).split("#")[-1]
             for c in g.subjects(RDF.type, TAB.GridCell)}
    assert types["2024-01-15"] == "Date" and types["$5"] == "Currency" and types["When"] == "Text"
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py::test_cell_datatype_detectors -v`
Expected: FAIL — `is_date`/`is_currency` do not exist.

- [ ] **Step 3: Add `tab:Date`/`tab:Currency` to `tab.ttl`**

In `vocab/ontology/tab.ttl`, next to `tab:Numeric`/`tab:Text`:

```turtle
tab:Date     a tab:CellDatatype ; rdfs:label "Date"@en .
tab:Currency a tab:CellDatatype ; rdfs:label "Currency"@en .
```

- [ ] **Step 4: Implement the detectors + classifier (proven grammars)**

In `src/iladub/etkl/celltype.py`, add (near the top, after the imports) the detectors, and change the classifier line:

```python
import re

_ISO_DATE = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
_DMY_DATE = re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$")
_MON_DATE = re.compile(r"^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}$", re.I)
_CURRENCY = re.compile(r"^-?[$€£¥]\s?-?[\d,]+(\.\d+)?$|^-?[\d,]+(\.\d+)?\s?[$€£¥]$")


def is_date(s):
    """Conservative date typing: a full date shape with a 4-digit YEAR and valid month(1-12)/
    day(1-31) ranges. The 4-digit-year + range requirement excludes '1-2', '99-99-9999',
    '2024-13-01'. Raw datatype detection (PROCEDURAL) — a format grammar, not a tuned tolerance."""
    t = s.strip()
    m = _ISO_DATE.match(t)
    if m:
        parts = re.split(r"[-/]", t)
        return 1 <= int(parts[1]) <= 12 and 1 <= int(parts[2]) <= 31
    m = _DMY_DATE.match(t)
    if m:
        parts = re.split(r"[-/]", t)
        return 1 <= int(parts[1]) <= 12 and 1 <= int(parts[0]) <= 31
    m = _MON_DATE.match(t)
    if m:
        return 1 <= int(re.match(r"^\d{1,2}", t).group()) <= 31
    return False


def is_currency(s):
    """A recognized currency symbol ($ € £ ¥) adjacent to a numeric body. PROCEDURAL raw typing."""
    return bool(_CURRENCY.match(s.strip()))


def _cell_datatype(t):
    """Numeric (= is_numeric, UNCHANGED) first, then the format-decidable structured types, else Text."""
    if is_numeric(t):
        return TAB.Numeric
    if is_date(t):
        return TAB.Date
    if is_currency(t):
        return TAB.Currency
    return TAB.Text
```

Then in `grid_evidence`, change the emission line from `TAB.Numeric if is_numeric(t) else TAB.Text` to `_cell_datatype(t)`.

- [ ] **Step 5: Run detector tests + the WHOLE suite (must be unchanged)**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py -v` — the detector tests + the existing B2a differential battery all pass (the B2a numeric refs are unaffected; the queries still key on `!= tab:Numeric`, so Date/Currency behave as Text did).
Run: `.venv/bin/python -m pytest tests/etkl -q` — **PASS with the SAME counts as before this task** (typing enrichment is behaviour-neutral until the queries generalize). If ANY behavioural or differential test changes here, STOP — a query is (wrongly) already sensitive to the new types, or a detector mis-fires; investigate.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/celltype.py vocab/ontology/tab.ttl tests/etkl/test_celltype.py
git commit -m "feat(etkl): Date/Currency cell-datatype detectors + lattice (typing enrichment) [B2b task 1]

celltype classifies into Numeric|Date|Currency|Text (Numeric = is_numeric UNCHANGED; detectors
apply only to non-numeric cells). Conservative grammars (4-digit-year dates + ranges; symbol
currency). Queries still key on !=Numeric, so behaviour is byte-identical until B2b tasks 2-3.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Generalize the SELECT queries (header/body + stub) — the recall

Generalize `header-body-split.rq` + `stub-data-split.rq` from "all-Numeric" to "homogeneous non-Text" (proven), adding date/currency column recall.

**Files:**
- Modify: `vocab/queries/header-body-split.rq`, `vocab/queries/stub-data-split.rq`, `tests/etkl/test_celltype.py`

- [ ] **Step 1: Write the failing recall + precision + no-regression battery**

Add to `tests/etkl/test_celltype.py` (reuse `_cells`, `_ref_header_body_split`, `_ref_stub_data_split` from B2a for the numeric no-regression cases, unchanged), plus new richer-typed cases:

```python
def _cells_split(grid):  # grid = list of rows, each = list of (col, text)
    return [(r, c, t) for r, row in enumerate(grid) for (c, t) in row]


HB_B2B = [   # (name, grid, ncols, expected split)
    ("numeric no-regression", [[(0, "N"), (1, "S")], [(0, "A"), (1, "10")], [(0, "B"), (1, "20")]], 2, 1),
    ("date column recall", [[(0, "Event"), (1, "When")], [(0, "L"), (1, "2024-01-15")], [(0, "C"), (1, "2024-02-20")]], 2, 1),
    ("currency column recall", [[(0, "Item"), (1, "Cost")], [(0, "P"), (1, "$1,000")], [(0, "B"), (1, "$2,500")]], 2, 1),
    ("dash-not-date -> None", [[(0, "A"), (1, "Range")], [(0, "x"), (1, "1-2")], [(0, "y"), (1, "3-4")]], 2, None),
    ("all-text -> None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2, None),
]


def test_header_body_split_recall_and_precision():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols, want in HB_B2B:
        g = celltype.grid_evidence(_cells_split(grid), ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "header-body-split.rq"), g)
        assert got == want, "%s: got %s want %s" % (name, got, want)


SD_B2B = [   # (name, cells, ncols, split, expected k)
    ("currency data k=2", [(0, 0, "R"), (0, 1, "Y"), (0, 2, "Cost"), (1, 0, "N"), (1, 1, "z"), (1, 2, "$5"), (2, 0, "S"), (2, 1, "w"), (2, 2, "$6")], 3, 1, 2),
    ("date data k=1", [(0, 0, "Item"), (0, 1, "When"), (1, 0, "a"), (1, 1, "2024-01-01"), (2, 0, "b"), (2, 1, "2024-02-01")], 2, 1, 1),
]


def test_stub_data_split_recall():
    from iladub.etkl import celltype
    from rdflib import Literal
    from rdflib.namespace import XSD
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells, ncols, split, want in SD_B2B:
        g = celltype.grid_evidence(cells, ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "stub-data-split.rq"), g,
                                  bindings={"split": Literal(split, datatype=XSD.integer)})
        assert got == want, "%s: got %s want %s" % (name, got, want)
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py::test_header_body_split_recall_and_precision -v`
Expected: FAIL — the date/currency recall cases return `None` (the query still keys on Numeric only).

- [ ] **Step 3: Generalize `header-body-split.rq`**

Replace the "column is all-Numeric from s" clause (the inner `?cc … FILTER NOT EXISTS { … ?d != tab:Numeric }`) with the **homogeneous-non-Text** form (proven):

```sparql
  FILTER EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?r1 . FILTER(?r1 >= ?s)
    # data column = homogeneous non-Text: no Text cell (row>=s) AND no two cells with different types
    FILTER NOT EXISTS { ?ct tab:atGridColumn ?col ; tab:atGridRow ?ctr ; tab:cellDatatype tab:Text . FILTER(?ctr >= ?s) }
    FILTER NOT EXISTS { ?ca tab:atGridColumn ?col ; tab:atGridRow ?car ; tab:cellDatatype ?cat .
                        ?cb tab:atGridColumn ?col ; tab:atGridRow ?cbr ; tab:cellDatatype ?cbt .
                        FILTER(?car >= ?s && ?cbr >= ?s && ?cat != ?cbt) }
  }
```
(Update the comment header to "homogeneous non-Text" and note the B2a proof + the B2b generalization.)

- [ ] **Step 4: Generalize `stub-data-split.rq`**

The two data-column tests (`?c3 is data` inside "every column ≥ k", and `?c4 is data` inside "no data column below k") each replace the `NOT EXISTS { … != tab:Numeric }` with the homogeneous-non-Text pair. For `?c3`:

```sparql
    FILTER NOT EXISTS {
      ?bc3 tab:atGridColumn ?c3 ; tab:atGridRow ?br3 . FILTER(?br3 >= ?split)
      FILTER NOT EXISTS { ?tc3 tab:atGridColumn ?c3 ; tab:atGridRow ?tr3 ; tab:cellDatatype tab:Text . FILTER(?tr3 >= ?split) }
      FILTER NOT EXISTS { ?ac3 tab:atGridColumn ?c3 ; tab:atGridRow ?ar3 ; tab:cellDatatype ?at3 .
                          ?dc3 tab:atGridColumn ?c3 ; tab:atGridRow ?dr3 ; tab:cellDatatype ?dt3 .
                          FILTER(?ar3 >= ?split && ?dr3 >= ?split && ?at3 != ?dt3) }
    }
```
and the symmetric replacement for the `?c4` block. (Both proven.)

- [ ] **Step 5: Run the batteries + no-regression + behavioural**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py -v` — the recall/precision battery green AND the B2a numeric differential battery (`test_header_body_split_matches_reference`, `test_stub_data_split_matches_reference`) STILL green (no-regression, proven — the generalized query subsumes numeric).
Run: `.venv/bin/python -m pytest tests/etkl/test_headers.py tests/etkl/test_rowheaders.py tests/etkl/test_matrix.py tests/etkl/test_hierarchical.py tests/etkl/test_segment.py -q` then full etkl `.venv/bin/python -m pytest tests/etkl -q`.
Expected: PASS. **If a behavioural fixture flips (escalate→assert), investigate:** is it a date/currency column now correctly recognized (intended new recall — update the assertion, note it in the report) or an over-split (a detector mis-fire — fix the detector)? Do NOT loosen a test to hide an over-split.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/header-body-split.rq vocab/queries/stub-data-split.rq tests/etkl/test_celltype.py
git commit -m "feat(etkl): generalize header/body + stub queries to homogeneous-non-Text (date/currency recall) [B2b task 2]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Generalize the ASK queries (transpose oracle) — structured + type-exact coherence

Generalize `looks-transposed.rq` + `transpose-coherent.rq` (proven). `transpose_is_coherent` becomes **type-exact** (a Date+Currency row is now incoherent) — the flagged nuance.

**Files:**
- Modify: `vocab/queries/looks-transposed.rq`, `vocab/queries/transpose-coherent.rq`, `tests/etkl/test_celltype.py`

- [ ] **Step 1: Write the failing orientation battery**

Add to `tests/etkl/test_celltype.py` (reuse the B2a `_ref`/battery for no-regression; add richer cases):

```python
ORI_B2B = [   # (name, cells, expected looks_transposed, expected coherent)
    ("date-value-transposed", [(0, 0, "M"), (0, 1, "A"), (0, 2, "B"), (1, 0, "Start"), (1, 1, "2024-01-01"), (1, 2, "2024-02-01"), (2, 0, "End"), (2, 1, "2024-03-01"), (2, 2, "2024-04-01")], True, True),
    ("upright-currency", [(0, 0, "Item"), (0, 1, "Cost"), (1, 0, "Pen"), (1, 1, "$5"), (2, 0, "Ink"), (2, 1, "$6")], False, True),
    ("incoherent date+currency row", [(0, 0, "K"), (0, 1, "V"), (0, 2, "U"), (1, 0, "x"), (1, 1, "2024-01-01"), (1, 2, "$5")], False, False),
]


def test_orientation_recall_and_typeexact_coherence():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells, want_lt, want_tc in ORI_B2B:
        ncols = max(c for (_r, c, _t) in cells) + 1
        g = celltype.grid_evidence(cells, ncols)
        lt = celltype.run_ask(os.path.join(QDIR, "looks-transposed.rq"), g)
        tc = celltype.run_ask(os.path.join(QDIR, "transpose-coherent.rq"), g)
        assert lt == want_lt, "%s looks_transposed: got %s want %s" % (name, lt, want_lt)
        assert tc == want_tc, "%s coherent: got %s want %s" % (name, tc, want_tc)
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py::test_orientation_recall_and_typeexact_coherence -v`
Expected: FAIL — the incoherent date+currency row still reports coherent (the ASK keys on Numeric-vs-not, so Date+Currency both read as "not Numeric" → homogeneous under the old query).

- [ ] **Step 3: Generalize `looks-transposed.rq`**

Replace both "all-Numeric" clauses with homogeneous-non-Text (proven). The typed-ROW clause (col≥1) and the typed-COLUMN clause (all cols):

```sparql
ASK {
  # a body row whose col>=1 cells are homogeneous non-Text (a typed STRUCTURED row)
  ?rc tab:atGridRow ?r ; tab:atGridColumn ?rcol . FILTER(?r >= 1 && ?rcol >= 1)
  FILTER NOT EXISTS { ?rt tab:atGridRow ?r ; tab:atGridColumn ?rtc ; tab:cellDatatype tab:Text . FILTER(?rtc >= 1) }
  FILTER NOT EXISTS { ?ra tab:atGridRow ?r ; tab:atGridColumn ?rac ; tab:cellDatatype ?rat .
                      ?rb tab:atGridRow ?r ; tab:atGridColumn ?rbc ; tab:cellDatatype ?rbt .
                      FILTER(?rac >= 1 && ?rbc >= 1 && ?rat != ?rbt) }
  # AND no typed STRUCTURED column (any column with all body cells homogeneous non-Text)
  FILTER NOT EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?cr . FILTER(?cr >= 1)
    FILTER NOT EXISTS { ?ct tab:atGridColumn ?col ; tab:atGridRow ?ctr ; tab:cellDatatype tab:Text . FILTER(?ctr >= 1) }
    FILTER NOT EXISTS { ?ca tab:atGridColumn ?col ; tab:atGridRow ?car ; tab:cellDatatype ?cat .
                        ?cb tab:atGridColumn ?col ; tab:atGridRow ?cbr ; tab:cellDatatype ?cbt .
                        FILTER(?car >= 1 && ?cbr >= 1 && ?cat != ?cbt) }
  }
}
```

- [ ] **Step 4: Generalize `transpose-coherent.rq` (type-exact)**

Replace the Numeric-vs-non-Numeric incoherent-row test with **two-different-types** (proven):

```sparql
ASK {
  # coherent iff NOT EXISTS a row with two DIFFERENT cell types among its value columns (col>=1)
  FILTER NOT EXISTS {
    ?a tab:atGridRow ?r ; tab:atGridColumn ?ac ; tab:cellDatatype ?at . FILTER(?ac >= 1)
    ?b tab:atGridRow ?r ; tab:atGridColumn ?bc ; tab:cellDatatype ?bt . FILTER(?bc >= 1 && ?at != ?bt)
  }
}
```
(Comment: now type-exact — a Date+Currency row is incoherent — the intended B2b refinement; must generalize together with `looks-transposed.rq`.)

- [ ] **Step 5: Run the batteries + no-regression + behavioural**

Run: `.venv/bin/python -m pytest tests/etkl/test_celltype.py -v` — the orientation recall battery green AND the B2a `test_orientation_matches_reference` (numeric refs) STILL green (no-regression). Note: the B2a `_ref_transpose_coherent` used the binary numeric-vs-not; for the B2a battery cases (numeric/text only), type-exact and binary agree (a text-only value row is homogeneous Text → coherent both ways; a numeric row → coherent both ways; a mixed numeric+text row → incoherent both ways). If a B2a orientation case diverges, that is a real semantic difference to investigate.
Run: `.venv/bin/python -m pytest tests/etkl/test_orientation.py -q` then full etkl `.venv/bin/python -m pytest tests/etkl -q`. Expected: PASS (investigate any behavioural flip as in Task 2).

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/looks-transposed.rq vocab/queries/transpose-coherent.rq tests/etkl/test_celltype.py
git commit -m "feat(etkl): generalize transpose oracle to structured types + type-exact coherence [B2b task 3]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Supersession + gate verification

**Files:**
- Modify: `tests/etkl/test_transform_gate.py`

- [ ] **Step 1: Extend the gate test**

Add to `tests/etkl/test_transform_gate.py`:

```python
def test_richer_typing_present_no_tuned_constant():
    from iladub.etkl.celltype import is_date, is_currency  # detectors present
    import iladub.etkl.celltype as ct
    # the four generalized queries key on tab:Text as the non-signal marker (not just Numeric)
    import os
    for q in ("header-body-split.rq", "stub-data-split.rq", "looks-transposed.rq", "transpose-coherent.rq"):
        body = _strip_comments(open(os.path.join(QUERIES, q), encoding="utf-8").read())
        assert not _FLOAT.search(body), "%s: no tuned constant" % q
    # celltype.py detectors carry no tuned float tolerance (regexes/ranges are structural)
    assert not _FLOAT.search(_strip_comments(open(ct.__file__, encoding="utf-8").read()))
```

(A date regex / month-range integers are not `\d+\.\d+` floats, so `_FLOAT` will not flag them — confirm.)

- [ ] **Step 2: Run gate + whole suite + ownership**

Run: `.venv/bin/python -m pytest tests/etkl/test_transform_gate.py -v` — PASS.
Run: `.venv/bin/python -m pytest tests/etkl -q` — PASS.
Run: `.venv/bin/python -m pytest tests/test_source_ownership.py -v` — PASS (`tab:Date`/`tab:Currency` + the `.rq` reference only owned `tab:`).
Run: `.venv/bin/python -m pytest -q` — PASS (only pre-existing skips; note any behavioural date/currency flip already reviewed in Tasks 2–3).

- [ ] **Step 3: Commit**

```bash
git add tests/etkl/test_transform_gate.py
git commit -m "test(etkl): gate + supersession verification for richer cell typing [B2b task 4]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage** (against `2026-07-17-richer-cell-typing-design.md`):
- §1/§3 Date+Currency detectors + Numeric-unchanged + homogeneous-non-Text generalization → Tasks 1–3. ✔
- §2 AXIOM queries / PROCEDURAL detectors, no tuned constant → Global Constraints + Task 4. ✔
- §4 all four decisions generalized; transpose coherence type-exact → Tasks 2–3. ✔
- §7 three batteries (no-regression = B2a oracle unchanged + recall + precision) + behavioural-flip investigation → Tasks 1–3. ✔
- §8 source ownership → Task 4. ✔
- §9 out-of-scope (Boolean/Code, regions.classify, knowledge/NEURAL) honoured; conservative escalate-floor preserved. ✔

**2. Placeholder scan:** Clean. Detectors + all four generalized queries are feasibility-proven (2026-07-17) and reproduced verbatim; the batteries carry concrete expected values (each hand-verified against the proven Python reference). No TBD.

**3. Type consistency:** `is_date(s) -> bool`, `is_currency(s) -> bool`, `_cell_datatype(t) -> URIRef` (Task 1) feed `grid_evidence` (unchanged interface). `run_scalar`/`run_ask` (from B2a) reused. The four functions' signatures and the emitter/runner contracts are untouched. `tab:Text` is the sole non-signal marker across all four queries (Task 2–3), so B2c/Boolean extend the lattice without query changes.
