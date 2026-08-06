"""Differential battery: pySHACL vs rudof (spec 2026-08-06 §3.3).

THE POINT: agreement on healthy graphs proves almost nothing — a validator that did nothing
would also agree. The mutation leg is the evidence: violations are INJECTED into real
compiled graphs and BOTH engines must catch every one."""
import glob
import os
import random
import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES_DIR = os.path.join(ROOT, "vocab", "shapes")
ONT_DIR = os.path.join(ROOT, "vocab", "ontology")
TESTS = os.path.join(ROOT, "tests")

pytestmark = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES_DIR, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES_DIR, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT_DIR, "tab.ttl"), format="turtle")


def _both(g):
    from iladub.etkl import membrane
    s, o = _shapes(), _ont()
    p, _ = membrane._validate_pyshacl(g, s, o)
    r, _ = membrane._validate_rudof(g, s, o)
    return p, r


def _focus_node_sets(g):
    """Each engine's set of sh:focusNode IRIs, for the ONE comparison that is reliably
    engine-independent: focus nodes are IRIs in our graphs. Source shapes are frequently
    blank nodes with engine-specific labels (each engine mints its own), so they are NOT
    compared here — see spec 2026-08-06 §8's blank-node-label risk.

    Both engines validate the SAME subclass-only-closed graph (`membrane.subclass_closure`),
    with each engine's own inference turned off — matching what `membrane.validate` now does
    in production, so this comparison is a genuine engine differential and not also a closure
    differential (that comparison lives in tests/etkl/test_closure_equiv.py).

    pySHACL's own `(bool, str)` contract in membrane.py is left unchanged for this: the
    battery calls `pyshacl.validate` directly to get the results Graph, rather than having
    `_validate_pyshacl` grow a return value only this test needs."""
    import pyshacl
    from iladub.etkl import membrane
    s, o = _shapes(), _ont()

    expanded = membrane.subclass_closure(g, o)
    _, results_graph, _ = pyshacl.validate(
        expanded, shacl_graph=s, inference="none", advanced=True)
    p_nodes = {n for n in results_graph.objects(None, SH.focusNode) if isinstance(n, URIRef)}

    _, report = membrane._validate_rudof(g, s, o)
    report_graph = Graph().parse(data=report, format="turtle")
    r_nodes = {n for n in report_graph.objects(None, SH.focusNode) if isinstance(n, URIRef)}

    return p_nodes, r_nodes


# ---------- leg 1: NEGATIVE — the committed leak fixtures (both must REFUSE) ----------

LEAKS = sorted(glob.glob(os.path.join(TESTS, "tab-*-leak.ttl")))


@pytest.mark.parametrize("path", LEAKS, ids=[os.path.basename(p) for p in LEAKS])
def test_both_engines_refuse_every_committed_leak(path):
    g = Graph().parse(path, format="turtle")
    p, r = _both(g)
    assert p is False, f"fixture precondition: pySHACL must refuse {os.path.basename(path)}"
    assert r is False, f"rudof ADMITTED a leak pySHACL refuses: {os.path.basename(path)}"

    # Spec §3.3 item 2: both engines must report a violation on the same focus node.
    # Source shapes are frequently blank nodes with engine-specific labels and are
    # deliberately NOT compared — see _focus_node_sets' docstring and spec §8.
    p_nodes, r_nodes = _focus_node_sets(g)
    assert p_nodes == r_nodes, (
        f"focus-node sets differ for {os.path.basename(path)}: "
        f"pySHACL={p_nodes} rudof={r_nodes}")


def test_leak_battery_is_not_empty():
    assert len(LEAKS) >= 10, f"expected the committed leak fixtures, found {len(LEAKS)}"


# ---------- leg 2: POSITIVE — a real compiled page graph (both must ADMIT) ----------

STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_both_engines_admit_a_real_page_graph():
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    p, r = _both(rep.graph)
    assert p is True and r is True, f"pySHACL={p} rudof={r} on the real stem page"


# ---------- leg 3: MUTATION — inject violations, BOTH must catch (the real evidence) ----------

def _mutations(g, seed):
    """Yield (name, mutated_graph): each drops or corrupts something a shape requires."""
    rnd = random.Random(seed)
    outs = []

    cells = [s for s in g.subjects(RDF.type, TAB.EntryCell)]
    if cells:
        c = rnd.choice(cells)
        m = Graph(); m += g
        for o in list(m.objects(c, TAB.onPage)):
            m.remove((c, TAB.onPage, o))          # EntryCellPhysicalShape: onPage minCount 1
        outs.append(("drop-onPage", m))

        m2 = Graph(); m2 += g
        for o in list(m2.objects(c, TAB.cellText)):
            m2.remove((c, TAB.cellText, o))
        m2.add((c, TAB.cellText, Literal("")))     # WrappedCellShape (sh:sparql)
        outs.append(("blank-cellText", m2))

        m3 = Graph(); m3 += g
        for o in list(m3.objects(c, TAB.hasBBox)):
            m3.remove((c, TAB.hasBBox, o))         # EntryCellPhysicalShape: hasBBox minCount 1
        outs.append(("drop-bbox", m3))

    m4 = Graph(); m4 += g
    um = URIRef("urn:mut:um")
    m4.add((um, RDF.type, TAB.UnitMarker))
    m4.add((um, TAB.markerSymbol, Literal("$")))   # UnitMarkerShape: markerRegion minCount 1
    outs.append(("orphan-unit-marker", m4))

    return outs


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
@pytest.mark.parametrize("seed", [11, 23, 37])
def test_both_engines_catch_every_injected_violation(seed):
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    # Pin the precondition the coverage below depends on, so a failure points at the
    # cause (no EntryCells in the compiled page) rather than the symptom (missing kinds).
    cells = list(rep.graph.subjects(RDF.type, TAB.EntryCell))
    assert cells, "no tab:EntryCell in the compiled page — mutation legs would be vacuous"
    muts = _mutations(rep.graph, seed)
    # A battery that passes while silently exercising only a quarter of its mutations
    # (e.g. because tab:EntryCell ever went to zero — corpus swap, extraction regression,
    # changed page_number) manufactures false confidence in the engine swap, which is
    # worse than no battery. `assert muts` alone is satisfied by the one unconditional
    # mutation, so pin full coverage explicitly.
    kinds = {name for name, _ in muts}
    assert kinds == {"drop-onPage", "blank-cellText", "drop-bbox", "orphan-unit-marker"}, (
        f"mutation coverage collapsed to {sorted(kinds)} — the graph shape changed "
        f"(zero tab:EntryCell would silently drop three of the four kinds)")
    for name, m in muts:
        p, r = _both(m)
        assert p is False, f"[{name}] fixture precondition: pySHACL must catch it"
        assert r is False, f"[{name}] rudof MISSED a violation pySHACL catches"
