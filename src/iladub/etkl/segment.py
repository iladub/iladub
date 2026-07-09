"""segment — split a fused multi-table band into single-table sub-bands.

detect_bands is 1-D (vertical gaps only), so it fuses side-by-side and
stacked-no-gap tables into one region. segment PROPOSES cuts (widest full-height
gutter; repeated-header row) and CERTIFIES each by re-running classify on both
sides. A certified cut is taken; a genuine-but-uncertain second table escalates
MULTI_TABLE_AMBIGUOUS (via the stub asymmetry). No single table is ever split.
"""
from __future__ import annotations

from .bands import Band
from .geometry import text_lines
from .grid import infer_leaf_grid
from .headers import header_body_split, is_numeric
from .regions import classify, RegionKind, column_of


def _band_from_lines(lines) -> Band:
    lines = tuple(lines)
    return Band(lines, min(l.top for l in lines), max(l.bottom for l in lines))


def _band_from_words(words) -> Band:
    return _band_from_lines(text_lines(list(words)))


def _row_tokens(line) -> tuple[str, ...]:
    return tuple(w.text for w in sorted(line.words, key=lambda w: w.x0))


def find_repeated_header(band: Band) -> list[int]:
    """Body-row indices whose token tuple equals the header row (row 0). A single
    table never repeats its exact header as a data row, so this is false-positive
    free."""
    rows = [_row_tokens(ln) for ln in band.lines]
    if len(rows) < 2:
        return []
    hdr = rows[0]
    return [i for i in range(1, len(rows)) if rows[i] == hdr]


def _col_ink_extents(band: Band, grid):
    b = grid.boundaries
    cw: dict[int, list] = {}
    for ln in band.lines:
        for w in ln.words:
            cw.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
    return {c: (min(w.x0 for w in ws), max(w.x1 for w in ws)) for c, ws in cw.items()}


def _widest_gutter_cut(band: Band):
    """(cut_x, left_words, right_words) at the widest inter-column ink gap, or None."""
    if len(band.lines) < 2:
        return None
    grid = infer_leaf_grid(band)
    if grid.ncols < 2:
        return None
    ext = _col_ink_extents(band, grid)
    gaps = [(c, ext[c + 1][0] - ext[c][1]) for c in range(grid.ncols - 1)
            if c in ext and c + 1 in ext]
    if not gaps:
        return None
    wc, _ = max(gaps, key=lambda z: z[1])
    cut = (ext[wc][1] + ext[wc + 1][0]) / 2.0
    words = [w for ln in band.lines for w in ln.words]
    left = [w for w in words if (w.x0 + w.x1) / 2.0 < cut]
    right = [w for w in words if (w.x0 + w.x1) / 2.0 >= cut]
    if not left or not right:
        return None
    return cut, left, right


def find_table_gutter(band: Band) -> float | None:
    """The x of a CERTIFIED side-by-side cut: the widest full-height gutter where
    BOTH sides independently classify RECORD_TABLE. Else None. The both-RECORD rule
    excludes the cross-tab (its halves are UNSUPPORTED) and every single table."""
    got = _widest_gutter_cut(band)
    if got is None:
        return None
    cut, left, right = got
    lk = classify(_band_from_words(left)).kind
    rk = classify(_band_from_words(right)).kind
    if lk is RegionKind.RECORD_TABLE and rk is RegionKind.RECORD_TABLE:
        return cut
    return None


def has_own_stub(band: Band) -> bool:
    """True iff the band's leftmost occupied column has majority-text body cells —
    its own row identity. Distinguishes a self-contained table from a cross-tab's
    data-only right fragment (threshold-free)."""
    if len(band.lines) < 2:
        return False
    grid = infer_leaf_grid(band)
    b = grid.boundaries
    split = header_body_split(band, grid) or 1
    colcells: dict[int, dict[int, list]] = {}
    for r, ln in enumerate(band.lines):
        for w in ln.words:
            colcells.setdefault(column_of((w.x0 + w.x1) / 2.0, b), {}).setdefault(r, []).append(w.text)
    if not colcells:
        return False
    leftcol = min(colcells)
    body = [" ".join(v) for r, v in colcells[leftcol].items() if r >= split]
    if not body:
        return False
    return sum(1 for t in body if not is_numeric(t)) / len(body) > 0.5


def segment(band: Band) -> list[Band]:
    """Recursively split a band into single-table sub-bands. Vertical (repeated
    header) first, then horizontal (certified gutter); returns [band] when no
    certified cut exists. Never splits a single table (certification guarantees it)."""
    reps = find_repeated_header(band)
    if reps:
        cuts = [0] + reps + [len(band.lines)]
        out: list[Band] = []
        for a, z in zip(cuts, cuts[1:]):
            grp = band.lines[a:z]
            if grp:
                out.extend(segment(_band_from_lines(grp)))
        return out
    cut = find_table_gutter(band)
    if cut is not None:
        words = [w for ln in band.lines for w in ln.words]
        left = [w for w in words if (w.x0 + w.x1) / 2.0 < cut]
        right = [w for w in words if (w.x0 + w.x1) / 2.0 >= cut]
        return segment(_band_from_words(left)) + segment(_band_from_words(right))
    return [band]


def is_multi_table_ambiguous(band: Band) -> bool:
    """True iff there is a genuine second table that segment could not cleanly split:
    a widest full-height gutter where the left is a valid table and the right has its
    OWN stub, yet the pair is not both-RECORD (so find_table_gutter declined). The
    cross-tab is excluded because its right half is data-only (has_own_stub False)."""
    if find_repeated_header(band) or find_table_gutter(band) is not None:
        return False                    # cleanly splittable — not ambiguous
    got = _widest_gutter_cut(band)
    if got is None:
        return False
    _, left, right = got
    lk = classify(_band_from_words(left)).kind
    return lk is not RegionKind.NON_TABLE and has_own_stub(_band_from_words(right))
