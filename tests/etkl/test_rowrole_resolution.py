"""Loop C — the driver: NEURAL propose -> tiling+conservation oracle -> promote.

Legality gates admission, never confidence. On any refusal the graph MUST be untouched and the
caller escalates MERGE_AMBIGUOUS. See spec §3.1.
"""
import pytest
from rdflib import Graph, Namespace, RDF, URIRef

from iladub.etkl.hierarchical import classify_hierarchical
from iladub.etkl.headers import merge_tiling_ok
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
from iladub.etkl.rowrole import resolve_header_row_roles
from tests.etkl.test_rowrole_reading import caption_and_wrap_band, out_of_grid_caption_band

ILADUB = Namespace("https://w3id.org/iladub#")
TAB = Namespace("https://w3id.org/iladub/tab#")
_T = URIRef("urn:doc#htable0")
_D = URIRef("urn:doc")


def _hreg_and_band():
    band = caption_and_wrap_band()
    hreg = classify_hierarchical(band)
    assert hreg is not None
    assert merge_tiling_ok(hreg.tree, hreg.grid) is False, "fixture must start escalating"
    return hreg, band


def _resolve(roles, confidence=0.8):
    hreg, band = _hreg_and_band()
    g = Graph()
    prop = None if roles is None else RowRoleProposal(roles, confidence, "test rationale")
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, FakeRowRoleProposer(prop))
    return g, out


def test_legal_reading_asserts_with_promotions():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None, "a legal, lossless reading must resolve"
    n_asserted, promos = out
    assert n_asserted > 0
    assert len(promos) == 2, "one promotion per classified non-leaf row"
    assert list(g.subjects(RDF.type, ILADUB.PromotionDecision))
    # the reading is a PROPOSITION, not an assertion of ground truth
    assert list(g.subjects(RDF.type, ILADUB.CandidateConcept))


def test_furniture_text_is_carried_as_a_caption():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None
    caps = {str(o) for _s, _p, o in g.triples((None, TAB.captionText, None))}
    assert caps == {"Monday", "5 May"}, caps


def test_merged_label_reaches_the_committed_graph():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None
    labels = {str(o) for _s, _p, o in g.triples((None, TAB.cellText, None))}
    assert "Unit Ref" in labels, labels


def test_abstaining_proposer_does_not_resolve():
    g, out = _resolve(None)
    assert out is None
    assert len(g) == 0, "graph must be untouched on refusal"


def test_all_level_reading_is_refused_by_the_oracle():
    # THE CONTRACT GUARD: an honest 'level' reading reproduces the illegal tree; the oracle
    # refuses it and the region escalates. High confidence must not rescue it.
    g, out = _resolve(("level", "level"), confidence=0.99)
    assert out is None, "an illegal reading must be refused regardless of confidence"
    assert len(g) == 0, "graph must be untouched on refusal"


def test_malformed_role_vector_is_refused():
    g, out = _resolve(("furniture",))          # wrong length
    assert out is None
    assert len(g) == 0


def test_unknown_role_is_refused():
    g, out = _resolve(("furniture", "wrap"))
    assert out is None
    assert len(g) == 0


def test_single_header_row_never_calls_the_proposer():
    # k == 0: nothing to classify -> return None without consulting the proposer.
    class _Exploding:
        def propose_header_row_roles(self, context):
            raise AssertionError("proposer must not be called when there are no non-leaf rows")

    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Word

    def _w(t, x0, x1, top):
        return Word(t, x0, x1, top, top + 10.0)

    def _line(ws, top):
        return Line(tuple(ws), top, top + 10.0)

    leaf = [_w("Item", 110, 140, 0.0), _w("Ref", 155, 172, 0.0),
            _w("Qty", 205, 230, 0.0), _w("Cost", 255, 285, 0.0)]
    d1 = [_w("aa", 110, 140, 12.0), _w("R1", 155, 172, 12.0),
          _w("10", 205, 230, 12.0), _w("1.5", 255, 285, 12.0)]
    band = Band((_line(leaf, 0.0), _line(d1, 12.0)), 0.0, 22.0)
    hreg = classify_hierarchical(band)
    if hreg is None:                            # a 2-line band may not classify; skip if so
        pytest.skip("band did not classify as hierarchical")
    g = Graph()
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, _Exploding())
    assert out is None
    assert len(g) == 0


def test_generator_valued_roles_still_promotes():
    # Regression: proposal.roles must be materialised ONCE and reused, not re-iterated. A
    # generator is a single-consumption iterable — if the driver consumes it once to build
    # the reading and again to emit promotions, the second pass silently yields zero
    # promotions while the reading still commits (a proposition passing as an assertion).
    hreg, band = _hreg_and_band()
    g = Graph()
    roles_gen = (r for r in ("furniture", "continuation"))
    prop = RowRoleProposal(roles_gen, 0.8, "test rationale")
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, FakeRowRoleProposer(prop))
    assert out is not None, "a legal, lossless reading must resolve even with a generator"
    n_asserted, promos = out
    assert n_asserted > 0
    assert len(promos) == 2, "one promotion per classified non-leaf row"
    assert len(list(g.subjects(RDF.type, ILADUB.PromotionDecision))) == 2


def test_round_trip_failure_refuses_via_the_n_le_0_guard():
    # THE n <= 0 GUARD, distinct from the malformed-vector and unplaceable-continuation guards
    # above: build_row_reading can produce a WELL-FORMED reading (a single non-leaf row, read as
    # its only legal single-role vector, 'furniture') that assert_hier_region itself then refuses
    # because the reading's region fails ITS OWN round-trip check (region_round_trips -> False ->
    # assert_hier_region emits ROUND_TRIP_FAIL into its (scratch) graph and returns n == 0). The
    # out-of-grid caption band's single non-leaf row sits entirely left of the grid boundaries;
    # reading it as furniture carries its text as a RegionCaption (so it is not the malformed- or
    # unplaceable-continuation guard that fires -- verified separately: build_row_reading returns
    # a non-None (nodes, captions, source_cells) here), but the resulting single-level leaf-only
    # tree fails the round trip against the source band. The driver must refuse via n <= 0 with
    # the CALLER's `graph` left untouched -- never fabricate the round trip.
    band = out_of_grid_caption_band()
    hreg = classify_hierarchical(band)
    assert hreg is not None
    assert merge_tiling_ok(hreg.tree, hreg.grid) is False, "fixture must start escalating"
    # Pin WHICH guard fires, not just the outcome: if a future change made build_row_reading
    # refuse this band, the two asserts below would stay green while silently no longer
    # covering n <= 0 (region_tiles is also False here, but n <= 0 short-circuits first).
    from iladub.etkl.rowrole import build_row_reading
    from iladub.etkl.headers import header_rows_of
    rows = header_rows_of(band, hreg.grid, hreg.body_line)
    assert build_row_reading(rows, hreg.grid, ("furniture",)) is not None, \
        "the reading must be well-formed, so the refusal is n <= 0 and not an earlier guard"
    g = Graph()
    prop = RowRoleProposal(("furniture",), 0.8, "test rationale")
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, FakeRowRoleProposer(prop))
    assert out is None, "a round-trip-failing reading must be refused"
    assert len(g) == 0, "graph must be untouched on refusal"


def test_proposer_is_called_exactly_once():
    # THE LOAD-BEARING INVARIANT: no search over the role space. 'all furniture' is always
    # legal and always conserves, so a retry loop or per-row calling would converge on it
    # and strip real header labels. A counting proposer makes any hidden retry visible.
    class _Counting:
        def __init__(self, proposal):
            self.proposal = proposal
            self.calls = 0

        def propose_header_row_roles(self, context):
            self.calls += 1
            return self.proposal

    hreg, band = _hreg_and_band()
    g = Graph()
    counting = _Counting(RowRoleProposal(("furniture", "continuation"), 0.8, "test rationale"))
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, counting)
    assert out is not None
    assert counting.calls == 1, "the proposer must be consulted exactly once per invocation"


def test_a_joined_label_points_at_the_source_cell_it_consumed_and_that_cell_carries_its_box():
    """[[R182]] — the edge and the geometry that make the containment shape expressible.

    Two facts in one committed graph, because either alone is useless: the label must REACH
    the source cell (`prov:wasDerivedFrom` — the same predicate `tab:RepeatedHeaderRow` uses
    for its own originating cells, `tab:RepeatedHeaderRow` in `vocab/ontology/tab.ttl`), and the source cell must
    carry WHERE it was (`tab:sourceRegion` + `tab:sourcePage`).

    NOT `tab:hasBBox` / `tab:onPage`, and this test pins the DEDICATED predicates on purpose.
    Those two carry `rdfs:domain tab:Cell`, so full RDFS closure types a `tab:HeaderSourceCell`
    as a `tab:Cell` — which carries `tab:sourceText`, not `tab:cellText` — and trips
    `tab:WrappedCellShape`. This loop shipped `tab:hasBBox` first; the membrane admitted it
    (subclass-only closure materialises no domain typing) and
    `tests/etkl/test_closure_equiv.py`'s owlrl leg refused 26 nodes. Assert the sibling
    predicates, or the next author will re-take the same wrong turn.
    """
    from rdflib.namespace import PROV
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None
    label = next(s for s, _p, o in g.triples((None, TAB.cellText, None)) if str(o) == "Unit Ref")
    srcs = list(g.objects(label, PROV.wasDerivedFrom))
    assert len(srcs) == 1, srcs
    src = srcs[0]
    assert (src, RDF.type, TAB.HeaderSourceCell) in g
    assert str(g.value(src, TAB.sourceText)) == "Unit"
    assert int(g.value(src, TAB.sourcePage)) == 0
    assert g.value(src, TAB.hasBBox) is None, \
        "a tab:HeaderSourceCell must NOT carry tab:hasBBox -- see the docstring"
    bb = g.value(src, TAB.sourceRegion)
    assert bb is not None, "a source cell a label claims as provenance must carry its box"
    assert (float(g.value(bb, TAB.x0)), float(g.value(bb, TAB.y0)),
            float(g.value(bb, TAB.x1)), float(g.value(bb, TAB.y1))) == (155.0, 12.0, 175.0, 22.0)


def test_an_unjoined_source_cell_claims_no_derivation():
    """The edge must not leak: the six header-region cells no continuation landed on are the
    provenance of nothing, and a shape that saw a spurious edge would compare unrelated boxes.
    Without this, deriving EVERY label from EVERY source cell would pass the test above."""
    from rdflib.namespace import PROV
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None
    derived = {str(g.value(o, TAB.sourceText)) for _s, _p, o in g.triples((None, PROV.wasDerivedFrom, None))
               if (o, RDF.type, TAB.HeaderSourceCell) in g}
    assert derived == {"Unit"}, derived
