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
