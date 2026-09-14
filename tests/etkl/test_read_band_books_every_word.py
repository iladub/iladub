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
    border_only_grid_pdf,
    transposed_table_pdf,
)


def _bands_and_reports(path, page=0, **compile_kw):
    """The band list `compile_tables` itself used, paired with the report it wrote for each.

    `reports[i]` IS `bands[i]` FOR EVERY i < len(bands): the compile loop appends exactly one
    report per band and derives `tokens_*` by DIFFERENCING the running totals around each band's
    turn (`src/iladub/etkl/compile.py:767-771`), so this pairing is an identity rather than an
    alignment guess. The bands are CAPTURED from the compile call rather than re-derived, because
    `page_bands` takes `section_repair_bands` and a second independent call is only *probably* the
    same list.

    PAIRED BY BAND INDEX, NOT BY EQUAL LENGTHS ([[R224]] I3, spec § 4). This helper used to assert
    `len(bands) == len(rep.regions)`, which REFUSED the datagrid fallback's shape — reports =
    bands + 1 — rather than checking it, and that refusal is one of the three reasons a defect
    from 2026-08-09 survived to be found by measurement instead of by CI. The fallback appends ONE
    region beyond the band loop, at index `len(bands)`, which by construction has NO band (this is
    [[R202]]'s answer, and the band-index contract `document.py:1648` already relies on it). That
    appended region is out of scope here and is checked by I1/I2 in
    `test_fallback_region_books_and_names.py`; every caller below zips, so it is dropped.
    """
    from iladub.etkl import compile as C

    seen = []
    real = C.page_bands
    C.page_bands = lambda *a, **kw: (lambda got: (seen.append(got), got)[1])(real(*a, **kw))
    try:
        rep = C.compile_tables(str(path), page, validate_shapes=False, **compile_kw)
    finally:
        C.page_bands = real
    assert len(seen) == 1, "expected exactly one page_bands call, saw %d" % len(seen)
    assert len(rep.regions) in (len(seen[0]), len(seen[0]) + 1), (
        "reports must be one per band, plus AT MOST the fallback's appended grid region: "
        "%d bands, %d reports" % (len(seen[0]), len(rep.regions)))
    return seen[0], rep


def _ink(band):
    return sum(len(ln.words) for ln in band.lines)


def test_no_band_books_ink_it_does_not_hold_on_the_fallback_page(tmp_path):
    """I3 ([[R224]], spec § 4) — the datagrid fallback must not book its grid's ink on a BAND.

    THE DEFECT THIS PINS, measured on ons-index-of-services 2026-09-13: the branch added the
    grid's tokens to `asserted_total` BEFORE appending its own `band_marks` entry, so the mark
    that closes the LAST BAND's slot already contained them and the differencing at
    `compile.py:1370` booked 285 words onto a 6-word IGNORED PROSE BAND (p8: 286 onto 4 words),
    while the grid's own report booked 0. Totals were preserved exactly, which is why no score
    moved and why the two sum identities (`test_datagrid.py:1149`,
    `test_adoption_document.py:141`) stayed true throughout.

    The IGNORED clause is the load-bearing one and it is two-sided. An ignored band books nothing
    BY DESIGN — its ink is prose (`compile.py:801`) — so `tokens == 0` there is not a tautology
    about this fixture but the exact statement the defect violated. Restoring the original
    statement order makes this fail with 24 booked on a band the reader never claimed to read.

    RETIRED 2026-09-14 (R225 D1) — NOT re-pointed, and the distinction is the point.

    Its two siblings in `test_fallback_region_books_and_names.py` (I1: a claiming region books
    ink; I2: it names a table) were RE-POINTED at the adoption route, because those claims were
    never about the fallback as such. **This one cannot follow them.** Its subject is the region
    appended BEYOND the band loop at index `len(bands)` — the thing that made `reports = bands +
    1` — and it pins that such a region's ink is not differenced onto the band below it. At
    document scope there is no such region: the adopted page's report is REBUILT, and its regions
    are the superseded bands, the grid and the residue, which are not band-paired at all
    (measured on the adopting fixture: 4 regions over 2 bands). `zip(bands, rep.regions)` has no
    meaning there, so the assertion has no subject rather than a moved one.

    Nor can it keep its own fixture: `border_only_grid_pdf` reached the gate by BEING R225's
    defect, so D1 repairs the page into a complete band reading (`RECORD_TABLE`, 20 cells, score
    1.0, ONE region) and the fallback never opens. Four replacement shapes were drawn and none
    reaches the gate, with a counting argument for why none can
    (`docs/superpowers/2026-09-14-d1-post-d2-measured.md` § 3).

    So the invariant is true and unreachable, and that is recorded as [[R228]] rather than left
    silent — per the standing instruction in the loop's own spec § 7. The fallback branch itself
    is deliberately NOT deleted (§ Producer-side guards: provable total coverage first; "no
    instance today" is not that proof), and `border_only_grid_pdf` is kept for the same reason.

    AN EXPLICIT SKIP, NOT AN EMPTY BODY. A test function whose body is only a docstring PASSES,
    which would leave a green test pinning nothing — the exact failure CLAUDE.md plan rule 4
    exists to catch. `pytest.skip` makes the retirement visible in every run instead.
    """
    pytest.skip("R228: the datagrid fallback is unreached post-D1 and this invariant has no "
                "document-scope subject — see the docstring and residues-open.md R228")


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

    WHICH OF THE THREE IT ACTUALLY COVERS, found by FALSIFYING rather than by reading — a first
    attempt injected the forbidden double-booking at `compile.py:1110` and this test **passed**,
    pinning nothing. Tracing the five `#htable`-producing fixtures
    (`all_text_hier_ruled_pdf`, `subtotal_hier_table_pdf`, `pivoted_table_pdf`,
    `left_aligned_parent_ruled_pdf`, `bordered_two_level_header_ruled_pdf`) shows **every one of
    them books at `:1193` and none at `:1110` or `:1136`**. Re-aimed at `:1193` the injection
    fails this test loudly (`tokens_escalated` 0 → 26), so it does pin its branch.
    **The other two wholesale branches are reached by CORPUS documents only** (who-wfa's ruled
    bands) and are therefore not guarded in CI — a new instance of [[R173]]'s open half, recorded
    here rather than left for the next reader to rediscover the same way.
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
