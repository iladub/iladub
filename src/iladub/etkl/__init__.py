"""iladub ET(K)L compiler — deterministic multimodal extraction (increment 1a)."""

from .geometry import Word, Line, extract_words, text_lines
from .bands import Band, detect_bands
from .grid import LeafGrid, infer_leaf_grid

__all__ = [
    "Word", "Line", "extract_words", "text_lines",
    "Band", "detect_bands",
    "LeafGrid", "infer_leaf_grid",
]
