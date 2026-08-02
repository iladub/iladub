"""ruledroles — the header-stack law under RULED evidence (loop L, 2026-08-02).

§8 CLASSIFICATION
  * THE DECISION (which header row is the leaf, and what each row above it is) is an **AXIOM**:
    a declarative, open-world derivation over presence facts about the author's own ruled column
    grid — `vocab/queries/header-row-role.rq`. The band is the closure boundary.
  * This module is the **PROCEDURAL** layer only, in the shape classifygraph.py (B2c) and
    headergraph.py (B) already established: two geometric presence tests (`_within` / `_encloses`,
    a strict-interior / whole-cover pair), emitting a transient evidence graph, invoking rdflib,
    and wiring the derived reading into the existing `rowrole.build_row_reading` rewrite +
    `tiling.region_tiles` SHACL oracle. No decision logic lives here, and no tuned constant: the
    only numeric tolerance touched anywhere on this path is `geometry.COORD_EPS`, the repo's
    float-comparison epsilon, reused unchanged. Because the presence facts are emitted here, the
    query itself carries no numeric literal at all.

WHY THIS EXISTS (measured, loop L Task 2)
  Loop C established that a short merged parent and a wrap fragment are geometrically identical
  *in general*, and routed that reading judgment to a NEURAL proposer. Under RULED evidence the
  author has already drawn the answer: the columns are marks in the document, so a header cell's
  relation to them is a fact, not a judgment. This module reads that fact. It does NOT widen the
  borderless path — with no vertical rules it abstains, and loop C's proposer is reached exactly
  as before.

THE LAW (stated in full in header-row-role.rq; nothing here reads label TEXT — residue R4)
  Preconditions (all refusals return None -> the caller's pre-loop-L behaviour, unchanged):
    P1  the band carries the author's vertical rules AND the region's leaf grid IS that ruled grid
        (grid.recover / refine may fall back to whitespace columns; the law is undefined there);
    P2  the header region has at least one non-leaf row to classify;
    P3  the LEAF header row aligns 1:1 with the ruled columns — every column holds exactly one
        leaf cell and no leaf cell falls outside. This is "the deepest line whose words align 1:1
        with the ruled columns" as a *check* rather than a search: header_rows_of already ends the
        header region at the body split, so its last row is the deepest candidate. P3 lives in the
        AXIOM (clause 1 of header-row-role.rq), not here; its refusal arrives as an empty result.
  Then per non-leaf row: furniture (banner) / level (group label) / continuation (wrap fragment),
  per header-row-role.rq.

KNOWN RESIDUE (honest, not silently absorbed)
  A genuinely merged parent whose label is SHORT enough to sit inside one ruled column reads as a
  `continuation` under this law, because geometry alone cannot tell it from a wrap fragment (loop
  C's Finding 3) and reading the text is forbidden here (R4). Three things contain it: the
  derivation only runs where there IS ruled evidence, its output must pass the tiling +
  header-content-conservation SHACL oracle, and no text is ever lost (a furniture row is carried
  as a tab:RegionCaption). To be registered in docs/superpowers/residues.md at loop close.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .geometry import COORD_EPS

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:ruledrole:")     # transient per-band instance namespace

# three dirs up from src/iladub/etkl/ruledroles.py -> repo root, then vocab/queries/
HEADER_ROW_ROLE_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "header-row-role.rq"


# --------------------------------------------------------------------- presence tests (geometry)

def _within(x0: float, x1: float, b, c: int) -> bool:
    """The ink [x0,x1] lies STRICTLY inside ruled column c — it reaches neither boundary.

    Deliberately STRICTER than regions._word_in_column, which asks a different question. That test
    ("does this word FIT in the column?") is about tiling and round-trip faithfulness, where ink
    flush against a boundary is perfectly fine. This test asks "is this ink IN the author's cell?",
    and the answer is visible in the document: a cell's content is laid out inside the cell, clear
    of the rule that draws its border. Ink that REACHES a ruled boundary was not laid out in that
    cell — it is a text run the renderer drew across the grid and rule_aware_lines then chopped at
    the boundary. (Measured on both a real report and the synthetic fixture: every genuine cell
    text clears its rules, while a banner's chopped pieces sit flush against the boundary they
    were cut at — the chop is exact, so the clearance is exactly zero.)

    Strictness is expressed with COORD_EPS, the repo's float-comparison epsilon (geometry.py) —
    it makes `>` mean `>` in floating point. It is NOT a clearance threshold: no minimum padding
    is required, only a non-zero one.
    """
    return x0 > b[c] + COORD_EPS and x1 < b[c + 1] - COORD_EPS


def _encloses(x0: float, x1: float, b, c: int) -> bool:
    """The ink [x0,x1] covers the WHOLE of ruled column c, boundary to boundary — the dual of
    `_within` and, like it, a presence test with COORD_EPS as the float epsilon only. Reaching a
    boundary exactly DOES count as covering it (a merged label drawn edge to edge), which is why
    this side of the pair is non-strict while `_within` is strict."""
    return x0 <= b[c] + COORD_EPS and x1 >= b[c + 1] - COORD_EPS


def ruled_boundaries(band):
    """The band's ruled boundary MARKS — the author's vertical rules, or the derived column_xs
    (author rules plus the interior boundaries loop G's header confirmation added) — or None when
    the band carries no vertical rule at all.

    This is verbatim the expression grid._rule_boundaries uses to pick its candidate boundaries,
    kept in step with it on purpose. It is deliberately NOT a call to `_rule_boundaries` itself:
    that function additionally VETOES the whole set when any band word straddles a boundary, which
    is exactly what a banner does (measured on a real report: the veto fires, yet recover_leaf_grid
    still lands on the ruled grid via a suffix that skips the banner line). Using the veto here
    would refuse the derivation on precisely the documents it exists for.
    """
    if not band.rules:
        return None
    xs = sorted(band.column_xs) if band.column_xs else sorted({round(r.x, 2) for r in band.rules})
    return tuple(float(x) for x in xs) if len(xs) >= 2 else None


def grid_is_the_ruled_grid(band, grid) -> bool:
    """P1: every boundary of the region's leaf grid is one of the band's ruled marks.

    Subset, not equality: `grid._rule_boundaries` legitimately DROPS marks bounding an interval no
    ink occupies (a double-drawn table border), so the grid is a sub-selection of the marks. What
    must not happen is a boundary the author never drew — that would mean the grid came from the
    whitespace fallback, where this law is undefined. Exact float comparison is correct because
    both sides are built from the same list of marks.
    """
    xs = ruled_boundaries(band)
    if xs is None or grid.ncols < 2:
        return False
    return set(float(x) for x in grid.boundaries) <= set(xs)


# ------------------------------------------------------------------- evidence graph + query run

def role_evidence(header_rows, grid) -> Graph:
    """Fresh Graph() for one band's header region — the inputs to header-row-role.rq.

    Emits one tab:RuledColumn per column; one tab:LeafHeaderCell per cell of the LAST row (the
    query's clause 1 reads these to check the 1:1 alignment — the leaf row is never given a role);
    and for every NON-LEAF row (header_rows[:-1]) a tab:HeaderRegionRow carrying its cells'
    `withinRuledColumn` / `enclosesRuledColumn` presence facts plus the row's own combined-ink
    `rowEnclosesRuledColumn` facts.
    """
    g = Graph()
    b = grid.boundaries
    cols = []
    for i in range(grid.ncols):
        col = URIRef(f"{_EV}col{i}")
        cols.append(col)
        g.add((col, RDF.type, TAB.RuledColumn))
    for j, cell in enumerate(header_rows[-1]):
        lu = URIRef(f"{_EV}leaf{j}")
        g.add((lu, RDF.type, TAB.LeafHeaderCell))
        for i in range(grid.ncols):
            if _within(cell.x0, cell.x1, b, i):
                g.add((lu, TAB.withinRuledColumn, cols[i]))
    for r, row in enumerate(header_rows[:-1]):
        ru = URIRef(f"{_EV}row{r}")
        g.add((ru, RDF.type, TAB.HeaderRegionRow))
        g.add((ru, TAB.headerRowOrder, Literal(r, datatype=XSD.integer)))
        rx0 = min(c.x0 for c in row)
        rx1 = max(c.x1 for c in row)
        for i in range(grid.ncols):
            if _encloses(rx0, rx1, b, i):
                g.add((ru, TAB.rowEnclosesRuledColumn, cols[i]))
        for j, cell in enumerate(row):
            cu = URIRef(f"{_EV}row{r}c{j}")
            g.add((cu, RDF.type, TAB.HeaderRegionCell))
            g.add((ru, TAB.hasHeaderRegionCell, cu))
            for i in range(grid.ncols):
                if _within(cell.x0, cell.x1, b, i):
                    g.add((cu, TAB.withinRuledColumn, cols[i]))
                if _encloses(cell.x0, cell.x1, b, i):
                    g.add((cu, TAB.enclosesRuledColumn, cols[i]))
    return g


def run_roles(rq_path, graph: Graph, n_rows: int):
    """Run header-row-role.rq; return the role vector (one entry per non-leaf row, in order), or
    None if the derivation did not decide every row.

    An EMPTY result is the query's own refusal: clause 1 (the leaf row must align 1:1 with the
    ruled columns) is a whole-query FILTER, so a stack this law does not govern yields no rows at
    all. A short-but-nonempty result would mean a malformed evidence graph; either way a partial
    answer is refused rather than silently padded."""
    q = Path(rq_path).read_text(encoding="utf-8")
    by_row = {int(row.row): str(row.role) for row in graph.query(q)}
    if len(by_row) != n_rows or set(by_row) != set(range(n_rows)):
        return None
    return tuple(by_row[i] for i in range(n_rows))


# ------------------------------------------------------------------------------- the derivation

def derive_row_roles(band, header_rows, grid):
    """The role vector for `header_rows`' non-leaf rows under ruled evidence, or None to refuse.

    Refuses (None) when any precondition P1-P3 fails — see the module docstring. Refusal is not a
    verdict: the caller simply keeps its pre-loop-L behaviour.
    """
    if len(header_rows) < 2:
        return None                                        # P2: no non-leaf row to classify
    if not grid_is_the_ruled_grid(band, grid):
        return None                                        # P1: not the author's ruled grid
    # P3 (the leaf row's 1:1 alignment) is NOT tested here — it is clause 1 of the AXIOM itself,
    # and its refusal arrives as an empty result from the query.
    return run_roles(HEADER_ROW_ROLE_RQ, role_evidence(header_rows, grid), len(header_rows) - 1)


def resolve_ruled_header_rows(graph, hreg, band, table_uri, doc_uri, page):
    """AXIOM derive -> SHACL-oracle dispose -> assert, for a ruled header stack.

    The declarative sibling of rowrole.resolve_header_row_roles (which proposes NEURALLY where
    there is no ruled evidence). Returns the asserted body-token count on success — with the
    region written into `graph` — or None, leaving `graph` untouched, so the caller falls through
    to its unchanged pre-loop-L path.

    Abstains (None) without touching `graph` when:
      * the roles cannot be derived (preconditions P1-P3 above);
      * the derived vector says every row is a `level` — that IS the pre-loop-L reading, so there
        is nothing to re-read and the caller's own path handles it verbatim;
      * build_row_reading refuses the rewrite (an unplaceable continuation fragment);
      * the resulting region does not tile or loses header content (the SHACL oracle refuses).

    No PromotionDecision is emitted: this reading is DERIVED from marks in the document, not
    proposed (CLAUDE.md §3 — promotion governs propositions, not assertions). The conservation
    evidence loop C introduced is still emitted, so the oracle checks that no header text is lost.
    """
    from dataclasses import replace as _replace
    from .headers import header_rows_of
    from .holon import assert_hier_region
    from .rowrole import build_row_reading, emit_reading_evidence
    from .tiling import region_tiles

    header_rows = header_rows_of(band, hreg.grid, hreg.body_line)
    roles = derive_row_roles(band, header_rows, hreg.grid)
    if roles is None or all(r == "level" for r in roles):
        return None

    built = build_row_reading(header_rows, hreg.grid, roles)
    if built is None:
        return None
    nodes, captions, source_cells = built

    scratch = Graph()
    n = assert_hier_region(scratch, _replace(hreg, tree=nodes), band, table_uri, doc_uri, page)
    emit_reading_evidence(scratch, table_uri, captions, source_cells)
    if n <= 0 or not region_tiles(scratch):
        return None                                        # the oracle refuses -> abstain
    graph += scratch
    return n
