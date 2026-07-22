import numpy as np
import pytest
pytest.importorskip("rapidocr")
from iladub.etkl.ocr import RapidOcrBackend, OcrRegion, _bounds


def test_bounds_of_polygon_is_axis_aligned():
    poly = [[300.0, 150.0], [600.0, 150.0], [600.0, 210.0], [300.0, 210.0]]
    assert _bounds(poly) == (300.0, 600.0, 150.0, 210.0)  # x0, x1, top, bottom


def test_rapidocr_transcribes_rendered_text_faithfully():
    # a white image with black text drawn via PIL -> RapidOCR reads it back
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (600, 120), "white")
    d = ImageDraw.Draw(img)
    d.text((20, 40), "Alpha Widget 42", fill="black")
    regions = RapidOcrBackend().transcribe(np.array(img))
    assert regions, "RapidOCR should find at least one region"
    joined = " ".join(r.text for r in regions)
    assert "Alpha" in joined and "Widget" in joined     # faithful transcription
    for r in regions:
        assert isinstance(r, OcrRegion)
        assert r.x1 > r.x0 and r.bottom > r.top and 0.0 <= r.confidence <= 1.0
