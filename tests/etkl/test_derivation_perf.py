"""Perf regression guard for the row-count-sensitive SPARQL derivations.

Audit (2026-07-20): of all vocab/queries/*.rq, four read body-row cells (tab:GridCell /
tab:atGridRow) and can scale with row count — header-body-split, stub-data-split, looks-transposed,
transpose-coherent. The rest read tab:HeaderWord / column markers / the recipe graph (few nodes) and
are not row-count-sensitive. This guard pins each body-row query to a wall-clock bound at 50 rows so a
future edit cannot silently reintroduce an O(n^2) cliff.
"""
import os
import time
import pytest
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


@pytest.mark.xfail(reason="stub-data-split.rq still O(n^2) — fixed in derivation-scaling Task 3", strict=True)
def test_stub_data_split_scales_to_50_rows():
    dt = _time_scalar("stub-data-split.rq", _grid(50), 4, {"split": Literal(1, datatype=XSD.integer)})
    assert dt < _BOUND_S, f"stub-data-split.rq took {dt:.2f}s at 50 rows"


@pytest.mark.xfail(reason="looks-transposed.rq still O(n^2) — fixed in derivation-scaling Task 3", strict=True)
def test_looks_transposed_scales_to_50_rows():
    dt = _time_ask("looks-transposed.rq", _grid(50), 4)
    assert dt < _BOUND_S, f"looks-transposed.rq took {dt:.2f}s at 50 rows"
