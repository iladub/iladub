"""Generate examples/raw-to-clean-traversal.ttl — the worked raw→clean traversal (holon:06, spec § 4).

The file is GENERATED: the grounding graph the compiler emits for the offer-table fixture with
`validate_shapes=True` and a `Traversal` (raw document + semantic terms). Do not hand-edit it;
rerun this script. `tests/test_hga_alignment.py` regenerates it and compares by isomorphism.

Gate classification (CLAUDE.md §8): PROCEDURAL glue (spec § 3.6) — it calls the shipped
compiler and serialises the result. Irreducible because file I/O has no axiom form; it decides
nothing (every triple is derived by `vocab/queries/raw-to-clean-traversal.rq` or the grounder).

    PYTHONPATH=src .venv/bin/python scripts/raw_to_clean_example.py
"""
from __future__ import annotations

import os
import sys

from rdflib import Graph, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = URIRef("https://example.org/demo/offer-table")
SEMANTIC = URIRef("https://example.org/demo/transplant-terms")
OUT = os.path.join(ROOT, "examples", "raw-to-clean-traversal.ttl")


def build() -> Graph:
    """The grounding graph of spec § 4 (decisions are blank nodes; compare by isomorphism)."""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    cwd = os.getcwd()
    os.chdir(ROOT)  # the fixture helpers load their inputs by repo-relative path
    try:
        from iladub.feed import Traversal, ground_document
        from tests.test_concept_feed import _compiled_offer_graph, _offer_deps
        c, terms, shapes, proposer = _offer_deps()
        g = Graph()
        ground_document(_compiled_offer_graph(), c, proposer, terms, shapes, g,
                        validate_shapes=True, traversal=Traversal(RAW, (SEMANTIC,)))
    finally:
        os.chdir(cwd)
    # Return the graph AS THE FILE READS IT BACK: Turtle writes xsd:decimal 55 as `55.0`, and
    # isomorphism compares lexical forms, so the in-memory graph would never equal its own file.
    # Measured 2026-10-15: the only difference is the two ejectionFraction lexicals (55 vs 55.0).
    return Graph().parse(data=g.serialize(format="turtle"), format="turtle")


if __name__ == "__main__":
    build().serialize(destination=OUT, format="turtle")
    print(f"wrote {OUT}")
