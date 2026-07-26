"""Randomized differential tests for the derivation-scaling rewrite.

header-body-split: the shipped query (v2, modal non-Blank column type, Blank wildcard) must equal
the fast Python reference (`_ref_hbs`, also v2) on many random grids incl. Blank tokens — the
oracle is the correctness gate for the query (Task 3, loop A robustness). The v1 semantics (bottom-
cell reference type, no Blank notion) and its old-vs-ref tie test are retired; see the note above
`_ref_hbs` below.
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


# v1 semantics RETIRED in Task 3 (loop A robustness): the bottom-cell reference type was
# corrupted by real-world total/footer rows and had no missing-value (Blank) notion. The OLD
# query text and its old-vs-ref tie test are removed; the shipped query and _ref_hbs below are
# both v2 (modal non-Blank column type, Blank wildcard) — see header-body-split.rq for the design
# note and docs/superpowers/specs/2026-07-26-header-body-split-robust-design.md.

_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A", "(blank)", ""]  # incl. Blank markers


def _ref_hbs(cells, ncols):
    """Fast python reference for header-body-split.rq v2: per column D = modal non-Blank datatype
    computed over BODY ROWS ONLY (row>=1) (argmax of counts; ALL count-tied datatypes considered)
    — a wrapped/multi-line Text header in row 0 must not out-vote the body. A data column has
    D != Text and >=1 non-Blank body cell (row>=1); s_col = 1 + max row, OVER ALL ROWS (incl. row
    0), of a non-Blank cell whose type != D (or 1 if homogeneous) — the diff scan locates the
    header boundary and is deliberately NOT restricted to body rows. Blank cells are wildcards.
    split = MIN(s_col) over data columns and tied D; None if none qualify. Types via the SAME
    celltype._cell_datatype the graph uses."""
    from collections import Counter
    BLANK = _cell_datatype("")      # tab:Blank
    TEXT = _cell_datatype("Alice")  # tab:Text
    by_col = {}
    for (r, c, t) in cells:
        by_col.setdefault(c, []).append((r, _cell_datatype(t)))
    best = None
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
            if s_col >= 1:
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
