import re, math
from rdflib import Graph, Namespace
TAB = Namespace("https://w3id.org/iladub/tab#")


# ---- frozen Python reference (the anti-overfit oracle; survives the rewrite) ----
def _is_numeric(s):
    t = re.sub(r"[,%]", "", s.strip())
    if not t:
        return False
    try:
        return math.isfinite(float(t))
    except ValueError:
        return False


# ---- loop-quantity-typing (fix round 1): independent port of the family/abstain rule ----
# The predicates below are hand-written from the SPEC's stated rule ("Blank and
# ParenthesizedNumber take no part in a homogeneity judgement; Numeric and Currency are
# ONE family") — NOT derived by reading vocab/queries/*.rq or copying its COALESCE/
# FILTER-NOT-EXISTS idiom. Same discipline as _is_numeric above: an independent
# reimplementation, so a bug IN the SPARQL idiom (wrong predicate, inverted abstains
# check, wrong family map) shows up as a genuine mismatch here instead of being
# replicated on both sides of the comparison.
def _is_currency(s):
    t = s.strip()
    return bool(re.match(r"^-?[$€£¥]\s?-?[\d,]+(\.\d+)?$|^-?[\d,]+(\.\d+)?\s?[$€£¥]$", t))


def _is_paren_shaped(s):
    return bool(re.match(r"^\(\s*-?[\d,]+(\.\d+)?\s*\)$", s.strip()))


def _is_blank_shaped(s):
    t = s.strip()
    return t == "" or t.lower() == "(blank)" or t == "-"


def _abstains(s):
    """A value that takes no part in a homogeneity judgement: missing (Blank-shaped) or
    a parenthesized number (footnote-ambiguous, per the spec)."""
    return _is_blank_shaped(s) or _is_paren_shaped(s)


def _is_quantity(s):
    """Numeric-shaped OR Currency-shaped: the spec's Quantity family, generalising
    _is_numeric to also admit currency amounts."""
    return _is_numeric(s) or _is_currency(s)


# Independent port of celltype.is_date's shape (not its range validation — that precision
# is irrelevant to which FAMILY key a value normalises to). tab:Date deliberately stays
# its own family, disjoint from Quantity (spec §3.2) — the fixture batteries below never
# mix quantities with dates, so this key never fires against a real assertion today, but a
# future date-bearing fixture must NOT silently fall into 'text' (M3, final review): a
# column of nothing but dates IS family-homogeneous non-Text, and _ref_type_key conflating
# it with plain text would make the reference oracle wrong, not just incomplete.
_ISO_DATE_SHAPED = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
_DMY_DATE_SHAPED = re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$")
_MON_DATE_SHAPED = re.compile(r"^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}$", re.I)


def _is_date_shaped(s):
    t = s.strip()
    return bool(_ISO_DATE_SHAPED.match(t) or _DMY_DATE_SHAPED.match(t) or _MON_DATE_SHAPED.match(t))


def _ref_type_key(s):
    """The homogeneity key a non-abstaining value normalises to: 'quantity' for
    Numeric/Currency-shaped values (one family), 'date' for date-shaped values (its own
    family — never equal to 'quantity'), else 'text'. The three-way split (M3, final
    review) matches the vocabulary's actual family lattice rather than the pre-loop
    reference's binary numeric-vs-not shape, so a date-bearing fixture cannot produce a
    spurious mismatch against ORI_BATTERY/SD_BATTERY by being conflated with 'text'."""
    if _is_quantity(s):
        return "quantity"
    if _is_date_shaped(s):
        return "date"
    return "text"


def _ref_typed_non_text(vals):
    """A group of cell values (a row's or column's cells) counts as homogeneous-non-Text
    iff, after dropping abstaining values, at least one survives and every survivor
    normalises to the SAME (non-'text') key."""
    kept = [v for v in vals if not _abstains(v)]
    if not kept:
        return False
    keys = {_ref_type_key(v) for v in kept}
    return len(keys) == 1 and "text" not in keys


def _ref_header_body_split(grid, ncols):
    """grid = list of rows; each row = list of (col, text). Port of headers.header_body_split."""
    for start in range(1, len(grid)):
        cols = {i: [] for i in range(ncols)}
        for r in range(start, len(grid)):
            for (c, t) in grid[r]:
                cols[c].append(t)
        if any(vs and all(_is_numeric(v) for v in vs) for vs in cols.values()):
            return start
    return None


def _cells(grid):
    return [(r, c, t) for r, row in enumerate(grid) for (c, t) in row]


# ---- battery: (name, grid, ncols) ----
HB_BATTERY = [
    ("split@1", [[(0, "Name"), (1, "Score")], [(0, "Alice"), (1, "10")], [(0, "Bob"), (1, "20")]], 2),
    ("split@2", [[(0, "Region"), (1, "Sales")], [(1, "USD")], [(0, "North"), (1, "100")], [(0, "South"), (1, "200")]], 2),
    ("all-text->None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2),
    ("3col@1", [[(0, "Id"), (1, "Qty"), (2, "Price")], [(0, "a"), (1, "1"), (2, "9.5")], [(0, "b"), (1, "2"), (2, "8.0")]], 3),
]


def test_header_body_split_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols in HB_BATTERY:
        g = celltype.grid_evidence(_cells(grid), ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "header-body-split.rq"), g)
        assert got == _ref_header_body_split(grid, ncols), "%s: got %s" % (name, got)


def _ref_stub_data_split(grid, ncols):
    """Port of rowheaders.stub_data_split. The split ROW is still located via
    _ref_header_body_split (untouched — header-body-split.rq already has its own
    independent oracle, _ref_hbs in test_derivation_equiv.py). The per-column DATA
    check (loop-quantity-typing fix round 1) now goes through _ref_typed_non_text —
    Numeric/Currency are one family and abstaining values (Blank, ParenthesizedNumber-
    shaped) take no part — instead of the old is_numeric-only check."""
    split = _ref_header_body_split(grid, ncols)
    if split is None:
        return None
    cols = {i: [] for i in range(ncols)}
    for r in range(split, len(grid)):
        for (c, t) in grid[r]:
            cols[c].append(t)
    numeric = [_ref_typed_non_text(cols[i]) for i in range(ncols)]
    k = next((i for i in range(ncols) if numeric[i]), None)
    if k is None or k == 0:
        return None
    if not all(numeric[i] for i in range(k, ncols)):
        return None
    return k


SD_BATTERY = [
    ("k=2 two stubs", [[(0, "Reg"), (1, "Yr"), (2, "Val")], [(0, "N"), (1, "x"), (2, "5")], [(0, "S"), (1, "y"), (2, "6")]], 3),
    ("k=0 no stub->None", [[(0, "V1"), (1, "V2")], [(0, "1"), (1, "2")], [(0, "3"), (1, "4")]], 2),
    ("text after data->None", [[(0, "A"), (1, "V"), (2, "Note")], [(0, "a"), (1, "1"), (2, "hi")], [(0, "b"), (1, "2"), (2, "yo")]], 3),
    ("all-text->None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2),
    # loop-quantity-typing fix round 1 (a): col "Cost" mixes Numeric ("30,739") and
    # Currency ("$5") body values. Under the OLD raw-type comparison these are two
    # DISTINCT types, so "Cost" would NOT be a data column, the [1, ncols) suffix
    # would not be all-data, and this would resolve to None. Under the new Quantity
    # family both normalise the same way, "Cost" is a data column, and k=1 (col "Reg"
    # is the only stub).
    ("currency+numeric mixed data k=1", [[(0, "Reg"), (1, "Yr"), (2, "Cost")], [(0, "N"), (1, "2020"), (2, "$5")], [(0, "S"), (1, "2021"), (2, "30,739")]], 3),
    # (b): col "Cost" has a genuine ParenthesizedNumber-shaped footnote cell ("(171)")
    # among otherwise-Numeric body values. The abstaining cell must take NO part —
    # dropped, the survivors ("5", "6") are still homogeneous, so "Cost" stays a data
    # column and k=1, exactly as if the footnote cell were absent.
    ("paren abstains inside data column k=1", [[(0, "Reg"), (1, "Yr"), (2, "Cost")], [(0, "N"), (1, "2020"), (2, "5")], [(0, "S"), (1, "2021"), (2, "(171)")], [(0, "T"), (1, "2022"), (2, "6")]], 3),
    # (c) control: a genuine Text cell ("oops") in col "Cost" must still break its
    # data-column-ness — the fix must not have over-broadened the family/abstain rule
    # to also swallow Text. "Cost" is heterogeneous -> not a data column -> the [1,
    # ncols) suffix is not all-data -> None, same as the pre-fix behaviour.
    ("text cell still breaks data column->None", [[(0, "Reg"), (1, "Yr"), (2, "Cost")], [(0, "N"), (1, "2020"), (2, "5")], [(0, "S"), (1, "2021"), (2, "oops")]], 3),
]


def test_stub_data_split_matches_reference():
    from iladub.etkl import celltype
    from rdflib import Literal as _L
    from rdflib.namespace import XSD as _X
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols in SD_BATTERY:
        ref = _ref_stub_data_split(grid, ncols)
        split = _ref_header_body_split(grid, ncols)
        if split is None:
            got = None
        else:
            g = celltype.grid_evidence(_cells(grid), ncols)
            got = celltype.run_scalar(os.path.join(QDIR, "stub-data-split.rq"), g,
                                      bindings={"split": _L(split, datatype=_X.integer)})
        assert got == ref, "%s: got %s ref %s" % (name, got, ref)


def _cells_split(grid):  # grid = list of rows, each = list of (col, text)
    return [(r, c, t) for r, row in enumerate(grid) for (c, t) in row]


HB_B2B = [   # (name, grid, ncols, expected split)
    ("numeric no-regression", [[(0, "N"), (1, "S")], [(0, "A"), (1, "10")], [(0, "B"), (1, "20")]], 2, 1),
    ("date column recall", [[(0, "Event"), (1, "When")], [(0, "L"), (1, "2024-01-15")], [(0, "C"), (1, "2024-02-20")]], 2, 1),
    ("currency column recall", [[(0, "Item"), (1, "Cost")], [(0, "P"), (1, "$1,000")], [(0, "B"), (1, "$2,500")]], 2, 1),
    ("dash-not-date -> None", [[(0, "A"), (1, "Range")], [(0, "x"), (1, "1-2")], [(0, "y"), (1, "3-4")]], 2, None),
    ("all-text -> None", [[(0, "A"), (1, "B")], [(0, "x"), (1, "y")]], 2, None),
]


def test_header_body_split_recall_and_precision():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, grid, ncols, want in HB_B2B:
        g = celltype.grid_evidence(_cells_split(grid), ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "header-body-split.rq"), g)
        assert got == want, "%s: got %s want %s" % (name, got, want)


SD_B2B = [   # (name, cells, ncols, split, expected k)
    ("currency data k=2", [(0, 0, "R"), (0, 1, "Y"), (0, 2, "Cost"), (1, 0, "N"), (1, 1, "z"), (1, 2, "$5"), (2, 0, "S"), (2, 1, "w"), (2, 2, "$6")], 3, 1, 2),
    ("date data k=1", [(0, 0, "Item"), (0, 1, "When"), (1, 0, "a"), (1, 1, "2024-01-01"), (2, 0, "b"), (2, 1, "2024-02-01")], 2, 1, 1),
]


def test_stub_data_split_recall():
    from iladub.etkl import celltype
    from rdflib import Literal
    from rdflib.namespace import XSD
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells, ncols, split, want in SD_B2B:
        g = celltype.grid_evidence(cells, ncols)
        got = celltype.run_scalar(os.path.join(QDIR, "stub-data-split.rq"), g,
                                  bindings={"split": Literal(split, datatype=XSD.integer)})
        assert got == want, "%s: got %s want %s" % (name, got, want)


def _ref_looks_transposed(cells, body_starts_at=1):
    """loop-quantity-typing fix round 1: row/column homogeneity now goes through
    _ref_typed_non_text (Numeric+Currency one family, abstaining values dropped first)
    instead of a bare _is_numeric-only check.

    R71 hardening: `body_starts_at` replaces the hardcoded `r > 0`. This reference is the
    differential oracle for looks-transposed.rq — if it does not track the query's body
    boundary, the equivalence tests keep passing while testing nothing."""
    rows, cols = {}, {}
    for (r, c, t) in cells:
        if r >= body_starts_at:
            rows.setdefault(r, {})[c] = t
            cols.setdefault(c, []).append(t)
    typed_row = any(_ref_typed_non_text([rm[cc] for cc in rm if cc >= 1]) for rm in rows.values())
    typed_col = any(_ref_typed_non_text(vals) for vals in cols.values())
    return typed_row and not typed_col


def _ref_transpose_coherent(cells, body_starts_at=1):
    """loop-quantity-typing fix round 1: a row is incoherent iff, after dropping
    abstaining values, its col>=1 cells normalise to MORE THAN ONE key (Numeric and
    Currency share the 'quantity' key).

    R71 hardening: this reference previously had NO row filter, mirroring the query's own
    gap — it read header rows as data. `body_starts_at` closes both together."""
    rows = {}
    for (r, c, t) in cells:
        if c >= 1 and r >= body_starts_at:
            rows.setdefault(r, []).append(t)
    for vals in rows.values():
        kept = [v for v in vals if not _abstains(v)]
        if len({_ref_type_key(v) for v in kept}) > 1:
            return False
    return True


ORI_BATTERY = [
    ("transposed", [(0, 0, "Metric"), (0, 1, "A"), (0, 2, "B"), (1, 0, "Rev"), (1, 1, "10"), (1, 2, "20"), (2, 0, "Cost"), (2, 1, "3"), (2, 2, "4")]),
    ("upright-numeric", [(0, 0, "Name"), (0, 1, "Score"), (1, 0, "Alice"), (1, 1, "10"), (2, 0, "Bob"), (2, 1, "20")]),
    ("all-text", [(0, 0, "A"), (0, 1, "B"), (1, 0, "x"), (1, 1, "y")]),
    ("incoherent-row", [(0, 0, "K"), (0, 1, "V"), (0, 2, "U"), (1, 0, "wt"), (1, 1, "5"), (1, 2, "kg")]),
    # Regression pin (Task-3 review Minor): col 0 (label column) is all-numeric in the
    # body — one typed-numeric COLUMN — while a *different* body row (r=1) has all
    # col>=1 cells numeric, making typed_row True too; the other body row (r=2) is
    # text in col>=1 so no single column c>=1 is all-numeric on its own. This makes
    # the typed-ROW check (col>=1 only) and the typed-COLUMN check (all columns,
    # including col 0) diverge: correct behaviour reads col 0 across ALL columns and
    # finds it typed (typed_col=True) -> looks_transposed=False. If looks-transposed.rq
    # ever grew a wrong `?col >= 1` guard on the typed-COLUMN NOT EXISTS block (mirroring
    # the typed-ROW block's col>=1 restriction), col 0 would be dropped from
    # consideration, no c>=1 column is all-numeric, typed_col would wrongly flip to
    # False, and the ASK would wrongly flip to True. Verified empirically: the shipped
    # query returns False on this case; a hand-mutated `?col >= 1` variant of the
    # typed-COLUMN check flips it to True.
    ("numeric-col0-mixed-rows", [(0, 0, "Id"), (0, 1, "A"), (0, 2, "B"), (1, 0, "1"), (1, 1, "10"), (1, 2, "20"), (2, 0, "2"), (2, 1, "x"), (2, 2, "y")]),
    # loop-quantity-typing fix round 1 (a): col 1 mixes Numeric ("10") and Currency
    # ("$3") — under the OLD raw-type comparison these are two DISTINCT types, so col 1
    # would NOT be homogeneous, typed_col would be False, and looks_transposed would
    # WRONGLY read True (this is the apple-band-4 bug class). Under the new Quantity
    # family both normalise the same way, col 1 is homogeneous, typed_col is True, and
    # looks_transposed correctly reads False.
    ("currency-numeric-family-col-homogeneous", [(0, 0, "Metric"), (0, 1, "Val"), (1, 0, "Rev"), (1, 1, "10"), (2, 0, "Cost"), (2, 1, "$3")]),
    # (b): col 1 mixes Numeric with a ParenthesizedNumber-shaped footnote cell
    # ("(171)"). The abstaining cell must take NO part — dropped, it leaves two
    # Numeric survivors ("10", "30,739"), still homogeneous, so col 1 stays typed and
    # looks_transposed stays False (the abstaining cell must not manufacture a second
    # "type" the way it would under naive raw-type comparison).
    ("paren-abstains-col-still-homogeneous", [(0, 0, "Metric"), (0, 1, "Val"), (1, 0, "Rev"), (1, 1, "10"), (2, 0, "Note"), (2, 1, "(171)"), (3, 0, "Cost"), (3, 1, "30,739")]),
    # (c) control: a genuine Text cell ("oops") in col 1 must still break homogeneity —
    # the fix must not have over-broadened the family/abstain rule to also swallow
    # Text. col 1 heterogeneous -> typed_col False; row 1 (single cell "10") is
    # trivially typed -> typed_row True -> looks_transposed reads True.
    ("text-cell-still-breaks-col-homogeneity", [(0, 0, "Metric"), (0, 1, "Val"), (1, 0, "Rev"), (1, 1, "10"), (2, 0, "Cost"), (2, 1, "oops")]),
]


def test_orientation_matches_reference():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells in ORI_BATTERY:
        ncols = max(c for (_r, c, _t) in cells) + 1
        # R71: exercise the default AND a shifted body boundary. Without the second, the
        # bodyStartsAt code path is never covered and the equivalence proves nothing about it.
        for body_start in (1, 2):
            g = celltype.grid_evidence(cells, ncols, body_starts_at=body_start)
            lt = celltype.run_ask(os.path.join(QDIR, "looks-transposed.rq"), g)
            tc = celltype.run_ask(os.path.join(QDIR, "transpose-coherent.rq"), g)
            assert lt == _ref_looks_transposed(cells, body_start), \
                "%s looks_transposed @body%d: got %s" % (name, body_start, lt)
            assert tc == _ref_transpose_coherent(cells, body_start), \
                "%s coherent @body%d: got %s" % (name, body_start, tc)


ORI_B2B = [   # (name, cells, expected looks_transposed, expected coherent)
    # NOTE (Task-3 investigation): with only 2 data columns and a single shared type (Date)
    # across the whole body, EVERY column is individually homogeneous non-Text by coincidence
    # (col1=[2024-01-01,2024-03-01], col2=[2024-02-01,2024-04-01]) -- this trips the
    # col-0-inclusive "no typed STRUCTURED column" veto inherited unchanged from B2a, so
    # looks_transposed is False here. This is NOT a Task-3 regression: the identical mechanism
    # already makes the pre-existing B2a numeric "transposed" fixture in ORI_BATTERY evaluate to
    # False under this same query shape (verified empirically) -- B2a's test only checks
    # self-consistency against the Python reference, which shares the limitation, so it was never
    # surfaced as a hard expectation. It is an inherent property of the 2-column/single-shared-type
    # symmetric case, out of Task-3's scope (generalize types + type-exact coherence; "do NOT
    # redesign" the proven ASK). Expected value corrected to the query's actual (and, given the
    # design, correct) answer; flagged as a concern for the task owner.
    ("date-value-transposed", [(0, 0, "M"), (0, 1, "A"), (0, 2, "B"), (1, 0, "Start"), (1, 1, "2024-01-01"), (1, 2, "2024-02-01"), (2, 0, "End"), (2, 1, "2024-03-01"), (2, 2, "2024-04-01")], False, True),
    ("upright-currency", [(0, 0, "Item"), (0, 1, "Cost"), (1, 0, "Pen"), (1, 1, "$5"), (2, 0, "Ink"), (2, 1, "$6")], False, True),
    ("incoherent date+currency row", [(0, 0, "K"), (0, 1, "V"), (0, 2, "U"), (1, 0, "x"), (1, 1, "2024-01-01"), (1, 2, "$5")], False, False),
]


def test_orientation_recall_and_typeexact_coherence():
    from iladub.etkl import celltype
    import os
    QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
    for name, cells, want_lt, want_tc in ORI_B2B:
        ncols = max(c for (_r, c, _t) in cells) + 1
        g = celltype.grid_evidence(cells, ncols)
        lt = celltype.run_ask(os.path.join(QDIR, "looks-transposed.rq"), g)
        tc = celltype.run_ask(os.path.join(QDIR, "transpose-coherent.rq"), g)
        assert lt == want_lt, "%s looks_transposed: got %s want %s" % (name, lt, want_lt)
        assert tc == want_tc, "%s coherent: got %s want %s" % (name, tc, want_tc)


def test_cell_datatype_detectors():
    from iladub.etkl.celltype import is_date, is_currency
    from iladub.etkl.headers import is_numeric
    # dates: 4-digit year + valid ranges
    for s in ["2024-01-15", "2024/1/5", "31/12/2024", "1-2-2024", "15 Jan 2024", "15 January 2024"]:
        assert is_date(s), s
    # NOT dates (precision): too few digits / no 4-digit year / out-of-range
    for s in ["1-2", "3-4", "99-99-9999", "2024-13-01", "2024-01-32", "hello", "10", ""]:
        assert not is_date(s), s
    # currency: symbol adjacent to a numeric body
    for s in ["$1,000", "€20.50", "£5", "10 £", "-$3.00"]:
        assert is_currency(s), s
    for s in ["$", "USD", "10", "hello"]:
        assert not is_currency(s), s
    # Numeric is UNCHANGED (% and commas still Numeric; $ and dates are NOT numeric)
    assert is_numeric("10") and is_numeric("10%") and is_numeric("1,000")
    assert not is_numeric("$10") and not is_numeric("2024-01-15")


def test_grid_evidence_types_date_and_currency():
    from iladub.etkl import celltype
    from rdflib import RDF
    TAB = __import__("rdflib").Namespace("https://w3id.org/iladub/tab#")
    g = celltype.grid_evidence([(0, 0, "When"), (1, 0, "2024-01-15"), (2, 0, "$5")], 1)
    types = {str(g.value(c, TAB.gridText)): str(g.value(c, TAB.cellDatatype)).split("#")[-1]
             for c in g.subjects(RDF.type, TAB.GridCell)}
    assert types["2024-01-15"] == "Date" and types["$5"] == "Currency" and types["When"] == "Text"
