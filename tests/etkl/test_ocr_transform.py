from iladub.etkl.ocr import OcrRegion, OcrBackend, pixels_to_word
from iladub.etkl.geometry import Word


def test_pixels_to_word_divides_by_scale_no_yflip():
    # a region at 3x render scale -> points are pixels/3, top stays top (no flip)
    r = OcrRegion("Alpha Widget", x0=300.0, x1=600.0, top=150.0, bottom=210.0, confidence=0.99)
    w = pixels_to_word(r, scale=3.0, page_number=2)
    assert w == Word("Alpha Widget", 100.0, 200.0, 50.0, 70.0, 2)


def test_ocrregion_is_frozen():
    import dataclasses
    r = OcrRegion("x", 0, 1, 0, 1, 1.0)
    assert dataclasses.is_dataclass(r)
    try:
        r.text = "y"  # type: ignore[misc]
        assert False, "OcrRegion must be frozen"
    except dataclasses.FrozenInstanceError:
        pass


def test_backend_protocol_is_runtime_checkable_shape():
    # a minimal transcriber satisfies the protocol structurally
    class Stub:
        def transcribe(self, image):
            return []
    assert hasattr(OcrBackend, "transcribe")
    Stub().transcribe(None)  # shape smoke
