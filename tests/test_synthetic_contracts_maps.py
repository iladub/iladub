"""Synthetic contract set Task 2: hand-authored part maps (spec § 4.1, § 4.5).

The maps are labels, field keys, page numbers and coordinates only — never template text.
The last test (local only) proves that against the downloaded templates themselves.
"""
import re
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import SH

from scripts.synthetic_contracts import manifest as mf
from scripts.synthetic_contracts import maps as mp

SYN = Namespace("https://w3id.org/iladub/synthetic#")
EX = mf.REPO / "examples" / "synthetic-contracts"
SHAPES = EX / "shapes.ttl"
VOCAB = EX / "synthetic.ttl"
NEGATIVE = EX / "negative" / "map-negative.ttl"
TEMPLATES = sorted(mf.load_manifest())

# A manifest template with no map yet, and why. Empty it in the change that adds the map.
PENDING: dict[str, str] = {}

# Dot-leader runs measured 2026-10-31 with pdfplumber `page.search(r"_{4,}|\.{6,}|…{2,}")`
# over every page (task-2 report). EXCLUDED names any run that is not a real blank, with its
# reason; each is subtracted explicitly. None was found in any of the four templates.
MEASURED_RUNS = {"gafta-48": 20, "gafta-79b": 17, "gafta-124": 15, "usda-ffp-cp": 45}
EXCLUDED: dict[str, dict[str, str]] = {"gafta-48": {}, "gafta-79b": {}, "gafta-124": {},
                                       "usda-ffp-cp": {}}
# Table parts: the page(s) of each, measured by hand from the ruling lines (task-2 report).
TABLE_PAGES = {"gafta-48": [], "gafta-79b": [(1,), (2,), (2,)], "gafta-124": [(6,)],
               "usda-ffp-cp": []}
DOC_PART = {"gafta-48": "contract-form", "gafta-79b": "contract-form", "gafta-124": "rules",
            "usda-ffp-cp": "charter-party"}


def _map_or_skip(tid):
    if not mp.map_path(tid).is_file():
        assert tid in PENDING, f"{tid} has no map and is not named in PENDING"
        pytest.skip(f"no map for {tid}: {PENDING[tid]}")
    return mp.load_map(tid)


def test_every_template_has_a_map_or_is_pending():
    present = {p.stem for p in mp.MAPS_DIR.glob("*.ttl")}
    assert present | set(PENDING) == set(TEMPLATES)
    assert not present & set(PENDING), "a mapped template is still listed as PENDING"


@pytest.mark.parametrize("tid", TEMPLATES)
def test_maps_conform(tid):
    _map_or_skip(tid)
    data = Graph().parse(mp.map_path(tid)).parse(VOCAB)
    ok, _, report = validate(data, shacl_graph=Graph().parse(SHAPES),
                             inference="rdfs", advanced=True)
    assert ok, report


def test_map_negative_fails():
    data = Graph().parse(NEGATIVE).parse(VOCAB)
    ok, rg, report = validate(data, shacl_graph=Graph().parse(SHAPES),
                              inference="rdfs", advanced=True)
    assert not ok
    results = list(rg.subjects(SH.resultSeverity, None))
    assert len(results) >= 3, report
    comps = {rg.value(r, SH.sourceConstraintComponent) for r in results}
    # the three planted faults, each caught by its own constraint kind
    assert SH.InConstraintComponent in comps, report          # part type outside the set
    assert SH.PatternConstraintComponent in comps, report     # field key with a space
    assert SH.SPARQLConstraintComponent in comps, report      # box with x1 < x0


def _inside(inner, outer):
    return (inner.page == outer.page and outer.x0 <= inner.x0 < inner.x1 <= outer.x1
            and outer.top <= inner.top < inner.bottom <= outer.bottom)


@pytest.mark.parametrize("tid", TEMPLATES)
def test_blanks_inside_their_part(tid):
    m = _map_or_skip(tid)
    parts = {p.id: p for p in m.parts}
    assert m.blanks
    for b in m.blanks:
        assert any(_inside(b.box, ob) for ob in parts[b.part].box), (tid, b.field)
    for p in m.parts:
        if p.parent is not None:
            for bx in p.box:
                assert any(_inside(bx, ob) for ob in parts[p.parent].box), (tid, p.id)


@pytest.mark.parametrize("tid", TEMPLATES)
def test_grids_rebuild_their_tables(tid):
    m = _map_or_skip(tid)
    tables = {p.id: p for p in m.parts if p.type == "table"}
    assert sorted(g.part for g in m.grids) == sorted(tables)
    for g in m.grids:
        (bx,) = [b for b in tables[g.part].box if b.page == g.page]
        for edges in (g.col_edges, g.row_edges):
            assert len(edges) >= 3 and list(edges) == sorted(set(edges))
        assert (g.col_edges[0], g.col_edges[-1]) == (bx.x0, bx.x1)
        assert (g.row_edges[0], g.row_edges[-1]) == (bx.top, bx.bottom)


@pytest.mark.parametrize("tid", TEMPLATES)
def test_counts_match_measurement(tid):
    m = _map_or_skip(tid)
    assert m.template == tid and m.review in ("draft", "owner-reviewed")
    assert len(m.blanks) == MEASURED_RUNS[tid] - len(EXCLUDED[tid])
    assert len({b.field for b in m.blanks}) == len(m.blanks)
    tables = [p for p in m.parts if p.type == "table"]
    assert sorted(tuple(b.page for b in t.box) for t in tables) == TABLE_PAGES[tid]
    (doc,) = [p for p in m.parts if p.parent is None]
    assert doc.type == DOC_PART[tid]
    assert [b.page for b in doc.box] == list(range(1, mf.load_manifest()[tid].pages + 1))
    assert all(t.parent == doc.id for t in tables)


def test_syn_terms_declared():
    vocab = Graph().parse(VOCAB)
    used = set()
    for f in [SHAPES, NEGATIVE, *mp.MAPS_DIR.glob("*.ttl")]:
        for t in Graph().parse(f):
            used |= {x for x in t if isinstance(x, URIRef) and str(x).startswith(str(SYN))}
    from rdflib import RDFS
    missing = [u for u in used if not (vocab.value(u, RDFS.label) and vocab.value(u, RDFS.comment))]
    assert not missing, missing


def _committed_files():
    roots = [EX, mf.REPO / "scripts" / "synthetic_contracts"]
    return [p for r in roots for p in r.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts]


@pytest.mark.parametrize("tid", TEMPLATES)
def test_no_template_text_committed(tid):
    pdf = mf.template_path(mf.load_manifest()[tid])
    if not pdf.is_file():
        pytest.skip(f"local only: {tid} template absent under synthetic/templates/")
    import pdfplumber
    lines = set()
    with pdfplumber.open(pdf) as doc:
        for page in doc.pages:
            for line in (page.extract_text() or "").splitlines():
                line = " ".join(line.split())
                if len(line.split()) >= 4:
                    lines.add(line)
    assert lines
    for f in _committed_files():
        text = " ".join(f.read_text(encoding="utf-8", errors="ignore").split())
        hits = [ln for ln in lines if ln in text]
        assert not hits, (str(f), hits[:3])
