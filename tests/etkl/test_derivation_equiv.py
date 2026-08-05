"""Randomized differential tests for the derivation-scaling rewrite.

header-body-split: the shipped query (v2, modal non-Blank column type, Blank wildcard) must equal
the fast Python reference (`_ref_hbs`, also v2) on many random grids incl. Blank tokens — the
oracle is the correctness gate for the query (Task 3, loop A robustness). The v1 semantics (bottom-
cell reference type, no Blank notion) and its old-vs-ref tie test are retired; see the note above
`_ref_hbs` below.
"""
import os, random
from types import SimpleNamespace
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD
from iladub.etkl import celltype
from iladub.etkl.celltype import _cell_datatype
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headergraph import HEADER_COVERS_RQ, header_evidence, run_covers
from iladub.etkl.holon import TAB

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")


def _run_text(query_text, cells, ncols, bindings=None):
    g = celltype.grid_evidence(cells, ncols)
    for row in g.query(query_text, initBindings=bindings or {}):
        v = row[0]
        return int(v) if v is not None else None
    return None


# v1 semantics RETIRED in Task 3 (loop A robustness): the bottom-cell reference type was
# corrupted by real-world total/footer rows and had no missing-value (Blank) notion. The OLD
# query text and its old-vs-ref tie test are removed; the shipped query and _ref_hbs below are
# both v2 (modal non-Blank column type, Blank wildcard) — see header-body-split.rq for the design
# note and docs/superpowers/specs/2026-07-26-header-body-split-robust-design.md.

_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A", "(blank)", ""]  # incl. Blank markers


def _ref_hbs(cells, ncols):
    """Fast python reference for header-body-split.rq v2: per column D = modal non-Blank datatype
    computed over rows below the first (row>=1) (argmax of counts; ALL count-tied datatypes
    considered) — the single label row (row 0) must not out-vote the body (a header wrapping into
    rows 1,2,... still votes; that general case is deferred Loop B). A data column has
    D != Text and >=1 non-Blank body cell (row>=1); s_col = 1 + max row, OVER ALL ROWS (incl. row
    0), of a non-Blank cell whose type != D (or 1 if homogeneous) — the diff scan locates the
    header boundary and is deliberately NOT restricted to body rows. Blank cells are wildcards.
    split = MIN(s_col) over data columns and tied D; None if none qualify. Types via the SAME
    celltype._cell_datatype the graph uses.
    R41 (2026-08-05): an s_col past the last evidence row is excluded — a valid split leaves >=1
    body row (mirrors the query's ?maxrow clause)."""
    from collections import Counter
    BLANK = _cell_datatype("")      # tab:Blank
    TEXT = _cell_datatype("Alice")  # tab:Text
    by_col = {}
    for (r, c, t) in cells:
        by_col.setdefault(c, []).append((r, _cell_datatype(t)))
    best = None
    maxrow = max(r for (r, c, t) in cells)   # every line has >=1 cell (text_lines invariant)
    for c, rt in by_col.items():
        nonblank = [(r, dt) for (r, dt) in rt if dt != BLANK]
        body = [(r, dt) for (r, dt) in nonblank if r >= 1]
        if not body:
            continue
        counts = Counter(dt for _, dt in body)          # mode over BODY rows only
        maxn = max(counts.values())
        modal = [dt for dt, n in counts.items() if n == maxn]   # all count-tied
        for D in modal:
            if D == TEXT:
                continue
            diffs = [r for (r, dt) in nonblank if dt != D]       # diff scan over ALL rows
            s_col = (max(diffs) + 1) if diffs else 1
            if 1 <= s_col <= maxrow:         # R41: a split must leave >=1 body row
                best = s_col if best is None else min(best, s_col)
    return best


def _rand_grids(seed, n=200, maxrows=9):
    """Random grids matching the PRODUCTION domain: every row 0..nrows-1 has >=1 cell (the
    geometry.text_lines invariant — no empty rows; the shipped fixtures obey this too), while
    COLUMNS may be ragged/missing within a row."""
    rnd = random.Random(seed)
    for _ in range(n):
        ncols = rnd.randint(1, 4)
        nrows = rnd.randint(1, maxrows)
        cells = []
        for r in range(nrows):
            present = [c for c in range(ncols) if rnd.random() < 0.85]
            if not present:                      # guarantee >=1 cell per row (no empty rows)
                present = [rnd.randrange(ncols)]
            for c in present:
                cells.append((r, c, rnd.choice(_TYPES)))
        yield cells, ncols


def test_header_body_split_new_matches_ref():
    """The rewritten query must equal the reference on many random grids (incl. Date/Currency/
    Text/ragged/empty-column)."""
    new_text = open(os.path.join(QDIR, "header-body-split.rq"), encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=1, n=300):
        ref = _ref_hbs(cells, ncols)
        new = _run_text(new_text, cells, ncols)
        assert ref == new, f"divergence ncols={ncols} cells={cells}: ref={ref} new={new}"


# ---------- stub-data-split + looks-transposed equivalence (new query vs old query text) ----------

def _run_ask_text(query_text, cells, ncols):
    g = celltype.grid_evidence(cells, ncols)
    return bool(g.query(query_text).askAnswer)


OLD_LT = r"""# looks-transposed.rq
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  ?rc tab:atGridRow ?r ; tab:atGridColumn ?rcol . FILTER(?r >= 1 && ?rcol >= 1)
  FILTER NOT EXISTS { ?rt tab:atGridRow ?r ; tab:atGridColumn ?rtc ; tab:cellDatatype tab:Text . FILTER(?rtc >= 1) }
  FILTER NOT EXISTS { ?ra tab:atGridRow ?r ; tab:atGridColumn ?rac ; tab:cellDatatype ?rat .
                      ?rb tab:atGridRow ?r ; tab:atGridColumn ?rbc ; tab:cellDatatype ?rbt .
                      FILTER(?rac >= 1 && ?rbc >= 1 && ?rat != ?rbt) }
  FILTER NOT EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?cr . FILTER(?cr >= 1)
    FILTER NOT EXISTS { ?ct tab:atGridColumn ?col ; tab:atGridRow ?ctr ; tab:cellDatatype tab:Text . FILTER(?ctr >= 1) }
    FILTER NOT EXISTS { ?ca tab:atGridColumn ?col ; tab:atGridRow ?car ; tab:cellDatatype ?cat .
                        ?cb tab:atGridColumn ?col ; tab:atGridRow ?cbr ; tab:cellDatatype ?cbt .
                        FILTER(?car >= 1 && ?cbr >= 1 && ?cat != ?cbt) }
  }
}
"""

OLD_STUB = r"""# stub-data-split.rq
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?k) AS ?stub) WHERE {
  ?km tab:columnIndex ?k . FILTER(?k >= 1)
  FILTER NOT EXISTS {
    ?cm3 tab:columnIndex ?c3 . FILTER(?c3 >= ?k)
    FILTER NOT EXISTS {
      ?bc3 tab:atGridColumn ?c3 ; tab:atGridRow ?br3 . FILTER(?br3 >= ?split)
      FILTER NOT EXISTS { ?tc3 tab:atGridColumn ?c3 ; tab:atGridRow ?tr3 ; tab:cellDatatype tab:Text . FILTER(?tr3 >= ?split) }
      FILTER NOT EXISTS { ?ac3 tab:atGridColumn ?c3 ; tab:atGridRow ?ar3 ; tab:cellDatatype ?at3 .
                          ?dc3 tab:atGridColumn ?c3 ; tab:atGridRow ?dr3 ; tab:cellDatatype ?dt3 .
                          FILTER(?ar3 >= ?split && ?dr3 >= ?split && ?at3 != ?dt3) }
    }
  }
  FILTER NOT EXISTS {
    ?cm4 tab:columnIndex ?c4 . FILTER(?c4 < ?k)
    FILTER EXISTS { ?bc4 tab:atGridColumn ?c4 ; tab:atGridRow ?br4 . FILTER(?br4 >= ?split) }
    FILTER NOT EXISTS { ?tc4 tab:atGridColumn ?c4 ; tab:atGridRow ?tr4 ; tab:cellDatatype tab:Text . FILTER(?tr4 >= ?split) }
    FILTER NOT EXISTS { ?ac4 tab:atGridColumn ?c4 ; tab:atGridRow ?ar4 ; tab:cellDatatype ?at4 .
                        ?dc4 tab:atGridColumn ?c4 ; tab:atGridRow ?dr4 ; tab:cellDatatype ?dt4 .
                        FILTER(?ar4 >= ?split && ?dr4 >= ?split && ?at4 != ?dt4) }
  }
}
"""


def test_looks_transposed_new_matches_old():
    new_text = open(os.path.join(QDIR, "looks-transposed.rq"), encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=3, n=60, maxrows=5):
        old = _run_ask_text(OLD_LT, cells, ncols)
        new = _run_ask_text(new_text, cells, ncols)
        assert old == new, f"looks-transposed divergence ncols={ncols} cells={cells}: old={old} new={new}"


def test_stub_data_split_new_matches_old():
    new_text = open(os.path.join(QDIR, "stub-data-split.rq"), encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=4, n=40, maxrows=5):
        for split in range(0, 4):
            b = {"split": Literal(split, datatype=XSD.integer)}
            old = _run_text(OLD_STUB, cells, ncols, b)
            new = _run_text(new_text, cells, ncols, b)
            assert old == new, f"stub divergence ncols={ncols} split={split} cells={cells}: old={old} new={new}"


# ---------- header-covers.rq equivalence (new query vs Python reference) ----------

def _ref_header_covers(header_rows, grid):
    """Python reference for header-covers.rq: for the LEAF row (max index), a cell covers the one
    column that CONTAINS its ink center — colX0 <= (x0+x1)/2 < colX1 (half-open, mirrors
    regions.column_of). Returns {(leaf_row, cell_idx): (col,)} for cells whose center lands in a
    column (the SPARQL query returns matches only; a center outside all columns yields no entry)."""
    b = grid.boundaries
    if not header_rows:
        return {}
    leaf = len(header_rows) - 1
    out = {}
    for j, cell in enumerate(header_rows[leaf]):
        center = (cell.x0 + cell.x1) / 2.0
        cols = tuple(i for i in range(grid.ncols) if b[i] <= center < b[i + 1])
        if cols:
            out[(leaf, j)] = cols
    return out


def test_header_covers_new_matches_ref():
    import random
    rnd = random.Random(20260726)
    for _ in range(200):
        ncols = rnd.randint(2, 6)
        # strictly-increasing boundaries, each column >= 5 pt wide
        b = [0.0]
        for _i in range(ncols):
            b.append(b[-1] + rnd.uniform(5.0, 90.0))
        grid = LeafGrid(tuple(b), ncols, (b[-1] - b[0]) / ncols, 1.0)
        rows = []
        for _r in range(rnd.randint(1, 3)):
            cells = []
            for _c in range(rnd.randint(1, ncols)):
                x0 = rnd.uniform(b[0], b[-1])
                x1 = x0 + rnd.uniform(1.0, 140.0)
                cells.append(SimpleNamespace(text="t", x0=x0, x1=x1))
            rows.append(cells)
        got = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))
        assert got == _ref_header_covers(rows, grid)


# ---------- row-group-key-logical.rq equivalence (new query vs OLD query text @ cfedaf3) ----------
# Loop N task-4 carry-in (b): the perf rewrite (task 3 review, MINOR-perf) proved its equivalence
# by hand against production calls + a bounded battery, but committed no durable oracle. This is
# that oracle. OLD is embedded VERBATIM from `git show cfedaf3:vocab/queries/row-group-key-logical.rq`
# — the property-path form the rewrite replaced (NOT the v0 page-local `row-group-key.rq`, a
# different query this loop never touched).

OLD_ROW_GROUP_KEY_LOGICAL = r"""PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT ?v ?cell WHERE {
  ?agg tab:aggregates ?m .
  ?cell a tab:EntryCell ; tab:atRow ?m ; tab:atColumn ?mc ; tab:cellText ?v ;
        tab:onPage ?pg ; tab:hasBBox ?bb .
  ?mc tab:continuesColumn* ?lcol .
  ?bb tab:y0 ?y .
  FILTER(STR(?v) != "")
  FILTER NOT EXISTS {
    ?agg tab:aggregates ?m2 .
    ?c2 a tab:EntryCell ; tab:atRow ?m2 ; tab:atColumn ?mc2 ; tab:cellText ?v2 .
    ?mc2 tab:continuesColumn* ?lcol .
    FILTER(STR(?v2) != "" && STR(?v2) != STR(?v))
  }
}
ORDER BY ?pg ?y
LIMIT 1
"""

_ROW_GROUP_KEY_LOGICAL_RQ = os.path.join(QDIR, "row-group-key-logical.rq")


def _rg_table(g, table, ncols):
    """A bare chain member: `ncols` leaf columns, nothing else — the row-group key law never
    reads a table's rows/headers, only its EntryCells and the column correspondence."""
    g.add((table, RDF.type, TAB.HierarchicalTable))
    for c in range(ncols):
        cu = URIRef(f"{table}-c{c}")
        g.add((cu, RDF.type, TAB.LeafColumn))
        g.add((table, TAB.hasLeafColumn, cu))


_rg_counter = [0]     # monotonic, so every random case mints fresh row/cell URIs


def _rg_add_cell(g, table, col, text, page):
    """One EntryCell of `table`'s column `col`, with a fresh row — identity is irrelevant to
    this differential (only the key law's OLD-vs-NEW parity is), so URIs are minted, not read
    back from any minting convention."""
    _rg_counter[0] += 1
    n = _rg_counter[0]
    row = URIRef(f"{table}-r{n}")
    cell = URIRef(f"{table}-e{n}")
    g.add((row, RDF.type, TAB.LeafRow))
    g.add((table, TAB.hasLeafRow, row))
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((table, TAB.hasCell, cell))
    g.add((cell, TAB.atRow, row))
    g.add((cell, TAB.atColumn, URIRef(f"{table}-c{col}")))
    g.add((cell, TAB.cellText, Literal(text)))
    g.add((cell, TAB.onPage, Literal(page, datatype=XSD.integer)))
    bb = BNode()
    g.add((bb, RDF.type, TAB.BBox))
    g.add((bb, TAB.y0, Literal(float(n), datatype=XSD.decimal)))
    g.add((cell, TAB.hasBBox, bb))
    return row


_RG_VALUES = ["Mackay", "Geelong", "Portland", ""]   # "" is the blank case; conflict/unique/
                                                     # suppressed follow from HOW these combine


def _rand_rowgroup_cases(seed, n_graphs=50):
    """`(graph, [(agg, lcol), ...])` — synthetic continuation chains (2-3 members, 2-4 columns),
    columns linked by the REAL `document._link_columns` (so tab:continuesColumn and its
    tab:inLogicalColumn closure are asserted exactly as a genuine compile would, never
    hand-faked), with member cells covering unique / conflicting / blank / suppressed label
    values — the four scenarios row-group-key-logical.rq's uniqueness guard must disambiguate."""
    from iladub.etkl.document import _link_columns
    rnd = random.Random(seed)
    for gi in range(n_graphs):
        g = Graph()
        nmembers = rnd.randint(2, 3)
        ncols = rnd.randint(2, 4)
        tables = [URIRef(f"urn:rgtest/{seed}/{gi}/p{i}#h0") for i in range(nmembers)]
        for t in tables:
            _rg_table(g, t, ncols)
        for i in range(1, nmembers):
            _link_columns(g, tables[i], tables[i - 1])
        cases = []
        for _case in range(rnd.randint(2, 4)):
            lcol_idx = rnd.randrange(ncols)
            _rg_counter[0] += 1
            agg = URIRef(f"urn:rgtest/{seed}/{gi}/agg{_rg_counter[0]}")
            for _m in range(rnd.randint(1, 4)):
                t = rnd.choice(tables)
                page = tables.index(t)
                if rnd.random() < 0.2:                       # suppressed: no cell at all
                    _rg_counter[0] += 1
                    row = URIRef(f"{t}-r{_rg_counter[0]}")
                    g.add((row, RDF.type, TAB.LeafRow))
                    g.add((t, TAB.hasLeafRow, row))
                else:
                    text = rnd.choice(_RG_VALUES)
                    row = _rg_add_cell(g, t, lcol_idx, text, page)
                g.add((agg, TAB.aggregates, row))
            cases.append((agg, URIRef(f"{tables[0]}-c{lcol_idx}")))
        yield g, cases


def test_row_group_key_logical_new_matches_old(tmp_path, monkeypatch):
    """Loop N task-4 carry-in (b): commit the equivalence differential the perf rewrite argued
    by hand (task-3 report's `Query cost` section) but never gave a durable oracle. OLD is the
    property-path form shipped at `cfedaf3` (embedded above); NEW is today's aggregation +
    one-hop-closure rewrite (`vocab/queries/row-group-key-logical.rq`). Both run over the SAME
    graph with the SAME `initBindings`, and their full `(v, cell)` result lists must match
    exactly — not just the winning row, since a divergence upstream of `ORDER BY`/`LIMIT 1`
    would still corrupt which row wins.

    Two legs, per the shipped pattern of this file (a random battery) plus the fixture calls the
    carry-in explicitly asks for:
      (a) the fixture calls — `cut_group_two_page_pdf`'s real document-level witness, captured by
          spying on `rowgroups.derive_row_groups_over` (the one seam `document.py` calls the key
          query through), so the comparison runs on a REAL compiled graph. `page_local_group_
          two_page_pdf` is included too and contributes ZERO calls: its subtotal is REFUSED at
          document level (loop-N review M-1), so `_derive_document_row_groups` never reaches the
          key query for it — the task-3 report's own "retraction: 0" line, reproduced structurally
          rather than asserted by fiat.
      (b) a seeded randomized battery of synthetic chains linked by the REAL
          `document._link_columns` (`_rand_rowgroup_cases`), covering unique / conflicting /
          blank / suppressed label values.
    """
    import iladub.etkl.rowgroups as rowgroups_mod
    from iladub.etkl.document import compile_document
    from tests.etkl.fixtures import cut_group_two_page_pdf, page_local_group_two_page_pdf

    new_text = open(_ROW_GROUP_KEY_LOGICAL_RQ, encoding="utf-8").read()
    captured = []
    orig = rowgroups_mod.derive_row_groups_over

    def _spy(g, attach_to, witnesses, key_query="row-group-key.rq"):
        witnesses = list(witnesses)
        if key_query == "row-group-key-logical.rq":
            captured.append((g, witnesses))
        return orig(g, attach_to, witnesses, key_query)

    monkeypatch.setattr(rowgroups_mod, "derive_row_groups_over", _spy)

    for fixture in (cut_group_two_page_pdf, page_local_group_two_page_pdf):
        pdf = str(tmp_path / f"{fixture.__name__}.pdf")
        fixture(pdf)
        compile_document(pdf)

    def _run(g, text, agg, lcol):
        return [tuple(r) for r in g.query(text, initBindings={"agg": agg, "lcol": lcol})]

    fixture_cases = 0
    for g, witnesses in captured:
        for arow, lcol_uri, _grp in witnesses:
            old = _run(g, OLD_ROW_GROUP_KEY_LOGICAL, arow, lcol_uri)
            new = _run(g, new_text, arow, lcol_uri)
            assert old == new, f"fixture divergence agg={arow} lcol={lcol_uri}: old={old} new={new}"
            fixture_cases += 1
    assert fixture_cases >= 1, \
        "the cut-group fixture must issue at least one document-level key call"

    rand_cases = 0
    for g, cases in _rand_rowgroup_cases(seed=20260803, n_graphs=50):
        for agg, lcol in cases:
            old = _run(g, OLD_ROW_GROUP_KEY_LOGICAL, agg, lcol)
            new = _run(g, new_text, agg, lcol)
            assert old == new, f"random divergence agg={agg} lcol={lcol}: old={old} new={new}"
            rand_cases += 1
    assert rand_cases >= 100, rand_cases


def test_row_group_key_logical_refuses_without_in_logical_column():
    """Loop N task-4 carry-in (a): the query's unstated PRECONDITION, pinned negatively.

    `row-group-key-logical.rq` reaches the label column through `tab:inLogicalColumn`, a
    materialized TRIPLE — not the property-path fixpoint the query it replaced used — so a
    member column with NO such edge makes it REFUSE (0 rows). The OLD form (`cfedaf3`) still
    matched in that state, via the zero-length case of `tab:continuesColumn*` (`?mc = ?lcol`
    needs no edge at all to hold). Built here as a single UNCHAINED table: `?lcol` is bound
    directly to the label column of the table that owns the candidate cell, so the OLD query's
    zero-length path trivially succeeds while the NEW form finds no `tab:inLogicalColumn` triple
    to walk and returns nothing.

    This is the honest, §7-safe direction (never fabricate a correspondence nothing asserted),
    not a regression — no compile-produced graph reaches this query without the edges
    (`document._derive_document_row_groups` runs only inside a chain, where `_link_columns`
    always asserted them). See the query's own header comment and `feed._logical_column`'s
    docstring for the one place the two readings DELIBERATELY diverge: that function still
    falls back to treating an unlinked column as its own logical column; this query does not."""
    g = Graph()
    t = URIRef("urn:rgtest/refusal#h0")
    _rg_table(g, t, 2)
    agg = URIRef("urn:rgtest/refusal#agg")
    row = _rg_add_cell(g, t, 0, "Mackay", 0)
    g.add((agg, TAB.aggregates, row))
    lcol = URIRef(f"{t}-c0")

    new_text = open(_ROW_GROUP_KEY_LOGICAL_RQ, encoding="utf-8").read()
    old = [tuple(r) for r in g.query(OLD_ROW_GROUP_KEY_LOGICAL,
                                     initBindings={"agg": agg, "lcol": lcol})]
    new = [tuple(r) for r in g.query(new_text, initBindings={"agg": agg, "lcol": lcol})]
    assert old, "fixture precondition: the OLD form must still match via its zero-length path"
    assert new == [], f"the NEW form must refuse without an inLogicalColumn edge, got {new}"
