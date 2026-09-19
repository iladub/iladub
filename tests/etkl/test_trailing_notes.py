"""The notes below a table's last row get a band of their own (2026-09-19).

bfs p6's `Tessin` row, its `Source:` line and two footnotes are set at one pitch, so they arrive
as one band; the footnotes' full-width ink closes the row's gutters and the row was never read.
`trailing.cut_trailing_notes` reads the page datagrid's verdicts from the bottom of the band and
cuts where refused lines sit directly below an admitted one.

The walk is tested OFFLINE first — CI has no corpus — and on the page second.
"""
import os
from types import SimpleNamespace

import pytest

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.trailing import trailing_refused

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BFS = os.path.join(ROOT, "corpus", "gov-stats", "bfs-population-bilan-2023.pdf")
needs_corpus = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")


def _band(*texts):
    lines = tuple(Line((Word(t, 10.0, 50.0, 10.0 * i, 10.0 * i + 8),), 10.0 * i, 10.0 * i + 8)
                  for i, t in enumerate(texts))
    return Band(lines, lines[0].top, lines[-1].bottom)


def _grid(rows=(), refused=(), reason="unplaceable"):
    return SimpleNamespace(rows=tuple(rows), refusals={j: reason for j in refused})


KEYS = ["row1", "row2", "Source:X", "1note"]


def test_refused_lines_below_an_admitted_row_are_counted():
    assert trailing_refused(_band("row1", "row2", "Source: X", "1 note"), KEYS,
                            _grid(rows=(0, 1), refused=(2, 3))) == 2


def test_a_band_the_datagrid_admits_nothing_in_is_never_cut():
    """The evidence-positive guard: refused ink below a line with NO verdict is not a table's
    notes — it is a paragraph, or a table the datagrid cannot read."""
    assert trailing_refused(_band("row1", "row2", "Source: X", "1 note"), KEYS,
                            _grid(rows=(), refused=(2, 3))) == 0


def test_a_trailing_row_refused_for_want_of_a_KEY_is_a_row_and_is_never_cut():
    """A row-grouped table's continuation row and a page-local subtotal are refused
    `RowAddressability/no-key`: shaped like a row, lacking a key. The first draft cut them and
    `test_closing_slice::test_row_grouped_compiles` lost its fifth leaf row."""
    assert trailing_refused(_band("row1", "row2", "Source: X", "1 note"), KEYS,
                            _grid(rows=(0, 1), refused=(2, 3),
                                  reason="RowAddressability/no-key")) == 0


def test_a_band_refused_top_to_bottom_is_never_cut():
    assert trailing_refused(_band("Source: X", "1 note"), KEYS, _grid(refused=(2, 3))) == 0


def test_an_admitted_last_line_means_no_cut():
    assert trailing_refused(_band("row1", "row2"), KEYS, _grid(rows=(0, 1))) == 0


def test_a_line_whose_ink_matches_two_page_lines_ends_the_walk():
    keys = KEYS + ["1note"]
    assert trailing_refused(_band("row1", "row2", "Source: X", "1 note"), keys,
                            _grid(rows=(0, 1), refused=(2, 3, 4))) == 0


@needs_corpus
def test_tessin_is_read_and_its_notes_are_not():
    from iladub.etkl.compile import compile_tables
    regions = compile_tables(BFS, page_number=6, validate_shapes=True).regions
    first = lambda r: ((r.ascii or "").strip().splitlines() or [""])[0].split()[:1]
    tessin = [r for r in regions if first(r) == ["Tessin"]]
    assert len(tessin) == 1
    assert tessin[0].verdict == "asserted" and tessin[0].cells == 9
    notes = regions[regions.index(tessin[0]) + 1]
    assert notes.verdict != "asserted" and notes.cells == 0


@needs_corpus
def test_FALSIFICATION_without_the_cut_tessin_is_not_read(monkeypatch):
    from iladub.etkl import trailing
    from iladub.etkl.compile import compile_tables
    monkeypatch.setattr(trailing, "cut_trailing_notes", lambda subs, pdf, pg: list(subs))
    regions = compile_tables(BFS, page_number=6, validate_shapes=True).regions
    assert not any(r.verdict == "asserted" and (r.ascii or "").lstrip().startswith("Tessin")
                   for r in regions)
