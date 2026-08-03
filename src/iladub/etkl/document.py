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

WHAT RECOGNITION THEN LICENSES (loop M task 3 — the carried header reading)
  Recognizing the cut is only the first move; task 3 un-does it. When the AXIOM licenses the pair
  (N-1, N), the driver hands page N-1's CONFIRMED header-block reading to page N's compile as a
  `carried_header_roles` entry for the recognized band, and ruledroles matches it onto page N's
  own header rows by EXACT per-column text identity. Measured on the specimen: page 0's block is
  four rows (a print-timestamp furniture row + two continuation rows + the leaf); pages 1-2 redraw
  the same block minus the timestamp, so three rows match, the furniture row simply has no
  counterpart, and the two continuation rows plus the leaf carry. Pages 1-2 went from escalating
  REGION_TILING_FAILED (R29) to asserting. Nothing is re-derived and nothing is guessed: the
  carriage is PROCEDURAL, licensed by the recognition AXIOM above and by the derivation that
  confirmed page N-1's reading — see ruledroles' module docstring for the licence in full. Each
  continuation page's redrawn header block is recorded as tab:RepeatedHeader rows traced back to
  the HEAD page's own header row, never read as data.

THE TWO RECORDS, AND WHY THEY STAY DISTINCT (they were equal on the specimen after task 3; that
  is a measurement, not an invariant)
    * `DocumentReport.recognized` records every page pair the AXIOM licensed — the honest record
      of what the LAW saw, independent of what the compile then managed. Recognition does not
      depend on either page compiling.
WHAT A CHAIN IS THEN FOR (loop N — the logical table is the closure holon; residue R35)
  A chain is the LOGICAL table the pagination cut. `reconcile_chain_arithmetic` re-runs the
  UNCHANGED loop-H subtotal arithmetic (`rows.detect_aggregation_rows`) over the chain's whole
  row sequence and reconciles the merged graph's aggregation typing to that result — the
  arithmetic is untouched, only the holon it closes over grows from the page to the logical
  table. See that function and `_UnitGrid` for the §8 classification, the cross-member column
  licence, and why refining a page-local intermediate here is honest rather than a rewrite.

    * `DocumentReport.chains` links tables that were RECOGNIZED **and** ASSERTED. A chain is a
      tuple of table URIs, so a page that asserted no table cannot appear in one — which is
      exactly the state task 2 measured (three singleton chains against `recognized` already
      holding ((0,1), (1,2))), and which any page whose carriage the SHACL oracle refuses will
      reproduce. `tab:continuesTable` is asserted on exactly the same condition as `chains`.
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
class ChainArithmetic:
    """What the document-level arithmetic pass did to ONE chain — the honest ledger (loop N).

    `page_confirmed` counts the rows of this chain's member tables that the PER-PAGE arithmetic
    had typed `tab:DetectedAggregationRow` before the pass ran; `document_confirmed` counts what
    the LOGICAL table's window confirms; `retracted` and `newly_confirmed` are the two
    differences. A row counted in both `page_confirmed` and `document_confirmed` may still have
    had its `tab:aggregates` operand set REWRITTEN (the wider window can find more members) —
    the pass always retracts before it asserts, so the edges in the graph are the document-level
    ones, never a mix.

    `groups_retracted` counts loop-I `tab:DerivedRowGroup` nodes withdrawn because the row that
    WITNESSED them was retracted — a derivation cannot outlive its ground (see
    `_retract_orphaned_groups`). It is reported separately from `retracted` because a retracted
    row need not have carried a group at all (loop I refuses one when the key is not unique).

    `abstained` is not None when the pass refused this chain outright and changed nothing: the
    graph did not admit an unambiguous logical row sequence (see `_logical_row_sequence`).
    Refusal is not a verdict — the page-local typing simply stands.
    """
    chain: tuple[URIRef, ...]
    page_confirmed: int = 0
    document_confirmed: int = 0
    retracted: int = 0
    newly_confirmed: int = 0
    abstained: str | None = None
    groups_retracted: int = 0


@dataclass(frozen=True)
class DocumentReport:
    """One document: the merged graph, the per-page reports, the continuation chains.

    `score` is asserted/(asserted+escalated) over the WHOLE document (never a mean of per-page
    scores — pages differ in size). `recognized` holds the (prev_page, page) pairs the
    continuation AXIOM licensed; `chains` holds the table URIs actually linked (see the module
    docstring for why the two can differ mid-loop). `arithmetic` holds one `ChainArithmetic` per
    MULTI-MEMBER chain the document-level subtotal pass ran on — empty for a single-page or
    unchained document, where the pass never runs at all.
    """
    score: float
    pages: tuple[CompilationReport, ...]
    chains: tuple[tuple[URIRef, ...], ...]
    graph: Graph
    recognized: tuple[tuple[int, int], ...] = ()
    arithmetic: tuple[ChainArithmetic, ...] = ()

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


# ------------------------------------- the document-level arithmetic pass (loop N, residue R35)
#
# §8 CLASSIFICATION — PROCEDURAL, and the justification is loop H's, VERBATIM and unchanged:
# `rows.detect_aggregation_rows` is DECIDABLE EXACT ARITHMETIC (exact Decimal sums over a finite
# ordered row sequence; a SPARQL formulation of nested running-sum windows would be obfuscation,
# not a lift). Not one line of that function changes here, and no new decision is taken: what
# changes is the HOLON it closes over. Loop H closed it over the page-local region because that
# was the only row sequence the compile had; a chain gives the LOGICAL table, and the logical
# table is the closure holon. Everything below is glue (sequence assembly, an index re-encoding,
# triple retraction/assertion) plus counting — it decides nothing, reads no label for meaning,
# and carries no numeric constant.


@dataclass(frozen=True)
class _SeqCell:
    """One populated cell of the logical sequence, re-encoded onto the unit grid (see below)."""
    x0: float
    x1: float
    text: str


@dataclass(frozen=True)
class _SeqRow:
    """One row of the logical sequence, in the shape `detect_aggregation_rows` reads (`.cells`)."""
    cells: tuple[_SeqCell, ...]


@dataclass(frozen=True)
class _UnitGrid:
    """A grid whose column i is the half-open interval [i, i+1) — the re-encoding target.

    THE CROSS-MEMBER COLUMN LICENCE, stated in full because it is the one thing this pass adds
    to loop H's arithmetic. `detect_aggregation_rows` takes ONE grid, and reads a candidate's
    NESTING LEVEL off its label's COLUMN INDEX. A chain's members are separate tables with
    separate geometry, so no single page's boundary list is the right instrument for all of
    them — a boundary that MOVES between pages (measured: the gutter before the last column at
    798.54 / 802.04 / 792.04 on the specimen) would re-map a cell that sits near it.

    So each row's columns are mapped by its OWN table's grid — which is exactly what the compile
    already did when it minted `{table}-e{r}_{col}` / `{table}-c{col}`, so the per-table mapping
    is READ back out of the graph rather than recomputed — and the resulting INDICES are then
    re-encoded onto this unit grid, on which `regions.column_of` returns the index it was given.
    The re-encoding is an identity by construction; the arithmetic sees the same `{column: text}`
    dicts it would have seen from the real cells.

    That indices from DIFFERENT member tables may be compared at all (level = label column index,
    so "column 17 here" must mean "column 17 there") is licensed by the continuation law that
    built the chain, not assumed — and by the pair of clauses that make the correspondence a
    BIJECTION, which is exactly what index comparison needs:
      * clauses (b)+(c) — column-for-column in BOTH directions: every column of page N-1's leaf
        row has a counterpart at the SAME column index on page N carrying the SAME text at an
        agreeing ink origin (b), and no column of page N's leaf row is left without such a
        counterpart (c). An extra or a missing column on either side refuses. So the two column
        sets are in 1:1 correspondence AT EQUAL INDEX — 17 = 17, not "17 maps to some 17-ish";
      * clause (d) — the two pages' AUTHOR-DRAWN leaf-grid boundary sets agree under COORD_EPS,
        so the same author's rules delimit those columns on both pages.
    It is the same licence loop M's carriage already rests on (the carried header signature is
    `(column index, exact text)` per cell, matched across the break).
    """
    boundaries: tuple[float, ...]


def _index_suffix(uri, table_uri, mark: str):
    """`{table_uri}-{mark}{n}` -> n, or None when the URI does not follow the minting convention.

    The convention is the compile's own, one call away (`holon.assert_hier_region` mints
    `-r{row}` / `-c{col}`, and `rowgroups.derive_row_groups` already constructs the same strings
    in the other direction). Reading it back is a parse of OUR OWN minting, never of a document.
    A URI that does not match makes the pass abstain rather than guess.
    """
    s, prefix = str(uri), f"{table_uri}-{mark}"
    if not s.startswith(prefix):
        return None
    tail = s[len(prefix):]
    return int(tail) if tail.isdigit() else None


def _logical_row_sequence(graph: Graph, chain):
    """`(rows, row_uris, note)` — the chain's LOGICAL row sequence, or `(None, None, reason)`.

    THE SEQUENCE: the member tables in CHAIN order, each member's body rows in ROW order, each
    row's cells mapped to columns by its OWN table's grid (as recorded in the graph) and
    re-encoded onto the unit grid (see `_UnitGrid` for the licence).

    Repeated-header rows cannot enter it, structurally: a continuation page's redrawn header
    block is recorded as `tab:RepeatedHeader` nodes (`{table}-rephdr{k}`, from
    `ruledroles.emit_repeated_headers`) which are NEVER `tab:LeafRow`s and never `tab:EntryCell`s
    — the header rows are consumed by the header reading and never reach the body. This function
    reads `tab:hasLeafRow` only, so the exclusion needs no filter, and the property was MEASURED
    on the specimen before this pass was written, not assumed: 6 `tab:RepeatedHeader` nodes over
    the two continuation pages, 195 `tab:LeafRow`s, zero nodes in both classes and zero repeated
    headers typed `tab:EntryCell`.

    ABSTAINS (returns a reason, changes nothing) when the graph does not admit ONE unambiguous
    reading: a row or column URI outside the minting convention, a row with no populated cell, or
    an entry cell carrying more than one `tab:cellText`. The last is the honest one — the compile
    welds two same-column cells of one row onto a single `-e{r}_{col}` node, and which of the two
    texts the arithmetic should read is then undecidable here. Refusing a chain leaves its
    page-local typing exactly as it was (§7: never guess to achieve coverage).
    """
    from rdflib import Literal as _Literal
    seq: list[tuple[URIRef, dict[int, str]]] = []
    for t in chain:
        rows: dict[int, URIRef] = {}
        for r in graph.objects(t, TAB.hasLeafRow):
            i = _index_suffix(r, t, "r")
            if i is None:
                return None, None, f"row URI outside the minting convention: {r}"
            rows[i] = r
        for i in sorted(rows):
            row = rows[i]
            cols: dict[int, str] = {}
            for e in graph.subjects(TAB.atRow, row):
                if (t, TAB.hasCell, e) not in graph:
                    continue
                c = graph.value(e, TAB.atColumn)
                col = None if c is None else _index_suffix(c, t, "c")
                if col is None:
                    return None, None, f"column URI outside the minting convention: {c}"
                texts = [o for o in graph.objects(e, TAB.cellText) if isinstance(o, _Literal)]
                if len(texts) != 1:
                    return None, None, f"{len(texts)} cellText literals on {e}"
                cols[col] = str(texts[0])
            if not cols:
                return None, None, f"leaf row with no populated cell: {row}"
            seq.append((row, cols))
    if not seq:
        return None, None, "no leaf rows in the chain"
    ncols = max(c for _, cols in seq for c in cols) + 1
    grid = _UnitGrid(tuple(float(i) for i in range(ncols + 1)))
    # 0.25/0.75 are NOT a tolerance and nothing is ever compared against them: they place the
    # cell strictly inside its own unit column, and ANY interior point yields the same index
    # from `regions.column_of` (`b[i] <= centre < b[i+1]`). The re-encoding is an identity.
    out = tuple(_SeqRow(tuple(_SeqCell(col + 0.25, col + 0.75, text)
                              for col, text in sorted(cols.items())))
                for _, cols in seq)
    return (out, grid), tuple(row for row, _ in seq), None


def _retract_orphaned_groups(graph: Graph, retracted_rows) -> int:
    """Retract every `tab:DerivedRowGroup` whose WITNESS the document window just de-typed.

    Loop I derives a row group FROM a confirmed `tab:DetectedAggregationRow` — the group node
    records that witness as `prov:wasDerivedFrom`, and takes its `tab:coversRow` members straight
    off the witness's `tab:aggregates` edges. So the group is not an independent fact: it is a
    DERIVATION, and when the wider window refuses its witness the derivation has no ground left.

    Leaving it standing is a §3/§7 violation, and a silent one — SHACL does not catch it
    (`tab:DerivedRowGroupShape` requires a `prov:wasDerivedFrom` to EXIST, not that its object
    still be an aggregation row), while `feed._read_table` keeps injecting the stale group's key
    into records whose arithmetic grounding has just been retracted. Constructed by the loop-N
    reviewer, not theorised: a page-1 subtotal that confirms page-locally (SUB = 250 over its two
    visible rows) and is REFUSED at document level (the walk-back reaches page 0's rows, 500 != 250)
    leaves `-rg{i}` behind, keying rows off a witness that no longer witnesses anything. Zero
    occurrences on the specimen — every stem retraction count is 0 — which is why it needs a
    constructed case and a pinned test, not a measurement.

    The witness going means the whole node goes: its types, its label edge, its members, its
    parent/level links, and any nesting edge pointing AT it. Task 3 re-derives groups over the
    document-level aggregations; this function only guarantees that retraction never leaves a
    derivation whose ground has been withdrawn. Returns the number of groups retracted.

    Stated because it is not recomputed here: a SURVIVING sibling's `tab:headerLevel` was derived
    as a depth walk that may have run through a node just removed, so it can be one level too
    deep until task 3 rebuilds the set. Nothing reads it in the interim — `RowNoOverlapShape`
    exempts every pair involving a derived group, and `feed._read_table` reads a group's label and
    members, never its level.
    """
    from .holon import PROV
    n = 0
    for row in retracted_rows:
        for grp in set(graph.subjects(PROV.wasDerivedFrom, row)):
            if (grp, RDF.type, TAB.DerivedRowGroup) not in graph:
                continue                     # some other derivation — not ours to withdraw
            graph.remove((grp, None, None))
            graph.remove((None, None, grp))  # hasHeaderNode, and any child's parentHeader
            n += 1
    return n


def reconcile_chain_arithmetic(graph: Graph, chain) -> ChainArithmetic:
    """Re-run the UNCHANGED loop-H arithmetic over one chain's logical table, and reconcile.

    RECONCILIATION, AND WHY IT IS HONEST. The per-page pass already typed some rows
    `tab:AggregationRow` / `tab:DetectedAggregationRow` with `tab:aggregationFunction` and
    `tab:aggregates` edges. Those typings are an INTERMEDIATE produced under a window we now
    know was too small — a page break cuts a group, so a page-local window can both MISS a
    subtotal whose members are on the previous page (the stem's page-2 rows: 22 candidates, 0
    confirmed) and, symmetrically, confirm one whose true operand set the wider window extends.
    This pass therefore retracts all four predicates over the chain's rows and re-asserts them
    from the document-level result, BEFORE the merged graph is consumed (the per-page SHACL
    membrane has already run inside `compile_tables`; whole-graph validation is loop N task 4).
    Refining your own intermediate is not falsification as long as it is COUNTED and stated:
    `ChainArithmetic` records page-confirmed, document-confirmed, retracted and newly-confirmed
    for exactly that reason, and the counts ride in the DocumentReport.

    `tab:aggregates` edges may now CROSS member tables — a page-2 subtotal pointing at page-1
    rows. That is the point: the operands are where the author put them, and the logical table is
    the closure holon.

    Only ever called for a chain of TWO OR MORE members (see `compile_document`), so a single-page
    document and an unchained page are untouched by construction, not by a guard that could rot.
    """
    from .rows import detect_aggregation_rows

    seq, row_uris, why = _logical_row_sequence(graph, chain)
    if seq is None:
        # the chain's page-local typing stands, unchanged, and the refusal is reported
        page_local = sum(1 for t in chain for r in graph.objects(t, TAB.hasLeafRow)
                         if (r, RDF.type, TAB.DetectedAggregationRow) in graph)
        return ChainArithmetic(tuple(chain), page_local, page_local, 0, 0, why)

    before = {r for r in row_uris if (r, RDF.type, TAB.DetectedAggregationRow) in graph}
    rows, grid = seq
    agg = detect_aggregation_rows(rows, grid)

    for r in row_uris:                       # retract, then assert — never a mix of two windows
        # ORDERING DEPENDENCY, recorded (review L-1): `tab:AggregationRow` has a SECOND producer,
        # `denormalization.annotate_aggregations`, which types rows BARE (no row-level operands —
        # see tab-shapes.ttl's DetectedAggregationRowShape comment). This unconditional remove
        # would strip such a typing without the ledger noticing, because the ledger counts the
        # DETECTED subclass only. It is unreachable today — `analyze`/denormalization is an opt-in
        # POST-pass over a compiled graph, never part of compile_document — and it must stay that
        # way: reconciliation runs first, annotation after, or this pass goes blind to what it
        # removed.
        graph.remove((r, RDF.type, TAB.AggregationRow))
        graph.remove((r, RDF.type, TAB.DetectedAggregationRow))
        graph.remove((r, TAB.aggregationFunction, None))
        graph.remove((r, TAB.aggregates, None))
    after = set()
    for i, (_lcol, _mcol, members) in agg.items():
        row = row_uris[i]
        after.add(row)
        graph.add((row, RDF.type, TAB.AggregationRow))
        graph.add((row, RDF.type, TAB.DetectedAggregationRow))
        graph.add((row, TAB.aggregationFunction, Literal("sum")))
        for m in members:
            graph.add((row, TAB.aggregates, row_uris[m]))
    groups = _retract_orphaned_groups(graph, before - after)
    return ChainArithmetic(tuple(chain), len(before), len(after),
                           len(before - after), len(after - before), None, groups)


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
    recognized: list[tuple[int, int]] = []
    links: dict[URIRef, URIRef] = {}          # continuation table -> the table it continues

    # ONE pass, pages in order: recognize the break BEFORE compiling page p, because the carried
    # reading is an INPUT to that compile (task 3). Recognition itself reads only the bands
    # (compile.page_bands, the shared seam — band index i in `blocks[p]` is region report i in
    # `pages[p]`), so it needs nothing from page p's compile and the ordering is sound. Carriage
    # chains: page 2 is carried from page 1's confirmed reading, which page 1 in turn carried.
    for p in range(n_pages):
        blocks.append(_recognition_blocks(page_bands(pdf_path, p)))
        carried, pair = None, None
        if p > 0 and blocks[p - 1] and blocks[p]:
            prev_idx = max(blocks[p - 1])     # the table that CLOSES the previous page
            cur_idx = min(blocks[p])          # the table that OPENS this one
            prev_cells, prev_bounds = blocks[p - 1][prev_idx]
            cur_cells, cur_bounds = blocks[p][cur_idx]
            if is_continuation(continuation_evidence_from_facts(
                    prev_cells, cur_cells, prev_bounds, cur_bounds)):
                recognized.append((p - 1, p))
                pair = (prev_idx, cur_idx)
                reading = pages[p - 1].regions[prev_idx].header_reading
                if reading is not None:
                    # THE ONLY place a carried reading is ever created. It is keyed by the band
                    # the law recognized, so no other band on this page — and no page the law
                    # refused — can receive one. `None` here means the previous page's band
                    # confirmed no reading to carry (every non-loop-L branch), and page p then
                    # compiles exactly as it would standalone.
                    carried = {cur_idx: reading}
        pages.append(compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes,
                                    span_proposer=span_proposer,
                                    row_role_proposer=row_role_proposer,
                                    doc_uri=page_doc_uri(p),
                                    carried_header_roles=carried))
        graph += pages[-1].graph
        if pair is None:
            continue
        prev_uri = pages[p - 1].regions[pair[0]].table_uri
        cur_uri = pages[p].regions[pair[1]].table_uri
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

    # LOOP N (R35): the subtotal arithmetic re-run over each chain's LOGICAL table, post-stitch
    # and before the merged graph is consumed. Chains of ONE member are skipped — not as an
    # optimisation but as the guarantee that a single-page document and an unrecognized page are
    # byte-untouched (a one-member chain IS the page-local window, so re-running would only risk
    # divergence for nothing).
    arithmetic = tuple(reconcile_chain_arithmetic(graph, chain)
                       for chain in chains if len(chain) > 1)

    asserted = sum(rep.asserted for rep in pages)
    escalated = sum(rep.escalated for rep in pages)
    denom = asserted + escalated
    score = 1.0 if denom == 0 else asserted / denom
    return DocumentReport(score, tuple(pages), tuple(chains), graph, tuple(recognized),
                          arithmetic)
