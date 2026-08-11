"""compile — the closing slice: PDF -> classify -> round-trip -> score + holon.

compile_tables runs the whole loop on one page and returns a CompilationReport
whose score is asserted_cells / (asserted + escalated) over table-candidate
regions. Non-table regions are reported but excluded from the ratio. Residue is
never dropped: every table-candidate region is asserted or escalated in-band.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph, URIRef, RDF

from .geometry import extract_words, text_lines
from .bands import detect_bands
from .regions import classify, RegionKind, column_of
from .roundtrip import cell_round_trips, render_ascii
from .holon import assert_record_region, escalate_region, TAB

_DOC = URIRef("https://example.org/etkl/doc")


def _tiles_rationale(tiles: bool, n: int, unit: str) -> str:
    """Formats the (tiles, n) pair a region_tiles gate call already produced into a
    diagnostic rationale distinct from the "tiles"/"does_not_tile" chosen label — pure
    formatting of state already computed at the call site, no judgement re-evaluated.

    `unit` names what `n` actually counts at THIS call site — the five assert_*_region
    functions do not all return the same kind of quantity. Four (assert_record_region,
    assert_transposed_region, assert_row_hier_region, assert_matrix_region) increment by
    1 per tab:EntryCell (holon.py:108,168,268,363) — "entries". assert_hier_region
    increments by len(cell.words) per cell (holon.py:482) — its own docstring
    (holon.py:382) calls this the "body-token count", so "body tokens" here, not
    "entries" — a cell with 2 words would otherwise be misreported as 2 entries."""
    return (f"region_tiles {'validated' if tiles else 'rejected'} "
            f"the {n} {unit} asserted into scratch")


# Which OTHER kind each `regions._reason` observation genuinely refutes (final-review C2).
# `_reason` (regions.py:88-98) returns a justification of the CHOSEN kind, NOT a per-option
# refutation, so broadcasting it onto every loser asserted observations the classifier never
# made (measured on apple page 0: 1 of 4 emitted refutations was true). What each observation
# actually says, read off `_reason`:
#   * NON_TABLE          -> "fewer than 2 lines" / "fewer than 2 columns": the band has no
#     table shape at all, which refutes BOTH table kinds.
#   * UNSUPPORTED_TABLE  -> "header has N words but M columns" / "header word 'X' is not
#     aligned 1:1 with column K": a header/column-ALIGNMENT observation, which is exactly what
#     separates the two TABLE kinds. It refutes RECORD_TABLE and says nothing whatever about
#     NON_TABLE (the band is a table either way).
#   * RECORD_TABLE       -> "flat single-level header": a POSITIVE justification of the winner.
#     It refutes nothing, so nothing is emitted — silence is the honest record (§7).
# A kind absent from a tuple carries no dec:rejectedBecause at all: the option is still in the
# dec:optionSpace (it was considered), it simply carries no refutation the reader ever made.
_KIND_REFUTED_BY_REASON = {
    "NON_TABLE": ("RECORD_TABLE", "UNSUPPORTED_TABLE"),
    "UNSUPPORTED_TABLE": ("RECORD_TABLE",),
    "RECORD_TABLE": (),
}


def _kind_refutations(chosen_name: str, reason: str | None) -> dict:
    """`{option name: the observation that genuinely refutes it}` for one kind judgement.

    Pure lookup over `_KIND_REFUTED_BY_REASON` — no judgement is re-evaluated here, and an
    absent reason yields no refutation at all."""
    if not reason:
        return {}
    return {name: reason for name in _KIND_REFUTED_BY_REASON.get(chosen_name, ())}


def _build_ruled_band(sub, sub_rules, sub_hrules, page_chars, section_repair=False):
    """Construct the Band for a RULED sub-band. THE SEAM for the no-synthesised-Rule guard:
    tests call this directly, so the guard exercises production code, not a copy (attempt 1's
    guard replicated this logic in its test body and was proven tautological).

    `section_repair` (loop Q Tasks 3-4, default False): False is byte-identical to before this
    parameter existed — the peel below reads grid_lines' default (band-level, MIN/MAX-x)
    interior test, vocab/queries/grid-region.rq, exactly as shipped, and the weld reads
    leading_hrule_box's full-width test exactly as shipped. True switches the repair pair on
    (spec §4.0's 'peel leading non-grid strips + weld the leading header box'): the SAME peel
    call reads the repair-scoped ink-witness variant (grid_lines(..., ink_witness=True) ->
    grid-region-ink.rq, salvaged from reverted b515283), and the SAME weld call falls back to
    the x-extent-free leading-box candidate (geometry.leading_box_y_fallback — Task 2's
    justified candidate rule, see the weld call site below) ONLY when the full-width test
    abstains, which is exactly what a doubled-edge border forces (measured: the CBH shape's
    hrules start strictly inside the border twins, so no hrule is ever full-width).
    Everything else in this function (the enclosed-lines guard, the leading-prefix rule in
    peel_leading_captions) is UNCHANGED, still reading `xs` (every rule x, not the
    ink-interior subset). Only `compile.page_bands` ever passes True, and only for a band
    index the caller's `section_repair_bands` names (loop Q Task 4 wires that from the
    driver's recognized, still-escalated repeat groups) — no other caller of this function is
    affected.

    Flow — every refusal exits to the author-bucketed band, i.e. main's behavior:
      author-bucketed lines -> candidate boundaries (geometry.refine_rule_columns) ->
      provisional grid + header/body split (locates the header region; computed on the
      AUTHOR-bucketed band so confirmation never depends on the candidates it judges) ->
      header-CONFIRMED boundaries (boundary.confirmed_boundaries, the confirm-boundary.rq AXIOM)
      -> re-bucket with author+confirmed and set Band.column_xs.

    sub_rules passes through UNTOUCHED — no Rule is ever synthesised; derived boundaries live
    only in Band.column_xs (the author's marks and the derived list are kept distinct on
    purpose). A single-row band has no header/body split, so nothing is ever confirmable there
    (closes attempt 1's single-row over-split structurally)."""
    from dataclasses import replace as _replace
    from .bands import Band
    from .geometry import refine_rule_columns, rule_aware_lines

    xs = sorted({round(r.x, 2) for r in sub_rules})

    # Loop P peel: full-width strips ABOVE the ruled grid (key headings, notices) are
    # never grid rows — split them off the WORD-based sub band (never rule-re-extracted)
    # BEFORE anything downstream reads sub.lines/sub.top, so they cannot leak into the
    # grid as fabricated all-column header levels. grid_lines is the AXIOM (interior-rule
    # presence, vocab/queries/grid-region.rq); this call site is the PROCEDURAL peel only.
    # Fix round 2 (regression repair): peel scope is a LEADING strip only (spec §3) —
    # peel_leading_captions leaves interior and TRAILING non-grid lines (e.g. a
    # below-grid total row) untouched in the band, main's byte-identical behavior. It
    # ALSO requires the leading run to be ENCLOSED by some rule's y-extent (measured:
    # "leading-only" alone still swallowed a floating merged-header row with no rule
    # near it, e.g. "Voyage" — see gridregion.peel_leading_captions's docstring).
    from .gridregion import grid_lines as _grid_lines, enclosed_lines as _enclosed_lines, \
        peel_leading_captions
    gset = _grid_lines(sub, sub_rules, ink_witness=section_repair)
    enclosed = _enclosed_lines(sub, sub_rules)
    caption_lines, kept_lines = peel_leading_captions(sub.lines, gset, enclosed)
    if caption_lines:
        sub = _replace(sub, lines=kept_lines, top=kept_lines[0].top)

    band_chars = [c for c in page_chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
    relines = rule_aware_lines(band_chars, xs) if len(xs) >= 2 else []
    if relines:
        from .geometry import weld_hrule_boxes
        # Loop Q Task 4 — the WELD half of the §4.0 repair ("peel leading non-grid strips
        # + weld the leading header box"). A doubled-edge border defeats leading_hrule_box's
        # full-width test (the hrules start strictly inside the border twins, measured on
        # the CBH shape), so under section_repair ONLY, when that test abstains, the weld
        # reads sectiongraph's x-extent-free candidate instead (geometry.
        # leading_box_y_fallback — same §8 posture: a PROCEDURAL candidate whose disposal
        # is the region membrane the pass-2 re-read must still pass; a wrong candidate
        # welds a wrong header row, which the tiling shapes then refuse — escalation, never
        # a false assertion). The default path passes box=None: byte-identical to shipped.
        weld_box = None
        if section_repair:
            from .geometry import leading_hrule_box, leading_box_y_fallback
            if leading_hrule_box(sub_hrules, xs) is None:
                weld_box = leading_box_y_fallback(sub_hrules)
        relines = weld_hrule_boxes(relines, sub_hrules, xs, box=weld_box)
    if not relines:
        return _replace(sub, rules=sub_rules, hrules=sub_hrules, captions=caption_lines)
    band = Band(tuple(relines), sub.top, sub.bottom, sub_rules, sub_hrules, captions=caption_lines)

    candidates = [x for x in refine_rule_columns(band_chars, xs) if x not in xs]
    if not candidates:
        return band
    from .cells import recover_leaf_grid
    from .headers import header_body_split
    try:
        grid = recover_leaf_grid(band)
    except ValueError:
        # verified: recover_leaf_grid's only fallible path is infer_leaf_grid, which raises
        # ValueError ONLY ("band has no words") — nothing else escapes here. That matters
        # because recover_leaf_grid/header_body_split now run earlier in the pipeline than on
        # main (main never called them from this seam); if either ever raised a DIFFERENT
        # exception type it would propagate up and abort the whole compile, where main had
        # not yet touched these functions at this point and so could not have aborted here.
        return band
    if grid.ncols < 2:
        return band
    split = header_body_split(band, grid)
    if split is None or not (1 <= split < len(band.lines)):
        return band                        # no header region -> nothing can be confirmed
    body_top = band.lines[split].top
    # verified invariant (do not "fix" this into a tolerance): Line.top is the MIN ink-char top
    # over the chars on that line, so every ink char belonging to a line at or below the split
    # has a center strictly greater than body_top — a body char can NEVER leak into the header
    # evidence via this midpoint filter. Checked on both measured documents: the filter selected
    # exactly the chars of band.lines[:split], 12/12 and 262/262.
    header_glyphs = [c for c in band_chars
                     if c.text.strip() and (c.top + c.bottom) / 2.0 < body_top]
    from .boundary import confirmed_boundaries
    triples = []
    for bx in candidates:
        lo = max(x for x in xs if x < bx)
        hi = min(x for x in xs if x > bx)
        triples.append((bx, lo, hi))
    confirmed = confirmed_boundaries(header_glyphs, triples)
    if not confirmed:
        return band
    col_xs = sorted(set(xs) | confirmed)
    relines2 = rule_aware_lines(band_chars, col_xs)
    if not relines2:
        return band
    return Band(tuple(relines2), sub.top, sub.bottom, sub_rules, sub_hrules, tuple(col_xs),
               captions=caption_lines)


def _emit_band_captions(graph, table_uri, band):
    """Loop P §5/§7 carry: one tab:RegionCaption per peeled strip line. captionRow is
    the line's index within the ORIGINAL band (captions precede the grid, so their
    order is their index).

    ALSO typed tab:SectionCaption (fix round, 2026-08-04, stem-pollution close): this is
    THE emitter for a peeled leading strip above a grid — the only kind of caption a
    section repair (or the ordinary leading-peel this function has always served) ever
    produces — and feed.py now reads ONLY tab:SectionCaption as candidate-key evidence.
    Loop C's row-role reading-furniture captions (rowrole.emit_reading_evidence, a
    print-timestamp/title line inside a header region) are a DIFFERENT emitter and stay
    tab:RegionCaption only — untouched by this change, never a candidate key."""
    from rdflib import Literal, RDF, URIRef
    from rdflib.namespace import XSD
    for k, ln in enumerate(getattr(band, "captions", ()) or ()):
        cap = URIRef("%s-bandcap%d" % (table_uri, k))
        graph.add((cap, RDF.type, TAB.RegionCaption))
        graph.add((cap, RDF.type, TAB.SectionCaption))
        graph.add((cap, TAB.captionText, Literal(" ".join(w.text for w in ln.words))))
        graph.add((cap, TAB.captionRow, Literal(k, datatype=XSD.integer)))
        graph.add((table_uri, TAB.hasCaption, cap))


def _emit_unit_markers(graph, table_uri, band, boundaries):
    """Spec 2026-08-05 §4 carry: one tab:UnitMarker per absorbed currency-marker
    column, attached to the SURVIVING neighbor column's URI (resolved against the
    FINAL grid boundaries via the carried neighbor_x). Provenance rides
    tab:markerRegion -> tab:BBox — deliberately NOT tab:hasBBox, whose rdfs:domain
    would type the marker as tab:Cell and trip WrappedCellShape at the gate (R19).

    `boundaries=None` (fix round 1, transposed branch ONLY): assert_transposed_region
    mints its `{table_uri}-c{k}` leaf-column URIs keyed by PHYSICAL ROW index (the axis
    flip — logical column k <- physical row k), while column_of(neighbor_x, boundaries)
    would resolve a PHYSICAL COLUMN index — a different axis entirely. Reusing that index
    against the flipped leaf columns would attach the marker to a coincidentally-numbered,
    semantically unrelated column: a false claim the evidence does not support. Rather
    than assert a mapping across an axis the flip does not preserve, a caller passing
    boundaries=None gets the marker attached to the TABLE itself instead — still carries
    the ink (CLAUDE.md §5: context is carried, not discarded), makes no column claim.
    Unmeasured shape: no document seen so far exhibits a marker column in a transposed
    table."""
    from rdflib import Literal, RDF, URIRef
    from rdflib.namespace import XSD
    for k, (sym, neighbor_x, regions) in enumerate(getattr(band, "unit_markers", ()) or ()):
        um = URIRef("%s-um%d" % (table_uri, k))
        graph.add((um, RDF.type, TAB.UnitMarker))
        graph.add((um, TAB.markerSymbol, Literal(sym)))
        for j, (x0, top, x1, bottom) in enumerate(regions):
            bb = URIRef("%s-um%d-r%d" % (table_uri, k, j))
            graph.add((bb, RDF.type, TAB.BBox))
            graph.add((bb, TAB.x0, Literal(float(x0), datatype=XSD.decimal)))
            graph.add((bb, TAB.y0, Literal(float(top), datatype=XSD.decimal)))
            graph.add((bb, TAB.x1, Literal(float(x1), datatype=XSD.decimal)))
            graph.add((bb, TAB.y1, Literal(float(bottom), datatype=XSD.decimal)))
            graph.add((um, TAB.markerRegion, bb))
        if boundaries is None:
            graph.add((table_uri, TAB.hasUnitMarker, um))
        else:
            col = column_of(neighbor_x, boundaries)
            graph.add((URIRef("%s-c%d" % (table_uri, col)), TAB.hasUnitMarker, um))


def _marker_word_count(band) -> int:
    """Final-review fix (C1): one accounted word per carried glyph region — the same
    unit an asserted branch counts (len(cell.words)). Used to restore token-accounting
    parity on an escalation/ignored path, where the marker ink is carried into the
    graph (via _emit_unit_markers, attached to the region/table node) but was never
    part of a Cell the round-trip accounting already counts."""
    return sum(len(m[2]) for m in getattr(band, "unit_markers", ()) or ())


def page_bands(pdf_path: str, page_number: int = 0,
               section_repair_bands: frozenset[int] | None = None):
    """The page's bands, exactly as compile_tables reads them (band i here IS band i there).

    THE SEAM for loop M's document driver: continuation recognition must read the SAME bands the
    compile reads, or the recognized band and the compiled table are two different things and the
    chain links the wrong URIs. Extracted verbatim from compile_tables (which now calls it), so
    there is one band-construction path, not a copy that can drift.

    BAND-INDEX ENUMERATION (loop Q Task 3, stated precisely since this is the load-bearing
    contract for `section_repair_bands`): the index at which a band ends up in the `bands` list
    THIS function returns is `len(bands)` at the moment of its append below — i.e. its final
    position in append order, for a RULED band exactly as much as an unruled one (every sub-band
    consumes one index, ruled or not). `compile_tables` calls `page_bands` and then enumerates
    that SAME returned list unchanged (`for idx, band in enumerate(bands)`), so an index in
    `section_repair_bands` names the identical band both here (feeding `_build_ruled_band`'s
    `section_repair` flag) and in the driver's per-band verdict/report — there is exactly one
    band-construction path and exactly one indexing scheme, never two that could drift apart.
    `section_repair_bands=None` (the default) is falsy for every index, so every band builds with
    `section_repair=False` — byte-identical to before this parameter existed.

    Disambiguation (review round 1, minor): "the driver's per-band verdict/report" above means
    THIS function's own caller, `compile_tables`'s per-PAGE loop (`for idx, band in
    enumerate(bands)`) — NOT `document.py`'s multi-PAGE driver, which enumerates pages, not
    bands, and (loop Q Task 4) will compute a fresh `section_repair_bands` per page from
    `sectiongraph.section_candidates` before calling `compile_tables` again for that page's
    pass-2 read. The index space this docstring pins is always page-local.
    """
    from .geometry import extract_rules, extract_chars, extract_hrules
    from dataclasses import replace as _replace
    from .segment import segment
    words = extract_words(pdf_path, page_number)
    page_rules = extract_rules(pdf_path, page_number)
    page_hrules = extract_hrules(pdf_path, page_number)
    page_chars = extract_chars(pdf_path, page_number) if page_rules else []
    raw_bands = detect_bands(text_lines(words))
    bands = []
    for band in raw_bands:
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules if r.top <= sub.bottom and r.bottom >= sub.top)
            sub_hrules = tuple(h for h in page_hrules if sub.top <= h.y <= sub.bottom)
            idx = len(bands)             # the position this band is about to occupy
            if not sub_rules:
                bands.append(_replace(sub, hrules=sub_hrules) if sub_hrules else sub)
                continue
            # RULED band: re-extract cells by the ruled columns (splits pdfplumber-merged blobs at
            # the author's exact boundaries) — else keep pdfplumber's words. Candidate boundaries
            # become columns only when the header confirms them (_build_ruled_band, the seam).
            section_repair = bool(section_repair_bands) and idx in section_repair_bands
            bands.append(_build_ruled_band(sub, sub_rules, sub_hrules, page_chars,
                                           section_repair=section_repair))
    from .unitmarker import absorb_unit_markers
    bands = [absorb_unit_markers(b) for b in bands]
    return bands


@dataclass(frozen=True)
class RegionReport:
    kind: RegionKind
    # "asserted" | "escalated" | "ignored" | "superseded". The fourth is written only by the
    # R73 adoption branch below, and only over a band that had booked escalated tokens whose ink
    # the adopted data grid then read: the band's own record no longer describes what happened to
    # that ink, so it neither escalates (the grid read it) nor asserts (this band did not read
    # it). Its tokens move to the grid region and to the DATAGRID_RESIDUE region, which is why a
    # "superseded" report always carries tokens_escalated == 0.
    verdict: str
    cells: int                 # asserted entry-cell count (0 otherwise)
    reason: str | None
    anchor: str | None
    ascii: str
    # The URI of the table holon this band was compiled into, or None when nothing was asserted
    # (escalated/ignored bands have no table). Loop M's document driver reads it to link
    # continuation chains without having to guess the URI a branch happened to mint.
    table_uri: URIRef | None = None
    # The band's CONFIRMED header-block reading (ruledroles.CarriedHeaderReading), or None when
    # this band's reading did not come from the loop-L law (every other branch, unchanged). Loop
    # M's driver carries it onto the next page when the continuation AXIOM licenses the pair —
    # it is never read for any other purpose, so a None here only means "nothing to carry".
    header_reading: object | None = None
    # THIS band's own contribution to the page's asserted/escalated token totals (loop Q Task 4).
    # Recorded by DIFFERENCING the running totals around each band's turn of the loop below —
    # never a re-derivation, so the invariant sum(r.tokens_*) == CompilationReport.asserted/
    # escalated holds by construction. The document driver's section repair needs it to
    # recompute a page's score honestly after swapping ONE band's report for its pass-2 re-read
    # (the page aggregates alone cannot be split back into per-band contributions).
    tokens_asserted: int = 0
    tokens_escalated: int = 0


@dataclass(frozen=True)
class CompilationReport:
    score: float
    regions: tuple[RegionReport, ...]
    graph: Graph
    # The score's own operands, kept so a caller can re-aggregate over several pages: a document
    # score is asserted/(asserted+escalated) over the WHOLE document, which cannot be recovered
    # from per-page ratios (loop M).
    asserted: int = 0
    escalated: int = 0

    def to_turtle(self) -> str:
        return self.graph.serialize(format="turtle")


def _repo_vocab():
    """Locate vocab/ by walking up from this file (works in-repo/dev checkout)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        cand = os.path.join(d, "vocab")
        if os.path.isdir(cand):
            return cand
        d = os.path.dirname(d)
    raise FileNotFoundError("vocab/ not found (needed for SHACL validation)")


_TAB_SHAPES = None
_DEC_SHAPES = None
_FULL_ONT = None

# The membrane's shape set, split by which ENGINE may evaluate it (spec 2026-08-10 §5.4).
# `_DEC_SHAPES` is pinned to pySHACL: both files carry an `sh:sparql` constraint and the
# promotion emitters mint blank-node subjects, which rudof provably cannot evaluate — see
# `membrane.validate`'s docstring for the measurement. The split is per shape SET, never per
# graph: no verdict depends on what happens to be in the data.
_TAB_SHAPE_FILES = ("tab-shapes.ttl", "tab-physical-shapes.ttl")
_DEC_SHAPE_FILES = ("dec-shapes.ttl", "iladub-shapes.ttl")
_DEC_ENGINE = "pyshacl"


def _build_membrane():
    global _TAB_SHAPES, _DEC_SHAPES, _FULL_ONT
    v = _repo_vocab()

    def _shapes(names):
        g = Graph()
        for n in names:
            g.parse(os.path.join(v, "shapes", n), format="turtle")
        return g

    _TAB_SHAPES = _shapes(_TAB_SHAPE_FILES)
    # R82: the membrane validates the DECISION graph too, not only the tab graph. A page
    # carrying an iladub:PromotionDecision with no deliberated option space used to cross
    # here unchallenged, which made "every grounded node is produced by an accountable
    # promotion decision" a claim rather than an enforced fact.
    _DEC_SHAPES = _shapes(_DEC_SHAPE_FILES)
    o = Graph()
    o.parse(os.path.join(v, "ontology", "tab.ttl"), format="turtle")
    # LOAD-BEARING, not decoration: the promotion shapes target dec:DecisionHolon, and only
    # `iladub:PromotionDecision rdfs:subClassOf dec:DecisionHolon` (iladub.ttl) puts an
    # emitted promotion under that target once the subclass closure runs. Without these two
    # files the dec shapes are parsed and target nothing at all.
    #
    # MEASURED (2026-08-10), because enlarging the ontology also enlarges the closure the TAB
    # shapes see: all 7 corpus documents were compiled once and validated twice against the
    # tab shapes alone — with tab.ttl, then with tab.ttl+dec.ttl+iladub.ttl. Every verdict was
    # (conforms=True, 0 refusing focus nodes, 0 results) both times. No tab verdict moves,
    # which is why ONE ontology graph serves both legs.
    o.parse(os.path.join(v, "ontology", "dec.ttl"), format="turtle")
    o.parse(os.path.join(v, "ontology", "iladub.ttl"), format="turtle")
    _FULL_ONT = o


def _validate(graph: Graph) -> tuple[bool, str]:
    if _TAB_SHAPES is None:
        _build_membrane()
    from . import membrane
    # BOTH legs always run, even when the first refuses: a membrane that reported only the
    # first failing shape set would make a page look like a tab defect when it is also a
    # promotion defect, and the caller raises on the combined verdict either way.
    tab_ok, tab_report = membrane.validate(graph, _TAB_SHAPES, _FULL_ONT)
    dec_ok, dec_report = membrane.validate(graph, _DEC_SHAPES, _FULL_ONT, engine=_DEC_ENGINE)
    if tab_ok and dec_ok:
        return True, tab_report
    return False, "\n".join(r for ok, r in ((tab_ok, tab_report), (dec_ok, dec_report))
                            if not ok)


def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True, span_proposer=None,
                   row_role_proposer=None, doc_uri: URIRef | None = None,
                   carried_header_roles: dict | None = None,
                   section_repair_bands: frozenset[int] | None = None,
                   datagrid_fallback: bool = True,
                   datagrid_adopt: bool = False) -> CompilationReport:
    """Compile one page. `doc_uri` names the document holon every URI this page mints hangs off;
    it defaults to `_DOC`, so a single-page call is byte-identical to before. Loop M's driver
    passes a PAGE-SCOPED URI (`{_DOC}/p{n}`) because two pages of one document otherwise mint the
    same `doc#table0` and their graphs collide when merged.

    `carried_header_roles` (loop M task 3) is `{band index on THIS page: CarriedHeaderReading}` —
    the previous page's CONFIRMED header-block reading, to be carried onto that band. The driver
    passes an entry ONLY for a band the continuation AXIOM recognized as continuing the previous
    page's table, so carriage cannot reach an unrecognized page at all: a caller that passes
    nothing (every single-page call, and every unrecognized page) gets exactly the pre-loop-M
    behaviour. What the carriage may then do at the band is stated in
    ruledroles.resolve_ruled_header_rows; it still has to pass the same SHACL tiling oracle.

    CARRIAGE IS ONLY SOUND WHERE CONTINUATION RECOGNITION LICENSED IT (review finding F3, stated
    here because this is a PUBLIC parameter and nothing in this signature enforces it): handing in
    a reading for a band that `document.compile_document`'s continuation AXIOM did not license
    means asserting one table's header reading over another table's rows. The in-repo call graph
    upholds the invariant — `compile_document` is the only producer, and it keys the map by the
    recognized band — but an external caller can bypass it. Registered as part of residue R34.

    `section_repair_bands` (loop Q Task 3, keyword-only, default None): forwarded verbatim to
    `page_bands` — see its docstring for the exact band-index enumeration this parameter names
    (the SAME index the `for idx, band in enumerate(bands)` loop just below uses, since `bands`
    here IS `page_bands`' returned list, unmodified). None (the default — every caller before
    this parameter existed, and every caller that omits it) makes `page_bands` build every band
    with `section_repair=False`, byte-identical to before."""
    from .segment import is_multi_table_ambiguous
    doc = _DOC if doc_uri is None else doc_uri
    bands = page_bands(pdf_path, page_number, section_repair_bands=section_repair_bands)
    graph = Graph()
    from .decisionlog import ReadingRecorder
    recorder = ReadingRecorder(graph, doc, page_number)
    reports: list[RegionReport] = []
    asserted_total = escalated_total = 0

    # Per-band token accounting (loop Q Task 4): snapshot the running totals at the TOP of each
    # band's turn (the one point every branch passes through — `continue` never skips it), close
    # with a sentinel after the loop, and difference. Every branch appends exactly one report per
    # band, so band_marks[i+1] - band_marks[i] IS band i's own contribution, exactly.
    band_marks: list[tuple[int, int]] = []

    for idx, band in enumerate(bands):
        band_marks.append((asserted_total, escalated_total))
        brec = recorder.band(idx)
        ascii_view = render_ascii(band)
        multi_table = is_multi_table_ambiguous(band)
        brec.record("multi_table", ["single", "multi"],
                    "multi" if multi_table else "single",
                    "MULTI_TABLE_AMBIGUOUS" if multi_table else "single table")
        if multi_table:
            cand_uri = URIRef(f"{doc}#region{idx}")
            escalate_region(graph, cand_uri, doc, ascii_view, "MULTI_TABLE_AMBIGUOUS",
                            TAB.HierarchicalTable, 0.4, page_number)
            if getattr(band, "unit_markers", ()):
                _emit_unit_markers(graph, cand_uri, band, None)
                escalated_total += _marker_word_count(band)
            escalated_total += sum(len(ln.words) for ln in band.lines)
            brec.record("verdict", ["asserted", "escalated", "ignored"],
                        "escalated", "MULTI_TABLE_AMBIGUOUS")
            reports.append(RegionReport(RegionKind.UNSUPPORTED_TABLE, "escalated", 0,
                                        "MULTI_TABLE_AMBIGUOUS", str(TAB.HierarchicalTable), ascii_view))
            continue
        region = classify(band)
        _kind_options = ["RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"]
        brec.record("kind", _kind_options, region.kind.name, region.reason or "",
                    rejected=_kind_refutations(region.kind.name, region.reason))

        if region.kind is RegionKind.NON_TABLE:
            if getattr(band, "unit_markers", ()):
                # C1 fix: an ignored band never contributed to the score, so no
                # accounting change — only the invariant "absorbed ink always lands
                # in the graph with provenance" applies here.
                cand_uri = URIRef(f"{doc}#region{idx}")
                _emit_unit_markers(graph, cand_uri, band, None)
            brec.record("verdict", ["asserted", "escalated", "ignored"], "ignored", "")
            reports.append(RegionReport(region.kind, "ignored", 0,
                                        region.reason, None, ascii_view))
            continue

        if region.kind is RegionKind.RECORD_TABLE:
            from .orientation import looks_transposed, transpose_is_coherent
            from .rowheaders import looks_row_grouped
            is_transposed = looks_transposed(region)
            brec.record("transposed", ["upright", "transposed"],
                        "transposed" if is_transposed else "upright",
                        "looks transposed" if is_transposed else "upright")
            if is_transposed:
                is_coherent = transpose_is_coherent(region)
                brec.record("transpose_coherent", ["coherent", "incoherent"],
                            "coherent" if is_coherent else "incoherent",
                            "coherence oracle accepted the transposed reading"
                            if is_coherent else
                            "coherence oracle refused the transposed reading")
                if is_coherent:
                    # compile by axis-flip: records run along columns -> a correct,
                    # un-inverted RecordTable (tab:sourceOrientation "transposed").
                    from .holon import assert_transposed_region
                    from .tiling import region_tiles
                    table_uri = URIRef(f"{doc}#ttable{idx}")
                    # R17 gate (loop J): scratch -> region_tiles -> commit-or-escalate, the
                    # same backstop as the hierarchical/matrix/row-hier paths. A defective
                    # region escalates in-band instead of crashing final validation.
                    scratch = Graph()
                    n = assert_transposed_region(scratch, region, table_uri, doc, page_number)
                    tiles = region_tiles(scratch) if n else None
                    if tiles is not None:
                        brec.record("region_tiles", ["tiles", "does_not_tile"],
                                    "tiles" if tiles else "does_not_tile",
                                    _tiles_rationale(tiles, n, "entries"))
                    if n and not tiles:
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view,
                                        "REGION_TILING_FAILED", TAB.RecordTable, 0.4, page_number)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "escalated", "REGION_TILING_FAILED")
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.RecordTable), ascii_view))
                    else:
                        graph += scratch
                        _emit_band_captions(graph, table_uri, band)
                        # fix round 1: this branch's leaf-column URIs are keyed by PHYSICAL
                        # ROW (the axis flip — see assert_transposed_region), not physical
                        # column, so column_of(neighbor_x, region.grid.boundaries) would name
                        # the wrong axis entirely. boundaries=None attaches the marker to the
                        # table instead of asserting an unsupported column mapping.
                        _emit_unit_markers(graph, table_uri, band, None)
                        b = region.grid.boundaries
                        value_cells = [c for c in region.cells if c.col >= 1]
                        asserted_total += sum(len(c.words) for c in value_cells if cell_round_trips(c, b))
                        escalated_total += sum(len(c.words) for c in value_cells if not cell_round_trips(c, b))
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "asserted", "")
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.RecordTable), ascii_view,
                                                    table_uri))
                else:
                    # detected but not confidently compilable — escalate (Loop 3 behaviour)
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view, "TRANSPOSED",
                                    TAB.TransposedTable, 0.4, page_number)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    brec.record("verdict", ["asserted", "escalated", "ignored"],
                                "escalated", "TRANSPOSED")
                    reports.append(RegionReport(region.kind, "escalated", 0, "TRANSPOSED",
                                                str(TAB.TransposedTable), ascii_view))
            else:
                is_row_grouped = looks_row_grouped(region)
                brec.record("row_grouped", ["flat", "row_grouped"],
                            "row_grouped" if is_row_grouped else "flat",
                            "row-grouping oracle read repeated row labels as record groups"
                            if is_row_grouped else
                            "row-grouping oracle found no repeated row-label groups")
                if is_row_grouped:
                    from .rowheaders import classify_row_hier
                    from .holon import assert_row_hier_region
                    from .tiling import region_tiles
                    rreg = classify_row_hier(band)
                    table_uri = URIRef(f"{doc}#rhtable{idx}")
                    scratch = Graph()
                    if rreg is not None:
                        n = assert_row_hier_region(scratch, rreg, band, table_uri, doc, page_number)
                    tiles = region_tiles(scratch) if rreg is not None else None
                    if tiles is not None:
                        brec.record("region_tiles", ["tiles", "does_not_tile"],
                                    "tiles" if tiles else "does_not_tile",
                                    _tiles_rationale(tiles, n, "entries"))
                    if rreg is not None and tiles:
                        graph += scratch
                        _emit_band_captions(graph, table_uri, band)
                        _emit_unit_markers(graph, table_uri, band, rreg.grid.boundaries)
                        b = rreg.grid.boundaries
                        for rb in rreg.leaf_rows:
                            for c in rb.cells:
                                col = column_of((c.x0 + c.x1) / 2.0, b)
                                if col in rreg.data_cols:
                                    fits = all(b[col] - 0.5 <= w.x0 and w.x1 <= b[col + 1] + 0.5 for w in c.words)
                                    (asserted_total, escalated_total) = (
                                        (asserted_total + len(c.words), escalated_total) if fits
                                        else (asserted_total, escalated_total + len(c.words)))
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "asserted", "")
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.HierarchicalTable), ascii_view,
                                                    table_uri))
                    else:
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view, "ROW_GROUP_AMBIGUOUS",
                                        TAB.HierarchicalTable, 0.4, page_number)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "escalated", "ROW_GROUP_AMBIGUOUS")
                        reports.append(RegionReport(region.kind, "escalated", 0, "ROW_GROUP_AMBIGUOUS",
                                                    str(TAB.HierarchicalTable), ascii_view))
                else:
                    # ---- existing RECORD_TABLE assert logic ----
                    from .tiling import region_tiles
                    table_uri = URIRef(f"{doc}#table{idx}")
                    # R17 gate (loop J): see the transposed branch above.
                    scratch = Graph()
                    n = assert_record_region(scratch, region, table_uri, doc, page_number)
                    tiles = region_tiles(scratch) if n else None
                    if tiles is not None:
                        brec.record("region_tiles", ["tiles", "does_not_tile"],
                                    "tiles" if tiles else "does_not_tile",
                                    _tiles_rationale(tiles, n, "entries"))
                    if n and not tiles:
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view,
                                        "REGION_TILING_FAILED", TAB.RecordTable, 0.4, page_number)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "escalated", "REGION_TILING_FAILED")
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.RecordTable), ascii_view))
                    else:
                        graph += scratch
                        _emit_band_captions(graph, table_uri, band)
                        _emit_unit_markers(graph, table_uri, band, region.grid.boundaries)
                        b = region.grid.boundaries
                        data_cells = [c for c in region.cells if c.row > 0]
                        asserted_total += sum(len(c.words) for c in data_cells if cell_round_trips(c, b))
                        escalated_total += sum(len(c.words) for c in data_cells if not cell_round_trips(c, b))
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "asserted", "")
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.RecordTable), ascii_view,
                                                    table_uri))
        else:  # UNSUPPORTED_TABLE
            from .matrix import is_matrix_candidate
            is_matrix = is_matrix_candidate(band)
            brec.record("matrix_candidate", ["matrix", "not_matrix"],
                        "matrix" if is_matrix else "not_matrix",
                        "matrix-candidacy oracle read the band as a two-axis matrix header"
                        if is_matrix else
                        "matrix-candidacy oracle found no two-axis matrix header structure")
            if is_matrix:
                from .matrix import classify_matrix
                from .holon import assert_matrix_region
                from .tiling import region_tiles
                mreg = classify_matrix(band)
                table_uri = URIRef(f"{doc}#mtable{idx}")
                scratch = Graph()
                if mreg is not None:
                    n = assert_matrix_region(scratch, mreg, band, table_uri, doc, page_number)
                tiles = region_tiles(scratch) if mreg is not None else None
                if tiles is not None:
                    brec.record("region_tiles", ["tiles", "does_not_tile"],
                                "tiles" if tiles else "does_not_tile",
                                _tiles_rationale(tiles, n, "entries"))
                if mreg is not None and tiles:
                    graph += scratch
                    _emit_band_captions(graph, table_uri, band)
                    _emit_unit_markers(graph, table_uri, band, mreg.grid.boundaries)
                    b = mreg.grid.boundaries
                    for rb in mreg.leaf_rows:
                        for sc in rb.cells:
                            col = column_of((sc.x0 + sc.x1) / 2.0, b)
                            if col in mreg.data_cols:
                                fits = all(b[col] - 0.5 <= w.x0 and w.x1 <= b[col + 1] + 0.5 for w in sc.words)
                                if fits:
                                    asserted_total += len(sc.words)
                                else:
                                    escalated_total += len(sc.words)
                    brec.record("verdict", ["asserted", "escalated", "ignored"],
                                "asserted", "")
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.HierarchicalTable), ascii_view,
                                                table_uri))
                else:
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view, "MATRIX_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4, page_number)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    brec.record("verdict", ["asserted", "escalated", "ignored"],
                                "escalated", "MATRIX_AMBIGUOUS")
                    reports.append(RegionReport(region.kind, "escalated", 0, "MATRIX_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
            else:
                # ---- existing Loop 2 hierarchical path, UNCHANGED ----
                from .hierarchical import classify_hierarchical
                from .holon import assert_hier_region
                hreg = classify_hierarchical(band)
                brec.record("hierarchical", ["hierarchical", "not_hierarchical"],
                            "hierarchical" if hreg is not None else "not_hierarchical",
                            f"hierarchical oracle inferred a {len(hreg.tree)}-node header tree"
                            if hreg is not None else
                            "hierarchical oracle inferred no header tree")
                from .headers import merge_tiling_ok
                # LOOP L (AXIOM) — the header-stack law. Under RULED evidence the author drew the
                # columns, so which header row is the leaf and what each row above it is are FACTS
                # (vocab/queries/header-row-role.rq), not reading judgments. Tried FIRST because a
                # derivable answer outranks a proposal (§8: the default is semantic). It abstains
                # unless the band is ruled, the leaf row aligns 1:1 with the ruled columns, and the
                # derived reading passes the SHACL tiling+conservation oracle — so every borderless
                # region, and every ruled region whose rows are all genuine levels, reaches the
                # unchanged branches below exactly as before.
                ruled_reading = None
                if hreg is not None:
                    from .ruledroles import resolve_ruled_header_rows
                    table_uri = URIRef(f"{doc}#htable{idx}")
                    ruled_scratch = Graph()
                    # LOOP M: the carried reading, present only for a band the continuation AXIOM
                    # recognized (see the parameter's docstring). `.get` is the whole guard —
                    # every other band, and every page the driver did not recognize, passes None.
                    ruled_reading = resolve_ruled_header_rows(
                        ruled_scratch, hreg, band, table_uri, doc, page_number,
                        carried=(carried_header_roles or {}).get(idx))
                if ruled_reading is not None:
                    n_ruled, reading = ruled_reading
                    graph += ruled_scratch
                    _emit_band_captions(graph, table_uri, band)
                    _emit_unit_markers(graph, table_uri, band, hreg.grid.boundaries)
                    tokens = sum(len(ln.words) for ln in band.lines)
                    asserted_total += n_ruled
                    escalated_total += max(0, tokens - n_ruled)
                    brec.record("verdict", ["asserted", "escalated", "ignored"],
                                "asserted", "")
                    reports.append(RegionReport(region.kind, "asserted", n_ruled, None,
                                                str(TAB.HierarchicalTable), ascii_view,
                                                table_uri, reading))
                elif hreg is not None and not merge_tiling_ok(hreg.tree, hreg.grid):
                    table_uri = URIRef(f"{doc}#htable{idx}")
                    resolved = None
                    if span_proposer is not None:
                        from .span import resolve_ambiguous_merge
                        resolved = resolve_ambiguous_merge(
                            graph, hreg, band, table_uri, doc, page_number, span_proposer)
                    if resolved is None and row_role_proposer is not None:
                        # Loop C NEURAL slice. The narrow-flank resolver keeps priority: it fires
                        # on an explicit ambiguous_flank flag, a strictly narrower trigger. This
                        # handles the general tiling failure (caption / wrap-continuation rows).
                        from .rowrole import resolve_header_row_roles
                        resolved = resolve_header_row_roles(
                            graph, hreg, band, table_uri, doc, page_number, row_role_proposer)
                    if resolved is not None:
                        n, _promos = resolved
                        _emit_band_captions(graph, table_uri, band)
                        _emit_unit_markers(graph, table_uri, band, hreg.grid.boundaries)
                        tokens = sum(len(ln.words) for ln in band.lines)
                        asserted_total += n
                        escalated_total += max(0, tokens - n)
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "asserted", "")
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.HierarchicalTable), ascii_view,
                                                    table_uri))
                    else:
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view, "MERGE_AMBIGUOUS",
                                        TAB.HierarchicalTable, 0.4, page_number)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "escalated", "MERGE_AMBIGUOUS")
                        reports.append(RegionReport(region.kind, "escalated", 0, "MERGE_AMBIGUOUS",
                                                    str(TAB.HierarchicalTable), ascii_view))
                elif hreg is not None:
                    table_uri = URIRef(f"{doc}#htable{idx}")
                    # THE MEMBRANE BACKSTOP (loop G attempt 2): assert into a SCRATCH graph and
                    # let region_tiles dispose it, exactly as the matrix and row-hier paths
                    # already do. The PLAIN HIERARCHICAL path wrote directly into the graph —
                    # which is why a defective region here CRASHED compile_tables at final
                    # validation (attempt 1's counter-example) instead of escalating.
                    # Loop J closed R17: the record and transposed paths now carry the same gate.
                    from .tiling import region_tiles
                    scratch = Graph()
                    n = assert_hier_region(scratch, hreg, band, table_uri, doc, page_number)
                    tiles = region_tiles(scratch) if n else None
                    if tiles is not None:
                        brec.record("region_tiles", ["tiles", "does_not_tile"],
                                    "tiles" if tiles else "does_not_tile",
                                    _tiles_rationale(tiles, n, "body tokens"))
                    if n and not tiles:
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view,
                                        "REGION_TILING_FAILED", TAB.HierarchicalTable, 0.4, page_number)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "escalated", "REGION_TILING_FAILED")
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.HierarchicalTable), ascii_view))
                    else:
                        # n == 0 keeps main's behavior byte-identical: assert_hier_region already
                        # wrote its ROUND_TRIP_FAIL escalation into scratch; merge and report as
                        # before. A tiling region merges exactly as it always did.
                        graph += scratch
                        if n:
                            _emit_band_captions(graph, table_uri, band)
                            _emit_unit_markers(graph, table_uri, band, hreg.grid.boundaries)
                        tokens = sum(len(ln.words) for ln in band.lines)
                        asserted_total += n
                        escalated_total += max(0, tokens - n)
                        # No escalate_region() call on this path (n == 0 short-circuits the
                        # gate above), so the honest rationale is "" even when the verdict
                        # itself is "escalated" (ROUND_TRIP_FAIL never reaches escalate_region).
                        brec.record("verdict", ["asserted", "escalated", "ignored"],
                                    "asserted" if n else "escalated", "")
                        reports.append(RegionReport(
                            region.kind,
                            "asserted" if n else "escalated",
                            n,
                            None if n else "ROUND_TRIP_FAIL",
                            str(TAB.HierarchicalTable),
                            ascii_view,
                            table_uri if n else None,
                        ))
                else:
                    # Not hierarchical — escalate whole region in-band
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view,
                                    reason="KIND_NOT_SUPPORTED",
                                    anchor=TAB.HierarchicalTable, confidence=0.4, page=page_number)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    tokens = sum(len(ln.words) for ln in band.lines)
                    escalated_total += tokens
                    brec.record("verdict", ["asserted", "escalated", "ignored"],
                                "escalated", "KIND_NOT_SUPPORTED")
                    reports.append(RegionReport(region.kind, "escalated", 0,
                                                "KIND_NOT_SUPPORTED",
                                                str(TAB.HierarchicalTable), ascii_view))

    # --- DATA-GRID FALLBACK (spec 2026-08-08-data-grid-types-elements-axioms.md §8.18)
    #
    # Only where the shipped path asserts NOTHING. Measured on the corpus, the two paths
    # segment cells differently — on the stem they share 441 cells with 59 old-only and
    # 51 new-only, because the ruled path re-extracts by drawn columns while the data
    # grid reads ink runs. Replacing wholesale would churn the one document with an
    # adjudicated floor (0.95) for no measured gain, so it does not replace: it fills in
    # where the page currently yields zero cells (apple page 1, ons page 7, cbh).
    #
    # The gate is NOTHING AT ALL — no assertion and no escalation. Not merely "asserted
    # nothing": a page that ESCALATED has already accounted for its ink, and appending a
    # reading there does two forbidden things. It masks an honest escalation, which §7
    # and the fluent-reader invariant require be FIXED rather than papered over. And it
    # DOUBLE-COUNTS — those lines' tokens are already in escalated_total, so adding them
    # to asserted_total inflates the ratio. Measured: apple page 1 reported 0.5941 under
    # the broader gate, a number in which the same tokens sat on both sides.
    #
    # Found by the suite, not by reasoning: four escalation-path tests failed because a
    # second region appeared on a page they had pinned to exactly one.
    if datagrid_fallback and asserted_total == 0 and escalated_total == 0:
        from .datagrid import derive_data_grid, emit_data_grid
        _grid = derive_data_grid(pdf_path, page_number)
        if _grid is not None and _grid.rows:
            _lines = [ln for ln in text_lines(extract_words(pdf_path, page_number))
                      if ln.words]
            _lines.sort(key=lambda ln: ln.top)
            _before = len(list(graph.subjects(RDF.type, TAB.EntryCell)))
            emit_data_grid(graph, _grid, _lines, doc, page_number)
            _cells = len(list(graph.subjects(RDF.type, TAB.EntryCell))) - _before
            _tokens = sum(len(_lines[i].words) for i in _grid.rows)
            asserted_total += _tokens
            reports.append(RegionReport(RegionKind.RECORD_TABLE, "asserted", _cells,
                                        None, str(TAB.DataGrid), ""))
            band_marks.append((asserted_total, escalated_total))

    band_marks.append((asserted_total, escalated_total))
    from dataclasses import replace as _dc_replace
    reports = [_dc_replace(r,
                           tokens_asserted=band_marks[i + 1][0] - band_marks[i][0],
                           tokens_escalated=band_marks[i + 1][1] - band_marks[i][1])
               for i, r in enumerate(reports)]

    # --- ADOPTION (R73). A page that read NOTHING and escalated everything is a total
    # failure of the shipped reader, and where the data grid reads it completely the
    # escalation is superseded rather than supplemented. Withdrawal is exact: the page's
    # graph is rebuilt from the grid alone, so no token is ever counted on both sides —
    # the defect that made the first wiring's 0.5941 meaningless.
    #
    # Warranted by an oracle, not by preference: apple page 1 is transcribed at 28 entry
    # rows and the grid reads 28 of 28 with nothing leaked, while the pipeline asserts
    # zero cells there.
    #
    # OFF by default at PAGE scope, and the reason is NOT the one this comment used to give.
    # The old reason — "the driver compiles each page standalone before re-compiling
    # continuation pages" — is MEASURED FALSE: `document.compile_document` makes ONE pass and
    # page N-1's carried reading is an INPUT to page N's compile, so forcing adoption on every
    # page leaves the stem document byte-identical at 0.9654553611484971.
    #
    # The real reason is the REFUSAL BRANCH, and its FIRST half is structural, not numeric: a
    # single-page compile is INCAPABLE OF CHAINING AT ALL — `CompilationReport` carries no chain
    # concept; chains exist only on the driver's `DocumentReport`. Whatever a page scores
    # standalone, it can never see the pages it continues onto.
    #
    # The score corroborates it, SAME PAGE under both scopes: stem p1 standalone with adoption
    # scores 0.9588 (measured this loop), against 0.9706 for the driver's own reading of that
    # same page 1 (Loop M, recorded at docs/superpowers/residues.md R29). Page scope is refused
    # not because the isolated reading would score deceptively HIGHER, but because it scores
    # measurably LOWER. NB the two COUNTS are not comparable and are not compared: R29's figure
    # is 825 TOKENS asserted under the driver, the standalone figure is 811 CELLS — only the two
    # scores share a scale. At document scope the whole stem is one chain of 3, 2152 cells, at
    # 0.9654553611484971. Pinned by tests/test_corpus_stem.py::
    #     test_page_scope_adoption_would_have_taken_the_page_the_driver_reads
    # (whose assertion pins the full-precision document floor, not the 4-decimal 0.9706).
    #
    # Adoption is therefore the DOCUMENT's last reader (`document.compile_document`), and this
    # flag stays the explicit page-scope API that measurement needs.
    #
    # IT RUNS HERE — AFTER the per-band differencing above and BEFORE the score — and the
    # position is load-bearing, not cosmetic. `RegionReport.tokens_escalated` defaults to 0
    # and the differencing block is the ONLY place it is ever set, so a branch placed before
    # it would hand `build_ledger` a `reports` list in which every band reads 0 escalated
    # tokens. The ledger's untouched-band term would then contribute nothing and an escalated
    # band the grid never touched would have its ink vanish from the denominator — the page
    # scoring higher than it read, the exact failure this loop exists to prevent. Running
    # afterwards also leaves `band_marks` untouched, so the differencing block's
    # `len(reports) == len(band_marks) - 1` invariant is not something adoption has to repair.
    # The move is behaviour-preserving for every other path: this branch's gate
    # (escalated_total > 0) and the fallback's (escalated_total == 0) are mutually exclusive,
    # so neither can now observe the other's writes any more than it could before.
    if datagrid_adopt and asserted_total == 0 and escalated_total > 0:
        from .adoption import build_ledger
        from .datagrid import derive_data_grid as _dg, emit_data_grid as _emit
        _grid = _dg(pdf_path, page_number)
        if _grid is not None and _grid.rows:
            _lines = sorted([ln for ln in text_lines(extract_words(pdf_path, page_number))
                             if ln.words], key=lambda ln: ln.top)
            _led = build_ledger(_lines, _grid.rows, bands, reports)
            # WHAT `rep.graph` IS AUTHORITATIVE FOR AT PAGE SCOPE (final review I2). The rebuild
            # discards every pass-1 escalation candidate on the page, including those of bands
            # the grid never TOUCHED — whose tokens `build_ledger` still books
            # (`adoption.py:90-93`, the untouched term). So for an untouched escalated band the
            # returned report books escalated ink that nothing in this graph escalates: at PAGE
            # scope `rep.graph` is authoritative for the TOUCHED bands, the grid and the residue,
            # and the REPORT (`RegionReport.tokens_escalated`, kept verbatim for an untouched
            # band) is the authority for the rest. `sum(r.tokens_escalated) == escalated_total`
            # is unaffected — the disagreement is graph-vs-ledger, never ledger-internal.
            #
            # NOT REPAIRED HERE, on purpose. Re-escalating the untouched bands into the rebuilt
            # graph would fix page scope and BREAK document scope: `document.compile_document`
            # withdraws only the SUPERSEDED bands' candidates and merges this graph wholesale
            # (document.py:1445-1447), so the driver's own untouched-band candidate would still
            # be standing under the page doc URI and a re-escalated copy would arrive beside it
            # under the adoption doc URI — two escalating nodes over one band's ink, against a
            # ledger that books it once. That is the double count R73 exists to prevent, moved
            # to the other side. The DOCUMENT path has no gap: it keeps the original page graph.
            #
            # MEASURED, so the exposure is stated rather than assumed: on both adopting pages in
            # the corpus the untouched term is EMPTY. stem p1 (`compile_tables(STEM, 1,
            # validate_shapes=False, datagrid_adopt=True)`) has exactly one escalated band
            # (region 1, REGION_TILING_FAILED) and the grid touches it — the other two bands are
            # `ignored` at 0 escalated tokens — leaving 1025 asserted / 44 escalated at 0.9588,
            # all 44 of them the grid's OWN residue candidate, which the rebuild does emit.
            # apple p1 likewise. Registered as residue R83.
            graph = Graph()                   # withdrawal: the page graph is rebuilt
            _grid_uri = _emit(graph, _grid, _lines, doc, page_number)
            _cells = len(list(graph.subjects(RDF.type, TAB.EntryCell)))
            # THE LEDGER IS LINE-GRANULAR (spec §5.3). Zeroing `escalated_total` would score
            # the page 1.0000 whatever the grid missed; withdrawing band-by-band would count
            # the read lines twice (0.594). Only the line is a unit both sides agree on.
            # PROCEDURAL and justified (CLAUDE.md §8): exact counting over line-index sets,
            # no threshold and no tolerance — see adoption.build_ledger's classification.
            asserted_total = _led.asserted_tokens
            escalated_total = _led.escalated_tokens
            # Band index IS region index: touched bands are SUPERSEDED in place, untouched
            # bands keep their report verbatim, and the grid (plus any residue) is appended.
            # The predicate is `tokens_escalated > 0`, the SAME one `build_ledger` selects its
            # escalated bands by, and it has to be: the ledger has already turned this band's
            # unread lines into residue, so leaving its own count standing would book that ink
            # twice. Keying on the verdict string here while the ledger keys on the tokens would
            # reopen the invariant sum(r.tokens_escalated) == escalated_total from the other side.
            reports = [
                _dc_replace(r, verdict="superseded", tokens_escalated=0)
                if i in _led.touched and r.tokens_escalated > 0 else r
                for i, r in enumerate(reports)
            ]
            reports.append(RegionReport(RegionKind.RECORD_TABLE, "asserted", _cells,
                                        None, str(TAB.DataGrid), "",
                                        table_uri=_grid_uri,
                                        tokens_asserted=_led.asserted_tokens))
            if _led.residue:
                _text = "\n".join(" ".join(w.text for w in _lines[j].words)
                                  for j in _led.residue)
                _res_uri = URIRef(f"{doc}#p{page_number}-datagrid-residue")
                escalate_region(graph, _res_uri, doc, _text,
                                "DATAGRID_RESIDUE", TAB.DataGrid, 0.0, page_number)
                reports.append(RegionReport(RegionKind.UNSUPPORTED_TABLE, "escalated", 0,
                                            "DATAGRID_RESIDUE", str(TAB.DataGrid), "",
                                            tokens_escalated=sum(len(_lines[j].words)
                                                                 for j in _led.residue)))

    denom = asserted_total + escalated_total
    if denom:
        score = asserted_total / denom
    else:
        # NOTHING was read. Whether that is right depends on whether there was anything
        # to read, and the page-level grid gate answers exactly that (R72). A page of
        # prose has nothing to read and scores 1.0; a page carrying a table that yielded
        # no cells FAILED, and a failure must not score perfect.
        #
        # Measured before this change: 11 of 27 corpus pages scored a degenerate 1.0 on
        # an empty reading — nine of them correctly (prose the gate discards) and two
        # (ons pages 7 and 8) real tables the reader produced nothing for.
        from .datagrid import page_has_table
        score = 0.0 if page_has_table(pdf_path, page_number) else 1.0

    if validate_shapes and (
        any(graph.subjects(RDF.type, TAB.RecordTable))
        or any(graph.subjects(RDF.type, TAB.HierarchicalTable))
    ):
        conforms, text = _validate(graph)
        if not conforms:
            raise AssertionError(f"asserted holon failed tab: SHACL:\n{text}")

    return CompilationReport(score, tuple(reports), graph, asserted_total, escalated_total)
