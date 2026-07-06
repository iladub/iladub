"""iladub ET(K)L compiler — deterministic multimodal extraction.

increment 1a: geometry -> bands -> body leaf-grid.
closing slice: classify -> round-trip -> validated table-holon + score.
"""

from .geometry import Word, Line, extract_words, text_lines
from .bands import Band, detect_bands
from .grid import LeafGrid, infer_leaf_grid
from .regions import RegionKind, Cell, ClassifiedRegion, classify, assign_cells, column_of
from .roundtrip import cell_round_trips, render_ascii
from .compile import compile_tables, CompilationReport, RegionReport

__all__ = [
    "Word", "Line", "extract_words", "text_lines",
    "Band", "detect_bands",
    "LeafGrid", "infer_leaf_grid",
    "RegionKind", "Cell", "ClassifiedRegion", "classify", "assign_cells", "column_of",
    "cell_round_trips", "render_ascii",
    "compile_tables", "CompilationReport", "RegionReport",
]
