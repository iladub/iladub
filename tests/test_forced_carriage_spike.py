"""scripts/forced_carriage_spike.py — the R165 spike instrument's one pure function, and the
seam fact the spike rests on.

`main()` needs a PDF and a compile, so it is exercised by running the script on the corpus (the
evidence doc `docs/superpowers/2026-09-03-r165-forced-carriage-spike.md` pastes its output).
`synthetic_reading` is the part that builds the block the seam would have received, and the
fact pinned beside it is the one the refutation stands on: `ruledroles.carried_roles_for`
REFUSES a receiving band whose only header row is a section heading (`Operating expenses:`),
because its rule is "every row of this page has an exact per-column counterpart in the carried
block" — the seam matches a REDRAWN header, it never supplies a missing one. Falsified by
handing the same function a receiving row that IS a redraw of the carried leaf: it matches.
"""
import importlib.util
import pathlib
from dataclasses import dataclass

from iladub.etkl.ruledroles import carried_roles_for

_SPEC = importlib.util.spec_from_file_location(
    "forced_carriage_spike",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "forced_carriage_spike.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


@dataclass(frozen=True)
class _W:
    x0: float
    x1: float
    text: str


@dataclass(frozen=True)
class _Line:
    words: tuple


@dataclass(frozen=True)
class _Grid:
    boundaries: tuple


# apple p0 band 3's measured leaf grid, and band 2's header lines placed over it (the spike's
# own printed signatures: `(2, 'Three Months Ended') (4, 'Nine Months Ended')`, then the dates,
# then the years as the leaf).
_GRID = _Grid((50.0, 300.0, 364.4, 430.4, 496.4, 562.4))
_HEADER_LINES = [
    _Line((_W(380, 420, "Three Months Ended"), _W(510, 550, "Nine Months Ended"))),
    _Line((_W(320, 350, "June 27,"), _W(380, 420, "June 28,"),
           _W(450, 480, "June 27,"), _W(510, 550, "June 28,"))),
    _Line((_W(320, 350, "2026"), _W(380, 420, "2025"), _W(450, 480, "2026"), _W(510, 550, "2025"))),
]


def test_synthetic_reading_keys_every_word_by_leaf_column_and_makes_the_last_line_the_leaf():
    reading = _MOD.synthetic_reading(_HEADER_LINES, _GRID.boundaries, "urn:x#t", 0)
    assert [r.signature for r in reading.rows] == [
        ((2, "Three Months Ended"), (4, "Nine Months Ended")),
        ((1, "June 27,"), (2, "June 28,"), (3, "June 27,"), (4, "June 28,")),
        ((1, "2026"), (2, "2025"), (3, "2026"), (4, "2025")),
    ]
    assert [r.role for r in reading.rows] == ["continuation", "continuation", None]
    assert all(r.origin_page == 0 for r in reading.rows)


def test_the_seam_refuses_a_band_whose_only_header_row_is_a_section_heading():
    reading = _MOD.synthetic_reading(_HEADER_LINES, _GRID.boundaries, "urn:x#t", 0)
    section_heading = [[_W(52, 140, "Operating expenses:")]]
    assert carried_roles_for(reading, section_heading, _GRID) is None


def test_the_same_seam_matches_a_band_that_redraws_the_carried_leaf():
    # The falsifying twin of the test above: the ONLY difference is that the receiving band's
    # header rows now repeat the carried block per column, which is what page-to-page carriage
    # was built for. If this passes and the one above fails, the refusal is about the section
    # heading, not about the reading. (Redrawing the LEAF alone is also refused — skipping a
    # `continuation` row is not inert, ruledroles' F1 — so the whole block is redrawn here.)
    reading = _MOD.synthetic_reading(_HEADER_LINES, _GRID.boundaries, "urn:x#t", 0)
    redrawn_block = [list(ln.words) for ln in _HEADER_LINES]
    match = carried_roles_for(reading, redrawn_block, _GRID)
    assert match is not None
    roles, matched = match
    assert roles == ("continuation", "continuation") and matched[-1][1] is reading.rows[-1]
