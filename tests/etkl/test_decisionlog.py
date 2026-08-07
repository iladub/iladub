"""The reading decision record (spec 2026-08-07-reading-decision-record-design.md).

Every judgement on the band-to-verdict path becomes a dec:DecisionHolon, so the reading is
queryable rather than lost. Uses only the owned dec: vocabulary — the differential half
(optionSpace/chosen/rejectedBecause) which had no producer before this loop."""
from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS, PROV
import pytest

from iladub.validate import validate

DEC = Namespace("https://w3id.org/iladub/dec#")
DOC = URIRef("urn:test:doc")

# Path to vocab files.
REPO_ROOT = Path(__file__).parent.parent.parent
ONTO_PATH = REPO_ROOT / "vocab" / "ontology" / "dec.ttl"
SHAPES_PATH = REPO_ROOT / "vocab" / "shapes" / "dec-shapes.ttl"


def _rec(g, agent=None):
    from iladub.etkl.decisionlog import ReadingRecorder
    return ReadingRecorder(g, DOC, 0, agent=agent)


def _validate_graph(g: Graph):
    """Validate a data graph against dec-shapes using the dec ontology.

    Returns a ValidationResult with conforms, report_text, and report_graph.
    Raises AssertionError if validation fails, with the report text included.
    """
    onto_g = Graph()
    onto_g.parse(str(ONTO_PATH), format="turtle")

    shapes_g = Graph()
    shapes_g.parse(str(SHAPES_PATH), format="turtle")

    result = validate(g, shapes_g, onto_g)
    assert result.conforms, f"Graph does not conform to dec-shapes:\n{result.report_text}"
    return result


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
    """Validate that all emitted dec:DecisionHolon nodes conform to dec:DecisionHolonShape.

    This is the positive control: a properly-formed graph must conform.
    """
    g = Graph()
    r = _rec(g)
    # Build a representative graph with multiple bands and judgements.
    b3 = r.band(3)
    d1 = b3.record("kind", ["RECORD_TABLE", "UNSUPPORTED_TABLE"], "RECORD_TABLE", "choice 1")
    d2 = b3.record("transposed", ["A", "B"], "B", "choice 2",
                   rejected={"A": "reason A"})
    b5 = r.band(5)
    d3 = b5.record("kind", ["X", "Y"], "Y", "choice 3")

    # Validate using the validation helper.
    _validate_graph(g)


def test_malformed_decision_holon_fails_validation():
    """Negative control: a deliberately malformed dec:DecisionHolon must fail validation.

    This verifies the SHACL validator is actually live and can catch violations.
    A test that always passes is not testing anything.
    """
    from rdflib import Literal
    g = Graph()

    # Create a deliberately malformed DecisionHolon.
    bad_decision = URIRef("urn:test:bad-decision")
    g.add((bad_decision, RDF.type, DEC.DecisionHolon))
    g.add((bad_decision, RDFS.label, Literal("broken")))
    g.add((bad_decision, DEC.rationale, Literal("no agent, no options, no chosen")))
    # Intentionally missing:
    # - dec:decidedBy (required minCount 1)
    # - dec:optionSpace (required minCount 2)
    # - dec:chosen (required minCount 1, maxCount 1)

    # Load ontology and shapes.
    onto_g = Graph()
    onto_g.parse(str(ONTO_PATH), format="turtle")
    shapes_g = Graph()
    shapes_g.parse(str(SHAPES_PATH), format="turtle")

    result = validate(g, shapes_g, onto_g)

    # This must NOT conform.
    assert not result.conforms, "A broken decision should fail validation"

    # The report must mention at least one violation.
    assert "violation" in result.report_text.lower() or "conforms: False" in result.report_text, \
        f"Report should mention violations. Got:\n{result.report_text}"


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
