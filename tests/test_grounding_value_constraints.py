from rdflib import Graph, Namespace
from iladub.ground import _property_shape, _has_value_constraint

TX = Namespace("https://example.org/transplant#")


def _shapes():
    return Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")


def test_ef_property_shape_has_value_constraint():
    s = _shapes()
    ps = _property_shape(s, str(TX) + "ejectionFraction")
    assert ps is not None
    assert _has_value_constraint(s, ps) is True          # datatype + range declared


def test_unconstrained_field_has_no_property_shape():
    s = _shapes()
    # causeOfDeath has no property shape at all -> nothing to verify -> quarantine downstream
    assert _property_shape(s, str(TX) + "causeOfDeath") is None


def test_cardinality_only_is_not_a_value_constraint():
    # organ shape is cardinality-only (min/maxCount) -> not a value constraint
    s = _shapes()
    ps = _property_shape(s, str(TX) + "organ")
    assert ps is not None
    assert _has_value_constraint(s, ps) is False
