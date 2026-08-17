"""The compile membrane validates the DECISION graph too (R82, spec 2026-08-10 §5.4).

`compile._validate` was the contract membrane for the tab graph only: `_FULL_SHAPES` held
`tab-shapes.ttl` + `tab-physical-shapes.ttl`, so a page could carry an `iladub:PromotionDecision`
with no deliberated option space and cross the membrane unchallenged. iladub's differentiator
claim — every grounded node is the product of an accountable promotion decision — is only a
claim until the membrane enforces it.

Two assertions, and the SECOND is the one that matters: (a) alone would pass if the shapes
were parsed into the membrane and then never applied to anything.
"""
import os

import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SH

ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES_DIR = os.path.join(ROOT, "vocab", "shapes")


def _built_membrane():
    """The membrane as `_validate` actually builds it — populated by calling it, never by
    re-reading the file list here. A test that rebuilt the set from its own list would pin
    its own copy rather than the membrane."""
    from iladub.etkl import compile as compile_mod
    # One triple, not an empty graph: rudof raises "The provided input is empty" on a
    # zero-triple data graph, which would fail this test for a reason that has nothing to
    # do with the membrane's shape set.
    seed = Graph()
    seed.add((URIRef("urn:test:seed"), RDF.type, RDFS.Resource))
    compile_mod._validate(seed)             # force the lazy build
    return compile_mod


def _declared_node_shapes(f):
    return set(Graph().parse(os.path.join(SHAPES_DIR, f), format="turtle")
               .subjects(RDF.type, SH.NodeShape))


def test_the_membrane_carries_every_shape_file_in_its_leg():
    """(a) The membrane's shape set is pinned by the FILES, not by a comment — and so is the
    leg each file lands in. The split is not cosmetic: the two legs are two different
    closed-world membranes (the tab graph and the decision graph), and a shape file that
    silently dropped out of its leg would stop being applied to anything at all.

    The legs are no longer split by ENGINE. `_DEC_ENGINE = "pyshacl"` used to live beside
    `_DEC_SHAPE_FILES` and was asserted here, because rudof raises on the sh:sparql
    constraints these two files carry when the focus node is a blank node. `membrane._payload`
    now skolemizes, so no blank-node focus node reaches an engine and the constant is gone
    (spec 2026-08-13-membrane-parity-design.md §4.3). The upstream rudof incapacity is still
    pinned — directly against `pyrudof`, in tests/etkl/test_membrane_equiv.py."""
    m = _built_membrane()
    for leg, files in ((m._TAB_SHAPES, m._TAB_SHAPE_FILES),
                       (m._DEC_SHAPES, m._DEC_SHAPE_FILES)):
        present = set(leg.subjects(RDF.type, SH.NodeShape))
        for f in files:
            declared = _declared_node_shapes(f)
            assert declared, f"fixture precondition: {f} declares no sh:NodeShape"
            assert not declared - present, f"{f} is not in its membrane leg"
    # `escalation-shapes.ttl` joined the DEC leg in R87 Task 4 (`0074144`). Updating this
    # tuple is the ONLY way a shape file may enter or leave a membrane — that is what the
    # exact-equality pin is for, and it caught this change on the fast suite before anything
    # else did. The loop above independently confirms the file's shapes are actually IN the
    # leg, so this line records a deliberate membrane change rather than admitting one.
    assert m._DEC_SHAPE_FILES == ("dec-shapes.ttl", "iladub-shapes.ttl",
                                  "escalation-shapes.ttl")
    assert not hasattr(m, "_DEC_ENGINE"), (
        "the capability pin is gone (R88): the decision leg must run on the process engine, "
        "not on a hard-coded one")


def test_the_decision_leg_is_load_bearing_for_a_blank_node_promotion():
    """Not paperwork. A promotion decision whose subject is a BLANK NODE — which is what
    `ground.py`, `promote.py` and `splitkey.py` actually mint — must cross the membrane
    without the engine throwing, on WHICHEVER engine this process selected. Before the
    skolemize step this passed only because the leg was pinned to pySHACL."""
    from iladub.etkl import compile as compile_mod
    from rdflib import BNode
    g = Graph()
    pd, cand = BNode(), BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, URIRef("urn:test:agent")))
    opts = (BNode(), BNode())
    for o in opts:
        g.add((o, RDF.type, DEC.Option))
        g.add((pd, DEC.optionSpace, o))
    g.add((pd, DEC.chosen, opts[0]))
    g.add((opts[1], DEC.rejectedBecause, Literal("the scheme admits the value")))
    conforms, report = compile_mod._validate(g)     # must not raise
    assert conforms is True, report


def _under_furnished_promotion():
    """A promotion decision that SATISFIES `iladub:PromotionDecisionShape` (it reviews a
    candidate and names an agent) and violates ONLY `dec:DecisionHolonShape` — no option
    space, no chosen option.

    That split is deliberate. If this node also violated the iladub-targeted shape, the test
    would pass with `iladub.ttl` absent from `_FULL_ONT`, and the subclass axiom
    `iladub:PromotionDecision rdfs:subClassOf dec:DecisionHolon` — the line that makes the
    dec shapes target anything at all — would be untested decoration."""
    g = Graph()
    pd = URIRef("urn:test:pd")
    cand = URIRef("urn:test:candidate")
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, URIRef("urn:test:agent")))
    g.add((pd, DEC.rationale, Literal("it looked right")))
    g.add((cand, RDF.type, RDFS.Resource))
    return g


def test_the_membrane_refuses_an_undeliberated_promotion():
    """(b) THE ASSERTION THAT MATTERS. A promotion decision with no deliberated option space
    is not an accountable decision, and the compile membrane must refuse it."""
    from iladub.etkl import compile as compile_mod
    conforms, report = compile_mod._validate(_under_furnished_promotion())
    assert conforms is False, (
        "the compile membrane ADMITTED a promotion decision with no dec:optionSpace and no "
        "dec:chosen — the promotion-epistemics claim is unenforced at this membrane\n" + report)


def test_the_membrane_admits_a_well_furnished_promotion():
    """The positive leg: the refusal above must be about the missing deliberation, not about
    `iladub:PromotionDecision` being unable to pass the membrane at all."""
    from iladub.etkl import compile as compile_mod
    g = _under_furnished_promotion()
    pd = URIRef("urn:test:pd")
    for local, chosen in (("opt-ground", True), ("opt-quarantine", False)):
        o = URIRef("urn:test:" + local)
        g.add((o, RDF.type, DEC.Option))
        g.add((o, RDFS.label, Literal(local)))
        g.add((pd, DEC.optionSpace, o))
        if chosen:
            g.add((pd, DEC.chosen, o))
        else:
            g.add((o, DEC.rejectedBecause, Literal("the scheme admits the value")))
    conforms, report = compile_mod._validate(g)
    assert conforms is True, report
