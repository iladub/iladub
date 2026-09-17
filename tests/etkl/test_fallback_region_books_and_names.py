"""R224 — a region that claims cells claims ink, and names the table it claims.

**THE ROUTE MOVED 2026-09-14 ([[R225]] D1); THE FILENAME DID NOT.** These invariants were written
against the datagrid fallback (`compile.py:1351`), whose only corpus instances were ons p7/p8 and
whose only synthetic fixture reached the gate by BEING R225's fusion defect. D1 repairs that
defect, so the fallback is now unreached on the corpus and uncoverable by any fixture ([[R228]]),
and these tests ride the ADOPTION route instead. The file keeps its name so `git log --follow`
keeps the history that explains why the invariants exist at all; renaming it would hide exactly
the reasoning a reader needs.

The invariants are about a REGION's own bookkeeping, not about a band's (spec
`2026-09-13-the-fallback-that-names-no-table-design.md` § 4). They exist because the fallback
produced, for two years' worth of loops, a region that claimed 276 entry cells while booking 0
tokens and naming no table at all.

    I1  a region with verdict == "asserted" and cells > 0 books ink:
            tokens_asserted + tokens_escalated > 0            <- FALSIFIABLE, and falsified
    I2  an UNTYPED, UNNAMED grid is REFUSED adoption                <- the guard, not the report

**WHY I2 IS STATED AS A REFUSAL AND NOT AS A PROPERTY OF THE REPORT.** In its original form — "the
claiming region names a table, and that URI is typed in the graph" — I2 cannot fail on this route:
`document.py:1629` refuses adoption when the report carries no `table_uri`, and `document.py:1687`
refuses it when the graph lacks `(grid_uri, rdf:type, tab:DataGrid)`. Both falsification attempts
(nulling `table_uri` at `compile.py:1590`; deleting `datagrid.py:641-642`) stopped the page
adopting, so the precondition collapsed and the tests ERRORED instead of the invariant FAILING.
The property is true by construction, so the claim moved to the guard that constructs it. This is
§ Producer-side guards vs the membrane inverted: the TEST was the duplicate of two guards.

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

from tests.etkl.fixtures import (  # noqa: E402
    currency_marker_escalating_with_asserting_table_pdf,
)

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
def adopting_doc(tmp_path_factory):
    """R224's I1/I2, RE-POINTED at the ADOPTION route (R225 D1, 2026-09-14).

    WHY THE SUBJECT MOVED, measured rather than preferred. These invariants used to ride
    `border_only_grid_pdf` through the datagrid fallback, and that fixture reached the gate by
    BEING [[R225]]'s defect reproduced synthetically: two page-border verticals fused the band to
    one column, so the page asserted nothing and `compile.py:1351` opened. D1 repairs the fusion,
    so the page now reads completely through its bands (`RECORD_TABLE`, 20 cells, score 1.0, ONE
    region) and the gate never opens. The fixture's mechanism was the defect, so repairing the
    defect destroyed the fixture.

    AND NO REPLACEMENT REACHES THAT GATE. Four candidate shapes were drawn and run
    (`docs/superpowers/2026-09-14-d1-post-d2-measured.md` § 3): the gate needs every >= 2-run row
    isolated in a <= 1-line band, `datagrid.py:363` needs >= 2-run rows to be the MODAL signature,
    and `bands.py:37-52` splits only above 1.8x the MEDIAN gap — whose small gaps can come only
    from multi-line single-run bands. Post-D1 the branch also has ZERO live corpus instances (ons
    p7/p8, its only two, now arrive adopt-scoped). Both facts are recorded as [[R228]]; the branch
    is NOT deleted here, because § Producer-side guards requires provable total coverage first and
    "no instance today" is not that proof.

    WHAT SURVIVES INTACT is the pair of claims, which were never about the fallback as such: a
    region that claims to have read something must BOOK ink (I1) and must NAME a table that exists
    in the graph (I2). Adoption appends exactly such a region. Measured on this fixture under D1:
    `adopted == (0,)`, one claiming region `p0 #2`, cells=18, booked=22, typed=True,
    `adopt#p0-datagrid` — so the population is non-empty by measurement, not by hope.
    """
    from iladub.etkl.document import compile_document

    p = tmp_path_factory.mktemp("r224") / "adopting.pdf"
    currency_marker_escalating_with_asserting_table_pdf(str(p))
    doc = compile_document(str(p))
    assert doc.adopted == (0,), (
        "fixture drift: this page must ADOPT, giving an adopt-scoped grid region; adopted=%r"
        % (doc.adopted,))
    return doc


def _all_claiming(doc):
    """Every claiming region across the document's pages — the population I1/I2 quantify over.

    NON-VACUITY IS ASSERTED BY THE CALLERS, not assumed here: an empty population would make both
    invariants pass with their subject absent, which is the failure CLAUDE.md plan rule 4 exists
    to catch (and which this very file's git history contains — see the `_band_table` note in
    `test_adoption_withdraws_the_table.py`).
    """
    return [(pi, ri, r)
            for pi, rep in enumerate(doc.pages)
            for ri, r in enumerate(_claiming_regions(rep))]


def test_the_adopted_grid_region_books_the_ink_it_claims(adopting_doc):
    """I1 on the adoption route. The adopt-scoped grid region claims cells; it must book ink too.

    Pre-repair (on the fallback route this test used to ride) the claiming region booked 0 while
    the ignored band above it booked 24 — the tokens existed and were attributed to the wrong
    region, so the page total was correct and every sum identity held. Nothing but a per-region
    check can see that, and that is why this claim outlives the branch it was written against.
    """
    claiming = _all_claiming(adopting_doc)
    assert claiming, "fixture drift: adoption must produce an asserted region with cells"
    for pi, ri, r in claiming:
        assert r.tokens_asserted + r.tokens_escalated > 0, (
            "p%d region#%d claims %d cells and books no ink at all -- its tokens have been "
            "differenced onto some other region" % (pi, ri, r.cells))


def test_an_untyped_grid_is_not_adopted(tmp_path, monkeypatch):
    """I2, RE-SCOPED TO THE GUARD — and the re-scoping is a MEASURED FINDING, not a preference.

    I2 used to assert that a claiming region names a table carrying `rdf:type`. On the adoption
    route that assertion **cannot fail**, because two producer-side guards already guarantee it
    upstream of any test:

        document.py:1629   if r.verdict != "asserted" or r.table_uri is None:   -> no adoption
        document.py:1687   if grid_uri is None or (grid_uri, RDF.type, TAB.DataGrid)
                               not in rep_a.graph:                              -> no adoption

    MEASURED, twice, while trying to falsify the old form: passing `table_uri=None` at the adopt
    twin (`compile.py:1590`), and removing both `rdf:type` triples for the grid
    (`datagrid.py:641-642`), each made the page STOP ADOPTING — so `adopted == (0,)` collapsed and
    the tests ERRORED in the fixture rather than FAILING on the invariant. A test whose subject is
    unreachable by any mutation pins nothing, which is the failure CLAUDE.md plan rule 4 exists to
    catch, and the shape it took here is the reverse of the usual one in § Producer-side guards vs
    the membrane: the TEST was the duplicate of two guards, not a guard duplicating a membrane.

    So the claim moves to where it can be refuted: the guard must REFUSE. An untyped grid must not
    be adopted — which fails the moment `document.py:1687` is deleted, and that is this test's
    falsification.

    `emit_data_grid` is monkeypatched rather than the graph edited afterwards because
    `compile.py:1505` imports it inside the adopt branch (late binding), so the patch reaches
    production code on the real path.
    """
    from iladub.etkl import datagrid as DG
    from iladub.etkl.document import compile_document

    real_emit = DG.emit_data_grid

    def emit_without_type(g, grid, lines, doc_uri, page, grid_uri=None):
        uri = real_emit(g, grid, lines, doc_uri, page, grid_uri)
        g.remove((uri, RDF.type, None))          # named, but untyped: the guard's exact subject
        return uri

    monkeypatch.setattr(DG, "emit_data_grid", emit_without_type)

    p = tmp_path / "untyped.pdf"
    currency_marker_escalating_with_asserting_table_pdf(str(p))
    doc = compile_document(str(p))

    assert doc.adopted == (), (
        "an UNTYPED grid was adopted: the driver's type guard (document.py:1687) did not refuse, "
        "so a page can be re-read against a grid the graph does not assert; adopted=%r"
        % (doc.adopted,))


def test_the_adopted_grid_region_names_the_table_it_asserted(adopting_doc):
    """I2's POSITIVE half, kept as a regression witness rather than as a falsifiable claim.

    See `test_an_untyped_grid_is_not_adopted` for why this one cannot fail on its own: the two
    guards make it true by construction. It stays because it is cheap and because it states the
    property in the form a reader expects to find it, but it is NOT this file's evidence — the
    negative test above is.

    `emit_data_grid` returns the grid's URI and it must reach the report.

    Pre-repair `compile.py:1359` discarded that return although it is declared `-> "URIRef"`
    (`datagrid.py:618-619`), so the grid sat in the graph while the report pointed at nothing,
    and every consumer keyed on `table_uri is not None` skipped it — intra-page section
    stitching (`document.py:1554`), the adoption driver's grid check (`document.py:1648`) and
    the document's chain assembly. The adopt twin at `compile.py:1477` never had this defect,
    which is what made it a dropped value rather than a missing feature.
    """
    claiming = _all_claiming(adopting_doc)
    assert claiming, "fixture drift: adoption must produce an asserted region with cells"
    for pi, ri, r in claiming:
        assert r.table_uri is not None, (
            "p%d region#%d claims %d cells and names no table" % (pi, ri, r.cells))
        assert (r.table_uri, RDF.type, None) in adopting_doc.graph, (
            "%s is named by the report but carries no rdf:type in the merged graph" % r.table_uri)


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
