"""§1g: when the grid supersedes a band that ASSERTED, the band's table is WITHDRAWN.

R225 arm B, D2 (spec `2026-09-14-the-gate-not-the-predicate-design.md` § 1g, § 9d).

Until the adoption gate widened, every superseded band had ESCALATED, so withdrawing its
escalation CANDIDATE was the whole job — a candidate is a leaf proposition nothing points at, and
`_remove_escalation_record` removes it whole. A band that asserted carries a TABLE instead, and
the document driver merges the grid's graph beside the page's own: without a withdrawal the same
lines are read once by the band and again by the grid, in one graph, with nothing saying which
reading stands.

CI-VISIBLE BY CONSTRUCTION. The only corpus page exercising this is apple p2, and the corpus is
not fetched in CI — the exact hole [[R224]] found in the datagrid fallback and had to author a
fixture to close. `currency_marker_escalating_with_asserting_table_pdf` reaches it synthetically:
one escalating band (so the gate opens) plus one asserting band whose lines the page-wide grid
also reads.

WHAT IS NOT PINNED HERE. Whether the grid's reading of those lines is CORRECT: that is the same
question `test_adoption_document.py` leaves open for its own fixture. These tests pin that the
graph holds ONE reading of the contested lines, not that it is the right one.
"""
import pytest
from rdflib import RDF, URIRef

from iladub.etkl.holon import TAB

#: The pass-1 table of the ASSERTING band — minted under the page's own doc URI, which is the one
#: the driver merged and therefore the one the withdrawal has to remove.
BAND_TABLE = URIRef("https://example.org/etkl/doc#table1")


@pytest.fixture(scope="module")
def withdrawing_doc(tmp_path_factory):
    from tests.etkl.fixtures import currency_marker_escalating_with_asserting_table_pdf
    from iladub.etkl.document import compile_document
    p = tmp_path_factory.mktemp("withdraw") / "withdrawing.pdf"
    currency_marker_escalating_with_asserting_table_pdf(str(p))
    return compile_document(str(p))


def test_the_page_adopts_over_a_band_that_asserted(withdrawing_doc):
    """THE PRECONDITION, and it is what the widened gate bought: a page holding a PARTIAL band
    reading (one band escalating, one asserting 6 cells) is adoptable at all.

    Under the gate this loop replaced, one asserted cell disqualified the page outright — so this
    assertion is the whole of D2 in one line, and it fails if the `.rq`'s deleted `NOT EXISTS
    tab:EntryCell` clause is restored, or if `compile.py`'s `asserted_total == 0` precondition is.
    """
    assert withdrawing_doc.adopted == (0,), withdrawing_doc.adopted


def test_the_withdrawn_table_is_gone_from_the_document_graph(withdrawing_doc):
    """§1g's PIN. The asserting band's pass-1 table is not in the merged graph.

    FALSIFICATION: delete the `graph -= _sub` loop in `document.py`'s adoption branch and this
    fails with the table still present; restore it and it passes.
    """
    g = withdrawing_doc.graph
    assert (BAND_TABLE, RDF.type, None) not in g, "the superseded band's table survived the merge"
    assert not list(g.predicate_objects(BAND_TABLE)), list(g.predicate_objects(BAND_TABLE))


def test_no_line_is_read_twice(withdrawing_doc):
    """THE POINT OF THE WITHDRAWAL, stated as a count rather than as an absence.

    The graph holds exactly the grid's cells — the band's 6 are not there beside them. Stated
    against the grid region's own claim rather than a hard-coded number, so a fixture whose grid
    reads differently re-baselines itself instead of going quietly wrong.
    """
    cells = list(withdrawing_doc.graph.subjects(RDF.type, TAB.EntryCell))
    grid_regions = [r for r in withdrawing_doc.pages[0].regions
                    if r.verdict == "asserted" and r.anchor == str(TAB.DataGrid)]
    assert len(grid_regions) == 1, grid_regions
    assert len(cells) == grid_regions[0].cells, (len(cells), grid_regions[0].cells)


def test_the_superseded_band_claims_no_cells_and_names_no_table(withdrawing_doc):
    """A superseded band's QUANTITIES go with its reading; its `kind` and `reason` stay.

    `cells` and `table_uri` are zeroed for the same reason `tokens_asserted` is: the reading was
    replaced. Leaving them would make `sum(r.cells)` count the band's cells beside the grid's —
    the cell-level form of the double count — and leave a report naming a table in no graph.
    """
    superseded = [r for r in withdrawing_doc.pages[0].regions if r.verdict == "superseded"]
    assert len(superseded) == 2, superseded            # the escalating band and the asserting one
    for r in superseded:
        assert r.cells == 0, r
        assert r.table_uri is None, r
        assert r.tokens_asserted == 0 and r.tokens_escalated == 0, r
    assert any(r.reason == "REGION_TILING_FAILED" for r in superseded), "history is kept"


def test_the_pages_ledger_still_adds_up(withdrawing_doc):
    """I5 on the new shape: the page's totals ARE the sum of its per-region token counts.

    This is the identity the two latent defects of spec § 9c would have broken — a touched band
    that asserted keeping its `tokens_asserted`, and the grid region booking the page's asserted
    total instead of its own admitted lines. Both are invisible on a page where no band asserts,
    which is every adopting page the corpus had before this loop.
    """
    p = withdrawing_doc.pages[0]
    assert sum(r.tokens_asserted for r in p.regions) == p.asserted
    assert sum(r.tokens_escalated for r in p.regions) == p.escalated
    assert p.escalated > 0, "ink the grid did not read must keep escalating"
