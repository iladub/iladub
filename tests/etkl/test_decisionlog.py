"""The reading decision record (spec 2026-08-07-reading-decision-record-design.md).

Every judgement on the band-to-verdict path becomes a dec:DecisionHolon, so the reading is
queryable rather than lost. Uses only the owned dec: vocabulary — the differential half
(optionSpace/chosen/rejectedBecause) which had no producer before this loop."""
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS, PROV
import pytest
from pyshacl import validate

DEC = Namespace("https://w3id.org/iladub/dec#")
DOC = URIRef("urn:test:doc")


def _rec(g, agent=None):
    from iladub.etkl.decisionlog import ReadingRecorder
    return ReadingRecorder(g, DOC, 0, agent=agent)


def test_a_decision_records_its_option_space_and_choice():
    g = Graph()
    b = _rec(g).band(3)
    d = b.record("kind", options=["RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"],
                 chosen="UNSUPPORTED_TABLE",
                 rationale="header has 1 words but 5 columns")
    assert (d, RDF.type, DEC.DecisionHolon) in g
    opts = list(g.objects(d, DEC.optionSpace))
    assert len(opts) == 3, "every candidate considered must be recorded, not just the winner"
    labels = {str(l) for o in opts for l in g.objects(o, RDFS.label)}
    assert labels == {"RECORD_TABLE", "UNSUPPORTED_TABLE", "NON_TABLE"}
    chosen = list(g.objects(d, DEC.chosen))
    assert len(chosen) == 1
    assert str(next(g.objects(chosen[0], RDFS.label))) == "UNSUPPORTED_TABLE"
    assert str(next(g.objects(d, DEC.rationale))) == "header has 1 words but 5 columns"


def test_rejected_options_carry_their_refutation():
    """The differential's point: a discarded candidate names the observation that killed it."""
    g = Graph()
    b = _rec(g).band(3)
    d = b.record("kind", options=["RECORD_TABLE", "UNSUPPORTED_TABLE"],
                 chosen="UNSUPPORTED_TABLE",
                 rationale="header has 1 words but 5 columns",
                 rejected={"RECORD_TABLE": "header has 1 words but 5 columns"})
    rej = [o for o in g.objects(d, DEC.optionSpace)
           if (o, DEC.rejectedBecause, None) in g]
    assert len(rej) == 1
    assert str(next(g.objects(rej[0], RDFS.label))) == "RECORD_TABLE"
    assert "1 words" in str(next(g.objects(rej[0], DEC.rejectedBecause)))
    # the chosen option is never also rejected
    chosen = next(g.objects(d, DEC.chosen))
    assert (chosen, DEC.rejectedBecause, None) not in g


def test_order_increments_within_a_band_and_restarts_per_band():
    """dec:order is what makes 'which gate fired first' answerable — the R55 question."""
    g = Graph()
    r = _rec(g)
    b3 = r.band(3)
    d1 = b3.record("kind", ["A", "B"], "A", "first")
    d2 = b3.record("transposed", ["A", "B"], "A", "second")
    b5 = r.band(5)
    d3 = b5.record("kind", ["A", "B"], "A", "other band")
    assert int(next(g.objects(d1, DEC.order))) == 0
    assert int(next(g.objects(d2, DEC.order))) == 1
    assert int(next(g.objects(d3, DEC.order))) == 0, "order is per band, not global"


def test_decisions_nest_band_under_page():
    """dcterms:isPartOf gives the document -> page -> band -> judgement hierarchy."""
    g = Graph()
    r = _rec(g)
    d = r.band(3).record("kind", ["A", "B"], "A", "why")
    band_node = next(g.objects(d, DEC.withinProcess))
    page_node = next(g.objects(band_node, DCTERMS.isPartOf))
    assert (page_node, DCTERMS.isPartOf, DOC) in g


def test_evidence_is_linked_when_supplied():
    g = Graph()
    ev = URIRef("urn:test:evidence")
    d = _rec(g).band(1).record("kind", ["A", "B"], "A", "why", evidence=[ev])
    assert (d, DEC.consideredEvidence, ev) in g


def test_regarding_points_at_the_band_region():
    g = Graph()
    d = _rec(g).band(4).record("kind", ["A", "B"], "A", "why")
    reg = next(g.objects(d, DEC.regarding))
    assert "region4" in str(reg), f"regarding should name the band's region, got {reg}"


def test_recorder_writes_only_to_the_graph_it_was_given():
    """The membrane hazard (spec §3.1): decisions must never leak into a region scratch graph."""
    g, other = Graph(), Graph()
    _rec(g).band(0).record("kind", ["A", "B"], "A", "why")
    assert len(other) == 0
    assert len(g) > 0


def test_every_emitted_decision_conforms_to_dec_shapes():
    """Validate that all emitted dec:DecisionHolon nodes conform to dec:DecisionHolonShape."""
    from pathlib import Path
    g = Graph()
    r = _rec(g)
    # Build a representative graph with multiple bands and judgements.
    b3 = r.band(3)
    d1 = b3.record("kind", ["RECORD_TABLE", "UNSUPPORTED_TABLE"], "RECORD_TABLE", "choice 1")
    d2 = b3.record("transposed", ["A", "B"], "B", "choice 2",
                   rejected={"A": "reason A"})
    b5 = r.band(5)
    d3 = b5.record("kind", ["X", "Y"], "Y", "choice 3")

    # Load the ontology and shapes.
    repo_root = Path(__file__).parent.parent.parent
    onto_path = repo_root / "vocab" / "ontology" / "dec.ttl"
    shapes_path = repo_root / "vocab" / "shapes" / "dec-shapes.ttl"

    onto_g = Graph()
    onto_g.parse(str(onto_path), format="turtle")

    shapes_g = Graph()
    shapes_g.parse(str(shapes_path), format="turtle")

    # Validate using pySHACL.
    conforms, report_graph, report_text = validate(
        g, shapesgraph=shapes_g, ontology=onto_g,
        inference="rdfs", advanced=True
    )
    assert conforms, f"Graph does not conform to dec-shapes:\n{report_text}"


def test_record_raises_if_options_less_than_2():
    """Negative test: a decision must have at least 2 options."""
    g = Graph()
    b = _rec(g).band(1)
    with pytest.raises(ValueError, match="at least 2 options"):
        b.record("kind", ["A"], "A", "why")


def test_record_raises_if_chosen_not_in_options():
    """Negative test: chosen must be in the options."""
    g = Graph()
    b = _rec(g).band(1)
    with pytest.raises(ValueError, match="not in options"):
        b.record("kind", ["A", "B"], "C", "why")
