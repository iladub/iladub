"""Round-trip oracle over the SPARQL forward CONSTRUCTs (loop one).

Supersedes the old Python-replay tests: the base is now a derived hproj:Projection
RDF graph; round_trip reconstructs the grid via the forward .rq files and exact-compares.
"""
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from rdflib.namespace import XSD
from iladub.etkl.oracle import round_trip
from iladub.etkl.recipe import UnpivotOp, StripAggregationOp, Recipe

TAB = Namespace("https://w3id.org/iladub/tab#"); EX = Namespace("https://example.org/d#")


def _base_region():
    """4-fact native-RDF base for Region×Year."""
    p = Graph()
    facts = [("10", "North", "2020"), ("20", "South", "2020"),
             ("11", "North", "2021"), ("21", "South", "2021")]
    for i, (mv, region, year) in enumerate(facts):
        bf = EX["bf%d" % i]
        p.add((bf, RDF.type, TAB.BaseFact)); p.add((bf, TAB.measureValue, Literal(mv, datatype=XSD.decimal)))
        cd = EX["bf%d-dim" % i]; cs = EX["bf%d-stub" % i]
        p.add((bf, TAB.atDimensionValue, cd)); p.add((cd, TAB.dimensionName, Literal("Region"))); p.add((cd, TAB.value, Literal(region)))
        p.add((bf, TAB.atDimensionValue, cs)); p.add((cs, TAB.dimensionName, Literal("Year"))); p.add((cs, TAB.value, Literal(year)))
    return p


ORIGINAL = {("2020", "North"): "10", ("2020", "South"): "20",
            ("2021", "North"): "11", ("2021", "South"): "21",
            ("2020", "Year"): "2020", ("2021", "Year"): "2021"}


def test_correct_recipe_round_trips():
    v = round_trip(ORIGINAL, _base_region(), Recipe((UnpivotOp("Region", "Year"),)))
    assert v.ok and v.residue == ()


def test_corrupted_base_is_rejected():
    bad = _base_region()
    # corrupt one measure: set bf0 (10 -> 999)
    bad.set((EX.bf0, TAB.measureValue, Literal("999", datatype=XSD.decimal)))
    v = round_trip(ORIGINAL, bad, Recipe((UnpivotOp("Region", "Year"),)))
    assert not v.ok and v.residue


def test_strip_round_trips_total_column():
    original = dict(ORIGINAL)
    original[("2020", "Total")] = "30"; original[("2021", "Total")] = "32"
    recipe = Recipe((UnpivotOp("Region", "Year"),
                     StripAggregationOp("column", "sum", ("North", "South"), "Total")))
    v = round_trip(original, _base_region(), recipe)
    assert v.ok, v.residue
