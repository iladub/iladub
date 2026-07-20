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
                   validate_shapes: bool = True) -> CompilationReport:
    from .geometry import extract_rules
    from dataclasses import replace as _replace
    words = extract_words(pdf_path, page_number)
    page_rules = extract_rules(pdf_path, page_number)
    raw_bands = detect_bands(text_lines(words))
    from .segment import segment, is_multi_table_ambiguous
    bands = []
    for band in raw_bands:
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules if r.top <= sub.bottom and r.bottom >= sub.top)
            bands.append(_replace(sub, rules=sub_rules) if sub_rules else sub)
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
                    table_uri = URIRef(f"{_DOC}#ttable{idx}")
                    n = assert_transposed_region(graph, region, table_uri, _DOC, page_number)
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
                # ---- existing RECORD_TABLE assert logic, unchanged ----
                table_uri = URIRef(f"{_DOC}#table{idx}")
                n = assert_record_region(graph, region, table_uri, _DOC, page_number)
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
                    cand_uri = URIRef(f"{_DOC}#region{idx}")
                    escalate_region(graph, cand_uri, _DOC, ascii_view, "MERGE_AMBIGUOUS",
                                    TAB.HierarchicalTable, 0.4)
                    escalated_total += sum(len(ln.words) for ln in band.lines)
                    reports.append(RegionReport(region.kind, "escalated", 0, "MERGE_AMBIGUOUS",
                                                str(TAB.HierarchicalTable), ascii_view))
                elif hreg is not None:
                    table_uri = URIRef(f"{_DOC}#htable{idx}")
                    n = assert_hier_region(graph, hreg, band, table_uri, _DOC, page_number)
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
