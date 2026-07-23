"""feed — the ET(K)L → grounding bridge (closes raw-doc→grounded-graph).

PROCEDURAL raw extraction: reads asserted tab:RecordTable cells out of a compiled
CompilationReport.graph into per-cell SurfaceConcepts (row = record), then grounds them via the
shipped ground_concept oracle (unchanged — no new grounding decision here). RDF reads only; no
tuned constant, no IRI-name parsing. This is the RawDocument→grounding-portal traversal.
"""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from .ground import SurfaceConcept

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")


@dataclass(frozen=True)
class Record:
    row_id: str
    concepts: tuple[SurfaceConcept, ...]


def table_records(graph: Graph) -> list[Record]:
    """Each asserted tab:RecordTable -> one Record per data row; each data cell -> a SurfaceConcept
    (text=its column header, value=cell text, region=cell provenance). RDF reads only."""
    out: list[Record] = []
    for t in graph.subjects(RDF.type, TAB.RecordTable):
        header: dict = {}
        for h in graph.objects(t, TAB.hasHeaderNode):
            lc = graph.value(h, TAB.hasLabel)
            label = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
            for col in graph.objects(h, TAB.coversColumn):
                header[col] = label
        rows: dict = {}
        for e in graph.subjects(RDF.type, TAB.EntryCell):
            if (t, TAB.hasCell, e) not in graph:
                continue
            col = graph.value(e, TAB.atColumn)
            row = graph.value(e, TAB.atRow)
            prov = graph.value(e, PROV.wasDerivedFrom)
            region = str(prov).split("#")[-1] if prov is not None else str(e).split("#")[-1]
            concept = SurfaceConcept(header.get(col, ""), str(graph.value(e, TAB.cellText)), region)
            x0, y0 = _bbox_xy(graph, e)
            rows.setdefault(row, []).append((x0, y0, concept))
        for row in sorted(rows, key=lambda r: min(y0 for _, y0, _ in rows[r])):
            cells = [c for _, _, c in sorted(rows[row], key=lambda kc: kc[0])]
            out.append(Record(str(row).split("#")[-1], tuple(cells)))
    return out


def _bbox_xy(graph: Graph, entry_cell) -> tuple[float, float]:
    """Read (x0, y0) off an EntryCell's tab:hasBBox node; missing bbox sorts as (0.0, 0.0)."""
    bbox = graph.value(entry_cell, TAB.hasBBox)
    if bbox is None:
        return (0.0, 0.0)
    x0 = graph.value(bbox, TAB.x0)
    y0 = graph.value(bbox, TAB.y0)
    return (float(x0) if x0 is not None else 0.0, float(y0) if y0 is not None else 0.0)


@dataclass(frozen=True)
class FeedResult:
    records: int
    grounded: int
    proposed: int


def ground_document(graph, contract, proposer, terms, shapes, g) -> FeedResult:
    """Ground a compiled document's record tables against a contract: one subject per row, each
    cell grounded via the shipped ground_concept oracle (unchanged). Populates `g` with grounded
    nodes + promotion decisions + propositions; returns the grounded/proposed tally."""
    from .ground import ground_concept

    records = table_records(graph)
    grounded = proposed = 0
    for rec in records:
        subject = URIRef("urn:iladub:record:" + rec.row_id)
        for concept in rec.concepts:
            status = ground_concept(concept, contract, subject, proposer, terms, shapes, g)
            if status == "grounded":
                grounded += 1
            else:
                proposed += 1
    return FeedResult(len(records), grounded, proposed)
