"""Synthetic contract set Task 6: the Word export flavour (spec 2026-10-31 § 4.3; owner decisions 6, 10).

`write_docx` and `locate` tests are CI-runnable (stdlib zip/XML, reportlab-made PDFs). The Word tests
are local only: they skip when Microsoft Word is absent or the templates are absent under
synthetic/templates/. Their oracle is pdfplumber reading the OUTPUT PDF Word exported, and the
template itself — used here in the tests, never by a reader.
"""
import sys
import zipfile
from collections import Counter
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from pyshacl import validate
from rdflib import Graph, Literal, URIRef

from scripts.synthetic_contracts import manifest as mf
from scripts.synthetic_contracts.docx_writer import Heading, Paragraph, Run, Table, write_docx
from scripts.synthetic_contracts.fills import FILLS_DIR, load_fill
from scripts.synthetic_contracts.locate import Ambiguous, NotFound, locate
from scripts.synthetic_contracts.maps import Box, load_map

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
EX = mf.REPO / "examples" / "synthetic-contracts"
FILLS = sorted(p.stem for p in FILLS_DIR.glob("*.ttl"))
WORD_APP = Path("/Applications/Microsoft Word.app")
SYN = "https://w3id.org/iladub/synthetic#"
MIN_WORDS = 0.95  # owner decision 10 as the brief states it: >= 95 % of each part's words carried


def test_docx_opens(tmp_path):
    blocks = [Heading("A heading", 1),
              Paragraph((Run("plain "), Run("bold", bold=True), Run(" & <esc>", italic=True)),
                        page_break_before=False),
              Table(((("r1c1",), ("r1c2", "second line")), (("r2c1",), ())), (100.0, 150.0)),
              Paragraph((Run("after"),), page_break_before=True),
              Table(((("only",),),), (200.0,))]
    p = tmp_path / "t.docx"
    write_docx(blocks, p)
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        names = set(z.namelist())
        assert {"[Content_Types].xml", "_rels/.rels", "word/document.xml"} <= names
        root = ET.fromstring(z.read("word/document.xml"))
        for n in names:
            if n.endswith(".xml") or n.endswith(".rels"):
                ET.fromstring(z.read(n))  # every part parses
    body = root.find(f"{W}body")
    assert len(body.findall(f"{W}tbl")) == sum(isinstance(b, Table) for b in blocks) == 2
    text = "".join(t.text or "" for t in root.iter(f"{W}t"))
    assert "bold" in text and " & <esc>" in text and "second line" in text
    assert len(root.findall(f".//{W}br[@{W}type='page']")) == 1


def _two_line_pdf(path, lines):
    from reportlab.pdfgen.canvas import Canvas
    c = Canvas(str(path), pagesize=(400, 300), invariant=1)
    c.setFont("Helvetica", 12)
    for i, s in enumerate(lines):
        c.drawString(40, 250 - 30 * i, s)
    c.save()


def test_locate_finds_once(tmp_path):
    p = tmp_path / "t.pdf"
    _two_line_pdf(p, ["Alpha ZQX-417 beta", "Gamma delta"])
    b = locate(p, "ZQX-417")
    assert isinstance(b, Box) and b.page == 1
    assert 40 < b.x0 < b.x1 < 200 and 300 - 250 - 12 < b.top < b.bottom < 300 - 250 + 4


def test_locate_refuses_ambiguous(tmp_path):
    p = tmp_path / "t.pdf"
    _two_line_pdf(p, ["Port of Kelvra-9", "then Port of Kelvra-9 again"])
    with pytest.raises(Ambiguous) as e:
        locate(p, "Port of Kelvra-9")
    assert e.value.needle == "Port of Kelvra-9" and e.value.n == 2


def test_locate_refuses_missing(tmp_path):
    p = tmp_path / "t.pdf"
    _two_line_pdf(p, ["Alpha", "Beta"])
    with pytest.raises(NotFound) as e:
        locate(p, "Omega-77")
    assert e.value.needle == "Omega-77"
    with pytest.raises(NotFound):  # a needle split across two lines is not found, never joined
        locate(p, "Alpha Beta")


def test_drawn_tables_groups_rects_by_exact_contact():
    """CI: two touching-rect grids and one lone rect are three pieces, with their exact extents."""
    import pdfplumber
    from reportlab.pdfgen.canvas import Canvas

    from scripts.synthetic_contracts.flavours.wordexport import drawn_tables

    buf = BytesIO()
    c = Canvas(buf, pagesize=(600.0, 800.0), invariant=1)
    for x0, top, w, h in ((100, 100, 200, 1), (100, 101, 1, 50), (299, 101, 1, 50), (100, 151, 200, 1),
                          (100, 300, 300, 1), (100, 301, 1, 20), (100, 321, 300, 1),
                          (500, 600, 10, 10)):
        c.rect(x0, 800 - top - h, w, h, stroke=0, fill=1)  # reportlab is bottom-left origin
    c.showPage()
    c.save()
    with pdfplumber.open(BytesIO(buf.getvalue())) as pdf:
        got = drawn_tables(pdf.pages[0])
    assert [(b.page, b.x0, b.top, b.x1, b.bottom) for b in got] == [
        (1, 100, 100, 300, 152), (1, 100, 300, 400, 322), (1, 500, 600, 510, 610)]


# ---------------------------------------------------------------- Word (local only)

def _need_word():
    if sys.platform != "darwin" or not WORD_APP.is_dir():
        pytest.skip("local only: Microsoft Word for macOS is absent")


@lru_cache(maxsize=None)
def _render(fid):
    _need_word()
    f = load_fill(fid)
    t = mf.load_manifest()[f.template]
    try:
        mf.verify(t)
    except mf.TemplateMissing:
        pytest.skip(f"local only: {t.id} template absent under synthetic/templates/")
    from scripts.synthetic_contracts.flavours.wordexport import render_wordexport
    return t, f, render_wordexport(t, load_map(f.template), f)


@pytest.mark.parametrize("fid", FILLS)
def test_wordexport_values_where_truth_says(fid):
    import pdfplumber
    t, f, (pdf, truth) = _render(fid)
    assert truth.flavour == "word-export" and truth.fills == (f.id,) and truth.seed == f.seed
    assert {v.field: v.value for v in truth.values} == f.values
    with pdfplumber.open(BytesIO(pdf)) as out:
        for v in truth.values:
            page = out.pages[v.box.page - 1]
            got = page.within_bbox((v.box.x0 - 0.01, v.box.top - 0.01, v.box.x1 + 0.01,
                                    v.box.bottom + 0.01)).extract_text()
            assert got == v.value, (v.field, got)


def _words(pages_boxes):
    out = Counter()
    for page, box in pages_boxes:
        for w in page.extract_words():
            cx, cy = (w["x0"] + w["x1"]) / 2, (w["top"] + w["bottom"]) / 2
            if box is None or (box.x0 <= cx <= box.x1 and box.top <= cy <= box.bottom):
                out[w["text"]] += 1
    return out


@pytest.mark.parametrize("fid", FILLS)
def test_wordexport_carries_real_text(fid):
    import pdfplumber
    t, f, (pdf, truth) = _render(fid)
    m = load_map(f.template)
    with pdfplumber.open(BytesIO(pdf)) as out, pdfplumber.open(mf.template_path(t)) as tpl:
        have = _words([(p, None) for p in out.pages])
        for part in m.parts:
            want = _words([(tpl.pages[b.page - 1], b) for b in part.box])
            assert want, part.id
            carried = sum((want & have).values()) / sum(want.values())
            assert carried >= MIN_WORDS, (part.id, round(carried, 4),
                                          list((want - have).items())[:10])


@pytest.mark.parametrize("fid", FILLS)
def test_wordexport_parts_cover_the_map(fid):
    import pdfplumber
    t, f, (pdf, truth) = _render(fid)
    m = load_map(f.template)
    assert [(p.id, p.type, p.parent) for p in truth.parts if p.type != "blank"] == \
        [(p.id, p.type, p.parent) for p in m.parts]
    assert sorted(p.id for p in truth.parts if p.type == "blank") == \
        sorted(f"blank.{b.field}" for b in m.blanks)
    with pdfplumber.open(BytesIO(pdf)) as out:
        n = len(out.pages)
        for p in truth.parts:
            assert p.boxes, p.id
            for b in p.boxes:
                pg = out.pages[b.page - 1]
                assert 1 <= b.page <= n and 0 <= b.x0 < b.x1 <= pg.width and \
                    0 <= b.top < b.bottom <= pg.height, (p.id, b)
        for v in truth.values:  # the blank part is where its value landed
            (bp,) = [p for p in truth.parts if p.id == f"blank.{v.field}"]
            assert bp.boxes == (v.box,)


def test_wordexport_truth_conforms():
    t, f, (pdf, truth) = _render(FILLS[0])
    g = Graph().parse(data=truth.to_turtle(), format="turtle")
    ok, _, report = validate(g + Graph().parse(EX / "synthetic.ttl"),
                             shacl_graph=Graph().parse(EX / "shapes.ttl"),
                             inference="rdfs", advanced=True)
    assert ok, report


def test_converter_recorded_is_running_word():
    _need_word()
    from scripts.synthetic_contracts.word import converter
    g = Graph().parse(EX / "synthetic.ttl")
    recorded = {str(o) for o in g.objects(URIRef("https://w3id.org/iladub/synthetic"),
                                          URIRef(SYN + "converter"))}
    assert recorded == {converter()}, (recorded, converter())
    assert Literal(converter()).value.startswith("Microsoft Word ")


TABLE_FILLS = [fid for fid in FILLS
               if any(p.type == "table" for p in load_map(load_fill(fid).template).parts)]


@pytest.mark.parametrize("fid", TABLE_FILLS)
def test_wordexport_table_truth_covers_the_drawn_table(fid):
    """Every border segment Word drew lies inside its table's truth box (final review I1).

    Until 2026-11-02 the box was the extent of the table's first and last text line, which missed
    the ruling and every empty last cell (gafta-79b-1 clause 8: x 28->382 against rules to 487).
    Each pdfplumber rect must lie, by exact comparison, inside exactly one table box of its page,
    and every table box must hold at least one. pdfium, a second extractor, must count as many path
    objects on the page as pdfplumber counts rects, so no drawn segment escapes the check. (Their
    coordinates are not compared with each other: pdfium reports float32, pdfplumber float64.)"""
    import pdfplumber
    import pypdfium2 as pdfium
    import pypdfium2.raw as pdfium_c

    t, f, (pdf, truth) = _render(fid)
    tables = [(p.id, b) for p in truth.parts if p.type == "table" for b in p.boxes]
    assert tables
    doc = pdfium.PdfDocument(pdf)
    seen = Counter()
    with pdfplumber.open(BytesIO(pdf)) as out:
        for n in sorted({b.page for _, b in tables}):
            page = out.pages[n - 1]
            boxes = [(pid, b) for pid, b in tables if b.page == n]
            paths = list(doc[n - 1].get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_PATH]))
            assert page.rects and len(paths) == len(page.rects), (fid, n, len(paths))
            for r in page.rects:
                inside = [pid for pid, b in boxes if b.x0 <= r["x0"] and r["x1"] <= b.x1
                          and b.top <= r["top"] and r["bottom"] <= b.bottom]
                assert len(inside) == 1, (fid, n, (r["x0"], r["top"], r["x1"], r["bottom"]), boxes)
                seen[inside[0]] += 1
    assert set(seen) == {pid for pid, _ in tables}, (fid, seen)
