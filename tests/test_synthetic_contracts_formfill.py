"""Synthetic contract set Task 4: the truth model and the form-fill flavour (spec § 4.3, § 4.5).

The truth tests are CI-runnable on hand-built `Truth` records. The form-fill tests are local only:
they skip when the templates are absent under synthetic/templates/. Their oracle is pdfplumber, an
independent reader of the OUTPUT PDF, used here in the tests only — never by the generator.
"""
import os
import subprocess
import sys
from collections import Counter
from functools import lru_cache
from io import BytesIO

import pytest
from pyshacl import validate
from rdflib import RDF, Graph, Namespace, URIRef
from rdflib.namespace import RDFS, SH

from scripts.synthetic_contracts import manifest as mf
from scripts.synthetic_contracts.fills import FILLS_DIR, load_fill
from scripts.synthetic_contracts.maps import Box, load_map
from scripts.synthetic_contracts.truth import PartTruth, Truth, ValueTruth

SYN = Namespace("https://w3id.org/iladub/synthetic#")
EX = mf.REPO / "examples" / "synthetic-contracts"
SHAPES = EX / "shapes.ttl"
VOCAB = EX / "synthetic.ttl"
NEGATIVE = EX / "negative" / "truth-negative.ttl"
FILLS = sorted(p.stem for p in FILLS_DIR.glob("*.ttl"))
SHA = "ed2e58f37433221155c43e33763d956807ff50a54b32ec97bf5fd5dd8aeb5103"
SHA2 = "76bb91193bf4607c848c16dc398d41ee7047700d7653fa6b42744491aea3fde4"


def _hand_built() -> Truth:
    # Awkward floats on purpose: an inexact sum, a tiny value that repr()s in exponent form.
    return Truth(
        doc_id="hand-1.mixed", flavour="mixed", templates=(SHA, SHA2), fills=("hand-1", "hand-2"),
        seed=42, review="draft",
        parts=(PartTruth("form", "contract-form", (Box(1, 0.0, 0.0, 595.32, 841.92),
                                                   Box(2, 0.0, 0.0, 595.32, 841.92)), None),
               PartTruth("form.table", "table", (Box(2, 10.1 + 0.2, 20.0, 300.0, 400.5),), "form"),
               PartTruth("blank.party.seller", "blank", (Box(1, 90.3, 262.9, 551.3, 272.9),), "form")),
        values=(ValueTruth("party.seller", 'Acme "Grain" \\ Co', Box(1, 92.1, 264.0, 180.25, 272.0)),
                ValueTruth("price.amount", "USD 1.5e-05", Box(2, 1e-05, 1.0, 50.0, 9.0))),
        transform=(0.9996573249755573, -0.026176948307873153, 1e-17, 0.026176948307873153,
                   0.9996573249755573, -3.5))


def _graph(t: Truth) -> Graph:
    return Graph().parse(data=t.to_turtle(), format="turtle")


def test_truth_roundtrips(tmp_path):
    t = _hand_built()
    p = tmp_path / "t.ttl"
    p.write_text(t.to_turtle(), encoding="utf-8")
    assert Truth.from_turtle(p) == t
    t2 = Truth("x.form-fill", "form-fill", (SHA,), ("x",), None, "owner-reviewed", (), (), None)
    p.write_text(t2.to_turtle(), encoding="utf-8")
    assert Truth.from_turtle(p) == t2


_DUMP = ("import sys; sys.path.insert(0, sys.argv[1]);"
         "from tests.test_synthetic_contracts_formfill import _hand_built;"
         "sys.stdout.write(_hand_built().to_turtle())")


def test_truth_turtle_is_byte_deterministic(tmp_path):
    t = _hand_built()
    a = t.to_turtle()
    assert a == t.to_turtle()
    p = tmp_path / "t.ttl"
    p.write_text(a, encoding="utf-8")
    assert Truth.from_turtle(p).to_turtle() == a
    # Fresh interpreters with different hash seeds: set/dict iteration order may change, bytes may not.
    outs = []
    for hs in ("1", "2", "3"):
        env = {**os.environ, "PYTHONHASHSEED": hs}
        outs.append(subprocess.run([sys.executable, "-c", _DUMP, str(mf.REPO)], env=env,
                                   capture_output=True, text=True, check=True).stdout)
    assert outs == [a, a, a]
    assert "_:" not in a and "[" not in a, "no blank nodes in truth"


def test_truth_has_no_pdf_hash():
    t = _hand_built()
    g = _graph(t)
    (doc,) = g.subjects(RDF.type, SYN.Truth)
    assert not list(g.objects(doc, SYN.sha256)), "the document node carries no sha256 (G6)"
    shas = {str(o) for s, o in g.subject_objects(SYN.sha256)}
    assert shas == set(t.templates)
    for s in g.subjects(SYN.sha256, None):
        assert (s, RDF.type, SYN.TemplateUse) in g


def test_truth_carries_licence_and_creator():
    g = _graph(_hand_built())
    (doc,) = g.subjects(RDF.type, SYN.Truth)
    assert str(g.value(doc, URIRef("http://purl.org/dc/terms/creator"))) == "François Rosselet"
    assert g.value(doc, URIRef("http://purl.org/dc/terms/license")) == URIRef(
        "https://creativecommons.org/licenses/by/4.0/")


def test_shift_pages():
    t = _hand_built()
    s = t.shift_pages(8)
    assert [b.page for p in s.parts for b in p.boxes] == [9, 10, 10, 9]
    assert [v.box.page for v in s.values] == [9, 10]
    assert s.parts[1].boxes[0].x0 == t.parts[1].boxes[0].x0
    assert (s.doc_id, s.templates, s.fills, s.transform) == (t.doc_id, t.templates, t.fills,
                                                             t.transform)


def test_truth_refuses_duplicate_part_ids():
    t = _hand_built()
    bad = Truth(t.doc_id, t.flavour, t.templates, t.fills, t.seed, t.review,
                t.parts + (PartTruth("form", "rules", (Box(3, 0, 0, 1, 1),), None),), t.values, None)
    with pytest.raises(ValueError, match="form"):
        bad.to_turtle()


def _conforms(g: Graph):
    return validate(g + Graph().parse(VOCAB), shacl_graph=Graph().parse(SHAPES),
                    inference="rdfs", advanced=True)


def test_truth_conforms():
    ok, _, report = _conforms(_graph(_hand_built()))
    assert ok, report


def test_truth_negative_fails():
    ok, rg, report = _conforms(Graph().parse(NEGATIVE))
    assert not ok
    results = list(rg.subjects(SH.resultSeverity, None))
    comps = {rg.value(r, SH.sourceConstraintComponent) for r in results}
    # the three planted faults, each caught by its own constraint kind
    assert SH.ClosedConstraintComponent in comps, report    # a sha256 on the document node (G6)
    assert SH.InConstraintComponent in comps, report        # a flavour outside the set
    assert SH.MaxCountConstraintComponent in comps, report  # a value with two boxes


def test_truth_syn_terms_declared():
    vocab = Graph().parse(VOCAB)
    used = set()
    for g in (_graph(_hand_built()), Graph().parse(NEGATIVE), Graph().parse(SHAPES)):
        for t in g:
            used |= {x for x in t if isinstance(x, URIRef) and str(x).startswith(str(SYN))}
    missing = [u for u in used if not (vocab.value(u, RDFS.label) and vocab.value(u, RDFS.comment))]
    assert not missing, missing


# ---------------------------------------------------------------- form fill (local only)

@lru_cache(maxsize=None)
def _render(fid):
    f = load_fill(fid)
    t = mf.load_manifest()[f.template]
    try:
        mf.verify(t)
    except mf.TemplateMissing:
        pytest.skip(f"local only: {t.id} template absent under synthetic/templates/")
    from scripts.synthetic_contracts.flavours.formfill import render_formfill
    return t, f, render_formfill(t, load_map(f.template), f)


def _key(c):
    return (c["text"], round(c["x0"], 1), round(c["top"], 1))


@pytest.mark.parametrize("fid", FILLS)
def test_formfill_values_where_truth_says(fid):
    # Substituted form (task-4 report): the value is drawn ON the blank's dot leaders, so a plain
    # crop(value.box) also returns the template's own dots. The oracle subtracts, per box, the chars
    # the TEMPLATE already has there (matched by text and position) and reads what the output adds.
    import pdfplumber
    t, f, (pdf, truth) = _render(fid)
    assert truth.flavour == "form-fill" and truth.fills == (f.id,) and truth.seed == f.seed
    assert {v.field: v.value for v in truth.values} == f.values
    with pdfplumber.open(BytesIO(pdf)) as out, pdfplumber.open(mf.template_path(t)) as tpl:
        for v in truth.values:
            bbox = (v.box.x0, v.box.top, v.box.x1, v.box.bottom)
            had = Counter(_key(c) for c in tpl.pages[v.box.page - 1].crop(bbox).chars)

            def added(o, had=had):
                if o.get("object_type") != "char":
                    return False
                k = _key(o)
                if had[k]:
                    had[k] -= 1
                    return False
                return True
            got = out.pages[v.box.page - 1].crop(bbox).filter(added).extract_text()
            assert got == v.value, (v.field, got)


@pytest.mark.parametrize("fid", FILLS)
def test_formfill_template_text_kept(fid):
    # Substituted form (task-4 report): drawn values interleave with the dot leaders they sit on, so
    # pdfplumber's WORD clustering of the output splits the template's leader words. The stronger
    # char-level form: every template glyph is in the output, same text, same page, same position.
    import pdfplumber
    t, f, (pdf, truth) = _render(fid)
    with pdfplumber.open(BytesIO(pdf)) as out, pdfplumber.open(mf.template_path(t)) as tpl:
        assert len(out.pages) == len(tpl.pages) == t.pages
        for po, pt in zip(out.pages, tpl.pages):
            # pypdfium2 stores page sizes as float32: 595.2 is written 595.20001 (1e-5 pt).
            assert [round(x, 3) for x in (po.width, po.height)] == \
                [round(x, 3) for x in (pt.width, pt.height)]
            want, have = Counter(map(_key, pt.chars)), Counter(map(_key, po.chars))
            assert want, "template page has text"
            assert not (want - have), (po.page_number, list((want - have).items())[:5])
            assert sum((have - want).values()) == sum(
                len(v.value) for v in truth.values if v.box.page == po.page_number)


@pytest.mark.parametrize("fid", FILLS)
def test_formfill_parts_copied_from_map(fid):
    t, f, (pdf, truth) = _render(fid)
    m = load_map(f.template)
    assert truth.templates == (t.sha256,) and truth.review == m.review and truth.transform is None
    assert [(p.id, p.type, p.boxes, p.parent) for p in truth.parts if p.type != "blank"] == \
        [(p.id, p.type, p.box, p.parent) for p in m.parts]
    assert [(p.id, p.boxes, p.parent) for p in truth.parts if p.type == "blank"] == \
        [(f"blank.{b.field}", (b.box,), b.part) for b in m.blanks]
    for v in truth.values:
        (b,) = [b for b in m.blanks if b.field == v.field]
        assert b.box.page == v.box.page and b.box.x0 <= v.box.x0 and v.box.x1 <= b.box.x1


@pytest.mark.parametrize("fid", FILLS[:1])
def test_formfill_truth_conforms_and_carries_no_pdf_hash(fid):
    import hashlib
    t, f, (pdf, truth) = _render(fid)
    g = _graph(truth)
    ok, _, report = _conforms(g)
    assert ok, report
    assert hashlib.sha256(pdf).hexdigest() not in truth.to_turtle()
    (doc,) = g.subjects(RDF.type, SYN.Truth)
    assert not list(g.objects(doc, SYN.sha256))
