"""The vacuity registry — the guard whose absence let R87 be filed as "0 violations".

R87 was a shape wired into a membrane that could not refuse anything. It was closed once,
on the instruction "parse it into the pinned leg", and that instruction was followed and was
insufficient: the shape parsed, targeted 769 focus nodes, and bound zero rows, because
nothing in the pipeline ever wrote the predicates its body joins on. Every oracle in the
repo asked "does this shape refuse when the graph is wrong". None asked "can this shape
refuse at all". This file asks the second question, for every wired shape.

TWO CRITERIA, because either alone is a rubber stamp:

  1. FOCUS NODES. Targets resolved (sh:targetClass / targetSubjectsOf / targetObjectsOf)
     against the SUBCLASS-CLOSED graph — closed because that is the graph the membrane
     actually validates, and `iladub:PromotionDecision rdfs:subClassOf dec:DecisionHolon`
     is exactly the kind of edge that decides whether a shape has focus nodes at all.

  2. TERM REACHABILITY, for shapes carrying sh:sparql. A shape whose body names a term that
     appears NOWHERE in the data cannot fire under any circumstances, however many focus
     nodes it has. This is R87 exactly: `dec:constrainedBy` and `dec:withinScope` were in
     no compiled graph, so no amount of corpus would ever have made the shape speak.

DEVIATION FROM THE PLAN'S WORDING FOR CRITERION 2, and the measurement that forced it.
The plan says criterion 2 is "whether the body's non-negated patterns bind >= 1 row". That
was implemented first and MEASURED WRONG (2026-08-16). For a SHACL sh:sparql constraint the
SELECT returns the VIOLATING nodes, so on a conformant graph a negation-free body binds zero
rows BY DEFINITION. Three shapes — `tab:NoOverlapShape`, `tab:RefinementShape`,
`tab:UnambiguousAccessShape` — bound zero rows while every term in their bodies was present
in the corpus. Registering them would have recorded CONFORMANCE as VACUITY, which is the
opposite of this guard's purpose. Term reachability separates "cannot fire" from "did not
fire"; row-binding does not.

The row counts are still computed and reported by `body_evidence`, as evidence rather than
as the verdict.

WHAT CRITERION 2 DOES NOT CATCH, stated rather than left to be discovered: a shape all of
whose terms are present but whose JOIN can never bind (e.g. requiring one node to be of two
disjoint types). That needs a different technique and would false-positive on a conformant
corpus. R87's class is term-absence, and that is what is guarded here.
"""
import os
import re

import pytest

pytest.importorskip("pdfplumber")

from rdflib import Graph, Namespace, RDF, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES_DIR = os.path.join(ROOT, "vocab", "shapes")

SH = Namespace("http://www.w3.org/ns/shacl#")
TAB = Namespace("https://w3id.org/iladub/tab#")
DEC = Namespace("https://w3id.org/iladub/dec#")
ILADUB = Namespace("https://w3id.org/iladub#")
RISK = Namespace("https://w3id.org/iladub/risk#")

_PREFIX_NS = {
    "tab": str(TAB), "dec": str(DEC), "iladub": str(ILADUB), "risk": str(RISK),
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
}
_TERM = re.compile(r"\b(tab|dec|iladub|risk|rdfs?):([A-Za-z][\w-]*)")

CORPUS = [
    ("cbh-stem", "corpus/ag-trade/cbh-stem-2026-08-03.pdf"),
    ("graincorp-capacity", "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf"),
    ("graincorp-stem", "corpus/ag-trade/graincorp-stem-2026-07-31.pdf"),
    ("apple", "corpus/financial/apple-fy2026q3-statements.pdf"),
    ("bfs", "corpus/gov-stats/bfs-population-bilan-2023.pdf"),
    ("ons", "corpus/gov-stats/ons-index-of-services-2026-02.pdf"),
    ("who-wfa", "corpus/health/who-wfa-boys-zscore-0-5.pdf"),
]


# ==================================================================== THE REGISTRY
#
# A shape idle by EITHER criterion must appear here WITH A MEASURED REASON. The test fails
# when a shape is idle and unregistered, and equally when a registered shape has become
# live — a stale registration is how a guard rots into a rubber stamp.
#
# Focus counts re-measured 2026-08-16 on all 7 corpus documents at `d278a6f`, NOT copied
# from spec §3's M7 table. Two of M7's ten rows (`dec:EventShape`,
# `dec:ExpansionRequestShape`) are deliberately ABSENT: they went live under this loop, and
# registering them would trip the "registered but live" arm immediately.

VACUITY_REGISTRY = {
    ILADUB.GroundedNodeShape: (
        "grounding-scope. Measured 0 focus nodes at compile on all 7 documents; live at "
        "`feed._validate_grounding`, whose graphs `compile_document` never produces. "
        "Correctly idle in THIS membrane."),
    ILADUB.PromotionDecisionShape: (
        "grounding-scope, same as iladub:GroundedNodeShape. Measured 0 focus nodes; the "
        "compile path emits no iladub:PromotionDecision at all."),
    ILADUB.NoLeakShape: (
        "CRITERION 2 ONLY, and the reason this guard has two criteria. Measured 11 focus "
        "nodes (it targets iladub:CandidateConcept, which the compile path does mint) but "
        "`iladub:asserted` appears in NO compiled graph — the status value is written on "
        "the grounding path. Focus-node counting alone pronounces this shape healthy; it "
        "cannot fire. Second shape of R87's own class, found by this file."),
    DEC.MilestoneShape: (
        "transplant/M4 track. Measured 0 focus nodes; the compile path mints no "
        "dec:Milestone. Stays idle under this loop by design (plan G4 forbids asserting "
        "it is live)."),
    TAB.AggregationCellShape: (
        "corpus does not exercise it — measured 0 focus nodes on all 7 documents. RESIDUE: "
        "corpus gap or dead shape, not adjudicated here."),
    TAB.BaseFactShape: (
        "corpus does not exercise it — measured 0 focus nodes on all 7 documents. RESIDUE: "
        "corpus gap or dead shape, not adjudicated here."),
    TAB.LicenceRefusalShape: (
        "idle by BOTH criteria — 0 focus nodes and `tab:licenceRefused` absent from every "
        "compiled graph. SPEC §3's REASON ('corpus does not exercise it') IS WRONG and this "
        "row replaces it: who-wfa DOES refuse a licence, on pair (1,2), and "
        "`DocumentReport.refused_licences` records it. The graph FACT is withheld "
        "DELIBERATELY — `document.py:1246-1253` writes the edge only when both refused "
        "regions asserted a table, because the fact names two table URIs, and its comment "
        "states the asymmetry is intended. So the shape is idle BY DESIGN on this corpus. "
        "RESIDUE: whether a refusal between two ASSERTED tables ever occurs, which is the "
        "only state that would make this shape speak."),
    TAB.PivotedDimensionShape: (
        "corpus does not exercise it — measured 0 focus nodes on all 7 documents. RESIDUE: "
        "corpus gap or dead shape, not adjudicated here."),
    TAB.SectionTotalShape: (
        "corpus does not exercise it — measured 0 focus nodes on all 7 documents. RESIDUE: "
        "corpus gap or dead shape, not adjudicated here."),
}


# ==================================================================== the criteria


def wired_shape_files():
    """The files actually in the compile membrane — read from the membrane, never restated.

    A list retyped here would pin this test's own copy rather than the membrane's, which is
    the failure `test_compile_membrane_shapes.py` exists to prevent.
    """
    from iladub.etkl import compile as compile_mod
    return sorted(set(compile_mod._TAB_SHAPE_FILES) | set(compile_mod._DEC_SHAPE_FILES))


def shapes_graph(files=None):
    g = Graph()
    for f in files if files is not None else wired_shape_files():
        g.parse(os.path.join(SHAPES_DIR, f), format="turtle")
    return g


def node_shapes(sg):
    return sorted(sg.subjects(RDF.type, SH.NodeShape), key=str)


def focus_nodes(data, sg, shape):
    """Criterion 1. `data` must already carry its subclass closure."""
    found = set()
    for o in sg.objects(shape, SH.targetClass):
        found |= set(data.subjects(RDF.type, o))
    for o in sg.objects(shape, SH.targetSubjectsOf):
        found |= set(data.subjects(o, None))
    for o in sg.objects(shape, SH.targetObjectsOf):
        found |= set(data.objects(None, o))
    return found


def body_terms(sg, shape):
    """Every prefixed term named in the shape's sh:sparql bodies."""
    terms = set()
    for c in sg.objects(shape, SH.sparql):
        select = next(sg.objects(c, SH.select), None)
        if select is None:
            continue
        for pfx, local in _TERM.findall(str(select)):
            terms.add(URIRef(_PREFIX_NS[pfx] + local))
    return terms


def vocabulary_of(data):
    """Every term the data graph could match a body pattern against: its predicates, and
    its rdf:type objects (for `?x a tab:Foo` patterns)."""
    return set(data.predicates(None, None)) | set(data.objects(None, RDF.type))


def unreachable_terms(data, sg, shape):
    """Criterion 2. Body terms that appear NOWHERE in the data — a shape naming one cannot
    fire, whatever its focus-node count."""
    return body_terms(sg, shape) - vocabulary_of(data)


def idle_shapes(graphs, sg):
    """{shape: reason} for every shape idle across ALL the given graphs.

    A shape is live if it is live on ANY document: a corpus-wide guard must not call a
    shape idle because one document happens not to exercise it.
    """
    out = {}
    for s in node_shapes(sg):
        max_focus = max(len(focus_nodes(g, sg, s)) for g in graphs)
        if max_focus == 0:
            out[s] = f"criterion 1: 0 focus nodes on every document"
            continue
        if list(sg.objects(s, SH.sparql)):
            unreachable = set.intersection(
                *[unreachable_terms(g, sg, s) for g in graphs]) if graphs else set()
            if unreachable:
                names = ", ".join(sorted(str(t).split("#")[-1] for t in unreachable))
                out[s] = (f"criterion 2: {max_focus} focus nodes, but these body terms "
                          f"appear in no graph: {names}")
    return out


def _match(text, i, open_c, close_c):
    i = text.index(open_c, i)
    depth = 0
    while i < len(text):
        if text[i] == open_c:
            depth += 1
        elif text[i] == close_c:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced group")


def strip_negated(body):
    """Remove NEGATED constraints, leaving the positive pattern.

    `MINUS { ... }` goes as a block. A `FILTER` whose expression involves NOT EXISTS goes
    WHOLE — `tab:InLogicalColumnDisciplineShape` nests one inside a boolean
    (`FILTER( !(sameTerm($this, ?y)) || NOT EXISTS { ... } )`), and excising only the block
    leaves `FILTER( ... || )`, which does not parse. A positive EXISTS is not a negation.
    """
    while True:
        m = re.search(r"\bMINUS\s*\{", body, re.IGNORECASE)
        if m:
            body = body[:m.start()] + body[_match(body, m.start(), "{", "}"):]
            continue
        for fm in re.finditer(r"\bFILTER\b", body, re.IGNORECASE):
            j = fm.end()
            while j < len(body) and body[j].isspace():
                j += 1
            if body.startswith(("NOT", "EXISTS"), j) and "{" in body[j:j + 40]:
                end = _match(body, j, "{", "}")
            else:
                end = _match(body, j, "(", ")")
            if re.search(r"\bNOT\s+EXISTS\b", body[fm.start():end], re.IGNORECASE):
                body = body[:fm.start()] + body[end:]
                break
        else:
            return body


def body_evidence(data, sg, shape, strip=False):
    """Rows the shape's sh:sparql body binds. `None` if it does not parse.

    Reported, not the vacuity verdict — see this module's docstring. TWO readings, and they
    answer different questions:

      strip=False  the body AS WRITTEN. For a SHACL sh:sparql constraint this is the
                   VIOLATION count, so 0 means the graph conforms.
      strip=True   the positive pattern with the negation removed: the CANDIDATES the shape
                   examined and cleared. This is the number that says a shape had something
                   to work on rather than nothing.
    """
    total = 0
    for c in sg.objects(shape, SH.sparql):
        select = next(sg.objects(c, SH.select), None)
        if select is None:
            continue
        text = strip_negated(str(select)) if strip else str(select)
        try:
            total += len(list(data.query(_runnable(sg, text))))
        except Exception:                                    # noqa: BLE001
            return None
    return total


def _prefix_header(sg):
    seen = {}
    for d in set(sg.objects(None, SH.declare)):
        p, ns = next(sg.objects(d, SH.prefix), None), next(sg.objects(d, SH.namespace), None)
        if p is not None and ns is not None:
            seen[str(p)] = str(ns)
    for p, n in _PREFIX_NS.items():
        seen.setdefault(p, n)
    return "\n".join(f"PREFIX {p}: <{n}>" for p, n in sorted(seen.items()))


def _runnable(sg, select):
    return _prefix_header(sg) + "\n" + select.replace("$this", "?this")


# ==================================================================== corpus fixture


@pytest.fixture(scope="module")
def corpus_graphs():
    """The 7 corpus documents, compiled once and subclass-closed. ~5.5 minutes.

    `-m corpus` because of exactly that cost: the plan is explicit that the fast suite must
    not grow a five-minute dependency. Placed beside `test_membrane.py` rather than
    `test_membrane_equiv.py` because the latter skips wholesale without `pyrudof`, which is
    not a core dependency — and the default install is the side that must run this guard.
    """
    from iladub.etkl.document import compile_document
    from iladub.etkl import compile as compile_mod
    from iladub.etkl import membrane

    compile_mod._build_membrane()
    graphs = {}
    for name, rel in CORPUS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            pytest.skip(f"corpus not populated: {rel}")
        rep = compile_document(path)
        graphs[name] = membrane.subclass_closure(rep.graph, compile_mod._FULL_ONT)
    return graphs


# ==================================================================== the guard


@pytest.mark.corpus
def test_every_idle_shape_is_registered(corpus_graphs):
    """A wired shape that cannot speak must be declared, with a measured reason."""
    sg = shapes_graph()
    idle = idle_shapes(list(corpus_graphs.values()), sg)
    unregistered = {s: why for s, why in idle.items() if s not in VACUITY_REGISTRY}
    assert not unregistered, (
        "wired shapes are idle and unregistered — either they are dead, or the corpus "
        "stopped exercising them, and either way it must be recorded:\n"
        + "\n".join(f"  {s} — {why}" for s, why in sorted(unregistered.items(), key=str)))


@pytest.mark.corpus
def test_no_registered_shape_has_gone_live(corpus_graphs):
    """The other arm, and the one that keeps the registry from rotting into a rubber stamp.

    `dec:EventShape` and `dec:ExpansionRequestShape` went live under R87 and are absent from
    the registry for exactly this reason.
    """
    sg = shapes_graph()
    idle = idle_shapes(list(corpus_graphs.values()), sg)
    stale = [s for s in VACUITY_REGISTRY if s not in idle]
    assert not stale, (
        "registered as idle but now LIVE — delete the row and, if it earned one, close its "
        "residue:\n" + "\n".join(f"  {s}" for s in sorted(stale, key=str)))


@pytest.mark.corpus
def test_the_registry_has_no_rows_for_shapes_that_are_not_wired(corpus_graphs):
    """A row naming a shape no membrane carries is bookkeeping about nothing."""
    wired = set(node_shapes(shapes_graph()))
    orphans = [s for s in VACUITY_REGISTRY if s not in wired]
    assert not orphans, f"registry rows for unwired shapes: {orphans}"


@pytest.mark.corpus
def test_the_escalation_shape_is_live_and_binds_the_furnished_escalations(corpus_graphs):
    """R87's own shape, pinned live — the thing this loop existed to achieve.

    Not redundant with the registry tests: they would stay green if
    `dec:EscalationShape` were live for some UNRELATED reason. This pins that its body
    binds exactly the escalations the derivation furnished, per document.
    """
    sg = shapes_graph()
    for name, g in corpus_graphs.items():
        requests = len(set(g.subjects(RDF.type, DEC.ExpansionRequest)))
        candidates = body_evidence(g, sg, DEC.EscalationShape, strip=True)
        violations = body_evidence(g, sg, DEC.EscalationShape)
        assert candidates is not None and violations is not None, \
            f"{name}: dec:EscalationShape's body did not parse"
        # The shape EXAMINED one candidate per furnished escalation...
        assert candidates == requests, (
            f"{name}: the shape's positive pattern binds {candidates} candidate escalations "
            f"but the derivation furnished {requests} expansion requests")
        # ...and CLEARED every one of them. Both halves are needed: candidates alone would
        # pass on a graph the shape refuses, and violations alone is 0 on a shape that
        # never looked at anything — which is R87.
        assert violations == 0, (
            f"{name}: dec:EscalationShape refuses {violations} decisions; the derivation "
            f"furnished an escalation the shape does not accept")
    assert sum(len(set(g.subjects(RDF.type, DEC.ExpansionRequest)))
               for g in corpus_graphs.values()) > 0, \
        "no corpus document furnished anything — this pin is vacuous"


# ==================================================================== T5.1 / O2, offline


def _furnished_graph():
    """A minimal graph in the state Task 3 leaves behind: an escalation decision with the
    three predicates the shape reads, plus the three carried vocabulary triples."""
    from rdflib import Literal
    g = Graph()
    d = URIRef("https://example.org/doc#region0-d0")
    req = URIRef("https://example.org/doc#region0-d0-expansion")
    g.add((d, RDF.type, DEC.DecisionHolon))
    g.add((d, DEC.constrainedBy, RISK.Breach))
    g.add((d, DEC.withinScope, ILADUB.readerScope))
    g.add((d, DEC.escalatedTo, req))
    g.add((ILADUB.readerScope, DEC.maxSeverity, RISK.Watch))
    g.add((RISK.Breach, RISK.order, Literal(2)))
    g.add((RISK.Watch, RISK.order, Literal(1)))
    return g, d


def test_o2_the_guard_catches_r87_itself():
    """T5.1 = O2, and this task's reason for existing.

    Withdraw the furnishing derivation's output while leaving the shape wired — R87's exact
    state — and `dec:EscalationShape` must be reported IDLE. If this passes green with the
    furnishing removed, the guard would have let R87 through again.

    Offline and fast: the criterion is a pure function of (graph, shapes), so O2 does not
    need five minutes of PDF compiling to be pinned.
    """
    sg = shapes_graph()
    furnished, _ = _furnished_graph()
    assert not unreachable_terms(furnished, sg, DEC.EscalationShape), \
        "fixture precondition: the furnished graph must make the shape reachable"
    assert DEC.EscalationShape not in idle_shapes([furnished], sg)

    # R87: the shape is wired, the decision holon is there, and NOTHING furnished it.
    unfurnished = Graph()
    unfurnished.add((next(furnished.subjects(RDF.type, DEC.DecisionHolon)),
                     RDF.type, DEC.DecisionHolon))
    missing = unreachable_terms(unfurnished, sg, DEC.EscalationShape)
    assert DEC.constrainedBy in missing and DEC.withinScope in missing, missing
    assert DEC.EscalationShape in idle_shapes([unfurnished], sg), \
        "the guard did not catch R87 — a wired shape whose body terms are in no graph"


def test_t5_4_criterion_2_sees_what_criterion_1_cannot():
    """T5.4. A shape with MANY focus nodes and an unreachable body term must be caught, and
    criterion 1 alone must NOT catch it — assert both, so that a future simplification
    collapsing the two criteria fails here.

    Pinned on a REAL shape rather than a synthetic one: `iladub:NoLeakShape` has 11 focus
    nodes on the corpus and names `iladub:asserted`, which no compiled graph contains.
    """
    sg = shapes_graph()
    g = Graph()
    for n in range(20):
        g.add((URIRef(f"https://example.org/c{n}"), RDF.type, ILADUB.CandidateConcept))

    assert len(focus_nodes(g, sg, ILADUB.NoLeakShape)) == 20, \
        "criterion 1 must find plenty of focus nodes here"
    assert ILADUB.asserted in unreachable_terms(g, sg, ILADUB.NoLeakShape)
    assert ILADUB.NoLeakShape in idle_shapes([g], sg), \
        "criterion 2 must catch a shape criterion 1 calls healthy"


def test_t5_2_an_idle_unregistered_shape_fails_the_guard():
    """T5.2. A shape with an unsatisfiable target is idle and, being unregistered, must be
    reported by the same function the corpus test asserts on."""
    sg = shapes_graph()
    sg.add((URIRef("urn:test:GhostShape"), RDF.type, SH.NodeShape))
    sg.add((URIRef("urn:test:GhostShape"), SH.targetClass, URIRef("urn:test:NeverMinted")))
    g = Graph()
    g.add((URIRef("urn:test:x"), RDF.type, DEC.DecisionHolon))

    idle = idle_shapes([g], sg)
    assert URIRef("urn:test:GhostShape") in idle
    assert URIRef("urn:test:GhostShape") not in VACUITY_REGISTRY, \
        "the synthetic shape must not be registered, or this test pins nothing"


def test_t5_3_a_registered_shape_that_went_live_fails_the_guard():
    """T5.3. The stale-registration arm. `dec:MilestoneShape` is registered idle; give the
    graph a dec:Milestone and it becomes live, which the guard must notice."""
    sg = shapes_graph()
    g = Graph()
    g.add((URIRef("urn:test:m"), RDF.type, DEC.Milestone))

    assert DEC.MilestoneShape in VACUITY_REGISTRY, "fixture precondition"
    assert DEC.MilestoneShape not in idle_shapes([g], sg), \
        "a registered shape that has become live must not be reported idle"
