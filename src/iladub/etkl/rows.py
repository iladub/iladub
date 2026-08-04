"""rows — logical row bands via a row-clock anchor column.

Wrap breaks top-alignment, so we cannot group physical lines into rows by their
tops. Instead an anchor column that is single-line per row supplies the rhythm;
every cell is assigned to the band whose vertical extent contains its midpoint.
"""
from __future__ import annotations

from dataclasses import dataclass

from .bands import Band
from .cells import SourceCell, group_wrapped
from .grid import LeafGrid
from .regions import column_of


@dataclass(frozen=True)
class RowBand:
    top: float
    bottom: float
    cells: tuple[SourceCell, ...]


def logical_rows(band: Band, grid: LeafGrid, body_start_top: float):
    b = grid.boundaries
    grouped = group_wrapped(band, grid)   # tuple of tuple[SourceCell]
    # keep only body rows (cells starting at/after body_start_top)
    body = [row for row in grouped if min((c.top for c in row), default=1e9) >= body_start_top - 0.5]
    if not body:
        return None
    # tag each cell with its column
    tagged = []
    for row in body:
        rc = []
        for c in row:
            col = column_of((c.x0 + c.x1) / 2.0, b)
            rc.append((col, c))
        tagged.append(rc)
    ncols = grid.ncols
    anchor = None
    for col in range(ncols):
        if all(sum(1 for (cc, _) in row if cc == col) == 1 for row in tagged):
            anchor = col
            break
    if anchor is None:
        return None
    # anchor cell tops define row tops; band bottom = tallest cell bottom in the row
    out = []
    anchor_cells = []
    for row in tagged:
        (_, ac), = [(cc, c) for (cc, c) in row if cc == anchor]
        anchor_cells.append(ac)
    tops = [ac.top for ac in anchor_cells]
    for i, row in enumerate(tagged):
        top = tops[i]
        bottom = max(c.bottom for (_, c) in row)
        cells = tuple(c for (_, c) in sorted(row, key=lambda cc: cc[0]))
        out.append(RowBand(top, bottom, cells))
    return tuple(out)


def _numeric_token_sum(text):
    """The exact sum of a cell's numeric tokens, or None if it has none.

    Identity for a single value. A multi-line box (the author drew no hrule inside it, so per
    the author it is ONE row) carries one value per boxed line — measured on a real report:
    two TBA bookings share a box whose measure cell reads '20,000 30,000', and the group's own
    printed subtotal (50,000) reconciles exactly with the token-sum. Non-numeric tokens
    (dates, dashes, words) contribute nothing; an all-non-numeric cell returns None.
    Exact decimal arithmetic — never float."""
    from decimal import Decimal
    from .headers import is_numeric
    total = None
    for tok in text.split():
        if is_numeric(tok):
            v = Decimal(tok.replace(",", "").replace("%", ""))
            total = v if total is None else total + v
    return total


def row_column_count(row, grid) -> int:
    """Number of DISTINCT OCCUPIED COLUMNS in `row` — cells bucketed by `column_of`, so two
    cells landing in the same column count ONCE. This is the unit `detect_aggregation_rows`
    (below) has always judged shape by (its `row_cols` dicts collapse same-column cells by
    construction); it diverged, before final-review F2, from a sibling check in
    `document._confirm_section_total` that counted raw `len(row.cells)` instead — the two
    coincide only when no row ever has two cells in one column. Factored out so both sites
    share ONE counting rule and can never drift apart again."""
    b = grid.boundaries
    return len({column_of((c.x0 + c.x1) / 2.0, b) for c in row.cells})


def is_aggregation_shaped(row, widest: int, grid) -> bool:
    """True iff `row` has the CANDIDATE aggregation shape (loop H, R4): exactly two distinct
    occupied columns (`row_column_count`, not raw cell count), strictly fewer than `widest`
    (the region's widest row, counted the SAME way). Shared by `detect_aggregation_rows` (the
    confirmed classifier, below) and `document._confirm_section_total`'s refusal-note gate —
    final-review F2's fix for the two having counted different things at the same shape
    question."""
    n = row_column_count(row, grid)
    return n == 2 and n < widest


def detect_aggregation_rows(rows, grid):
    """Arithmetic subtotal detection (loop H, residue R4). PROCEDURAL — and justified: this is
    the §8 gate's second procedural class, DECIDABLE EXACT ARITHMETIC (exact Decimal sums over
    a finite ordered row sequence; a SPARQL formulation of nested running-sum windows would be
    obfuscation, not a lift). The closed-world check is SHACL
    (tab:DetectedAggregationRowShape); language is NEVER read — a ' Total' suffix test is the
    tuned constant of natural language and is forbidden (spec §5).

    A row is a CANDIDATE iff it has exactly two DISTINCT OCCUPIED COLUMNS (`is_aggregation_shaped`
    below — cells bucketed by `column_of`, not raw cell count: two cells sharing one column
    count once), strictly fewer than the WIDEST populated-column count of the region's rows (a
    frequency mode dies on small groups — the Task 2 catch), one cell whose tokens are ALL
    numeric (the measure) and one that is not (the label). The label's COLUMN encodes the
    nesting level (measured: port totals carry their label in the Port column, month totals in
    the Month column).

    A candidate at row i with label column L and measure value v is CONFIRMED iff
    v == the token-sum, in the measure column, of the non-aggregation rows above i back to
    (exclusive) the previous CONFIRMED aggregation row whose label column <= L — and at least
    one member exists. Unconfirmed sparse rows remain ordinary rows AND contribute their
    token-sum to enclosing groups (the measured cascade). Zero-member candidates (a grand
    total directly after a same-level total) are never confirmed — honest refusal.

    Returns {row_index: (label_col, measure_col, member_indices)}.
    """
    from .headers import is_numeric
    b = grid.boundaries
    row_cols = []
    for rb in rows:
        cols = {}
        for c in rb.cells:
            cols[column_of((c.x0 + c.x1) / 2.0, b)] = c.text
        row_cols.append(cols)
    if not row_cols:
        return {}
    # The "normal" (full) row shape is the WIDEST one: real data rows are always
    # maximally populated; only aggregation candidates are ever sparser. A frequency mode
    # would tie against the max whenever aggregation-shaped rows outnumber full rows in a
    # sample — exact widest-row count, not a tuned constant.
    widest = max(len(rc) for rc in row_cols)
    agg = {}
    for i, rc in enumerate(row_cols):
        # final-review F2: the shape test is the SAME `is_aggregation_shaped` predicate
        # `document._confirm_section_total` uses — `rows[i]` re-buckets by `column_of` exactly
        # as `rc` above already did, so this is behavior-identical, not a new rule.
        if not is_aggregation_shaped(rows[i], widest, grid):
            continue
        # CANDIDATE classification is STRICT (every token numeric), while MEMBER contributions
        # below stay lenient (_numeric_token_sum). The distinction is load-bearing and was
        # caught on the real document: a month-total label like 'Jul 26 Total' contains the
        # numeric token '26', so lenient classification read it as a second measure — month
        # totals stopped being candidates, and every unconfirmed month total then polluted the
        # member sums of everything after it (detection collapsed from 17 rows to 4).
        measures = []
        labels = []
        for c, t in sorted(rc.items()):
            toks = t.split()
            if toks and all(is_numeric(tok) for tok in toks):
                measures.append((c, _numeric_token_sum(t)))
            else:
                labels.append(c)
        if len(measures) != 1 or len(labels) != 1:
            continue
        mcol, v = measures[0]
        lcol = labels[0]
        members = []
        total = None
        for j in range(i - 1, -1, -1):
            if j in agg:
                if agg[j][0] <= lcol:
                    break                      # previous same-or-outer aggregation: stop
                continue                       # inner aggregation: not a member
            if mcol not in row_cols[j]:
                continue                       # no cell in the measure column (a section-title
                                               # line): contributes nothing, so it is not an
                                               # operand either — §7, only emit what the source
                                               # supports (final-review M-2)
            members.append(j)
            s = _numeric_token_sum(row_cols[j][mcol])
            if s is not None:
                total = s if total is None else total + s
        if members and total is not None and total == v:
            agg[i] = (lcol, mcol, tuple(sorted(members)))
    return agg
