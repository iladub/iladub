import os, tempfile
import pytest
pytest.importorskip("pypdfium2")
from iladub.etkl.ocr import render_page_to_words, OcrRegion
from iladub.etkl.geometry import Word, extract_words


class _StubBackend:
    """Deterministic transcriber: three gap-separated regions (pixel coords at scale=3)."""
    def transcribe(self, image):
        return [OcrRegion("Alpha", 30, 120, 30, 60, 1.0),
                OcrRegion("Widget", 300, 450, 30, 60, 1.0),
                OcrRegion("42", 600, 660, 30, 60, 1.0)]


def _any_pdf():
    from tests.etkl import fixtures as F
    p = os.path.join(tempfile.mkdtemp(), "s.pdf"); F.simple_table_pdf(p); return p


def test_render_maps_regions_to_words_in_points_region_as_word():
    words = render_page_to_words(_any_pdf(), backend=_StubBackend(), scale=3.0)
    assert words == [Word("Alpha", 10, 40, 10, 20, 0),
                     Word("Widget", 100, 150, 10, 20, 0),
                     Word("42", 200, 220, 10, 20, 0)]


def test_image_only_pdf_has_no_text_layer():
    from tests.etkl import fixtures as F
    p = os.path.join(tempfile.mkdtemp(), "img.pdf"); F.image_only_table_pdf(p)
    assert extract_words.__module__  # sanity
    # pdfplumber sees no words on a pure-image page:
    import pdfplumber
    with pdfplumber.open(p) as pdf:
        assert pdf.pages[0].extract_words() == []
