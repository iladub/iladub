"""Build the synthetic contract set (spec 2026-10-31 § 4.4, § 4.5, § 6). Licence: Apache-2.0.

`build()` verifies every template against the manifest first (spec § 6: it refuses on a mismatch),
then renders each committed fill in the three flavours and each committed mixed document, writing
`synthetic/out/<doc_id>.pdf` (gitignored) and `examples/synthetic-contracts/truth/<doc_id>.ttl`
(committed). `doc_id` is `<fill-id>.<flavour>`, or the mixed document's id.

A mixed document (`compose`) concatenates parts the set already has (spec § 4.4): their pages are
appended in order (pypdfium2 `import_pages`), and their truth is shifted by the page count before
them (`Truth.shift_pages`). Each component's part ids and parent references are prefixed with its
letter (`a.`, `b.`, ...), so the composed record's part ids stay unique even when a fill is composed
with itself (m3). Value field keys are not prefixed: they name the blank a value fills, and pages
tell the components apart. A mixed record carries no seed (each fill's seed is in its own record)
and no transform (any scan matrix is already applied to its component's boxes and is recorded in
that component's own record). Its review state is "owner-reviewed" only if every component's is.

Justified PROCEDURAL (CLAUDE.md § 8): orchestration and PDF assembly — this module MAKES documents
and writes what it made. Nothing here reads a document to decide anything, and there is no
tolerance. No reader may call it (A3).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import pypdfium2 as pdfium
from rdflib import RDF, Graph, Namespace

from scripts.synthetic_contracts.fills import FILLS_DIR, load_fill
from scripts.synthetic_contracts.flavours.formfill import map_parts, render_formfill
from scripts.synthetic_contracts.manifest import (REPO, SYNTH_ROOT, Template, load_manifest,
                                                  template_path, verify)
from scripts.synthetic_contracts.maps import load_map
from scripts.synthetic_contracts.overlay import to_bytes
from scripts.synthetic_contracts.truth import PartTruth, Truth

SYN = Namespace("https://w3id.org/iladub/synthetic#")
EX = REPO / "examples" / "synthetic-contracts"
TRUTH_DIR = EX / "truth"
MIXED_DIR = EX / "mixed"
OUT_DIR = SYNTH_ROOT / "out"
FLAVOURS = ("form-fill", "word-export", "handwriting-scan")
UNFILLED = "unfilled"
LETTERS = "abcdefghijklmnopqrstuvwxyz"


@dataclass(frozen=True)
class Component:
    order: int
    flavour: str          # one of FLAVOURS, or "unfilled"
    fill: str | None      # a fill id, for a filled component
    template: str | None  # a template id, for an unfilled one


def load_mixed(path: Path) -> list[Component]:
    g = Graph().parse(Path(path), format="turtle")
    (doc,) = list(g.subjects(RDF.type, SYN.MixedDocument))
    out = []
    for n in g.objects(doc, SYN.component):
        fill, tpl = g.value(n, SYN.fillId), g.value(n, SYN.componentTemplate)
        out.append(Component(int(g.value(n, SYN.order)), str(g.value(n, SYN.componentFlavour)),
                             str(fill) if fill is not None else None,
                             str(tpl) if tpl is not None else None))
    out.sort(key=lambda c: c.order)
    for c in out:
        if (c.flavour == UNFILLED) != (c.fill is None) or (c.fill is None) == (c.template is None):
            raise ValueError(f"{path}: component {c.order} must be a fill with a flavour, "
                             "or an unfilled template")
        if c.flavour != UNFILLED and c.flavour not in FLAVOURS:
            raise ValueError(f"{path}: component {c.order}: unknown flavour {c.flavour}")
    return out


def mixed_id(path: Path) -> str:
    g = Graph().parse(Path(path), format="turtle")
    (doc,) = list(g.subjects(RDF.type, SYN.MixedDocument))
    return str(g.value(doc, SYN.mixedId))


def unfilled(t: Template) -> tuple[bytes, Truth]:
    """A template's pages as-is; truth = its map's parts (blanks included), no values."""
    verify(t)
    m = load_map(t.id)
    return template_path(t).read_bytes(), Truth(
        doc_id=f"{t.id}.{UNFILLED}", flavour="form-fill", templates=(t.sha256,), fills=(),
        seed=None, review=m.review, parts=map_parts(m), values=(), transform=None)


def _prefixed(t: Truth, prefix: str) -> Truth:
    return replace(t, parts=tuple(
        PartTruth(prefix + p.id, p.type, p.boxes, None if p.parent is None else prefix + p.parent)
        for p in t.parts))


def compose(parts: list[tuple[bytes, Truth]], doc_id: str = "mixed") -> tuple[bytes, Truth]:
    if not parts or len(parts) > len(LETTERS):
        raise ValueError(f"compose needs 1..{len(LETTERS)} parts, got {len(parts)}")
    out = pdfium.PdfDocument.new()
    keep, shifted = [], []
    for k, (pdf, t) in enumerate(parts):
        src = pdfium.PdfDocument(pdf)
        n = len(src)
        top = max((b.page for p in t.parts for b in p.boxes), default=0)
        top = max([top] + [v.box.page for v in t.values])
        if top > n:
            raise ValueError(f"{t.doc_id}: truth names page {top}, PDF has {n} page(s)")
        shifted.append(_prefixed(t.shift_pages(len(out)), f"{LETTERS[k]}."))
        out.import_pages(src)
        keep.append(src)
    truths = [t for _, t in parts]
    reviews = {t.review for t in truths}
    composed = Truth(
        doc_id=doc_id, flavour="mixed",
        templates=tuple(s for t in truths for s in t.templates),
        fills=tuple(f for t in truths for f in t.fills), seed=None,
        review="owner-reviewed" if reviews == {"owner-reviewed"} else "draft",
        parts=tuple(p for t in shifted for p in t.parts),
        values=tuple(v for t in shifted for v in t.values), transform=None)
    pdf = to_bytes(out)
    del keep
    return pdf, composed


def _render(flavour: str, t: Template, fid: str) -> tuple[bytes, Truth]:
    m, f = load_map(t.id), load_fill(fid)
    if flavour == "form-fill":
        return render_formfill(t, m, f)
    if flavour == "handwriting-scan":
        from scripts.synthetic_contracts.flavours.handwriting import render_handwriting
        return render_handwriting(t, m, f)
    if flavour == "word-export":
        from scripts.synthetic_contracts.flavours.wordexport import render_wordexport
        return render_wordexport(t, m, f)
    raise ValueError(f"unknown flavour {flavour}")


def _write(doc_id: str, pdf: bytes, truth: Truth, out_dir: Path, truth_dir: Path) -> Path:
    if truth.doc_id != doc_id:
        raise ValueError(f"truth {truth.doc_id} written as {doc_id}")
    text = truth.to_turtle()
    out = out_dir / f"{doc_id}.pdf"
    out.write_bytes(pdf)
    (truth_dir / f"{doc_id}.ttl").write_text(text, encoding="utf-8")
    print(f"  built {doc_id} ({len(pdfium.PdfDocument(pdf))} pages)")
    return out


def build(root: Path = SYNTH_ROOT, truth_dir: Path = TRUTH_DIR, fills_dir: Path = FILLS_DIR,
          mixed_dir: Path = MIXED_DIR) -> list[Path]:
    """Verify every template, then build every fill x flavour and every mixed document."""
    templates = load_manifest()
    for t in templates.values():  # refuse before writing anything (spec § 6)
        verify(t, root)
    out_dir = Path(root) / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(truth_dir).mkdir(parents=True, exist_ok=True)
    made: dict[str, tuple[bytes, Truth]] = {}
    written = []
    for fid in sorted(p.stem for p in Path(fills_dir).glob("*.ttl")):
        t = templates[load_fill(fid, fills_dir).template]
        for fl in FLAVOURS:
            doc_id = f"{fid}.{fl}"
            made[doc_id] = _render(fl, t, fid)
            written.append(_write(doc_id, *made[doc_id], out_dir, truth_dir))
    for spec in sorted(Path(mixed_dir).glob("*.ttl")):
        mid = mixed_id(spec)
        comps = []
        for c in load_mixed(spec):
            if c.flavour == UNFILLED:
                comps.append(unfilled(templates[c.template]))
            else:
                comps.append(made[f"{c.fill}.{c.flavour}"])
        written.append(_write(mid, *compose(comps, doc_id=mid), out_dir, truth_dir))
    return written
