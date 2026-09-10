"""R207 — a section marker grounds on the UNIQUE contract scheme that carries its value.

`feed._inject_section_captions` puts every peeled caption on every record of its section as
`SurfaceConcept(text, text, region, is_section_marker=True)`: text and value are the same
string, because a caption names no column. `ground_concept` used to reach such a concept only
through `exact_field`, which compares the concept's TEXT to contract FIELD NAMES — `GERALDTON`
is no field — so every marker was quarantined, even the 49 on cbh-stem whose value is a
`skos:prefLabel` of `cbh:scheme-port`, and no cbh record carried a port at all (measured
2026-09-10: 58 of 58 records without `cbh:port` after `ground_document`; the handoff
`docs/superpowers/2026-09-10-r207-marker-grounds-by-scheme-handoff.md` § 2).

The branch this pins is AXIOM (CLAUDE.md § 8): for a marker `exact_field` cannot name, the
contract's scheme-bound fields are asked which of their schemes carries the value as a
prefLabel; exactly ONE admitting field grounds the marker on that field, through the same
`_grounds_to` oracle every scheme value crosses; zero or two abstain. It is the per-VALUE
counterpart of `splitkey`'s arm 2 (the per-NAME unique-admitting-field rule), and it carries
that arm's suggester IRI so a reader of the graph sees one rule, not two.
"""
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS

from iladub.feed import ground_document, _record_uri, table_records
from iladub.ground import (Contract, ContractField, SurfaceConcept, marker_field,
                           _UNIQUE_ADMITTING_FIELD_RULE)
from iladub.propose_ground import FakeGroundingProposer, GroundingProposal
from tests.test_feed_section_keys import _caption, _table

EX = Namespace("https://example.org/r207#")
ILA = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
T = URIRef("urn:doc/p0#table0")
NOTICE = "BERTH MAY BE UNAVAILABLE 2000HRS"

PORT = ContractField(str(EX["f-port"]), str(EX.port), str(EX["scheme-port"]))
COMMODITY = ContractField(str(EX["f-commodity"]), str(EX.commodity), str(EX["scheme-commodity"]))
CLIENT = ContractField(str(EX["f-client"]), str(EX.client), None)
CONTRACT = Contract(str(EX.Record), (PORT, COMMODITY, CLIENT))

ABSTAIN = FakeGroundingProposer(GroundingProposal(
    None, str(EX) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))


def _terms(extra=()):
    """port scheme {GERALDTON, KWINANA}, commodity scheme {Wheat}, plus `extra` (scheme, label)
    pairs — the doctored graph the ambiguity test needs."""
    t = Graph()
    members = [("scheme-port", "GERALDTON"), ("scheme-port", "KWINANA"),
               ("scheme-commodity", "Wheat"), *extra]
    for k, (scheme, label) in enumerate(members):
        c = EX[f"c{k}"]
        t.add((c, RDF.type, SKOS.Concept))
        t.add((c, SKOS.inScheme, EX[scheme]))
        t.add((c, SKOS.prefLabel, Literal(label, lang="en")))
    return t


def _section(*captions, headers=("Client", "Volume")):
    """Two-row section table whose peeled captions are `captions`, in that positional order."""
    g = Graph()
    _table(g, T, 0, list(headers),
           {0: {0: "Brahman", 1: "30000"}, 1: {0: "CBH", 1: "50000"}})
    for k, text in enumerate(captions):
        _caption(g, T, k, text)
    return g


def _ground(doc, terms, validate=True):
    g = Graph()
    res = ground_document(doc, CONTRACT, ABSTAIN, terms, Graph(), g, validate_shapes=validate)
    return res, g


def _candidate(g, value):
    return next(c for c in g.subjects(RDF.type, ILA.CandidateConcept)
                if str(g.value(c, ILA.surfaceText)) == value)


# --- the unit: which field, if any, a marker's value uniquely admits into --------------

def test_marker_field_is_the_unique_scheme_carrying_the_value():
    m = SurfaceConcept("GERALDTON", "GERALDTON", "cap0", is_section_marker=True)
    assert marker_field(m, CONTRACT, _terms()) == PORT


def test_marker_field_abstains_on_zero_and_on_two_admitting_schemes():
    none = SurfaceConcept(NOTICE, NOTICE, "cap1", is_section_marker=True)
    assert marker_field(none, CONTRACT, _terms()) is None
    both = SurfaceConcept("GERALDTON", "GERALDTON", "cap0", is_section_marker=True)
    assert marker_field(both, CONTRACT, _terms(extra=[("scheme-commodity", "GERALDTON")])) is None


# --- the record: what ground_document now writes on a section's rows --------------------

def test_section_key_grounds_on_every_record_and_the_notice_stays_quarantined():
    """Client exact-matches a bare field (2 grounded); Volume names no field (2 proposed); the
    GERALDTON marker grounds on `port` through scheme membership (2 grounded); the notice is a
    marker no scheme carries (2 proposed). The grounded graph crosses the promotion membrane."""
    res, g = _ground(_section("GERALDTON", NOTICE), _terms())
    assert (res.records, res.grounded, res.proposed) == (2, 4, 4), res
    for rec in table_records(_section("GERALDTON", NOTICE)):
        subj = _record_uri(rec.row_id)
        assert (subj, EX.port, Literal("GERALDTON")) in g, rec.row_id
        assert list(g.objects(subj, EX.port)) == [Literal("GERALDTON")]
    assert (None, EX.port, Literal(NOTICE)) not in g
    assert g.value(_candidate(g, NOTICE), ILA.status) == ILA.proposed


def test_the_marker_s_promotion_records_the_membership_rule_and_the_scheme_concept():
    res, g = _ground(_section("GERALDTON"), _terms())
    cand = _candidate(g, "GERALDTON")
    pd = g.value(None, ILA.reviews, cand)
    assert g.value(pd, DEC.decidedBy) == URIRef(_UNIQUE_ADMITTING_FIELD_RULE)
    gn = g.value(pd, DEC.produced)
    assert g.value(gn, ILA.groundsTo) == EX.c0            # the GERALDTON skos:Concept
    assert "unique" in str(g.value(pd, DEC.rationale)).lower()


def test_a_marker_two_schemes_carry_is_quarantined_not_guessed():
    """Ambiguity abstains (§3 — never let a proposition pass as an assertion): with GERALDTON a
    prefLabel in BOTH schemes, no field is unique, so no port and no commodity is written —
    Client grounds (2), Volume and the marker quarantine (2 + 2)."""
    res, g = _ground(_section("GERALDTON"), _terms(extra=[("scheme-commodity", "GERALDTON")]))
    assert (res.grounded, res.proposed) == (2, 4), res
    assert (None, EX.port, None) not in g and (None, EX.commodity, None) not in g
    assert g.value(_candidate(g, "GERALDTON"), ILA.status) == ILA.proposed


def test_a_data_cell_carrying_a_scheme_value_is_not_a_marker_and_stays_quarantined():
    """The branch is scoped to `is_section_marker`. A cell under an undeclared column whose value
    happens to be a port label is a data cell the contract does not name — the proposer's
    question, not the AXIOM's — so it must not ground by value alone."""
    doc = Graph()
    _table(doc, T, 0, ["Client", "Where"],
           {0: {0: "Brahman", 1: "GERALDTON"}, 1: {0: "CBH", 1: "KWINANA"}})
    res, g = _ground(doc, _terms())
    assert (res.grounded, res.proposed) == (2, 2), res
    assert (None, EX.port, None) not in g
