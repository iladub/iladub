"""trailing — the notes set below a table's last row are not rows of it.

MEASURED 2026-09-19 on bfs p6: the `Tessin` row, the `Source:` line and two footnotes arrive as
ONE band, because the author sets the notes at the row pitch and `detect_bands` has no gap to
cut on. The two footnotes run the band's full width, so they close every gutter the row's own
numbers keep open and its first four columns fuse into a single word; the band escalates
KIND_NOT_SUPPORTED and the row is never read.

CLAUDE.md §8 CLASSIFICATION: `trailing_refused` is PROCEDURAL glue over a shipped derivation,
the same shape as `donation.head_line_refusals`. It takes no reading judgement and carries no
constant: `datagrid.derive_data_grid` has ALREADY ruled on every text line of the page —
admitted as a body row, or refused with a reason — and this walks the band's lines from the
bottom reading those verdicts. WHICH lines are notes is the datagrid's answer, never this
module's.

EVIDENCE-POSITIVE, and that is the guard. The cut exists only where a run of UNPLACEABLE lines ends
the band AND the line directly above the run is one the datagrid ADMITTED: a table row,
positively identified, with refused ink below it. A band the datagrid admits nothing in is never
cut, so a paragraph, a boxhead or a band of a table the datagrid cannot read stays whole.

Corpus census, 2026-09-19 (every band of >= 2 lines on every page): the walk fires on 5 bands —
bfs p5 b5 and b13 and p6 b10 (`Source(s):` + footnotes), ons p4 b0 (`Source:`), ons p7 b6 (a
stray `"`) — and every line it cuts is a note. No data row is cut anywhere.

ONLY ONE REFUSAL COUNTS, and the suite is what said so. The datagrid refuses a line for several
reasons and they are not alike: `unplaceable` says the line's ink places into NO column of the
grid — it is not shaped like a row — while `RowAddressability/no-key` says it IS shaped like a
row and lacks a key, which is exactly what a row-grouped table's continuation rows and a
page-local subtotal are (`fixtures.row_grouped_table_pdf`'s `Cost 70`,
`case3_with_subtotals_pdf`'s `SUB 250`). The first draft counted every refusal; the corpus census
could not see the difference (all 5 firings, all 12 lines cut, are `unplaceable`) and two
synthetic fixtures lost a data row. `gridregion.peel_leading_captions` records the same lesson
for the other end of the band.

Lines are re-identified BY INK, never by index ([[R202]]); a line whose key matches no page line
or more than one ends the walk, exactly as `head_line_refusals` abstains.
"""
from __future__ import annotations

from typing import Sequence

from .bands import Band

# `datagrid.derive_data_grid`'s own string for a line whose ink places into none of its columns.
UNPLACEABLE = "unplaceable"


def trailing_refused(band: Band, page_keys: Sequence[str], grid) -> int:
    """How many lines at the END of `band` the page datagrid found UNPLACEABLE, directly below a line it
    admitted — or 0. `page_keys[j]` is the ink key of the page's text line `j`, the list
    `grid.rows` and `grid.refusals` index into."""
    from .donation import _ink_key

    def verdict(line) -> str | None:
        hits = [j for j, k in enumerate(page_keys) if k == _ink_key(line)]
        if len(hits) != 1:
            return None
        if hits[0] in grid.rows:
            return "admitted"
        return "unplaceable" if grid.refusals.get(hits[0]) == UNPLACEABLE else None

    n = len(band.lines)
    t = 0
    while t < n and verdict(band.lines[n - 1 - t]) == "unplaceable":
        t += 1
    if t == 0 or t == n or verdict(band.lines[n - 1 - t]) != "admitted":
        return 0
    return t


def trailing_refused_in_grids(band: Band, page_keys: Sequence[str], grids) -> int:
    """`trailing_refused` under the page's grids (R291): the cut the grid whose row the notes
    trail supports, or 0.

    A page can hold more than one grid (R290), and the seed winner need not be the table a
    band's notes trail. bfs p5 under R265 is the measured case: the canton grid outbids the year
    grid, admits none of the year rows, and the year band's `Sources:` lines were never cut. The
    ruled rebuild then read rows and notes as one band, and `2020` fused into `8 606 033`.

    At most one grid fires. The line above the cut must be a row of the firing grid, and
    `derive_data_grids` strikes a line another grid admitted from every other grid's refusals,
    which ends that grid's walk at the same line. With one grid this is `trailing_refused`."""
    return max((trailing_refused(band, page_keys, g) for g in grids), default=0)


def cut_trailing_notes(subs: Sequence[Band], pdf_path: str, page_number: int) -> list[Band]:
    """`subs` with every band `trailing_refused` fires on replaced by two: its rows, then its
    notes. The notes keep a band of their own, so their ink is classified and booked exactly as
    any other band's is — nothing is dropped.

    LAZY: the datagrid is derived only when some band has a second line to cut."""
    from .datagrid import derive_data_grids
    from .donation import _ink_key
    from .geometry import extract_words, text_lines
    from .segment import _band_from_lines

    if not any(len(b.lines) >= 2 for b in subs):
        return list(subs)
    grids = derive_data_grids(pdf_path, page_number)
    if not grids:
        return list(subs)
    # EXACTLY `derive_data_grid`'s own line list: every grid's verdicts are keyed by position in it.
    keys = [_ink_key(l) for l in sorted(text_lines(extract_words(pdf_path, page_number)),
                                        key=lambda l: l.top) if l.words]
    out: list[Band] = []
    for b in subs:
        t = trailing_refused_in_grids(b, keys, grids)
        if t == 0:
            out.append(b)
            continue
        out.append(_band_from_lines(b.lines[:-t]))
        out.append(_band_from_lines(b.lines[-t:]))
    return out
