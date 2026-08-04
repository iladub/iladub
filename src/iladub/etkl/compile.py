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


def _build_ruled_band(sub, sub_rules, sub_hrules, page_chars):
    """Construct the Band for a RULED sub-band. THE SEAM for the no-synthesised-Rule guard:
    tests call this directly, so the guard exercises production code, not a copy (attempt 1's
    guard replicated this logic in its test body and was proven tautological).

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
    from .geometry import refine_rule_columns, rule_aware_lines, weld_hrule_boxes, opening_box_rows

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
        interior_rule_xs as _interior_rule_xs, peel_leading_captions
    gset = _grid_lines(sub, sub_rules)
    enclosed = _enclosed_lines(sub, sub_rules)
    # loop P fixwave A: the ink-interior rule x's (real column separators — has ink
    # on both sides; never a double-drawn outer-border twin), computed once on the
    # PRE-peel band/rules (interior-ness is a property of the rules + band words,
    # unaffected by whether captions are peeled) and fed to the welder's/opening-box
    # test below. rule_aware_lines' own column bucketing (xs, just above) is
    # UNCHANGED — it keeps using every rule x, including the outer edges.
    interior_xs = _interior_rule_xs(sub, sub_rules)
    caption_lines, kept_lines = peel_leading_captions(sub.lines, gset, enclosed)

    # fixwave A round 3 (stem regression fix, round 2's per-line straddle witness
    # retired — it broke BOTH specimens): "leading + enclosed" is a PROPOSAL, not a
    # licence. The stem's header stack is a leading, enclosed run too (its interior
    # verticals start below it), so peeling it on that evidence alone strands loop
    # L's row-above-the-block-rule licence. Dispose the proposal by re-extracting
    # the TENTATIVE kept band and checking whether its own grid opens with a drawn
    # multi-line header box (CBH's wrapped-header signature, >= 2 re-extracted rows
    # in the first full-width hrule box, geometry.opening_box_rows) — the stem's
    # grid opens with bare single-row data-row boxes, so it fails this check and
    # the peel is abandoned, falling back to the UNPEELED construction path,
    # byte-identical to "no peel". Single propose -> check -> commit-or-fallback;
    # no further candidate peel length is ever tried (deterministic, no retry loop).
    committed = False
    if caption_lines:
        tentative_sub = _replace(sub, lines=kept_lines, top=kept_lines[0].top)
        tentative_chars = [c for c in page_chars
                           if c.top >= tentative_sub.top - 0.5 and c.bottom <= tentative_sub.bottom + 0.5]
        tentative_relines = rule_aware_lines(tentative_chars, xs) if len(xs) >= 2 else []
        if opening_box_rows(tentative_relines, sub_hrules, interior_xs) >= 2:
            sub, band_chars, relines = tentative_sub, tentative_chars, tentative_relines
            committed = True
        else:
            caption_lines = ()
    if not committed:
        band_chars = [c for c in page_chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
        relines = rule_aware_lines(band_chars, xs) if len(xs) >= 2 else []

    if relines:
        relines = weld_hrule_boxes(relines, sub_hrules, interior_xs)
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
    order is their index)."""
    from rdflib import Literal, RDF, URIRef
    from rdflib.namespace import XSD
    for k, ln in enumerate(getattr(band, "captions", ()) or ()):
        cap = URIRef("%s-bandcap%d" % (table_uri, k))
        graph.add((cap, RDF.type, TAB.RegionCaption))
        graph.add((cap, TAB.captionText, Literal(" ".join(w.text for w in ln.words))))
        graph.add((cap, TAB.captionRow, Literal(k, datatype=XSD.integer)))
        graph.add((table_uri, TAB.hasCaption, cap))


def page_bands(pdf_path: str, page_number: int = 0):
    """The page's bands, exactly as compile_tables reads them (band i here IS band i there).

    THE SEAM for loop M's document driver: continuation recognition must read the SAME bands the
    compile reads, or the recognized band and the compiled table are two different things and the
    chain links the wrong URIs. Extracted verbatim from compile_tables (which now calls it), so
    there is one band-construction path, not a copy that can drift.
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
            if not sub_rules:
                bands.append(_replace(sub, hrules=sub_hrules) if sub_hrules else sub)
                continue
            # RULED band: re-extract cells by the ruled columns (splits pdfplumber-merged blobs at
            # the author's exact boundaries) — else keep pdfplumber's words. Candidate boundaries
            # become columns only when the header confirms them (_build_ruled_band, the seam).
            bands.append(_build_ruled_band(sub, sub_rules, sub_hrules, page_chars))
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
    from pyshacl import validate
    global _FULL_SHAPES, _FULL_ONT
    if _FULL_SHAPES is None:
        v = _repo_vocab()
        s = Graph()
        s.parse(os.path.join(v, "shapes", "tab-shapes.ttl"), format="turtle")
        s.parse(os.path.join(v, "shapes", "tab-physical-shapes.ttl"), format="turtle")
        _FULL_SHAPES = s
        _FULL_ONT = Graph().parse(os.path.join(v, "ontology", "tab.ttl"), format="turtle")
    conforms, _, text = validate(graph, shacl_graph=_FULL_SHAPES, ont_graph=_FULL_ONT,
                                 inference="rdfs", advanced=True)
    return conforms, text


def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True, span_proposer=None,
                   row_role_proposer=None, doc_uri: URIRef | None = None,
                   carried_header_roles: dict | None = None) -> CompilationReport:
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
    recognized band — but an external caller can bypass it. Registered as part of residue R34."""
    from .segment import is_multi_table_ambiguous
    doc = _DOC if doc_uri is None else doc_uri
    bands = page_bands(pdf_path, page_number)
    graph = Graph()
    reports: list[RegionReport] = []
    asserted_total = escalated_total = 0

    for idx, band in enumerate(bands):
        ascii_view = render_ascii(band)
        if is_multi_table_ambiguous(band):
            cand_uri = URIRef(f"{doc}#region{idx}")
            escalate_region(graph, cand_uri, doc, ascii_view, "MULTI_TABLE_AMBIGUOUS",
                            TAB.HierarchicalTable, 0.4)
            escalated_total += sum(len(ln.words) for ln in band.lines)
            reports.append(RegionReport(RegionKind.UNSUPPORTED_TABLE, "escalated", 0,
                                        "MULTI_TABLE_AMBIGUOUS", str(TAB.HierarchicalTable), ascii_view))
            continue
        region = classify(band)

        if region.kind is RegionKind.NON_TABLE:
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
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.RecordTable), ascii_view))
                    else:
                        graph += scratch
                        _emit_band_captions(graph, table_uri, band)
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
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0,
                                                "REGION_TILING_FAILED",
                                                str(TAB.RecordTable), ascii_view))
                else:
                    graph += scratch
                    _emit_band_captions(graph, table_uri, band)
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
                    tokens = sum(len(ln.words) for ln in band.lines)
                    escalated_total += tokens
                    reports.append(RegionReport(region.kind, "escalated", 0,
                                                "KIND_NOT_SUPPORTED",
                                                str(TAB.HierarchicalTable), ascii_view))

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
