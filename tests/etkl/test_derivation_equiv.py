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

_TYPES = ["7", "3.5", "1,200", "$5", "2020-01-02", "Alice", "N/A", "(blank)", "", "(171)"]  # incl. Blank/abstaining markers


def _ref_hbs(cells, ncols):
    """Fast python reference for header-body-split.rq v2: per column D = modal non-abstaining
    NORMALISED datatype computed over rows below the first (row>=1) (argmax of counts; ALL
    count-tied datatypes considered) — the single label row (row 0) must not out-vote the body (a
    header wrapping into rows 1,2,... still votes; that general case is deferred Loop B). A data
    column has D != Text and >=1 non-abstaining body cell (row>=1); s_col = 1 + max row, OVER ALL
    ROWS (incl. row 0), of a non-abstaining cell whose NORMALISED type != D (or 1 if homogeneous)
    — the diff scan locates the header boundary and is deliberately NOT restricted to body rows.
    Abstaining datatypes (Blank, ParenthesizedNumber — tab:datatypeAbstains) are wildcards.
    split = MIN(s_col) over data columns and tied D; None if none qualify. Types via the SAME
    celltype._cell_datatype the graph uses, normalised the SAME way the graph's
    tab:inDatatypeFamily declarations do (Numeric/Currency -> Quantity).
    R41 (2026-08-05): an s_col past the last evidence row is excluded — a valid split leaves >=1
    body row (mirrors the query's ?maxrow clause).
    Loop quantity-typing (task 2): abstainers now include tab:ParenthesizedNumber alongside
    tab:Blank, and tab:Currency is normalised to tab:Quantity (with tab:Numeric) before both the
    modal vote and the mismatch scan — mirroring the query's THE ONE IDIOM."""
    from collections import Counter
    BLANK = _cell_datatype("")           # tab:Blank
    TEXT = _cell_datatype("Alice")       # tab:Text
    PAREN = _cell_datatype("(171)")      # tab:ParenthesizedNumber
    NUMERIC = _cell_datatype("7")        # tab:Numeric
    CURRENCY = _cell_datatype("$5")      # tab:Currency
    ABSTAIN = {BLANK, PAREN}
    FAMILY = {NUMERIC: TAB.Quantity, CURRENCY: TAB.Quantity}

    def _norm(dt):
        return FAMILY.get(dt, dt)

    by_col = {}
    for (r, c, t) in cells:
        by_col.setdefault(c, []).append((r, _cell_datatype(t)))
    best = None
    maxrow = max(r for (r, c, t) in cells)   # every line has >=1 cell (text_lines invariant)
    for c, rt in by_col.items():
        nonabstain = [(r, _norm(dt)) for (r, dt) in rt if dt not in ABSTAIN]
        body = [(r, dt) for (r, dt) in nonabstain if r >= 1]
        if not body:
            continue
        counts = Counter(dt for _, dt in body)          # mode over BODY rows only
        maxn = max(counts.values())
        modal = [dt for dt, n in counts.items() if n == maxn]   # all count-tied
        for D in modal:
            if D == TEXT:
                continue
            diffs = [r for (r, dt) in nonabstain if dt != D]     # diff scan over ALL rows
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


# OLD_LT/OLD_STUB below are the naive PAIRWISE forms the aggregation rewrite (loop N-era) replaced;
# their job is to prove the aggregated query is behaviorally equivalent to the naive form, NOT to
# pin pre-loop-quantity-typing semantics. Loop quantity-typing (task 2) made the aggregated queries
# compare NORMALISED families and drop abstainers (THE ONE IDIOM); to keep proving the SAME
# structural property (aggregated == naive-pairwise) these naive forms now apply the identical idiom
# inline at every type comparison, rather than being retired — the divergence surfaced here was the
# naive forms lagging the new semantics, not the rewritten .rq files (verified against the brief's
# idiom and against _ref_hbs/header-body-split.rq, which used the SAME idiom and pass).
OLD_LT = r"""# looks-transposed.rq (naive pairwise form, idiom-normalised — see comment above)
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  ?rc tab:atGridRow ?r ; tab:atGridColumn ?rcol ; tab:cellDatatype ?rcraw . FILTER(?r >= 1 && ?rcol >= 1)
  FILTER NOT EXISTS { ?rcraw tab:datatypeAbstains true }   # anchor must be a non-abstaining cell
  FILTER NOT EXISTS { ?rt tab:atGridRow ?r ; tab:atGridColumn ?rtc ; tab:cellDatatype tab:Text . FILTER(?rtc >= 1) }
  FILTER NOT EXISTS {
    ?ra tab:atGridRow ?r ; tab:atGridColumn ?rac ; tab:cellDatatype ?raraw . FILTER(?rac >= 1)
    FILTER NOT EXISTS { ?raraw tab:datatypeAbstains true }
    OPTIONAL { ?raraw tab:inDatatypeFamily ?rafam }
    BIND(COALESCE(?rafam, ?raraw) AS ?rat)
    ?rb tab:atGridRow ?r ; tab:atGridColumn ?rbc ; tab:cellDatatype ?rbraw . FILTER(?rbc >= 1)
    FILTER NOT EXISTS { ?rbraw tab:datatypeAbstains true }
    OPTIONAL { ?rbraw tab:inDatatypeFamily ?rbfam }
    BIND(COALESCE(?rbfam, ?rbraw) AS ?rbt)
    FILTER(?rat != ?rbt)
  }
  FILTER NOT EXISTS {
    ?cc tab:atGridColumn ?col ; tab:atGridRow ?cr ; tab:cellDatatype ?ccraw . FILTER(?cr >= 1)
    FILTER NOT EXISTS { ?ccraw tab:datatypeAbstains true }   # anchor must be a non-abstaining cell
    FILTER NOT EXISTS { ?ct tab:atGridColumn ?col ; tab:atGridRow ?ctr ; tab:cellDatatype tab:Text . FILTER(?ctr >= 1) }
    FILTER NOT EXISTS {
      ?ca tab:atGridColumn ?col ; tab:atGridRow ?car ; tab:cellDatatype ?caraw . FILTER(?car >= 1)
      FILTER NOT EXISTS { ?caraw tab:datatypeAbstains true }
      OPTIONAL { ?caraw tab:inDatatypeFamily ?cafam }
      BIND(COALESCE(?cafam, ?caraw) AS ?cat)
      ?cb tab:atGridColumn ?col ; tab:atGridRow ?cbr ; tab:cellDatatype ?cbraw . FILTER(?cbr >= 1)
      FILTER NOT EXISTS { ?cbraw tab:datatypeAbstains true }
      OPTIONAL { ?cbraw tab:inDatatypeFamily ?cbfam }
      BIND(COALESCE(?cbfam, ?cbraw) AS ?cbt)
      FILTER(?cat != ?cbt)
    }
  }
}
"""

OLD_STUB = r"""# stub-data-split.rq (naive pairwise form, idiom-normalised — see comment above OLD_LT)
PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT (MIN(?k) AS ?stub) WHERE {
  ?km tab:columnIndex ?k . FILTER(?k >= 1)
  FILTER NOT EXISTS {
    ?cm3 tab:columnIndex ?c3 . FILTER(?c3 >= ?k)
    FILTER NOT EXISTS {
      ?bc3 tab:atGridColumn ?c3 ; tab:atGridRow ?br3 ; tab:cellDatatype ?bc3raw . FILTER(?br3 >= ?split)
      FILTER NOT EXISTS { ?bc3raw tab:datatypeAbstains true }   # anchor must be a non-abstaining cell
      FILTER NOT EXISTS { ?tc3 tab:atGridColumn ?c3 ; tab:atGridRow ?tr3 ; tab:cellDatatype tab:Text . FILTER(?tr3 >= ?split) }
      FILTER NOT EXISTS {
        ?ac3 tab:atGridColumn ?c3 ; tab:atGridRow ?ar3 ; tab:cellDatatype ?araw3 . FILTER(?ar3 >= ?split)
        FILTER NOT EXISTS { ?araw3 tab:datatypeAbstains true }
        OPTIONAL { ?araw3 tab:inDatatypeFamily ?afam3 }
        BIND(COALESCE(?afam3, ?araw3) AS ?at3)
        ?dc3 tab:atGridColumn ?c3 ; tab:atGridRow ?dr3 ; tab:cellDatatype ?draw3 . FILTER(?dr3 >= ?split)
        FILTER NOT EXISTS { ?draw3 tab:datatypeAbstains true }
        OPTIONAL { ?draw3 tab:inDatatypeFamily ?dfam3 }
        BIND(COALESCE(?dfam3, ?draw3) AS ?dt3)
        FILTER(?at3 != ?dt3)
      }
    }
  }
  FILTER NOT EXISTS {
    ?cm4 tab:columnIndex ?c4 . FILTER(?c4 < ?k)
    FILTER EXISTS {
      ?bc4 tab:atGridColumn ?c4 ; tab:atGridRow ?br4 ; tab:cellDatatype ?bc4raw . FILTER(?br4 >= ?split)
      FILTER NOT EXISTS { ?bc4raw tab:datatypeAbstains true }   # anchor must be a non-abstaining cell
    }
    FILTER NOT EXISTS { ?tc4 tab:atGridColumn ?c4 ; tab:atGridRow ?tr4 ; tab:cellDatatype tab:Text . FILTER(?tr4 >= ?split) }
    FILTER NOT EXISTS {
      ?ac4 tab:atGridColumn ?c4 ; tab:atGridRow ?ar4 ; tab:cellDatatype ?araw4 . FILTER(?ar4 >= ?split)
      FILTER NOT EXISTS { ?araw4 tab:datatypeAbstains true }
      OPTIONAL { ?araw4 tab:inDatatypeFamily ?afam4 }
      BIND(COALESCE(?afam4, ?araw4) AS ?at4)
      ?dc4 tab:atGridColumn ?c4 ; tab:atGridRow ?dr4 ; tab:cellDatatype ?draw4 . FILTER(?dr4 >= ?split)
      FILTER NOT EXISTS { ?draw4 tab:datatypeAbstains true }
      OPTIONAL { ?draw4 tab:inDatatypeFamily ?dfam4 }
      BIND(COALESCE(?dfam4, ?draw4) AS ?dt4)
      FILTER(?at4 != ?dt4)
    }
  }
}
"""


def test_looks_transposed_new_matches_old():
    new_text = open(os.path.join(QDIR, "looks-transposed.rq"), encoding="utf-8").read()
    for cells, ncols in _rand_grids(seed=3, n=60, maxrows=5):
        old = _run_ask_text(OLD_LT, cells, ncols)
        new = _run_ask_text(new_text, cells, ncols)
        assert old == new, f"looks-transposed divergence ncols={ncols} cells={cells}: old={old} new={new}"


# ---------- transpose-coherent.rq: the ONE acknowledged behavioural change of loop
# harden-transposition, pinned as a documented divergence rather than an equality ----------
#
# OLD_TC is embedded VERBATIM from `git show 7b8359e~1:vocab/queries/transpose-coherent.rq` — the
# form that shipped before `tab:bodyStartsAt` existed. It has NO ROW FILTER AT ALL, only the
# column bounds `?ac >= 1` / `?bc >= 1`, so it read EVERY physical row including the header.
#
# The shipped query filters `?r >= ?bodyStart`. At the DEFAULT ?bodyStart = 1 that is NOT an
# identity — it drops row 0. `looks-transposed.rq` is the opposite case (its old filters were the
# literal constants `?r >= 1` / `?cr >= 1`, so substituting ?bodyStart IS an identity at 1, and
# test_looks_transposed_new_matches_old above asserts plain EQUALITY). This query had no such
# guard, which is exactly why the change went unnoticed and was described as inert.
#
# The change is DELIBERATE and was adjudicated on merits: excluding the header from a BODY-
# coherence check is the intended semantics, and header pollution is what R71 exists to fix. So
# this test documents the divergence's exact shape instead of forbidding it — an UNINTENDED
# divergence still fails.

OLD_TRANSPOSE_COHERENT = r"""# transpose-coherent.rq @ 7b8359e~1 — no row filter, reads the header as data
PREFIX tab: <https://w3id.org/iladub/tab#>
ASK {
  FILTER NOT EXISTS {
    ?a tab:atGridRow ?r ; tab:atGridColumn ?ac ; tab:cellDatatype ?araw . FILTER(?ac >= 1)
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
"""

_TRANSPOSE_COHERENT_RQ = os.path.join(QDIR, "transpose-coherent.rq")
_LOOKS_TRANSPOSED_RQ = os.path.join(QDIR, "looks-transposed.rq")


def _run_ask_text_at(query_text, cells, ncols, body_starts_at):
    g = celltype.grid_evidence(cells, ncols, body_starts_at=body_starts_at)
    return bool(g.query(query_text).askAnswer)


def _mismatch_rows(cells):
    """Python reference for 'which rows carry a type mismatch across their value columns' — the
    single fact BOTH queries are built on. A row mismatches iff its col>=1 cells hold more than one
    distinct NORMALISED datatype family, with abstaining datatypes (Blank, ParenthesizedNumber)
    dropped. Same idiom as `_ref_hbs` above and as the queries' own THE ONE IDIOM."""
    BLANK = _cell_datatype("")
    PAREN = _cell_datatype("(171)")
    NUMERIC = _cell_datatype("7")
    CURRENCY = _cell_datatype("$5")
    ABSTAIN = {BLANK, PAREN}
    FAMILY = {NUMERIC: TAB.Quantity, CURRENCY: TAB.Quantity}
    by_row = {}
    for (r, c, t) in cells:
        if c < 1:
            continue
        dt = _cell_datatype(t)
        if dt in ABSTAIN:
            continue
        by_row.setdefault(r, set()).add(FAMILY.get(dt, dt))
    return {r for r, fams in by_row.items() if len(fams) > 1}


def test_transpose_coherent_diverges_from_old_only_on_the_header_row():
    """The shipped `transpose-coherent.rq` vs the pre-`tab:bodyStartsAt` form, with the divergence
    CHARACTERISED rather than forbidden.

    OLD answers 'coherent' iff NO row anywhere mismatches. NEW answers 'coherent' iff no row at or
    below `?bodyStart` mismatches. So NEW can only ever be MORE permissive, and it differs from OLD
    in exactly one situation:

        some HEADER row (r < ?bodyStart) mismatches, and NO BODY row (r >= ?bodyStart) does.

    That is a header whose labels mix types over a body that does not — precisely the pollution the
    body bound exists to remove. Everything else must agree exactly. `_mismatch_rows` computes the
    predicate independently in Python, so an unintended divergence — one not explained by a
    header-only mismatch — fails here, and so does an unintended AGREEMENT where a divergence is
    predicted.

    Measured on this battery (400 grids x body_start in 1,2,3 = 1200 cases): 127 divergences, ALL
    of them incoherent->coherent, ALL explained; 21 of those fall at the production default of 1.
    """
    new_text = open(_TRANSPOSE_COHERENT_RQ, encoding="utf-8").read()
    diverged = 0
    cases = 0
    for cells, ncols in _rand_grids(seed=3, n=400, maxrows=9):
        old = _run_ask_text(OLD_TRANSPOSE_COHERENT, cells, ncols)
        mism = _mismatch_rows(cells)
        for body_start in (1, 2, 3):
            new = _run_ask_text_at(new_text, cells, ncols, body_start)
            cases += 1
            header_only = (bool({r for r in mism if r < body_start})
                           and not {r for r in mism if r >= body_start})
            assert (old != new) == header_only, (
                f"unexplained transpose-coherent divergence ncols={ncols} body_start={body_start} "
                f"cells={cells}: old={old} new={new} mismatch_rows={sorted(mism)}")
            if old != new:
                assert (old, new) == (False, True), (
                    "the body bound can only RELAX coherence, never tighten it: "
                    f"old={old} new={new} cells={cells}")
                diverged += 1
    assert cases == 1200, cases
    assert diverged == 127, f"divergence count moved: {diverged} (was 127 when this was measured)"


def test_both_transposition_oracles_fail_closed_without_a_body_boundary():
    """The unpinned precondition, now pinned: with `tab:bodyStartsAt` ABSENT, neither oracle may
    assert anything from the missing evidence (CLAUDE.md §8 — never derive by absence).

    This was a live defect in `transpose-coherent.rq`: the binding sat INSIDE its
    `FILTER NOT EXISTS` group, so removing the triple made the group unsatisfiable, NOT EXISTS
    held vacuously, and the query returned True — COHERENT asserted out of nothing. Hoisting the
    binding above the filter makes the ASK simply not match. Measured before the hoist: True.
    Measured after, and asserted here: False, for both queries, on a grid where the boundary
    being present would give True.

    Unreachable in production today — `celltype.grid_evidence` always emits the triple — which is
    why it needs a test rather than a fix downstream.
    """
    lt_text = open(_LOOKS_TRANSPOSED_RQ, encoding="utf-8").read()
    tc_text = open(_TRANSPOSE_COHERENT_RQ, encoding="utf-8").read()
    # a 2x2 grid whose body IS coherent, so transpose-coherent answers True while the boundary is
    # present — the answer that must NOT survive the boundary's removal
    cells = [(0, 0, "Metric"), (0, 1, "7"), (1, 0, "Date"), (1, 1, "2020-01-02")]

    present = celltype.grid_evidence(cells, 2)
    assert bool(present.query(tc_text).askAnswer) is True, \
        "fixture precondition: with the boundary present this grid is coherent"

    absent = celltype.grid_evidence(cells, 2)
    absent.remove((None, TAB.bodyStartsAt, None))
    assert (None, TAB.bodyStartsAt, None) not in absent
    assert bool(absent.query(tc_text).askAnswer) is False, \
        "transpose-coherent must fail CLOSED without tab:bodyStartsAt, not assert coherence"
    assert bool(absent.query(lt_text).askAnswer) is False, \
        "looks-transposed must fail CLOSED without tab:bodyStartsAt"


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
