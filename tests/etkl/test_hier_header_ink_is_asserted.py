"""Header ink a hierarchical reading CARRIED is booked asserted, not escalated.

The defect, measured 2026-09-27 (`docs/superpowers/2026-09-27-cbh-boxhead-is-bookkeeping-evidence.md`):
the `#htable` assert branches book `max(0, tokens - n)` as escalated, where `n` is
`assert_hier_region`'s asserted BODY-token count. The header nodes the same call emitted — tiled,
SHACL-disposed, each with the box of the words it was read from ([[R177]]) — therefore landed in
`e`. On cbh, graincorp-stem and who that was ALL of the document's escalated ink but three words.

R176 (`test_read_band_books_every_word.py`) left these branches alone on purpose because they book
every word, which is still true and still pinned there. They booked it on the wrong side.

THE ORACLE IS INDEPENDENT OF THE BOOKING. It spies on the real emitter (never a mock) to read the
tree and `body_line` it was handed, and derives the expected escalation from the band's own words:
a word is escalated iff it is in no body line AND in no emitted header-node box. Exact containment,
no tolerance — a node's box is min/max over its own words.
"""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

import tests.etkl.fixtures as F
from tests.etkl.test_read_band_books_every_word import _bands_and_reports, _ink

# Every CI fixture measured 2026-09-27 to reach an asserted `#htable` band that booked escalated
# ink before the repair.
FIXTURES = [
    "all_text_hier_ruled_pdf", "bordered_two_level_header_ruled_pdf", "cut_group_two_page_pdf",
    "left_aligned_parent_ruled_pdf", "page_local_group_two_page_pdf", "partial_merge_report_pdf",
    "pivoted_table_pdf", "record_and_pivot_pdf", "region_pivot_pdf",
    "spanner_with_space_ruled_pdf", "stacked_banner_ruled_pdf", "subtotal_hier_table_pdf",
    "unequal_width_merge_report_pdf",
]


def _rowrole_kw():
    from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
    prop = RowRoleProposal(("furniture", "continuation"), 0.85, "date caption + wrap fragment")
    return {"row_role_proposer": FakeRowRoleProposer(prop)}


# (id, builder, compile kwargs). The thirteen fixtures reach the ruled and plain `#htable` sites;
# the last case is the CI route into the NEURAL-proposer site (`test_rowrole_integration.py`'s
# success path). Each of the three sites was blinded in turn and fails a case here.
#
# The SPAN-DONATION site keeps `max(0, tokens - n)` on purpose: a donated header's words live in
# the DONOR band, so the recipient band holds no carried header ink and the repair there is a no-op
# on every input measured (blinding it left `test_span_donation_seam.py`'s page green, and
# graincorp-capacity, the corpus's only donated table, already books e = 0). Code nothing can pin
# does not ship.
CASES = ([(n, getattr(F, n), dict) for n in FIXTURES]
         + [("rowrole_resolving_proposer", F.caption_wrap_report_pdf, _rowrole_kw)])


def _spy_emitter(monkeypatch):
    import iladub.etkl.holon as H
    real = H.assert_hier_region
    seen = {}

    def spy(g, region, band, *a, **kw):
        n = real(g, region, band, *a, **kw)
        if n > 0:                                  # the last SUCCESSFUL emission for this band
            seen[id(band)] = (region, n)
        return n
    monkeypatch.setattr(H, "assert_hier_region", spy)
    return seen


def _expected_escalated(band, region):
    boxes = [(h.x0, h.top, h.x1, h.bottom) for h in region.tree
             if None not in (h.x0, h.top, h.x1, h.bottom)]
    body = {id(w) for ln in band.lines[region.body_line:] for w in ln.words}
    return sum(1 for ln in band.lines for w in ln.words
               if id(w) not in body
               and not any(x0 <= w.x0 and w.x1 <= x1 and y0 <= w.top and w.bottom <= y1
                           for x0, y0, x1, y1 in boxes))


@pytest.mark.parametrize("name,make,kw", CASES, ids=[c[0] for c in CASES])
def test_carried_header_ink_is_booked_asserted(tmp_path, monkeypatch, name, make, kw):
    from iladub.etkl.compile import _marker_word_count
    seen = _spy_emitter(monkeypatch)
    p = tmp_path / "t.pdf"
    make(str(p))
    bands, rep = _bands_and_reports(p, **kw())
    checked = 0
    for i, (band, r) in enumerate(zip(bands, rep.regions)):
        if r.verdict != "asserted" or "#htable" not in str(r.table_uri or ""):
            continue
        region, n = seen[id(band)]
        want = _expected_escalated(band, region)
        assert r.tokens_escalated == want, (
            "%s band %d books %d escalated; only %d of its words lie outside the body and every "
            "emitted header node" % (name, i, r.tokens_escalated, want))
        assert r.tokens_asserted + r.tokens_escalated <= _ink(band) + _marker_word_count(band), (
            "%s band %d double-books" % (name, i))
        checked += 1
    assert checked, "fixture drift: %s reaches no asserted #htable band" % name


def test_a_span_resolution_hands_back_the_header_boxes_it_emitted():
    """The span-proposer route into the NEURAL site has no `compile_tables` path in CI (its fixture
    is assembled by hand, `test_span_gate._ambiguous_hier_region`), so its pass-through is pinned
    here: the extents a resolution returns are exactly the boxed header labels it wrote."""
    from rdflib import Graph, RDF, URIRef
    from iladub.etkl.holon import TAB
    from iladub.etkl.propose import FakeSpanProposer, SpanProposal
    from iladub.etkl.span import resolve_ambiguous_merge
    from tests.etkl.test_span_gate import _ambiguous_hier_region
    hreg, band = _ambiguous_hier_region()
    g, extents = Graph(), []
    out = resolve_ambiguous_merge(g, hreg, band, URIRef("urn:doc#htable0"), URIRef("urn:doc"), 0,
                                  FakeSpanProposer(SpanProposal("standalone", 0.8, "x")), extents)
    assert out is not None, "fixture drift: the tie must resolve"
    boxed = [lc for h in g.subjects(RDF.type, TAB.HeaderNode) for lc in g.objects(h, TAB.hasLabel)
             if (lc, TAB.hasBBox, None) in g]
    assert boxed, "fixture drift: the reading emits no boxed header label"
    assert len(extents) == len(boxed)
