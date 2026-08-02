"""document — the whole-document driver: per-page compile + continuation recognition (loop M).

§8 CLASSIFICATION
  * THE DECISION ("is the table opening page N the CONTINUATION of the table closing page N-1?")
    is an **AXIOM**: a declarative, open-world derivation over presence/equality facts about the
    two pages' leaf header blocks — `vocab/queries/continuation-of.rq`. The page PAIR is the
    closure boundary.
  * This module is the **PROCEDURAL** layer only, in the shape ruledroles.py (loop L) established:
    raw extraction (page count, and the bands, via compile.page_bands — the shared seam, not a
    copy), an evidence emitter that applies the float equalities with `geometry.COORD_EPS` AT
    EMISSION so the query carries no numeric literal, invoking rdflib, and the driver wiring that
    compiles each page under a PAGE-SCOPED document URI and merges the graphs. No decision logic
    lives here, and no tuned constant: COORD_EPS is the repo's float-comparison epsilon, reused
    unchanged.

WHY THIS EXISTS (spec 2026-08-02 §3b; residue R29)
  Pagination is an ACCOMMODATION: one logical table, cut to fit the page, with its header block
  redrawn on each continuation page so a reader can read any page standalone. Compiling page by
  page inherits the cut — the continuation pages arrive as headers-without-a-table (measured on
  the specimen: pages 1-2 escalate REGION_TILING_FAILED, R29) and the document's records are
  fragmented. Recognizing the cut is the first move of un-doing it.

THE LAW (stated in full in continuation-of.rq, with the measurement behind clause (d))
  Page N continues page N-1 iff both pages present a leaf header row, every column matches
  column-for-column by EXACT text at an agreeing ink origin in BOTH directions, and the two
  pages' AUTHOR-DRAWN leaf-grid boundaries agree as SETS under COORD_EPS. Nothing is read for
  meaning: two renderings of one string are compared for identity, which is evidence comparison,
  not text reading.

  ITS KNOWN FALSE-POSITIVE CLASS (residue R33; measured, not theorised): two INDEPENDENT tables
  built from one TEMPLATE — same header, same grid, different data — satisfy every clause, and
  the law stitches them. That is the taxonomy case-2 / case-3 boundary, and this law does not
  decide it. Recognition therefore means "the header block repeats and the grid matches", which
  is necessary but NOT sufficient for "these are one table"; anything that acts on recognition
  (task 3's carriage, task 4's chain-walk) inherits the exposure. The closing discriminator is
  the BODY side, not text reading — see continuation-of.rq's header.

WHAT THIS TASK DOES AND DOES NOT DO (loop M task 2 — state the mid-loop state honestly)
  Recognition only. A recognized continuation page is compiled exactly as before, so on the
  specimen it still ESCALATES: the header-block rule clause-0 needs exists only on page 0 (R29),
  and CARRYING page 0's confirmed reading into page N is task 3's work. Consequently:
    * `DocumentReport.recognized` records every page pair the AXIOM licensed — the honest record
      of what the law saw, independent of what the compile then managed;
    * `DocumentReport.chains` links tables that were RECOGNIZED **and** ASSERTED. A chain is a
      tuple of table URIs, so a page that asserted no table cannot appear in one; mid-loop the
      specimen therefore yields three singleton chains while `recognized` already holds
      ((0,1), (1,2)). `tab:continuesTable` is asserted on exactly the same condition.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .compile import CompilationReport, compile_tables, page_bands, _DOC
from .geometry import COORD_EPS
from .holon import TAB

_EV = Namespace("urn:iladub:continuation:")   # transient per-pair instance namespace

# three dirs up from src/iladub/etkl/document.py -> repo root, then vocab/queries/
CONTINUATION_OF_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "continuation-of.rq"


@dataclass(frozen=True)
class DocumentReport:
    """One document: the merged graph, the per-page reports, the continuation chains.

    `score` is asserted/(asserted+escalated) over the WHOLE document (never a mean of per-page
    scores — pages differ in size). `recognized` holds the (prev_page, page) pairs the
    continuation AXIOM licensed; `chains` holds the table URIs actually linked (see the module
    docstring for why the two can differ mid-loop).
    """
    score: float
    pages: tuple[CompilationReport, ...]
    chains: tuple[tuple[URIRef, ...], ...]
    graph: Graph
    recognized: tuple[tuple[int, int], ...] = ()

    def to_turtle(self) -> str:
        return self.graph.serialize(format="turtle")


# ----------------------------------------------------------------- raw extraction (PROCEDURAL)

def page_count(pdf_path: str) -> int:
    """The document's page count. Irreducibly procedural: reading the PDF's page tree."""
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        return len(pdf.pages)


def page_doc_uri(page_number: int, doc_uri: URIRef | None = None) -> URIRef:
    """The page-scoped document URI every URI minted for that page hangs off.

    Two pages of one document otherwise mint the same `doc#table0`, and merging their graphs
    silently welds two different tables into one (measured on the specimen before this change).
    """
    return URIRef(f"{doc_uri or _DOC}/p{page_number}")


# --------------------------------------------------------------- the leaf block of a page band

def _author_boundaries(band, grid) -> tuple[float, ...]:
    """Those leaf-grid boundaries the AUTHOR actually DREW (a vertical rule sits on them).

    The exclusions are MEASURED, not assumed — see continuation-of.rq's header for the numbers.
    Loop G's header-CONFIRMED boundaries are inferred from ONE page's ink, so they say nothing
    about whether two pages share the AUTHOR's grid. Measured on the specimen, TWO boundaries drop
    from the full leaf grid, and they behave differently: the gutter before the last column MOVES
    (798.54 / 802.04 / 792.04 across the three pages), while 751.54 happens to be identical on all
    three. Both are excluded, and for the same reason — an inferred boundary that agrees agrees by
    coincidence of this document's ink, which is not evidence about the author's grid. (The
    restriction also makes the clause immune to R32: a boundary loop G FABRICATED inside spanning
    ink carries no rule, so it can never enter the comparison.)

    COORD_EPS is the float-comparison epsilon on an EQUALITY (both sides derive from the same
    rule list, via `round(r.x, 2)` in the grid recovery), never a proximity window.
    """
    rule_xs = [round(float(r.x), 2) for r in band.rules]
    return tuple(float(x) for x in grid.boundaries
                 if any(abs(float(x) - rx) <= COORD_EPS for rx in rule_xs))


def leaf_block(band):
    """`(leaf_cells, author_boundaries)` for the band's repeated-header evidence, or None.

    `leaf_cells` is one `(column_index, exact_text, ink_origin_x)` per cell of the band's LEAF
    header row — the deepest header line above the body, loop L's notion, reached through the
    same `recover_leaf_grid` / `header_body_split` / `header_rows_of` path the compile uses.

    Returns None (the band evidences nothing, so it neither continues nor is continued) when the
    band carries no vertical rule, has no recoverable multi-column leaf grid, or has no
    header/body split. Refusal is not a verdict.
    """
    from .cells import recover_leaf_grid
    from .headers import header_body_split, header_rows_of
    from .regions import column_of

    if not band.rules:
        return None
    try:
        grid = recover_leaf_grid(band)
    except ValueError:
        return None                                     # "band has no words" — nothing to compare
    if grid.ncols < 2:
        return None
    split = header_body_split(band, grid)
    if split is None or not (1 <= split < len(band.lines)):
        return None                                     # no header region -> no repeated header
    rows = header_rows_of(band, grid, split)
    if not rows:
        return None
    cells = tuple((column_of((c.x0 + c.x1) / 2.0, grid.boundaries), c.text, float(c.x0))
                  for c in rows[-1])
    return cells, _author_boundaries(band, grid)


# ------------------------------------------------------------- evidence graph + query run (AXIOM)

def continuation_evidence_from_facts(prior_cells, continuation_cells,
                                     prior_boundaries=(), continuation_boundaries=()) -> Graph:
    """Fresh Graph() for ONE page pair — the inputs to continuation-of.rq.

    The single evidence shape, reached two ways: `continuation_evidence` derives the facts from
    two compiled bands, tests hand them in directly. Cells are `(column_index, text, origin_x)`;
    boundaries are the author-drawn leaf-grid x's of each page.

    Every float comparison happens HERE, with COORD_EPS, and surfaces as a presence link
    (`tab:originAgreesWith` / `tab:boundaryAgreesWith`) — which is why the query carries no
    numeric literal at all (the ruledroles idiom, loop L).

    NOTE the two uses of the coordinates are deliberately different: the `tab:leafOriginX` /
    `tab:ruledBoundaryX` literals are ROUNDED (2 dp) because they exist only to make the evidence
    graph readable as an audit trail, while every AGREEMENT link is computed on the UNROUNDED
    floats — so no comparison ever inherits a rounding artefact.
    """
    g = Graph()
    prior, cur = URIRef(f"{_EV}prior"), URIRef(f"{_EV}continuation")
    g.add((prior, RDF.type, TAB.PriorPageBlock))
    g.add((cur, RDF.type, TAB.ContinuationPageBlock))

    def _cells(block, side, facts):
        out = []
        for i, (col, text, x) in enumerate(facts):
            u = URIRef(f"{_EV}{side}-c{i}")
            g.add((u, RDF.type, TAB.PageLeafCell))
            g.add((block, TAB.hasLeafCell, u))
            g.add((u, TAB.leafColumnIndex, Literal(int(col), datatype=XSD.integer)))
            g.add((u, TAB.leafCellText, Literal(text)))
            g.add((u, TAB.leafOriginX, Literal(round(float(x), 2), datatype=XSD.double)))
            out.append((u, float(x)))
        return out

    def _bounds(block, side, xs):
        out = []
        for i, x in enumerate(xs):
            u = URIRef(f"{_EV}{side}-b{i}")
            g.add((u, RDF.type, TAB.AuthorRuledBoundary))
            g.add((block, TAB.hasAuthorBoundary, u))
            g.add((u, TAB.ruledBoundaryX, Literal(round(float(x), 2), datatype=XSD.double)))
            out.append((u, float(x)))
        return out

    pcells = _cells(prior, "prior", prior_cells)
    ccells = _cells(cur, "continuation", continuation_cells)
    for pu, px in pcells:
        for cu, cx in ccells:
            if abs(px - cx) <= COORD_EPS:
                g.add((pu, TAB.originAgreesWith, cu))

    pb = _bounds(prior, "prior", prior_boundaries)
    cb = _bounds(cur, "continuation", continuation_boundaries)
    for pu, px in pb:
        for cu, cx in cb:
            if abs(px - cx) <= COORD_EPS:
                g.add((pu, TAB.boundaryAgreesWith, cu))
    return g


def continuation_evidence(prev_band, prev_grid, cur_band, cur_grid) -> Graph:
    """The evidence graph for two BANDS (the production entry point).

    `prev_grid` / `cur_grid` are the bands' `LeafGrid`s — the plan named them `*_grid_xs`, but the
    leaf ROW cannot be located from boundaries alone (header_rows_of needs the grid), and the xs
    are `grid.boundaries`. An empty graph side means that band evidences no leaf block, which
    clause (a) refuses.
    """
    from .headers import header_body_split, header_rows_of
    from .regions import column_of

    def _facts(band, grid):
        split = header_body_split(band, grid)
        if split is None or not (1 <= split < len(band.lines)):
            return (), ()
        rows = header_rows_of(band, grid, split)
        if not rows:
            return (), ()
        cells = tuple((column_of((c.x0 + c.x1) / 2.0, grid.boundaries), c.text, float(c.x0))
                      for c in rows[-1])
        return cells, _author_boundaries(band, grid)

    p_cells, p_bounds = _facts(prev_band, prev_grid)
    c_cells, c_bounds = _facts(cur_band, cur_grid)
    return continuation_evidence_from_facts(p_cells, c_cells, p_bounds, c_bounds)


def is_continuation(evidence: Graph) -> bool:
    """Run continuation-of.rq over one pair's evidence: did the law license the continuation?

    A row means the derivation held for the pair; no row is the law's own refusal (any clause
    unmet), and refusal keeps the two pages independent — the case-1 behaviour.
    """
    q = Path(CONTINUATION_OF_RQ).read_text(encoding="utf-8")
    return any(True for _ in evidence.query(q))


# ------------------------------------------------------------------------------- the driver

def _recognition_blocks(bands):
    """{band_index: (leaf_cells, author_boundaries)} for every band evidencing a leaf block."""
    out = {}
    for i, band in enumerate(bands):
        blk = leaf_block(band)
        if blk is not None:
            out[i] = blk
    return out


def compile_document(pdf_path: str, validate_shapes: bool = True,
                     span_proposer=None, row_role_proposer=None) -> DocumentReport:
    """Compile a whole document: every page under its own page-scoped document URI, merged into
    one graph, with continuation chains recognized across the page breaks.

    The pairing is STRUCTURAL, not a heuristic: pagination cuts a table at a page break, so the
    only candidates are the table that CLOSES page N-1 (its last band evidencing a leaf block)
    and the one that OPENS page N (its first). The law then decides; a page that evidences
    nothing, or whose evidence does not match, stays independent.

    COVERAGE LIMIT of that pairing, stated plainly: EXACTLY ONE candidate pair is tested per page
    break. A page carrying several tables, of which a middle one is the continued one, is not
    reached; two tables continuing across the same break are not reached either. The bias is
    toward REFUSAL (an unexamined pair stays independent), never toward a wrong stitch.

    FALSE-POSITIVE CLASS (residue R33 — read before consuming `chains`): recognition means "the
    header block repeats and the author's grid matches", which two INDEPENDENT tables built from
    one template satisfy exactly (measured). It is necessary, not sufficient, for "one table" —
    the case-2 / case-3 boundary. See continuation-of.rq's header for the measurement and for the
    body-side discriminator that would close it.
    """
    n_pages = page_count(pdf_path)
    pages: list[CompilationReport] = []
    blocks: list[dict] = []
    graph = Graph()

    for p in range(n_pages):
        # The driver reads the SAME bands the compile reads (compile.page_bands is the shared
        # seam), so band index i in `blocks[p]` is region report i in `pages[p]`.
        blocks.append(_recognition_blocks(page_bands(pdf_path, p)))
        pages.append(compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes,
                                    span_proposer=span_proposer,
                                    row_role_proposer=row_role_proposer,
                                    doc_uri=page_doc_uri(p)))
        graph += pages[-1].graph

    recognized: list[tuple[int, int]] = []
    links: dict[URIRef, URIRef] = {}          # continuation table -> the table it continues
    for p in range(1, n_pages):
        prev_blocks, cur_blocks = blocks[p - 1], blocks[p]
        if not prev_blocks or not cur_blocks:
            continue
        prev_idx = max(prev_blocks)           # the table that CLOSES the previous page
        cur_idx = min(cur_blocks)             # the table that OPENS this one
        prev_cells, prev_bounds = prev_blocks[prev_idx]
        cur_cells, cur_bounds = cur_blocks[cur_idx]
        if not is_continuation(continuation_evidence_from_facts(
                prev_cells, cur_cells, prev_bounds, cur_bounds)):
            continue
        recognized.append((p - 1, p))
        prev_uri = pages[p - 1].regions[prev_idx].table_uri
        cur_uri = pages[p].regions[cur_idx].table_uri
        if prev_uri is None or cur_uri is None:
            continue                          # recognized, but one side asserted no table (R29)
        graph.add((cur_uri, TAB.continuesTable, prev_uri))
        links[cur_uri] = prev_uri

    ordered = [r.table_uri for rep in pages for r in rep.regions if r.table_uri is not None]
    successor = {prev: cur for cur, prev in links.items()}
    chains = []
    for head in ordered:
        if head in links:
            continue                          # not a head: it continues an earlier table
        chain = [head]
        while chain[-1] in successor:
            chain.append(successor[chain[-1]])
        chains.append(tuple(chain))

    asserted = sum(rep.asserted for rep in pages)
    escalated = sum(rep.escalated for rep in pages)
    denom = asserted + escalated
    score = 1.0 if denom == 0 else asserted / denom
    return DocumentReport(score, tuple(pages), tuple(chains), graph, tuple(recognized))
