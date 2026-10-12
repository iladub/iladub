"""Grounding by declared role, and the refusal of a shared row label by rule.

Spec `docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md` §§ 3.5, 9.2.
A concept read in a structural role takes the contract field that DECLARES that role
(`ground._DECLARED_ROLE_RULE`), and is then disposed by `_grounds_to` exactly as an exact match
is: the role picks the field, it never admits the value. A row label several rows of one table
share carries `SHARED_ROW_KEY` and is refused by `ground._SHARED_ROW_LABEL_RULE` before any
field is looked for, because the scheme that would admit it is the defect.

Contract, terms and shapes are built here: no corpus document exercises these branches.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS

from iladub import ground
from iladub.feed import _validate_grounding
from iladub.ground import (ROLE_CELL_VALUE, ROLE_COLUMN_KEY, ROLE_ROW_KEY, SHARED_ROW_KEY,
                           Contract, ContractField, SurfaceConcept, ground_concept)
from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

EX = Namespace("https://example.org/fieldrole#")
ILA = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
SH = Namespace("http://www.w3.org/ns/shacl#")
OBS = URIRef("urn:iladub:record:p0-3-1")

LINE_ITEM = ContractField(str(EX["f-line-item"]), str(EX.lineItem), str(EX["scheme-line-item"]),
                          ROLE_ROW_KEY)
PERIOD = ContractField(str(EX["f-period"]), str(EX.period), None, ROLE_COLUMN_KEY)
AMOUNT = ContractField(str(EX["f-amount"]), str(EX.amount), None, ROLE_CELL_VALUE)
# A role-less field whose NAME is a line item's label: what `exact_field` would pick for the
# row key "Net sales" if the role did not win.
NET_SALES = ContractField(str(EX["f-net-sales"]), str(EX.netSales), None)
CONTRACT = Contract(str(EX.Observation), (LINE_ITEM, PERIOD, AMOUNT, NET_SALES))


class _Raises:
    """A proposer that must not be asked."""

    def propose_grounding(self, concept, fields, page_context=None):
        raise AssertionError(f"the proposer was asked about {concept!r}")


def _terms():
    t = Graph()
    for k, label in enumerate(["Net sales", "Total net sales", "Products"]):
        c = EX[f"li{k}"]
        t.add((c, RDF.type, SKOS.Concept))
        t.add((c, SKOS.inScheme, EX["scheme-line-item"]))
        t.add((c, SKOS.prefLabel, Literal(label)))
    return t


def _shapes():
    """`period` admits a printed fiscal-year label, `amount` a printed numeral. The patterns are
    the contract's (they live in its SHACL shape), not the grounding code's."""
    s = Graph()
    for prop, pattern in ((EX.period, r"^\d{4}$"), (EX.amount, r"^\(?[\d,]+\)?$")):
        ps = BNode()
        s.add((EX.ObservationShape, RDF.type, SH.NodeShape))
        s.add((EX.ObservationShape, SH.property, ps))
        s.add((ps, SH.path, prop))
        s.add((ps, SH.pattern, Literal(pattern)))
    return s


def _ground(concept, proposer=None, contract=CONTRACT, g=None):
    g = Graph() if g is None else g
    status = ground_concept(concept, contract, OBS, proposer or _Raises(), _terms(), _shapes(), g)
    return status, g


def _decisions(g):
    return list(g.subjects(RDF.type, ILA.PromotionDecision))


def _one_candidate(g):
    cands = list(g.subjects(RDF.type, ILA.CandidateConcept))
    assert len(cands) == 1, cands
    return cands[0]


def _quarantined_under(g, rule):
    """One candidate, proposed, suggested by `rule`, and nothing promoted."""
    cand = _one_candidate(g)
    assert g.value(cand, ILA.status) == ILA.proposed
    assert g.value(cand, ILA.suggestedBy) == URIRef(rule)
    assert _decisions(g) == []
    assert list(g.subjects(RDF.type, ILA.GroundedNode)) == []
    assert (OBS, None, None) not in g
    return cand


ROW = SurfaceConcept("Net sales", "Net sales", "p0#mtable2-rhl1", role=ROLE_ROW_KEY)
COL = SurfaceConcept("2023", "2023", "p0#mtable2-chl4", role=ROLE_COLUMN_KEY)
CELL = SurfaceConcept("", "383,285", "p0-305-143", role=ROLE_CELL_VALUE)


# --- the row key: the role picks the field, scheme membership admits the value -----------

def test_a_row_key_grounds_to_its_scheme_concept():
    status, g = _ground(SurfaceConcept("Total net sales", "Total net sales", "p0#mtable2-rhl3",
                                       role=ROLE_ROW_KEY))
    assert status == "grounded"
    gn = next(g.subjects(RDF.type, ILA.GroundedNode))
    assert g.value(gn, ILA.groundsTo) == EX.li1
    assert (OBS, EX.lineItem, Literal("Total net sales")) in g
    pd = g.value(gn, ILA.wasPromotedBy)
    assert g.value(pd, DEC.decidedBy) == URIRef(ground._DECLARED_ROLE_RULE)
    rationale = str(g.value(pd, DEC.rationale))
    assert ROLE_ROW_KEY in rationale and "no proposer" in rationale


def test_a_row_key_outside_the_scheme_is_quarantined():
    status, g = _ground(SurfaceConcept("Goodwill", "Goodwill", "p0#mtable2-rhl9",
                                       role=ROLE_ROW_KEY))
    assert status == "proposed"
    _quarantined_under(g, ground._DECLARED_ROLE_RULE)


# --- the column key: the role picks the field, the SHACL pattern admits the value --------

def test_a_column_key_grounds_when_the_pattern_admits_it():
    status, g = _ground(COL)
    assert status == "grounded"
    gn = next(g.subjects(RDF.type, ILA.GroundedNode))
    assert g.value(gn, ILA.groundsTo) == EX.period
    assert (OBS, EX.period, Literal("2023")) in g
    pd = g.value(gn, ILA.wasPromotedBy)
    assert g.value(pd, DEC.decidedBy) == URIRef(ground._DECLARED_ROLE_RULE)
    # The value crossed the SHACL membrane, and the record says so on both sides: the rationale
    # does not carry the "weaker than scheme-identity" rider a PROPOSED field earns, and the
    # option not taken names the membrane as what would have refused.
    assert "weaker than scheme-identity" not in str(g.value(pd, DEC.rationale))
    rejected = [str(o) for o in g.objects(None, DEC.rejectedBecause)]
    assert len(rejected) == 1 and "SHACL value constraint" in rejected[0]


def test_a_column_key_is_quarantined_when_it_does_not():
    status, g = _ground(SurfaceConcept("Change", "Change", "p0#mtable2-chl6",
                                       role=ROLE_COLUMN_KEY))
    assert status == "proposed"
    _quarantined_under(g, ground._DECLARED_ROLE_RULE)


# --- the cell: no label at all, and the role is the only thing that can place it ---------

def test_a_cell_value_grounds_under_the_value_field_with_an_empty_text():
    assert CELL.text == ""
    status, g = _ground(CELL)
    assert status == "grounded"
    assert (OBS, EX.amount, Literal("383,285")) in g
    cand = _one_candidate(g)
    assert g.value(cand, RDFS_LABEL) == Literal("")
    assert g.value(cand, ILA.surfaceText) == Literal("383,285")
    # the role picks the field; the pattern still disposes the value
    status, g = _ground(SurfaceConcept("", "n/m", "p0-305-144", role=ROLE_CELL_VALUE))
    assert status == "proposed"
    _quarantined_under(g, ground._DECLARED_ROLE_RULE)


RDFS_LABEL = URIRef("http://www.w3.org/2000/01/rdf-schema#label")


# --- precedence ---------------------------------------------------------------------------

def test_the_role_wins_over_an_exact_name_match():
    """"Net sales" normalises to the role-less field `netSales`. Without the role branch
    `exact_field` takes it and grounds by field identity on the wrong property."""
    assert ground.exact_field(ROW, CONTRACT) == NET_SALES
    status, g = _ground(ROW)
    assert status == "grounded"
    assert (OBS, EX.lineItem, Literal("Net sales")) in g
    assert (OBS, EX.netSales, None) not in g
    gn = next(g.subjects(RDF.type, ILA.GroundedNode))
    assert g.value(gn, ILA.groundsTo) == EX.li0


def test_a_role_with_no_field_of_that_role_falls_through():
    """No field declares `ColumnKey`: the concept takes the path a role-less one takes. With the
    role-less field `period` in the contract the proposer is asked (the pattern admits "2023",
    so the pre-filter does not skip it), and its proposal is what the record carries."""
    bare_period = ContractField(str(EX["f-period"]), str(EX.period), None)
    contract = Contract(str(EX.Observation), (LINE_ITEM, bare_period, AMOUNT))
    proposer = FakeGroundingProposer(GroundingProposal(
        bare_period.iri, str(EX.anchor), 0.6, "looks like a period", "urn:iladub:suggester/fake"))
    status, g = _ground(COL, proposer=proposer, contract=contract)
    roleless = SurfaceConcept(COL.text, COL.value, COL.region)
    status0, g0 = _ground(roleless, proposer=proposer, contract=contract)
    assert status == status0 == "grounded"
    for graph in (g, g0):
        pd = _decisions(graph)[0]
        assert graph.value(pd, DEC.decidedBy) == URIRef("urn:iladub:suggester/fake")
        assert "weaker than scheme-identity" in str(graph.value(pd, DEC.rationale))
    assert len(g) == len(g0)


# --- spec § 9.2: the shared row label ------------------------------------------------------

def test_a_shared_row_key_is_refused_whatever_the_proposer_says():
    """The label IS in the scheme, and a proposer naming the row-key field would get it grounded
    by scheme membership (measured: S2). The refusal is the rule's, taken before any field is
    looked for, so nothing a proposer says can reach it."""
    shared = SurfaceConcept("Products", "Products", "p0#mtable2-rhl5", role=SHARED_ROW_KEY)
    assert ground.scheme_member("Products", LINE_ITEM.scheme, _terms()) is not None
    # The control, and it is what the rule prevents: the same label with no role, under a
    # proposer that names the row-key field, grounds.
    names_row_key = FakeGroundingProposer(GroundingProposal(
        LINE_ITEM.iri, str(EX.anchor), 0.9, "a line item", "urn:iladub:suggester/fake"))
    status, _ = _ground(SurfaceConcept("Products", "Products", "p0#mtable2-rhl5"),
                        proposer=names_row_key)
    assert status == "grounded"

    status, g = _ground(shared, proposer=names_row_key)
    assert status == "proposed"
    _quarantined_under(g, ground._SHARED_ROW_LABEL_RULE)
    # and the proposer was never asked: one that raises does not raise
    status, g = _ground(shared, proposer=_Raises())
    assert status == "proposed"
    _quarantined_under(g, ground._SHARED_ROW_LABEL_RULE)


def test_a_shared_row_key_does_not_consult_the_admissible_fields(monkeypatch):
    def _never(*a, **k):
        raise AssertionError("_admissible_fields was consulted for a shared row key")
    monkeypatch.setattr(ground, "_admissible_fields", _never)
    shared = SurfaceConcept("Products", "Products", "p0#mtable2-rhl5", role=SHARED_ROW_KEY)
    assert _ground(shared)[0] == "proposed"


# --- the membrane, and the proposer ---------------------------------------------------------

def test_a_role_grounded_graph_conforms_to_the_membrane():
    """One observation: a grounded row key, column key and cell, plus the three quarantines the
    branches produce (a value the oracle refuses, a cell with an empty label, a shared label)."""
    g = Graph()
    statuses = [_ground(c, g=g)[0] for c in (
        ROW, COL, CELL,
        SurfaceConcept("", "n/m", "p0-305-144", role=ROLE_CELL_VALUE),
        SurfaceConcept("Goodwill", "Goodwill", "p0#mtable2-rhl9", role=ROLE_ROW_KEY),
        SurfaceConcept("Products", "Products", "p0#mtable2-rhl5", role=SHARED_ROW_KEY))]
    assert statuses == ["grounded"] * 3 + ["proposed"] * 3
    conforms, report = _validate_grounding(g)
    assert conforms, report
    # what the membrane requires of each promotion, read back rather than trusted
    pds = _decisions(g)
    assert len(pds) == 3
    for pd in pds:
        options = list(g.objects(pd, DEC.optionSpace))
        assert len(options) == 2
        not_taken = [o for o in options if o != g.value(pd, DEC.chosen)]
        assert len(not_taken) == 1 and g.value(not_taken[0], DEC.rejectedBecause) is not None
    # a key's region is `p<page>#<fragment>`: it must name ONE well-formed region IRI and
    # survive a serialisation round trip
    region = URIRef("urn:iladub:region:p0#mtable2-rhl1")
    assert (region, RDF.type, ILA.SourceRegion) in g
    back = Graph().parse(data=g.serialize(format="nt"), format="nt")
    assert (region, RDF.type, ILA.SourceRegion) in back


def test_no_proposer_is_asked_for_a_role_concept():
    """Every outcome of the two branches, under a proposer that raises if asked."""
    for concept, expected in (
            (ROW, "grounded"), (COL, "grounded"), (CELL, "grounded"),
            (SurfaceConcept("Goodwill", "Goodwill", "r", role=ROLE_ROW_KEY), "proposed"),
            (SurfaceConcept("Change", "Change", "r", role=ROLE_COLUMN_KEY), "proposed"),
            (SurfaceConcept("", "n/m", "r", role=ROLE_CELL_VALUE), "proposed"),
            (SurfaceConcept("Products", "Products", "r", role=SHARED_ROW_KEY), "proposed")):
        assert _ground(concept, proposer=_Raises())[0] == expected, concept


# --- a header node with no label cell: a key with EMPTY text and value -------------------

def test_an_empty_key_is_quarantined_by_the_oracle_of_its_field():
    """The feed can mint a key with no text for a header node that has no label cell. The role
    still picks the field; the scheme and the pattern each refuse the empty value."""
    for role in (ROLE_ROW_KEY, ROLE_COLUMN_KEY):
        status, g = _ground(SurfaceConcept("", "", "p0#mtable2-rh7", role=role))
        assert status == "proposed", role
        _quarantined_under(g, ground._DECLARED_ROLE_RULE)


def test_an_empty_key_under_an_unconstrained_role_field_grounds_by_field_identity():
    """MEASURED, NOT ENDORSED. A role field that declares neither a scheme nor a value constraint
    has field identity as its only oracle (`_grounds_to`, as for any exact match), and field
    identity cannot refuse anything — the empty key included: the record asserts the property
    with an empty literal, and the membrane conforms on it. The refusal available today is the
    contract's (declare a scheme or a pattern on a role field), as the test above shows. Pinned
    so that a change to this — a shape that requires a constraint on a role field, or a feed
    that mints no empty key — is a visible diff here rather than a silent one."""
    unshaped = ContractField(str(EX["f-unshaped"]), str(EX.unshaped), None, ROLE_COLUMN_KEY)
    contract = Contract(str(EX.Observation), (LINE_ITEM, unshaped, AMOUNT))
    status, g = _ground(SurfaceConcept("", "", "p0#mtable2-ch7", role=ROLE_COLUMN_KEY),
                        contract=contract)
    assert status == "grounded"
    assert list(g.objects(OBS, EX.unshaped)) == [Literal("")]
    rejected = [str(o) for o in g.objects(None, DEC.rejectedBecause)]
    # The record says what identified the field: the contract's declaration of the role. No
    # label did (the key's label is empty), and the sentence an exact NAME match earns is absent.
    assert len(rejected) == 1
    assert rejected[0] == (
        f"the contract declares {EX.unshaped} as its field of role {ROLE_COLUMN_KEY}, the role "
        f"the concept was read in; no label was matched and no proposer was asked, and the field "
        f"declares neither a scheme nor a value constraint, so field identity is the oracle; "
        f"quarantine is the branch for a field that was proposed rather than declared")
    assert "label exactly identifies" not in rejected[0]
    conforms, report = _validate_grounding(g)
    assert conforms, report
