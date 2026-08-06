"""Typing differential (spec 2026-08-06-quantity-typing-design.md §5).

This loop changes homogeneity for EVERY document, so the evidence must show which query
verdicts move and where. Each corpus document's real bands are run through the four
band-level homogeneity queries, and the verdicts are compared against a recorded baseline —
the four documents whose scores are the no-regression gate must not move at all."""
import os
import pytest
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
from iladub.etkl.orientation import looks_transposed, transpose_is_coherent
from iladub.etkl.headers import header_body_split

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOCS = [
    ("stem", "corpus/ag-trade/graincorp-stem-2026-07-31.pdf"),
    ("cbh", "corpus/ag-trade/cbh-stem-2026-08-03.pdf"),
    ("capacity", "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf"),
    ("apple", "corpus/financial/apple-fy2026q3-statements.pdf"),
]

# The no-regression gate (spec §4: stem 0.9655/2152 cells/chain [3], CBH 0.9047, capacity
# 1.0000, WHO 0.5597 all byte-identical pre/post this loop). These are the MEASURED page-0
# band verdicts under the production `compile.page_bands` seam, recorded here as a literal
# baseline so a future change to any of these four documents' verdicts is a test FAILURE,
# not just a printed line a reviewer has to notice.
EXPECTED_VERDICTS = {
    "stem": [
        ("NON_TABLE", None, None, None),
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 4, False, None),
        ("NON_TABLE", None, None, None),
    ],
    "cbh": [
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 7, False, None),
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 4, False, None),
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 5, False, None),
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 4, False, None),
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 1, False, None),
    ],
    "capacity": [
        ("NON_TABLE", None, None, None),
        ("NON_TABLE", None, None, None),
        ("NON_TABLE", None, None, None),
        ("RECORD_TABLE", 1, False, None),
        ("NON_TABLE", None, None, None),
    ],
    "apple": [
        ("NON_TABLE", None, None, None),
        ("NON_TABLE", None, None, None),
        ("UNSUPPORTED_TABLE", 1, False, None),
        ("UNSUPPORTED_TABLE", 1, False, None),
        ("RECORD_TABLE", 1, False, None),
        ("UNSUPPORTED_TABLE", 1, False, None),
        ("UNSUPPORTED_TABLE", 1, False, None),
        ("UNSUPPORTED_TABLE", 1, False, None),
    ],
}


def _band_verdicts(path, page=0):
    """(kind, header_body_split, looks_transposed, transpose_is_coherent) per band — the four
    band-level judgements this loop's typing change can move."""
    out = []
    for b in page_bands(os.path.join(ROOT, path), page):
        reg = classify(b)
        if reg.grid is None or reg.grid.ncols < 2:
            out.append((reg.kind.name, None, None, None))
            continue
        split = header_body_split(b, reg.grid)
        lt = looks_transposed(reg)
        co = transpose_is_coherent(reg) if lt else None
        out.append((reg.kind.name, split, lt, co))
    return out


@pytest.mark.parametrize("name,path", DOCS, ids=[d[0] for d in DOCS])
def test_band_verdicts_are_recorded_and_stable(name, path):
    """Runs every corpus document's page-0 bands through the four homogeneity judgements,
    PRINTS them for a reviewer, and GATES them against the measured baseline (spec §4's
    no-regression table). A verdict that moves on stem/CBH/capacity, or moves anywhere other
    than the apple band-4 transposition flip, fails here — not just in a diff a human has to
    notice."""
    if not os.path.exists(os.path.join(ROOT, path)):
        pytest.skip(f"{name}: corpus document not fetched")
    verdicts = _band_verdicts(path)
    assert verdicts, f"{name}: no bands"
    print(f"\n{name}: {verdicts}")
    assert verdicts == EXPECTED_VERDICTS[name], (
        f"{name}: page-0 band verdicts moved from the measured baseline (spec "
        f"2026-08-06-quantity-typing-design.md §4) — got {verdicts}, expected "
        f"{EXPECTED_VERDICTS[name]}"
    )


def test_apple_band_4_is_no_longer_seen_as_transposed():
    """The loop's target, pinned. Measured before the change: looks_transposed=True and
    transpose_is_coherent=False, so the band escalated TRANSPOSED. The CURRENCY half of this
    loop is what flips looks_transposed (measured: the paren half alone changes nothing) —
    so this test pins the mechanism the spec §2 table identifies, not a coincidence.

    The band is located by CONTENT ("(171)", the parenthesized cell the spec's measurement
    keys off) rather than a fixed index — band ORDER is not this test's claim, band IDENTITY
    is, and content-lookup survives a future band-ordering change that would otherwise let the
    wrong band pass silently."""
    apple = os.path.join(ROOT, "corpus/financial/apple-fy2026q3-statements.pdf")
    if not os.path.exists(apple):
        pytest.skip("corpus document not fetched")
    bands = page_bands(apple, 0)
    hits = [
        b for b in bands
        if any("(171)" in w.text for ln in b.lines for w in ln.words)
    ]
    assert len(hits) == 1, f"expected exactly one band containing '(171)', found {len(hits)}"
    b = hits[0]
    reg = classify(b)
    assert reg.kind.name == "RECORD_TABLE"
    assert looks_transposed(reg) is False, \
        "band containing '(171)' still reads as transposed — the Quantity family is not " \
        "being applied"


def test_paren_cells_do_not_break_row_homogeneity():
    """The paren half, pinned at the query level. A body row [Numeric, ParenthesizedNumber,
    Numeric, ParenthesizedNumber] (row index 1 — row 0 is the header row by convention and is
    excluded from both the row- and column-homogeneity checks) must read the same whether the
    negative cells are parenthesized or plain, because the abstaining cells take no part.

    A second body row (row index 2, disjoint text values) is included so the column-
    homogeneity check has two real contributing rows per column rather than one — with a
    single body row every populated column is trivially "homogeneous" regardless of typing,
    which would make this differential pass vacuously (fix round 1, C1: the reviewer's probe
    showed the pre-fix fixture returned the SAME verdict for parens, plain numerics, AND
    nonsense text, because the cells under test sat at row 0 where neither check looks, and
    the lone body row made every column trivially homogeneous).

    Fix-round verification (scratch script, not committed): with this fixture, monkeypatching
    `celltype._cell_datatype` so `ParenthesizedNumber` maps to `Text` (simulating the
    abstention breaking) flips the parens-present verdict True -> False while leaving the
    plain-numeric verdict at True — i.e. the equality assertion below WOULD fail if abstention
    regressed. See task-3-report.md for the full output."""
    from iladub.etkl import celltype
    q = os.path.join(ROOT, "vocab", "queries", "looks-transposed.rq")

    paren_cells = [
        (0, 0, "Header"), (0, 1, "Q1"), (0, 2, "Q2"), (0, 3, "Q3"), (0, 4, "Q4"),
        (1, 0, "Net income"), (1, 1, "572"), (1, 2, "(171)"), (1, 3, "670"), (1, 4, "(698)"),
        (2, 0, "Other"), (2, 1, "Q1 note"), (2, 2, "N/A"), (2, 3, "flag"), (2, 4, "text"),
    ]
    plain_cells = [
        (0, 0, "Header"), (0, 1, "Q1"), (0, 2, "Q2"), (0, 3, "Q3"), (0, 4, "Q4"),
        (1, 0, "Net income"), (1, 1, "572"), (1, 2, "171"), (1, 3, "670"), (1, 4, "698"),
        (2, 0, "Other"), (2, 1, "Q1 note"), (2, 2, "N/A"), (2, 3, "flag"), (2, 4, "text"),
    ]

    from iladub.etkl.celltype import _cell_datatype
    from rdflib import Namespace
    TAB = Namespace("https://w3id.org/iladub/tab#")
    assert _cell_datatype("(171)") == TAB.ParenthesizedNumber

    g_paren = celltype.grid_evidence(paren_cells, 5)
    g_plain = celltype.grid_evidence(plain_cells, 5)
    verdict_with_parens = celltype.run_ask(q, g_paren)
    verdict_plain = celltype.run_ask(q, g_plain)
    assert verdict_plain is True, (
        "fixture regression: the plain-numeric verdict must be True (traced by the "
        "reviewer) — otherwise the equality assertion below would pass vacuously with "
        "both verdicts False"
    )
    assert verdict_with_parens == verdict_plain, (
        f"paren cells changed the looks-transposed verdict ({verdict_with_parens} vs "
        f"{verdict_plain}) — they did not genuinely abstain"
    )
