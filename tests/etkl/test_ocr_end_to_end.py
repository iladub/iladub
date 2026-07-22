import os, tempfile
import pytest
pytest.importorskip("rapidocr"); pytest.importorskip("pypdfium2")
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl import compile_tables
from tests.etkl import fixtures as F


def test_scanned_table_pdf_compiles_to_asserted_region():
    p = os.path.join(tempfile.mkdtemp(), "scan_e2e.pdf")
    F.image_only_table_pdf(p)
    rep = compile_tables(p)                       # no text layer -> real OCR runs
    verdicts = [r.verdict for r in rep.regions]
    assert "asserted" in verdicts, [(str(r.kind).split(".")[-1], r.verdict, r.reason)
                                    for r in rep.regions]
    assert rep.score > 0.0, "a scanned table should compile via OCR (was nothing pre-slice)"
