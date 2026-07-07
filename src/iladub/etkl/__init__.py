"""iladub ET(K)L compiler — deterministic multimodal extraction.

increment 1a: geometry -> bands -> body leaf-grid.
closing slice: classify -> round-trip -> validated table-holon + score.
loop 2: hierarchical header tree + multi-level holon emission.
"""

from .geometry import Word, Line, extract_words, text_lines
from .bands import Band, detect_bands
from .grid import LeafGrid, infer_leaf_grid
from .regions import RegionKind, Cell, ClassifiedRegion, classify, assign_cells, column_of
from .roundtrip import cell_round_trips, render_ascii
from .compile import compile_tables, CompilationReport, RegionReport
from .hierarchical import classify_hierarchical, HierRegion
from .cells import recover_leaf_grid
from .orientation import looks_transposed, transpose_is_coherent
from .holon import assert_record_region, assert_transposed_region

__all__ = [
    "Word", "Line", "extract_words", "text_lines",
    "Band", "detect_bands",
    "LeafGrid", "infer_leaf_grid",
    "RegionKind", "Cell", "ClassifiedRegion", "classify", "assign_cells", "column_of",
    "cell_round_trips", "render_ascii",
    "compile_tables", "CompilationReport", "RegionReport",
    "classify_hierarchical", "HierRegion",
    "recover_leaf_grid",
    "looks_transposed", "transpose_is_coherent", "assert_transposed_region",
    "assert_record_region",
]
