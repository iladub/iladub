"""Differential battery: pySHACL vs rudof (spec 2026-08-06 §3.3).

THE POINT: agreement on healthy graphs proves almost nothing — a validator that did nothing
would also agree. The mutation leg is the evidence: violations are INJECTED into real
compiled graphs and BOTH engines must catch every one."""
import glob
import os
import random
import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH, XSD

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


# ---------- leg 4: the DECISION shapes, engine-differentially (spec 2026-08-10 §5.4) ------
#
# WHY THIS LEG EXISTS: legs 1-3 cover the TAB shapes only. Task 6 puts dec-shapes.ttl and
# iladub-shapes.ttl into the compile membrane, and `membrane.validate` resolves to RUDOF
# wherever pyrudof is installed — so without this leg the promotion-epistemics enforcement
# path would ship with no engine-equivalence evidence at all, while every number measured
# for it came from pySHACL.
#
# BOTH shape files carry an sh:sparql constraint (dec-shapes.ttl:23, iladub-shapes.ttl:67),
# which is precisely where a native Rust validator and pySHACL are most likely to diverge.
# Those two mutations are the point of this leg; the minCount ones are the control.

DEC = Namespace("https://w3id.org/iladub/dec#")
ILADUB = Namespace("https://w3id.org/iladub#")
EXN = Namespace("urn:equiv:")


def _dec_shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES_DIR, "dec-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES_DIR, "iladub-shapes.ttl"), format="turtle")
    return g


def _dec_ont():
    g = Graph()
    for f in ("dec.ttl", "iladub.ttl"):
        g.parse(os.path.join(ONT_DIR, f), format="turtle")
    return g


def _both_dec(g):
    from iladub.etkl import membrane
    s, o = _dec_shapes(), _dec_ont()
    p, _ = membrane._validate_pyshacl(g, s, o)
    r, _ = membrane._validate_rudof(g, s, o)
    return p, r


def _conformant_promotion():
    """An iladub:PromotionDecision that conforms — the same shape the producers emit after
    this loop's Tasks 2-5. It reaches dec:DecisionHolonShape only through the subclass
    axiom in iladub.ttl, so this fixture also exercises the closure the membrane depends on."""
    g = Graph()
    pd, cand = EXN.pd, EXN.cand
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, EXN.agent))
    for local in ("optA", "optB"):
        o = EXN[local]
        g.add((o, RDF.type, DEC.Option))
        g.add((pd, DEC.optionSpace, o))
    g.add((pd, DEC.chosen, EXN.optA))
    g.add((EXN.optB, DEC.rejectedBecause, Literal("the scheme has no member for this value")))
    return g


def test_both_engines_admit_a_conformant_promotion_decision():
    p, r = _both_dec(_conformant_promotion())
    assert p is True and r is True, f"pySHACL={p} rudof={r} on a conformant promotion decision"


def _dec_mutations():
    """(name, graph): each breaks exactly one thing dec-shapes/iladub-shapes require."""
    outs = []

    m = _conformant_promotion()
    for o in list(m.objects(EXN.pd, DEC.optionSpace)):
        m.remove((EXN.pd, DEC.optionSpace, o))
    outs.append(("drop-optionSpace", m))

    m = _conformant_promotion()
    m.remove((EXN.pd, DEC.chosen, EXN.optA))
    outs.append(("drop-chosen", m))

    m = _conformant_promotion()                    # dec:DecisionHolonShape's sh:sparql
    m.remove((EXN.pd, DEC.chosen, EXN.optA))
    m.add((EXN.pd, DEC.chosen, EXN.optRogue))
    outs.append(("chosen-outside-optionSpace [sh:sparql]", m))

    m = _conformant_promotion()                    # iladub:NoLeakShape's sh:sparql
    c = EXN.cand
    m.add((c, RDF.type, ILADUB.CandidateConcept))
    m.add((c, ILADUB.surfaceText, Literal("tonnes")))
    m.add((c, ILADUB.suggestedAnchor, EXN.anchor))
    m.add((c, ILADUB.suggestedBy, EXN.agent))
    m.add((c, ILADUB.confidence, Literal("0.8", datatype=XSD.decimal)))
    m.add((c, ILADUB.fromRegion, EXN.region))
    m.add((c, ILADUB.status, ILADUB.proposed))
    m.add((c, ILADUB.status, ILADUB.asserted))     # a proposition asserted directly
    outs.append(("proposition-also-asserted [sh:sparql]", m))

    m = _conformant_promotion()                    # THE invariant
    m.add((EXN.node, RDF.type, ILADUB.GroundedNode))
    m.add((EXN.node, ILADUB.status, ILADUB.asserted))
    m.add((EXN.node, ILADUB.groundsTo, EXN.concept))
    outs.append(("grounded-node-with-no-promotion", m))

    return outs


@pytest.mark.parametrize("name,graph", _dec_mutations(),
                         ids=[n for n, _ in _dec_mutations()])
def test_both_engines_catch_every_decision_violation(name, graph):
    p, r = _both_dec(graph)
    assert p is False, f"[{name}] fixture precondition: pySHACL must catch it"
    assert r is False, f"[{name}] rudof MISSED a decision violation pySHACL catches"


def test_the_decision_mutation_battery_covers_both_sparql_constraints():
    """A battery that silently lost its sh:sparql legs would still pass on the minCount
    ones and manufacture false confidence in exactly the place the engines can diverge."""
    kinds = {n for n, _ in _dec_mutations()}
    assert sum("sh:sparql" in k for k in kinds) == 2, (
        f"both sh:sparql constraints must be exercised, got {sorted(kinds)}")


# ---------- leg 5: the BLANK-NODE focus, where the engines are NOT equivalent -------------
#
# THE GAP THAT COST THIS LOOP A TASK: legs 1-4 use IRI subjects, and every one of them passes
# under both engines. But the promotion emitters mint BLANK NODES — ground.py:90,145,
# promote.py:67,114,158, splitkey.py:125 — and on a blank-node focus node rudof does not
# disagree with pySHACL, it REFUSES TO ANSWER: it binds $this through `VALUES $this { _:b… }`,
# which is illegal SPARQL, and raises rather than returning a verdict.
#
# MEASURED 2026-08-10: core constraints are unaffected on blank nodes (rudof returns correct
# True/False once the sh:sparql shapes are removed), and BOTH ShaclValidationMode.Native and
# .Sparql raise. That is why compile._validate pins the dec/iladub shapes to pySHACL.
#
# THIS TEST FAILING IS GOOD NEWS. It means rudof learned to evaluate sh:sparql on blank-node
# focus nodes, and `compile._DEC_ENGINE` can stop being pinned.

def _bnode_promotion():
    from rdflib import BNode
    g = Graph()
    pd, cand = BNode(), BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, URIRef("urn:equiv:agent")))
    o1, o2 = BNode(), BNode()
    for o in (o1, o2):
        g.add((o, RDF.type, DEC.Option))
        g.add((pd, DEC.optionSpace, o))
    g.add((pd, DEC.chosen, o1))
    g.add((o2, DEC.rejectedBecause, Literal("the scheme has no member for this value")))
    return g


def test_pyshacl_evaluates_sparql_constraints_on_a_blank_node_focus():
    from iladub.etkl import membrane
    conforms, _ = membrane._validate_pyshacl(_bnode_promotion(), _dec_shapes(), _dec_ont())
    assert conforms is True, "pySHACL must return a VERDICT for a blank-node promotion"


def test_rudof_still_cannot_evaluate_sparql_constraints_on_a_blank_node_focus():
    from iladub.etkl import membrane
    with pytest.raises(ValueError) as exc:
        membrane._validate_rudof(_bnode_promotion(), _dec_shapes(), _dec_ont())
    assert "SHACL" in str(exc.value), str(exc.value)


def test_rudof_handles_a_blank_node_focus_once_the_sparql_shapes_are_gone():
    """Isolates the incapacity to sh:sparql specifically, so the pin cannot be blamed on
    blank nodes in general — core constraints judge a blank-node focus correctly."""
    from iladub.etkl import membrane
    core = _dec_shapes()
    for s, p, o in list(core.triples((None, SH.sparql, None))):
        core.remove((s, p, o))
        for t in list(core.triples((o, None, None))):
            core.remove(t)
    good, _ = membrane._validate_rudof(_bnode_promotion(), core, _dec_ont())
    assert good is True
    bad_graph = _bnode_promotion()
    pd = next(bad_graph.subjects(RDF.type, ILADUB.PromotionDecision))
    for o in list(bad_graph.objects(pd, DEC.optionSpace)):
        bad_graph.remove((pd, DEC.optionSpace, o))
    bad, _ = membrane._validate_rudof(bad_graph, core, _dec_ont())
    assert bad is False, "rudof must still REFUSE an under-furnished blank-node decision"


def test_the_capability_pin_refuses_a_conflicting_forced_engine():
    """The pin outranks ILADUB_MEMBRANE and says so LOUDLY — an operator who forced rudof
    must never be handed pySHACL's verdict unannounced."""
    from iladub.etkl import membrane
    os.environ["ILADUB_MEMBRANE"] = "rudof"
    try:
        with pytest.raises(ValueError, match="capability pin"):
            membrane.validate(_conformant_promotion(), _dec_shapes(), _dec_ont(),
                              engine="pyshacl")
    finally:
        del os.environ["ILADUB_MEMBRANE"]
