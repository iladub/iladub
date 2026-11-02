"""The truth record of one generated PDF (spec 2026-10-31 § 4.5). Licence: Apache-2.0.

A truth record says, for one generated document: which template(s) by manifest sha256, which
flavour, which fill(s) and seed, the map's review state; every part (type, page boxes, parent) and
every filled value (field, text, box) — in the OUTPUT document's own coordinates (points, top-left
origin, 1-based pages). It never records the output PDF's hash (G6), and it carries no template
text: part ids, field keys and our own fake values only.

Serialisation is hand-written Turtle and byte-deterministic: every node has a stable IRI derived
from the document id and the node's position (no blank nodes, whose labels and order churn),
subjects and predicates are emitted sorted, and decimals are written from the float's shortest
round-trip repr, so `from_turtle(to_turtle(t)) == t` exactly.

Justified PROCEDURAL (CLAUDE.md § 8): this module records what the generator did — serialisation
and parsing, raw extraction, no decision. It never reads a generated document. Nothing here is a
tolerance. No reader may call it (A3).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path

from rdflib import RDF, Graph, Literal, Namespace, URIRef

from scripts.synthetic_contracts.maps import Box

SYN = Namespace("https://w3id.org/iladub/synthetic#")
CREATOR = "François Rosselet"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
FLAVOURS = ("form-fill", "word-export", "handwriting-scan", "mixed")


@dataclass(frozen=True)
class PartTruth:
    id: str
    type: str
    boxes: tuple[Box, ...]
    parent: str | None


@dataclass(frozen=True)
class ValueTruth:
    field: str
    value: str
    box: Box


@dataclass(frozen=True)
class Truth:
    doc_id: str
    flavour: str
    templates: tuple[str, ...]  # manifest sha256s, in document order
    fills: tuple[str, ...]      # fill ids, in document order
    seed: int | None
    review: str
    parts: tuple[PartTruth, ...]
    values: tuple[ValueTruth, ...]
    transform: tuple[float, ...] | None

    def shift_pages(self, offset: int) -> Truth:
        def mv(b: Box) -> Box:
            return replace(b, page=b.page + offset)
        return replace(
            self,
            parts=tuple(replace(p, boxes=tuple(mv(b) for b in p.boxes)) for p in self.parts),
            values=tuple(replace(v, box=mv(v.box)) for v in self.values))

    def to_turtle(self) -> str:
        return _to_turtle(self)

    @staticmethod
    def from_turtle(path: Path) -> Truth:
        return _from_turtle(Graph().parse(Path(path), format="turtle"))


# ------------------------------------------------------------------ writing

def _dec(x: float) -> str:
    s = format(Decimal(repr(float(x))), "f")
    return s if "." in s else s + ".0"


def _str(s: str) -> str:
    return Literal(s).n3()


def doc_iri(doc_id: str) -> str:
    return f"urn:iladub:synthetic:truth:{doc_id}"


def _box_preds(b: Box) -> list[tuple[str, str]]:
    return [("a", "syn:Box"), ("syn:page", str(b.page)), ("syn:x0", _dec(b.x0)),
            ("syn:top", _dec(b.top)), ("syn:x1", _dec(b.x1)), ("syn:bottom", _dec(b.bottom))]


def _to_turtle(t: Truth) -> str:
    ids = [p.id for p in t.parts]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise ValueError(f"truth {t.doc_id}: part ids not unique: {', '.join(dup)}")
    doc = doc_iri(t.doc_id)
    part_iri = {p.id: f"{doc}:part:{n:04d}" for n, p in enumerate(t.parts, 1)}
    nodes: dict[str, list[tuple[str, str]]] = {}
    d = [("a", "syn:Truth"), ("dcterms:creator", _str(CREATOR)), ("dcterms:license", f"<{LICENSE}>"),
         ("syn:docId", _str(t.doc_id)), ("syn:flavour", _str(t.flavour)),
         ("syn:review", _str(t.review))]
    if t.seed is not None:
        d.append(("syn:seed", str(int(t.seed))))
    if t.transform is not None:
        d.append(("syn:transform", _str(" ".join(_dec(x) for x in t.transform))))
    for n, sha in enumerate(t.templates, 1):
        iri = f"{doc}:template:{n:04d}"
        d.append(("syn:usesTemplate", f"<{iri}>"))
        nodes[iri] = [("a", "syn:TemplateUse"), ("syn:order", str(n)), ("syn:sha256", _str(sha))]
    for n, fid in enumerate(t.fills, 1):
        iri = f"{doc}:fill:{n:04d}"
        d.append(("syn:usesFill", f"<{iri}>"))
        nodes[iri] = [("a", "syn:FillUse"), ("syn:order", str(n)), ("syn:fillId", _str(fid))]
    nodes[doc] = d
    for n, p in enumerate(t.parts, 1):
        iri = part_iri[p.id]
        preds = [("a", "syn:PartTruth"), ("syn:inDocument", f"<{doc}>"), ("syn:order", str(n)),
                 ("syn:partId", _str(p.id)), ("syn:partType", _str(p.type))]
        if p.parent is not None:
            if p.parent not in part_iri:
                raise ValueError(f"truth {t.doc_id}: part {p.id} has unknown parent {p.parent}")
            preds.append(("syn:parent", f"<{part_iri[p.parent]}>"))
        for k, b in enumerate(p.boxes, 1):
            biri = f"{iri}:box:{k:04d}"
            preds.append(("syn:box", f"<{biri}>"))
            nodes[biri] = _box_preds(b)
        nodes[iri] = preds
    for n, v in enumerate(t.values, 1):
        iri = f"{doc}:value:{n:04d}"
        biri = f"{iri}:box"
        nodes[iri] = [("a", "syn:ValueTruth"), ("syn:inDocument", f"<{doc}>"), ("syn:order", str(n)),
                      ("syn:field", _str(v.field)), ("syn:text", _str(v.value)),
                      ("syn:box", f"<{biri}>")]
        nodes[biri] = _box_preds(v.box)
    out = ["# Truth record (spec 2026-10-31 § 4.5), written by the generator; never read by a router.",
           "# Output-page coordinates. Our own part ids, field keys and fake values; no template text.",
           "# CC-BY-4.0, François Rosselet.",
           "@prefix dcterms: <http://purl.org/dc/terms/> .",
           "@prefix syn: <https://w3id.org/iladub/synthetic#> .", ""]
    for s in sorted(nodes):
        preds = sorted(nodes[s], key=lambda po: (po[0] != "a", po[0], po[1]))
        body = " ;\n    ".join(f"{p} {o}" for p, o in preds)
        out.append(f"<{s}> {body} .\n")
    return "\n".join(out)


# ------------------------------------------------------------------ reading

def _box(g: Graph, n) -> Box:
    return Box(int(g.value(n, SYN.page)), float(g.value(n, SYN.x0)), float(g.value(n, SYN.top)),
               float(g.value(n, SYN.x1)), float(g.value(n, SYN.bottom)))


def _ordered(g: Graph, nodes):
    return sorted(nodes, key=lambda n: int(g.value(n, SYN.order)))


def _from_turtle(g: Graph) -> Truth:
    (doc,) = list(g.subjects(RDF.type, SYN.Truth))
    seed = g.value(doc, SYN.seed)
    tr = g.value(doc, SYN.transform)
    members = list(g.subjects(SYN.inDocument, doc))
    parts_n = _ordered(g, [n for n in members if (n, RDF.type, SYN.PartTruth) in g])
    values_n = _ordered(g, [n for n in members if (n, RDF.type, SYN.ValueTruth) in g])
    pid = {n: str(g.value(n, SYN.partId)) for n in parts_n}
    parts = []
    for n in parts_n:
        parent = g.value(n, SYN.parent)
        boxes = tuple(_box(g, b) for b in sorted(g.objects(n, SYN.box), key=str))
        parts.append(PartTruth(pid[n], str(g.value(n, SYN.partType)), boxes,
                               pid[parent] if parent is not None else None))
    values = [ValueTruth(str(g.value(n, SYN.field)), str(g.value(n, SYN.text)),
                         _box(g, g.value(n, SYN.box))) for n in values_n]
    return Truth(
        doc_id=str(g.value(doc, SYN.docId)), flavour=str(g.value(doc, SYN.flavour)),
        templates=tuple(str(g.value(n, SYN.sha256))
                        for n in _ordered(g, g.objects(doc, SYN.usesTemplate))),
        fills=tuple(str(g.value(n, SYN.fillId)) for n in _ordered(g, g.objects(doc, SYN.usesFill))),
        seed=int(seed) if seed is not None else None, review=str(g.value(doc, SYN.review)),
        parts=tuple(parts), values=tuple(values),
        transform=tuple(float(x) for x in str(tr).split()) if tr is not None else None)
