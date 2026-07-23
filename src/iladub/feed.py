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
            rows.setdefault(row, []).append((col, concept))
        for row in sorted(rows, key=lambda r: str(r)):
            cells = [c for _, c in sorted(rows[row], key=lambda kc: str(kc[0]))]
            out.append(Record(str(row).split("#")[-1], tuple(cells)))
    return out
