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
