"""R224 — a region that claims cells claims ink, and names the table it claims.

The two invariants here (spec `2026-09-13-the-fallback-that-names-no-table-design.md` § 4) are
about a REGION's own bookkeeping, not about a band's. They exist because the datagrid fallback
(`src/iladub/etkl/compile.py:1351-1365`) produced, for two years' worth of loops, a region that
claimed 276 entry cells while booking 0 tokens and naming no table at all.

    I1  a region with verdict == "asserted" and cells > 0 books ink:
            tokens_asserted + tokens_escalated > 0
    I2  ... and names the table it asserted: table_uri is not None, and that URI is TYPED in
        the page graph.

WHY `> 0` AND NOT A RATIO. Cells and tokens are not proportional, measured across the corpus's
14 asserted record tables: cbh books 54 tokens for 13 cells, apple 6 for 3, graincorp 406 for
406. Any tighter form would be a tuned constant, which CLAUDE.md § 8 makes prima facie evidence
that the decision belongs in AXIOM or NEURAL rather than in a test.

WHY THIS FILE IS NOT A DUPLICATE OF `test_read_band_books_every_word.py`. That file's subject is
a BAND — it pairs report to band by index and asks whether the band's ink was booked. The
fallback's appended region has NO band (index `len(bands)`; see [[R202]]), so it falls outside
that file's pairing by construction, and the two invariants below are the only thing that reaches
it. This is the split the spec's § 4 states once: I3 keeps the band half, I1/I2 take the region
half.

WHY THE SYNTHETIC FIXTURE MATTERS. A sweep of every single-argument fixture in
`tests/etkl/fixtures.py` (2026-09-13) found ZERO that trip the fallback gate, so before
`border_only_grid_pdf` these invariants were checkable only against a gitignored corpus — which
is to say, not in CI. The corpus sweep below is kept as the wider oracle and is marked, but the
fixture test is the one that holds the line on every push.
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib.namespace import RDF  # noqa: E402

from tests.etkl.fixtures import border_only_grid_pdf  # noqa: E402

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
CORPUS_FILES = [
    "ag-trade/cbh-stem-2026-08-03.pdf",
    "ag-trade/graincorp-capacity-2026-08-04.pdf",
    "ag-trade/graincorp-stem-2026-07-31.pdf",
    "financial/apple-fy2026q3-statements.pdf",
    "gov-stats/bfs-population-bilan-2023.pdf",
    "gov-stats/ons-index-of-services-2026-02.pdf",
    "health/who-wfa-boys-zscore-0-5.pdf",
]


def _claiming_regions(rep):
    """Every region that claims to have READ something: asserted, with cells."""
    return [r for r in rep.regions if r.verdict == "asserted" and r.cells > 0]


# --------------------------------------------------------------- the CI half: the fixture

@pytest.fixture(scope="module")
def fallback_page(tmp_path_factory):
    from iladub.etkl.compile import compile_tables

    p = tmp_path_factory.mktemp("r224") / "border_only.pdf"
    border_only_grid_pdf(str(p))
    rep = compile_tables(str(p), 0, validate_shapes=False, datagrid_fallback=True)
    assert len(rep.regions) == 2, (
        "fixture drift: this page must reach the datagrid fallback and yield bands + 1 = 2 "
        "regions, got %d" % len(rep.regions))
    return rep


def test_the_fallback_region_books_the_ink_it_claims(fallback_page):
    """I1 on the fixture. The appended grid region claims 24 cells; it must book tokens too.

    Pre-repair this region booked 0 while the ignored band above it booked 24 — the tokens
    existed and were attributed to the wrong region, so the page total was correct and every
    sum identity held. Nothing but a per-region check can see that.
    """
    claiming = _claiming_regions(fallback_page)
    assert claiming, "fixture drift: the fallback must produce an asserted region with cells"
    for r in claiming:
        assert r.tokens_asserted + r.tokens_escalated > 0, (
            "a region claiming %d cells books no ink at all -- its tokens have been "
            "differenced onto some other region" % r.cells)


def test_the_fallback_region_names_the_table_it_asserted(fallback_page):
    """I2 on the fixture. `emit_data_grid` returns the grid's URI and it must reach the report.

    Pre-repair `compile.py:1359` discarded that return although it is declared `-> "URIRef"`
    (`datagrid.py:599-600`), so the grid sat in the graph while the report pointed at nothing,
    and every consumer keyed on `table_uri is not None` skipped it — intra-page section
    stitching (`document.py:1554`), the adoption driver's grid check (`document.py:1648`) and
    the document's chain assembly. The adopt twin at `compile.py:1477` never had this defect,
    which is what made it a dropped value rather than a missing feature.
    """
    for r in _claiming_regions(fallback_page):
        assert r.table_uri is not None, (
            "a region claiming %d cells names no table" % r.cells)
        assert (r.table_uri, RDF.type, None) in fallback_page.graph, (
            "%s is named by the report but carries no rdf:type in the page graph" % r.table_uri)


# ------------------------------------------------- the wider oracle: the corpus, all 7 docs

@pytest.mark.corpus
@pytest.mark.parametrize("rel", CORPUS_FILES)
def test_every_claiming_region_books_ink_and_names_its_table(rel):
    """I1 + I2 over the whole corpus, at DOCUMENT scope — the scope the score is computed at.

    Measured 2026-09-13 before the repair: of 14 asserted record-table regions corpus-wide,
    exactly 2 carried `table_uri=None` — ons p7#16 and p8#9 — and those same 2 booked 0 tokens.
    Both are this branch's signature, `compile.py:1363` being the only site that built a
    record-table report without passing a URI. This test is that sweep, frozen.
    """
    path = os.path.join(CORPUS, rel)
    if not os.path.exists(path):
        pytest.skip("corpus not fetched")
    from iladub.etkl.document import compile_document

    doc = compile_document(path)
    offenders = []
    for pi, rep in enumerate(doc.pages):
        for ri, r in enumerate(_claiming_regions(rep)):
            booked = r.tokens_asserted + r.tokens_escalated
            named = r.table_uri is not None
            typed = named and (r.table_uri, RDF.type, None) in doc.graph
            if booked <= 0 or not named or not typed:
                offenders.append(
                    "p%d region#%d cells=%d booked=%d uri=%s typed=%s"
                    % (pi, ri, r.cells, booked, r.table_uri, typed))
    assert not offenders, "%s: %d claiming region(s) fail I1/I2:\n  %s" % (
        rel, len(offenders), "\n  ".join(offenders))
