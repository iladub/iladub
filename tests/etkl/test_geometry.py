from iladub.etkl.geometry import extract_words, text_lines, Word
from tests.etkl.fixtures import simple_table_pdf, PAGE_H


def test_extract_words_returns_points(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    words = extract_words(str(pdf))
    hgb = [w for w in words if w.text == "Hemoglobin"]
    assert len(hgb) == 1
    # x0 is in points, near the first column's left edge (72)
    assert abs(hgb[0].x0 - truth["cols"][0]) < 3.0
    # pdfplumber `top` is measured from the page top
    assert 0 < hgb[0].top < PAGE_H


def test_text_lines_groups_rows(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    simple_table_pdf(str(pdf))
    lines = text_lines(extract_words(str(pdf)))
    # 1 title line + 4 table rows = 5 lines
    assert len(lines) == 5
    # each table row line has 3 words; sorted left-to-right
    body = [ln for ln in lines if any(w.text == "Hemoglobin" for w in ln.words)][0]
    assert [w.text for w in body.words] == ["Hemoglobin", "13.2", "g/dL"]
