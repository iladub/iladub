"""The documentation-governance lint (spec §6): PROCEDURAL extraction →
SHACL membrane (hard fail) → SPARQL derivations (evidence-staleness hard,
code-staleness warning, promotion queue report). Runs on the LIVE repo."""
import warnings
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

from tests.docgov_extract import extract

REPO = Path(__file__).resolve().parent.parent
SHAPES = REPO / "vocab" / "shapes" / "doc-governance-shapes.ttl"
QUERIES = REPO / "vocab" / "queries"


@pytest.fixture(scope="module")
def facts() -> Graph:
    return extract(REPO)


def _construct(g: Graph, name: str) -> Graph:
    out = Graph()
    for triple in g.query((QUERIES / name).read_text()):
        out.add(triple)
    return out


def test_membrane(facts):
    """Closed world: class totality, leak boundary, nav integrity, wiki
    frontmatter, doc-impact registration."""
    conforms, _, report = validate(
        facts, shacl_graph=Graph().parse(SHAPES),
        inference="rdfs", advanced=True,
    )
    assert conforms, f"doc-governance membrane violated:\n{report}"


def test_no_wiki_page_stale_against_evidence(facts):
    stale = _construct(facts, "docgov-staleness-evidence.rq")
    assert len(stale) == 0, (
        "wiki pages stale against changed evidence (update the page + its "
        f"`updated:` date):\n{stale.serialize(format='turtle')}"
    )


def test_code_staleness_is_a_warning_not_a_gate(facts):
    stale = _construct(facts, "docgov-staleness-code.rq")
    if len(stale):
        warnings.warn(
            "wiki pages stale against cited code (non-blocking, spec §6):\n"
            + stale.serialize(format="turtle"),
            UserWarning,
        )


def test_promotion_queue_report(facts):
    queue = _construct(facts, "docgov-promotion-queue.rq")
    if len(queue):
        warnings.warn(
            f"promotion queue: {len(queue)} wiki page(s) awaiting a release "
            "(spec §5, drained at the next tag):\n"
            + queue.serialize(format="turtle"),
            UserWarning,
        )
