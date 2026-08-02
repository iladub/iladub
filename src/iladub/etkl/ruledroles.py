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
    P1  the band is ruled and the region's leaf grid is that band's ruled boundary SET
        (`grid_is_the_ruled_grid` — read its docstring for what that set does and does not
        guarantee: it includes loop-G header-confirmed boundaries, which are NOT author marks);
    P2  the header region has at least one non-leaf row to classify;
    P3  the LEAF header row aligns 1:1 with the ruled columns. P3 lives in the AXIOM (clause 1 of
        header-row-role.rq), not here; its refusal arrives as an empty result.
  Then per non-leaf row: furniture / continuation / level, per header-row-role.rq — where BOTH
  non-default roles demand positive evidence (an author header-block rule; a shared alignment
  origin) and `level` is the unchanged pre-loop-L default.

WHAT THE SHACL ORACLE DOES AND DOES NOT DO (review finding F3 — state this accurately)
  `region_tiles` refuses a reading that does not TILE or that LOSES header text. It CANNOT tell a
  right reading from a wrong one: tab:HeaderContentConservedShape is satisfied by a LabelCell OR a
  tab:RegionCaption, so demoting a real header label to a caption — or welding it onto a leaf
  label — conserves the text and passes. Correctness therefore rests entirely on the positive
  evidence each role requires. Do not describe the oracle as a correctness backstop.

KNOWN RESIDUES (honest, not silently absorbed; to be registered at loop close)
  * CENTRE-ALIGNED wrapped headers are not recovered: their lines share neither edge, so
    `_shares_origin` refuses and the row falls to `level` — today's behaviour, i.e. escalation.
    An honest miss, never a wrong assertion.
  * A label that is NOT a wrap fragment but happens to sit strictly inside one ruled column AND to
    share that column's leaf label's exact left or right edge would be welded onto it. This is the
    residual of loop C's Finding 3, now reduced from "any short label" to "a label laid out from
    the identical coordinate as the leaf label" — the signature of same-cell text.
  * Loop G's header-confirmed refinement can fabricate a column boundary inside a spanning label
    that contains a space (a pre-existing defect). Loop L does NOT worsen it in the reading — a
    spanning label's fragments do not share the leaf labels' origins, so they stay `level` — but
    the fabricated column does change the grid this law is evaluated against, so loop L AMPLIFIES
    its consequences: clause 1 may pass on a grid the author never drew. Registered as such.
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


def _shares_origin(a, b_) -> bool:
    """The two cells share an ALIGNMENT ORIGIN — the same left edge or the same right edge.

    Wrapped lines of one table cell are laid out from that cell's own origin: left-aligned text
    shares x0, right-aligned text shares x1. So a header fragment sharing its leaf label's origin
    is the renderer's own accommodation, read back (spec §2b) — positive evidence that the two are
    lines of ONE cell rather than two independent labels. Measured on the specimen: all eight wrap
    fragments match their leaf label's x0 to the bit, while the leaked date line's ink in the same
    column does not (398.28 vs 376.32).

    COORD_EPS is the float-comparison epsilon on an EQUALITY, not a proximity window: nothing
    "close enough" passes, only ink laid out from the same coordinate. Centre-aligned cells are
    deliberately NOT matched — their wrapped lines share no edge, so this law abstains on them
    (they fall to `level`, i.e. today's behaviour). Registered as a residue, not silently absorbed.
    """
    return abs(a.x0 - b_.x0) <= COORD_EPS or abs(a.x1 - b_.x1) <= COORD_EPS


def _header_block_rules(band, grid, header_rows):
    """The author's HEADER-BLOCK rules: horizontal rules drawn across every interior ruled boundary,
    lying strictly inside the header region (below the topmost header row's ink, above the leaf
    row's ink). Such a rule is the author writing "the header block starts below here".

    "Across every interior boundary" is a per-boundary presence test, NOT a width threshold — the
    specimen's block rule spans x 13.44..832.80 while the grid's outer boundaries are 12.48/832.08,
    so any "covers the full span" comparison would need a tolerance. Covering each interior
    boundary needs none, and it is what actually distinguishes a table-wide rule from the
    single-cell underlines the same document draws (x 13.44..56.16).
    """
    b = grid.boundaries
    interior = [b[i] for i in range(1, len(b) - 1)]
    if not interior:
        return []
    first_top = min(c.top for c in header_rows[0])
    leaf_top = min(c.top for c in header_rows[-1])
    out = []
    for h in getattr(band, "hrules", ()):
        if not (first_top < h.y < leaf_top):
            continue                                   # outside the header region
        if all(h.x0 - COORD_EPS <= x <= h.x1 + COORD_EPS for x in interior):
            out.append(h)
    return out


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
    """P1: every boundary of the region's leaf grid belongs to the band's ruled boundary SET.

    What this DOES guarantee: the grid was not produced by the whitespace fallback. Subset rather
    than equality, because `grid._rule_boundaries` legitimately drops marks bounding an interval no
    ink occupies (a double-drawn table border). Exact float comparison is correct — both sides are
    built from the same list.

    WHAT IT DOES NOT GUARANTEE (review finding F4 — the earlier docstring overstated this):
    `band.column_xs`, once loop G's header confirmation has populated it, already contains
    boundaries the author never DREW — interior gutters inferred from header ink. The specimen
    depends on two of them (751.54, 798.54), so "author-drawn rules only" is not an available
    precondition. A confirmed boundary can even be fabricated inside a spanning label that contains
    a space, and this predicate will accept the resulting grid. Containment against that case lives
    in the LAW, not here: a spanning label's fragments share no leaf label's alignment origin, so
    they derive `level` and the region keeps its pre-loop-L outcome.
    """
    xs = ruled_boundaries(band)
    if xs is None or grid.ncols < 2:
        return False
    return set(float(x) for x in grid.boundaries) <= set(xs)


# ------------------------------------------------------------------- evidence graph + query run

def role_evidence(band, header_rows, grid) -> Graph:
    """Fresh Graph() for one band's header region — the inputs to header-row-role.rq.

    Emits: one tab:RuledColumn per column; one tab:HeaderBlockRule per author header-block rule;
    one tab:LeafHeaderCell per cell of the LAST row (clause 1 reads these for the 1:1 check — the
    leaf row is never given a role); and, for every NON-LEAF row, a tab:HeaderRegionRow with its
    `rowAboveHeaderBlockRule` links and its cells' `withinRuledColumn` /
    `sharesAlignmentOriginWith` presence facts.
    """
    g = Graph()
    b = grid.boundaries
    cols = []
    for i in range(grid.ncols):
        col = URIRef(f"{_EV}col{i}")
        cols.append(col)
        g.add((col, RDF.type, TAB.RuledColumn))

    leaf_cells = []
    for j, cell in enumerate(header_rows[-1]):
        lu = URIRef(f"{_EV}leaf{j}")
        leaf_cells.append((lu, cell))
        g.add((lu, RDF.type, TAB.LeafHeaderCell))
        for i in range(grid.ncols):
            if _within(cell.x0, cell.x1, b, i):
                g.add((lu, TAB.withinRuledColumn, cols[i]))

    block_rules = []
    for k, h in enumerate(_header_block_rules(band, grid, header_rows)):
        hu = URIRef(f"{_EV}block{k}")
        block_rules.append((hu, h))
        g.add((hu, RDF.type, TAB.HeaderBlockRule))

    for r, row in enumerate(header_rows[:-1]):
        ru = URIRef(f"{_EV}row{r}")
        g.add((ru, RDF.type, TAB.HeaderRegionRow))
        g.add((ru, TAB.headerRowOrder, Literal(r, datatype=XSD.integer)))
        row_bottom = max(c.bottom for c in row)
        for hu, h in block_rules:
            if row_bottom <= h.y + COORD_EPS:          # the row's ink lies wholly above the rule
                g.add((ru, TAB.rowAboveHeaderBlockRule, hu))
        for j, cell in enumerate(row):
            cu = URIRef(f"{_EV}row{r}c{j}")
            g.add((cu, RDF.type, TAB.HeaderRegionCell))
            g.add((ru, TAB.hasHeaderRegionCell, cu))
            for i in range(grid.ncols):
                if _within(cell.x0, cell.x1, b, i):
                    g.add((cu, TAB.withinRuledColumn, cols[i]))
            for lu, lcell in leaf_cells:
                if _shares_origin(cell, lcell):
                    g.add((cu, TAB.sharesAlignmentOriginWith, lu))
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
    return run_roles(HEADER_ROW_ROLE_RQ, role_evidence(band, header_rows, grid),
                     len(header_rows) - 1)


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
