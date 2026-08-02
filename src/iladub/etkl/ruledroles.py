"""ruledroles — the header-stack law under RULED evidence (loop L, 2026-08-02).

§8 CLASSIFICATION
  * THE DECISION (which header row is the leaf, and what each row above it is) is an **AXIOM**:
    a declarative, open-world derivation over presence facts about the author's own ruled column
    grid — `vocab/queries/header-row-role.rq`. The band is the closure boundary.
  * THE CARRIAGE (loop M, the `Carried*` section at the foot of this file) is licensed
    **PROCEDURAL** plumbing, and the licence is worth stating exactly because it is the whole
    justification for moving a reading between pages without re-deriving it:
      - the reading being carried was DERIVED declaratively on page N-1, by the AXIOM above (or
        carried onto N-1 from N-2 under this same licence) and then DISPOSED by the SHACL tiling
        oracle — carriage never invents a role, it only re-uses a confirmed one;
      - carrying it onto page N is licensed by loop M's RECOGNITION AXIOM
        (`vocab/queries/continuation-of.rq`, run by document.py): page N's block was already
        derived to be the SAME header block, column for column, at agreeing ink origins, over the
        author's agreeing drawn grid;
      - and carriage is then applied only to rows that are TEXT-IDENTICAL per column to the prior
        page's rows (`carried_roles_for`). A row with no exact counterpart is REFUSED, not guessed.
    What is left here is copying, matching by string equality, and emitting. The result still
    passes the same SHACL oracle before it is admitted, so a carried reading that does not tile is
    refused exactly like a derived one.
    HONEST QUALIFICATION (review finding F2 — the first cut of this bullet claimed "no decision
    lives here", and that claim was too strong): *which* carried row a page-N row repeats IS a
    decision, and `carried_roles_for` answers it with a greedy in-order scan written in Python
    control flow — a declarative law (in-order counterpart, exact per-column identity, leaf-is-the-
    leaf, inert-skip-only) implemented procedurally, when its AXIOM twin already exists in this
    loop in `continuation-of.rq`'s clause shape. Registered as **residue R34** with its named
    disposition: a `repeats-row.rq` derivation over the same presence/equality evidence. What IS
    true unconditionally is the rest: no ROLE is ever invented here, and no tuned constant exists
    on this path.
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
  * THE UNDERDETERMINED RESIDUAL, and the reason this slice is scoped the way it is: WITHOUT an
    author header-block rule, a short merged parent and a wrap fragment are not separable by ruled
    geometry. Measured (re-review round 2): a parent 'Arr' left-aligned at its column's leaf-label
    x0 shares that origin BY CONSTRUCTION — every cell in a left-aligned column starts at the same
    coordinate — so no alignment predicate can tell them apart, and reading the label TEXT is
    forbidden here (R4). Loop L therefore does not attempt it. Correction (round-2 re-review): the
    residual does NOT sit outside clause 0's engagement context — it FIRES INSIDE an engaged header
    block, for rows below the block rule, and is measured there ('Arr Tonnes' asserted at 0.9195
    where BASE escalated). Engagement narrows WHERE the law fires at all; once engaged, it does
    not by itself separate a merged parent from a wrap fragment, and the pre-loop-L reading is
    kept for that row. NAMED FUTURE DISPOSITION: §8 sends this
    to NEURAL — a proposer reading the joined text ("does 'Arr Tonnes' read as one column name?"),
    disposed by the tiling oracle, exactly as loop C's rowrole slice already does for the
    borderless case. It is a reading judgment, not a geometry gap.
  * CENTRE-ALIGNED wrapped headers inside an engaged header block are not recovered: their lines
    share neither edge, so `_shares_origin` refuses, the row derives `level`, and the derivation
    abstains. An honest miss, never a wrong assertion.
  * Loop G's header-confirmed refinement can fabricate a column boundary inside a spanning label
    that contains a space (a pre-existing defect). Loop L does not worsen the reading, but the
    fabricated column changes the grid this law is evaluated against, so loop L AMPLIFIES its
    consequences: clause 1 may pass on a grid the author never drew. Closing it means making
    banner/spanner ink ineligible to confirm a boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .geometry import COORD_EPS

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
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

    WHAT THIS DOES AND DOES NOT ESTABLISH (re-review finding N1 — the round-1 docstring overstated
    it, and the overstatement was the defect). A shared origin EXCLUDES centre-aligned spanners:
    a merged label centred over a column group shares no edge with any leaf label, so it cannot be
    read as a continuation. It does NOT, on its own, distinguish a wrap fragment from a merged
    parent in the common LEFT-ALIGNED regime — there, every cell in a column starts at the same x
    BY CONSTRUCTION, so a short parent left-aligned in its cell shares the leaf label's x0 exactly.
    Measured: a parent 'Arr' drawn at the leaf's own x0 derives `continuation` on this predicate
    alone and welds a correct two-level header into a flat one. The specimen measurement quoted in
    round 1 (fragments matching their leaf label's x0 to the bit) is real but proves only that
    wrap fragments DO share the origin — not that parents do not.

    What carries the discrimination is therefore the STRUCTURAL engagement clause (clause 0 of
    header-row-role.rq): the derivation runs only inside an author-delimited header block, with
    furniture above the block rule and continuations below it. This predicate is the secondary
    filter that removes centre-aligned spanners from the rows the structure admits.

    COORD_EPS is the float-comparison epsilon on an EQUALITY, not a proximity window: nothing
    "close enough" passes, only ink laid out from the same coordinate.
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
        row_top = min(c.top for c in row)
        for hu, h in block_rules:
            if row_bottom <= h.y + COORD_EPS:          # the row's ink lies wholly above the rule
                g.add((ru, TAB.rowAboveHeaderBlockRule, hu))
            elif row_top >= h.y - COORD_EPS:           # ...wholly below it (and above the leaf)
                g.add((ru, TAB.rowBelowHeaderBlockRule, hu))
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


# ------------------------------------------------- the carried header reading (loop M, task 3)
#
# PROCEDURAL, and licensed as such — see the CARRIAGE bullet of the module docstring. Everything
# below copies, compares strings, or emits; nothing here decides anything.


@dataclass(frozen=True)
class CarriedHeaderRow:
    """One row of a CONFIRMED header block, in the form that can be carried to the next page.

    signature   the row's cells as `(ruled column index, EXACT surface text)`, left to right —
                the only thing matched across a page break. Text is compared by identity: two
                renderings of one string, never read for meaning (the continuation-of.rq idiom).
    role        the role that row was confirmed with ("furniture" / "continuation"), or None for
                the LEAF row (the leaf is never given a role — it is the leaf).
    source      the ORIGINATING page's `tab:HeaderSourceCell` URIs for this row. Pinned: when a
                carried reading is re-exported onto the NEXT page (page 0 -> 1 -> 2), the source
                stays page 0's, so every `tab:RepeatedHeader` on every continuation page traces to
                the head table's own header row, not to the page before it.
    origin_page the page those source cells were measured on (provenance, never matched on).
    """
    signature: tuple[tuple[int, str], ...]
    role: str | None
    source: tuple[URIRef, ...]
    origin_page: int


@dataclass(frozen=True)
class CarriedHeaderReading:
    """A whole confirmed header block, top to bottom; the last row is the leaf."""
    rows: tuple[CarriedHeaderRow, ...]


def _row_signature(row, grid) -> tuple[tuple[int, str], ...]:
    """`(column index, exact text)` per cell — the cross-page matching key.

    The column index is `regions.column_of` over the row's own page's leaf grid, i.e. the same
    notion the recognition AXIOM's `tab:leafColumnIndex` carries, so "identical per column" means
    the same thing on both sides of the break.
    """
    from .regions import column_of
    b = grid.boundaries
    return tuple((column_of((c.x0 + c.x1) / 2.0, b), c.text) for c in row)


def header_reading_of(header_rows, grid, roles, table_uri, page, inherited=None):
    """The `CarriedHeaderReading` for a header block whose reading has just been CONFIRMED.

    `roles` is the confirmed role vector over the NON-leaf rows; the leaf row is appended with
    role None. Source URIs are the `-hsc{k}` nodes rowrole.emit_reading_evidence writes for this
    very block (same flat enumeration over `header_rows`, so the indices agree by construction —
    they are computed here, never guessed).

    `inherited` is the reading this block was CARRIED from, when it was: its rows' `source` and
    `origin_page` are passed through unchanged (see CarriedHeaderRow.source), and only the rows
    this page actually carries are re-exported — a furniture row that has no counterpart here
    simply does not exist downstream.
    """
    if inherited is not None:
        return CarriedHeaderReading(tuple(inherited))
    out, k = [], 0
    for r, row in enumerate(header_rows):
        src = tuple(URIRef(f"{table_uri}-hsc{k + j}") for j in range(len(row)))
        k += len(row)
        role = None if r == len(header_rows) - 1 else roles[r]
        out.append(CarriedHeaderRow(_row_signature(row, grid), role, src, page))
    return CarriedHeaderReading(tuple(out))


def carried_roles_for(reading: CarriedHeaderReading, header_rows, grid):
    """Match THIS page's header rows against a carried block; return `(roles, matched)` or None.

    The rule, and its refusals (brief: never guess):
      * every one of this page's header rows must have an EXACTLY text-identical counterpart in
        the carried block, per column, and the counterparts must appear in the SAME ORDER — the
        block was redrawn, not rearranged;
      * this page's LAST header row must be the carried block's LAST row: the leaf is the leaf.
        Without this a continuation page could take a non-leaf row's reading for its leaf;
      * a carried row with NO counterpart here may be skipped ONLY if its confirmed role is
        `furniture` — that is the print-timestamp the head page carries and the continuation pages
        do not (measured on the specimen: page 0 has 4 header rows, pages 1-2 have the same 3
        minus the timestamp, whose source cells are hsc0/hsc1). The role condition is load-bearing
        and was NOT in the first cut of this function (review finding F1): skipping a `furniture`
        row is INERT — the row contributed no level and no text to any label, so its absence
        changes nothing about the reading. Skipping a `continuation` row is not: that row's text
        was PREFIXED onto a leaf label, so dropping it silently changes what the column is called
        ('Total Grain Tonnes' on page N-1 against 'Grain Tonnes' on page N — reproduced offline by
        the reviewer), and the two chained tables then carry different labels for the same column.
        No oracle catches that: each page tiles and conserves its own text perfectly. So a page
        that redraws the leaf but omits a WRAP row is refused, and compiles on its own path
        (which, standalone, escalates) rather than being stitched under a mutated label;
      * a carried block containing two rows with the SAME signature is refused outright: which of
        them a page-N row repeats is then genuinely undecidable by text identity, and the two may
        carry different roles. Refusing costs nothing real (no measured block has one) and is the
        alternative to picking the first one — i.e. to guessing;
      * anything else — a row that matches nothing, a non-leaf row that matches the carried leaf —
        returns None, and the caller keeps its own (un-carried) path.

    `matched` is `((this page's row index, the carried row), ...)` for EVERY row of this page,
    leaf included: it is what `emit_repeated_headers` records, so the leaf row is carried as a
    repeated header too (it is the most repeated row of all).

    The 1:1 rule-alignment notion loop L's clause 1 demands is inherited rather than re-derived:
    the carried leaf was confirmed 1:1 against ITS page's ruled columns, and this page's leaf is
    identical to it column-for-column — which is exactly what the recognition AXIOM established
    over the two pages' agreeing author-drawn grids.
    """
    if not header_rows or not reading.rows:
        return None
    carried_sigs = [r.signature for r in reading.rows]
    if len(set(carried_sigs)) != len(carried_sigs):
        return None                           # ambiguous counterpart -> refuse, never guess
    sigs = [_row_signature(row, grid) for row in header_rows]
    roles, matched, i = [], [], 0
    for k, sig in enumerate(sigs):
        while i < len(reading.rows) and reading.rows[i].signature != sig:
            if reading.rows[i].role != "furniture":
                return None                   # F1: only an INERT skip is admissible (see above)
            i += 1
        if i >= len(reading.rows):
            return None                       # a row with no counterpart -> refuse, never guess
        crow = reading.rows[i]
        i += 1
        matched.append((k, crow))
        if k < len(sigs) - 1:
            if crow.role is None:
                return None                   # a non-leaf row matched the carried LEAF -> refuse
            roles.append(crow.role)
    if matched[-1][1] is not reading.rows[-1]:
        return None                           # this page's last row is not the carried leaf
    return tuple(roles), tuple(matched)


def emit_repeated_headers(g, table_uri, header_rows, matched, page):
    """Record the repeated header block as FACTS: one `tab:RepeatedHeader` per repeated row.

    Each node carries the row's surface text, the page it was measured on and its bounding box
    (the union of the row's cells — provenance-to-the-page, CLAUDE.md §6), and
    `prov:wasDerivedFrom` every `tab:HeaderSourceCell` of the ORIGINATING page's row it repeats.
    PROV allows a derivation from several entities, and the originating row IS several nodes in
    this graph — the head table records its header block cell by cell (rowrole.emit_reading_
    evidence), so pointing at the row means pointing at its cells.

    These rows are NEVER `tab:EntryCell`s: the carried reading reads them as header rows
    (continuation fragments folded into the leaf labels, furniture carried as captions), so they
    never reach the body. This class is the positive record of that — the repeated block is a
    rendering accommodation, carried as a fact, never mistaken for data.

    `tab:cellText` is emitted deliberately, not incidentally: `tab:onPage` and `tab:hasBBox` are
    domain-`tab:Cell` properties, so under the compile's `inference="rdfs"` validation this node
    IS a `tab:Cell`, and `tab:WrappedCellShape` then requires it to carry its surface text (the
    drop-continuation guard). It does carry it — the whole row's text, joined in reading order.
    """
    for k, crow in matched:
        row = header_rows[k]
        u = URIRef(f"{table_uri}-rephdr{k}")
        g.add((u, RDF.type, TAB.RepeatedHeader))
        g.add((table_uri, TAB.hasRepeatedHeader, u))
        g.add((u, TAB.cellText, Literal(" ".join(c.text for c in row))))
        g.add((u, TAB.onPage, Literal(int(page), datatype=XSD.integer)))
        bb = BNode()
        g.add((bb, RDF.type, TAB.BBox))
        g.add((bb, TAB.x0, Literal(round(min(c.x0 for c in row), 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y0, Literal(round(min(c.top for c in row), 2), datatype=XSD.decimal)))
        g.add((bb, TAB.x1, Literal(round(max(c.x1 for c in row), 2), datatype=XSD.decimal)))
        g.add((bb, TAB.y1, Literal(round(max(c.bottom for c in row), 2), datatype=XSD.decimal)))
        g.add((u, TAB.hasBBox, bb))
        for s in crow.source:
            g.add((u, PROV.wasDerivedFrom, s))


def resolve_ruled_header_rows(graph, hreg, band, table_uri, doc_uri, page, carried=None):
    """AXIOM derive (or loop-M CARRY) -> SHACL-oracle dispose -> assert, for a ruled header stack.

    The declarative sibling of rowrole.resolve_header_row_roles (which proposes NEURALLY where
    there is no ruled evidence). Returns `(asserted_body_token_count, CarriedHeaderReading)` on
    success — with the region written into `graph` — or None, leaving `graph` untouched, so the
    caller falls through to its unchanged pre-loop-L path. The returned reading is what the
    document driver carries onto the NEXT page if the recognition AXIOM licenses it.

    `carried` (loop M) is the previous page's confirmed reading, and it is passed ONLY when the
    continuation AXIOM licensed this page as a continuation of that one. When present it REPLACES
    the derivation for this band — the roles are matched over by exact per-column text identity
    (`carried_roles_for`), not re-derived — and the repeated header block is recorded as
    `tab:RepeatedHeader` facts. A page that is not a recognized continuation never receives one,
    so the un-carried behaviour is unreachable-by-construction for case 1. If the match refuses,
    this falls back to the derivation, exactly as if nothing had been carried.

    Abstains (None) without touching `graph` when:
      * the roles cannot be derived (preconditions P1-P3, or the clause-0 engagement context) and
        no carried reading matched;
      * ANY row derives `level`. Round 2 tightened this from "every row" to "any row": a partly
        evidenced reading was asserting the UNEVIDENCED rows too, which is how a rule-chopped
        banner ended up asserted as a level-0 parent under strings the author never wrote (N3).
        The law now speaks only when it can account for the whole header stack. (A CARRIED vector
        cannot contain `level`: the reading it came from was confirmed under this same rule.)
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
    matched = None
    if carried is not None:
        match = carried_roles_for(carried, header_rows, hreg.grid)
        if match is not None:
            roles, matched = match
    if matched is None:
        roles = derive_row_roles(band, header_rows, hreg.grid)
    if roles is None or any(r == "level" for r in roles):
        return None

    built = build_row_reading(header_rows, hreg.grid, roles)
    if built is None:
        return None
    nodes, captions, source_cells = built

    scratch = Graph()
    n = assert_hier_region(scratch, _replace(hreg, tree=nodes), band, table_uri, doc_uri, page)
    emit_reading_evidence(scratch, table_uri, captions, source_cells)
    if matched is not None:
        emit_repeated_headers(scratch, table_uri, header_rows, matched, page)
    if n <= 0 or not region_tiles(scratch):
        return None                                        # the oracle refuses -> abstain
    graph += scratch
    inherited = [crow for _, crow in matched] if matched is not None else None
    return n, header_reading_of(header_rows, hreg.grid, roles, table_uri, page, inherited)
