"""Line extraction from PDF bytes (document-router plan, Task 3). PROCEDURAL raw extraction."""
import hashlib
import io

import pytest

pdfium = pytest.importorskip("pypdfium2")
canvas = pytest.importorskip("reportlab.pdfgen.canvas")

from iladub.route.lines import Line, extract_lines, lines_graph  # noqa: E402


def _pdf(pages):
    buf = io.BytesIO()
    c = canvas.Canvas(buf)                      # A4: 595.27 x 841.89
    for strings in pages:
        for y, text in strings:
            c.drawString(72, y, text)
        c.showPage()
    c.save()
    return buf.getvalue()


def test_three_lines_in_order():
    lines = extract_lines(_pdf([[(800, "First line"), (700, "Second line"), (600, "Third line")]]))
    assert [ln.text for ln in lines] == ["First line", "Second line", "Third line"]
    assert [(ln.page, ln.index) for ln in lines] == [(1, 0), (1, 1), (1, 2)]
    tops = [ln.top for ln in lines]
    assert tops == sorted(tops) and len(set(tops)) == 3
    assert all(ln.top < ln.bottom and ln.x0 < ln.x1 for ln in lines)


def test_blank_page_has_no_lines():
    lines = extract_lines(_pdf([[], [(700, "Page two")]]))
    assert [(ln.page, ln.index, ln.text) for ln in lines] == [(2, 0, "Page two")]


def test_mid_page_line_positions():
    (ln,) = extract_lines(_pdf([[(400, "Middle")]]))
    assert 300 < ln.top < 442
    assert ln.top < ln.bottom


def test_sha_is_sha256_of_text():
    ln = Line(1, 0, "Sellers: A", 0.0, 8.0, 0.0, 50.0)
    assert ln.sha == hashlib.sha256("Sellers: A".encode("utf-8")).hexdigest()


def test_pdfium_line_breaks_are_counted_chars_with_zero_area_boxes():
    """MEASURED 2026-11-03 (pypdfium2 5.11.0): pdfium generates `\\r\\n` between lines; both are
    counted by count_chars() and carry a zero-area box. Pins the fact extract_lines splits on."""
    tp = pdfium.PdfDocument(_pdf([[(800, "AB"), (700, "CD")]]))[0].get_textpage()
    chars = [tp.get_text_range(i, 1) for i in range(tp.count_chars())]
    assert chars == ["A", "B", "\r", "\n", "C", "D"]
    for i in (2, 3):
        left, bottom, right, top = tp.get_charbox(i)
        assert left == right and bottom == top


def test_two_one_char_lines_get_no_pdfium_break():
    """MEASURED 2026-11-03 (pypdfium2 5.11.0), a known limit of splitting on pdfium's own text:
    when two consecutive lines are each ONE char, pdfium generates no break between them, so they
    read as one line. ("Hello"/"1" and "1"/"Hello" do get a break.) Pinned so a pdfium change that
    alters it is seen, not absorbed."""
    tp = pdfium.PdfDocument(_pdf([[(800, "A"), (700, "B")]]))[0].get_textpage()
    assert tp.get_text_range() == "AB"
    assert [ln.text for ln in extract_lines(_pdf([[(800, "A"), (700, "B")]]))] == ["AB"]


def test_lines_graph_uses_route_terms_and_stores_no_text():
    from rdflib import Literal, Namespace, RDF, URIRef
    route = Namespace("https://w3id.org/iladub/route#")
    lines = extract_lines(_pdf([[(800, "Secret text")]]))
    sha = "0123456789abcdef" * 4
    g = lines_graph(lines, sha)
    node = URIRef("urn:iladub:route:0123456789ab:p1:l0")
    assert (node, RDF.type, route.Line) in g
    assert g.value(node, route.onPage).toPython() == 1
    assert g.value(node, route.lineIndex).toPython() == 0
    assert g.value(node, route.textSha) == Literal(lines[0].sha)
    assert "Secret text" not in g.serialize(format="turtle")
