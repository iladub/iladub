"""document — the whole-document driver: per-page compile + continuation recognition (loop M).

§8 CLASSIFICATION
  * THE DECISION ("is the table opening page N the CONTINUATION of the table closing page N-1?")
    is an **AXIOM**: a declarative, open-world derivation over presence/equality facts about the
    two pages' leaf header blocks — `vocab/queries/continuation-of.rq`. The page PAIR is the
    closure boundary.
  * THE SECOND DECISION ("may a RECOGNIZED pair actually be stitched?") is a second **AXIOM**,
    `vocab/queries/continuation-licence.rq` (loop O, residue R33) — the CONTINUATION LICENCE,
    over presence facts about the two pages' NON-TABLE text blocks. Recognition says the pages
    share a template; the licence says the document was CUT. `is_licensed` runs it and
    `licence_evidence` emits its inputs; `compile_document` GATES on it (loop O task 3) —
    see THE GATE below.
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
  is necessary but NOT sufficient for "these are one table". What CLOSES it is neither text
  reading nor the body-side test continuation-of.rq's header proposed (measured falsification,
  R33: a page-invariant footer sits BELOW the table band on every specimen page, so "the earlier
  table runs to its page's last text line" refuses the genuine stitch) — it is what the renderer
  drew AROUND the two tables. See THE GATE below.

THE GATE (loop O, R33): RECOGNITION LICENSES NOTHING BY ITSELF
  `compile_document` asks the two questions in order, and the SECOND one gates EVERYTHING
  downstream. A recognized pair the licence REFUSES gets: no `tab:continuesTable`, no
  `tab:continuesColumn`/`tab:inLogicalColumn`, no carried header reading, no chain — and so, by
  construction rather than by a second guard, no document-level arithmetic window and no
  document-level row groups (both run per CHAIN, and a refused pair forms none). Each page then
  compiles exactly as it would standalone, which is the pre-loop-M behaviour. The refusal is
  RECORDED, never dropped, two ways: `DocumentReport.refused_licences` holds the page pair, and
  the merged graph carries `cur tab:licenceRefused prev` between the two tables (residue R34's
  in-kind closure, applied here — a refusal signal that exists must be auditable; the absence of
  a link cannot be told from a pair the law never considered). `tab:LicenceRefusalShape` refuses
  the contradiction of asserting both verdicts over one pair.

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
    * `DocumentReport.recognized` records every page pair the RECOGNITION AXIOM licensed — the
      honest record of what that law saw, independent of what the licence then said and of what
      the compile then managed. Recognition does not depend on either page compiling.
    * `DocumentReport.refused_licences` records the subset of those pairs the CONTINUATION
      LICENCE then refused (loop O). It is a subset of `recognized` by construction, and a pair
      in it can never appear in `chains`.
WHAT A CHAIN IS THEN FOR (loop N — the logical table is the closure holon; residue R35)
  A chain is the LOGICAL table the pagination cut. `reconcile_chain_arithmetic` re-runs the
  UNCHANGED loop-H subtotal arithmetic (`rows.detect_aggregation_rows`) over the chain's whole
  row sequence and reconciles the merged graph's aggregation typing to that result — the
  arithmetic is untouched, only the holon it closes over grows from the page to the logical
  table. See that function and `_UnitGrid` for the §8 classification, the cross-member column
  licence, and why refining a page-local intermediate here is honest rather than a rewrite.
  The ROW GROUPS follow the arithmetic that witnesses them: loop I's derivation (AXIOM,
  unchanged) re-runs over the document-confirmed aggregations and attaches to the chain's HEAD,
  and the members' page-local group sets are withdrawn rather than left in parallel — one
  logical table, one group set, whichever page a member row sits on. See
  `_supersede_page_groups` for that decision and `_link_columns` for the committed
  `tab:continuesColumn` correspondence that lets a key be read across the break at all.

    * `DocumentReport.chains` links tables that were RECOGNIZED **and** ASSERTED. A chain is a
      tuple of table URIs, so a page that asserted no table cannot appear in one — which is
      exactly the state task 2 measured (three singleton chains against `recognized` already
      holding ((0,1), (1,2))), and which any page whose carriage the SHACL oracle refuses will
      reproduce. `tab:continuesTable` is asserted on exactly the same condition as `chains`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import XSD

from .compile import CompilationReport, compile_tables, page_bands, _DOC, _validate
from .decisionlog import DEC
from .geometry import COORD_EPS
from .holon import TAB

_EV = Namespace("urn:iladub:continuation:")   # transient per-pair instance namespace
_LIC = Namespace("urn:iladub:licence:")       # transient per-pair licence-evidence namespace

# three dirs up from src/iladub/etkl/document.py -> repo root, then vocab/queries/
_QUERIES = Path(__file__).resolve().parents[3] / "vocab" / "queries"
CONTINUATION_OF_RQ = _QUERIES / "continuation-of.rq"
CONTINUATION_LICENCE_RQ = _QUERIES / "continuation-licence.rq"


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

    `groups_superseded` counts the page-derived groups withdrawn because the DOCUMENT-level
    derivation replaces them (loop N task 3): a chain member's page-local group set and the
    logical table's group set are two readings of the same rows, and keeping both would leave
    the feed two truths to choose between. `groups_derived` counts what the document-level
    derivation then built, attached to the chain's HEAD. The two are reported separately from
    `groups_retracted` because they answer different questions — "what did the wider window
    destroy" versus "what did it rebuild".

    `abstained` is not None when the pass refused this chain outright and changed nothing: the
    graph did not admit an unambiguous logical row sequence (see `_logical_row_sequence`).
    Refusal is not a verdict — the page-local typing AND the page-local groups simply stand.
    """
    chain: tuple[URIRef, ...]
    page_confirmed: int = 0
    document_confirmed: int = 0
    retracted: int = 0
    newly_confirmed: int = 0
    abstained: str | None = None
    groups_retracted: int = 0
    groups_superseded: int = 0
    groups_derived: int = 0


@dataclass(frozen=True)
class DocumentReport:
    """One document: the merged graph, the per-page reports, the continuation chains.

    `score` is asserted/(asserted+escalated) over the WHOLE document (never a mean of per-page
    scores — pages differ in size). `recognized` holds the (prev_page, page) pairs the
    continuation RECOGNITION AXIOM licensed; `chains` holds the table URIs actually linked (see
    the module docstring for why the two can differ mid-loop). `arithmetic` holds one
    `ChainArithmetic` per MULTI-MEMBER chain the document-level subtotal pass ran on — empty for
    a single-page or unchained document, where the pass never runs at all.

    `refused_licences` holds the (prev_page, page) pairs that were RECOGNIZED but which the
    CONTINUATION LICENCE refused (loop O, R33) — the negative record of the gate, kept because a
    refusal is evidence in its own right (two pages that look like one table and are not) and a
    pipeline that discards its refusals cannot be audited for them. It is recorded here for EVERY
    refused pair; the matching `tab:licenceRefused` graph fact needs two table URIs to name, so a
    pair one of whose pages asserted no table appears here and not in the graph — the same
    asymmetry `recognized` already has with `chains`.

    `repaired_bands` (loop Q, spec §4.0) holds every (page, band_index) whose pass-2
    section-repair re-read the membrane ADMITTED and the driver therefore adopted — the honest
    record of the repair's reach. ONLY adopted bands appear: a recognized candidate whose pass-2
    re-read still escalates leaves no entry here (its pass-1 report stands byte-untouched) but
    gets a `notes` line, and a page with no recognized intra-page section group never reaches
    the repair at all (the monotonicity the stem shapes pin).

    `notes` carries the repair's and the section-total oracle's REFUSALS as prose — a failed
    pass-2 candidate, a printed section total that does not reconcile — because a refusal
    signal that exists must be recorded (R34's discipline), and neither has a graph node to
    hang a fact on (the refused state IS the absence of the fact).
    """
    score: float
    pages: tuple[CompilationReport, ...]
    chains: tuple[tuple[URIRef, ...], ...]
    graph: Graph
    recognized: tuple[tuple[int, int], ...] = ()
    arithmetic: tuple[ChainArithmetic, ...] = ()
    refused_licences: tuple[tuple[int, int], ...] = ()
    repaired_bands: tuple[tuple[int, int], ...] = ()
    notes: tuple[str, ...] = ()

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


# ------------------------------------------- the continuation LICENCE (loop O, residue R33)
#
# §8 CLASSIFICATION — the DECISION ("may this recognized pair actually be STITCHED?") is an
# AXIOM: `vocab/queries/continuation-licence.rq`, a declarative open-world derivation over
# presence facts about the two pages' NON-TABLE text blocks. The pair is the closure boundary.
# Everything below is the PROCEDURAL evidence layer, in the shape the recognition machinery
# above established: raw extraction of each page's block inventory from bands the compile
# already built, and one node per block. It decides nothing and reads no block for meaning. It
# carries no epsilon (the licence compares strings and page-side, never coordinates), no
# threshold and no tuned constant. The only geometry it touches is an ORDERING (`band.top >
# table.bottom`, "this band is below the table"), which is a comparison of two measured
# quantities with no tolerance: bands do not overlap, so a non-table band is either wholly above
# the table band or wholly below it. The one arithmetic it performs — page index + 1, the
# PRINTED page ordinal — is an index-base conversion applied at emission, for exactly the reason
# COORD_EPS is applied at emission; see `licence_evidence` for the assumption it makes and how
# that assumption fails safe. The ordinal NORMALIZATION clause (b) compares over is applied at
# emission for the same reason and one more (round-2 review, F1): tokenizing is a string
# operation with a boundary convention, and a convention belongs where the facts are made, not
# inside a law that must stay digit-blind. See `_ordinal_normalized`.

_ORDINAL_SENTINEL = "<ORDINAL>"     # a non-numeric marker; nothing is ever compared against it


def _ordinal_normalized(text: str, ordinal) -> str:
    """`text` with every WHOLE TOKEN equal to the page's printed ordinal replaced by the sentinel.

    THE TOKEN BOUNDARY IS THE WHOLE POINT (loop O round-2 review, finding F1). The law says
    "tokens equal to the block's own printed page ordinal", and this function is where that word
    is honoured: an earlier form did an unanchored substring replacement inside the query, which
    silently cancelled the LEADING DIGIT of unrelated numbers — measured, `TOTAL 1000` / `TOTAL
    2000` both normalized to `<ORDINAL>000` and LICENSED, which is exactly the below-table
    subtotal/total shape the licence exists to refuse. Whole-token replacement refuses all three
    measured cases (`TOTAL 1000`/`TOTAL 2000`, `Lot 11`/`Lot 22`, `Subtotal 141`/`Subtotal 242`)
    and, as a bonus, LICENSES the commonest real footer idiom `Page 1 of 12` / `Page 2 of 12`,
    which the substring form refused (F2: `12` contains `1`).

    TOKENIZATION is `str.split()` per line — whitespace, the repo's established convention, the
    same one `rows._numeric_token_sum` and `rows.detect_aggregation_rows` tokenize cells with.
    Line structure is preserved (each line normalized, then rejoined with the newline
    `_band_text` used) so two blocks are never made equal by a difference in line breaking.

    ONE ASYMMETRY, STATED (loop O close, re-review N2): the rejoin collapses WHITESPACE RUNS
    within a line, so clause (b) compares whitespace-collapsed text while clause (a) compares
    `tab:blockText` verbatim. The two entry points agree on every real band — `_band_text`
    already single-space-joins its words — so the divergence is reachable only through
    hand-built facts handed to `licence_evidence_from_facts`, never from a compiled page.

    Doing this HERE rather than in the query keeps the AXIOM digit-blind: the query compares two
    emitted strings for identity and never learns what an ordinal, a numeral or a token is. The
    sentinel is a non-numeric marker, so no numeral enters the query either.
    """
    mark = str(int(ordinal))
    return "\n".join(
        " ".join(_ORDINAL_SENTINEL if tok == mark else tok for tok in line.split())
        for line in text.split("\n"))


def licence_evidence_from_facts(blocks) -> Graph:
    """Fresh Graph() for ONE page pair — the inputs to continuation-licence.rq.

    The single evidence shape, reached two ways (the `continuation_evidence` idiom):
    `licence_evidence` derives the facts from two pages' bands, tests hand them in directly.

    `blocks` is an iterable of `(text, page_side, below_its_table, page_ordinal)`:
      * `page_side` — 0 for the PRIOR page N-1, 1 for the CONTINUATION page N;
      * `below_its_table` — True when the block sits BELOW its OWN page's table (a tail block,
        `tab:BelowTableBlock`), False when it sits above it (`tab:AboveTableBlock`). ONE
        positional fact, read the same way on both pages;
      * `page_ordinal` — that page's PRINTED ordinal, 1-based (see `licence_evidence` for where
        the +1 is applied and on what licence).
    The facts record WHERE a block sits and WHAT ordinal its page carries; what a position
    REQUIRES is the query's business, not this function's — which is why an unconstrained
    prior-page head block still enters the graph (it can answer a continuation block's
    counterpart test) rather than being dropped here, and why the ordinal is emitted on EVERY
    block, including the ones no clause constrains.

    TWO TEXT FACTS PER BLOCK, and the law uses each for one clause: `tab:blockText` is the exact
    surface text (clause (a) compares it strictly), `tab:ordinalNormalizedText` is the same text
    with whole tokens equal to THIS page's ordinal replaced by a sentinel (clause (b) compares
    that). Both are computed HERE — see `_ordinal_normalized` — so the AXIOM stays digit-blind.
    `tab:pageOrdinal` itself is carried for AUDITABILITY only: the query never reads it (the
    `tab:leafOriginX` idiom, one derivation over).

    The `tab:ContinuationPairUnderTest` node is emitted unconditionally, so a pair with NO blocks
    at all still presents a subject for the law to license — vacuity is licence, deliberately
    (see the query header).
    """
    g = Graph()
    pair = URIRef(f"{_LIC}pair")
    g.add((pair, RDF.type, TAB.ContinuationPairUnderTest))
    for i, (text, page_side, below, ordinal) in enumerate(blocks):
        side = "prior" if not page_side else "continuation"
        u = URIRef(f"{_LIC}{side}-t{i}")
        g.add((pair, TAB.hasPageBlock, u))
        g.add((u, RDF.type, TAB.PriorPageTextBlock if not page_side
               else TAB.ContinuationPageTextBlock))
        g.add((u, TAB.blockText, Literal(text)))
        g.add((u, TAB.ordinalNormalizedText, Literal(_ordinal_normalized(text, ordinal))))
        g.add((u, RDF.type, TAB.BelowTableBlock if below else TAB.AboveTableBlock))
        g.add((u, TAB.pageOrdinal, Literal(int(ordinal), datatype=XSD.integer)))
    return g


def _band_text(band) -> str:
    """A band's exact surface text: words left-to-right, lines top-to-bottom, newline-joined.

    Raw extraction, and the whole of it — no normalisation, no case folding, no stripping. Two
    renderings of one furniture block on two pages produce the same string exactly when the
    renderer drew the same words; anything softer would be the pipeline deciding that two
    different blocks are "the same enough", which is a judgment the law does not make.
    """
    return "\n".join(" ".join(w.text for w in ln.words) for ln in band.lines)


def licence_evidence(prev_bands, prev_table_index, cur_bands, cur_table_index,
                     prev_page_number, cur_page_number) -> Graph:
    """The licence evidence for two pages' BAND inventories (the production entry point).

    `prev_table_index` / `cur_table_index` are the indices, in each page's own `page_bands` list,
    of the band the recognition AXIOM paired — the table that CLOSES page N-1 and the one that
    OPENS page N. (The plan named the arguments `prev_table_span` / `cur_repeated_header_span`;
    the band index carries both, and reading the span off the band keeps this one seam with
    `compile.page_bands` rather than adding a second geometry path that could drift.)
    `prev_page_number` / `cur_page_number` are the 0-BASED page indices the driver iterates.

    A NON-TABLE BLOCK is, here, any OTHER band of the page. Two consequences, both stated because
    neither is free:
      * the repeated header block needs no exclusion of its own — it is drawn INSIDE the
        recognized table band, and bands do not overlap, so every band this function emits is
        outside it by construction;
      * a page carrying a SECOND table is treated as carrying a text block, since this function
        has no compile verdict to tell one band from another. The bias is toward REFUSAL — an
        unlicensed pair stays two independent documents — which is the same direction the
        driver's one-candidate-pair-per-break limit already leans (see `compile_document`), and
        never toward a wrong stitch.

    THE POSITION CLASS is an ORDERING over the page's own y axis, read the same way on both
    pages: a band whose top lies below its page's table band's bottom is BELOW that table's last
    body row. No tolerance, no epsilon, no tuned threshold — the bands were cut apart by
    `detect_bands`, so they are disjoint intervals and there is no third case to arbitrate.

    THE PRINTED PAGE ORDINAL, and the licence for computing it here (clause (b) of the law).
    `tab:pageOrdinal` is emitted as `page index + 1`. The `+ 1` is the 0-based-index-to-1-based-
    ordinal conversion of the PDF page tree, applied AT EMISSION for exactly the reason
    `continuation_evidence` applies COORD_EPS at emission: the query must carry no numeral, so
    every arithmetic and every float comparison is spent HERE and surfaces as a fact the law can
    only match, never compute with. It is not a tuned constant and nothing is compared against
    it — a page's ordinal is the same fact as its index, stated in the numbering a reader sees.
    THE ASSUMPTION IT MAKES, stated where it is made: that the document's PRINTED ordinal equals
    its page index plus one. That holds on the specimen (page 0 prints '1') and fails for roman
    front matter or an offset first page — and when it fails the normalization simply does not
    cancel, so the pair REFUSES. Conservative, never a wrong stitch (§7).
    """
    facts = []
    prev_table, cur_table = prev_bands[prev_table_index], cur_bands[cur_table_index]
    for i, band in enumerate(prev_bands):
        if i != prev_table_index:
            facts.append((_band_text(band), 0, band.top > prev_table.bottom,
                          prev_page_number + 1))
    for i, band in enumerate(cur_bands):
        if i != cur_table_index:
            facts.append((_band_text(band), 1, band.top > cur_table.bottom,
                          cur_page_number + 1))
    return licence_evidence_from_facts(facts)


def is_licensed(evidence: Graph) -> bool:
    """Run continuation-licence.rq over one pair's evidence: may the pair be STITCHED?

    A row means the law licensed the pair; no row is its refusal, and a refused pair stays two
    independent documents however well their header blocks matched. Recognition and licence are
    two different questions and are kept as two derivations: the first says the pages share a
    template, the second says the document was CUT.
    """
    q = Path(CONTINUATION_LICENCE_RQ).read_text(encoding="utf-8")
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


def _link_columns(graph: Graph, cur_uri: URIRef, prev_uri: URIRef) -> int:
    """Assert `tab:continuesColumn` column-for-column, at EQUAL INDEX, for a licensed pair.

    The column half of `tab:continuesTable`, asserted in the same place and on the same
    licence: clauses (b)+(c) of continuation-of.rq put the two pages' leaf columns in 1:1
    correspondence AT EQUAL INDEX (every column of page N-1's leaf row has a counterpart at the
    same index with the same text at an agreeing ink origin, and none of page N's is left
    without one), so index i on the continuation page IS index i on the page it continues.

    WHY COMMIT IT rather than recompute it where it is needed: two consumers must recognize one
    logical column across the break — the document-level row-group key (which member cell sits
    in "the label column"?) and the feed's key injection (does this row already carry a value in
    that column?). Without the edge each would have to parse `-c{i}` out of the column IRIs, and
    the feed in particular is explicitly IRI-parsing-free. The edge is read, not named.

    TWO RELATIONS, AND WHY (loop N review). `tab:continuesColumn` is the PAIRWISE fact, which is
    all this one licensed pair evidences. `tab:inLogicalColumn` is its reflexive-transitive
    CLOSURE, pointing every member's column at the chain HEAD's — materialized here, incrementally
    (the head's column is read off the PREVIOUS page's own closure edge, so a third page reaches
    page 0 without anyone knowing the chain yet; the driver stitches pairs in strictly increasing
    page order, which is what makes the induction sound). It is asserted rather than entailed
    because iladub is reasoner-free, and because a `tab:continuesColumn*` property path inside the
    key derivation was MEASURED at 21 s for one 94-member witness where the one-hop closure form
    costs 0.26 s on the same graph. The reflexive edge on the head's own column is not a trick: a
    column IS part of its own logical column, and it is what lets ONE triple pattern reach a head
    cell and a continuation cell alike.

    Indices are read back out of OUR OWN minting (`_index_suffix`), and a column URI that does
    not follow the convention is simply not linked — no guess, and the pair's other columns are
    unaffected. An index present on only one side gets no edge either: the law licensed a
    bijection, and asserting an edge the evidence does not carry would be fabrication (§7).
    Returns the number of `tab:continuesColumn` edges asserted (one per shared index)."""
    def _by_index(t):
        out = {}
        for c in graph.objects(t, TAB.hasLeafColumn):
            i = _index_suffix(c, t, "c")
            if i is not None:
                out[i] = c
        return out

    prev_cols, cur_cols = _by_index(prev_uri), _by_index(cur_uri)
    n = 0
    for i in sorted(set(prev_cols) & set(cur_cols)):
        graph.add((cur_cols[i], TAB.continuesColumn, prev_cols[i]))
        canonical = graph.value(prev_cols[i], TAB.inLogicalColumn) or prev_cols[i]
        graph.add((prev_cols[i], TAB.inLogicalColumn, canonical))    # reflexive at the head
        graph.add((cur_cols[i], TAB.inLogicalColumn, canonical))
        n += 1
    return n


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
    deep until task 3 rebuilds the set. Nothing before task 3 depends on the value being exact:
    RowNoOverlapShape exempts every pair involving a derived group. feed._header_path DOES read a
    group's tab:headerLevel (the max-selector picking the deepest header covering a row), but an
    inflated level can only mis-select where two groups cover the same row — which needs a
    surviving group whose parent was retracted, a state no constructed specimen has reached
    (retraction extends a walk-back across the break, and any barrier protecting a child protects
    its parent equally). Not proven unreachable — registered as a residue.
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


def _supersede_page_groups(graph: Graph, chain) -> int:
    """Withdraw every SURVIVING page-derived row group on this chain's member tables.

    THE SUPERSESSION DECISION, stated because it is a decision (loop N task 3). After the
    document window has re-typed the chain's aggregations, a chain member can still carry loop
    I's page-local `tab:DerivedRowGroup` nodes — derived, honestly, from the page-local reading
    of a table the pagination had cut. The document-level derivation now produces the LOGICAL
    table's group set over the same rows. Two options existed and only one is honest:

      * leave both — the graph then holds two parallel group sets over one row axis, and the
        feed picks between them by iteration order. A record's identity and its injected keys
        would depend on which set the reader happened to walk. That is a §3 violation dressed as
        conservatism: a page-local group over a CUT group is a proposition the wider window has
        already disposed of, and letting it stand is letting it pass as an assertion;
      * withdraw the page-local set and re-derive at document level — ONE truth about the
        chain's row groups, derived from the document-confirmed facts, with the page-local
        reading recorded as `groups_superseded` in the ledger rather than silently dropped.

    We take the second. It is the same idiom `_retract_orphaned_groups` uses (that one withdraws
    a derivation whose GROUND was retracted; this one withdraws a derivation the wider holon
    RE-TOOK), and it makes two task-2 residues moot for chains rather than fixed in place: a
    surviving sibling's stale `tab:headerLevel` (appendix (c)) and a surviving group's
    stale-but-not-orphaned `tab:coversRow` (appendix (d)) both belonged to nodes that no longer
    exist — every level and every member edge on a chain is now derived fresh, in one pass, from
    the document-level `tab:aggregates`.

    SCOPE: member tables of THIS chain only, and only when the pass did not abstain. A
    non-chained table is never reached (a one-member chain never calls this), so its page-local
    groups are byte-untouched. Returns the number of groups withdrawn."""
    n = 0
    for t in chain:
        for grp in set(graph.objects(t, TAB.hasHeaderNode)):
            if (grp, RDF.type, TAB.DerivedRowGroup) not in graph:
                continue                     # an AUTHORED header node — never ours to withdraw
            graph.remove((grp, None, None))
            graph.remove((None, None, grp))  # hasHeaderNode, and any child's parentHeader
            n += 1
    return n


def _derive_document_row_groups(graph: Graph, chain, agg, row_uris) -> int:
    """Re-derive loop I's row groups over the LOGICAL table, attached to the chain's HEAD.

    Loop I's derivation is unchanged and still an AXIOM (row-group-key-logical.rq +
    row-group-nesting.rq); this is the caller that resolves its three URIs for a chain — the
    witness row and its members from the merged graph's own row URIs (so `tab:coversRow` edges
    MAY cross member tables, which is the point), and the label column from the HEAD table at
    the index the arithmetic read the level off. The head's column stands for the logical column
    because `tab:continuesColumn` links each member's column to it — the committed record of
    clauses (b)+(c), which the key query reaches via `tab:inLogicalColumn` (the materialized
    one-hop closure, loop N review's perf rewrite) rather than parsing any IRI.

    Group nodes are minted `{head}-rg{k}` on the LOGICAL sequence position k. For the head's own
    rows that is exactly the URI loop I minted (the sequence opens with the head's rows, in row
    order), so a group that survives the wider window keeps its identity; a member's group gets a
    URI in the head's space because the group is the LOGICAL table's, not the page's."""
    from .rowgroups import derive_row_groups_over
    head = chain[0]
    witnesses = tuple((row_uris[k], URIRef(f"{head}-c{agg[k][0]}"), URIRef(f"{head}-rg{k}"))
                      for k in sorted(agg))
    return derive_row_groups_over(graph, head, witnesses, "row-group-key-logical.rq")


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
    # THE GROUP SET IS RE-TAKEN AT DOCUMENT LEVEL (task 3): whatever page-local groups survive
    # are withdrawn (`_supersede_page_groups` states the decision and why the alternative is
    # dishonest), and loop I's derivation re-runs over the document-confirmed aggregations,
    # attached to the HEAD. Ordering is load-bearing twice over: supersession must follow the
    # orphan retraction (so `groups_retracted` still counts the destroyed derivations, not the
    # superseded ones), and both must precede the re-derivation (or the fresh groups would be
    # swept away by the very sweep that clears the stale ones).
    superseded = _supersede_page_groups(graph, chain)
    derived = _derive_document_row_groups(graph, chain, agg, row_uris)
    return ChainArithmetic(tuple(chain), len(before), len(after),
                           len(before - after), len(after - before), None, groups,
                           superseded, derived)


# --------------------------------------- the SECTION repair (loop Q, spec 2026-08-04 §4.0-§4.1)
#
# §8 CLASSIFICATION
#   * WHICH bands repeat the same author-drawn section shape is the sectiongraph AXIOM
#     (section-repeat.rq), verdict-independent — this module only calls it.
#   * WHETHER a re-read candidate may be ADOPTED is decided by the EXISTING region membrane
#     (tiling shapes + score) inside the pass-2 `compile_tables` call — no new decision here.
#   * WHETHER a printed per-section total CONFIRMS its section is loop H's
#     `detect_aggregation_rows`, VERBATIM, run with the SECTION as the closure window —
#     justified PROCEDURAL for loop H's own reason (decidable exact Decimal arithmetic).
#   * Everything below is PROCEDURAL glue in the reconcile_chain_arithmetic mould: subgraph
#     copy, triple retraction of our own minting, report bookkeeping. It reads no text for
#     meaning and carries no tuned constant.


def _remove_escalation_record(graph: Graph, page_doc: URIRef, idx: int) -> None:
    """Withdraw the pass-1 escalation CANDIDATE of ONE adopted band — precisely what the compile
    minted for an escalated band and nothing else. Two possible subjects, both OUR OWN minting
    (`compile_tables` / `holon.assert_hier_region`): `{page_doc}#region{idx}` (every
    escalate_region call site in compile_tables) and `{page_doc}#htable{idx}-rt` (the hier
    path's ROUND_TRIP_FAIL candidate). `holon.escalate_region` emits OUTGOING triples only, so
    removing the subjects' triples removes the PROPOSITION whole. THE DECISION (stated per the
    plan's 'document your choice'): the pass-1 escalation is not kept as a parallel proposition
    — the pass-2 re-read supersedes it (the same idiom `_supersede_page_groups` documents: two
    parallel truths over one band would leave the feed to pick by iteration order, a §3
    violation), and the adoption is recorded on `DocumentReport.repaired_bands` instead.

    WHAT THIS DOES **NOT** REMOVE, and why (final-review C1). An earlier form of this docstring
    claimed 'nothing in the repo ever points AT a candidate node'. Since the reading decision
    record (spec 2026-08-07) that is FALSE: the band's pass-1 judgement chain
    (`{page_doc}#region{idx}-reading`, `-d{n}`, `-d{n}-opt-*`) points at the candidate with
    `dec:regarding`, and it is deliberately LEFT STANDING. The chain is not a proposition about
    the document — it is the truthful account of what the reader did on pass 1, and 'pass 1
    escalated, pass 2 recovered' is exactly the reasoning this record exists to preserve
    (CLAUDE.md §5: context is carried, not discarded). What makes it non-contradictory is that
    the caller carries the pass-2 chain in beside it and links the two verdict decisions with
    `dec:supersedes` — see `_band_reading_subgraph` / `_verdict_decision` and the adoption site
    in `compile_document`. So the candidate IRI survives as the OBJECT of `dec:regarding` with
    no outgoing triples of its own: it names the band region the reading was about, and asserts
    nothing about it."""
    for cand in (URIRef(f"{page_doc}#region{idx}"), URIRef(f"{page_doc}#htable{idx}-rt")):
        graph.remove((cand, None, None))


def _band_reading_subgraph(g: Graph, page_doc: URIRef, idx: int) -> Graph:
    """ONE band's READING DECISION RECORD out of a whole-page compile (final-review C1).

    The companion of `_band_subgraph`, over the other URI space the compile mints per band:
    `decisionlog` hangs the band process, its judgements and their options off
    `{page_doc}#region{idx}-` (`-reading`, `-d{n}`, `-d{n}-opt-{slug}`). The trailing hyphen is
    what keeps band 1 from swallowing band 10 — `region10-reading` does not start with
    `region1-`. Closed over outgoing reachability exactly as `_band_subgraph` is, so the page
    process (`dcterms:isPartOf`) and the reader agent (`dec:decidedBy`) ride along; the
    `dec:regarding` object is the band's own region node, which on an ASSERTED band has no
    outgoing triples and so contributes nothing. A COPY, never a mutation of `g`."""
    from rdflib import BNode
    out = Graph()
    prefix = f"{page_doc}#region{idx}-"
    seen: set = {s for s in set(g.subjects())
                 if isinstance(s, URIRef) and str(s).startswith(prefix)}
    frontier = list(seen)
    while frontier:
        s = frontier.pop()
        for pred, o in g.predicate_objects(s):
            out.add((s, pred, o))
            if isinstance(o, (URIRef, BNode)) and o not in seen:
                seen.add(o)
                frontier.append(o)
    return out


def _verdict_decision(g: Graph, page_doc: URIRef, idx: int):
    """ONE band's `verdict` judgement node, or None (final-review C1).

    Read back out of OUR OWN minting, as `_index_suffix` reads the table URIs: `decisionlog`
    mints `{page_doc}#region{idx}-d{n}` and labels it with the judgement name, and
    `compile_tables` records exactly ONE `verdict` judgement per band on every branch. A band
    with no chain (or none yet recorded) yields None and the caller simply asserts no lineage —
    an edge the evidence does not carry is never invented (§7)."""
    prefix = f"{page_doc}#region{idx}-d"
    for d in g.subjects(RDF.type, DEC.DecisionHolon):
        if str(d).startswith(prefix) and (d, RDFS.label, Literal("verdict")) in g:
            return d
    return None


def _band_subgraph(g: Graph, table_uri: URIRef) -> Graph:
    """The ONE band's subgraph out of a pass-2 whole-page compile: every subject minted under
    the table's URI space (`{table_uri}`, `{table_uri}-...` — the compile's own minting
    convention, the `_index_suffix` licence read in the other direction; this catches the
    ROUND_TRIP_FAIL `-cc{r}_{col}` propositions, which hang off no table edge), closed over
    outgoing reachability so BNode bboxes ride along. Objects outside the band (the pass-2 doc
    URI, provenance region URIs) have no outgoing triples in the page graph and contribute
    nothing. A COPY, never a mutation of the pass-2 graph."""
    from rdflib import BNode
    out = Graph()
    prefix = str(table_uri) + "-"
    roots = [s for s in set(g.subjects())
             if isinstance(s, URIRef) and (s == table_uri or str(s).startswith(prefix))]
    seen: set = set(roots)
    frontier = list(roots)
    while frontier:
        s = frontier.pop()
        for pred, o in g.predicate_objects(s):
            out.add((s, pred, o))
            if isinstance(o, (URIRef, BNode)) and o not in seen:
                seen.add(o)
                frontier.append(o)
    return out


def _confirm_section_total(graph: Graph, table_uri: URIRef, band) -> tuple[bool, str | None]:
    """Associate a section table's printed trailing total with the table — or refuse.

    THE ORACLE IS ARITHMETIC (spec §4.0: 'the section boundary oracle is arithmetic'): the
    total candidate is the section table's LAST row, positioned strictly BELOW the section
    grid's closing rule (the band's last drawn hrule — presence/ordering over author marks,
    no tolerance: bands' lines and hrules are measured, disjoint quantities), and it CONFIRMS
    iff loop H's `detect_aggregation_rows` — unchanged, run over THIS table's own row sequence,
    the section being the closure window — confirms it: exact Decimal equality between the
    printed measure and the section rows' measure-column token-sum. 'TOTAL' is never read as a
    word; language is never evidence (loop H's own law).

    Returns (confirmed, note): confirmed=True emits `tab:SectionTotal` + `tab:confirmsSection`;
    a candidate-shaped last row that does NOT reconcile returns a refusal note and emits
    NOTHING (absence + note, §7 — never guessed); a section with no trailing strip below its
    closing rule, or no candidate-shaped last row, has no total to judge — (False, None)."""
    from .rows import detect_aggregation_rows, is_aggregation_shaped, row_column_count
    hy = [round(float(h.y), 2) for h in (getattr(band, "hrules", ()) or ())]
    if not hy or not any((ln.top + ln.bottom) / 2.0 > max(hy) for ln in band.lines):
        return False, None            # nothing printed below the grid's closing rule
    seq, row_uris, why = _logical_row_sequence(graph, (table_uri,))
    if seq is None:
        return False, f"section-total window abstained ({why})"
    rows, grid = seq
    if len(rows) < 2:
        return False, None
    agg = detect_aggregation_rows(rows, grid)
    last = len(rows) - 1
    if last in agg:
        graph.add((row_uris[last], RDF.type, TAB.SectionTotal))
        graph.add((row_uris[last], TAB.confirmsSection, table_uri))
        return True, None
    # final-review F2: was `max(len(r.cells) for r in rows)` / `len(rows[last].cells) == 2` —
    # RAW CELL counts, which diverge from `detect_aggregation_rows`'s DISTINCT-COLUMN counting
    # (rows.py:121) whenever a row has two cells in one column. Now the SAME predicate, so the
    # two checks can never drift apart again.
    widest = max(row_column_count(r, grid) for r in rows)
    if is_aggregation_shaped(rows[last], widest, grid):
        return False, ("printed section total does not reconcile with the section's "
                       "measure-column sum; association refused")
    return False, None                # no total candidate printed — nothing to confirm


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

    THE LICENCE GATE (loop O, residue R33 — read before consuming `chains`). Recognition means
    "the header block repeats and the author's grid matches", which two INDEPENDENT tables built
    from one template satisfy exactly (measured) — necessary, not sufficient, for "one table".
    So a recognized pair is asked a SECOND question before anything acts on it: is the pair
    LICENSED (`continuation-licence.rq` over the two pages' non-table blocks — was the document
    CUT here, or do these pages merely share a template)? The gate sits between recognition and
    every consumer: an unlicensed pair gets no carried reading, no `tab:continuesTable`, no
    `tab:continuesColumn`/`tab:inLogicalColumn` and no chain — hence, with no second guard
    needed, no document-level arithmetic window and no document-level row groups (both iterate
    CHAINS, and a refused pair forms none). Both its pages compile as they would standalone.
    The refusal is recorded, never dropped: `refused_licences` on the report, and
    `cur tab:licenceRefused prev` in the graph (R34's in-kind closure).

    WHOLE-GRAPH VALIDATION (loop N task 4; gate re-decided loop O task 3). `compile_tables`
    already validates each PAGE's own subgraph (inside the per-page loop below, before merge) —
    but the document-level facts (`tab:continuesTable`/`tab:continuesColumn`/
    `tab:inLogicalColumn`, `tab:licenceRefused`, and the arithmetic pass's cross-table
    `tab:aggregates`/`tab:coversRow` edges) are all asserted AFTER that, onto the MERGED graph,
    and never met a SHACL membrane until this pass. Measured on the stem (29,377 triples):
    validation costs 41.3 s on top of the ~179 s compile — real, not absorbed silently.
    THE GATE IS `recognized`, i.e. it runs whenever the RECOGNITION law fired, licensed or not —
    deliberately unchanged by loop O, and the reason is now stronger than it was: a document with
    a refused pair carries `tab:licenceRefused` in its merged graph, so it is no longer the plain
    disjoint union of already-validated page graphs and `tab:LicenceRefusalShape` has something
    to check. Gating on the LICENCE instead would leave exactly the new fact unvalidated. With no
    recognition at all the merged graph IS that disjoint union and no document-level triple
    exists for any shape to see, so re-validating would spend the same 41 s proving nothing (a
    single-page or unchained document is exactly this case, always). The logical table is the
    closure holon (spec §2b/§8), and this is where its closure gets checked.
    """
    n_pages = page_count(pdf_path)
    pages: list[CompilationReport] = []
    blocks: list[dict] = []
    band_lists: list[list] = []               # page p's band inventory, kept for loop Q's repair
    graph = Graph()
    recognized: list[tuple[int, int]] = []
    refused: list[tuple[int, int]] = []       # recognized, then REFUSED by the licence (loop O)
    links: dict[URIRef, URIRef] = {}          # continuation table -> the table it continues
    prev_bands = None                         # page p-1's band inventory, the licence's evidence

    # ONE pass, pages in order: recognize the break BEFORE compiling page p, because the carried
    # reading is an INPUT to that compile (task 3). Recognition itself reads only the bands
    # (compile.page_bands, the shared seam — band index i in `blocks[p]` is region report i in
    # `pages[p]`), so it needs nothing from page p's compile and the ordering is sound. Carriage
    # chains: page 2 is carried from page 1's confirmed reading, which page 1 in turn carried.
    for p in range(n_pages):
        bands = page_bands(pdf_path, p)
        band_lists.append(bands)
        blocks.append(_recognition_blocks(bands))
        carried, pair, refused_pair = None, None, None
        if p > 0 and blocks[p - 1] and blocks[p]:
            prev_idx = max(blocks[p - 1])     # the table that CLOSES the previous page
            cur_idx = min(blocks[p])          # the table that OPENS this one
            prev_cells, prev_bounds = blocks[p - 1][prev_idx]
            cur_cells, cur_bounds = blocks[p][cur_idx]
            if is_continuation(continuation_evidence_from_facts(
                    prev_cells, cur_cells, prev_bounds, cur_bounds)):
                recognized.append((p - 1, p))
                # THE LICENCE GATE (loop O, R33) — the second question, asked BEFORE anything
                # downstream exists. It reads the two pages' NON-TABLE bands, which is why the
                # band lists are kept: `page_bands` is the one seam, and `prev_bands` still holds
                # page p-1's inventory at this point (it is re-bound below, after the gate).
                if is_licensed(licence_evidence(prev_bands, prev_idx, bands, cur_idx, p - 1, p)):
                    pair = (prev_idx, cur_idx)
                    reading = pages[p - 1].regions[prev_idx].header_reading
                    if reading is not None:
                        # THE ONLY place a carried reading is ever created. It is keyed by the
                        # band the law recognized, so no other band on this page — and no page
                        # either law refused — can receive one. `None` here means the previous
                        # page's band confirmed no reading to carry (every non-loop-L branch),
                        # and page p then compiles exactly as it would standalone.
                        carried = {cur_idx: reading}
                else:
                    # A REFUSED pair leaves `pair` and `carried` None, so page p compiles
                    # standalone and no link, chain, arithmetic window or row group can form
                    # from it. The refusal itself is recorded, below and on the report.
                    refused.append((p - 1, p))
                    refused_pair = (prev_idx, cur_idx)
        prev_bands = bands
        pages.append(compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes,
                                    span_proposer=span_proposer,
                                    row_role_proposer=row_role_proposer,
                                    doc_uri=page_doc_uri(p),
                                    carried_header_roles=carried))
        graph += pages[-1].graph
        if refused_pair is not None:
            # The refusal as a FACT (R34's in-kind closure): asserted only when both pages did
            # assert a table, since the fact names the two tables. The pair is on the report
            # either way — the same asymmetry `recognized`/`chains` already has.
            prev_uri = pages[p - 1].regions[refused_pair[0]].table_uri
            cur_uri = pages[p].regions[refused_pair[1]].table_uri
            if prev_uri is not None and cur_uri is not None:
                graph.add((cur_uri, TAB.licenceRefused, prev_uri))
        if pair is None:
            continue
        prev_uri = pages[p - 1].regions[pair[0]].table_uri
        cur_uri = pages[p].regions[pair[1]].table_uri
        if prev_uri is None or cur_uri is None:
            continue                          # recognized, but one side asserted no table (R29)
        graph.add((cur_uri, TAB.continuesTable, prev_uri))
        _link_columns(graph, cur_uri, prev_uri)   # the column half of the same link (loop N)
        links[cur_uri] = prev_uri

    # ------------------------------------------------------ LOOP Q (spec §4.0): SECTION REPAIR
    # Strictly AFTER band reading and carriage — the order of authority (band reading →
    # carriage → section repair) is load-bearing and pinned on both specimen shapes. Per page:
    # recognize the intra-page section repetition over ALL ruled bands, VERDICT-INDEPENDENT
    # (sectiongraph.section_candidates — the identity evidence is raw author marks + raw text,
    # no successful reading required); within a recognized group, re-read ONLY the
    # still-escalated members (pass-2 compile_tables with `section_repair_bands`, under the
    # page-scoped `{page_uri}/r2` URI so pass-2 mints can never collide with pass-1's); ADOPT a
    # candidate's re-read IFF the existing region membrane admitted it. MONOTONE BY
    # CONSTRUCTION: a band that asserted in pass 1 is never re-read; a candidate whose pass-2
    # still escalates keeps its pass-1 report byte-untouched (noted, never traced); a page with
    # no recognized group skips everything — the stem shapes never reach this code (their pages
    # carry at most one ruled band, and recognition needs two).
    from .sectiongraph import section_candidates
    from dataclasses import replace as _dc_replace
    repaired: list[tuple[int, int]] = []
    notes: list[str] = []
    page_section_groups: list[tuple[int, tuple[tuple[int, ...], ...]]] = []
    for p in range(n_pages):
        ruled = [(i, b, tuple(b.rules)) for i, b in enumerate(band_lists[p]) if b.rules]
        if len(ruled) < 2:
            continue                  # nothing can repeat intra-page: recognition needs a pair
        groups = section_candidates(ruled)
        if not groups:
            continue
        page_section_groups.append((p, groups))
        # region report index IS band index (page_bands' pinned enumeration contract), so the
        # verdict filter and the repair flag name the same band by the same integer.
        candidates = frozenset(i for grp in groups for i in grp
                               if pages[p].regions[i].verdict == "escalated")
        if not candidates:
            continue                  # every member asserted at band level: stitch-only page
        # final-review F4: `validate_shapes=validate_shapes` — pass 2 inherits pass 1's SHACL
        # policy verbatim, on purpose. `compile_tables` raises AssertionError if an ASSERTED
        # holon fails the tab: SHACL membrane; that is a COMPILER-INVARIANT violation ("this
        # code minted a graph its own contract rejects"), never a fact about the document, so
        # it must abort here exactly as it would on a pass-1 band — a repaired band silently
        # let through with a laxer policy would be evidence laundering, not repair.
        r2_doc = URIRef(f"{page_doc_uri(p)}/r2")
        rep2 = compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes,
                              span_proposer=span_proposer,
                              row_role_proposer=row_role_proposer,
                              doc_uri=r2_doc,
                              section_repair_bands=candidates)
        new_regions = list(pages[p].regions)
        adopted_any = False
        for idx in sorted(candidates):
            r2 = rep2.regions[idx]
            if r2.verdict == "asserted" and r2.table_uri is not None:
                # ADOPTION: swap the region report, swap the triples. The pass-1 escalation
                # CANDIDATE is withdrawn (superseded, not kept as a parallel proposition — see
                # _remove_escalation_record for the decision) and the pass-2 table's own
                # subgraph — already membrane-validated inside the pass-2 compile — merges in.
                _remove_escalation_record(graph, page_doc_uri(p), idx)
                graph += _band_subgraph(rep2.graph, r2.table_uri)
                # THE READING RECORD OF THE RE-READ (final-review C1). Before this, the merged
                # graph kept ONLY the pass-1 chain, whose verdict says `escalated`, next to a
                # region the graph now ASSERTS — the record contradicted the graph, silently.
                # Carrying the pass-2 chain in and linking the two VERDICT decisions with
                # `dec:supersedes` (`vocab/ontology/dec.ttl:174` — domain and range are both
                # dec:DecisionHolon, which is why the link joins the two judgements and NOT the
                # two dec:Process containers) keeps both readings and makes the supersession
                # queryable: a chain whose verdict decision is the object of a `dec:supersedes`
                # is history, and the one that is not is the effective verdict.
                graph += _band_reading_subgraph(rep2.graph, r2_doc, idx)
                v1 = _verdict_decision(graph, page_doc_uri(p), idx)
                v2 = _verdict_decision(rep2.graph, r2_doc, idx)
                if v1 is not None and v2 is not None:
                    graph.add((v2, DEC.supersedes, v1))
                new_regions[idx] = r2
                repaired.append((p, idx))
                adopted_any = True
            else:
                notes.append(f"page {p} band {idx}: section-repair pass-2 re-read still "
                             f"escalated ({r2.reason}); pass-1 report kept")
        if adopted_any:
            # the page's score is recomputed HONESTLY from the per-band token ledger the
            # compile now carries (RegionReport.tokens_*): the adopted bands' tokens moved
            # from escalated to (mostly) asserted, and the document score below inherits it.
            # final-review F5: a repaired band's peeled strip lines re-emit as
            # `tab:RegionCaption` (`_emit_band_captions`), NOT as cells — caption words never
            # entered `tokens_asserted`/`tokens_escalated` in pass 1 or pass 2, so they leave
            # this asserted+escalated denominator exactly as they always have: captions are
            # carried context, not table content.
            a = sum(r.tokens_asserted for r in new_regions)
            e = sum(r.tokens_escalated for r in new_regions)
            pages[p] = _dc_replace(pages[p], regions=tuple(new_regions), asserted=a,
                                   escalated=e, score=1.0 if (a + e) == 0 else a / (a + e))

    # §4.1 intra-page stitching: link ALL recognized members that ASSERT — band-level-asserted
    # and repaired alike, whichever route they took — in reading order, and feed the links into
    # loop M's OWN successor map, so the existing chain assembly (and loop N's arithmetic
    # riding it) builds the section chain with no second mechanism.
    section_facts = bool(repaired)
    for p, groups in page_section_groups:
        for grp in groups:
            uris = [pages[p].regions[i].table_uri for i in grp
                    if pages[p].regions[i].verdict == "asserted"
                    and pages[p].regions[i].table_uri is not None]
            for prev_uri, cur_uri in zip(uris, uris[1:]):
                if cur_uri in links or prev_uri in set(links.values()):
                    continue          # never fork loop M's successor map — refusal, not a guess
                graph.add((cur_uri, TAB.continuesTable, prev_uri))
                _link_columns(graph, cur_uri, prev_uri)
                links[cur_uri] = prev_uri
                section_facts = True

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

    # §4.0 TOTALS — the arithmetic section-boundary oracle, run over every recognized member
    # that asserted (repaired or not), AFTER the chain arithmetic so nothing it emits can be
    # swept by the reconciliation's retract-then-assert. See _confirm_section_total for the
    # law; refusals land in `notes`, associations in the graph — never both for one section.
    for p, groups in page_section_groups:
        for grp in groups:
            for i in grp:
                r = pages[p].regions[i]
                if r.verdict != "asserted" or r.table_uri is None:
                    continue
                confirmed, note = _confirm_section_total(graph, r.table_uri, band_lists[p][i])
                section_facts = section_facts or confirmed
                if note:
                    notes.append(f"page {p} band {i}: {note}")

    # WHOLE-GRAPH VALIDATION (task 4; see the docstring above for why the gate is `recognized`
    # rather than always-on — and, since loop Q, `section_facts` for exactly the same reason:
    # an adoption, an intra-page stitch or a section total puts document-level facts into the
    # merged graph that no per-page membrane ever saw). Every document-level fact is asserted
    # by this point: the pairing loop above added continuesTable/continuesColumn/
    # inLogicalColumn, the arithmetic pass retyped aggregations and rebuilt row groups over the
    # logical table, and the section pass added its adoptions, links and totals.
    if validate_shapes and (recognized or section_facts):
        conforms, text = _validate(graph)
        if not conforms:
            raise AssertionError(f"document-level facts failed tab: SHACL:\n{text}")

    asserted = sum(rep.asserted for rep in pages)
    escalated = sum(rep.escalated for rep in pages)
    denom = asserted + escalated
    score = 1.0 if denom == 0 else asserted / denom
    return DocumentReport(score, tuple(pages), tuple(chains), graph, tuple(recognized),
                          arithmetic, tuple(refused), tuple(repaired), tuple(notes))
