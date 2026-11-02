"""Seeded fill specs for the synthetic contract set (spec § 4.2). Licence: Apache-2.0.

A fill is the fake values placed in one template's blanks, plus the font drawn for them. Fills
are committed as Turtle (`examples/synthetic-contracts/fills/<template>-<n>.ttl`): the values
are fixed data, not regenerated randomness. Values are our own fake strings, no template text.

Justified PROCEDURAL (CLAUDE.md § 8): this module GENERATES documents' inputs. Its seed mixing,
size range and re-draw count are generation parameters, not reading tolerances; the fit test is
decidable exact arithmetic (a string's width against a box's width). No reader may call it.
"""
from __future__ import annotations

import random
import zlib
from dataclasses import dataclass
from pathlib import Path

from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, XSD
from reportlab.pdfbase.pdfmetrics import stringWidth

from scripts.synthetic_contracts.manifest import REPO
from scripts.synthetic_contracts.maps import PartMap, load_map
from scripts.synthetic_contracts.values import draw

SYN = Namespace("https://w3id.org/iladub/synthetic#")
FILLS_DIR = REPO / "examples" / "synthetic-contracts" / "fills"
FONTS = ("Helvetica", "Times-Roman", "Courier")
DRAWS = 20
SLACK = 2.0  # points kept clear inside each blank


class ValueTooLong(Exception):
    def __init__(self, field: str):
        super().__init__(field)
        self.field = field


@dataclass(frozen=True)
class Fill:
    id: str
    template: str
    seed: int
    values: dict[str, str]
    font: str
    size: float


def fill_id(template: str, n: int) -> str:
    return f"{template}-{n}"


def seed_of(template: str, n: int) -> int:
    return (zlib.crc32(template.encode()) * 1000003 + n) & 0xFFFFFFFF


def _clash(v: str, others) -> bool:
    return any(v in o or o in v for o in others)


def make_fill(m: PartMap, n: int) -> Fill:
    seed = seed_of(m.template, n)
    rng = random.Random(seed)
    font = rng.choice(FONTS)
    size = float(rng.choice((8.0, 8.5, 9.0, 9.5, 10.0)))
    values: dict[str, str] = {}
    for b in sorted(m.blanks, key=lambda b: b.field):
        width = b.box.x1 - b.box.x0
        for _ in range(DRAWS):
            v = draw(b.field, rng, width)
            if stringWidth(v, font, size) <= width - SLACK and not _clash(v, values.values()):
                values[b.field] = v
                break
        else:
            raise ValueTooLong(b.field)
    return Fill(fill_id(m.template, n), m.template, seed, values, font, size)


def fill_path(fid: str, fills_dir: Path = FILLS_DIR) -> Path:
    return Path(fills_dir) / f"{fid}.ttl"


def _node(fid: str) -> URIRef:
    return URIRef(f"urn:iladub:synthetic:fill:{fid}")


def write_fill(f: Fill, fills_dir: Path = FILLS_DIR) -> Path:
    p = fill_path(f.id, fills_dir)
    if p.exists():
        raise FileExistsError(p)
    g = Graph()
    g.bind("syn", SYN)
    g.bind("dcterms", DCTERMS)
    n = _node(f.id)
    g.add((n, RDF.type, SYN.Fill))
    g.add((n, SYN.fillId, Literal(f.id)))
    g.add((n, SYN.template, Literal(f.template)))
    g.add((n, SYN.seed, Literal(f.seed, datatype=XSD.integer)))
    g.add((n, SYN.font, Literal(f.font)))
    g.add((n, SYN.size, Literal(f.size, datatype=XSD.decimal)))
    g.add((n, DCTERMS.creator, Literal("François Rosselet")))
    g.add((n, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    for k in sorted(f.values):
        g.add((n, SYN.value, _vnode(g, f, k)))
    p.parent.mkdir(parents=True, exist_ok=True)
    head = ("# Fill spec (spec 2026-10-31 § 4.2): our own fake values, no template text.\n"
            "# CC-BY-4.0, François Rosselet.\n")
    p.write_text(head + g.serialize(format="turtle"), encoding="utf-8")
    return p


def _vnode(g: Graph, f: Fill, key: str):
    b = BNode()
    g.add((b, RDF.type, SYN.FillValue))
    g.add((b, SYN.field, Literal(key)))
    g.add((b, SYN.text, Literal(f.values[key])))
    return b


def load_fill(fid: str, fills_dir: Path = FILLS_DIR) -> Fill:
    g = Graph().parse(fill_path(fid, fills_dir), format="turtle")
    n = _node(fid)
    values = {str(g.value(b, SYN.field)): str(g.value(b, SYN.text)) for b in g.objects(n, SYN.value)}
    return Fill(str(g.value(n, SYN.fillId)), str(g.value(n, SYN.template)),
                int(g.value(n, SYN.seed)), values, str(g.value(n, SYN.font)),
                float(g.value(n, SYN.size)))


def write_all(templates, count: int = 3, maps_dir=None, fills_dir: Path = FILLS_DIR) -> list[Path]:
    """Write only absent fill files; never overwrite."""
    out = []
    for t in sorted(templates):
        m = load_map(t) if maps_dir is None else load_map(t, maps_dir)
        for n in range(1, count + 1):
            if not fill_path(fill_id(t, n), fills_dir).exists():
                out.append(write_fill(make_fill(m, n), fills_dir))
    return out
