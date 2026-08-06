"""Closure differential: full RDFS closure vs subclass-only (spec 2026-08-06 §3).

THE POINT: this loop changes behaviour, and the danger is NOT that something starts failing
— it is that a shape silently stops SEEING a node, so a violation goes uncaught. Verdict
parity alone would miss that. So the load-bearing leg compares FOCUS-NODE SETS per shape."""
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


def _verdict_and_focus(expanded, shapes):
    """(conforms, {focus-node IRIs}) for an ALREADY-EXPANDED graph, via pySHACL with
    inference off — the expansion under test is the variable, so the engine must add none."""
    from pyshacl import validate
    conforms, results, _ = validate(expanded, shacl_graph=shapes, inference="none",
                                    advanced=True)
    focus = {n for n in results.objects(None, SH.focusNode) if isinstance(n, URIRef)}
    return bool(conforms), focus


def _both_closures(data):
    from iladub.etkl import membrane
    shapes, ont = _shapes(), _ont()
    full = membrane.rdfs_closure(data, ont)
    sub = membrane.subclass_closure(data, ont)
    return _verdict_and_focus(full, shapes), _verdict_and_focus(sub, shapes)


# ---------- leg 1: the committed leak fixtures — verdict AND focus-node parity ----------

LEAKS = sorted(glob.glob(os.path.join(TESTS, "tab-*-leak.ttl")))


def test_leak_battery_is_not_empty():
    assert len(LEAKS) >= 10, f"expected the committed leak fixtures, found {len(LEAKS)}"


@pytest.mark.parametrize("path", LEAKS, ids=[os.path.basename(p) for p in LEAKS])
def test_both_closures_agree_on_every_committed_leak(path):
    name = os.path.basename(path)
    data = Graph().parse(path, format="turtle")
    (full_ok, full_focus), (sub_ok, sub_focus) = _both_closures(data)
    assert full_ok is False, f"fixture precondition: the reference closure must refuse {name}"
    assert sub_ok is False, (
        f"REGRESSION: subclass-only closure ADMITS {name}, which full closure refuses — "
        f"a shape lost sight of its focus node")
    assert full_focus == sub_focus, (
        f"focus-node divergence on {name}: only-full={sorted(full_focus - sub_focus)} "
        f"only-sub={sorted(sub_focus - full_focus)}")


# ---------- leg 2: a real compiled page — verdict AND focus-node parity ----------

STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_both_closures_agree_on_a_real_page_graph():
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    (full_ok, full_focus), (sub_ok, sub_focus) = _both_closures(rep.graph)
    assert full_ok == sub_ok is True, f"full={full_ok} sub={sub_ok} on the real stem page"
    assert full_focus == sub_focus, (
        f"focus-node divergence on the real page: "
        f"only-full={sorted(full_focus - sub_focus)[:5]} "
        f"only-sub={sorted(sub_focus - full_focus)[:5]}")


# ---------- leg 3: R58's mandated sh:class falsifiability case ----------

needs_rudof = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


def _bad_bbox_graph():
    """An EntryCell whose tab:hasBBox points at something that is NOT a tab:BBox. Under FULL
    closure this conforms, because tab:hasBBox's rdfs:range types the object regardless —
    which is what made sh:class unfalsifiable. Under subclass-only it must be refused."""
    g = Graph()
    cell, notbb = URIRef("urn:k:cell"), URIRef("urn:k:notabbox")
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("x")))
    g.add((cell, TAB.onPage, Literal(0)))
    g.add((cell, TAB.hasBBox, notbb))
    g.add((notbb, RDF.type, TAB.LeafRow))     # deliberately the wrong class
    return g


def test_sh_class_was_unfalsifiable_under_full_closure():
    """The premise R58 states, pinned so the next leg means something."""
    from iladub.etkl import membrane
    full = membrane.rdfs_closure(_bad_bbox_graph(), _ont())
    assert (URIRef("urn:k:notabbox"), RDF.type, TAB.BBox) in full, \
        "range typing did NOT fire — R58's premise is wrong, investigate before proceeding"


def test_sh_class_is_falsifiable_under_subclass_closure():
    from iladub.etkl import membrane
    sub = membrane.subclass_closure(_bad_bbox_graph(), _ont())
    assert (URIRef("urn:k:notabbox"), RDF.type, TAB.BBox) not in sub
    conforms, _ = _verdict_and_focus(sub, _shapes())
    assert conforms is False, "sh:class tab:BBox still unfalsifiable under the new closure"


@needs_rudof
def test_rudof_implements_sh_class_once_range_typing_is_gone():
    """R58's addendum: prove the NEW ENGINE actually implements sh:ClassConstraintComponent,
    now that the range-typing fallback no longer hides it."""
    from iladub.etkl import membrane
    ok, report = membrane._validate_rudof(_bad_bbox_graph(), _shapes(), _ont())
    assert ok is False, "rudof admitted a wrong-class hasBBox — sh:class unimplemented?"
