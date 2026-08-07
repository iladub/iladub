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


# ---------------------------------------------------------------- integration

import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")
needs_apple = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus doc not fetched")


@needs_apple
def test_every_band_carries_a_chain():
    """No region may end without a record of how it got there (spec §6).

    Task 1's interface differs from the original brief: band/page containers are
    dec:Process (not dec:DecisionHolon), and a judgement links to its band via
    dec:withinProcess (not dec:partOf). Band containers are found by their
    RDF.type, DEC.Process; every one of them must have at least one judgement
    decision hanging off it via dec:withinProcess.
    """
    from iladub.etkl import compile_tables
    rep = compile_tables(APPLE, page_number=0)
    g = rep.graph
    bands = list(g.subjects(RDF.type, DEC.Process))
    bands = [b for b in bands if str(b).endswith("-reading") and "region" in str(b)]
    assert bands, "no band processes recorded at all"
    for b in bands:
        judgements = list(g.subjects(DEC.withinProcess, b))
        assert judgements, f"band {b} has no judgement decisions"


@needs_apple
def test_the_kind_rejection_is_recorded_for_band_3():
    """Spec §5's honest limit, made concrete: band 3 rejected RECORD_TABLE because the
    caption line was read as a header row — and nothing else was ever a candidate."""
    from iladub.etkl import compile_tables
    g = compile_tables(APPLE, page_number=0).graph
    rejections = [str(o) for _, _, o in g.triples((None, DEC.rejectedBecause, None))]
    assert any("1 words" in r for r in rejections), \
        f"band 3's kind rejection is not in the record; got {rejections[:5]}"


@needs_apple
def test_band_4_records_transposed_before_coherence():
    """THE R55 QUESTION. The register claimed coherence failed 'solely' because of
    parenthesized negatives; the truth is looks_transposed fired FIRST and the coherence
    oracle was only then consulted. dec:order must make that readable."""
    from iladub.etkl import compile_tables
    g = compile_tables(APPLE, page_number=0).graph
    orders = {}
    for d in g.subjects(RDF.type, DEC.DecisionHolon):
        if "region4-d" not in str(d):
            continue
        label = str(next(g.objects(d, RDFS.label)))
        orders[label] = int(next(g.objects(d, DEC.order)))
    assert "transposed" in orders, f"no transposed judgement recorded; got {sorted(orders)}"
    if "transpose_coherent" in orders:
        assert orders["transposed"] < orders["transpose_coherent"]


@needs_apple
def test_rationale_is_not_a_restatement_of_chosen():
    """Fix round 1: transpose_coherent / row_grouped / matrix_candidate / hierarchical /
    region_tiles must each carry a rationale distinct from dec:chosen — a diagnostic
    sentence answering 'why', not a bare restatement of the enum value ('because
    incoherent'). transposed already set this standard (chosen='transposed',
    rationale='looks transposed'); this guards the other five against regressing to a
    restated label, which is truthful but empty."""
    from iladub.etkl import compile_tables
    g = compile_tables(APPLE, page_number=0).graph
    diagnostic_labels = {"transpose_coherent", "row_grouped", "matrix_candidate",
                          "hierarchical", "region_tiles"}
    found = 0
    for d in g.subjects(RDF.type, DEC.DecisionHolon):
        label = str(next(g.objects(d, RDFS.label), ""))
        if label not in diagnostic_labels:
            continue
        rationale = str(next(g.objects(d, DEC.rationale)))
        chosen = next(g.objects(d, DEC.chosen))
        chosen_label = str(next(g.objects(chosen, RDFS.label)))
        assert rationale != chosen_label, \
            f"{label} rationale '{rationale}' is a bare restatement of chosen '{chosen_label}'"
        found += 1
    assert found, ("no transpose_coherent/row_grouped/matrix_candidate/hierarchical/"
                   "region_tiles judgement was recorded at all")


@needs_apple
def test_region_tiles_rationale_names_the_real_unit():
    """Fix round 2: `n` is an EntryCell count (asserted += 1) on the
    assert_record_region / assert_transposed_region / assert_row_hier_region /
    assert_matrix_region paths, but a body-TOKEN count (asserted += len(cell.words),
    holon.py:482, docstring holon.py:382) on the plain-hierarchical assert_hier_region
    path — a cell with 2 words contributes 2 there, not 1. A rationale that calls that
    "entries" overstates the count. This asserts BOTH units are actually observed on the
    real corpus doc, so a regression to one generic word for both cannot pass silently.

    A band is identified as the assert_hier_region path when it carries a "hierarchical"
    judgement chosen "hierarchical" (UNSUPPORTED_TABLE + not-matrix + classify_hierarchical
    succeeded) alongside a region_tiles judgement — the only region_tiles call in that
    branch of compile_tables is assert_hier_region's. A band is identified as an
    entry-counting path when it carries region_tiles alongside either kind="RECORD_TABLE"
    (assert_transposed_region / assert_row_hier_region / assert_record_region, all
    "asserted += 1") or matrix_candidate="matrix" (assert_matrix_region, also
    "asserted += 1")."""
    from iladub.etkl import compile_tables
    g = compile_tables(APPLE, page_number=0).graph
    by_band: dict = {}
    for d in g.subjects(RDF.type, DEC.DecisionHolon):
        band = str(next(g.objects(d, DEC.withinProcess)))
        label = str(next(g.objects(d, RDFS.label), ""))
        chosen = next(g.objects(d, DEC.chosen))
        chosen_label = str(next(g.objects(chosen, RDFS.label)))
        rationale = str(next(g.objects(d, DEC.rationale), ""))
        by_band.setdefault(band, {})[label] = (chosen_label, rationale)

    saw_body_tokens = saw_entries = False
    for judgements in by_band.values():
        if "region_tiles" not in judgements:
            continue
        _, tiles_rationale = judgements["region_tiles"]
        hier_chosen = judgements.get("hierarchical", (None, None))[0]
        kind_chosen = judgements.get("kind", (None, None))[0]
        matrix_chosen = judgements.get("matrix_candidate", (None, None))[0]
        if hier_chosen == "hierarchical":
            assert "body tokens" in tiles_rationale, \
                f"assert_hier_region path rationale should name body tokens, got {tiles_rationale!r}"
            saw_body_tokens = True
        elif kind_chosen == "RECORD_TABLE" or matrix_chosen == "matrix":
            assert "entries" in tiles_rationale, \
                f"entry-counting path rationale should name entries, got {tiles_rationale!r}"
            saw_entries = True

    assert saw_body_tokens, \
        "the apple corpus doc's page 0 does not exercise the assert_hier_region " \
        "(body-token) region_tiles path — cannot assert the unit fix on this fixture"
    assert saw_entries, \
        "the apple corpus doc's page 0 does not exercise an entry-counting " \
        "region_tiles path — cannot assert the unit fix on this fixture"


@needs_apple
def test_recording_does_not_change_the_verdicts():
    """This slice records; it does not decide."""
    from iladub.etkl import compile_tables
    rep = compile_tables(APPLE, page_number=0)
    verdicts = [(r.kind.name, r.verdict, r.reason, r.cells) for r in rep.regions]
    assert abs(rep.score - 0.1170) < 0.0001, f"score moved: {rep.score}"
    assert sum(1 for v in verdicts if v[1] == "asserted") == 1
