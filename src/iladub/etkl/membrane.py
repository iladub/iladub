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
    """The engine this process validates with. `ILADUB_MEMBRANE` selects it."""
    return os.environ.get("ILADUB_MEMBRANE", "pyshacl")


def validate(data_graph: Graph, shapes_graph: Graph, ont_graph: Graph) -> tuple[bool, str]:
    """(conforms, report_text) for `data_graph` against `shapes_graph`.

    Semantics are exactly today's: RDFS inference over data + ontology, SHACL advanced
    features on. Callers must not depend on the report's exact wording — it differs by
    engine; only its content (shape names, focus nodes) is stable.
    """
    return _validate_pyshacl(data_graph, shapes_graph, ont_graph)


def _validate_pyshacl(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    from pyshacl import validate as _v
    conforms, _, text = _v(data_graph, shacl_graph=shapes_graph, ont_graph=ont_graph,
                           inference="rdfs", advanced=True)
    return bool(conforms), text


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
