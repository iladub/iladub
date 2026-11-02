"""Per-template part maps for the synthetic contract set (spec § 4.1, § 4.5). Licence: Apache-2.0.

A part map is authored by hand, once per template, in the template's own coordinates
(points, top-left origin, pdfplumber's `(x0, top, x1, bottom)`, 1-based pages). It carries
labels, field keys, page numbers and coordinates only — no template text. The owner
reviews it (`syn:review "draft"` -> `"owner-reviewed"`) before it is labelled human truth.

Justified PROCEDURAL (CLAUDE.md § 8): this module only parses committed Turtle into typed
records — raw extraction, no decision. Nothing here reads a document or answers a
span/read/group question; the coordinates were measured by hand and are data, not
tolerances. The generator uses these records to make documents; no reader may call it.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import RDF, Graph, Namespace

from scripts.synthetic_contracts.manifest import REPO

SYN = Namespace("https://w3id.org/iladub/synthetic#")
MAPS_DIR = REPO / "examples" / "synthetic-contracts" / "maps"
PART_TYPES = ("contract-form", "rules", "charter-party", "table", "blank")


@dataclass(frozen=True)
class Box:
    page: int
    x0: float
    top: float
    x1: float
    bottom: float


@dataclass(frozen=True)
class Part:
    id: str
    type: str
    box: tuple[Box, ...]  # one Box per page the part covers, in page order
    parent: str | None


@dataclass(frozen=True)
class Blank:
    field: str
    box: Box
    part: str


@dataclass(frozen=True)
class TableGrid:
    part: str
    page: int
    col_edges: tuple[float, ...]
    row_edges: tuple[float, ...]


@dataclass(frozen=True)
class PartMap:
    template: str
    parts: tuple[Part, ...]
    blanks: tuple[Blank, ...]
    grids: tuple[TableGrid, ...]
    review: str


def map_path(template_id: str, maps_dir: Path = MAPS_DIR) -> Path:
    return Path(maps_dir) / f"{template_id}.ttl"


def _box(g: Graph, n) -> Box:
    return Box(int(g.value(n, SYN.page)), float(g.value(n, SYN.x0)), float(g.value(n, SYN.top)),
               float(g.value(n, SYN.x1)), float(g.value(n, SYN.bottom)))


def _edges(lit) -> tuple[float, ...]:
    return tuple(float(v) for v in str(lit).split())


def load_map(template_id: str, maps_dir: Path = MAPS_DIR) -> PartMap:
    g = Graph().parse(map_path(template_id, maps_dir), format="turtle")
    (pm,) = list(g.subjects(RDF.type, SYN.PartMap))
    node_id = {}
    for n in g.subjects(RDF.type, SYN.Part):
        if g.value(n, SYN.partType).toPython() != "blank":
            node_id[n] = str(g.value(n, SYN.partId))
    parts, blanks, grids = [], [], []
    for n in sorted(g.subjects(RDF.type, SYN.Part)):
        kind = str(g.value(n, SYN.partType))
        boxes = tuple(sorted((_box(g, b) for b in g.objects(n, SYN.box)), key=lambda b: b.page))
        parent = g.value(n, SYN.parent)
        if kind == "blank":
            (box,) = boxes
            blanks.append(Blank(str(g.value(n, SYN.field)), box, node_id[parent]))
            continue
        parts.append(Part(node_id[n], kind, boxes, node_id[parent] if parent else None))
        for gr in g.objects(n, SYN.grid):
            grids.append(TableGrid(node_id[n], int(g.value(gr, SYN.page)),
                                   _edges(g.value(gr, SYN.colEdges)),
                                   _edges(g.value(gr, SYN.rowEdges))))
    return PartMap(str(g.value(pm, SYN.template)), tuple(parts), tuple(blanks), tuple(grids),
                   str(g.value(pm, SYN.review)))
