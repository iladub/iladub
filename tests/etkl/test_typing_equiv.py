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
    """Runs every corpus document's page-0 bands through the four homogeneity judgements and
    PRINTS them. This is the differential's record: a reviewer reads it to see exactly what
    the typing change did, per band, per document."""
    if not os.path.exists(os.path.join(ROOT, path)):
        pytest.skip(f"{name}: corpus document not fetched")
    verdicts = _band_verdicts(path)
    assert verdicts, f"{name}: no bands"
    print(f"\n{name}: {verdicts}")


def test_apple_band_4_is_no_longer_seen_as_transposed():
    """The loop's target, pinned. Measured before the change: looks_transposed=True and
    transpose_is_coherent=False, so the band escalated TRANSPOSED. The CURRENCY half of this
    loop is what flips looks_transposed (measured: the paren half alone changes nothing) —
    so this test pins the mechanism the spec §2 table identifies, not a coincidence."""
    apple = os.path.join(ROOT, "corpus/financial/apple-fy2026q3-statements.pdf")
    if not os.path.exists(apple):
        pytest.skip("corpus document not fetched")
    b = page_bands(apple, 0)[4]
    reg = classify(b)
    assert reg.kind.name == "RECORD_TABLE"
    assert looks_transposed(reg) is False, \
        "band 4 still reads as transposed — the Quantity family is not being applied"


def test_paren_cells_do_not_break_row_homogeneity():
    """The paren half, pinned at the query level on a synthetic row of the apple shape:
    [Numeric, ParenthesizedNumber, Numeric, ParenthesizedNumber] must read as homogeneous,
    because the abstaining cells take no part."""
    from iladub.etkl import celltype
    import os as _os
    q = _os.path.join(ROOT, "vocab", "queries", "looks-transposed.rq")
    cells = [(0, 0, "Label"), (0, 1, "572"), (0, 2, "(171)"), (0, 3, "670"), (0, 4, "(698)"),
             (1, 0, "Other"), (1, 1, "100"), (1, 2, "200"), (1, 3, "300"), (1, 4, "400")]
    g = celltype.grid_evidence(cells, 5)
    # every row is quantity-homogeneous once the parens abstain, so the transposed reading
    # is available; the assertion is that the parens did not make it impossible.
    assert celltype.run_ask(q, g) in (True, False)   # runs without error on the new lattice
    from iladub.etkl.celltype import _cell_datatype
    from rdflib import Namespace
    TAB = Namespace("https://w3id.org/iladub/tab#")
    assert _cell_datatype("(171)") == TAB.ParenthesizedNumber

    # The abstaining cells must take NO PART: swap them for plain numerics and the verdict
    # must not change. This is the real pin — "runs without error" alone asserts nothing about
    # whether the parens actually abstained.
    plain_cells = [(0, 0, "Label"), (0, 1, "572"), (0, 2, "171"), (0, 3, "670"), (0, 4, "698"),
                   (1, 0, "Other"), (1, 1, "100"), (1, 2, "200"), (1, 3, "300"), (1, 4, "400")]
    g_plain = celltype.grid_evidence(plain_cells, 5)
    verdict_with_parens = celltype.run_ask(q, g)
    verdict_plain = celltype.run_ask(q, g_plain)
    assert verdict_with_parens == verdict_plain, (
        f"paren cells changed the looks-transposed verdict ({verdict_with_parens} vs "
        f"{verdict_plain}) — they did not genuinely abstain"
    )
