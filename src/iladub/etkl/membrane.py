"""membrane — the ONE place any SHACL validation runs (spec 2026-08-06).

Both closed-world membranes (tiling.region_tiles' per-region gate and compile._validate's
whole-graph pass) call this seam. They keep their DISTINCT shape sets — that distinction is
semantic (intra-region vs whole-graph) and is not this module's business.

Gate classification (CLAUDE.md §8): PROCEDURAL engine glue only. No decision lives here —
the decisions are the SHACL shapes. Irreducible: a validator must be invoked from somewhere,
and the invocation carries no domain decision.
"""
from __future__ import annotations

import os

from rdflib import Graph, RDF


def engine_name() -> str:
    """The engine this process validates with.

    rudof (Rust) is preferred where installed; pySHACL is the fallback AND the escape hatch:
    `ILADUB_MEMBRANE=pyshacl` re-runs any suspect verdict under the reference engine without
    a code change. Correctness is established by tests/etkl/test_membrane_equiv.py, not by
    trust — see spec 2026-08-06 §3.3.

    Fails LOUD, not silent: an `ILADUB_MEMBRANE` value that names neither engine is a
    misconfiguration, not a silent fallback — and forcing `rudof` on a process where
    `pyrudof` isn't importable must not quietly resolve to pySHACL, or an operator who
    thinks they forced the new engine has actually re-run the old one unnoticed.
    """
    forced = os.environ.get("ILADUB_MEMBRANE")
    if forced:
        if forced not in ("pyshacl", "rudof"):
            raise ValueError(
                f"ILADUB_MEMBRANE={forced!r} is not a known engine (expected 'pyshacl' or "
                f"'rudof')")
        if forced == "rudof" and not rudof_available():
            raise ValueError(
                "ILADUB_MEMBRANE=rudof was forced but pyrudof is not installed")
        return forced
    return "rudof" if rudof_available() else "pyshacl"


def validate(data_graph: Graph, shapes_graph: Graph, ont_graph: Graph,
             engine: str | None = None) -> tuple[bool, str]:
    """(conforms, report_text) for `data_graph` against `shapes_graph`.

    Both engines now validate the SAME subclass-only-closed graph (spec
    2026-08-06-subclass-only-closure-design.md): the seam expands `data_graph` with
    `subclass_closure` and hands each engine its own inference turned OFF, so the engine is
    the only variable — `ILADUB_MEMBRANE=pyshacl` isolates the engine, as intended, rather
    than also swapping the inference semantics underneath it. SHACL advanced features on.
    Callers must not depend on the report's exact wording — it differs by engine; only its
    content (shape names, focus nodes) is stable.

    `engine` is a CAPABILITY PIN, not a preference, and it is the one thing that outranks
    `ILADUB_MEMBRANE`. MEASURED 2026-08-10: rudof cannot evaluate an `sh:sparql` constraint
    whose focus node is a blank node — it binds `$this` through `VALUES $this { _:b… }`,
    which is illegal SPARQL, and raises `ValueError: … expected UNDEF` instead of returning
    a verdict. Core constraints are unaffected on blank nodes; both
    `ShaclValidationMode.Native` and `.Sparql` raise it. `dec-shapes.ttl:23` and
    `iladub-shapes.ttl:67` are exactly such constraints, and the promotion emitters mint
    blank-node subjects (`ground.py:90,145`, `promote.py:67,114,158`, `splitkey.py:125`), so
    a caller validating those shapes MUST pin pySHACL or the membrane throws.

    The env var still selects among engines that CAN evaluate a shape set; it cannot conjure
    a capability rudof lacks. Forcing `rudof` at a pinned call therefore RAISES rather than
    quietly running pySHACL — an operator who thinks they forced the new engine must never
    be handed the old one's verdict unannounced (the same rule `engine_name` already keeps).
    """
    if engine is None:
        engine = engine_name()
    else:
        if engine not in ("pyshacl", "rudof"):
            raise ValueError(
                f"engine={engine!r} is not a known engine (expected 'pyshacl' or 'rudof')")
        forced = os.environ.get("ILADUB_MEMBRANE")
        if forced and forced != engine:
            raise ValueError(
                f"ILADUB_MEMBRANE={forced!r} conflicts with a capability pin of {engine!r} on "
                f"this shape set. The pin is not a preference: see this function's docstring "
                f"for the measured incapacity it works around.")
    if engine == "rudof":
        return _validate_rudof(data_graph, shapes_graph, ont_graph)
    return _validate_pyshacl(data_graph, shapes_graph, ont_graph)


def _validate_pyshacl(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    """pySHACL's own inference is OFF (`inference="none"`): the seam supplies the SAME
    subclass-only closure `_validate_rudof` uses, via `subclass_closure`, so this path no
    longer materialises domain/range typing either (R19's mechanism — see
    `subclass_closure`'s docstring). Before this, `_validate_pyshacl` was the ONLY path that
    still ran full RDFS inference (`inference="rdfs"`), so any install without `pyrudof` (core
    and `[etkl]` installs both lack it) kept R19 alive under a different name."""
    from pyshacl import validate as _v
    expanded = subclass_closure(data_graph, ont_graph)
    conforms, _, text = _v(expanded, shacl_graph=shapes_graph, inference="none", advanced=True)
    return bool(conforms), text


_RUDOF = None          # persistent instance: shapes parse ONCE (0.02 s), data resets per call


def rudof_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("pyrudof") is not None


def _rudof_instance(shapes_graph):
    """One instance per process, keyed by the shapes graph's identity — the two call sites
    use DIFFERENT shape sets, so a single cached instance would validate against the wrong
    one. Shapes parsing is 0.02 s; data loading (0.58 s on an 8k-triple page) dominates and
    is per-call regardless.

    The cache holds a STRONG reference to `shapes_graph` deliberately, compared with `is`:
    an id()-only key is unsafe because CPython reuses object ids after garbage collection, so
    a freed shapes graph's address could later be handed to an unrelated Graph, silently
    matching the stale cache entry and validating against the wrong shape set with no error.
    That the two production call sites (`compile._FULL_SHAPES`, `tiling._TILING_SHAPES`)
    happen to hold process-lifetime singletons is not a guarantee a future caller inherits —
    keeping the graph alive here removes the hazard regardless of caller lifetime."""
    global _RUDOF
    import pyrudof
    if _RUDOF is None or _RUDOF[0] is not shapes_graph:
        r = pyrudof.Rudof(pyrudof.RudofConfig())
        r.read_shacl(shapes_graph.serialize(format="turtle"), format=pyrudof.ShaclFormat.Turtle)
        _RUDOF = (shapes_graph, r)
    return _RUDOF[1]


def _conforms_from_report(report: str) -> bool:
    """The verdict, read as RDF rather than matched as text.

    A substring test over the report is unsound: rudof echoes offending literal values into
    sh:value, so a graph containing the token would flip the verdict — measured, a violating
    graph read as conforming. Fails CLOSED: an unparseable or ambiguous report is never
    conformance.
    """
    from rdflib import Graph as _Graph, Literal as _Literal
    from rdflib.namespace import SH
    try:
        g = _Graph().parse(data=report, format="turtle")
    except Exception:
        return False
    vals = list(g.objects(None, SH.conforms))
    return len(vals) == 1 and vals[0] == _Literal(True)


def _validate_rudof(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    """rudof does NO inference of its own — the seam now supplies a SUBCLASS-ONLY closure
    (spec 2026-08-06-subclass-only-closure-design.md), not the old full RDFS closure:
    domain/range typing is gone by design (the R19 mechanism), and its literal-subject filter
    is what makes the payload parseable by rudof's strict reader."""
    import pyrudof
    expanded = subclass_closure(data_graph, ont_graph)
    r = _rudof_instance(shapes_graph)
    r.reset_data()
    r.read_data(expanded.serialize(format="nt"), format=pyrudof.RDFFormat.NTriples)
    r.validate_shacl(mode=pyrudof.ShaclValidationMode.Native)
    report = str(r.serialize_shacl_validation_results(
        pyrudof.ResultShaclValidationFormat.Turtle))
    return _conforms_from_report(report), report


def rdfs_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """SUPERSEDED for production (spec 2026-08-06-subclass-only-closure-design.md): the seam now
    calls `subclass_closure`. This function is RETAINED as the reference implementation the
    closure differential (tests/etkl/test_closure_equiv.py) compares against — it is what
    pySHACL's `inference="rdfs"` produces, so it is the baseline any claim of "no verdict
    changed" must be measured against. Not called in production.

    A NEW graph: data + ontology axioms, RDFS-expanded, minus every literal-subject triple.

    Reproduces exactly what pySHACL's `inference="rdfs"` does today — subclass closure AND
    domain/range typing (the latter is the R19 mechanism, deliberately preserved here; the
    successor loop, spec 2026-08-06 §7, is where dropping it is argued and measured).

    The ontology is mixed in via pySHACL's own `inoculate()` (the RDFS/OWL axiom whitelist:
    classes and properties typed/predicated as RDFS or OWL vocabulary), NOT a full graph
    union. `Validator.mix_in_ontology()` uses `inoculate()` by default (`PYSHACL_USE_FULL_MIXIN`
    is unset in this repo), so a full union would inject ontology content — arbitrary
    non-axiom triples the ontology graph happens to carry — that pySHACL never puts in the
    validated graph. That mismatch would make the Task 4 engine differential compare two
    different graphs, not two engines on the same graph. Calling pySHACL's function (rather
    than re-implementing the whitelist by hand) guarantees the match and tracks upstream.

    The literal-subject filter is NOT optional: owlrl's closure emits triples whose subject
    is a Literal (`"307.47"^^xsd:decimal rdf:type rdfs:Resource`), which is illegal RDF.
    rdflib tolerates them; a strict parser rejects the whole graph. They are semantically
    vacuous, so dropping them changes no verdict.

    The RDFS semantics class is pySHACL's own `CustomRDFSSemantics`, NOT plain
    `owlrl.RDFS_Semantics`. Plain `RDFS_Semantics` runs owlrl's `one_time_rules()`, which
    does literal VALUE-SPACE unification and fabricates triples: measured on the
    test_row_groups fixture, a cell with `tab:onPage "0"^^xsd:integer` came out of closure
    ALSO carrying a fabricated `"0.0"^^xsd:decimal` twin, invented from an unrelated
    xsd:decimal elsewhere in the graph because 0 and 0.0 are the same value. That fabricated
    literal then fails `sh:datatype xsd:integer` — rudof would refuse a graph pySHACL admits.
    pySHACL avoids this itself (`pyshacl/inference/custom_rdfs_closure.py`: `CustomRDFSSemantics`
    overrides `one_time_rules()` to a no-op, with the docstring "These rules usually add
    'hidden' literals to the graph in such a way that breaks some SHACL validation tests").
    We reuse pySHACL's own class rather than re-suppressing the rule by hand, for the same
    reason as the `inoculate` mix-in above: the two engines must validate the same graph.
    """
    from pyshacl.inference.custom_rdfs_closure import CustomRDFSSemantics
    from pyshacl.rdfutil.inoculate import inoculate
    from rdflib import Literal as _Literal
    import owlrl
    merged = Graph()
    merged += data_graph
    inoculate(merged, ont_graph)
    owlrl.DeductiveClosure(CustomRDFSSemantics).expand(merged)
    out = Graph()
    for s, p, o in merged:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    return out


def subclass_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """A NEW graph: the data plus its own rdfs:subClassOf type closure. Nothing else.

    The ontology is READ for its `rdfs:subClassOf` axioms and never mixed in, so no ontology
    node can become a focus node and the validated graph is data plus its type closure.
    Axioms are sourced from `ont_graph` ONLY: any `rdfs:subClassOf` triple appearing in
    `data_graph` itself is copied through into the output (it is ordinary data, like any other
    triple) but is never consulted for materialisation — inert today, since nothing under
    `src/iladub/` emits `rdfs:subClassOf` into a data graph.

    WHAT THIS DELIBERATELY DOES NOT DO (spec 2026-08-06-subclass-only-closure-design.md):
    domain/range typing. A node no longer becomes a `tab:Cell` merely by carrying
    `tab:hasBBox` — that inference is the R19 accident, and dropping it closes that hazard at
    its root. Measured on the real stem page: the only typings lost are 2,105 vacuous
    `rdfs:Resource`, 207 ontology-node types, and 18 `tab:LabelCell` — and NO shape targets
    `tab:LabelCell`, so no verdict changes. Consequence to know: `sh:class tab:BBox` becomes
    FALSIFIABLE again, because `tab:hasBBox`'s range no longer types its object regardless
    (all 586 bbox objects on the real page are explicitly typed, so nothing relied on it).

    The literal-subject filter is an INVARIANT GUARD here, not a repair: no code path in this
    function can emit a literal-subject triple (unlike owlrl's closure, which emitted 1,533).

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue — a transitive closure over
    declared axioms. No domain decision, no tuned constant.
    """
    from rdflib import Literal as _Literal
    from rdflib.namespace import RDFS

    supers: dict = {}
    for a, _, b in ont_graph.triples((None, RDFS.subClassOf, None)):
        supers.setdefault(a, set()).add(b)
    changed = True                       # transitive closure over the axioms, computed once
    while changed:
        changed = False
        for a in list(supers):
            for b in list(supers[a]):
                for c in supers.get(b, ()):
                    if c not in supers[a]:
                        supers[a].add(c)
                        changed = True

    out = Graph()
    for s, p, o in data_graph:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    for s, _, cls in data_graph.triples((None, RDF.type, None)):
        if isinstance(s, _Literal):
            continue
        for c in supers.get(cls, ()):
            out.add((s, RDF.type, c))
    return out
