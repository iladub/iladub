import re, math
from rdflib import Graph, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


# ---- frozen Python reference (the anti-overfit oracle; survives the rewrite) ----
def _is_numeric(s):
    t = re.sub(r"[,%]", "", s.strip())
    if not t:
        return False
    try:
        return math.isfinite(float(t))
    except ValueError:
        return False


def _ref_header_body_split(grid, ncols):
    """grid = list of rows; each row = list of (col, text). Port of headers.header_body_split."""
    for start in range(1, len(grid)):
        cols = {i: [] for i in range(ncols)}
        for r in range(start, len(grid)):
            for (c, t) in grid[r]:
                cols[c].append(t)
        if any(vs and all(_is_numeric(v) for v in vs) for vs in cols.values()):
            return start
    return None


def _cells(grid):
    return [(r, c, t) for r, row in enumerate(grid) for (c, t) in row]


# ---- battery: (name, grid, ncols) ----
HB_BATTERY = [
    ("split@1", [[(0, "Name"), (1, "Score")], [(0, "Alice"), (1, "10")], [(0, "Bob"), (1, "20")]], 2),
    ("split@2", [[(0, "Region"), (1, "Sales")], [(1, "USD")], [(0, "North"), (1, "100")], [(0, "South"), (1, "200")]], 2),
    ("all-text->None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2),
    ("3col@1", [[(0, "Id"), (1, "Qty"), (2, "Price")], [(0, "a"), (1, "1"), (2, "9.5")], [(0, "b"), (1, "2"), (2, "8.0")]], 3),
]


def test_header_body_split_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols in HB_BATTERY:
        g = celltype.grid_evidence(_cells(grid), ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "header-body-split.rq"), g)
        assert got == _ref_header_body_split(grid, ncols), "%s: got %s" % (name, got)


def _ref_stub_data_split(grid, ncols):
    """Port of rowheaders.stub_data_split."""
    split = _ref_header_body_split(grid, ncols)
    if split is None:
        return None
    cols = {i: [] for i in range(ncols)}
    for r in range(split, len(grid)):
        for (c, t) in grid[r]:
            cols[c].append(t)
    numeric = [bool(cols[i]) and all(_is_numeric(v) for v in cols[i]) for i in range(ncols)]
    k = next((i for i in range(ncols) if numeric[i]), None)
    if k is None or k == 0:
        return None
    if not all(numeric[i] for i in range(k, ncols)):
        return None
    return k


SD_BATTERY = [
    ("k=2 two stubs", [[(0, "Reg"), (1, "Yr"), (2, "Val")], [(0, "N"), (1, "x"), (2, "5")], [(0, "S"), (1, "y"), (2, "6")]], 3),
    ("k=0 no stub->None", [[(0, "V1"), (1, "V2")], [(0, "1"), (1, "2")], [(0, "3"), (1, "4")]], 2),
    ("text after data->None", [[(0, "A"), (1, "V"), (2, "Note")], [(0, "a"), (1, "1"), (2, "hi")], [(0, "b"), (1, "2"), (2, "yo")]], 3),
    ("all-text->None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2),
]


def test_stub_data_split_matches_reference():
    from iladub.etkl import celltype
    from rdflib import Literal as _L
    from rdflib.namespace import XSD as _X
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols in SD_BATTERY:
        ref = _ref_stub_data_split(grid, ncols)
        split = _ref_header_body_split(grid, ncols)
        if split is None:
            got = None
        else:
            g = celltype.grid_evidence(_cells(grid), ncols)
            got = celltype.run_scalar(os.path.join(QDIR, "stub-data-split.rq"), g,
                                      bindings={"split": _L(split, datatype=_X.integer)})
        assert got == ref, "%s: got %s ref %s" % (name, got, ref)


def _ref_looks_transposed(cells):
    rows, cols = {}, {}
    for (r, c, t) in cells:
        if r > 0:
            rows.setdefault(r, {})[c] = t
            cols.setdefault(c, []).append(t)
    typed_row = any(any(cc >= 1 for cc in rm) and all(_is_numeric(rm[cc]) for cc in rm if cc >= 1) for rm in rows.values())
    typed_col = any(vals and all(_is_numeric(v) for v in vals) for vals in cols.values())
    return typed_row and not typed_col


def _ref_transpose_coherent(cells):
    rows = {}
    for (r, c, t) in cells:
        if c >= 1:
            rows.setdefault(r, []).append(t)
    for vals in rows.values():
        if vals and not (all(_is_numeric(v) for v in vals) or all(not _is_numeric(v) for v in vals)):
            return False
    return True


ORI_BATTERY = [
    ("transposed", [(0, 0, "Metric"), (0, 1, "A"), (0, 2, "B"), (1, 0, "Rev"), (1, 1, "10"), (1, 2, "20"), (2, 0, "Cost"), (2, 1, "3"), (2, 2, "4")]),
    ("upright-numeric", [(0, 0, "Name"), (0, 1, "Score"), (1, 0, "Alice"), (1, 1, "10"), (2, 0, "Bob"), (2, 1, "20")]),
    ("all-text", [(0, 0, "A"), (0, 1, "B"), (1, 0, "x"), (1, 1, "y")]),
    ("incoherent-row", [(0, 0, "K"), (0, 1, "V"), (0, 2, "U"), (1, 0, "wt"), (1, 1, "5"), (1, 2, "kg")]),
    # Regression pin (Task-3 review Minor): col 0 (label column) is all-numeric in the
    # body — one typed-numeric COLUMN — while a *different* body row (r=1) has all
    # col>=1 cells numeric, making typed_row True too; the other body row (r=2) is
    # text in col>=1 so no single column c>=1 is all-numeric on its own. This makes
    # the typed-ROW check (col>=1 only) and the typed-COLUMN check (all columns,
    # including col 0) diverge: correct behaviour reads col 0 across ALL columns and
    # finds it typed (typed_col=True) -> looks_transposed=False. If looks-transposed.rq
    # ever grew a wrong `?col >= 1` guard on the typed-COLUMN NOT EXISTS block (mirroring
    # the typed-ROW block's col>=1 restriction), col 0 would be dropped from
    # consideration, no c>=1 column is all-numeric, typed_col would wrongly flip to
    # False, and the ASK would wrongly flip to True. Verified empirically: the shipped
    # query returns False on this case; a hand-mutated `?col >= 1` variant of the
    # typed-COLUMN check flips it to True.
    ("numeric-col0-mixed-rows", [(0, 0, "Id"), (0, 1, "A"), (0, 2, "B"), (1, 0, "1"), (1, 1, "10"), (1, 2, "20"), (2, 0, "2"), (2, 1, "x"), (2, 2, "y")]),
]


def test_orientation_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells in ORI_BATTERY:
        ncols = max(c for (_r, c, _t) in cells) + 1
        g = celltype.grid_evidence(cells, ncols)
        lt = celltype.run_ask(os.path.join(QDIR, "looks-transposed.rq"), g)
        tc = celltype.run_ask(os.path.join(QDIR, "transpose-coherent.rq"), g)
        assert lt == _ref_looks_transposed(cells), "%s looks_transposed: got %s" % (name, lt)
        assert tc == _ref_transpose_coherent(cells), "%s coherent: got %s" % (name, tc)


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
