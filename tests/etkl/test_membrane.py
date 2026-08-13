"""The membrane seam: one place any SHACL runs (spec 2026-08-06-membrane-engine-swap-design.md).

Task 1 establishes the seam over pySHACL with NO behaviour change; later tasks swap the
engine underneath it. The point of the seam is that `tiling.region_tiles` and
`compile._validate` stop constructing their own pyshacl.validate calls."""
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES = os.path.join(ROOT, "vocab", "shapes")
ONT = os.path.join(ROOT, "vocab", "ontology")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT, "tab.ttl"), format="turtle")


def test_membrane_reports_conformance_on_a_clean_graph():
    from iladub.etkl import membrane
    g = Graph()
    cell = URIRef("urn:m:cell")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("Americas")))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is True, report
    assert isinstance(report, str)


def test_membrane_catches_a_core_violation():
    # UnitMarkerShape: a tab:UnitMarker needs >=1 tab:markerRegion.
    from iladub.etkl import membrane
    g = Graph()
    um = URIRef("urn:m:um")
    g.add((um, RDF.type, TAB.UnitMarker))
    g.add((um, TAB.markerSymbol, Literal("$")))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False
    assert "markerRegion" in report or "UnitMarkerShape" in report


def test_membrane_catches_a_sparql_constraint_violation():
    # WrappedCellShape (sh:sparql): a bbox-carrying tab:Cell needs non-empty cellText.
    from iladub.etkl import membrane
    g = Graph()
    cell, bb = URIRef("urn:m:c"), URIRef("urn:m:bb")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("")))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((cell, TAB.hasBBox, bb))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False
    assert "cellText" in report or "WrappedCellShape" in report


def test_membrane_no_longer_infers_types_from_property_domains():
    """INVERTED by spec 2026-08-06 (was test_membrane_applies_rdfs_inference).

    A node carrying tab:hasBBox but no explicit type is NO LONGER a tab:Cell, so
    WrappedCellShape does not fire on it. That inference was the R19 accident — a
    ROUND_TRIP_FAIL candidate carrying a bbox typed as a Cell and crashing the compile — and
    dropping it closes R19 at its root. The graph below carries no OTHER violation, so it now
    conforms."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:m:inf"), URIRef("urn:m:infbb")
    g.add((node, TAB.hasBBox, bb))          # no explicit rdf:type
    g.add((bb, RDF.type, TAB.BBox))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is True, report


def test_engine_name_is_reported():
    from iladub.etkl import membrane
    assert membrane.engine_name() in ("pyshacl", "rudof")


def test_call_sites_use_the_seam():
    """Structural pin: neither call site may construct its own pyshacl.validate."""
    import inspect
    from iladub.etkl import tiling
    import iladub.etkl.compile as C
    assert "membrane" in inspect.getsource(tiling.region_tiles)
    assert "membrane" in inspect.getsource(C._validate)


# ---------------------------------------------------------------- closure

def test_rdfs_closure_materializes_subclass_and_domain_types():
    """Closure must reproduce what inference='rdfs' gives pySHACL today: subclass closure
    (EntryCell -> Cell, which sh:targetClass needs) AND domain typing (the R19 mechanism).

    This pins the RETAINED reference closure (rdfs_closure), not production; production now
    uses subclass_closure, whose domain-typing behaviour is pinned by
    test_subclass_closure_drops_domain_typing."""
    from iladub.etkl import membrane
    g = Graph()
    ec, node, bb = URIRef("urn:c:ec"), URIRef("urn:c:n"), URIRef("urn:c:bb")
    g.add((ec, RDF.type, TAB.EntryCell))     # subclass of tab:Cell in tab.ttl
    g.add((node, TAB.hasBBox, bb))           # rdfs:domain tab:Cell
    out = membrane.rdfs_closure(g, _ont())
    assert (ec, RDF.type, TAB.Cell) in out, "subclass closure missing"
    assert (node, RDF.type, TAB.Cell) in out, "domain typing missing (R19 mechanism)"


def test_rdfs_closure_drops_literal_subject_triples():
    """owlrl emits `"307.47"^^xsd:decimal rdf:type rdfs:Resource` — illegal RDF that rdflib
    tolerates and a strict parser refuses. The closure must remove every such triple."""
    from iladub.etkl import membrane
    from rdflib.namespace import XSD
    g = Graph()
    c = URIRef("urn:c:cell")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.x0, Literal("307.47", datatype=XSD.decimal)))
    out = membrane.rdfs_closure(g, _ont())
    bad = [s for s in out.subjects() if isinstance(s, Literal)]
    assert bad == [], f"literal-subject triples survived: {bad[:3]}"


def test_rdfs_closure_does_not_mutate_its_input():
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:c:x"), RDF.type, TAB.EntryCell))
    before = len(g)
    membrane.rdfs_closure(g, _ont())
    assert len(g) == before, "rdfs_closure must return a NEW graph"


def test_rdfs_closure_injects_only_ontology_axioms():
    """rdfs_closure must mix the ontology in the way pySHACL's inoculate() does: only
    RDFS/OWL axioms cross into the merged graph, not arbitrary triples the ontology graph
    happens to carry. A full graph union would leak the latter into what rudof sees, making
    the Task 4 engine differential compare two different graphs, not two engines."""
    from rdflib.namespace import RDFS
    from iladub.etkl import membrane
    ont = Graph()
    sub, sup, thing = URIRef("urn:o:Sub"), URIRef("urn:o:Super"), URIRef("urn:o:thing")
    ont.add((sub, RDFS.subClassOf, sup))                              # a real RDFS axiom
    ont.add((thing, URIRef("urn:o:randomPredicate"), Literal("x")))   # NOT an axiom
    data = Graph()
    data.add((URIRef("urn:c:d"), RDF.type, sub))
    out = membrane.rdfs_closure(data, ont)
    assert (URIRef("urn:c:d"), RDF.type, sup) in out, "axiom's subclass closure missing"
    assert (thing, URIRef("urn:o:randomPredicate"), Literal("x")) not in out, \
        "non-axiom ontology triple leaked through — full union, not inoculate()"


def test_rdfs_closure_does_not_fabricate_hidden_literals():
    """Plain owlrl.RDFS_Semantics runs one_time_rules(), which does literal VALUE-SPACE
    unification and fabricates triples: measured on the test_row_groups fixture, a cell with
    tab:onPage "0"^^xsd:integer came out of closure ALSO carrying "0.0"^^xsd:decimal, invented
    from an unrelated xsd:decimal elsewhere in the graph because 0 and 0.0 are the same value.
    pySHACL avoids this by suppressing one_time_rules (CustomRDFSSemantics) — rdfs_closure
    must do the same, or rudof rejects graphs pySHACL admits (sh:datatype violated by the
    fabricated twin)."""
    from rdflib.namespace import XSD
    from iladub.etkl import membrane
    g = Graph()
    cell, other = URIRef("urn:c:cell"), URIRef("urn:c:other")
    g.add((cell, TAB.onPage, Literal(0, datatype=XSD.integer)))
    g.add((other, TAB.y0, Literal(0.0, datatype=XSD.decimal)))
    out = membrane.rdfs_closure(g, _ont())
    values = list(out.objects(cell, TAB.onPage))
    assert len(values) == 1, f"onPage gained fabricated twin(s): {values}"
    assert values[0].datatype == XSD.integer, f"onPage datatype corrupted: {values[0].datatype}"


# ---------------------------------------------------------------- rudof engine

import pytest

needs_rudof = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


@needs_rudof
def test_rudof_engine_agrees_on_a_clean_graph():
    from iladub.etkl import membrane
    g = Graph()
    c = URIRef("urn:r:c")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.cellText, Literal("Americas")))
    ok_p, _ = membrane._validate_pyshacl(g, _shapes(), _ont())
    ok_r, _ = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_p == ok_r is True


@needs_rudof
def test_rudof_engine_catches_a_sparql_constraint_violation():
    from iladub.etkl import membrane
    g = Graph()
    c, bb = URIRef("urn:r:c2"), URIRef("urn:r:bb2")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.cellText, Literal("")))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((c, TAB.hasBBox, bb))
    ok_r, report = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_r is False
    assert "cellText" in report or "WrappedCellShape" in report


@needs_rudof
def test_rudof_engine_does_not_see_domain_inferred_types():
    """INVERTED by spec 2026-08-06 (was test_rudof_engine_sees_inferred_types).

    rudof does NO inference of its own — the seam now runs subclass_closure, not
    rdfs_closure, so a node carrying tab:hasBBox but no explicit type is NO LONGER typed
    tab:Cell and WrappedCellShape does not fire. Rudof-path twin of
    test_membrane_no_longer_infers_types_from_property_domains."""
    from iladub.etkl import membrane
    g = Graph()
    n, bb = URIRef("urn:r:inf"), URIRef("urn:r:infbb")
    g.add((n, TAB.hasBBox, bb))
    g.add((bb, RDF.type, TAB.BBox))
    ok_r, report = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_r is True, report


@needs_rudof
def test_engine_switch_selects_rudof(monkeypatch):
    from iladub.etkl import membrane
    monkeypatch.setenv("ILADUB_MEMBRANE", "rudof")
    assert membrane.engine_name() == "rudof"
    monkeypatch.setenv("ILADUB_MEMBRANE", "pyshacl")
    assert membrane.engine_name() == "pyshacl"


@needs_rudof
def test_engine_defaults_to_rudof_when_unset(monkeypatch):
    """Pins the loop's headline behaviour: with no override, rudof is what actually runs."""
    from iladub.etkl import membrane
    monkeypatch.delenv("ILADUB_MEMBRANE", raising=False)
    assert membrane.engine_name() == "rudof"


def test_engine_name_rejects_an_unknown_forced_value(monkeypatch):
    from iladub.etkl import membrane
    monkeypatch.setenv("ILADUB_MEMBRANE", "not-a-real-engine")
    import pytest as _pytest
    with _pytest.raises(ValueError):
        membrane.engine_name()


def test_engine_name_refuses_to_silently_fall_back_when_rudof_forced_but_unavailable(monkeypatch):
    from iladub.etkl import membrane
    monkeypatch.setenv("ILADUB_MEMBRANE", "rudof")
    monkeypatch.setattr(membrane, "rudof_available", lambda: False)
    import pytest as _pytest
    with _pytest.raises(ValueError):
        membrane.engine_name()


def test_rudof_unparseable_report_is_not_conformance():
    """Fail-safe direction, pinned independent of pyrudof being installed: an empty or
    malformed report must never read as conformance."""
    from iladub.etkl import membrane
    assert membrane._conforms_from_report("") is False
    assert membrane._conforms_from_report("garbage, not turtle at all") is False
    assert membrane._conforms_from_report(
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n_:1 a sh:ValidationReport ;\n"
        "\tsh:conforms false .\n") is False
    assert membrane._conforms_from_report(
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n_:1 a sh:ValidationReport ;\n"
        "\tsh:conforms true .\n") is True


@needs_rudof
def test_conforms_parse_is_not_fooled_by_a_literal_containing_the_token():
    """C1 regression: a substring test over the report is unsound because rudof echoes
    offending literal values into sh:value. A tab:EntryCell whose tab:onPage literal IS the
    string "sh:conforms true" must still be refused — that literal also violates
    EntryCellPhysicalShape's sh:datatype xsd:integer, so the report legitimately contains
    the string `sh:conforms false` (the real verdict) alongside the echoed offending value."""
    from iladub.etkl import membrane
    g = Graph()
    cell, bb = URIRef("urn:m:injected"), URIRef("urn:m:injectedbb")
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("x")))
    g.add((cell, TAB.onPage, Literal("sh:conforms true")))  # plain string, not xsd:integer
    g.add((cell, TAB.hasBBox, bb))
    g.add((bb, RDF.type, TAB.BBox))
    ok_p, _ = membrane._validate_pyshacl(g, _shapes(), _ont())
    ok_r, _ = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_p is False, "fixture precondition: pySHACL must refuse this graph"
    assert ok_r is False, "rudof's report was fooled by the echoed literal — substring bug"


# ---------------------------------------------------------------- the parity invariant

def test_both_legs_are_built_from_the_very_same_document():
    """THE INVARIANT THE WHOLE PARITY LOOP EXISTS TO GUARANTEE, pinned as an oracle rather
    than left to hold by construction (spec 2026-08-13-membrane-parity-design.md §3).

    Since 2026-08-13 the two production legs no longer call the same function: `_validate_rudof`
    takes `_payload_nt`'s string (pyrudof.read_data takes a string, so re-parsing it into a
    Graph only to discard it was 148 ms of waste per call on a real page), while
    `_validate_pyshacl` takes `_payload`'s re-parsed Graph. That split is safe ONLY while
    `_payload` is a pure delegate to `_payload_nt` — and nothing else asserted it.

    Insert any step into `_payload` after the delegation (a repair, a normalisation, a second
    closure pass) and the two engines silently start judging different documents again, which
    is precisely R94, the thing this loop closed. Byte equality is the cheapest possible
    detector for that, and it costs one line.

    Deliberately NOT in tests/etkl/test_membrane_equiv.py: that whole module is skipped where
    `pyrudof` is absent, and this invariant governs the pySHACL-only install too.
    """
    from iladub.etkl import membrane
    from rdflib import BNode
    g = Graph()
    cell, bb = URIRef("urn:m:pcell"), BNode()      # a blank node, so skolemization is exercised
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("Americas")))
    g.add((cell, TAB.hasBBox, bb))
    g.add((bb, RDF.type, TAB.BBox))
    graph_payload, nt_payload = membrane._payload(g, _ont())
    assert nt_payload == membrane._payload_nt(g, _ont()), (
        "the two production legs are being handed DIFFERENT documents — `_payload` has grown "
        "a step `_payload_nt` does not have, and R94's asymmetry is back")
    # ...and the Graph the pySHACL leg gets is that same document, not some other artifact.
    assert len(graph_payload) == len(Graph().parse(data=nt_payload, format="nt"))


# ---------------------------------------------------------------- subclass-only closure

def test_subclass_closure_materializes_supertypes():
    """The half the shapes actually use: sh:targetClass tab:Cell must still see an
    explicitly-typed tab:EntryCell (tab:EntryCell rdfs:subClassOf tab:Cell in tab.ttl)."""
    from iladub.etkl import membrane
    g = Graph()
    ec = URIRef("urn:s:ec")
    g.add((ec, RDF.type, TAB.EntryCell))
    out = membrane.subclass_closure(g, _ont())
    assert (ec, RDF.type, TAB.Cell) in out, "subclass closure missing"


def test_subclass_closure_is_transitive():
    """A -> B -> C must yield C, not just B."""
    from rdflib.namespace import RDFS
    from iladub.etkl import membrane
    ont = Graph()
    a, b, c = URIRef("urn:s:A"), URIRef("urn:s:B"), URIRef("urn:s:C")
    ont.add((a, RDFS.subClassOf, b))
    ont.add((b, RDFS.subClassOf, c))
    data = Graph()
    node = URIRef("urn:s:n")
    data.add((node, RDF.type, a))
    out = membrane.subclass_closure(data, ont)
    assert (node, RDF.type, b) in out and (node, RDF.type, c) in out


def test_subclass_closure_drops_domain_typing():
    """THE BEHAVIOUR CHANGE, pinned positively. A node carrying tab:hasBBox must NOT become
    a tab:Cell — that inference is the R19 accident (a ROUND_TRIP_FAIL candidate with a bbox
    typed as a Cell and tripped WrappedCellShape). Dropping it closes R19 at its root."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:s:n"), URIRef("urn:s:bb")
    g.add((node, TAB.hasBBox, bb))      # rdfs:domain tab:Cell in tab.ttl
    g.add((bb, RDF.type, TAB.BBox))
    out = membrane.subclass_closure(g, _ont())
    assert (node, RDF.type, TAB.Cell) not in out, "domain typing survived — R19 still open"


def test_subclass_closure_drops_range_typing():
    """The other half of the same change, and the reason R58 mandates an sh:class case:
    tab:hasBBox rdfs:range tab:BBox must no longer type its object, which is what makes
    sh:class tab:BBox falsifiable again."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:s:n2"), URIRef("urn:s:bb2")
    g.add((node, TAB.hasBBox, bb))      # bb NOT explicitly typed
    out = membrane.subclass_closure(g, _ont())
    assert (bb, RDF.type, TAB.BBox) not in out, "range typing survived — sh:class stays unfalsifiable"


def test_subclass_closure_injects_no_ontology_triples():
    """The ontology is READ for its axioms, never mixed into the validated graph. So the
    graph rudof sees is data plus its own type closure — nothing else — and no ontology node
    can ever become a focus node."""
    from rdflib.namespace import RDFS
    from iladub.etkl import membrane
    ont = Graph()
    sub, sup = URIRef("urn:o:Sub"), URIRef("urn:o:Super")
    ont.add((sub, RDFS.subClassOf, sup))
    ont.add((URIRef("urn:o:thing"), URIRef("urn:o:randomPredicate"), Literal("x")))
    data = Graph()
    d = URIRef("urn:s:d")
    data.add((d, RDF.type, sub))
    out = membrane.subclass_closure(data, ont)
    assert (d, RDF.type, sup) in out, "the axiom's effect is missing"
    assert (sub, RDFS.subClassOf, sup) not in out, "a subClassOf axiom leaked into the data graph"
    assert (URIRef("urn:o:thing"), URIRef("urn:o:randomPredicate"), Literal("x")) not in out


def test_subclass_closure_does_not_mutate_its_input():
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:s:x"), RDF.type, TAB.EntryCell))
    before = len(g)
    membrane.subclass_closure(g, _ont())
    assert len(g) == before, "subclass_closure must return a NEW graph"


def test_subclass_closure_drops_literal_subject_triples():
    """The filter survives as an INVARIANT GUARD, not a workaround: nothing in this closure
    can produce a literal-subject triple, so this pins that property rather than repairing
    owlrl's output. Built by injecting one directly, since no code path emits one."""
    from rdflib.namespace import XSD
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:s:c"), RDF.type, TAB.EntryCell))
    g.add((Literal("307.47", datatype=XSD.decimal), RDF.type, TAB.Cell))   # illegal RDF
    out = membrane.subclass_closure(g, _ont())
    assert [s for s in out.subjects() if isinstance(s, Literal)] == []
