"""feed — the ET(K)L → grounding bridge (closes raw-doc→grounded-graph).

PROCEDURAL raw extraction: reads asserted tab:RecordTable cells out of a compiled
CompilationReport.graph into per-cell SurfaceConcepts (row = record), then grounds them via the
shipped ground_concept oracle (unchanged — no new grounding decision here). RDF reads only; no
tuned constant, no IRI-name parsing. This is the RawDocument→grounding-portal traversal.
"""
from __future__ import annotations

import re
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
    """Each asserted tab:RecordTable OR tab:HierarchicalTable -> one Record per data row; each data
    cell -> a SurfaceConcept (text=its column's HEADER PATH, value=cell text, region=cell provenance).
    For a flat RecordTable the path reduces to the single column label (backward compatible). RDF
    reads only; no tuned constant, no IRI-name parsing."""
    out: list[Record] = []
    tables = (set(graph.subjects(RDF.type, TAB.RecordTable))
              | set(graph.subjects(RDF.type, TAB.HierarchicalTable)))
    for t in sorted(tables, key=str):
        header = _column_header_path(graph, t)
        row_path = _row_header_path(graph, t)
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
            rid = row_path.get(row, str(row).split("#")[-1])
            out.append(Record(rid, tuple(cells)))
    return out


def _bbox_xy(graph: Graph, entry_cell) -> tuple[float, float]:
    """Read (x0, y0) off an EntryCell's tab:hasBBox node; missing bbox sorts as (0.0, 0.0)."""
    bbox = graph.value(entry_cell, TAB.hasBBox)
    if bbox is None:
        return (0.0, 0.0)
    x0 = graph.value(bbox, TAB.x0)
    y0 = graph.value(bbox, TAB.y0)
    return (float(x0) if x0 is not None else 0.0, float(y0) if y0 is not None else 0.0)


def _header_path(graph: Graph, table, cover_pred) -> dict:
    """Map each target (column or row) covered by `table`'s header tree to its HEADER PATH: the
    deepest HeaderNode covering the target (via `cover_pred` = TAB.coversColumn or TAB.coversRow),
    walked up parentHeader to the root, labels joined ' > '. For a flat axis (level-0, single target,
    no parent) this is the single label. Returns {} when no header node covers via `cover_pred`.
    RDF reads only; no tuned constant, no IRI-name parsing."""
    label: dict = {}
    parent: dict = {}
    best: dict = {}                                 # target -> (level, header_node)
    for h in graph.objects(table, TAB.hasHeaderNode):
        lc = graph.value(h, TAB.hasLabel)
        label[h] = str(graph.value(lc, TAB.cellText)) if lc is not None else ""
        parent[h] = graph.value(h, TAB.parentHeader)
        lvl_lit = graph.value(h, TAB.headerLevel)
        lvl = int(lvl_lit) if lvl_lit is not None else 0
        for u in graph.objects(h, cover_pred):
            if u not in best or lvl > best[u][0]:
                best[u] = (lvl, h)
    paths: dict = {}
    for u, (_, h) in best.items():
        parts: list = []
        cur = h
        while cur is not None:
            parts.append(label.get(cur, ""))
            cur = parent.get(cur)
        paths[u] = " > ".join(reversed(parts))
    return paths


def _column_header_path(graph: Graph, table) -> dict:
    """Column paths (deepest coversColumn header walked to root). Single label per column for a flat
    RecordTable (backward compatible)."""
    return _header_path(graph, table, TAB.coversColumn)


def _row_header_path(graph: Graph, table) -> dict:
    """Row paths (deepest coversRow header walked to root) — a cross-tab's row identity. {} when the
    table has no row-header tree (RecordTable / plain hierarchical)."""
    return _header_path(graph, table, TAB.coversRow)


def _record_uri(row_id: str) -> URIRef:
    """Mint a URI-safe record subject from a row id. Preserves an already-safe opaque fragment
    (e.g. 'table0-r1'); slugs a header path ('Region > North' -> 'Region_North')."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", row_id).strip("_") or "record"
    return URIRef("urn:iladub:record:" + slug)


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
        subject = _record_uri(rec.row_id)
        for concept in rec.concepts:
            status = ground_concept(concept, contract, subject, proposer, terms, shapes, g)
            if status == "grounded":
                grounded += 1
            else:
                proposed += 1
    return FeedResult(len(records), grounded, proposed)
