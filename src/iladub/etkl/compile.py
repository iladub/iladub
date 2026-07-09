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


def _validate(graph: Graph) -> tuple[bool, str]:
    from pyshacl import validate
    v = _repo_vocab()
    shapes = Graph()
    shapes.parse(os.path.join(v, "shapes", "tab-shapes.ttl"), format="turtle")
    shapes.parse(os.path.join(v, "shapes", "tab-physical-shapes.ttl"), format="turtle")
    ont = Graph().parse(os.path.join(v, "ontology", "tab.ttl"), format="turtle")
    conforms, _, text = validate(graph, shacl_graph=shapes, ont_graph=ont,
                                 inference="rdfs", advanced=True)
    return conforms, text


def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True) -> CompilationReport:
    bands = detect_bands(text_lines(extract_words(pdf_path, page_number)))
    graph = Graph()
    reports: list[RegionReport] = []
    asserted_total = escalated_total = 0

    for idx, band in enumerate(bands):
        region = classify(band)
        ascii_view = render_ascii(band)

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
                from .rowheaders import classify_row_hier, row_tree_tiles
                from .holon import assert_row_hier_region
                rreg = classify_row_hier(band)
                if rreg is not None and row_tree_tiles(rreg.tree, len(rreg.leaf_rows)):
                    table_uri = URIRef(f"{_DOC}#rhtable{idx}")
                    n = assert_row_hier_region(graph, rreg, band, table_uri, _DOC, page_number)
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
                from .matrix import classify_matrix, matrix_tiles
                from .holon import assert_matrix_region
                mreg = classify_matrix(band)
                if mreg is not None and matrix_tiles(mreg):
                    table_uri = URIRef(f"{_DOC}#mtable{idx}")
                    n = assert_matrix_region(graph, mreg, band, table_uri, _DOC, page_number)
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
                if hreg is not None:
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
