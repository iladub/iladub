"""Perf regression guard for the row-count-sensitive SPARQL derivations.

Audit (2026-07-20): of all vocab/queries/*.rq, four read body-row cells (tab:GridCell /
tab:atGridRow) and can scale with row count — header-body-split, stub-data-split, looks-transposed,
transpose-coherent. The rest read tab:HeaderWord / column markers / the recipe graph (few nodes) and
are not row-count-sensitive. This guard pins each body-row query to a wall-clock bound at 50 rows so a
future edit cannot silently reintroduce an O(n^2) cliff.
"""
import os
import time
from rdflib import Literal
from rdflib.namespace import XSD
from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
_BOUND_S = 2.0   # generous enough to be machine-independent, tight enough to catch O(n^2) at n=50


def _grid(nrows, ncols=4):
    # grouped-header-ish: row 0 Text header, then numeric body
    return [(r, c, ("Hdr%d" % c if r == 0 else str(r * 10 + c))) for r in range(nrows) for c in range(ncols)]


def _time_scalar(q, cells, ncols, bindings=None):
    g = celltype.grid_evidence(cells, ncols)
    t = time.time()
    celltype.run_scalar(os.path.join(QDIR, q), g, bindings)
    return time.time() - t


def _time_ask(q, cells, ncols):
    g = celltype.grid_evidence(cells, ncols)
    t = time.time()
    celltype.run_ask(os.path.join(QDIR, q), g)
    return time.time() - t


def test_header_body_split_scales_to_50_rows():
    dt = _time_scalar("header-body-split.rq", _grid(50), 4)
    assert dt < _BOUND_S, f"header-body-split.rq took {dt:.2f}s at 50 rows (super-linear regression?)"


def test_transpose_coherent_scales_to_50_rows():
    dt = _time_ask("transpose-coherent.rq", _grid(50), 4)
    assert dt < _BOUND_S, f"transpose-coherent.rq took {dt:.2f}s at 50 rows"


def test_stub_data_split_scales_to_50_rows():
    dt = _time_scalar("stub-data-split.rq", _grid(50), 4, {"split": Literal(1, datatype=XSD.integer)})
    assert dt < _BOUND_S, f"stub-data-split.rq took {dt:.2f}s at 50 rows"


def test_looks_transposed_scales_to_50_rows():
    dt = _time_ask("looks-transposed.rq", _grid(50), 4)
    assert dt < _BOUND_S, f"looks-transposed.rq took {dt:.2f}s at 50 rows"


def test_realistic_multirow_report_compiles_fast():
    """A ~50-row grouped-header table that HANGS on the pre-rewrite queries now compiles quickly
    (drives the real hierarchical pipeline: header_body_split + stub/orientation derivations)."""
    from iladub.etkl.geometry import Word, Line
    from iladub.etkl.bands import Band
    from iladub.etkl.hierarchical import classify_hierarchical
    def w(t, x0, x1, top): return Word(t, x0, x1, top, top + 10.0)
    header = [w("Region", 150, 350, 0.0)]                       # spanning coarse header
    leaf = [w("Site", 10, 60, 12), w("Q1", 110, 160, 12), w("Q2", 210, 260, 12), w("Q3", 310, 360, 12)]
    rows = []
    for i in range(50):
        top = 24.0 + i * 12.0
        rows.append([w("s%d" % i, 10, 60, top), w(str(i), 110, 160, top),
                     w(str(i + 1), 210, 260, top), w(str(i + 2), 310, 360, top)])
    lines = [Line(tuple(header), 0.0, 10.0), Line(tuple(leaf), 12, 22)] + \
            [Line(tuple(r), 24.0 + i * 12.0, 34.0 + i * 12.0) for i, r in enumerate(rows)]
    band = Band(tuple(lines), 0.0, lines[-1].bottom)
    t = time.time()
    hreg = classify_hierarchical(band)
    dt = time.time() - t
    assert dt < 5.0, f"50-row hierarchical compile took {dt:.2f}s (regression)"
    assert hreg is not None, "the realistic 50-row report should classify, not escalate/hang"
