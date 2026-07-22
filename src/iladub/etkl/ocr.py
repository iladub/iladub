"""ocr — faithful OCR first mile: a scanned (text-layer-less) page -> Words.

§8 gate: every step here is PROCEDURAL raw extraction or exact arithmetic (see the
per-function docstrings for the irreducibility statement). There is NO AXIOM/NEURAL step:
OCR is the image analog of geometry.extract_words. Faithfulness is guaranteed by FORBIDDING
the generative backend class (see OcrBackend), not by a confidence oracle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .geometry import Word


@dataclass(frozen=True)
class OcrRegion:
    """One transcribed text line/segment. Bounds are PIXELS at the render scale,
    x from page-left, top/bottom from page-TOP (matching pdfplumber after /scale)."""
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    confidence: float


@runtime_checkable
class OcrBackend(Protocol):
    """A page transcriber. image -> transcribed line-regions.

    FAITHFULNESS CONTRACT (first-mile, load-bearing): an OcrBackend MUST be a
    DISCRIMINATIVE TRANSCRIBER — detection + CTC/attention recognition over image regions,
    faithful by construction. AUTOREGRESSIVE GENERATIVE-VLM DECODERS ARE FORBIDDEN: they can
    paraphrase, hallucinate, repeat, or silently omit, which poisons everything downstream.
    This is the §8/§3/§7 guarantee expressed as a type contract."""
    def transcribe(self, image) -> list[OcrRegion]: ...


def pixels_to_word(region: OcrRegion, scale: float, page_number: int = 0) -> Word:
    """PROCEDURAL exact arithmetic: pixel bounds at `scale` -> PDF points (point = pixel/scale).
    pypdfium2 renders top-origin, so `top` maps to `top` with NO y-flip. Irreducible: a unit
    conversion, not a decision — gates no classification."""
    return Word(region.text, region.x0 / scale, region.x1 / scale,
                region.top / scale, region.bottom / scale, page_number)


def _bounds(poly) -> tuple[float, float, float, float]:
    """Axis-aligned (x0, x1, top, bottom) of a 4-point OCR polygon. PROCEDURAL exact
    arithmetic (min/max over corners) — no tuned constant."""
    xs = [float(p[0]) for p in poly]
    ys = [float(p[1]) for p in poly]
    return min(xs), max(xs), min(ys), max(ys)


class RapidOcrBackend:
    """Default backend: RapidOCR (PP-OCR on ONNX Runtime) — a DISCRIMINATIVE TRANSCRIBER
    (detection + CTC recognition), faithful by construction. Satisfies OcrBackend. Emits one
    region per detected text line/segment; per-word boxes are NOT available (region-as-Word
    downstream). Lazy-imports rapidocr so the dep stays optional."""

    def __init__(self):
        from rapidocr import RapidOCR  # lazy: optional [ocr] extra
        self._engine = RapidOCR()

    def transcribe(self, image) -> list["OcrRegion"]:
        res = self._engine(image)
        if res is None or getattr(res, "boxes", None) is None:
            return []
        out: list[OcrRegion] = []
        for poly, txt, score in zip(res.boxes, res.txts, res.scores):
            x0, x1, top, bottom = _bounds(poly)
            out.append(OcrRegion(str(txt), x0, x1, top, bottom, float(score)))
        return out


def render_page_to_words(pdf_path: str, page_number: int = 0,
                         backend: "OcrBackend | None" = None, scale: float = 3.0) -> list[Word]:
    """Scanned page -> Words. PROCEDURAL raw extraction: (1) pypdfium2 rasterizes the page at
    `scale` (a rendering-FIDELITY constant — more pixels = better recognition; it gates NO
    classification, so it is not a tuned decision threshold); (2) the backend transcribes it
    (discriminative, faithful); (3) each line-region becomes ONE Word (region-as-Word — no
    invented per-word coordinates, §7). Lazy-imports pypdfium2 so the dep stays optional."""
    import numpy as np
    import pypdfium2 as pdfium

    if backend is None:
        backend = RapidOcrBackend()
    pdf = pdfium.PdfDocument(pdf_path)
    try:
        image = np.array(pdf[page_number].render(scale=scale).to_pil().convert("RGB"))
    finally:
        pdf.close()
    regions = backend.transcribe(image)
    return [pixels_to_word(r, scale, page_number) for r in regions]
