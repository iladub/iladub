import os, tempfile, builtins
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl import geometry
from iladub.etkl.geometry import extract_words, Word
from tests.etkl import fixtures as F


def _pdf(fn, name):
    p = os.path.join(tempfile.mkdtemp(), name + ".pdf"); fn(p); return p


def test_born_digital_never_invokes_ocr(monkeypatch):
    # a real text layer -> OCR must NOT run
    def _boom(*a, **k):
        raise AssertionError("OCR must not run when a text layer is present")
    monkeypatch.setattr("iladub.etkl.ocr.render_page_to_words", _boom, raising=False)
    words = extract_words(_pdf(F.simple_table_pdf, "digital"))
    assert words and all(isinstance(w, Word) for w in words)


def test_image_only_falls_back_to_ocr(monkeypatch):
    # no text layer -> OCR fallback is called; stub it to avoid the heavy engine
    stub = [Word("Alpha", 10, 40, 10, 20, 0)]
    monkeypatch.setattr("iladub.etkl.ocr.render_page_to_words",
                        lambda *a, **k: stub, raising=False)
    words = extract_words(_pdf(F.image_only_table_pdf, "scan"))
    assert words == stub


def test_graceful_escalation_when_ocr_extra_absent(monkeypatch):
    # Simulate the [ocr] extra not installed -> extract_words returns [] (no crash).
    # The `iladub.etkl.ocr` module always ships with the package; the extra is the ENGINE
    # (pypdfium2 / rapidocr), lazy-imported inside the OCR call. So absence == those top-level
    # packages being unimportable at call time.
    p = _pdf(F.image_only_table_pdf, "scan2")  # build the scan BEFORE blocking the engine
    real_import = builtins.__import__
    def _no_ocr(name, *a, **k):
        if name.split(".")[0] in {"pypdfium2", "rapidocr"}:
            raise ImportError("simulated: ocr extra absent")
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", _no_ocr)
    assert extract_words(p) == []
