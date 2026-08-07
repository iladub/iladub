# Harden the Transposition Oracles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give both transposition oracles the body-start row instead of assuming the header is one line, so `looks_transposed` stops firing on stem's two wrapped-header bands — closing R71 and unblocking slice B, with corpus scores byte-identical.

**Doc impact:** none for this plan file — the loop's `Doc impact: increment` is declared in the design spec (`2026-08-07-harden-transposition-oracles-design.md`).

**Architecture:** Four tasks. Task 1 adds the owned term `tab:bodyStartsAt` and threads it into the evidence graph with a default that reproduces today's behaviour. Task 2 makes both AXIOMs read it and parameterises the Python reference implementations that prove them correct. Task 3 wires the two orientation call sites and flips the characterisation guard — the only task that changes behaviour. Task 4 measures and closes.

**Tech Stack:** Python 3.11+/pytest, rdflib SPARQL, the owned `tab:` vocabulary.

**Spec:** `docs/superpowers/specs/2026-08-07-harden-transposition-oracles-design.md` — read it first, especially §3 (the differential oracle must move in lockstep) and §4 (why this cannot move a verdict today).

## Global Constraints

- **NO VERDICT MAY CHANGE.** Corpus scores must stay byte-identical: stem **0.9655** / 2152 cells / chain [3], CBH **0.9047**, capacity **1.0000**, apple **0.0606860158**, WHO **0.5597**. This is safe by measurement — every band reaching either oracle today has `header_body_split == 1` — but it must be confirmed, not assumed. The controller runs the corpus suites; you never do.
- **NO TUNED CONSTANT** (CLAUDE.md §8). The body-start row is *derived* by the existing `header_body_split` AXIOM. A word-count or line-count threshold anywhere in this change is a defect, not a shortcut.
- **`None` means fall back to 1, never guess.** `header_body_split` returns `None` when no split exists (an all-text table). Falling back to today's assumption is the honest default; inventing a boundary violates §7 (only emit what the source supports).
- **The differential oracle must not go vacuous.** `tests/etkl/test_celltype.py`'s `_ref_looks_transposed` / `_ref_transpose_coherent` are Python references that prove the AXIOMs correct. If the queries change and the references do not, the equivalence tests keep passing while testing nothing. Task 2 requires the equivalence test be *observed failing* on an inverted reference.
- **`body_starts_at` defaults to 1.** This is what keeps `rowheaders`, `headers.header_body_split` and three test modules unchanged by construction. `header_body_split` computes the split, so it must never be given one.
- **Broken system git:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …`.
- **`timeout` does not exist on this macOS shell.** Run tests in the FOREGROUND.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-harden-transposition` — already created off `main`; the design spec is already committed there.
- Do **not** run the full suite or any corpus suite — the CONTROLLER's job.

---

### Task 1: The term and the evidence

**Files:**
- Modify: `vocab/ontology/tab.ttl`
- Modify: `src/iladub/etkl/celltype.py` (`grid_evidence`)
- Create: `tests/etkl/test_body_start_evidence.py`

**Interfaces:**
- Produces (Tasks 2–3 depend on these exactly): `celltype.grid_evidence(cells, ncols, body_starts_at=1)` emits `_EV["band"] a tab:ClassifyBand ; tab:bodyStartsAt <int>`. The evidence node IRI is `_EV["band"]`; the property is `tab:bodyStartsAt`.

- [ ] **Step 1: Write the failing test** — create `tests/etkl/test_body_start_evidence.py`:

```python
"""tab:bodyStartsAt — the header/body boundary, carried as evidence rather than assumed
(spec 2026-08-07-harden-transposition-oracles-design.md §2.1/§2.2).

The DEFAULT of 1 is load-bearing: it reproduces the behaviour every caller had before this
term existed, so rowheaders, header_body_split and the existing suites are unchanged by
construction rather than by inspection.
"""
from rdflib import Namespace, Literal
from rdflib.namespace import RDF, XSD

TAB = Namespace("https://w3id.org/iladub/tab#")

CELLS = [(0, 0, "Region"), (0, 1, "Value"), (1, 0, "North"), (1, 1, "10")]


def _band_node(g):
    nodes = list(g.subjects(RDF.type, TAB.ClassifyBand))
    assert len(nodes) == 1, f"expected exactly one band node, got {nodes}"
    return nodes[0]


def test_the_default_records_a_body_start_of_one():
    """Today's assumption, now stated in the evidence instead of hidden in a query."""
    from iladub.etkl import celltype
    g = celltype.grid_evidence(CELLS, 2)
    assert (_band_node(g), TAB.bodyStartsAt, Literal(1, datatype=XSD.integer)) in g


def test_an_explicit_body_start_is_carried():
    from iladub.etkl import celltype
    g = celltype.grid_evidence(CELLS, 2, body_starts_at=4)
    assert (_band_node(g), TAB.bodyStartsAt, Literal(4, datatype=XSD.integer)) in g


def test_the_cells_are_unchanged_by_the_new_parameter():
    """The parameter adds evidence; it must not filter or renumber cells."""
    from iladub.etkl import celltype
    a = celltype.grid_evidence(CELLS, 2)
    b = celltype.grid_evidence(CELLS, 2, body_starts_at=4)
    cells_a = set(a.subject_objects(TAB.gridText))
    cells_b = set(b.subject_objects(TAB.gridText))
    assert cells_a == cells_b, "cell evidence must be identical regardless of body_starts_at"


def test_the_term_is_declared_in_the_ontology():
    import os
    from rdflib import Graph
    from rdflib.namespace import RDFS
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    g = Graph().parse(os.path.join(root, "vocab", "ontology", "tab.ttl"), format="turtle")
    assert (TAB.bodyStartsAt, RDFS.domain, TAB.ClassifyBand) in g
    assert (TAB.bodyStartsAt, RDFS.range, XSD.integer) in g
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_body_start_evidence.py -q`
Expected: FAIL — no band node is emitted and `tab:bodyStartsAt` is not declared.

- [ ] **Step 3: Declare the term.** In `vocab/ontology/tab.ttl`, immediately after the `tab:gridColumnCount` declaration (currently around line 246-247), add:

```turtle
tab:bodyStartsAt a owl:DatatypeProperty ; rdfs:domain tab:ClassifyBand ; rdfs:range xsd:integer ; rdfs:label "body starts at"@en ;
    rdfs:comment "First grid ROW that is body rather than header, as derived by header_body_split (headers.py) from the typed-cell evidence. 1 when the header is a single physical line — the assumption the transposition oracles previously hardcoded. A multi-row WRAPPED column header makes it >1; without it, header rows are read as data and destroy the column type-homogeneity looks_transposed tests for."@en .
```

Match the file's existing one-line-per-term style.

- [ ] **Step 4: Thread it into the evidence.** In `src/iladub/etkl/celltype.py`, change `grid_evidence` to:

```python
def grid_evidence(cells, ncols, body_starts_at=1):
    """Build the transient typed-cell evidence graph. `cells`: iterable of (row, col, text).
    Emits a tab:GridCell per cell (row/col/text/cellDatatype) + a column marker per index,
    and one tab:ClassifyBand carrying tab:bodyStartsAt.

    `body_starts_at` is the first row that is BODY rather than header, derived by
    headers.header_body_split. It DEFAULTS TO 1 — the assumption the transposition oracles
    hardcoded before this parameter existed — so every caller that does not pass it behaves
    exactly as before. Note header_body_split is itself a caller: it COMPUTES the split, so
    it must never be given one, and its query does not read this term.
    """
    g = Graph()
    for i, (r, c, t) in enumerate(cells):
        u = _EV["cell-%d" % i]
        g.add((u, RDF.type, TAB.GridCell))
        g.add((u, TAB.atGridRow, Literal(int(r), datatype=XSD.integer)))
        g.add((u, TAB.atGridColumn, Literal(int(c), datatype=XSD.integer)))
        g.add((u, TAB.gridText, Literal(t)))
        g.add((u, TAB.cellDatatype, _cell_datatype(t)))
    for c in range(ncols):
        g.add((_EV["col-%d" % c], TAB.columnIndex, Literal(c, datatype=XSD.integer)))
    g.add((_EV["band"], RDF.type, TAB.ClassifyBand))
    g.add((_EV["band"], TAB.bodyStartsAt, Literal(int(body_starts_at), datatype=XSD.integer)))
    _emit_datatype_declarations(g)
    return g
```

- [ ] **Step 5: Run — verify green, and that nothing else moved**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_body_start_evidence.py tests/etkl/test_celltype.py tests/etkl/test_typing_equiv.py tests/etkl/test_invalid_split_refusal.py tests/test_tab.py -q
```
Expected: all PASS. Those four existing modules are the other `grid_evidence` consumers — if any fails, the default is not reproducing prior behaviour and that is the bug, not the test.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/ontology/tab.ttl src/iladub/etkl/celltype.py tests/etkl/test_body_start_evidence.py && git commit -m "feat(loop-harden-transposition): the header/body boundary becomes evidence

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: The AXIOMs read it, and the references follow

**Files:**
- Modify: `vocab/queries/looks-transposed.rq`
- Modify: `vocab/queries/transpose-coherent.rq`
- Modify: `tests/etkl/test_celltype.py` (the two `_ref_*` functions and the equivalence battery)

**Interfaces:**
- Consumes: Task 1's `tab:bodyStartsAt` triple.
- Produces: both `.rq` files honour the body boundary; `_ref_looks_transposed(cells, body_starts_at=1)` and `_ref_transpose_coherent(cells, body_starts_at=1)`.

**SPARQL subtlety you must not get wrong.** In `looks-transposed.rq` each check is a `SELECT` **subquery**. SPARQL evaluates subqueries bottom-up, so a variable bound in the outer group is **not** visible inside them. `?b tab:bodyStartsAt ?bodyStart` must therefore appear **inside each subquery**, not once at the top. In `transpose-coherent.rq` the check is a plain `FILTER NOT EXISTS` group, so the pattern goes inside that group.

- [ ] **Step 1: Rewrite `vocab/queries/looks-transposed.rq`**

```sparql
# looks-transposed.rq — a typed-STRUCTURED body ROW (cols>=1 homogeneous non-Text) but NO
# typed-STRUCTURED COLUMN (any column with all body cells homogeneous non-Text).
# The transposition signature, generalized to all structured datatypes (Numeric/Date/Currency).
# Homogeneity is judged over datatype FAMILIES (tab:inDatatypeFamily), not raw tab:cellDatatype
# values, and abstaining datatypes (tab:datatypeAbstains — Blank, ParenthesizedNumber) take no
# part: they neither count toward nor break the distinct-type tally.
#
# BODY = row >= ?bodyStart, read from tab:bodyStartsAt rather than assumed to be 1. A multi-row
# WRAPPED column header would otherwise enter the grid as body rows, seeding Text cells across
# every column and destroying the column homogeneity whose ABSENCE this query tests for — the
# false positive R71 recorded. ?bodyStart is bound INSIDE each subquery on purpose: SPARQL
# evaluates subqueries bottom-up, so an outer binding would not reach them.
#
# AGGREGATION FORM (linear in cells): the typed-row EXISTENCE and the typed-column NON-existence are
# two INDEPENDENT existence checks, each a single GROUP BY + HAVING over the body cells (homogeneity
# = one distinct normalised type and no Text), replacing the O(cells^2) pair self-joins AND avoiding
# re-evaluating the column check per row. Equivalent to the prior pairwise form — proven by the
# celltype differential oracle (test_orientation_matches_reference) + the randomized new-vs-reference
# test (tests/etkl/test_derivation_equiv.py). No pair self-join, no cross-correlation.
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  # EXISTS a typed-structured body row (its col>=1 cells homogeneous non-Text)
  FILTER EXISTS {
    SELECT ?r WHERE {
      ?b tab:bodyStartsAt ?bodyStart .
      ?rc tab:atGridRow ?r ; tab:atGridColumn ?rcol ; tab:cellDatatype ?rraw . FILTER(?r >= ?bodyStart && ?rcol >= 1)
      FILTER NOT EXISTS { ?rraw tab:datatypeAbstains true }
      OPTIONAL { ?rraw tab:inDatatypeFamily ?rfam }
      BIND(COALESCE(?rfam, ?rraw) AS ?rt)
    } GROUP BY ?r HAVING(COUNT(DISTINCT ?rt) = 1 && SUM(IF(?rt = tab:Text, 1, 0)) = 0)
  }
  # AND NO typed-structured column (all body cells row>=?bodyStart homogeneous non-Text)
  FILTER NOT EXISTS {
    SELECT ?col WHERE {
      ?b2 tab:bodyStartsAt ?bodyStart2 .
      ?cc tab:atGridColumn ?col ; tab:atGridRow ?cr ; tab:cellDatatype ?craw . FILTER(?cr >= ?bodyStart2)
      FILTER NOT EXISTS { ?craw tab:datatypeAbstains true }
      OPTIONAL { ?craw tab:inDatatypeFamily ?cfam }
      BIND(COALESCE(?cfam, ?craw) AS ?ct)
    } GROUP BY ?col HAVING(COUNT(DISTINCT ?ct) = 1 && SUM(IF(?ct = tab:Text, 1, 0)) = 0)
  }
}
```

- [ ] **Step 2: Rewrite `vocab/queries/transpose-coherent.rq`**

```sparql
# transpose-coherent.rq — TRUE iff every BODY row is type-EXACT across its value columns (col>=1):
# NOT EXISTS a body row with two DIFFERENT cell type FAMILIES (Quantity/Date/Text) in col>=1.
# Types are normalised via tab:inDatatypeFamily before comparison, and abstaining datatypes
# (tab:datatypeAbstains — Blank, ParenthesizedNumber) are dropped on BOTH sides, so a
# parenthesized cell can never be one half of a mismatch pair.
#
# BODY = row >= ?bodyStart, from tab:bodyStartsAt. Before R71 this query had NO row filter at
# all — only column bounds — so it read every physical row including the header. A multi-row
# wrapped header therefore contributed label text as if it were data. This was the more
# polluted of the two transposition oracles.
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  # coherent iff NOT EXISTS a body row with two DIFFERENT normalised types among its value columns
  FILTER NOT EXISTS {
    ?bd tab:bodyStartsAt ?bodyStart .
    ?a tab:atGridRow ?r ; tab:atGridColumn ?ac ; tab:cellDatatype ?araw . FILTER(?ac >= 1 && ?r >= ?bodyStart)
    FILTER NOT EXISTS { ?araw tab:datatypeAbstains true }
    OPTIONAL { ?araw tab:inDatatypeFamily ?afam }
    BIND(COALESCE(?afam, ?araw) AS ?ta)
    ?b tab:atGridRow ?r ; tab:atGridColumn ?bc ; tab:cellDatatype ?braw . FILTER(?bc >= 1)
    FILTER NOT EXISTS { ?braw tab:datatypeAbstains true }
    OPTIONAL { ?braw tab:inDatatypeFamily ?bfam }
    BIND(COALESCE(?bfam, ?braw) AS ?tb)
    FILTER(?ta != ?tb)
  }
}
```

- [ ] **Step 3: Parameterise the references** in `tests/etkl/test_celltype.py`. Replace the two functions with:

```python
def _ref_looks_transposed(cells, body_starts_at=1):
    """loop-quantity-typing fix round 1: row/column homogeneity now goes through
    _ref_typed_non_text (Numeric+Currency one family, abstaining values dropped first)
    instead of a bare _is_numeric-only check.

    R71 hardening: `body_starts_at` replaces the hardcoded `r > 0`. This reference is the
    differential oracle for looks-transposed.rq — if it does not track the query's body
    boundary, the equivalence tests keep passing while testing nothing."""
    rows, cols = {}, {}
    for (r, c, t) in cells:
        if r >= body_starts_at:
            rows.setdefault(r, {})[c] = t
            cols.setdefault(c, []).append(t)
    typed_row = any(_ref_typed_non_text([rm[cc] for cc in rm if cc >= 1]) for rm in rows.values())
    typed_col = any(_ref_typed_non_text(vals) for vals in cols.values())
    return typed_row and not typed_col


def _ref_transpose_coherent(cells, body_starts_at=1):
    """loop-quantity-typing fix round 1: a row is incoherent iff, after dropping
    abstaining values, its col>=1 cells normalise to MORE THAN ONE key (Numeric and
    Currency share the 'quantity' key).

    R71 hardening: this reference previously had NO row filter, mirroring the query's own
    gap — it read header rows as data. `body_starts_at` closes both together."""
    rows = {}
    for (r, c, t) in cells:
        if c >= 1 and r >= body_starts_at:
            rows.setdefault(r, []).append(t)
    for vals in rows.values():
        kept = [v for v in vals if not _abstains(v)]
        if len({_ref_type_key(v) for v in kept}) > 1:
            return False
    return True
```

- [ ] **Step 4: Extend the equivalence battery to exercise a non-default split.** In the same file, replace `test_orientation_matches_reference` with:

```python
def test_orientation_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells in ORI_BATTERY:
        ncols = max(c for (_r, c, _t) in cells) + 1
        # R71: exercise the default AND a shifted body boundary. Without the second, the
        # bodyStartsAt code path is never covered and the equivalence proves nothing about it.
        for body_start in (1, 2):
            g = celltype.grid_evidence(cells, ncols, body_starts_at=body_start)
            lt = celltype.run_ask(os.path.join(QDIR, "looks-transposed.rq"), g)
            tc = celltype.run_ask(os.path.join(QDIR, "transpose-coherent.rq"), g)
            assert lt == _ref_looks_transposed(cells, body_start), \
                "%s looks_transposed @body%d: got %s" % (name, body_start, lt)
            assert tc == _ref_transpose_coherent(cells, body_start), \
                "%s coherent @body%d: got %s" % (name, body_start, tc)
```

- [ ] **Step 5: Run**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_celltype.py tests/etkl/test_derivation_equiv.py tests/etkl/test_body_start_evidence.py -q
```
Expected: all PASS. If `test_derivation_equiv.py` fails, read it before changing anything — it is a randomized new-vs-reference test and a failure there means query and reference genuinely disagree.

- [ ] **Step 6: Prove the equivalence test still bites**

This is the task's real gate. Temporarily change `_ref_looks_transposed`'s `if r >= body_starts_at:` back to `if r > 0:`, run `test_orientation_matches_reference`, and confirm it **FAILS** on a `@body2` case. Then revert and confirm it passes. Paste both outputs in your report.

A differential oracle that cannot detect a divergence between query and reference is the vacuous-gate failure this project has shipped before. Do not skip this.

- [ ] **Step 7: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/queries/looks-transposed.rq vocab/queries/transpose-coherent.rq tests/etkl/test_celltype.py && git commit -m "feat(loop-harden-transposition): both AXIOMs read the body boundary, references follow

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Wire the call sites and flip the guard

**Files:**
- Modify: `src/iladub/etkl/orientation.py`
- Modify: `tests/etkl/test_kind_gate_is_load_bearing.py`

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: the behaviour change. This is the only task that alters what the compiler computes.

- [ ] **Step 1: Wire both oracles.** In `src/iladub/etkl/orientation.py`, add this helper above `looks_transposed`:

```python
def _body_start(region) -> int:
    """The first BODY row of `region`, derived by the header_body_split AXIOM.

    Falls back to 1 — today's assumption — when the split is undefined: header_body_split
    returns None for an all-text table (no column ever homogenizes to a non-Text family),
    and inventing a boundary there would assert more than the source supports (CLAUDE.md §7).
    Also 1 when the region has no grid, since the split is undefined without one.
    """
    if getattr(region, "grid", None) is None:
        return 1
    from .headers import header_body_split
    split = header_body_split(region.band, region.grid)
    return 1 if split is None else int(split)
```

Then in **both** `looks_transposed` and `transpose_is_coherent`, change the evidence line from:

```python
    g = celltype.grid_evidence(_region_cells(region), _ncols(region))
```

to:

```python
    g = celltype.grid_evidence(_region_cells(region), _ncols(region), _body_start(region))
```

Add to each function's docstring one line recording that the body boundary is now derived rather than assumed, citing R71.

- [ ] **Step 2: Run — see the guard fail, which is the point**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_kind_gate_is_load_bearing.py -v
```
Expected: the two `test_looks_transposed_is_a_false_positive_here` cases **FAIL**, because `looks_transposed` now returns `False` on both stem bands. **That is the loop succeeding**, and the guard's own docstring pre-authorised it. Paste this output — it is the loop's headline evidence.

The routing test (`test_page0_region2_still_compiles_through_the_unsupported_path`) must still **PASS**: that band is `UNSUPPORTED_TABLE`, so it never reaches the oracle, and its 586 cells must be untouched. If it fails, stop and report — that is a real regression, not an expected flip.

- [ ] **Step 3: Measure what the oracles now say**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
from dataclasses import replace
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify, assign_cells
from iladub.etkl.headers import header_body_split
from iladub.etkl import orientation
P = "corpus/ag-trade/graincorp-stem-2026-07-31.pdf"
for pg, idx in ((0, 2), (2, 1)):
    band = list(page_bands(P, pg))[idx]
    r = classify(band)
    rc = replace(r, cells=assign_cells(band, r.grid))
    print(f"stem p{pg} region{idx}: split={header_body_split(band, r.grid)} "
          f"looks_transposed={orientation.looks_transposed(rc)} "
          f"transpose_is_coherent={orientation.transpose_is_coherent(rc)}")
EOF
```
Record the output verbatim. Spec §6 requires `transpose_is_coherent` be **measured against the shipped change**, not inherited from an earlier probe — report whatever it actually says.

- [ ] **Step 4: Flip the guard.** In `tests/etkl/test_kind_gate_is_load_bearing.py`:

- Change `test_looks_transposed_is_a_false_positive_here`'s assertion to `is False`, rename it to `test_looks_transposed_no_longer_fires_on_the_wrapped_header`, and rewrite its docstring: the false positive is **fixed**, by giving the oracle the body boundary (`tab:bodyStartsAt`, R71 closed by the 2026-08-07 hardening loop). Its failure message should now say that a return to `True` means the hardening regressed.
- Rewrite the **module docstring**: it currently announces itself as a characterisation guard pinning wrong-but-protective behaviour. That framing is now historical. State what it pins today — that these two bands remain `UNSUPPORTED_TABLE` with a multi-row wrapped header, that the oracle no longer misfires on them, and that the routing test still guards page 0's 586 cells. Keep the record of what the defect was; delete the instructions that no longer apply (the "do not relax it" warning about a deliberately-wrong assertion).
- Leave `test_the_band_is_unsupported_...`, `test_the_header_is_a_multi_row_wrapped_header`, `test_both_bands_carry_real_content` and the routing test **unchanged** — all still true, and they are slice B's evidence.
- Update `test_the_coherence_oracle_refuses_the_transposed_reading` **only if** Step 3 measured it changing. If it still returns `False`, leave it alone.

- [ ] **Step 5: Run**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_kind_gate_is_load_bearing.py tests/etkl/test_closing_slice.py tests/etkl/test_orientation.py tests/etkl/test_transposed_chain.py -q
```
Expected: all PASS. `test_closing_slice.py` and `test_transposed_chain.py` exercise the two fixtures — `false_transposed_pdf` must still escalate `TRANSPOSED` and `transposed_table_pdf` must still compile. **If either moves, stop and report**: those are the R55 ordering specimens and a change there is a real regression, not an expected flip.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/orientation.py tests/etkl/test_kind_gate_is_load_bearing.py && git commit -m "fix(loop-harden-transposition): the oracles read the body boundary; the false positive is gone

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Measure and close

**Files:**
- Modify: `docs/superpowers/specs/2026-08-07-harden-transposition-oracles-design.md`
- Modify: `docs/superpowers/residues.md`

**Note for the controller:** Steps 1–3 are measurements — the controller runs them and hands the implementer the numbers.

- [ ] **Step 1 (CONTROLLER): byte-identity gate**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: 13 passed. Then:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -c "
from iladub.etkl.document import compile_document
for n,p,b in (('apple','corpus/financial/apple-fy2026q3-statements.pdf','0.0606860158'),
              ('capacity','corpus/ag-trade/graincorp-capacity-2026-08-04.pdf','1.0000'),
              ('who','corpus/health/who-wfa-boys-zscore-0-5.pdf','0.5597')):
    print(f'{n}: {compile_document(p).score:.10f}  [{b}]')"
```
Any movement is a regression — §4 predicts none, since every reachable band has `split == 1`. STOP and report if one moves.

- [ ] **Step 2 (CONTROLLER): the cost this adds**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -c "
import time
from iladub.etkl.document import compile_document
t0=time.monotonic(); compile_document('corpus/ag-trade/graincorp-stem-2026-07-31.pdf')
print(f'stem: {time.monotonic()-t0:.0f}s  [pre-loop ~160s isolated]')"
```
Spec §7 requires the per-band cost of the extra `header_body_split` call be measured, not assumed.

- [ ] **Step 3 (CONTROLLER): full suite**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -6
```
Expected: only the known machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag`.

- [ ] **Step 4: Close the spec**

Set `**Status:**` to `closed 2026-08-07` and add a measured-results section: the controller's corpus numbers, the Task 3 Step 3 oracle measurements, the cost figure, and a criterion-by-criterion pass over §6. §6 has seven criteria — check each honestly and say plainly if any is unmet or only partly met.

- [ ] **Step 5: Delete R71**

R71 is closed — `looks_transposed` no longer fires on a caption-line/wrapped-header band, which is exactly its stated closing condition. Per the register's rule, **delete the row in the same change**. Renumber nothing.

If Step 1 showed any corpus movement, R71 does **not** close — report instead.

- [ ] **Step 6: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/specs/2026-08-07-harden-transposition-oracles-design.md docs/superpowers/residues.md && git commit -m "docs(loop-harden-transposition): close — R71 closed, slice B unblocked

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 7: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-07)

- **Spec coverage:** §1 (the defect, both queries) → Tasks 1–2; §2.1 (the term) → Task 1 Step 3; §2.2 (evidence + load-bearing default) → Task 1 Steps 4–5, whose Step 5 runs exactly the other three consumer modules; §2.3 (both queries) → Task 2 Steps 1–2, including the subquery-scope warning; §2.4 (call sites, `None`→1) → Task 3 Step 1's `_body_start`; §3 (differential oracle in lockstep) → Task 2 Steps 3–4 **and** Step 6's observed-failure gate; §4 (verdict-neutral by measurement) → Task 4 Step 1; §5 (the guard flips) → Task 3 Step 4; §6's seven criteria → Task 4 Step 4; §7's cost risk → Task 4 Step 2.
- **Placeholder scan:** none. Every query, function and test is given in full. The one judgement call left open — whether `test_the_coherence_oracle_refuses_the_transposed_reading` needs updating — is explicitly conditioned on Task 3 Step 3's measurement rather than guessed.
- **Type consistency:** `grid_evidence(cells, ncols, body_starts_at=1)` is defined in Task 1 and called positionally in Task 3 (`_body_start(region)`) and by keyword in Tasks 1–2's tests; `_ref_looks_transposed(cells, body_starts_at=1)` / `_ref_transpose_coherent(cells, body_starts_at=1)` are defined and called consistently in Task 2 Steps 3–4; `_body_start` returns `int`, never `None`.
- **One risk I checked rather than assumed:** `?bodyStart` bound inside each `SELECT` subquery rather than once at the top — SPARQL evaluates subqueries bottom-up, so an outer binding would not reach them and the filter would silently compare against an unbound variable. The two subqueries use distinct variable names (`?bodyStart` / `?bodyStart2`) so neither can accidentally capture the other's scope.
