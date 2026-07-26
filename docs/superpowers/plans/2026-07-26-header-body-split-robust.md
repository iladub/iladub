# Robust Header/Body Split Implementation Plan (Loop A)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the header/body split derivation robust to anomalous bottom rows and missing-value placeholder cells, so real reports (GrainCorp) split correctly (48→4) instead of escalating.

**Architecture:** Two AXIOM changes over the typed-cell evidence graph: (1) `celltype` types genuinely-missing cells as `tab:Blank`; (2) `header-body-split.rq` v2 uses each column's MODAL non-Blank datatype (not the bottom-cell type) with Blank as a wildcard, MIN over data columns. The differential oracle's reference moves to the v2 semantics.

**Tech Stack:** Python 3.12, rdflib SPARQL, pytest. Evidence graph: `iladub.etkl.celltype.grid_evidence` (`tab:GridCell` with `tab:atGridRow/atGridColumn/gridText/cellDatatype`).

## Global Constraints

- **AXIOM only:** the split stays a declarative derivation over the evidence graph; **no tuned constant** (mode = argmax); the `Blank` marker set is minimal + self-documenting. `header_body_split` returning `None` for all-text tables (honest escalation) is preserved.
- **No overfitting:** validate on a synthetic failure-mode fixture + the differential oracle, not on the GrainCorp bytes. **No third-party PDF committed** — the GrainCorp PDF is a local (gitignored scratchpad) confirmation only.
- **Source ownership:** `tab:Blank` is owned `tab:` vocab.
- **Each task leaves the full suite green.** The `tab:Blank` addition changes `grid_evidence` output, which the differential oracle consumes — Task 1 keeps the oracle green by removing Blank-producing tokens from its random-grid alphabet until the v2 reference (Task 3) re-adds Blank coverage.
- **Commands:** `. .venv/bin/activate && python3 -m pytest ...` (binary is `python3`).
- **Branch:** `iladub-header-body-split-robust`.

**Exact current shapes (do not change beyond this plan):**
- `celltype._cell_datatype(t)`: `if is_numeric(t): TAB.Numeric; elif is_date(t): TAB.Date; elif is_currency(t): TAB.Currency; else TAB.Text`. `is_numeric` from `.headers`. `TAB = Namespace("https://w3id.org/iladub/tab#")`.
- `celltype.grid_evidence(cells, ncols)` emits per `(row,col,text)` a `tab:GridCell` with `tab:cellDatatype _cell_datatype(text)`.
- `celltype.run_scalar(rq_path, graph, bindings=None) -> int|None`.
- `header-body-split.rq`: per-column bottom-cell reference type; `SELECT (MIN(?s_col) AS ?split)`.
- `tests/etkl/test_derivation_equiv.py`: `_run_text(query_text, cells, ncols)`, `OLD_HBS` (old query text), `_ref_hbs(cells, ncols)`, `_TYPES=["7","3.5","1,200","$5","2020-01-02","Alice","N/A",""]`, `_rand_grids`, `test_ref_hbs_matches_old_query_on_small_grids`, `test_header_body_split_new_matches_ref`.

---

### Task 1: `tab:Blank` cell type (foundation)

**Files:**
- Modify: `src/iladub/etkl/celltype.py`
- Modify: `vocab/ontology/tab.ttl`
- Modify: `tests/etkl/test_derivation_equiv.py` (keep it green — drop Blank-producing tokens for now)
- Test: `tests/etkl/test_celltype_blank.py` (new)

**Interfaces:**
- Produces: `celltype.is_blank(s) -> bool`; `_cell_datatype` returns `TAB.Blank` for missing cells; `TAB.Blank` declared in `tab.ttl`.

- [ ] **Step 1: Write the failing unit test `tests/etkl/test_celltype_blank.py`**

```python
"""tab:Blank — genuinely-missing cells (empty / '(blank)' / lone '-') type as Blank, not Text.
A minimal, self-documenting missing-value marker set (loop A)."""
from iladub.etkl.celltype import _cell_datatype
from iladub.etkl.holon import TAB


def test_missing_cells_are_blank():
    for t in ("", "   ", "(blank)", "(BLANK)", "-"):
        assert _cell_datatype(t) == TAB.Blank, t


def test_non_missing_cells_unchanged():
    assert _cell_datatype("7") == TAB.Numeric
    assert _cell_datatype("-5") == TAB.Numeric          # a signed number, not blank
    assert _cell_datatype("0") == TAB.Numeric
    assert _cell_datatype("2020-01-02") == TAB.Date
    assert _cell_datatype("$5") == TAB.Currency
    assert _cell_datatype("Alice") == TAB.Text
    assert _cell_datatype("N/A") == TAB.Text            # ambiguous marker -> NOT blank (stays Text)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_celltype_blank.py -q`
Expected: FAIL (`_cell_datatype("(blank)")` currently returns `TAB.Text`, and `TAB.Blank` may not exist).

- [ ] **Step 3: Add `is_blank` + `TAB.Blank` to `src/iladub/etkl/celltype.py`**

Add the helper above `_cell_datatype` and the Blank branch first:

```python
def is_blank(s):
    """A genuinely-missing cell: empty/whitespace, the self-declaring '(blank)', or a lone '-'.
    Minimal, self-documenting missing-value recognition (a format signal, like is_date/is_currency)
    — NOT a broad keyword list; ambiguous markers ('N/A', '0', '-5') are left to their real type."""
    t = s.strip()
    return t == "" or t.lower() == "(blank)" or t == "-"


def _cell_datatype(t):
    """Blank (missing) first, then Numeric (= is_numeric), then the format-decidable structured
    types, else Text."""
    if is_blank(t):
        return TAB.Blank
    if is_numeric(t):
        return TAB.Numeric
    if is_date(t):
        return TAB.Date
    if is_currency(t):
        return TAB.Currency
    return TAB.Text
```

- [ ] **Step 4: Declare `tab:Blank` in `vocab/ontology/tab.ttl`**

Update the CellDatatype block (around lines 206–211): extend the OPEN-lattice comment to mention Blank and add the individual:

```turtle
tab:Blank    a tab:CellDatatype ; rdfs:label "Blank"@en ;
    rdfs:comment "A genuinely-missing cell: empty, the self-declaring '(blank)', or a lone '-'. Not a datum — excluded from a column's dominant type and treated as a wildcard by the header/body split derivation."@en .
```

Edit the `tab:CellDatatype` comment to note Blank is part of the open lattice.

- [ ] **Step 5: Keep the differential oracle green — drop Blank tokens from its alphabet**

In `tests/etkl/test_derivation_equiv.py`, `_TYPES` contains `""` (now Blank). Until the v2 reference (Task 3) understands Blank, remove Blank-producing tokens so the random grids stay Blank-free and the existing `_ref_hbs`/`OLD_HBS`/new-query chain is unaffected. Change:

```python
_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A"]   # (Blank tokens re-added in Task 3 with the v2 reference)
```

(`"N/A"` stays — it is Text, not Blank.)

- [ ] **Step 6: Run tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_celltype_blank.py tests/etkl/test_derivation_equiv.py tests/test_source_ownership.py -q`
Expected: PASS (Blank recognized; oracle still green over Blank-free grids; source-ownership green — `tab:Blank` is owned).

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/celltype.py vocab/ontology/tab.ttl tests/etkl/test_derivation_equiv.py tests/etkl/test_celltype_blank.py
git commit -m "feat(etkl): tab:Blank cell type — recognize genuinely-missing cells (loop A foundation)"
```

---

### Task 2: Failure-mode correctness test (TDD red)

**Files:**
- Create: `tests/etkl/test_header_body_split_robust.py`

**Interfaces:**
- Consumes: `celltype.grid_evidence`, `celltype.run_scalar`, the `header-body-split.rq` path.
- Produces: a correctness test asserting the true split on a report-shaped grid (placeholder in a numeric column + a text bottom/total row). Fails on the current query; passes after Task 3.

- [ ] **Step 1: Write the failing test**

```python
"""Robust header/body split: a report with missing-value placeholders in a data column and a
text total/footer bottom row must still split at the true data-start. Reproduces the GrainCorp
failure mode synthetically (no third-party PDF). See docs/superpowers/specs/2026-07-26-header-body-split-robust-design.md."""
import os
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
HBS = os.path.join(QDIR, "header-body-split.rq")

# cols: 0=Ship(Text), 1=Date, 2=Qty(Numeric). Row 0 = header labels. Rows 1-4 = data
# (row 3 has a '(blank)' placeholder in the numeric Qty column). Row 5 = a text total row
# ('TOTAL' in the Date column flips its bottom-cell type; Qty stays numeric).
CELLS = [
    (0, 0, "Ship"), (0, 1, "Date"),        (0, 2, "Qty"),
    (1, 0, "Alpha"), (1, 1, "2020-01-02"), (1, 2, "100"),
    (2, 0, "Beta"),  (2, 1, "2020-03-04"), (2, 2, "200"),
    (3, 0, "Gamma"), (3, 1, "2020-05-06"), (3, 2, "(blank)"),   # placeholder in a numeric column
    (4, 0, "Delta"), (4, 1, "2020-07-08"), (4, 2, "300"),
    (5, 0, "Total"), (5, 1, "TOTAL"),      (5, 2, "600"),       # text total row
]


def _split(cells, ncols=3):
    g = celltype.grid_evidence(cells, ncols)
    return celltype.run_scalar(HBS, g)


def test_split_is_true_data_start_despite_placeholders_and_total_row():
    # The header is row 0; data starts at row 1. A robust split must return 1 — the Qty column
    # is Numeric once its '(blank)' placeholder is treated as missing, and the Date column's
    # 'TOTAL' bottom cell must not corrupt the boundary.
    assert _split(CELLS) == 1
```

- [ ] **Step 2: Run it to verify it fails (documents the bug)**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_body_split_robust.py -q`
Expected: FAIL. With `tab:Blank` in place (Task 1) but the **current** bottom-type query, the Qty column's `(blank)` (now `tab:Blank`) is a mismatch vs its bottom type Numeric → `s_col=4`, and the Date column is excluded (bottom cell `TOTAL` is Text) → the query returns **4**, not 1. Record the observed value in the report.

- [ ] **Step 3: Commit the red test**

```bash
git add tests/etkl/test_header_body_split_robust.py
git commit -m "test(etkl): failing header/body split case — placeholders + text total row (loop A red)"
```

---

### Task 3: `header-body-split.rq` v2 + oracle reference (green)

**Files:**
- Modify: `vocab/queries/header-body-split.rq`
- Modify: `tests/etkl/test_derivation_equiv.py`

**Interfaces:**
- Consumes: the evidence graph with `tab:Blank`.
- Produces: v2 split semantics (modal non-Blank type, Blank wildcard); the differential oracle retied to the v2 python reference.

- [ ] **Step 1: Rewrite `vocab/queries/header-body-split.rq` to v2**

```sparql
# header-body-split.rq (v2) — MIN body-start row s>=1 over DATA columns, robust to anomalous
# bottom rows and missing-value cells. Per column: D = the MODAL (dominant) non-Blank cellDatatype
# (a group-count argmax); a DATA column has D != tab:Text and >=1 non-Blank body cell (row>=1).
# tab:Blank cells are WILDCARDS — excluded from the mode and never a mismatch. For a data column,
#   s_col = MAX(row of a non-Blank cell whose type != D) + 1   (the label->data transition),
#         = 1                                                    if homogeneous in D.
# split = MIN(s_col). Empty result -> None (all-text -> caller escalates; unchanged).
# Replaces the v1 BOTTOM-cell reference (corrupted by total/footer rows) + no missing-value notion.
# Ties: a count-tie yields multiple D per column; each contributes an s_col and the outer MIN
# absorbs them (mirrored by the python reference in test_derivation_equiv). No tuned constant.
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?s_col) AS ?split) WHERE {
  {
    SELECT ?col ?D (MAX(?diffrow) AS ?maxdiff) (MAX(?bodyrow) AS ?maxbody) WHERE {
      # D = modal non-Blank datatype for ?col (argmax of per-type counts)
      {
        SELECT ?col ?D WHERE {
          { SELECT ?col ?D (COUNT(*) AS ?n) WHERE {
              ?c tab:atGridColumn ?col ; tab:cellDatatype ?D .
              FILTER(?D != tab:Blank)
          } GROUP BY ?col ?D }
          { SELECT ?col (MAX(?n2) AS ?maxn) WHERE {
              { SELECT ?col ?d2 (COUNT(*) AS ?n2) WHERE {
                  ?c2 tab:atGridColumn ?col ; tab:cellDatatype ?d2 .
                  FILTER(?d2 != tab:Blank)
              } GROUP BY ?col ?d2 }
          } GROUP BY ?col }
          FILTER(?n = ?maxn)
        }
      }
      FILTER(?D != tab:Text)
      ?cell tab:atGridColumn ?col ; tab:atGridRow ?crow ; tab:cellDatatype ?ct .
      FILTER(?ct != tab:Blank)                       # Blank cells are wildcards
      BIND(IF(?ct != ?D, ?crow, -1) AS ?diffrow)
      BIND(IF(?crow >= 1, ?crow, -1) AS ?bodyrow)
    } GROUP BY ?col ?D
  }
  BIND(IF(?maxdiff >= 0, ?maxdiff + 1, 1) AS ?s_cand)
  BIND(IF(?maxbody >= 1, ?s_cand, -1) AS ?s_col)     # -1 => no non-Blank body cell, excluded
  FILTER(?s_col >= 1)
}
```

- [ ] **Step 2: Confirm Task 2's correctness test now passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_header_body_split_robust.py -q`
Expected: PASS (split == 1: Qty's `(blank)` is a wildcard so Qty is homogeneous Numeric → `s_col=1`; the Date column's `TOTAL` gives a high `s_col` but MIN picks Qty's 1).

- [ ] **Step 3: Update the differential oracle to the v2 semantics**

In `tests/etkl/test_derivation_equiv.py`: replace `_ref_hbs` with a v2 reference implementing modal-non-Blank + Blank-wildcard (mirroring the query, including tie behavior), re-add a Blank token to `_TYPES`, retie `test_header_body_split_new_matches_ref` to the v2 reference, and retire the `OLD_HBS`/`ref==old` tie (note it — the old semantics are intentionally replaced).

```python
_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A", "(blank)", ""]  # incl. Blank markers


def _ref_hbs(cells, ncols):
    """Fast python reference for header-body-split.rq v2: per column D = modal non-Blank datatype
    (argmax of counts; ALL count-tied datatypes considered); a data column has D != Text and >=1
    non-Blank body cell (row>=1); s_col = 1 + max row of a non-Blank cell whose type != D (or 1 if
    homogeneous); Blank cells are wildcards. split = MIN(s_col) over data columns and tied D; None
    if none qualify. Types via the SAME celltype._cell_datatype the graph uses."""
    from collections import Counter
    BLANK = _cell_datatype("")      # tab:Blank
    TEXT = _cell_datatype("Alice")  # tab:Text
    by_col = {}
    for (r, c, t) in cells:
        by_col.setdefault(c, []).append((r, _cell_datatype(t)))
    best = None
    for c, rt in by_col.items():
        nonblank = [(r, dt) for (r, dt) in rt if dt != BLANK]
        if not nonblank:
            continue
        counts = Counter(dt for _, dt in nonblank)
        maxn = max(counts.values())
        modal = [dt for dt, n in counts.items() if n == maxn]   # all count-tied
        for D in modal:
            if D == TEXT:
                continue
            body = [r for (r, dt) in nonblank if r >= 1]
            if not body:
                continue
            diffs = [r for (r, dt) in nonblank if dt != D]
            s_col = (max(diffs) + 1) if diffs else 1
            if s_col >= 1:
                best = s_col if best is None else min(best, s_col)
    return best
```

Remove (or comment as retired) `OLD_HBS` and `test_ref_hbs_matches_old_query_on_small_grids` — the v1 semantics no longer define correctness. Keep `test_header_body_split_new_matches_ref` (now: shipped v2 query == `_ref_hbs` v2 over random grids incl. Blank).

- [ ] **Step 4: Run the oracle**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_derivation_equiv.py -q`
Expected: PASS (`test_header_body_split_new_matches_ref`: v2 query == v2 reference on many random grids incl. Blank). If they diverge, the query and reference disagree on some grid shape (likely a tie or Blank edge) — read the failing grid, reconcile the query's argmax/Blank handling with the reference until they agree (the oracle is the correctness gate for the query).

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/header-body-split.rq tests/etkl/test_derivation_equiv.py
git commit -m "feat(etkl): header-body-split.rq v2 — modal non-Blank column type, Blank wildcard (loop A)"
```

---

### Task 4: Full-suite regression + GrainCorp confirmation

**Files:**
- None committed (verification only).

- [ ] **Step 1: Full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass (prior total + the new Blank/robust tests). Pay attention to the celltype-derived queries that share the evidence graph — `stub-data-split`, `classify-kind`, `orientation`/`transpose` tests — and the `etkl_demo_data` fixture compiles: the `tab:Blank` addition must not regress them (the synthetic fixtures contain no `(blank)`/lone-`-`/empty cells, so `tab:Blank` is inert for them). If any regresses, read it — a fixture cell may now type as Blank; reconcile without weakening the marker rule.

- [ ] **Step 2: GrainCorp real-world confirmation (LOCAL, not committed)**

Run:
```bash
. .venv/bin/activate && python3 -c "
from iladub.etkl import extract_words, text_lines, detect_bands, infer_leaf_grid
from iladub.etkl.headers import header_body_split
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
tb=[b for b in detect_bands(text_lines(extract_words(p))) if len(b.lines)>10][0]
print('GrainCorp header_body_split:', header_body_split(tb, infer_leaf_grid(tb)))
"
```
Expected: prints **4** (was 48). Record in the report. Do NOT commit the PDF. (GrainCorp compile_tables will still escalate — on the header-tree/caption gap, which defines Loop B; that is expected and not a failure of this loop.)

- [ ] **Step 3: Commit (only if a fix was needed in Step 1; otherwise skip)**

```bash
git add -A && git commit -m "fix(etkl): <describe any regression fix>"
```

---

## Self-Review

**Spec coverage:**
- §1/§3.1 `tab:Blank` (celltype + tab.ttl) → Task 1.
- §1/§3.2 v2 query (modal non-Blank, Blank wildcard, MIN) → Task 3 Step 1; verified by Task 2's correctness test + the oracle.
- §3.3 differential-oracle reference update → Task 3 Step 3.
- §4 committed synthetic regression (cells-list, no PDF) → Task 2; GrainCorp local confirmation → Task 4 Step 2.
- §5 gate (AXIOM, no tuned constant, minimal marker set, None-escalation preserved) → the query stays declarative; `is_blank` is format recognition; all-text still returns None (no data column qualifies).

**Placeholder scan:** none — full code for celltype, tab.ttl, the v2 SPARQL, the python reference, and the tests is given.

**Type consistency:** `is_blank`, `_cell_datatype`→`TAB.Blank`, `TAB.Blank`, `grid_evidence`/`run_scalar`, `header-body-split.rq` `?split`, `_ref_hbs` v2 signature — consistent across tasks. The correctness fixture (`CELLS`) is self-contained in Task 2.

**Coupling note (verified):** the `tab:Blank` addition changes `grid_evidence` output consumed by the oracle; Task 1 keeps the oracle green by removing Blank tokens from `_TYPES`, and Task 3 re-adds them with the matching v2 reference. This ordering keeps every task's suite green.

**Oracle-as-gate:** the v2 SPARQL's exact argmax/tie/Blank behavior is validated by the differential oracle (Task 3 Step 4) against the python reference over random grids — if the hand-written SPARQL is subtly off, that test fails and the implementer reconciles. The correctness test (Task 2) independently pins that the *semantics* are right (split at the true data-start).
