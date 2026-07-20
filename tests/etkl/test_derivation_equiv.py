"""Randomized differential tests for the derivation-scaling rewrite.

Equivalence chain: new query == fast Python reference (`_ref_hbs`) on many random grids,
AND the Python reference == the OLD (pre-rewrite) query on a few small grids. Together:
new == ref == old. The Python reference is used for the bulk comparison because the OLD
O(n^2) query is far too slow to run hundreds of times.
"""
import os, random
from rdflib import Literal
from rdflib.namespace import XSD
from iladub.etkl import celltype
from iladub.etkl.celltype import _cell_datatype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")


def _run_text(query_text, cells, ncols, bindings=None):
    g = celltype.grid_evidence(cells, ncols)
    for row in g.query(query_text, initBindings=bindings or {}):
        v = row[0]
        return int(v) if v is not None else None
    return None


# The CURRENT (pre-rewrite) header-body-split.rq, verbatim — the ground-truth oracle the fast
# Python reference is validated against on small grids.
OLD_HBS = r"""# header-body-split.rq — first body-start row: MIN row s>=1 such that some column is
# homogeneous non-Text (no Text cell, and no two cells of different cellDatatype) from s to the
# band end. Empty result -> None (caller escalates). Generalized from all-Numeric (proven vs the
# Python, 2026-07-16) to homogeneous non-Text (proven, 2026-07-17) — subsumes numeric and adds
# Date/Currency body-column recall [B2b task 2].
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?s) AS ?split) WHERE {
  ?anycell tab:atGridRow ?s . FILTER(?s >= 1)
  FILTER EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?r1 . FILTER(?r1 >= ?s)
    FILTER NOT EXISTS { ?ct tab:atGridColumn ?col ; tab:atGridRow ?ctr ; tab:cellDatatype tab:Text . FILTER(?ctr >= ?s) }
    FILTER NOT EXISTS { ?ca tab:atGridColumn ?col ; tab:atGridRow ?car ; tab:cellDatatype ?cat .
                        ?cb tab:atGridColumn ?col ; tab:atGridRow ?cbr ; tab:cellDatatype ?cbt .
                        FILTER(?car >= ?s && ?cbr >= ?s && ?cat != ?cbt) }
  }
}
"""

_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A", ""]   # Numeric/Currency/Date/Text/blank


def _ref_hbs(cells, ncols):
    """Fast Python port of the OLD query's 'homogeneous non-Text' semantics. Candidate split
    rows are CELL-BEARING rows only (the OLD query's ?s ranges over rows with >=1 GridCell) —
    MIN such s>=1 for which some column has >=1 cell at row>=s, no Text cell at row>=s, and one
    distinct cellDatatype at row>=s. Types via the SAME celltype._cell_datatype the graph uses."""
    if not cells:
        return None
    by_col = {}
    cell_rows = set()
    for (r, c, t) in cells:
        by_col.setdefault(c, []).append((r, _cell_datatype(t)))
        cell_rows.add(r)
    TEXT = _cell_datatype("Alice")   # tab:Text
    for s in sorted(x for x in cell_rows if x >= 1):
        for c, cs in by_col.items():
            suffix = [dt for (r, dt) in cs if r >= s]
            if suffix and TEXT not in suffix and len(set(suffix)) == 1:
                return s
    return None


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


def test_ref_hbs_matches_old_query_on_small_grids():
    """Tie the fast Python reference to the ACTUAL old query on small grids (old query is slow,
    so few + tiny). Proves _ref_hbs faithfully encodes the shipped query's semantics."""
    for cells, ncols in _rand_grids(seed=7, n=25, maxrows=5):
        old = _run_text(OLD_HBS, cells, ncols)
        assert old == _ref_hbs(cells, ncols), f"ref!=old ncols={ncols} cells={cells}: old={old} ref={_ref_hbs(cells,ncols)}"


def test_header_body_split_new_matches_ref():
    """The rewritten query must equal the reference on many random grids (incl. Date/Currency/
    Text/ragged/empty-column)."""
    new_text = open(os.path.join(QDIR, "header-body-split.rq"), encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=1, n=300):
        ref = _ref_hbs(cells, ncols)
        new = _run_text(new_text, cells, ncols)
        assert ref == new, f"divergence ncols={ncols} cells={cells}: ref={ref} new={new}"
