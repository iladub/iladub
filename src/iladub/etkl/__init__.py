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
from .rowheaders import looks_row_grouped, classify_row_hier, RowHierRegion, RowHeaderNode
from .holon import assert_record_region, assert_transposed_region, assert_row_hier_region, assert_matrix_region
from .matrix import (is_matrix_candidate, classify_matrix,
                     infer_column_tree_by_proximity, MatrixRegion, ColHeaderNode)
from .segment import segment, find_table_gutter, find_repeated_header, has_own_stub, is_multi_table_ambiguous
from .denormalization import (recover_dimensions, annotate_dimensions, PivotedDimension,
                              detect_aggregations, annotate_aggregations, verify_group,
                              AggregationEvidence, emit_base_facts, analyze, DenormalizationReport)

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
    "looks_row_grouped", "classify_row_hier", "RowHierRegion", "RowHeaderNode",
    "assert_row_hier_region",
    "is_matrix_candidate", "classify_matrix",
    "infer_column_tree_by_proximity", "MatrixRegion", "ColHeaderNode",
    "assert_matrix_region",
    "segment", "find_table_gutter", "find_repeated_header", "has_own_stub", "is_multi_table_ambiguous",
    "recover_dimensions", "annotate_dimensions", "PivotedDimension",
    "detect_aggregations", "annotate_aggregations", "verify_group", "AggregationEvidence",
    "emit_base_facts", "analyze", "DenormalizationReport",
]
