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
    verdict: str                 # "asserted" | "escalated" | "ignored"
    cells: int                   # asserted entry-cell count (0 otherwise)
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


_FULL_SHAPES = None
_FULL_ONT = None


def _validate(graph: Graph) -> tuple[bool, str]:
    global _FULL_SHAPES, _FULL_ONT
    if _FULL_SHAPES is None:
        v = _repo_vocab()
        s = Graph()
        s.parse(os.path.join(v, "shapes", "tab-shapes.ttl"), format="turtle")
        s.parse(os.path.join(v, "shapes", "tab-physical-shapes.ttl"), format="turtle")
        _FULL_SHAPES = s
        _FULL_ONT = Graph().parse(os.path.join(v, "ontology", "tab.ttl"), format="turtle")
    from . import membrane
    return membrane.validate(graph, _FULL_SHAPES, _FULL_ONT)


def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True, span_proposer=None,
                   row_role_proposer=None, doc_uri: URIRef | None = None,
                   carried_header_roles: dict | None = None,
                   section_repair_bands: frozenset[int] | None = None) -> CompilationReport:
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
    reports: list[RegionReport] = []
    asserted_total = escalated_total = 0

    # Per-band token accounting (loop Q Task 4): snapshot the running totals at the TOP of each
    # band's turn (the one point every branch passes through — `continue` never skips it), close
    # with a sentinel after the loop, and difference. Every branch appends exactly one report per
    # band, so band_marks[i+1] - band_marks[i] IS band i's own contribution, exactly.
    band_marks: list[tuple[int, int]] = []

    for idx, band in enumerate(bands):
        band_marks.append((asserted_total, escalated_total))
        ascii_view = render_ascii(band)
        if is_multi_table_ambiguous(band):
            cand_uri = URIRef(f"{doc}#region{idx}")
            escalate_region(graph, cand_uri, doc, ascii_view, "MULTI_TABLE_AMBIGUOUS",
                            TAB.HierarchicalTable, 0.4)
            if getattr(band, "unit_markers", ()):
                _emit_unit_markers(graph, cand_uri, band, None)
                escalated_total += _marker_word_count(band)
            escalated_total += sum(len(ln.words) for ln in band.lines)
            reports.append(RegionReport(RegionKind.UNSUPPORTED_TABLE, "escalated", 0,
                                        "MULTI_TABLE_AMBIGUOUS", str(TAB.HierarchicalTable), ascii_view))
            continue
        region = classify(band)

        if region.kind is RegionKind.NON_TABLE:
            if getattr(band, "unit_markers", ()):
                # C1 fix: an ignored band never contributed to the score, so no
                # accounting change — only the invariant "absorbed ink always lands
                # in the graph with provenance" applies here.
                cand_uri = URIRef(f"{doc}#region{idx}")
                _emit_unit_markers(graph, cand_uri, band, None)
            reports.append(RegionReport(region.kind, "ignored", 0,
                                        region.reason, None, ascii_view))
            continue

        if region.kind is RegionKind.RECORD_TABLE:
            from .orientation import looks_transposed, transpose_is_coherent
            from .rowheaders import looks_row_grouped
            if looks_transposed(region):
                if transpose_is_coherent(region):
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
                    if n and not region_tiles(scratch):
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view,
                                        "REGION_TILING_FAILED", TAB.RecordTable, 0.4)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
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
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.RecordTable), ascii_view,
                                                    table_uri))
                else:
                    # detected but not confidently compilable — escalate (Loop 3 behaviour)
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view, "TRANSPOSED",
                                    TAB.TransposedTable, 0.4)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "TRANSPOSED",
                                                str(TAB.TransposedTable), ascii_view))
            elif looks_row_grouped(region):
                from .rowheaders import classify_row_hier
                from .holon import assert_row_hier_region
                from .tiling import region_tiles
                rreg = classify_row_hier(band)
                table_uri = URIRef(f"{doc}#rhtable{idx}")
                scratch = Graph()
                if rreg is not None:
                    n = assert_row_hier_region(scratch, rreg, band, table_uri, doc, page_number)
                if rreg is not None and region_tiles(scratch):
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
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.HierarchicalTable), ascii_view,
                                                table_uri))
                else:
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view, "ROW_GROUP_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "ROW_GROUP_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
            else:
                # ---- existing RECORD_TABLE assert logic ----
                from .tiling import region_tiles
                table_uri = URIRef(f"{doc}#table{idx}")
                # R17 gate (loop J): see the transposed branch above.
                scratch = Graph()
                n = assert_record_region(scratch, region, table_uri, doc, page_number)
                if n and not region_tiles(scratch):
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view,
                                    "REGION_TILING_FAILED", TAB.RecordTable, 0.4)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
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
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.RecordTable), ascii_view,
                                                table_uri))
        else:  # UNSUPPORTED_TABLE
            from .matrix import is_matrix_candidate
            if is_matrix_candidate(band):
                from .matrix import classify_matrix
                from .holon import assert_matrix_region
                from .tiling import region_tiles
                mreg = classify_matrix(band)
                table_uri = URIRef(f"{doc}#mtable{idx}")
                scratch = Graph()
                if mreg is not None:
                    n = assert_matrix_region(scratch, mreg, band, table_uri, doc, page_number)
                if mreg is not None and region_tiles(scratch):
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
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.HierarchicalTable), ascii_view,
                                                table_uri))
                else:
                    cand_uri = URIRef(f"{doc}#region{idx}")
                    escalate_region(graph, cand_uri, doc, ascii_view, "MATRIX_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "MATRIX_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
            else:
                # ---- existing Loop 2 hierarchical path, UNCHANGED ----
                from .hierarchical import classify_hierarchical
                from .holon import assert_hier_region
                hreg = classify_hierarchical(band)
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
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.HierarchicalTable), ascii_view,
                                                    table_uri))
                    else:
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view, "MERGE_AMBIGUOUS",
                                        TAB.HierarchicalTable, 0.4)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
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
                    if n and not region_tiles(scratch):
                        cand_uri = URIRef(f"{doc}#region{idx}")
                        escalate_region(graph, cand_uri, doc, ascii_view,
                                        "REGION_TILING_FAILED", TAB.HierarchicalTable, 0.4)
                        if getattr(band, "unit_markers", ()):
                            _emit_unit_markers(graph, cand_uri, band, None)
                            escalated_total += _marker_word_count(band)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
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
                                    anchor=TAB.HierarchicalTable, confidence=0.4)
                    if getattr(band, "unit_markers", ()):
                        _emit_unit_markers(graph, cand_uri, band, None)
                        escalated_total += _marker_word_count(band)
                    tokens = sum(len(ln.words) for ln in band.lines)
                    escalated_total += tokens
                    reports.append(RegionReport(region.kind, "escalated", 0,
                                                "KIND_NOT_SUPPORTED",
                                                str(TAB.HierarchicalTable), ascii_view))

    band_marks.append((asserted_total, escalated_total))
    from dataclasses import replace as _dc_replace
    reports = [_dc_replace(r,
                           tokens_asserted=band_marks[i + 1][0] - band_marks[i][0],
                           tokens_escalated=band_marks[i + 1][1] - band_marks[i][1])
               for i, r in enumerate(reports)]

    denom = asserted_total + escalated_total
    score = 1.0 if denom == 0 else asserted_total / denom

    if validate_shapes and (
        any(graph.subjects(RDF.type, TAB.RecordTable))
        or any(graph.subjects(RDF.type, TAB.HierarchicalTable))
    ):
        conforms, text = _validate(graph)
        if not conforms:
            raise AssertionError(f"asserted holon failed tab: SHACL:\n{text}")

    return CompilationReport(score, tuple(reports), graph, asserted_total, escalated_total)
