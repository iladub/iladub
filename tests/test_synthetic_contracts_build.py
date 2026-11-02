"""Synthetic contract set Task 7: build, mixed documents, agreement (spec § 4.4, § 4.5).

`compose` and `agree` tests are CI-runnable on hand-built truths and tiny reportlab PDFs. The
committed-truth tests run wherever the repo is checked out (the truth files are committed). Only
`test_build_counts` is local: it skips when `synthetic/out/` (gitignored) is absent.
"""
from collections import Counter
from io import BytesIO

import pypdfium2 as pdfium
import pytest
from pyshacl import validate
from rdflib import Graph
from reportlab.pdfgen.canvas import Canvas

from scripts.synthetic_contracts import manifest as mf
from scripts.synthetic_contracts.agreement import agree
from scripts.synthetic_contracts.build import (MIXED_DIR, OUT_DIR, TRUTH_DIR, compose,
                                               load_mixed)
from scripts.synthetic_contracts.fills import FILLS_DIR
from scripts.synthetic_contracts.flavours.formfill import map_parts
from scripts.synthetic_contracts.maps import Box, load_map
from scripts.synthetic_contracts.truth import PartTruth, Truth, ValueTruth

EX = mf.REPO / "examples" / "synthetic-contracts"
SHAPES = EX / "shapes.ttl"
VOCAB = EX / "synthetic.ttl"
FILLS = sorted(p.stem for p in FILLS_DIR.glob("*.ttl"))
FLAVOURS = ("form-fill", "word-export", "handwriting-scan")
MIXED = ("m1", "m2", "m3")
SHA = "ed2e58f37433221155c43e33763d956807ff50a54b32ec97bf5fd5dd8aeb5103"
SHA2 = "76bb91193bf4607c848c16dc398d41ee7047700d7653fa6b42744491aea3fde4"


def _pdf(pages: int) -> bytes:
    buf = BytesIO()
    c = Canvas(buf, pagesize=(595.0, 842.0), invariant=1)
    for n in range(pages):
        c.drawString(72, 720, f"page {n + 1}")
        c.showPage()
    c.save()
    return buf.getvalue()


def _truth(doc_id: str, pages: int, sha: str = SHA, fill: str = "hand-1",
           value: str = "Acme Grain Co") -> Truth:
    whole = tuple(Box(p, 0.0, 0.0, 595.0, 842.0) for p in range(1, pages + 1))
    return Truth(
        doc_id=doc_id, flavour="form-fill", templates=(sha,), fills=(fill,), seed=7, review="draft",
        parts=(PartTruth("form", "contract-form", whole, None),
               PartTruth("blank.party.seller", "blank", (Box(pages, 90.0, 260.0, 550.0, 272.0),),
                         "form")),
        values=(ValueTruth("party.seller", value, Box(pages, 92.0, 262.0, 180.0, 271.0)),),
        transform=None)


# ------------------------------------------------------------------ compose (CI)

def test_mixed_truth_offsets_pages():
    first, second = _truth("x.form-fill", 3), _truth("y.form-fill", 2, sha=SHA2, fill="hand-2")
    pdf, t = compose([(_pdf(3), first), (_pdf(2), second)], doc_id="mx")
    assert len(pdfium.PdfDocument(pdf)) == 5
    parts = {p.id: p for p in t.parts}
    # the second part's pages start at the first's page count + 1
    assert [b.page for b in parts["b.form"].boxes] == [4, 5]
    assert [b.page for b in parts["a.form"].boxes] == [1, 2, 3]
    assert parts["b.blank.party.seller"].boxes[0].page == 5
    assert parts["a.blank.party.seller"].boxes[0].page == 3
    assert sorted(v.box.page for v in t.values) == [3, 5]
    assert t.templates == (SHA, SHA2) and t.fills == ("hand-1", "hand-2")
    assert t.flavour == "mixed" and t.doc_id == "mx"


def test_compose_prefixes_part_ids_and_parents():
    # m3 is one fill composed with itself: without the prefix its part ids would collide.
    a, b = _truth("x.form-fill", 2), _truth("x.handwriting-scan", 2)
    _, t = compose([(_pdf(2), a), (_pdf(2), b)], doc_id="mx")
    ids = [p.id for p in t.parts]
    assert len(ids) == len(set(ids)) == 4
    assert {p.id: p.parent for p in t.parts} == {
        "a.form": None, "a.blank.party.seller": "a.form",
        "b.form": None, "b.blank.party.seller": "b.form"}
    Graph().parse(data=t.to_turtle(), format="turtle")  # to_turtle refuses duplicate ids


def test_compose_refuses_page_count_disagreement():
    with pytest.raises(ValueError):
        compose([(_pdf(2), _truth("x.form-fill", 3))], doc_id="mx")


# ------------------------------------------------------------------ agree (CI)

def test_agree_identical_ignores_coordinates():
    a = _truth("x.form-fill", 2)
    b = Truth(**{**a.__dict__, "doc_id": "x.word-export",
                 "values": (ValueTruth("party.seller", "Acme Grain Co",
                                       Box(1, 1.0, 2.0, 3.0, 4.0)),)})
    assert agree(a, b) == []


def test_agree_reports_value_and_part_differences():
    a = _truth("x.form-fill", 2)
    b = _truth("x.word-export", 2, value="Other Grain Co")
    diffs = agree(a, b)
    assert diffs and any("Other Grain Co" in d for d in diffs)
    c = Truth(**{**a.__dict__, "parts": a.parts + (PartTruth("t", "table", (Box(1, 0, 0, 1, 1),),
                                                             "form"),)})
    assert any("table" in d for d in agree(a, c))


# ------------------------------------------------------------------ mixed specs (CI)

def test_mixed_specs_are_the_three_of_spec_4_4():
    got = {m: [(c.fill or c.template, c.flavour) for c in load_mixed(MIXED_DIR / f"{m}.ttl")]
           for m in MIXED}
    assert got == {
        "m1": [("gafta-48-1", "form-fill"), ("gafta-124", "unfilled")],
        "m2": [("gafta-79b-2", "word-export"), ("usda-ffp-cp-2", "form-fill")],
        "m3": [("gafta-48-3", "form-fill"), ("gafta-48-3", "handwriting-scan")]}


# ------------------------------------------------------------------ committed truth

def _truth_files():
    return sorted(TRUTH_DIR.glob("*.ttl"))


def _expected_ids():
    return sorted([f"{f}.{fl}" for f in FILLS for fl in FLAVOURS] + list(MIXED))


def test_committed_truth_is_the_39():
    assert len(FILLS) == 12
    assert sorted(p.stem for p in _truth_files()) == _expected_ids()


def test_committed_truth_conforms():
    files = _truth_files()
    assert len(files) == 39
    g = Graph()
    for p in files:
        g.parse(p, format="turtle")
    ok, _, report = validate(g, shacl_graph=Graph().parse(SHAPES), ont_graph=Graph().parse(VOCAB),
                             inference="rdfs", advanced=True)
    assert ok, report


def test_committed_truth_templates_in_manifest():
    shas = {t.sha256 for t in mf.load_manifest().values()}
    for p in _truth_files():
        t = Truth.from_turtle(p)
        assert t.templates and set(t.templates) <= shas, p.name


@pytest.mark.parametrize("fid", FILLS)
def test_agreement_across_flavours(fid):
    paths = [TRUTH_DIR / f"{fid}.{fl}.ttl" for fl in FLAVOURS]
    if not all(p.is_file() for p in paths):
        pytest.skip(f"truth for {fid} absent")
    ff, we, hw = (Truth.from_turtle(p) for p in paths)
    assert agree(ff, we) == []
    assert agree(ff, hw) == []
    assert agree(we, hw) == []
    assert len(ff.values) > 0


def test_mixed_truth_composes_its_components():
    for m in MIXED:
        t = Truth.from_turtle(TRUTH_DIR / f"{m}.ttl")
        assert t.flavour == "mixed"
        comps = load_mixed(MIXED_DIR / f"{m}.ttl")
        types = Counter(p.type for p in t.parts)
        want = Counter()
        for c in comps:
            if c.flavour == "unfilled":
                want += Counter(p.type for p in map_parts(load_map(c.template)))
            else:
                ct = Truth.from_turtle(TRUTH_DIR / f"{c.fill}.{c.flavour}.ttl")
                want += Counter(p.type for p in ct.parts)
        assert types == want, m
        assert {p.id.split(".", 1)[0] for p in t.parts} == set("abcdefgh"[:len(comps)]), m


# ------------------------------------------------------------------ the built set (local)

def test_build_counts():
    if not OUT_DIR.is_dir():
        pytest.skip("local only: synthetic/out/ absent (run the build)")
    pdfs = sorted(p.stem for p in OUT_DIR.glob("*.pdf"))
    assert pdfs == _expected_ids()
    assert len(_truth_files()) == 39
    shas = {t.sha256 for t in mf.load_manifest().values()}
    for p in _truth_files():
        t = Truth.from_turtle(p)
        assert set(t.templates) <= shas
        n = len(pdfium.PdfDocument(str(OUT_DIR / f"{p.stem}.pdf")))
        assert max(b.page for part in t.parts for b in part.boxes) == n, p.stem


# ------------------------------------------------------------------ mixed spec shapes (CI)

def _validate(*files):
    g = Graph()
    for f in files:
        g.parse(f, format="turtle")
    return validate(g, shacl_graph=Graph().parse(SHAPES), ont_graph=Graph().parse(VOCAB),
                    inference="rdfs", advanced=True)


def test_mixed_specs_conform():
    ok, _, report = _validate(*(MIXED_DIR / f"{m}.ttl" for m in MIXED))
    assert ok, report


def test_mixed_negative_fails_each_planted_fault():
    ok, rg, report = _validate(EX / "negative" / "mixed-negative.ttl")
    assert not ok
    from rdflib.namespace import SH
    paths = {str(rg.value(r, SH.resultPath)) for r in rg.subjects(SH.resultSeverity, SH.Violation)}
    comps = {str(rg.value(r, SH.sourceConstraintComponent))
             for r in rg.subjects(SH.resultSeverity, SH.Violation)}
    assert "https://w3id.org/iladub/synthetic#component" in paths            # one component
    assert "https://w3id.org/iladub/synthetic#componentFlavour" in paths     # photocopy
    assert str(SH.XoneConstraintComponent) in comps                          # fill and template


def test_mixed_syn_terms_declared():
    from rdflib import RDFS, URIRef
    vocab = Graph().parse(VOCAB)
    syn = "https://w3id.org/iladub/synthetic#"
    used = set()
    for f in [*MIXED_DIR.glob("*.ttl"), EX / "negative" / "mixed-negative.ttl"]:
        for t in Graph().parse(f):
            used |= {x for x in t if isinstance(x, URIRef) and str(x).startswith(syn)}
    missing = [u for u in used if not (vocab.value(u, RDFS.label) and vocab.value(u, RDFS.comment))]
    assert not missing, missing


# ------------------------------------------------------------------ build's root (CI)

def test_build_refuses_a_non_default_root(tmp_path):
    # The flavours read their templates under SYNTH_ROOT; another root would verify one set of
    # templates and render another, so build refuses before verifying or writing anything.
    from scripts.synthetic_contracts.build import NonDefaultRoot, build
    with pytest.raises(NonDefaultRoot, match="build root must be"):
        build(tmp_path)
    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------------------------ committed truth is current (CI; final review I3)

@pytest.mark.parametrize("fid", FILLS)
def test_committed_formfill_truth_is_current(fid):
    """Each committed `<fid>.form-fill.ttl` is byte-for-byte what its committed map and fill produce.
    The form-fill record needs no template file (`formfill_truth`), so this runs in CI; a box edit
    or a review flip in a map, or a regenerated fill, without a rebuild fails here."""
    from scripts.synthetic_contracts.fills import load_fill
    from scripts.synthetic_contracts.flavours.formfill import formfill_truth

    f = load_fill(fid)
    t = mf.load_manifest()[f.template]
    want = formfill_truth(t, load_map(f.template), f).to_turtle()
    assert (TRUTH_DIR / f"{fid}.form-fill.ttl").read_text(encoding="utf-8") == want, fid


def test_committed_truth_review_is_its_maps_review():
    """Every truth record's syn:review is its maps' review state: "owner-reviewed" only if every map
    of every template it was made from is (the rule `compose` applies to mixed records), else
    "draft". The other flavours' records copy `m.review` too, so this covers what CI cannot rebuild."""
    by_sha = {t.sha256: t.id for t in mf.load_manifest().values()}
    files = _truth_files()
    assert len(files) == 39
    for p in files:
        tr = Truth.from_turtle(p)
        reviews = {load_map(by_sha[s]).review for s in tr.templates}
        want = "owner-reviewed" if reviews == {"owner-reviewed"} else "draft"
        assert tr.review == want, (p.name, tr.review, reviews)


# ------------------------------------------------------------------ CLI refusals (CI; final review minor 2)

def _boom(exc):
    def f(*a, **k):
        raise exc
    return f


@pytest.mark.parametrize("exc", [
    mf.TemplateMissing("gafta-48"),
    mf.TemplateMismatch("gafta-48", "a" * 64, "b" * 64),
    __import__("scripts.synthetic_contracts.word", fromlist=["WordFailed"]).WordFailed("no Word"),
    __import__("subprocess").TimeoutExpired(["osascript"], 330),
    __import__("scripts.synthetic_contracts.flavours.wordexport",
               fromlist=["BuildRefused"]).BuildRefused("page 3 overflowed"),
], ids=["missing", "mismatch", "word-failed", "timeout", "refused"])
def test_build_refusal_is_one_line_and_exit_1(exc, monkeypatch, capsys):
    from scripts.synthetic_contracts import __main__ as cli
    from scripts.synthetic_contracts import build as b

    monkeypatch.setattr(b, "build", _boom(exc))
    assert cli.main(["build"]) == 1
    out = capsys.readouterr()
    assert out.out == "" and out.err.count("\n") == 1 and out.err.startswith("build refused: "), out
    assert str(exc).splitlines()[0] in out.err
