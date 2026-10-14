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
    # proposer that names the scheme-bound field, grounds — on a field that declares no role.
    # (On the row-key field itself it cannot: R310, `test_a_proposer_cannot_name_a_role_field`.)
    names_row_key = FakeGroundingProposer(GroundingProposal(
        LINE_ITEM.iri, str(EX.anchor), 0.9, "a line item", "urn:iladub:suggester/fake"))
    status, _ = _ground(SurfaceConcept("Products", "Products", "p0#mtable2-rhl5"),
                        proposer=names_row_key, contract=CONTROL_CONTRACT)
    assert status == "grounded"

    status, g = _ground(shared, proposer=names_row_key, contract=CONTROL_CONTRACT)
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


UNSHAPED = ContractField(str(EX["f-unshaped"]), str(EX.unshaped), None, ROLE_COLUMN_KEY)
UNSHAPED_CONTRACT = Contract(str(EX.Observation), (LINE_ITEM, UNSHAPED, AMOUNT))


def test_field_identity_is_not_an_oracle_for_a_role_field():
    """[[R311]], ruled 2026-10-14: a role field declares an oracle — a scheme or a value
    constraint. Field identity is not one, because the role reaches the field for every key of
    that role, the empty key included. Before the ruling this test pinned the empty key GROUNDING
    here, with an empty literal the source did not print. A caller that skips `ground_document`'s
    contract check still gets the quarantine: `_grounds_to` has no field-identity path for a
    role-picked field."""
    for value in ("", "2023", "n/m"):
        status, g = _ground(SurfaceConcept("", value, "p0#mtable2-ch7", role=ROLE_COLUMN_KEY),
                            contract=UNSHAPED_CONTRACT)
        assert status == "proposed", value
        _quarantined_under(g, ground._DECLARED_ROLE_RULE)


def test_ground_document_refuses_a_role_field_with_no_oracle():
    """[[R311]]: the contract is refused where the contract and its shapes first meet, before
    any record is read, and the refusal names the field."""
    import pytest
    from iladub.feed import ground_document
    with pytest.raises(ValueError) as refused:
        ground_document(_statement_under_a_caption(), UNSHAPED_CONTRACT, _Raises(), _terms(),
                        _shapes(), Graph())
    assert str(EX["f-unshaped"]) in str(refused.value)
    # the two other role fields carry an oracle each, and are not named
    assert str(EX["f-line-item"]) not in str(refused.value)
    assert str(EX["f-amount"]) not in str(refused.value)


# --- a role field is not filled by a section-marker rider (final review I-2) ---------------

RIDER_TEXT = "Total net sales"                  # a prefLabel of the line-item scheme
# The rider's proposer abstains. Under `ROLE_CONTRACT` it is not asked at all: the only field
# whose scheme admits the rider declares a role, so the pre-filter finds nothing to propose
# ([[R310]]). Under `CONTROL_CONTRACT` it is asked about the row keys, which have no field of
# their role there. A proposer that NAMES the row-key field: the R310 tests at the end.
ABSTAINS = FakeGroundingProposer(GroundingProposal(
    None, str(EX.anchor), 0.1, "n/a", "urn:iladub:suggester/fake"))
ROLE_CONTRACT = Contract(str(EX.Observation), (LINE_ITEM, PERIOD, AMOUNT))
# The control: the same three fields, the scheme-bound one declaring NO role.
BARE_LINE_ITEM = ContractField(LINE_ITEM.iri, LINE_ITEM.fills_property, LINE_ITEM.scheme)
CONTROL_CONTRACT = Contract(str(EX.Observation), (BARE_LINE_ITEM, PERIOD, AMOUNT))


def _statement_under_a_caption():
    """A 2x2 matrix, rows "Net sales" and "Products", columns "2023" and "2022", under one
    `tab:SectionCaption` reading "Total net sales". The feed carries the caption onto every cell
    record as a role-less section marker (plan D2)."""
    from tests.test_feed_matrix_cell import M0, TAB, _matrix
    g = _matrix(Graph(), M0, 0, [("2023",), ("2022",)],
                [("Net sales", {0: "100", 1: "90"}), ("Products", {0: "40", 1: "35"})])
    cap = URIRef(f"{M0}-cap0")
    g.add((M0, TAB.hasCaption, cap))
    g.add((cap, RDF.type, TAB.RegionCaption))
    g.add((cap, RDF.type, TAB.SectionCaption))
    g.add((cap, TAB.captionText, Literal(RIDER_TEXT)))
    g.add((cap, TAB.captionRow, Literal(0)))
    return g


def _ground_statement(contract, monkeypatch):
    """`ground_document` over the statement, through the membrane, with every `marker_field`
    call for a section marker recorded as `(concept, field it returned)`."""
    from iladub.feed import ground_document
    asked = []
    real = ground.marker_field

    def _spy(concept, contract_, terms):
        field = real(concept, contract_, terms)
        if concept.is_section_marker:
            asked.append((concept, field))
        return field
    monkeypatch.setattr(ground, "marker_field", _spy)
    g = Graph()
    result = ground_document(_statement_under_a_caption(), contract, ABSTAINS, _terms(),
                             _shapes(), g, validate_shapes=True)
    return result, g, asked


def _line_items(g):
    out = {}
    for s, o in g.subject_objects(EX.lineItem):
        out.setdefault(str(s), []).append(str(o))
    return out


def test_a_section_marker_rider_does_not_fill_the_row_key_field(monkeypatch):
    from iladub.feed import table_records
    # THE SETUP REACHES `marker_field`, measured rather than assumed: every record carries the
    # rider as a role-less section marker, no field is NAMED "Total net sales", and the scheme
    # of the row-key field carries it.
    recs = table_records(_statement_under_a_caption(), per_cell=True)
    assert len(recs) == 4
    for r in recs:
        (rider,) = [c for c in r.concepts if c.is_section_marker]
        assert (rider.text, rider.value, rider.role) == (RIDER_TEXT, RIDER_TEXT, None)
        assert ground.exact_field(rider, ROLE_CONTRACT) is None
        assert [c.role for c in r.concepts if c is not rider] == [
            ROLE_ROW_KEY, ROLE_COLUMN_KEY, ROLE_CELL_VALUE]
    assert ground.scheme_member(RIDER_TEXT, LINE_ITEM.scheme, _terms()) is not None

    result, g, asked = _ground_statement(ROLE_CONTRACT, monkeypatch)
    # `marker_field` WAS asked about the rider, once per record, and offered no field
    assert [(c.value, f) for c, f in asked] == [(RIDER_TEXT, None)] * 4
    # each record: row key, column key and cell grounded; the rider quarantined
    assert (result.records, result.grounded, result.proposed) == (4, 12, 4)
    riders = [c for c in g.subjects(RDF.type, ILA.CandidateConcept)
              if g.value(c, ILA.surfaceText) == Literal(RIDER_TEXT)]
    assert len(riders) == 4
    for cand in riders:
        assert g.value(cand, ILA.status) == ILA.proposed
        # no proposer was asked: the only admitting field declares a role ([[R310]])
        assert g.value(cand, ILA.suggestedBy) == URIRef(ground._NO_ADMISSIBLE_FIELD_RULE)
        assert list(g.subjects(ILA.reviews, cand)) == []        # no decision reviews it
    # no decision was taken on the rider: every promotion's rule is the declared-role rule
    assert {g.value(pd, DEC.decidedBy) for pd in _decisions(g)} == {
        URIRef(ground._DECLARED_ROLE_RULE)}
    assert len(_decisions(g)) == 12
    # ONE line item per subject, and it is the row's own
    items = _line_items(g)
    assert len(items) == 4
    assert sorted(map(tuple, items.values())) == [("Net sales",)] * 2 + [("Products",)] * 2


def test_the_same_rider_still_grounds_on_a_scheme_field_that_declares_no_role(monkeypatch):
    """The positive control. The contract is the one above with the role taken off the
    scheme-bound field: `marker_field` offers it, and the rider grounds as it always did."""
    result, g, asked = _ground_statement(CONTROL_CONTRACT, monkeypatch)
    assert [(c.value, f) for c, f in asked] == [(RIDER_TEXT, BARE_LINE_ITEM)] * 4
    items = _line_items(g)
    assert len(items) == 4
    assert all(v == [RIDER_TEXT] for v in items.values())
    by_rule = {}
    for pd in _decisions(g):
        rule = str(g.value(pd, DEC.decidedBy))
        by_rule[rule] = by_rule.get(rule, 0) + 1
    assert by_rule == {ground._UNIQUE_ADMITTING_FIELD_RULE: 4, ground._DECLARED_ROLE_RULE: 8}
    # the row keys have no field of their role here, are not markers, and the proposer abstains
    assert (result.records, result.grounded, result.proposed) == (4, 12, 4)


# --- [[R310]]: a role field is filled only by a concept read in that role, at every door ----
#
# Ruled by the maintainer 2026-10-14. `marker_field` was the first door closed (above); these
# are the other three: `exact_field`, the proposer's answer, and the pre-filter that decides
# whether a proposer is asked at all.

NAMES_ROW_KEY = FakeGroundingProposer(GroundingProposal(
    LINE_ITEM.iri, str(EX.anchor), 0.9, "a line item", "urn:iladub:suggester/fake"))


def test_exact_field_does_not_name_a_role_field_for_a_concept_of_another_role():
    """A role-less concept whose TEXT normalises to the row-key field's name ("Line item" →
    `lineItem`): `exact_field` would take the field by name."""
    named = SurfaceConcept("Line item", "Net sales", "p0#cap1")
    assert ground.exact_field(named, ROLE_CONTRACT) is None
    # ... and a concept read in a different role does not take it either
    assert ground.exact_field(SurfaceConcept("Line item", "2023", "r", role=ROLE_COLUMN_KEY),
                              Contract(str(EX.Observation), (LINE_ITEM, AMOUNT))) is None
    # the role-less field of the same name is still found: the rule reads the role, not the name
    assert ground.exact_field(named, CONTROL_CONTRACT) == BARE_LINE_ITEM
    status, g = _ground(named, contract=ROLE_CONTRACT)
    assert status == "proposed"
    assert (OBS, EX.lineItem, None) not in g


def test_a_role_field_is_not_admissible_to_a_concept_of_another_role():
    """The pre-filter. "Products" is in the row-key field's scheme, and no other field of
    `ROLE_CONTRACT` admits it: offered the role field, the pre-filter would ask a proposer whose
    answer could not be admitted ("no oracle, no worker")."""
    products = SurfaceConcept("Products", "Products", "p0#mtable2-rhl5")
    assert ground._admissible_fields(products, ROLE_CONTRACT, _terms(), _shapes(), OBS) == []
    assert ground._admissible_fields(products, CONTROL_CONTRACT, _terms(), _shapes(), OBS) == [
        BARE_LINE_ITEM]
    # so a proposer that raises is never asked
    status, g = _ground(products, proposer=_Raises(), contract=ROLE_CONTRACT)
    assert status == "proposed"
    _quarantined_under(g, ground._NO_ADMISSIBLE_FIELD_RULE)


def test_a_proposer_cannot_name_a_role_field():
    """The proposer door. The ask is reached through a role-less field whose scheme admits the
    value too, so the pre-filter does not skip it, and the proposer names the ROLE field."""
    bare = ContractField(str(EX["f-bare"]), str(EX.bare), LINE_ITEM.scheme)
    contract = Contract(str(EX.Observation), (LINE_ITEM, PERIOD, AMOUNT, bare))
    products = SurfaceConcept("Products", "Products", "p0#mtable2-rhl5")
    assert ground._admissible_fields(products, contract, _terms(), _shapes(), OBS) == [bare]
    status, g = _ground(products, proposer=NAMES_ROW_KEY, contract=contract)
    assert status == "proposed"
    assert _decisions(g) == []
    assert (OBS, EX.lineItem, None) not in g
    cand = _one_candidate(g)                    # the proposer WAS asked, and its answer refused
    assert g.value(cand, ILA.suggestedBy) == URIRef("urn:iladub:suggester/fake")
    # a concept read in ANOTHER role, falling through for want of a field of its own, cannot
    # take the row-key field from a proposer either
    col = Contract(str(EX.Observation), (LINE_ITEM, AMOUNT, bare))
    status, g = _ground(SurfaceConcept("Products", "Products", "r", role=ROLE_COLUMN_KEY),
                        proposer=NAMES_ROW_KEY, contract=col)
    assert status == "proposed"
    assert (OBS, EX.lineItem, None) not in g


def test_the_rider_does_not_fill_the_row_key_field_under_a_naming_proposer(monkeypatch):
    """The R310 setup, under the proposer the earlier test could only abstain with. The rider's
    value is in the row-key scheme; nothing but the role keeps it out."""
    from iladub.feed import ground_document
    g = Graph()
    result = ground_document(_statement_under_a_caption(), ROLE_CONTRACT, NAMES_ROW_KEY,
                             _terms(), _shapes(), g, validate_shapes=True)
    assert (result.records, result.grounded, result.proposed) == (4, 12, 4)
    items = _line_items(g)
    assert sorted(map(tuple, items.values())) == [("Net sales",)] * 2 + [("Products",)] * 2
    assert {g.value(pd, DEC.decidedBy) for pd in _decisions(g)} == {
        URIRef(ground._DECLARED_ROLE_RULE)}
