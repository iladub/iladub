import pdfplumber
from tests.etkl.fixtures import simple_table_pdf


def test_fixture_pdf_is_readable(tmp_path):
    pdf = tmp_path / "cbc.pdf"
    truth = simple_table_pdf(str(pdf))
    with pdfplumber.open(str(pdf)) as doc:
        text = doc.pages[0].extract_text() or ""
    assert truth["title"] in text
    assert "Hemoglobin" in text
