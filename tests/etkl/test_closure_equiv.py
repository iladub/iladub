"""Closure differential: full RDFS closure vs subclass-only (spec 2026-08-06 §3).

THE POINT: this loop changes behaviour, and the danger is NOT that something starts failing
— it is that a shape silently stops SEEING a node, so a violation goes uncaught. Verdict
parity alone would miss that. So the load-bearing legs compare VIOLATION SETS — each a
(sourceConstraintComponent, focusNode, resultPath) triple, not a bare focus-node set,
because a flat focus-node set collapses a case where a genuinely NEW constraint fires on a
node that was already a focus node for some other reason: two different violations on the
same node would wrongly compare as equal. Fix round 1 (reviewer-found): the original single
flat focus-node set could not distinguish "same violations" from "same focus nodes, different
violations", which is precisely the class of defect this battery exists to catch."""
import glob
import os
import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES_DIR = os.path.join(ROOT, "vocab", "shapes")
ONT_DIR = os.path.join(ROOT, "vocab", "ontology")
TESTS = os.path.join(ROOT, "tests")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES_DIR, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES_DIR, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT_DIR, "tab.ttl"), format="turtle")


def _violations(results):
    """The set of (sourceConstraintComponent, focusNode, resultPath) triples a validation
    report graph actually carries — all three are IRIs, so they compare reliably run-to-run.

    Deliberately NOT sh:sourceShape: pySHACL mints a fresh blank node per property shape on
    every run, and blank-node identifiers are not stable across separate validate() calls, so
    comparing them would report a "divergence" that has nothing to do with the closure under
    test — it would just be blank-node relabeling noise.

    `resultPath` is `None` when a result carries no path (node-shape violations, e.g. a
    SPARQL-based shape's $this-only result) — using None rather than dropping the triple
    keeps those violations comparable too, instead of silently disappearing from the set."""
    out = set()
    for vr in results.subjects(RDF.type, SH.ValidationResult):
        comp = results.value(vr, SH.sourceConstraintComponent)
        focus = results.value(vr, SH.focusNode)
        path = results.value(vr, SH.resultPath)
        if isinstance(comp, URIRef) and isinstance(focus, URIRef):
            out.add((comp, focus, path if isinstance(path, URIRef) else None))
    return out


def _verdict_and_violations(expanded, shapes):
    """(conforms, {(constraintComponent, focusNode, resultPath)}) for an ALREADY-EXPANDED
    graph, via pySHACL with inference off — the expansion under test is the variable, so the
    engine must add none."""
    from pyshacl import validate
    conforms, results, _ = validate(expanded, shacl_graph=shapes, inference="none",
                                    advanced=True)
    return bool(conforms), _violations(results)


def _both_closures(data):
    from iladub.etkl import membrane
    shapes, ont = _shapes(), _ont()
    full = membrane.rdfs_closure(data, ont)
    sub = membrane.subclass_closure(data, ont)
    return _verdict_and_violations(full, shapes), _verdict_and_violations(sub, shapes)


# ---------- leg 1: the committed leak fixtures — verdict AND violation-set parity ----------

LEAKS = sorted(glob.glob(os.path.join(TESTS, "tab-*-leak.ttl")))


def test_leak_battery_is_not_empty():
    assert len(LEAKS) >= 10, f"expected the committed leak fixtures, found {len(LEAKS)}"


@pytest.mark.parametrize("path", LEAKS, ids=[os.path.basename(p) for p in LEAKS])
def test_both_closures_agree_on_every_committed_leak(path):
    name = os.path.basename(path)
    data = Graph().parse(path, format="turtle")
    (full_ok, full_v), (sub_ok, sub_v) = _both_closures(data)
    assert full_ok is False, f"fixture precondition: the reference closure must refuse {name}"
    assert sub_ok is False, (
        f"REGRESSION: subclass-only closure ADMITS {name}, which full closure refuses — "
        f"a shape lost sight of its focus node")
    assert full_v, (
        f"{name} produced no violations under full closure — fixture is inert, and "
        f"full_v == sub_v below would pass vacuously")
    assert full_v == sub_v, (
        f"violation-set divergence on {name} ((constraintComponent, focusNode, resultPath) "
        f"triples): only-full={sorted(full_v - sub_v)} only-sub={sorted(sub_v - full_v)}")


# ---------- leg 2: a real compiled page ----------

STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_both_closures_agree_on_a_real_page_graph():
    """VERDICT PARITY ONLY. The real stem page conforms under both closures, so both
    violation sets are empty here BY CONSTRUCTION — set() == set() would be vacuous
    "evidence" that proves nothing about per-shape visibility (fix round 1, reviewer-found:
    the original version compared these empty sets and called it focus-node parity evidence).
    The real violation-set evidence on a real graph lives in
    test_both_closures_agree_on_a_mutated_real_page_graph below, which injects an actual
    violation into a copy of this same compiled graph."""
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    (full_ok, _), (sub_ok, _) = _both_closures(rep.graph)
    assert full_ok == sub_ok is True, f"full={full_ok} sub={sub_ok} on the real stem page"


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_both_closures_agree_on_a_mutated_real_page_graph():
    """The load-bearing leg-2 evidence: take the real compiled page, strip one EntryCell's
    tab:onPage (an EntryCellPhysicalShape MinCount violation), and require both closures to
    refuse it with the IDENTICAL, NON-EMPTY violation set. Unlike the unmutated page above,
    this has a real, reproducible violation to compare — not two empty sets."""
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    mutated = Graph()
    mutated += rep.graph
    cells = sorted(mutated.subjects(RDF.type, TAB.EntryCell))
    assert cells, "no tab:EntryCell found on the real stem page — cannot inject a mutation"
    target = cells[0]
    removed = list(mutated.objects(target, TAB.onPage))
    assert removed, f"chosen EntryCell {target} carries no tab:onPage — cannot mutate it away"
    for o in removed:
        mutated.remove((target, TAB.onPage, o))

    (full_ok, full_v), (sub_ok, sub_v) = _both_closures(mutated)
    assert full_ok is False, "mutation precondition: removing tab:onPage must make full closure refuse"
    assert sub_ok is False, (
        "REGRESSION: subclass-only closure ADMITS the mutated real page graph, which full "
        "closure refuses — a shape lost sight of its focus node")
    assert full_v, "mutation produced no violations under full closure — mutation is inert"
    assert full_v == sub_v, (
        f"violation-set divergence on the mutated real page: "
        f"only-full={sorted(full_v - sub_v)[:5]} only-sub={sorted(sub_v - full_v)[:5]}")


# ---------- leg 3: R58's mandated sh:class falsifiability case ----------

needs_rudof = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


def _bad_bbox_graph():
    """An EntryCell that satisfies EVERY OTHER shape it is targeted by — cellText, onPage,
    exactly one atColumn, exactly one atRow, and no table linkage to trip any of the
    SPARQL-based orphan/coverage shapes (those all require a `?tbl tab:hasCell`/
    `tab:hasLeafRow`/`tab:hasLeafColumn` triple to bind before they can fire, and this graph
    deliberately has none) — EXCEPT that tab:hasBBox points at something that is NOT a
    tab:BBox. Under FULL closure this CONFORMS OUTRIGHT (fix round 1, reviewer-found: the
    original fixture omitted atColumn/atRow, so EntryCellShape's own MinCount already refused
    it under both closures regardless of sh:class — the docstring's "conforms" claim was
    empirically false), because tab:hasBBox's rdfs:range types the object regardless, which is
    what made sh:class unfalsifiable. Under subclass-only it must be refused, and refused for
    exactly that one reason."""
    g = Graph()
    cell, notbb = URIRef("urn:k:cell"), URIRef("urn:k:notabbox")
    col, row = URIRef("urn:k:col"), URIRef("urn:k:row")
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("x")))
    g.add((cell, TAB.onPage, Literal(0)))
    g.add((cell, TAB.atColumn, col))
    g.add((cell, TAB.atRow, row))
    g.add((cell, TAB.hasBBox, notbb))
    g.add((notbb, RDF.type, TAB.LeafRow))     # deliberately the wrong class
    return g


def test_sh_class_was_unfalsifiable_under_full_closure():
    """The premise R58 states, pinned so the next leg means something: under full closure the
    ONLY defect in this otherwise-conformant EntryCell (a wrong-class hasBBox target) is
    invisible — the graph CONFORMS OUTRIGHT, not merely "happens not to trip sh:class". If it
    conformed only because some OTHER shape's own violation swallowed the fixture's intent,
    that would not be evidence sh:class itself was unfalsifiable — it would be a confounded
    fixture (exactly fix round 1's finding about the pre-fix version of this test)."""
    from iladub.etkl import membrane
    data = _bad_bbox_graph()
    full = membrane.rdfs_closure(data, _ont())
    assert (URIRef("urn:k:notabbox"), RDF.type, TAB.BBox) in full, \
        "range typing did NOT fire — R58's premise is wrong, investigate before proceeding"
    conforms, violations = _verdict_and_violations(full, _shapes())
    assert conforms is True, (
        f"R58's premise is wrong: the otherwise-conformant graph does NOT conform under full "
        f"closure — something besides sh:class is also refusing it, so this fixture cannot "
        f"show sh:class was unfalsifiable. Violations: {sorted(violations)}")


def test_sh_class_is_falsifiable_under_subclass_closure():
    from iladub.etkl import membrane
    sub = membrane.subclass_closure(_bad_bbox_graph(), _ont())
    assert (URIRef("urn:k:notabbox"), RDF.type, TAB.BBox) not in sub
    conforms, violations = _verdict_and_violations(sub, _shapes())
    assert conforms is False, "sh:class tab:BBox still unfalsifiable under the new closure"
    expected = (SH.ClassConstraintComponent, URIRef("urn:k:cell"), TAB.hasBBox)
    assert expected in violations, (
        f"expected a ClassConstraintComponent violation on (focus=urn:k:cell, "
        f"path=tab:hasBBox), got: {sorted(violations)}")


@needs_rudof
def test_rudof_implements_sh_class_once_range_typing_is_gone():
    """R58's addendum: prove the NEW ENGINE actually implements sh:ClassConstraintComponent,
    now that the range-typing fallback no longer hides it. `ok is False` alone would not
    prove THIS constraint fired — the report must actually carry a ClassConstraintComponent
    violation (fix round 1: the same confounding risk as the pySHACL legs applies here)."""
    from iladub.etkl import membrane
    ok, report = membrane._validate_rudof(_bad_bbox_graph(), _shapes(), _ont())
    assert ok is False, "rudof admitted a wrong-class hasBBox — sh:class unimplemented?"
    report_graph = Graph().parse(data=report, format="turtle")
    assert (None, SH.sourceConstraintComponent, SH.ClassConstraintComponent) in report_graph, (
        f"rudof's report has no ClassConstraintComponent violation — sh:class may be "
        f"unimplemented rather than merely never having fired before:\n{report}")
