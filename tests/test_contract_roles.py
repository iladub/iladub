"""A contract field's structural role (`etkl:fieldRole`): the vocabulary's shape and the load.

Spec `docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md` §§ 3.1, 3.2,
9.2. The shape is the constraint (closed world, CLAUDE.md § 8); `load_contract` refuses by
running it, so every refusal pinned on the shape below is pinned again on the load.
"""
import os

import pytest
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from iladub import ground
from iladub.ground import ContractField, SurfaceConcept, load_contract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology", "etkl.ttl")
SHAPES = os.path.join(ROOT, "vocab", "shapes", "etkl-shapes.ttl")
CAPACITY = os.path.join(ROOT, "examples", "shipping", "capacity-contract.ttl")
TWO_CELL_VALUES = os.path.join(ROOT, "tests", "etkl-contract-two-cell-values-leak.ttl")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("https://example.org/roles#")

ROLE_SHAPES = [ETKL.ContractRoleShape, ETKL.FieldRoleShape]

_HEAD = """\
@prefix ex:   <https://example.org/roles#> .
@prefix etkl: <https://w3id.org/iladub/etkl#> .
"""

# The spec § 4 shape of a role contract: one field per role. It carries a target shape and a
# knowledge module so it conforms to the WHOLE of etkl-shapes.ttl, not only to the role shapes.
# The target shape is in the same graph because `etkl:RoleFieldOracleShape` reads the contract
# and its value shapes together ([[R311]]): the two scheme-less role fields have their oracle
# there, as the shipped finance contract's have theirs in `statement-shapes.ttl`.
ROLE_CONTRACT = _HEAD + """
@prefix sh:   <http://www.w3.org/ns/shacl#> .

ex:contract a etkl:SemanticDataContract ;
    etkl:targetClass ex:Observation ;
    etkl:hasTargetShape ex:ObservationShape ;
    etkl:requiresKnowledge ex:scheme-line-item ;
    etkl:hasField ex:f-line-item , ex:f-period , ex:f-amount .

ex:f-line-item a etkl:Field ; etkl:fillsProperty ex:lineItem ; etkl:fieldRole etkl:RowKey ;
    etkl:admissibleScheme ex:scheme-line-item .
ex:f-period    a etkl:Field ; etkl:fillsProperty ex:period   ; etkl:fieldRole etkl:ColumnKey .
ex:f-amount    a etkl:Field ; etkl:fillsProperty ex:amount   ; etkl:fieldRole etkl:CellValue .

ex:ObservationShape a sh:NodeShape ;
    sh:targetClass ex:Observation ;
    sh:property [ sh:path ex:period ; sh:pattern "^[0-9]{4}$" ] ;
    sh:property [ sh:path ex:amount ; sh:pattern "^[0-9,]+$" ] .
"""

TWO_ROLES = ROLE_CONTRACT.replace(
    "etkl:fieldRole etkl:ColumnKey", "etkl:fieldRole etkl:ColumnKey , etkl:RowKey")
# `ex:Footnote` is not one of the three individuals. The contract still has its one CellValue
# field, so nothing but the role's VALUE is wrong with it.
UNKNOWN_ROLE = ROLE_CONTRACT.replace(
    "etkl:fieldRole etkl:ColumnKey", "etkl:fieldRole ex:Footnote")
NO_CELL_VALUE = ROLE_CONTRACT.replace(" ; etkl:fieldRole etkl:CellValue", "")
TWO_ROW_KEYS = ROLE_CONTRACT.replace(
    "etkl:fieldRole etkl:ColumnKey", "etkl:fieldRole etkl:RowKey")
# No `a etkl:SemanticDataContract`, no `a etkl:Field`: what `load_contract` reads is the
# `etkl:targetClass` / `etkl:hasField` structure, and the shape must reach it there too.
UNTYPED_TWO_CELL_VALUES = _HEAD + """
ex:contract etkl:targetClass ex:Observation ; etkl:hasField ex:f-a , ex:f-b .
ex:f-a etkl:fillsProperty ex:a ; etkl:fieldRole etkl:CellValue .
ex:f-b etkl:fillsProperty ex:b ; etkl:fieldRole etkl:CellValue .
"""


def _report(data: Graph, use_shapes=None):
    """(conforms, results) against etkl-shapes.ttl, the way `tests/test_vocab_shapes.py`
    validates: etkl.ttl as the ontology graph, RDFS inference, advanced on. `results` is one
    (focus node, message) pair per `sh:ValidationResult`."""
    conforms, report, text = validate(
        data, shacl_graph=Graph().parse(SHAPES, format="turtle"),
        ont_graph=Graph().parse(ONT, format="turtle"),
        inference="rdfs", advanced=True, use_shapes=use_shapes)
    results = sorted(
        (str(report.value(r, SH.focusNode)), str(report.value(r, SH.resultMessage)))
        for r in report.subjects(RDF.type, SH.ValidationResult))
    return conforms, results, text


def _ttl(text: str) -> Graph:
    return Graph().parse(data=text, format="turtle")


def _write(tmp_path, text: str) -> str:
    path = tmp_path / "contract.ttl"
    path.write_text(text, encoding="utf-8")
    return str(path)


# --- the vocabulary ---

def test_the_role_vocabulary_is_declared():
    ont = Graph().parse(ONT, format="turtle")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    assert (ETKL.FieldRole, RDF.type, OWL.Class) in ont
    assert (ETKL.fieldRole, RDF.type, OWL.ObjectProperty) in ont
    assert ont.value(ETKL.fieldRole, RDFS.domain) == ETKL.Field
    assert ont.value(ETKL.fieldRole, RDFS.range) == ETKL.FieldRole
    for individual in (ETKL.RowKey, ETKL.ColumnKey, ETKL.CellValue):
        assert (individual, RDF.type, ETKL.FieldRole) in ont
    for term in (ETKL.FieldRole, ETKL.fieldRole, ETKL.RowKey, ETKL.ColumnKey, ETKL.CellValue):
        assert ont.value(term, RDFS.label) is not None, term
        assert ont.value(term, RDFS.comment) is not None, term


def test_the_role_constants_name_the_three_individuals():
    assert ground.ROLE_ROW_KEY == str(ETKL.RowKey)
    assert ground.ROLE_COLUMN_KEY == str(ETKL.ColumnKey)
    assert ground.ROLE_CELL_VALUE == str(ETKL.CellValue)
    roles = {ground.ROLE_ROW_KEY, ground.ROLE_COLUMN_KEY, ground.ROLE_CELL_VALUE}
    assert len(roles) == 3
    # Spec § 9.2: the shared row key's value is one no contract can declare — not a role
    # individual, and not any term the ontology declares at all.
    assert isinstance(ground.SHARED_ROW_KEY, str)
    assert ground.SHARED_ROW_KEY not in roles
    ont = Graph().parse(ONT, format="turtle")
    assert not list(ont.triples((URIRef(ground.SHARED_ROW_KEY), None, None)))


def test_role_is_a_defaulted_field_that_leaves_value_equality_alone():
    assert ContractField("i", "p", None) == ContractField("i", "p", None, None)
    assert ContractField("i", "p", None).role is None
    assert ContractField("i", "p", None, ground.ROLE_ROW_KEY).role == ground.ROLE_ROW_KEY
    assert SurfaceConcept("t", "v", "r") == SurfaceConcept("t", "v", "r", False, False, None)
    assert SurfaceConcept("t", "v", "r").role is None
    assert SurfaceConcept("t", "v", "r", role=ground.SHARED_ROW_KEY).role == ground.SHARED_ROW_KEY


# --- the shape ---

def test_a_role_contract_conforms():
    conforms, results, text = _report(_ttl(ROLE_CONTRACT))
    assert conforms, text
    assert results == []


def test_two_cell_value_fields_are_refused():
    data = Graph().parse(TWO_CELL_VALUES, format="turtle")
    # Against the whole file: ONE result, on the contract, and it is the CellValue cardinality —
    # so the fixture is refused by the role shape and by nothing else.
    conforms, results, text = _report(data)
    assert not conforms
    assert len(results) == 1, text
    focus, message = results[0]
    assert focus == "https://example.org/roles#two-cell-values-contract"
    assert "exactly one etkl:CellValue field" in message
    # And against the role shapes alone, which is what `load_contract` runs.
    assert not _report(data, use_shapes=ROLE_SHAPES)[0]


def test_a_field_with_two_roles_is_refused():
    conforms, results, text = _report(_ttl(TWO_ROLES))
    assert not conforms
    assert (str(EX["f-period"]), "A contract field carries at most one etkl:fieldRole.") in results, text


def test_an_unknown_role_is_refused():
    conforms, results, text = _report(_ttl(UNKNOWN_ROLE))
    assert not conforms
    assert [focus for focus, _ in results] == [str(EX["f-period"])], text
    assert "etkl:RowKey, etkl:ColumnKey or etkl:CellValue" in results[0][1]


def test_roles_without_a_cell_value_are_refused():
    conforms, results, text = _report(_ttl(NO_CELL_VALUE))
    assert not conforms
    assert [focus for focus, _ in results] == [str(EX.contract)], text
    assert "exactly one etkl:CellValue field" in results[0][1]


def test_two_fields_on_one_key_role_are_refused():
    conforms, results, text = _report(_ttl(TWO_ROW_KEYS))
    assert not conforms
    assert [focus for focus, _ in results] == [str(EX.contract)], text
    assert "at most one etkl:RowKey field" in results[0][1]


def test_a_contract_with_no_role_is_untouched():
    data = Graph().parse(CAPACITY, format="turtle")
    conforms, results, text = _report(data, use_shapes=ROLE_SHAPES)
    assert conforms, text
    contract = load_contract(CAPACITY)
    assert len(contract.fields) == 4
    assert [f.role for f in contract.fields] == [None, None, None, None]
    # What it returned before the role existed: the same four three-argument fields.
    ship = "https://example.org/shipping#"
    assert set(contract.fields) == {
        ContractField(ship + "f-cap-year", ship + "year", None),
        ContractField(ship + "f-cap-period", ship + "elevationPeriod", None),
        ContractField(ship + "f-cap-port", ship + "port", ship + "scheme-port"),
        ContractField(ship + "f-cap-capacity", ship + "capacity", None),
    }
    assert contract.target_class == ship + "ElevationCapacity"


@pytest.mark.parametrize("name", ["capacity-contract", "cbh-contract", "stem-contract"])
def test_the_shipped_shipping_contracts_load_with_no_role(name):
    contract = load_contract(os.path.join(ROOT, "examples", "shipping", f"{name}.ttl"))
    assert contract.fields
    assert all(f.role is None for f in contract.fields)


# --- the load ---

def test_load_contract_reads_the_role(tmp_path):
    contract = load_contract(_write(tmp_path, ROLE_CONTRACT))
    roles = {f.fills_property: f.role for f in contract.fields}
    assert roles == {
        str(EX.lineItem): ground.ROLE_ROW_KEY,
        str(EX.period): ground.ROLE_COLUMN_KEY,
        str(EX.amount): ground.ROLE_CELL_VALUE,
    }
    assert all(isinstance(f.role, str) for f in contract.fields)
    assert all(f.role != ground.SHARED_ROW_KEY for f in contract.fields)


@pytest.mark.parametrize("text", [
    TWO_ROLES, UNKNOWN_ROLE, NO_CELL_VALUE, TWO_ROW_KEYS, UNTYPED_TWO_CELL_VALUES,
], ids=["two-roles", "unknown-role", "no-cell-value", "two-row-keys", "untyped-two-cell-values"])
def test_load_contract_refuses_what_the_shape_refuses(tmp_path, text):
    """Review Focus 3: the load's refusal IS the shape's verdict. Every contract here is first
    shown refused by the role shapes, then shown refused at load, and the load names the path."""
    path = _write(tmp_path, text)
    assert not _report(_ttl(text), use_shapes=ROLE_SHAPES)[0]
    with pytest.raises(ValueError) as refused:
        load_contract(path)
    assert path in str(refused.value)


def test_load_contract_refuses_the_two_cell_value_fixture():
    with pytest.raises(ValueError) as refused:
        load_contract(TWO_CELL_VALUES)
    assert TWO_CELL_VALUES in str(refused.value)
    assert "exactly one etkl:CellValue field" in str(refused.value)


def test_load_contract_cannot_be_handed_the_shared_row_key(tmp_path):
    """Spec § 9.2: no contract can declare the shared row key. A contract that names its IRI as
    a role is refused by the shape's closed list, so `load_contract` never returns it."""
    text = ROLE_CONTRACT.replace(
        "etkl:fieldRole etkl:RowKey", f"etkl:fieldRole <{ground.SHARED_ROW_KEY}>")
    with pytest.raises(ValueError):
        load_contract(_write(tmp_path, text))


# --- [[R311]]: a role field declares an oracle for its value ---------------------------------

NO_ORACLE = os.path.join(ROOT, "tests", "etkl-contract-role-without-oracle-leak.ttl")
FINANCE = os.path.join(ROOT, "examples", "finance")
ORACLE_SHAPE = [ETKL.RoleFieldOracleShape]


def test_the_oracle_parameter_is_declared():
    ont = Graph().parse(ONT, format="turtle")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    assert (ETKL.valueConstraintParameter, RDF.type, OWL.ObjectProperty) in ont
    assert ont.value(ETKL.valueConstraintParameter, RDFS.label) is not None
    assert ont.value(ETKL.valueConstraintParameter, RDFS.comment) is not None


def test_the_shipped_finance_contract_has_an_oracle_on_every_role_field():
    """The worked example that conforms: the finance contract with its own shapes file. Alone,
    its two scheme-less role fields have no oracle in view, and the shape says so: the check is
    over the union, which is why `load_contract` cannot run it."""
    contract = Graph().parse(os.path.join(FINANCE, "statement-contract.ttl"), format="turtle")
    shapes = Graph().parse(os.path.join(FINANCE, "statement-shapes.ttl"), format="turtle")
    conforms, results, text = _report(contract + shapes, use_shapes=ORACLE_SHAPE)
    assert conforms, text
    conforms, results, _ = _report(contract, use_shapes=ORACLE_SHAPE)
    assert not conforms
    assert sorted(focus for focus, _ in results) == [
        "https://example.org/finance#f-period", "https://example.org/finance#f-value"]


def test_a_role_field_with_no_oracle_is_refused():
    """The negative fixture, against the WHOLE file: one result, on the column-key field, and it
    is the oracle shape's — the fixture is refused by that shape and by nothing else."""
    conforms, results, text = _report(Graph().parse(NO_ORACLE, format="turtle"))
    assert not conforms
    assert len(results) == 1, text
    focus, message = results[0]
    assert focus == str(EX["f-period"])
    assert "declares an oracle for its value" in message


def test_require_role_oracles_runs_the_shape(tmp_path):
    """The refusal is the shape's verdict, at the one place that holds both graphs. The fixture
    LOADS — `load_contract` sees no shapes and cannot refuse it — and is refused here."""
    g = Graph().parse(NO_ORACLE, format="turtle")
    with pytest.raises(ValueError) as refused:
        ground.require_role_oracles(load_contract(NO_ORACLE), g)
    assert str(EX["f-period"]) in str(refused.value)
    assert str(EX["f-amount"]) not in str(refused.value)
    ground.require_role_oracles(load_contract(_write(tmp_path, ROLE_CONTRACT)), _ttl(ROLE_CONTRACT))


@pytest.mark.parametrize("param", sorted(ground._value_constraints(), key=str))
def test_each_declared_parameter_is_an_oracle_and_the_code_agrees(param):
    """The list is stated once, on the shape; the grounding code reads it from there. Each
    parameter alone satisfies the shape, and `_has_value_constraint` says the same of it."""
    shapes = Graph()
    ps = URIRef("urn:test:ps")
    shapes.add((ps, SH.path, EX.period))
    shapes.add((ps, param, EX.anything))
    shapes.add((URIRef("urn:test:ps2"), SH.path, EX.amount))
    shapes.add((URIRef("urn:test:ps2"), SH.pattern, EX.anything))
    contract = Graph().parse(data=ROLE_CONTRACT.split("ex:ObservationShape a")[0], format="turtle")
    conforms, _, text = _report(contract + shapes, use_shapes=ORACLE_SHAPE)
    assert conforms, text
    assert ground._has_value_constraint(shapes, ps)


def test_a_cardinality_is_not_an_oracle_and_the_code_agrees():
    shapes = Graph()
    ps = URIRef("urn:test:ps")
    shapes.add((ps, SH.path, EX.period))
    shapes.add((ps, SH.minCount, EX.anything))
    shapes.add((URIRef("urn:test:ps2"), SH.path, EX.amount))
    shapes.add((URIRef("urn:test:ps2"), SH.pattern, EX.anything))
    contract = Graph().parse(data=ROLE_CONTRACT.split("ex:ObservationShape a")[0], format="turtle")
    conforms, results, text = _report(contract + shapes, use_shapes=ORACLE_SHAPE)
    assert not conforms
    assert [focus for focus, _ in results] == [str(EX["f-period"])], text
    assert not ground._has_value_constraint(shapes, ps)


def test_the_parameter_list_is_the_nine_value_constraints():
    """What `ground._VALUE_CONSTRAINTS` held before the list moved into the vocabulary."""
    assert ground._value_constraints() == frozenset(
        SH[p] for p in ("datatype", "in", "pattern", "minInclusive", "maxInclusive",
                        "minExclusive", "maxExclusive", "minLength", "maxLength"))
