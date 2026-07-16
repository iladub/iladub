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
