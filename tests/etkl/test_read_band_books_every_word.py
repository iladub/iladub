"""R176 — a band the reader claims to have READ must book every word it holds.

The defect, measured corpus-wide before any of this was written
(`docs/superpowers/specs/2026-09-07-the-denominator-that-moves-design.md` § 1.1):

    verdict       bands        ink     booked   unbooked  unbooked%
    asserted         24       2482       2220        262  10.6%
    escalated        21       2996       2998         -2  -0.1%
    ignored         146       2935          0       2935  100.0%

An ESCALATED band books 100% of its ink; an IGNORED band books 0% BY DESIGN (its ink is prose --
`compile.py:801`); an ASSERTED band booked 89.4% and silently dropped the rest. So the score's
denominator was a property of the VERDICT, not of the page, and shrank by ~10% of a band's ink at
the exact moment the band started being read. That is what made `score` incomparable between two
readings of the same page.

WHY THE FIXTURES BELOW AND NOT THE CORPUS. Four assert branches book a SUBSET of their band, and
each mints a distinct table-URI prefix, which is how the census named them without inference:
`#ttable` (transposed, `compile.py:864`), `#rhtable` (row-hierarchical, `:872`), `#table`
(record, `:923`), `#mtable` (matrix, `:963`). The corpus exercises three of them; **no corpus
document reaches the row-hierarchical site at all**, so a corpus-only oracle is structurally blind
to a quarter of the subject. These fixtures cover all four in CI.

The `#htable` branches (`:1019`, `:1045`, `:1102`) already book every word and are NOT in scope --
`test_a_wholesale_branch_is_left_alone` is the pin that says so, because adding the repair there
would double-book.
"""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl import compile_tables
from iladub.etkl.compile import page_bands
from tests.etkl.fixtures import (
    all_text_hier_ruled_pdf,
    crosstab_table_pdf,
    row_grouped_table_pdf,
    simple_table_pdf,
    transposed_table_pdf,
)


def _bands_and_reports(path, page=0):
    """The band list `compile_tables` itself used, paired with the report it wrote for each.

    `reports[i]` IS `bands[i]`: the compile loop appends exactly one report per band and derives
    `tokens_*` by DIFFERENCING the running totals around each band's turn
    (`src/iladub/etkl/compile.py:767-771`), so this pairing is an identity rather than an
    alignment guess. The bands are CAPTURED from the compile call rather than re-derived, because
    `page_bands` takes `section_repair_bands` and a second independent call is only *probably* the
    same list.
    """
    from iladub.etkl import compile as C

    seen = []
    real = C.page_bands
    C.page_bands = lambda *a, **kw: (lambda got: (seen.append(got), got)[1])(real(*a, **kw))
    try:
        rep = C.compile_tables(str(path), page, validate_shapes=False)
    finally:
        C.page_bands = real
    assert len(seen) == 1, "expected exactly one page_bands call, saw %d" % len(seen)
    assert len(seen[0]) == len(rep.regions)
    return seen[0], rep


def _ink(band):
    return sum(len(ln.words) for ln in band.lines)


ASSERT_SITES = [
    (simple_table_pdf, "record  (compile.py:990, #table)"),
    (transposed_table_pdf, "transposed (compile.py:864, #ttable)"),
    (crosstab_table_pdf, "matrix  (compile.py:1034, #mtable)"),
    (row_grouped_table_pdf, "row-hier (compile.py:921, #rhtable)"),
]


@pytest.mark.parametrize("make,site", ASSERT_SITES, ids=[s.split()[0] for _, s in ASSERT_SITES])
def test_an_asserted_band_books_every_word_it_holds(tmp_path, make, site):
    """THE invariant (spec § 3.1). Every word of an asserted band lands in exactly one operand.

    Two-sided by construction: booking label ink as `escalated` instead of `asserted` would still
    satisfy this test, which is why `test_recovered_label_ink_is_ASSERTED_not_escalated` exists
    beside it. This one only pins that no word is DROPPED.
    """
    p = tmp_path / "t.pdf"
    make(str(p))
    bands, rep = _bands_and_reports(p)
    asserted = [(i, b, r) for i, (b, r) in enumerate(zip(bands, rep.regions))
                if r.verdict == "asserted"]
    assert asserted, "fixture asserts nothing -- it cannot exercise %s" % site
    for i, band, r in asserted:
        assert r.tokens_asserted + r.tokens_escalated == _ink(band), (
            "%s band %d books %d+%d of %d words"
            % (site, i, r.tokens_asserted, r.tokens_escalated, _ink(band)))


def test_recovered_label_ink_is_ASSERTED_not_escalated(tmp_path):
    """The other side of the fork: label ink the reading CARRIED is asserted, not escalated.

    `simple_table_pdf`'s header row round-trips into `tab:LabelCell`s, so its words reached the
    graph. Booking them `escalated` would satisfy the invariant above while claiming the reader
    failed to read what it demonstrably read -- and would drop this page off 1.0.
    """
    p = tmp_path / "t.pdf"
    make = simple_table_pdf
    make(str(p))
    bands, rep = _bands_and_reports(p)
    for band, r in zip(bands, rep.regions):
        if r.verdict != "asserted":
            continue
        assert r.tokens_escalated == 0, (
            "header ink was booked escalated: %d words" % r.tokens_escalated)
    assert rep.score == 1.0, rep.score


def test_a_wholesale_branch_is_left_alone(tmp_path):
    """The `#htable` branches already book `tokens` -- every word -- and must not gain the repair.

    Measured on the corpus before the repair: who-wfa p0 bands 3 and 5, `ink == booked == 76`,
    unbooked 0 on all 7 corpus bands reaching those sites. This fixture is the CI-runnable stand-in.
    A second booking there would push `tokens_asserted + tokens_escalated` ABOVE the band's ink
    plus its unit-marker ink, which is what this asserts cannot happen. The marker term is not
    slack: `_marker_word_count` is carried glyph ink that is genuinely booked ON TOP of
    `band.lines` on the paths that emit it (`compile.py:261-267`), and the corpus shows it doing
    exactly that -- apple p2 band 2 books 24 for 22 words of ink.
    """
    from iladub.etkl.compile import _marker_word_count
    p = tmp_path / "t.pdf"
    all_text_hier_ruled_pdf(str(p))
    bands, rep = _bands_and_reports(p)
    for i, (band, r) in enumerate(zip(bands, rep.regions)):
        if r.verdict == "ignored":
            continue
        ceiling = _ink(band) + _marker_word_count(band)
        assert r.tokens_asserted + r.tokens_escalated <= ceiling, (
            "band %d books %d, above its ceiling of %d -- double-booked"
            % (i, r.tokens_asserted + r.tokens_escalated, ceiling))
