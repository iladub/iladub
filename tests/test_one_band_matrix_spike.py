"""scripts/one_band_matrix_spike.py — the instrument's one pure function, and the two facts
apple p2's refusal stands on.

`main()` needs a PDF and a compile, so it is exercised by running the script on the corpus (the
evidence doc `docs/superpowers/2026-09-04-one-band-matrix-spike.md` pastes its output). What is
pinned here is `merge_bands` — the construction the CONFIRMED result rests on — plus the two
independent reasons p2 refused, each beside the twin that falsifies it:

  * R167, **CLOSED 2026-09-09** (`docs/superpowers/2026-09-09-the-nil-glyph.md`): the em-dash
    USED to type `tab:Text` while the ASCII `-` `is_blank` already accepts typed `tab:Blank`, and
    that one `tab:Text` body cell is what disqualified apple p2's column 1 in `stub-data-split.rq`.
    The nil spellings are now declared as `tab:nilSpelling` on `tab:Blank` and read from the
    ontology, so all three glyphs agree. The pin below is INVERTED from what the spike recorded,
    and its falsifying twin moved with it — see that test's own docstring.
  * R162: `infer_column_tree_by_proximity`'s uncarried-ink guard refuses a three-WORD
    `Nine Months Ended` over two data columns, because `Months` wins no column. The falsifying
    twin is the same header as ONE word — the cell a RULED band re-extracts — which yields a tree.

The tests are deliberately fixture-built, not PDF-driven: both facts are about geometry the
fixture states in full, and a PDF would hide the one word position that decides each.
"""
import importlib.util
import pathlib

from rdflib import Namespace

from iladub.etkl.bands import Band
from iladub.etkl.celltype import _cell_datatype
from iladub.etkl.geometry import Line, Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.matrix import infer_column_tree_by_proximity

TAB = Namespace("https://w3id.org/iladub/tab#")

_SPEC = importlib.util.spec_from_file_location(
    "one_band_matrix_spike",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "one_band_matrix_spike.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def _line(words, top):
    ws = tuple(Word(t, x0, x1, top, top + 10.0) for t, x0, x1 in words)
    return Line(ws, top, top + 10.0)


def _band(lines, **kw):
    return Band(tuple(lines), min(l.top for l in lines), max(l.bottom for l in lines), **kw)


# ---------------------------------------------------------------- merge_bands

def test_merge_bands_concatenates_lines_in_document_order_and_spans_the_run():
    a = _band([_line([("Header", 50.0, 90.0)], 100.0)])
    b = _band([_line([("Body", 50.0, 80.0)], 120.0)])
    c = _band([_line([("More", 50.0, 80.0)], 140.0)])
    merged = _MOD.merge_bands([a, b, c], 0, 2)
    assert [w.text for ln in merged.lines for w in ln.words] == ["Header", "Body", "More"]
    assert merged.top == 100.0
    assert merged.bottom == 150.0


def test_merge_bands_takes_column_xs_from_the_first_band_that_has_any_never_unions_them():
    """`column_xs` is a boundary VECTOR: unioning two would invent boundaries no band derived."""
    a = _band([_line([("a", 50.0, 60.0)], 100.0)])                       # no column_xs
    b = _band([_line([("b", 50.0, 60.0)], 120.0)], column_xs=(50.0, 300.0, 562.0))
    c = _band([_line([("c", 50.0, 60.0)], 140.0)], column_xs=(50.0, 400.0, 562.0))
    assert _MOD.merge_bands([a, b, c], 0, 2).column_xs == (50.0, 300.0, 562.0)


def test_merge_bands_carries_every_rule_and_marker_of_the_run():
    a = _band([_line([("a", 50.0, 60.0)], 100.0)], unit_markers=(("$", 310.0, ()),))
    b = _band([_line([("b", 50.0, 60.0)], 120.0)], unit_markers=(("$", 420.0, ()),))
    merged = _MOD.merge_bands([a, b], 0, 1)
    assert [m[1] for m in merged.unit_markers] == [310.0, 420.0]


# ---------------------------------------------------------------- R167: the em-dash

def test_the_em_dash_types_as_blank_now_that_r167_is_closed():
    """R167, INVERTED 2026-09-09 when the residue closed. This pin read
    `_cell_datatype('—') == tab:Text` at the spike, and that single body cell was the whole
    reason `stub_data_split` returned 2 instead of 1 for apple p2 column 1.

    **The old falsifying twin no longer falsifies.** It was the ASCII `-` — same position, same
    grammar, opposite answer — which separated only while the classifier disagreed about the two
    glyphs. Now that all three agree, that twin would pass against a classifier that returned
    `tab:Blank` for everything. The twin that still separates is a dash INSIDE other text:
    matching is by equality on the stripped cell and never as a substring, so `'2020—2024'` is
    ink, not absence. Deleting the twin rather than moving it would leave this pin vacuous."""
    assert _cell_datatype("-") == TAB.Blank
    assert _cell_datatype("—") == TAB.Blank         # em dash — was tab:Text before R167 closed
    assert _cell_datatype("–") == TAB.Blank         # en dash
    assert _cell_datatype("2020—2024") == TAB.Text  # the twin that still falsifies


# ---------------------------------------------------------------- R162: word-vs-cell granularity

_GRID = LeafGrid((50.0, 417.2, 488.7, 562.4), 3, 100.0, 1.0)   # apple p2's own boundaries
_DATA_COLS = (1, 2)


def test_a_three_word_spanner_over_two_data_columns_refuses_via_the_uncarried_ink_guard():
    """R162 at apple p2 band 2's exact geometry. Data-column centres are 452.95 and 525.55;
    `Nine` (centre 462.5) wins column 1, `Ended` (517.0) wins column 2, and `Months` (488.0 —
    which `column_of` places in DATA column 1) wins nothing, so the guard refuses rather than
    dropping its ink."""
    band = _band([
        _line([("Nine", 454.0, 471.0), ("Months", 473.0, 503.0), ("Ended", 505.0, 529.0)], 100.0),
        _line([("June 27,", 438.0, 471.0), ("June 28,", 511.0, 545.0)], 112.0),
        _line([("2026", 444.0, 465.0), ("2025", 518.0, 538.0)], 124.0),
        _line([("Net income", 53.0, 117.0), ("101,464", 453.0, 486.0), ("84,544", 532.0, 562.0)], 136.0),
    ])
    assert infer_column_tree_by_proximity(band, _GRID, 3, _DATA_COLS) is None


def test_the_same_spanner_as_ONE_word_yields_a_tree_the_falsifying_twin():
    """The cell a RULED band re-extracts — `Nine Months Ended` as one word over both data
    columns. Same geometry, same guard, opposite answer: the refusal above is about the WORD
    split, not about the header being unreadable."""
    band = _band([
        _line([("Nine Months Ended", 454.0, 529.0)], 100.0),
        _line([("June 27,", 438.0, 471.0), ("June 28,", 511.0, 545.0)], 112.0),
        _line([("2026", 444.0, 465.0), ("2025", 518.0, 538.0)], 124.0),
        _line([("Net income", 53.0, 117.0), ("101,464", 453.0, 486.0), ("84,544", 532.0, 562.0)], 136.0),
    ])
    tree = infer_column_tree_by_proximity(band, _GRID, 3, _DATA_COLS)
    assert tree is not None
    assert [(n.level, n.covers, n.text) for n in tree][0] == (0, (1, 2), "Nine Months Ended")
