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
import re

import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SH

ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
TAB = Namespace("https://w3id.org/iladub/tab#")

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
    conforms, report, legs = compile_mod._validate(g)     # must not raise
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
    conforms, report, legs = compile_mod._validate(_under_furnished_promotion())
    assert conforms is False, (
        "the compile membrane ADMITTED a promotion decision with no dec:optionSpace and no "
        "dec:chosen — the promotion-epistemics claim is unenforced at this membrane\n" + report)


def test_a_dec_leg_refusal_names_dec_and_not_tab():
    """O4. The message a diagnosing reader sees must send them to the vocabulary that actually
    refused. Asserting the ABSENCE of `tab` is the half that matters: a test checking only that
    `dec` is named passes when the message names both."""
    from iladub.etkl import compile as compile_mod
    conforms, report, legs = compile_mod._validate(_under_furnished_promotion())
    assert conforms is False, report
    assert legs == ("dec",), f"the refusing leg was mislabelled: {legs}"
    assert "tab" not in legs


def _bad_unit_marker():
    """A `tab:UnitMarker` with no `tab:markerRegion` — violates `UnitMarkerShape`'s MinCount(1)
    and NOTHING else (no other tab shape targets a bare UnitMarker with only `markerSymbol`).
    Confirmed by direct call: `compile_mod._validate` on this graph alone returns
    `(False, ..., ("tab",))` — the identical fixture `test_membrane.py`'s
    `test_membrane_catches_a_core_violation` already uses against `membrane.validate` directly,
    reused here against the compile-level `_validate` instead."""
    g = Graph()
    um = URIRef("urn:t:um")
    g.add((um, RDF.type, TAB.UnitMarker))
    g.add((um, TAB.markerSymbol, Literal("$")))
    return g


def test_a_both_legs_refusal_names_both():
    """I-D's other direction: a graph that violates BOTH legs must name both, so the label fix
    cannot become a mislabel the other way (a message that always said "dec" would pass T1a's
    negative half by accident if it also always omitted "tab").

    Setup NOT verified reusable as a single cross-file import: `test_closure_equiv.py`'s
    `_bad_bbox_graph()` does refuse through `compile._validate` on the tab leg alone (checked
    directly), but importing one test module from another in this tree fails under the
    project's default pytest invocation (`tests/etkl` carries no `__init__.py` and is not on
    `sys.path` — MEASURED: `from test_closure_equiv import _bad_bbox_graph` raises
    `ModuleNotFoundError` when run via `pytest tests/etkl/...`, even in isolation). So the tab
    half is constructed fresh here instead, minimal and local: `_bad_unit_marker()` above fails
    `UnitMarkerShape`'s MinCount(1) on `tab:markerRegion` — confirmed refusing through
    `compile._validate` with `legs == ("tab",)` alone. The dec half reuses
    `_under_furnished_promotion()`, already used by the two tests above. Their union violates
    both legs independently."""
    from iladub.etkl import compile as compile_mod
    g = _bad_unit_marker() + _under_furnished_promotion()
    conforms, report, legs = compile_mod._validate(g)
    assert conforms is False, report
    assert legs == ("tab", "dec"), f"expected both legs to refuse, got: {legs}"
    assert "tab" in report and "dec" in report


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
    conforms, report, legs = compile_mod._validate(g)
    assert conforms is True, report


def test_refusal_message_names_exactly_the_failing_legs():
    """I-D, pure-function form (no PDF, no corpus — see the module docstring's rationale for
    why the raise message is tested through a helper rather than end-to-end). For each leg
    combination the message must name every failing leg and no other, and must keep the
    caller's own subject noun so a future refactor cannot quietly drop it."""
    from iladub.etkl.compile import _refusal_message
    msg = _refusal_message("asserted holon", ("dec",), "…")
    assert "asserted holon" in msg
    assert "dec" in msg
    assert "tab" not in msg

    msg = _refusal_message("asserted holon", ("tab",), "…")
    assert "asserted holon" in msg
    assert "tab" in msg
    assert "dec" not in msg

    msg = _refusal_message("document-level facts", ("tab", "dec"), "…")
    assert "document-level facts" in msg
    assert "tab" in msg
    assert "dec" in msg


def test_neither_raise_site_hardcodes_a_leg_name():
    """Structural pin, in the style of `test_membrane.py`'s `test_call_sites_use_the_seam`:
    the two functions that raise on a membrane refusal — `compile.compile_tables` (raises at
    `compile.py:1103`) and `document.compile_document` (raises at `document.py:1587`) — must
    build their raise message from `_validate`'s own reported legs, not from the literal
    string that named the tab leg before this change.

    Pinned as the exact old f-string fragment (`"failed tab: SHACL:"`), not the bare substring
    `"tab: SHACL"`: `document.py:1299` carries an unrelated EXPLANATORY COMMENT — "fails the
    tab: SHACL membrane" — that legitimately survives this change (it is prose about the
    membrane, not a hardcoded raise message) and would false-positive a broader substring
    check. MEASURED: `grep -n "tab: SHACL" src/iladub/etkl/document.py` returns exactly that
    one comment line once the raise site itself is fixed."""
    import inspect
    from iladub.etkl import compile as compile_mod
    from iladub.etkl import document as document_mod
    assert "failed tab: SHACL:" not in inspect.getsource(compile_mod.compile_tables)
    assert "failed tab: SHACL:" not in inspect.getsource(document_mod.compile_document)


# --------------------------------------------------------------------------------------
# R103, decided 2026-08-20: `tab-datagrid.ttl` stays OUT of `_FULL_ONT`.
#
# The decision rests on a condition that can rot, so it is pinned here rather than left in a
# comment. `subclass_closure` (membrane.py:448) reads ONLY `rdfs:subClassOf` from the ontology
# graph, so adding a file to `_FULL_ONT` can affect a verdict by exactly one mechanism: an
# axiom `Sub ⊑ Super` materialising `Super` on a node typed `Sub`, where some shape can reach
# `Super`. `tab-datagrid.ttl` introduces three such superclasses and NO shape reaches any of
# them, which is why admitting the file is a provable no-op (MEASURED: 27 corpus pages, closure
# delta 0 triples, every verdict identical — see the R103 row).
#
# If a shape ever targets `tab:DataGrid`, `tab:ColumnUniverse` or `tab:SuppressedRepeat`, the
# no-op argument dies and R103 has to be reopened. That is what this test says out loud.
# --------------------------------------------------------------------------------------

def _shape_reachable_classes():
    """Every class a membrane shape can reach: `sh:targetClass` plus `sh:class` value-type
    constraints, over BOTH shape sets the compile membrane actually builds."""
    compile_mod = _built_membrane()
    reached = set()
    for g in (compile_mod._TAB_SHAPES, compile_mod._DEC_SHAPES):
        reached |= set(g.objects(None, SH.targetClass))
        reached |= set(g.objects(None, SH["class"]))
    return reached


def test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape():
    """R103's decision condition. Read the ADDED superclasses out of the file itself — never
    from a hardcoded list here, or the test pins its own copy of the vocabulary instead of the
    vocabulary (the `_built_membrane` lesson, above)."""
    ont_dir = os.path.join(ROOT, "vocab", "ontology")
    dg = Graph().parse(os.path.join(ont_dir, "tab-datagrid.ttl"), format="turtle")
    base = Graph()
    for f in ("tab.ttl", "dec.ttl", "iladub.ttl"):
        base.parse(os.path.join(ont_dir, f), format="turtle")

    added = set(dg.triples((None, RDFS.subClassOf, None))) - set(
        base.triples((None, RDFS.subClassOf, None)))
    assert added, "tab-datagrid.ttl declares no subClassOf axioms — the premise changed"

    supers = {sup for _sub, _p, sup in added}
    reachable = _shape_reachable_classes()
    collide = supers & reachable
    assert not collide, (
        "a membrane shape now reaches a superclass tab-datagrid.ttl introduces "
        f"({sorted(str(c) for c in collide)}) — admitting the file is no longer a no-op. "
        "REOPEN R103 and re-run the 27-page closure-delta measurement.")


# ============================================================ R152: the transport premise

_BLANK_NODE_SPARQL = re.compile(r"\b(isBlank|isIRI|isURI|BNODE)\s*\(", re.I)


def membrane_shape_files():
    """Every shape file that reaches `membrane._payload_nt`, read from the modules that wire
    it — never a list retyped here, which would pin this test's copy rather than the membrane's.

    THREE legs call `membrane.validate`, and all three are skolemized by the same
    `_payload_nt`, so the premise below is about all of them and not only the compile leg:
    `compile.py:546` (tab + dec), `feed.py:615` (grounding), `tiling.py:70`. Tiling adds no
    FILE — `_build_tiling_shapes` takes CBDs out of `tab-shapes.ttl` + `tab-physical-shapes.ttl`,
    both already wired into the compile leg — so it is covered by inclusion. That is asserted
    by `test_the_tiling_leg_adds_no_shape_file_of_its_own`, not assumed here.
    """
    from iladub import feed
    from iladub.etkl import compile as compile_mod
    return sorted(set(compile_mod._TAB_SHAPE_FILES) | set(compile_mod._DEC_SHAPE_FILES)
                  | set(feed._GROUND_SHAPE_FILES))


def _sparql_bodies(g):
    """Every SPARQL text a shape carries — constraints (`sh:select`, `sh:ask`) and rules
    (`sh:construct`). All three are strings an engine runs, none reachable as triples."""
    for p in (SH.select, SH.ask, SH.construct):
        for o in g.objects(None, p):
            yield str(p), str(o)


def test_the_tiling_leg_adds_no_shape_file_of_its_own():
    """`membrane_shape_files` claims tiling is covered by inclusion; this measures it.

    `tiling._build_tiling_shapes` extracts CBDs from two files rather than naming a file list
    of its own, so the claim cannot be checked by comparing tuples — it is checked by the
    shapes it produces all being declared in files the compile leg already carries.
    """
    from iladub.etkl import tiling
    declared = set()
    for f in membrane_shape_files():
        declared |= _declared_node_shapes(f)
    tiling_shapes = set(tiling._TILING_SHAPES.subjects(RDF.type, SH.NodeShape))
    assert tiling_shapes and tiling_shapes <= declared, (
        f"the tiling leg carries shapes no membrane-wired file declares: "
        f"{sorted(tiling_shapes - declared, key=str)} — R152's premise guard does not cover "
        f"them, so give tiling its own arm rather than widening this claim")


@pytest.mark.parametrize("shape_file", membrane_shape_files())
def test_no_membrane_shape_can_see_the_skolemization(shape_file):
    """`_payload_nt`'s premise, machine-checked — R152.

    `membrane._payload_nt` SKOLEMIZES the data graph before either engine sees it (R88's
    unpin: rudof cannot bind a blank-node focus — it emits `VALUES $this { _:b… }`, which is
    illegal SPARQL). Skolemization is declared a TRANSPORT concern, and `membrane.py:342-343`
    states the premise that makes it verdict-neutral: *no shape file uses `sh:nodeKind` and no
    `sh:sparql` body tests `isBlank`/`isIRI`/`isURI`/`BNODE`.* **Nothing enforced that**, and it
    is a claim about the SHAPES, held only by nobody having written one.

    The day someone does, they get a constraint that is VACUOUS at the compile membrane by
    construction — every blank node has already become an IRI — while refusing correctly at
    `iladub.validate.validate`, the seam the vocabulary examples are tested at. The two seams
    disagree silently, in the PERMISSIVE direction, and the shape looks enforced. Measured on
    `tests/supersession-blank-object.ttl` while closing R128: same shapes, same data,
    `pyshacl_rdfs=False membrane=True`.

    **This does NOT make `sh:nodeKind` work at the membrane** — that is R88's territory and
    would need the rudof blank-node incapacity re-measured first. It fails at the moment the
    hazard comes into existence, which is the moment someone writes the constraint.
    """
    g = Graph().parse(os.path.join(SHAPES_DIR, shape_file), format="turtle")

    carriers = sorted(g.subjects(SH.nodeKind, None), key=str)
    assert carriers == [], (
        f"{shape_file} uses sh:nodeKind on {carriers} — VACUOUS at the compile membrane, "
        f"which skolemizes before any engine runs (membrane._payload_nt), while refusing "
        f"correctly at iladub.validate.validate. See R152 before shipping it")

    blank_aware = [(p, body) for p, body in _sparql_bodies(g)
                   if _BLANK_NODE_SPARQL.search(body)]
    assert blank_aware == [], (
        f"{shape_file} has a SPARQL body testing blank-node-ness; the membrane skolemizes "
        f"first, so it can never fire there. See R152: {blank_aware}")
