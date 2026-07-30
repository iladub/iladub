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
    from .geometry import refine_rule_columns, rule_aware_lines

    xs = sorted({round(r.x, 2) for r in sub_rules})
    band_chars = [c for c in page_chars if c.top >= sub.top - 0.5 and c.bottom <= sub.bottom + 0.5]
    relines = rule_aware_lines(band_chars, xs) if len(xs) >= 2 else []
    if not relines:
        return _replace(sub, rules=sub_rules, hrules=sub_hrules)
    band = Band(tuple(relines), sub.top, sub.bottom, sub_rules, sub_hrules)

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
    return Band(tuple(relines2), sub.top, sub.bottom, sub_rules, sub_hrules, tuple(col_xs))


@dataclass(frozen=True)
class RegionReport:
    kind: RegionKind
    verdict: str                 # "asserted" | "escalated" | "ignored"
    cells: int                   # asserted entry-cell count (0 otherwise)
    reason: str | None
    anchor: str | None
    ascii: str


@dataclass(frozen=True)
class CompilationReport:
    score: float
    regions: tuple[RegionReport, ...]
    graph: Graph

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
                   row_role_proposer=None) -> CompilationReport:
    from .geometry import extract_rules, extract_chars, extract_hrules
    from dataclasses import replace as _replace
    words = extract_words(pdf_path, page_number)
    page_rules = extract_rules(pdf_path, page_number)
    page_hrules = extract_hrules(pdf_path, page_number)
    page_chars = extract_chars(pdf_path, page_number) if page_rules else []
    raw_bands = detect_bands(text_lines(words))
    from .segment import segment, is_multi_table_ambiguous
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
    graph = Graph()
    reports: list[RegionReport] = []
    asserted_total = escalated_total = 0

    for idx, band in enumerate(bands):
        ascii_view = render_ascii(band)
        if is_multi_table_ambiguous(band):
            cand_uri = URIRef(f"{_DOC}#region{idx}")
            escalate_region(graph, cand_uri, _DOC, ascii_view, "MULTI_TABLE_AMBIGUOUS",
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
                    table_uri = URIRef(f"{_DOC}#ttable{idx}")
                    # R17 gate (loop J): scratch -> region_tiles -> commit-or-escalate, the
                    # same backstop as the hierarchical/matrix/row-hier paths. A defective
                    # region escalates in-band instead of crashing final validation.
                    scratch = Graph()
                    n = assert_transposed_region(scratch, region, table_uri, _DOC, page_number)
                    if n and not region_tiles(scratch):
                        cand_uri = URIRef(f"{_DOC}#region{idx}")
                        escalate_region(graph, cand_uri, _DOC, ascii_view,
                                        "REGION_TILING_FAILED", TAB.RecordTable, 0.4)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        reports.append(RegionReport(region.kind, "escalated", 0,
                                                    "REGION_TILING_FAILED",
                                                    str(TAB.RecordTable), ascii_view))
                    else:
                        graph += scratch
                        b = region.grid.boundaries
                        value_cells = [c for c in region.cells if c.col >= 1]
                        asserted_total += sum(len(c.words) for c in value_cells if cell_round_trips(c, b))
                        escalated_total += sum(len(c.words) for c in value_cells if not cell_round_trips(c, b))
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.RecordTable), ascii_view))
                else:
                    # detected but not confidently compilable — escalate (Loop 3 behaviour)
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "TRANSPOSED",
                                    TAB.TransposedTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "TRANSPOSED",
                                                str(TAB.TransposedTable), ascii_view))
            elif looks_row_grouped(region):
                from .rowheaders import classify_row_hier
                from .holon import assert_row_hier_region
                from .tiling import region_tiles
                rreg = classify_row_hier(band)
                table_uri = URIRef(f"{_DOC}#rhtable{idx}")
                scratch = Graph()
                if rreg is not None:
                    n = assert_row_hier_region(scratch, rreg, band, table_uri, _DOC, page_number)
                if rreg is not None and region_tiles(scratch):
                    graph += scratch
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
                                                str(TAB.HierarchicalTable), ascii_view))
                else:
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "ROW_GROUP_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "ROW_GROUP_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
            else:
                # ---- existing RECORD_TABLE assert logic ----
                from .tiling import region_tiles
                table_uri = URIRef(f"{_DOC}#table{idx}")
                # R17 gate (loop J): see the transposed branch above.
                scratch = Graph()
                n = assert_record_region(scratch, region, table_uri, _DOC, page_number)
                if n and not region_tiles(scratch):
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view,
                                    "REGION_TILING_FAILED", TAB.RecordTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0,
                                                "REGION_TILING_FAILED",
                                                str(TAB.RecordTable), ascii_view))
                else:
                    graph += scratch
                    b = region.grid.boundaries
                    data_cells = [c for c in region.cells if c.row > 0]
                    asserted_total += sum(len(c.words) for c in data_cells if cell_round_trips(c, b))
                    escalated_total += sum(len(c.words) for c in data_cells if not cell_round_trips(c, b))
                    reports.append(RegionReport(region.kind, "asserted", n, None,
                                                str(TAB.RecordTable), ascii_view))
        else:  # UNSUPPORTED_TABLE
            from .matrix import is_matrix_candidate
            if is_matrix_candidate(band):
                from .matrix import classify_matrix
                from .holon import assert_matrix_region
                from .tiling import region_tiles
                mreg = classify_matrix(band)
                table_uri = URIRef(f"{_DOC}#mtable{idx}")
                scratch = Graph()
                if mreg is not None:
                    n = assert_matrix_region(scratch, mreg, band, table_uri, _DOC, page_number)
                if mreg is not None and region_tiles(scratch):
                    graph += scratch
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
                                                str(TAB.HierarchicalTable), ascii_view))
                else:
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "MATRIX_AMBIGUOUS",
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
                if hreg is not None and not merge_tiling_ok(hreg.tree, hreg.grid):
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    resolved = None
                    if span_proposer is not None:
                        from .span import resolve_ambiguous_merge
                        resolved = resolve_ambiguous_merge(
                            graph, hreg, band, table_uri, _DOC, page_number, span_proposer)
                    if resolved is None and row_role_proposer is not None:
                        # Loop C NEURAL slice. The narrow-flank resolver keeps priority: it fires
                        # on an explicit ambiguous_flank flag, a strictly narrower trigger. This
                        # handles the general tiling failure (caption / wrap-continuation rows).
                        from .rowrole import resolve_header_row_roles
                        resolved = resolve_header_row_roles(
                            graph, hreg, band, table_uri, _DOC, page_number, row_role_proposer)
                    if resolved is not None:
                        n, _promos = resolved
                        tokens = sum(len(ln.words) for ln in band.lines)
                        asserted_total += n
                        escalated_total += max(0, tokens - n)
                        reports.append(RegionReport(region.kind, "asserted", n, None,
                                                    str(TAB.HierarchicalTable), ascii_view))
                    else:
                        cand_uri = URIRef(f"{_DOC}#region{idx}")
                        escalate_region(graph, cand_uri, _DOC, ascii_view, "MERGE_AMBIGUOUS",
                                        TAB.HierarchicalTable, 0.4)
                        escalated_total += sum(len(ln.words) for ln in band.lines)
                        reports.append(RegionReport(region.kind, "escalated", 0, "MERGE_AMBIGUOUS",
                                                    str(TAB.HierarchicalTable), ascii_view))
                elif hreg is not None:
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    # THE MEMBRANE BACKSTOP (loop G attempt 2): assert into a SCRATCH graph and
                    # let region_tiles dispose it, exactly as the matrix and row-hier paths
                    # already do. The PLAIN HIERARCHICAL path wrote directly into the graph —
                    # which is why a defective region here CRASHED compile_tables at final
                    # validation (attempt 1's counter-example) instead of escalating.
                    # Loop J closed R17: the record and transposed paths now carry the same gate.
                    from .tiling import region_tiles
                    scratch = Graph()
                    n = assert_hier_region(scratch, hreg, band, table_uri, _DOC, page_number)
                    if n and not region_tiles(scratch):
                        cand_uri = URIRef(f"{_DOC}#region{idx}")
                        escalate_region(graph, cand_uri, _DOC, ascii_view,
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
                        ))
                else:
                    # Not hierarchical — escalate whole region in-band
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view,
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

    return CompilationReport(score, tuple(reports), graph)
