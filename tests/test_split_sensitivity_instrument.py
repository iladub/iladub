"""scripts/unshown_ink_split_sensitivity.py — the one function its figures rest on, and the
corpus shape it found, reproduced where CI can see it.

The instrument's corpus modes need `corpus/*.pdf`, which is fetched and never committed
(`.gitignore:52`), so the numbers in `docs/superpowers/2026-09-18-does-the-split-move-evidence.md`
are re-run by hand and cannot be pinned here. Two things CAN be, and both are load-bearing:

  1. **`split_parts` does not drift from `header_body_split`.** The instrument reproduces that
     function's body rather than calling it, because its whole subject is WHICH of the two
     branches answered — the AXIOM (`header-body-split.rq`) or the `_hrule_split` fallback — and
     the function returns one number that does not say. A reproduction is a copy, and a copy
     drifts; this compares them on both branches.

  2. **The corpus finding's MECHANISM, on a fixture that states the geometry in full.** On
     cbh-stem every address that moves the split is a column LABEL in the header row, and
     abstaining one of them alone collapses the split to 1 — the header is read as body. That is
     not cbh-specific arithmetic: a label row is Text over a numeric column, so it is the MAX
     mismatch row that sets `s_col`, and removing it leaves the column homogeneous from row 1.

`tests/etkl/test_unshown_ink.py::test_an_unshown_cell_does_not_vote_in_the_homogeneity_judgement`
already pins that an unshown cell abstains, on a BODY cell holding the word "closed". This pins
the case that makes it consequential rather than merely visible: the abstaining cell is the
header's own label, and the split does not shift by one — it collapses to the floor.
"""
import importlib.util
import pathlib

from dataclasses import replace

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headers import header_body_split

_SPEC = importlib.util.spec_from_file_location(
    "unshown_ink_split_sensitivity",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "unshown_ink_split_sensitivity.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

# Two columns, four rows, in cbh's shape: a title line the grid reads in column 0 only, then the
# column-LABEL row, then two data rows. Column 1 is Quantity from the label row down except for
# the label itself, so the label is the mismatch that puts the split at 2.
_BOUNDS = (50.0, 150.0, 250.0)
_GRID = LeafGrid(_BOUNDS, 2, 100.0, 1.0)
_ROWS = [[("Shipping stem", 55.0, 145.0)],
         [("Region", 55.0, 145.0), ("Volume", 155.0, 245.0)],
         [("North", 55.0, 145.0), ("10", 155.0, 245.0)],
         [("South", 55.0, 145.0), ("20", 155.0, 245.0)]]


def _band(rows=_ROWS, **kw):
    lines = []
    for i, words in enumerate(rows):
        top = 100.0 + 20.0 * i
        ws = tuple(Word(t, x0, x1, top, top + 10.0) for t, x0, x1 in words)
        lines.append(Line(ws, top, top + 10.0))
    return Band(tuple(lines), lines[0].top, lines[-1].bottom, **kw)


LABEL = (1, 1)          # "Volume" — the column label, in the label row


def test_the_fixture_puts_the_split_below_the_label_row():
    """The control. Without it the collapse below could be a split that was already 1."""
    assert header_body_split(_band(), _GRID) == 2


def test_abstaining_the_column_LABEL_alone_collapses_the_split_to_the_floor():
    """cbh's mechanism: one unshown address in the header row erases the header.

    Not "the split moves" — it goes to 1, the minimum the derivation can return, so every header
    line is read as body. On cbh-stem this is measured on four bands: 7 -> 1, 4 -> 1, 5 -> 1,
    4 -> 1 (2026-09-18 evidence § 2).
    """
    moved = header_body_split(replace(_band(), unshown=(LABEL,)), _GRID)
    assert moved == 1, f"the label still voted in the homogeneity judgement (got {moved!r})"


def test_a_BODY_address_of_the_same_column_does_not_move_it():
    """The null. Abstention is not globally destabilising — it matters WHERE the address is, and
    that is the whole reason the corpus splits into cbh (movers in the header) and graincorp
    (110 unshown addresses, all in the body, 0 movers)."""
    for body_addr in [(2, 1), (3, 1)]:
        held = header_body_split(replace(_band(), unshown=(body_addr,)), _GRID)
        assert held == 2, f"{body_addr} moved the split to {held!r}; only the label should"


def test_split_parts_reports_the_AXIOM_branch_and_agrees_with_the_function():
    """Drift guard, the branch where the query answers."""
    band = _band()
    axiom, final = _MOD.split_parts(band, _GRID)
    assert axiom == 2 and final == header_body_split(band, _GRID)
    axiom, final = _MOD.split_parts(band, _GRID, (LABEL,))
    assert axiom == 1 and final == header_body_split(replace(band, unshown=(LABEL,)), _GRID)


def test_split_parts_reports_the_FALLBACK_branch_and_agrees_with_the_function():
    """Drift guard, the branch where the query returns None and `_hrule_split` answers.

    An all-Text band has no non-Text column, so the AXIOM returns None; with no horizontal rule
    to fall back on, the function returns None too. The point of the pin is that `axiom` and
    `final` are reported apart — a single number could not tell these two Nones from a split.
    """
    text_only = [[("Region", 55.0, 145.0), ("Note", 155.0, 245.0)],
                 [("North", 55.0, 145.0), ("open", 155.0, 245.0)],
                 [("South", 55.0, 145.0), ("closed", 155.0, 245.0)]]
    band = _band(text_only)
    axiom, final = _MOD.split_parts(band, _GRID)
    assert axiom is None, "fixture is not discriminating: the AXIOM answered"
    assert final == header_body_split(band, _GRID)
