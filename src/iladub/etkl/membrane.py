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

from rdflib import Graph


def engine_name() -> str:
    """The engine this process validates with.

    rudof (Rust) is preferred where installed; pySHACL is the fallback AND the escape hatch:
    `ILADUB_MEMBRANE=pyshacl` re-runs any suspect verdict under the reference engine without
    a code change. Correctness is established by tests/etkl/test_membrane_equiv.py, not by
    trust — see spec 2026-08-06 §3.3.
    """
    forced = os.environ.get("ILADUB_MEMBRANE")
    if forced:
        return forced
    return "rudof" if rudof_available() else "pyshacl"


def validate(data_graph: Graph, shapes_graph: Graph, ont_graph: Graph) -> tuple[bool, str]:
    """(conforms, report_text) for `data_graph` against `shapes_graph`.

    Semantics are exactly today's: RDFS inference over data + ontology, SHACL advanced
    features on. Callers must not depend on the report's exact wording — it differs by
    engine; only its content (shape names, focus nodes) is stable.
    """
    if engine_name() == "rudof" and rudof_available():
        return _validate_rudof(data_graph, shapes_graph, ont_graph)
    return _validate_pyshacl(data_graph, shapes_graph, ont_graph)


def _validate_pyshacl(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    from pyshacl import validate as _v
    conforms, _, text = _v(data_graph, shacl_graph=shapes_graph, ont_graph=ont_graph,
                           inference="rdfs", advanced=True)
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
    """True only when the serialized SHACL report contains a bare `sh:conforms true`.

    Fails closed: an empty, malformed, or otherwise unparseable report never reads as
    conformance — it simply doesn't contain the substring, so this returns False."""
    return "sh:conforms true" in " ".join(report.split())


def _validate_rudof(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    """rudof does NO inference of its own — rdfs_closure supplies the expanded graph, and
    its literal-subject filter is what makes the payload parseable by rudof's strict reader."""
    import pyrudof
    expanded = rdfs_closure(data_graph, ont_graph)
    r = _rudof_instance(shapes_graph)
    r.reset_data()
    r.read_data(expanded.serialize(format="nt"), format=pyrudof.RDFFormat.NTriples)
    r.validate_shacl(mode=pyrudof.ShaclValidationMode.Native)
    report = str(r.serialize_shacl_validation_results(
        pyrudof.ResultShaclValidationFormat.Turtle))
    return _conforms_from_report(report), report


def rdfs_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """A NEW graph: data + ontology axioms, RDFS-expanded, minus every literal-subject triple.

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
    """
    from pyshacl.rdfutil.inoculate import inoculate
    from rdflib import Literal as _Literal
    import owlrl
    merged = Graph()
    merged += data_graph
    inoculate(merged, ont_graph)
    owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(merged)
    out = Graph()
    for s, p, o in merged:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    return out
