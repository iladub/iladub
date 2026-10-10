"""[[R300]] — an adopted page's report names the tables its graph holds.

`compile_document` re-compiles an adopting page under `{page_doc_uri(p)}/adopt` and merges only
what that re-compile rebuilt: the grids, the residue, the superseded bands' withdrawal. Every band
the grid did NOT touch keeps PASS 1's subgraph, under `page_doc_uri(p)`. The driver used to
install the re-compile's report whole (`pages[p] = rep_a`), so an untouched band that asserted
named `…/p0/adopt#table1` while the graph held `…/p0#table1`. A consumer following the report to
the graph found nothing. On held-out fed-h41 that was p3 `htable7` and p10 `htable3`
(`docs/superpowers/2026-10-09-r300-cause-measured-handoff.md` § 2).

The fixture is synthetic, so this runs in CI. Its band inventory is measured in
`fixtures.currency_marker_escalating_with_untouched_table_pdf`'s docstring.
"""
import pytest
from rdflib import URIRef

SYNTH_ADOPTED_PAGE = 0
UNTOUCHED = 1                      # the all-text band no grid admits


@pytest.fixture(scope="module")
def doc(tmp_path_factory):
    from tests.etkl.fixtures import currency_marker_escalating_with_untouched_table_pdf
    from iladub.etkl.document import compile_document
    p = tmp_path_factory.mktemp("r300") / "untouched.pdf"
    currency_marker_escalating_with_untouched_table_pdf(str(p))
    return compile_document(str(p))


def test_the_page_adopts_beside_an_untouched_asserted_band(doc):
    """THE CONTROL. Without an asserted band that no grid supersedes, the pin below is vacuous:
    every other region on an adopted page is either a grid (from the re-compile's own graph) or
    carries no table at all."""
    assert doc.adopted == (SYNTH_ADOPTED_PAGE,), (doc.adopted, doc.notes)
    regions = doc.pages[SYNTH_ADOPTED_PAGE].regions
    r = regions[UNTOUCHED]
    assert (r.verdict, r.cells, r.tokens_asserted) == ("asserted", 6, 8)
    assert r.table_uri is not None
    assert not any(UNTOUCHED in g.supersedes for g in regions), \
        [(i, g.supersedes) for i, g in enumerate(regions)]


def test_every_asserted_report_names_a_table_in_the_document_graph(doc):
    """R300's criterion, on the synthetic adopted page."""
    dangling = [(p, i, r.table_uri)
                for p, page in enumerate(doc.pages)
                for i, r in enumerate(page.regions)
                if r.verdict == "asserted" and r.table_uri is not None
                and (URIRef(r.table_uri), None, None) not in doc.graph]
    assert dangling == []


def test_the_untouched_band_reads_as_pass_one_did(doc):
    """THE INSTALL IS PASS 1's REPORT, not a re-labelled copy of the re-compile's: the name is
    the page's own, and the reading's quantities are the ones pass 1 booked."""
    from iladub.etkl.document import page_doc_uri
    r = doc.pages[SYNTH_ADOPTED_PAGE].regions[UNTOUCHED]
    assert str(r.table_uri).startswith(f"{page_doc_uri(SYNTH_ADOPTED_PAGE)}#"), r.table_uri


# ------------------------------------------------- the refusal branch, unreached on all eleven
# documents (measured 2026-10-10), so it is pinned here rather than left to a corpus that
# cannot reach it.

def _report(verdict, cells, uri):
    from iladub.etkl.compile import RegionKind, RegionReport
    return RegionReport(RegionKind.RECORD_TABLE, verdict, cells, None, None, "",
                        table_uri=uri, tokens_asserted=cells)


def test_pass_one_is_installed_for_untouched_bands_only():
    from iladub.etkl.document import _untouched_from_pass_one
    pass1 = (_report("asserted", 3, "p0#table0"), _report("escalated", 0, None))
    recompiled = (_report("asserted", 3, "p0/adopt#table0"), _report("superseded", 0, None),
                  _report("asserted", 9, "p0/adopt#p0-datagrid"))
    assert _untouched_from_pass_one(pass1, recompiled, 2) == (
        pass1[0], recompiled[1], recompiled[2])


def test_a_band_the_two_compiles_read_differently_refuses():
    from iladub.etkl.document import _untouched_from_pass_one
    pass1 = (_report("asserted", 3, "p0#table0"),)
    recompiled = (_report("asserted", 4, "p0/adopt#table0"),
                  _report("asserted", 9, "p0/adopt#p0-datagrid"))
    assert _untouched_from_pass_one(pass1, recompiled, 1) is None


def test_the_driver_refuses_the_page_before_it_mutates_anything(tmp_path, monkeypatch):
    """The caller's half: None becomes a refusal note, and the grid never reaches the graph."""
    from tests.etkl.fixtures import currency_marker_escalating_with_untouched_table_pdf
    from iladub.etkl import document
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    monkeypatch.setattr(document, "_untouched_from_pass_one", lambda *a: None)
    p = tmp_path / "untouched.pdf"
    currency_marker_escalating_with_untouched_table_pdf(str(p))
    rep = document.compile_document(str(p), validate_shapes=False)
    assert rep.adopted == ()
    assert any("read an untouched band differently" in n for n in rep.notes), rep.notes
    assert not any(rep.graph.subjects(RDF.type, TAB.DataGrid))
